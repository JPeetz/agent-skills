#!/usr/bin/env python3
"""Generate a month-end close checklist from a JSON config.

Stdlib only, no network. The checklist is scoped to the modules that are
actually active for the entity, so an entity without inventory never sees an
inventory task, and status is computed against the actual close day rather than
being hand-maintained.

Usage:
    python3 close_checklist.py --input close-config.json
    python3 close_checklist.py --input close-config.json --format json
    python3 close_checklist.py --input close-config.json --day D+3
    python3 close_checklist.py --input close-config.json --done PC-01 --done CC-02
    python3 close_checklist.py --self-test

Config schema (only `entity` and `period` are required):

    {
      "entity": "Acme Inc.",
      "period": "2026-10",
      "close_model": "business_day",          # or "calendar_day"
      "modules": ["bank", "accruals", "prepaids", "deferred_revenue",
                  "fixed_assets", "payroll", "ar", "ap", "tax"],
      "materiality": 25000,
      "team": {"controller": "A. Chen", "accountant": "M. Ortiz"}
    }

`modules` defaults to the full set. Unknown module ids are rejected rather than
ignored: a typo that silently drops a module would produce a checklist that
looks complete and is not. Exit codes: 0 ok, 2 bad input, 1 self-test failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# task library
# ---------------------------------------------------------------------------
# day: integer offset from period end (negative = business days before D0).
# owner_role: key into config["team"], or a role label if unassigned.
# modules: module ids that must be active for the task to appear. An empty
#          tuple means the task is core and always appears.

ALL_MODULES = (
    "bank", "ar", "ap", "payroll", "accruals", "prepaids", "deferred_revenue",
    "fixed_assets", "inventory", "intercompany", "commissions", "tax", "fx",
)

TASKS = [
    # ---- pre-close -------------------------------------------------------
    dict(id="PC-01", day=-5, phase="pre-close", owner_role="controller",
         title="Confirm close calendar and publish dates",
         detail="Publish D-5 through D+8 dates, dependencies and named owners; "
                "record the calendar/versus business-day model in use.",
         est_hours=1.0, modules=(), depends_on=[]),
    dict(id="PC-02", day=-5, phase="pre-close", owner_role="controller",
         title="Apply change freeze to ERP config and chart of accounts",
         detail="No chart-of-accounts, billing-rule or workflow changes until "
                "the period is locked. Freeze notice in writing.",
         est_hours=0.5, modules=(), depends_on=["PC-01"]),
    dict(id="PC-03", day=-5, phase="pre-close", owner_role="close_lead",
         title="Send data request to department heads",
         detail="Uncoded receipts, pending approvals, known commitments and "
                "large purchases for the period.",
         est_hours=1.0, modules=(), depends_on=[]),
    dict(id="PC-04", day=-4, phase="pre-close", owner_role="ap_clerk",
         title="AP cutoff communication to vendors and requesters",
         detail="State the invoice/receipt cutoff date and where to send "
                "late items so they accrue rather than slip.",
         est_hours=0.5, modules=("ap",), depends_on=["PC-01"]),
    dict(id="PC-05", day=-4, phase="pre-close", owner_role="accountant",
         title="Confirm bank and card feeds are current",
         detail="Every account connected, no feed gaps, last transaction date "
                "at or after D0. A missing feed is a silent understatement.",
         est_hours=0.5, modules=("bank",), depends_on=[]),
    dict(id="PC-06", day=-3, phase="pre-close", owner_role="accountant",
         title="Snapshot preliminary trial balance",
         detail="Archive the pre-close TB so post-close review can prove what "
                "changed and when.",
         est_hours=0.5, modules=(), depends_on=[]),
    dict(id="PC-07", day=-3, phase="pre-close", owner_role="accountant",
         title="Confirm subledger cutoffs (AR, AP, inventory)",
         detail="Transactions dated after D0 must not post to this period; "
                "confirm the system prevents it, do not rely on discipline.",
         est_hours=1.0, modules=("ar", "ap"), depends_on=["PC-06"]),
    dict(id="PC-08", day=-2, phase="pre-close", owner_role="payroll",
         title="Reconcile payroll register to HR headcount",
         detail="Headcount, gross-to-net, employer taxes and benefit costs "
                "tied to the register before the journal is prepared.",
         est_hours=2.0, modules=("payroll",), depends_on=[]),
    dict(id="PC-09", day=-2, phase="pre-close", owner_role="accountant",
         title="Clear unposted batches older than five days",
         detail="Aged unposted batches are the usual cause of a TB that will "
                "not tie after cutover.",
         est_hours=1.0, modules=(), depends_on=[]),
    dict(id="PC-10", day=-1, phase="pre-close", owner_role="billing",
         title="Freeze revenue subledger",
         detail="No invoicing or contract changes without controller approval "
                "after this point; revenue run starts from a fixed snapshot.",
         est_hours=0.5, modules=("deferred_revenue",), depends_on=[]),
    dict(id="PC-11", day=-1, phase="pre-close", owner_role="controller",
         title="Pre-close stand-up",
         detail="Known issues, expected accruals, staffing gaps and anything "
                "already known to be late.",
         est_hours=0.5, modules=(), depends_on=["PC-03", "PC-06"]),

    # ---- core close ------------------------------------------------------
    dict(id="CC-01", day=1, phase="core-close", owner_role="payroll",
         title="Post payroll journal",
         detail="Gross wages, employer taxes, benefits and accruals to the "
                "correct cost centres and periods.",
         est_hours=1.5, modules=("payroll",), depends_on=["PC-08"]),
    dict(id="CC-02", day=1, phase="core-close", owner_role="accountant",
         title="Import all bank and card transactions through D0",
         detail="Import count must reconcile to statement line count. A short "
                "import looks exactly like a clean month.",
         est_hours=1.0, modules=("bank",), depends_on=["PC-05"]),
    dict(id="CC-03", day=1, phase="core-close", owner_role="accountant",
         title="Post recurring journal entries",
         detail="Rent, subscriptions, loan interest, depreciation templates. "
                "Confirm each template still has a live underlying contract.",
         est_hours=1.5, modules=(), depends_on=["PC-09"]),
    dict(id="CC-04", day=2, phase="core-close", owner_role="accountant",
         title="Bank reconciliations - all operating and reserve accounts",
         detail="Statement balance + deposits in transit - outstanding checks "
                "= GL adjusted balance. Residual must be zero or explained.",
         est_hours=4.0, modules=("bank",), depends_on=["CC-02"]),
    dict(id="CC-05", day=2, phase="core-close", owner_role="accountant",
         title="Corporate card reconciliations and expense coding",
         detail="Uncoded items routed to owners with a deadline, not absorbed "
                "into a general expense account.",
         est_hours=2.5, modules=("bank",), depends_on=["CC-02"]),
    dict(id="CC-06", day=2, phase="core-close", owner_role="ar_analyst",
         title="AR reconciliation, aging review and allowance assessment",
         detail="Subledger to GL tie at zero; aging movement explained; "
                "allowance assessed on evidence, not on prior percentage.",
         est_hours=3.0, modules=("ar",), depends_on=["PC-07"]),
    dict(id="CC-07", day=3, phase="core-close", owner_role="ap_clerk",
         title="AP reconciliation and search for unrecorded liabilities",
         detail="Sample invoices received after cutoff and confirm each is "
                "either accrued or genuinely next-period.",
         est_hours=3.0, modules=("ap",), depends_on=["PC-04", "PC-07"]),
    dict(id="CC-08", day=3, phase="core-close", owner_role="accountant",
         title="Post accrual entries with reversals in the same batch",
         detail="Every accrual expected to be invoiced next period carries its "
                "reversing entry. No accrual reverses 'later'.",
         est_hours=4.0, modules=("accruals",), depends_on=["CC-07"]),
    dict(id="CC-09", day=3, phase="core-close", owner_role="accountant",
         title="Prepaid amortization run and posting",
         detail="Day-count amortization within the period; short/long-term "
                "split checked; roll-forward ties to the GL.",
         est_hours=2.0, modules=("prepaids",), depends_on=["CC-03"]),
    dict(id="CC-10", day=3, phase="core-close", owner_role="cost_accountant",
         title="Inventory valuation and COGS reconciliation",
         detail="Quantity x cost tie to the perpetual record; standard-cost "
                "variances explained; reserve assessed against ageing.",
         est_hours=4.0, modules=("inventory",), depends_on=["PC-07"]),
    dict(id="CC-11", day=3, phase="core-close", owner_role="revops",
         title="Commission accrual and plan attainment check",
         detail="Attainment computed from booked revenue, not from forecast; "
                "employer burden included on top of the commission.",
         est_hours=2.0, modules=("commissions",), depends_on=["PC-10"]),
    dict(id="CC-12", day=4, phase="core-close", owner_role="accountant",
         title="Fixed asset roll-forward, depreciation and disposals",
         detail="Opening + additions - disposals - depreciation = closing; CWIP "
                "reviewed for items placed in service.",
         est_hours=3.0, modules=("fixed_assets",), depends_on=["CC-03"]),
    dict(id="CC-13", day=4, phase="core-close", owner_role="rev_accountant",
         title="Revenue recognition run and deferred revenue roll-forward",
         detail="Opening + billings - recognized +/- adjustments = closing, per "
                "contract and in total. No negative contract balances.",
         est_hours=4.0, modules=("deferred_revenue",), depends_on=["PC-10"]),
    dict(id="CC-14", day=4, phase="core-close", owner_role="consolidation",
         title="Intercompany matching and elimination entries",
         detail="Both sides of every IC transaction agree exactly; residual is "
                "zero before eliminations, not after.",
         est_hours=3.0, modules=("intercompany",), depends_on=["CC-03"]),
    dict(id="CC-15", day=4, phase="core-close", owner_role="accountant",
         title="Accrual true-up against prior month actuals",
         detail="Compare last month's accrual to the invoice actually received; "
                "a large stable true-up means the accrual basis is wrong.",
         est_hours=1.5, modules=("accruals",), depends_on=["CC-08"]),
    dict(id="CC-16", day=5, phase="core-close", owner_role="treasury",
         title="FX revaluation of monetary balances",
         detail="Closing rate applied to monetary items; revaluation posted to "
                "the FX account; CTA computed where the entity is foreign.",
         est_hours=2.0, modules=("fx",), depends_on=["CC-03"]),
    dict(id="CC-17", day=5, phase="core-close", owner_role="tax",
         title="Sales tax / VAT reconciliation and filing prep",
         detail="Return amount tied to GL tax liability; nexus and rate changes "
                "confirmed; filing calendar checked.",
         est_hours=2.5, modules=("tax",), depends_on=["CC-06"]),
    dict(id="CC-18", day=5, phase="core-close", owner_role="controller",
         title="Trial balance review - balance check and unusual movements",
         detail="Debits = credits, BS balances, subledger ties at zero, sign "
                "flips and dormant accounts investigated.",
         est_hours=2.0, modules=(), depends_on=["CC-04", "CC-08", "CC-13"]),
    dict(id="CC-19", day=5, phase="core-close", owner_role="fpa",
         title="Flux analysis above threshold with commentary",
         detail="Every account over threshold gets a driver classification and "
                "quantification. Explanation from the account owner.",
         est_hours=4.0, modules=(), depends_on=["CC-18"]),

    # ---- review ----------------------------------------------------------
    dict(id="RV-01", day=6, phase="review", owner_role="controller",
         title="Journal entry review and approval",
         detail="Every manual JE has support, a business reason, and an approver "
                "who is not the preparer. Unsupported entries get pulled.",
         est_hours=2.5, modules=(), depends_on=["CC-08", "CC-15"]),
    dict(id="RV-02", day=6, phase="review", owner_role="fpa",
         title="Variance commentary completion and sign-off",
         detail="Budget-versus-actual narrative for every account group over "
                "threshold; unfavorable variances not netted away.",
         est_hours=3.0, modules=(), depends_on=["CC-19"]),
    dict(id="RV-03", day=7, phase="review", owner_role="controller",
         title="Build financial statement package",
         detail="P&L, balance sheet, cash flow and supporting schedules, with "
                "the reconciliation and JE logs attached.",
         est_hours=4.0, modules=(), depends_on=["RV-01", "RV-02"]),
    dict(id="RV-04", day=7, phase="review", owner_role="cfo",
         title="Management review and sign-off",
         detail="Balance sheet sign-off and a challenge session on the largest "
                "three movements. No sign-off on unreviewed numbers.",
         est_hours=1.5, modules=(), depends_on=["RV-03"]),
    dict(id="RV-05", day=8, phase="review", owner_role="controller",
         title="Lock period and close subledgers",
         detail="Hard lock in the ERP; post-close adjustments require a logged, "
                "approved entry that is reported next period.",
         est_hours=1.0, modules=(), depends_on=["RV-04"]),
    dict(id="RV-06", day=8, phase="review", owner_role="close_lead",
         title="Close retrospective and efficiency metrics capture",
         detail="Days consumed per task, stale item count, rework count, "
                "post-close adjustments. Trend beats any single month.",
         est_hours=1.5, modules=(), depends_on=["RV-05"]),
]

PHASE_LABELS = {
    "pre-close": "Pre-close",
    "core-close": "Core close",
    "review": "Review",
}

DEFAULT_TEAM = {
    "controller": "Controller",
    "close_lead": "Close lead",
    "accountant": "Staff accountant",
    "senior_accountant": "Senior accountant",
    "ap_clerk": "AP clerk",
    "ar_analyst": "AR analyst",
    "payroll": "Payroll",
    "billing": "Billing",
    "rev_accountant": "Revenue accountant",
    "revops": "RevOps",
    "cost_accountant": "Cost accountant",
    "consolidation": "Consolidation",
    "treasury": "Treasury",
    "tax": "Tax",
    "fpa": "FP&A",
    "cfo": "CFO",
}

DAY_TOKEN = re.compile(r"^D([+-]\d+)$")
PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ConfigError(Exception):
    """Raised on malformed or contradictory configuration."""


# ---------------------------------------------------------------------------
# input validation
# ---------------------------------------------------------------------------

def parse_day(value, field="close_day"):
    """Accept -5, "D-5", "D+3", "+3", or "0". Return an int offset."""
    if isinstance(value, bool):
        raise ConfigError("{}: expected a day offset, got a boolean".format(field))
    if isinstance(value, int):
        offset = value
    elif isinstance(value, str):
        text = value.strip().upper().replace(" ", "")
        if text in ("0", "D0"):
            offset = 0
        else:
            match = DAY_TOKEN.match(text)
            if not match:
                raise ConfigError(
                    "{}: {!r} is not a valid day token (use D-5, D+3 or 0)".format(field, value))
            offset = int(match.group(1))
    else:
        raise ConfigError("{}: expected an integer or day token".format(field))

    if offset < -10 or offset > 15:
        raise ConfigError(
            "{}: offset {} is outside the supported range (-10 to +15)".format(field, offset))
    return offset


def validate_config(raw):
    """Validate and normalise a config dict. Raises ConfigError on bad input."""
    if not isinstance(raw, dict):
        raise ConfigError("config must be a JSON object, got {}".format(type(raw).__name__))

    entity = raw.get("entity")
    if not isinstance(entity, str) or not entity.strip():
        raise ConfigError("entity: required non-empty string")

    period = raw.get("period")
    if not isinstance(period, str) or not PERIOD_RE.match(period.strip()):
        raise ConfigError(
            "period: required as YYYY-MM (got {!r})".format(period))

    model = raw.get("close_model", "business_day")
    if model not in ("business_day", "calendar_day"):
        raise ConfigError(
            "close_model: must be 'business_day' or 'calendar_day' (got {!r})".format(model))

    modules = raw.get("modules", list(ALL_MODULES))
    if not isinstance(modules, list) or not all(isinstance(m, str) for m in modules):
        raise ConfigError("modules: must be a list of strings")
    unknown = sorted(set(modules) - set(ALL_MODULES))
    if unknown:
        raise ConfigError(
            "modules: unknown module(s) {}; valid: {}".format(
                ", ".join(unknown), ", ".join(ALL_MODULES)))
    if len(set(modules)) != len(modules):
        raise ConfigError("modules: duplicate entries are not allowed")

    materiality = raw.get("materiality", 0)
    if isinstance(materiality, bool) or not isinstance(materiality, (int, float)):
        raise ConfigError("materiality: must be a number")
    if materiality < 0:
        raise ConfigError("materiality: must be >= 0")

    team = raw.get("team", {})
    if not isinstance(team, dict):
        raise ConfigError("team: must be an object mapping role to person")
    for role, person in team.items():
        if not isinstance(person, str) or not person.strip():
            raise ConfigError("team.{}: must be a non-empty string".format(role))

    close_day = raw.get("close_day")
    offset = parse_day(close_day) if close_day is not None else None

    return {
        "entity": entity.strip(),
        "period": period.strip(),
        "close_model": model,
        "modules": modules,
        "materiality": materiality,
        "team": team,
        "close_day": offset,
    }


# ---------------------------------------------------------------------------
# checklist generation
# ---------------------------------------------------------------------------

def build_checklist(cfg, done=(), day_override=None):
    """Return the scoped, status-annotated task list plus summary metrics."""
    modules = set(cfg["modules"])
    current = cfg["close_day"] if day_override is None else day_override
    done_set = set(done)

    unknown_done = sorted(done_set - {t["id"] for t in TASKS})
    if unknown_done:
        raise ConfigError("done: unknown task id(s) {}".format(", ".join(unknown_done)))

    rows = []
    for task in TASKS:
        required = task["modules"]
        # A task is in scope if it is core, or if every module it needs is active.
        if required and not set(required).issubset(modules):
            continue

        owner = cfg["team"].get(task["owner_role"], DEFAULT_TEAM.get(task["owner_role"],
                                                                   task["owner_role"]))
        unassigned = task["owner_role"] not in cfg["team"]

        if task["id"] in done_set:
            status = "done"
        elif current is None:
            status = "pending"
        elif task["day"] < current:
            status = "overdue"
        elif task["day"] == current:
            status = "due today"
        else:
            status = "upcoming"

        rows.append({
            "id": task["id"],
            "day": task["day"],
            "day_label": "D0" if task["day"] == 0 else "D{:+d}".format(task["day"]),
            "phase": task["phase"],
            "phase_label": PHASE_LABELS[task["phase"]],
            "title": task["title"],
            "detail": task["detail"],
            "owner_role": task["owner_role"],
            "owner": owner,
            "owner_assigned": not unassigned,
            "est_hours": task["est_hours"],
            "depends_on": list(task["depends_on"]),
            "status": status,
        })

    # Drop dependencies that were scoped out, so the output never points at a
    # task the reader cannot see.
    present = {r["id"] for r in rows}
    for row in rows:
        row["depends_on"] = [d for d in row["depends_on"] if d in present]

    by_status = {}
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1

    by_owner = {}
    for row in rows:
        if row["status"] == "done":
            continue
        by_owner[row["owner"]] = round(by_owner.get(row["owner"], 0.0) + row["est_hours"], 2)

    warnings = []
    coverage_modules = [m for m in modules if m in ALL_MODULES]
    uncovered = []
    for module in coverage_modules:
        has_task = any(module in t["modules"] for t in TASKS)
        if not has_task:
            uncovered.append(module)
    if uncovered:
        warnings.append("no checklist task covers module(s): " + ", ".join(sorted(uncovered)))

    unassigned = sorted({r["owner_role"] for r in rows if not r["owner_assigned"]})
    if unassigned:
        warnings.append(
            "no named owner for role(s): " + ", ".join(unassigned) +
            " - checklist will show role labels only")

    if not modules:
        warnings.append("modules list is empty: only core accounting tasks are included")

    if not cfg["materiality"]:
        warnings.append("materiality is 0 or unset: flux and variance thresholds default to 0")

    critical = {"CC-18", "RV-03", "RV-05"}
    critical_path = [r["id"] for r in rows if r["id"] in critical]
    if len(critical_path) < len(critical):
        missing = sorted(critical - set(critical_path))
        warnings.append("core tasks scoped out unexpectedly: " + ", ".join(missing))

    return {
        "entity": cfg["entity"],
        "period": cfg["period"],
        "close_model": cfg["close_model"],
        "close_day": cfg["close_day"] if day_override is None else day_override,
        "close_day_label": ("not set" if current is None else
                            ("D0" if current == 0 else "D{:+d}".format(current))),
        "materiality": cfg["materiality"],
        "modules_active": list(cfg["modules"]),
        "summary": {
            "task_count": len(rows),
            "total_hours": round(sum(r["est_hours"] for r in rows), 2),
            "remaining_hours": round(sum(r["est_hours"] for r in rows
                                         if r["status"] != "done"), 2),
            "by_status": by_status,
            "hours_by_owner": by_owner,
            "reconciliation_coverage": round(
                100.0 * len([m for m in coverage_modules if m not in uncovered]) /
                len(coverage_modules), 1) if coverage_modules else 0.0,
        },
        "critical_path": critical_path,
        "warnings": warnings,
        "tasks": rows,
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def render_markdown(result):
    lines = []
    add = lines.append
    add("# Month-end close checklist — {}".format(result["entity"]))
    add("")
    add("Period **{}** · close model **{}** · status as of **{}**".format(
        result["period"], result["close_model"], result["close_day_label"]))
    add("")
    if result["materiality"]:
        add("Materiality: **{:,.2f}**. Flux and variance thresholds default to this "
            "amount unless overridden per account.".format(result["materiality"]))
        add("")

    s = result["summary"]
    add("## Summary")
    add("")
    add("| Metric | Value |")
    add("|---|---|")
    add("| Tasks in scope | {} |".format(s["task_count"]))
    add("| Estimated hours | {:.1f} |".format(s["total_hours"]))
    add("| Hours remaining | {:.1f} |".format(s["remaining_hours"]))
    add("| Reconciliation coverage | {}% |".format(s["reconciliation_coverage"]))
    for status in ("done", "overdue", "due today", "upcoming", "pending"):
        if status in s["by_status"]:
            add("| Tasks {} | {} |".format(status, s["by_status"][status]))
    add("")

    if s["hours_by_owner"]:
        add("### Remaining hours by owner")
        add("")
        add("| Owner | Hours |")
        add("|---|---|")
        for owner, hours in sorted(s["hours_by_owner"].items(), key=lambda kv: -kv[1]):
            add("| {} | {:.1f} |".format(owner, hours))
        add("")

    if result["warnings"]:
        add("### Warnings")
        add("")
        for warning in result["warnings"]:
            add("- {}".format(warning))
        add("")

    add("## Critical path")
    add("")
    add(" ".join("`{}`".format(i) for i in result["critical_path"]) or "n/a")
    add("")

    for phase in ("pre-close", "core-close", "review"):
        rows = [t for t in result["tasks"] if t["phase"] == phase]
        if not rows:
            continue
        add("## {}".format(PHASE_LABELS[phase]))
        add("")
        add("| ID | Day | Task | Owner | Est h | Depends | Status |")
        add("|---|---|---|---|---|---|---|")
        for row in rows:
            add("| {} | {} | {} | {} | {:.1f} | {} | {} |".format(
                row["id"], row["day_label"], row["title"], row["owner"],
                row["est_hours"], ", ".join(row["depends_on"]) or "—",
                _status_cell(row["status"])))
        add("")
        add("<details><summary>Task detail</summary>")
        add("")
        for row in rows:
            add("- **{}** — {}".format(row["id"], row["detail"]))
        add("")
        add("</details>")
        add("")

    add("## Completion rule")
    add("")
    add("A task is complete only when its evidence artifact exists — a signed "
        "reconciliation, a posted JE batch, a roll-forward that ties. Marking a "
        "task done because the day arrived is checklist theatre and is tracked "
        "as rework at the retrospective.")
    return "\n".join(lines)


def _status_cell(status):
    return {
        "done": "done",
        "overdue": "**overdue**",
        "due today": "*due today*",
        "upcoming": "upcoming",
        "pending": "—",
    }.get(status, status)


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

DEMO_CONFIG = {
    "entity": "Northwind Robotics Ltd",
    "period": "2026-10",
    "close_model": "business_day",
    "close_day": "D+3",
    "materiality": 25000,
    "modules": ["bank", "accruals", "deferred_revenue", "fixed_assets",
                "payroll", "ar", "ap", "tax"],
    "team": {"controller": "A. Chen", "accountant": "M. Ortiz",
             "payroll": "K. Idris", "fpa": "S. Rahman"},
}


def self_test():
    checks = []

    def check(name, condition, detail=""):
        checks.append((name, bool(condition), detail))

    # 1. demo config validates
    cfg = validate_config(DEMO_CONFIG)
    check("demo config validates", cfg["entity"] == "Northwind Robotics Ltd")

    # 2. scoping: inventory and intercompany tasks are excluded
    result = build_checklist(cfg)
    ids = {t["id"] for t in result["tasks"]}
    check("inventory task scoped out", "CC-10" not in ids)
    check("intercompany task scoped out", "CC-14" not in ids)
    check("bank rec in scope", "CC-04" in ids)
    check("task count sane", 20 <= len(ids) <= 40, "{} tasks".format(len(ids)))

    # 3. status logic against D+3
    statuses = {t["id"]: t["status"] for t in result["tasks"]}
    check("D-5 task overdue at D+3", statuses["PC-01"] == "overdue")
    check("D+3 task due today", statuses["CC-08"] == "due today")
    check("D+8 task upcoming", statuses["RV-05"] == "upcoming")

    # 4. done override wins over day status
    done_result = build_checklist(cfg, done=["PC-01", "CC-01"])
    done_status = {t["id"]: t["status"] for t in done_result["tasks"]}
    check("done overrides overdue", done_status["PC-01"] == "done")
    check("done reduces remaining hours",
          done_result["summary"]["remaining_hours"] < result["summary"]["remaining_hours"])

    # 5. dependencies only reference visible tasks
    visible = {t["id"] for t in result["tasks"]}
    dangling = [t["id"] for t in result["tasks"]
                if any(d not in visible for d in t["depends_on"])]
    check("no dangling dependencies", not dangling, str(dangling))

    # 6. markdown renders with all three phases and no unresolved braces
    md = render_markdown(result)
    check("markdown has pre-close", "## Pre-close" in md)
    check("markdown has core close", "## Core close" in md)
    check("markdown has review", "## Review" in md)
    check("markdown has no format residue", "{" not in md.split("## Completion rule")[0])
    check("markdown lists overdue", "overdue" in md)

    # 7. json round-trips
    try:
        roundtrip = json.loads(json.dumps(result))
        check("json serialises", roundtrip["entity"] == cfg["entity"])
    except (TypeError, ValueError) as exc:
        check("json serialises", False, str(exc))

    # 8. validation rejects bad input
    bad_cases = [
        ("missing entity", {"period": "2026-10"}),
        ("bad period", {"entity": "X", "period": "2026-13"}),
        ("bad period format", {"entity": "X", "period": "October"}),
        ("unknown module", {"entity": "X", "period": "2026-10", "modules": ["banks"]}),
        ("bad close day", {"entity": "X", "period": "2026-10", "close_day": "day three"}),
        ("negative materiality", {"entity": "X", "period": "2026-10", "materiality": -1}),
        ("duplicate modules", {"entity": "X", "period": "2026-10", "modules": ["bank", "bank"]}),
        ("bad team value", {"entity": "X", "period": "2026-10", "team": {"cfo": 3}}),
        ("not an object", ["entity"]),
    ]
    for name, payload in bad_cases:
        try:
            validate_config(payload)
            check("rejects " + name, False, "accepted invalid config")
        except ConfigError:
            check("rejects " + name, True)

    # 9. day token parsing
    check("parses D+3", parse_day("D+3") == 3)
    check("parses D-5", parse_day("D-5") == -5)
    check("parses int", parse_day(0) == 0)
    try:
        parse_day("D99")
        check("rejects out-of-range day", False)
    except ConfigError:
        check("rejects out-of-range day", True)

    # 10. unknown done id is an error, not silently ignored
    try:
        build_checklist(cfg, done=["ZZ-99"])
        check("rejects unknown done id", False)
    except ConfigError:
        check("rejects unknown done id", True)

    # 11. no-modules config still produces the core checklist
    minimal = validate_config({"entity": "Solo Ltd", "period": "2026-01", "modules": []})
    minimal_result = build_checklist(minimal)
    check("minimal config has core tasks", minimal_result["summary"]["task_count"] >= 6)
    check("minimal config warns", any("modules list is empty" in w
                                      for w in minimal_result["warnings"]))

    # 12. coverage metric is bounded
    check("coverage bounded", 0 <= result["summary"]["reconciliation_coverage"] <= 100)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print("{}  {}{}".format("PASS" if ok else "FAIL", name,
                                "" if ok or not detail else "  ({})".format(detail)))
    print("\n{}/{} checks passed".format(len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="close_checklist.py",
        description="Generate a month-end close checklist from a JSON config.",
        epilog="Example: close_checklist.py --input close-config.json --day D+3 "
               "--format markdown")
    parser.add_argument("--input", "-i", metavar="PATH",
                        help="path to the close config JSON")
    parser.add_argument("--format", "-f", choices=("markdown", "json"),
                        default="markdown", help="output format (default: markdown)")
    parser.add_argument("--out", "-o", metavar="PATH",
                        help="write output to a file instead of stdout")
    parser.add_argument("--day", metavar="D+N", default=None,
                        help="override status day (e.g. D-2, D+4, 0)")
    parser.add_argument("--done", action="append", default=[], metavar="TASK_ID",
                        help="mark a task complete; repeatable (e.g. --done CC-01)")
    parser.add_argument("--self-test", action="store_true",
                        help="run built-in checks against a demo config and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.input:
        parser.error("--input is required unless --self-test is used")

    try:
        with open(args.input, encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        print("error: no such file: {}".format(args.input), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: {} is not valid JSON: {}".format(args.input, exc), file=sys.stderr)
        return 2

    try:
        cfg = validate_config(raw)
        day_override = parse_day(args.day) if args.day is not None else None
        result = build_checklist(cfg, done=args.done, day_override=day_override)
    except ConfigError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    if args.format == "json":
        text = json.dumps(result, indent=2)
    else:
        text = render_markdown(result)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
        except OSError as exc:
            print("error: cannot write {}: {}".format(args.out, exc), file=sys.stderr)
            return 2
        print("wrote {} ({} tasks, {})".format(
            args.out, result["summary"]["task_count"], args.format), file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
