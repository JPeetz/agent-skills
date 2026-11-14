#!/usr/bin/env python3
"""Compute a full SaaS metrics pack from a JSON input.

Stdlib only, no network. Every metric is emitted with the definition it used so
a board pack cannot silently mix variants.

Usage:
    python3 metrics_calculator.py --input metrics.json --output markdown
    python3 metrics_calculator.py --input metrics.json --output json

Input schema (all money in one currency, numbers as JSON numbers):

    {
      "company": "Acme",
      "currency": "USD",
      "period":  {"start": "2026-01", "end": "2026-06"},
      "mrr":     {"begin": 100000, "end": 128000},
      "movement":{"new": 30000, "expansion": 9000, "reactivation": 2000,
                  "contraction": 4000, "churn": 9000},
      "customers": {"begin": 200, "end": 214, "new": 30, "churned": 16},
      "pnl":     {"revenue": 660000, "cogs": 132000, "sales_marketing": 180000},
      "cash":    {"balance": 4200000, "net_burn_monthly": 100000},
      "acquisition": {"paid_spend": 90000, "paid_new_customers": 12},
      "assumptions": {"ltv_lifetime_months": 48, "segment": "mid-market",
                      "gross_margin": 0.8}
    }

Only `mrr` is strictly required. Optional blocks compute what they can and the
output marks the rest "n/a" rather than inventing a value. `movement` must be
complete if present: a partial bridge silently misstates churn.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Optional

MOVEMENT_KEYS = ("new", "expansion", "reactivation", "contraction", "churn")


class InputError(Exception):
    """Raised on malformed or contradictory input."""


# ---------------------------------------------------------------------------
# input helpers
# ---------------------------------------------------------------------------

def num(value, label, *, required=False):
    """Coerce to float, rejecting booleans, strings and negatives."""
    if value is None:
        if required:
            raise InputError("missing required field: {}".format(label))
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError("{} must be a number, got {!r}".format(label, value))
    if value < 0:
        raise InputError("{} must not be negative (report magnitudes; the "
                         "script applies signs)".format(label))
    return float(value)


def read_movement(block) -> Optional[tuple]:
    """Return (new, expansion, reactivation, contraction, churn) or None.

    A partial block is an error: treating a missing component as zero would
    understate churn and overstate NRR.
    """
    if block is None:
        return None
    if not isinstance(block, dict):
        raise InputError("movement must be a JSON object")
    missing = [k for k in MOVEMENT_KEYS if block.get(k) is None]
    if missing:
        raise InputError("movement is present but missing: {}. Supply all of "
                         "{} or omit the block entirely."
                         .format(", ".join(missing), ", ".join(MOVEMENT_KEYS)))
    values = []
    for key in MOVEMENT_KEYS:
        value = num(block[key], "movement." + key)
        assert value is not None  # presence checked above
        values.append(abs(value))
    return tuple(values)


def read_customers(block) -> Optional[tuple]:
    """Return (begin, end, new, churned) with new/churned possibly None."""
    if block is None:
        return None
    if not isinstance(block, dict):
        raise InputError("customers must be a JSON object")
    begin = num(block.get("begin"), "customers.begin")
    end = num(block.get("end"), "customers.end")
    if begin is None or end is None:
        raise InputError("customers requires both begin and end")
    return (float(begin), float(end),
            num(block.get("new"), "customers.new"),
            num(block.get("churned"), "customers.churned"))


def div(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def months_in_period(period) -> Optional[int]:
    """Inclusive month count between period start and end (YYYY-MM)."""
    if not isinstance(period, dict) or "start" not in period or "end" not in period:
        return None
    try:
        start = date.fromisoformat(str(period["start"])[:7] + "-01")
        end = date.fromisoformat(str(period["end"])[:7] + "-01")
    except ValueError:
        raise InputError("period.start and period.end must be YYYY-MM")
    if end < start:
        raise InputError("period.end precedes period.start")
    return (end.year - start.year) * 12 + (end.month - start.month) + 1


def annualise_rate(period_rate, months: Optional[int]):
    """Period churn -> monthly rate. Never multiply by 12."""
    if period_rate is None or not months or months <= 0:
        return None
    if period_rate >= 1:
        return 1.0
    return 1 - (1 - period_rate) ** (1.0 / months)


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

def pct(value):
    return "n/a" if value is None else "{:.1f}%".format(value * 100)


def money(value, currency="USD"):
    return "n/a" if value is None else "{:,.0f} {}".format(value, currency)


def ratio(value):
    return "n/a" if value is None else "{:.2f}x".format(value)


def months_fmt(value):
    return "n/a" if value is None else "{:.1f} months".format(value)


def count(value):
    if value is None:
        return "n/a"
    return "{:,.0f}".format(value)


# ---------------------------------------------------------------------------
# calculation
# ---------------------------------------------------------------------------

def calculate(data) -> dict:
    if not isinstance(data, dict):
        raise InputError("input must be a JSON object")

    currency = str(data.get("currency", "USD")).upper()
    period = data.get("period") or {}
    months = months_in_period(period)
    assumptions = data.get("assumptions") or {}
    if not isinstance(assumptions, dict):
        raise InputError("assumptions must be a JSON object")

    res = {
        "company": data.get("company", "Unnamed company"),
        "currency": currency,
        "period": period,
        "months": months,
        "segment": str(assumptions.get("segment", "")).lower() or "unspecified",
        "metrics": {},
        "checks": {},
        "flags": [],
        "definitions": {},
        "benchmarks": [],
    }
    m = res["metrics"]
    flags = res["flags"]

    def flag(severity, metric, message):
        flags.append({"severity": severity, "metric": metric, "message": message})

    # -- Layer 1: revenue base -------------------------------------------
    mrr = data.get("mrr") or {}
    if not isinstance(mrr, dict):
        raise InputError("mrr must be a JSON object")
    mrr_begin = num(mrr.get("begin"), "mrr.begin", required=True)
    mrr_end = num(mrr.get("end"), "mrr.end", required=True)
    if mrr_begin == 0:
        raise InputError("mrr.begin must be greater than zero")

    m["mrr_begin"] = round(mrr_begin, 2)
    m["mrr_end"] = round(mrr_end, 2)
    m["arr_begin"] = round(mrr_begin * 12, 2)
    m["arr_end"] = round(mrr_end * 12, 2)
    m["mrr_growth_pct"] = (mrr_end - mrr_begin) / mrr_begin
    m["arr_growth_pct"] = m["mrr_growth_pct"]

    movement = read_movement(data.get("movement"))
    if movement is not None:
        new, expansion, reactivation, contraction, churn = movement
        net_new_mrr = new + expansion + reactivation - contraction - churn
        m["movement"] = {
            "new": new, "expansion": expansion, "reactivation": reactivation,
            "contraction": contraction, "churn": churn,
        }
        m["net_new_mrr"] = round(net_new_mrr, 2)
        m["net_new_arr"] = round(net_new_mrr * 12, 2)

        residual = (mrr_begin + net_new_mrr) - mrr_end
        res["checks"]["mrr_bridge_residual"] = round(residual, 2)
        if abs(residual) > max(1.0, mrr_begin * 0.001):
            flag("high", "mrr_bridge",
                 "MRR bridge does not close: begin + movements = {:,.0f} but end "
                 "MRR is {:,.0f} (residual {:,.0f}). Find the uncategorised "
                 "movement before reporting."
                 .format(mrr_begin + net_new_mrr, mrr_end, residual))

        # -- Layer 2: retention ------------------------------------------
        leak = contraction + churn
        m["gross_revenue_churn_rate"] = div(leak, mrr_begin)
        m["gross_revenue_churn_monthly"] = annualise_rate(
            m["gross_revenue_churn_rate"], months)
        m["grr"] = div(mrr_begin - leak, mrr_begin)
        m["nrr"] = div(mrr_begin + expansion - leak, mrr_begin)
        m["nrr_incl_reactivation"] = div(
            mrr_begin + expansion + reactivation - leak, mrr_begin)
        m["quick_ratio"] = div(new + expansion, leak)
        m["expansion_rate"] = div(expansion, mrr_begin)
        res["definitions"]["nrr"] = (
            "(begin + expansion - contraction - churn) / begin; excludes new "
            "business and reactivation")
        res["definitions"]["grr"] = (
            "(begin - contraction - churn) / begin; always <= 100%")

    # -- customers --------------------------------------------------------
    customers = read_customers(data.get("customers"))
    c_new = None
    if customers is not None:
        c_begin, c_end, c_new, c_churned = customers
        if c_begin == 0:
            raise InputError("customers.begin must be greater than zero")
        m["customers_begin"] = c_begin
        m["customers_end"] = c_end
        m["arpa_begin"] = div(mrr_begin, c_begin)
        m["arpa_end"] = div(mrr_end, c_end)
        m["net_customer_adds"] = c_end - c_begin
        if c_churned is not None:
            m["logo_churn_rate"] = div(c_churned, c_begin)
            m["logo_churn_monthly"] = annualise_rate(m["logo_churn_rate"], months)

    # -- Layer 3: unit economics -----------------------------------------
    pnl = data.get("pnl") or {}
    if not isinstance(pnl, dict):
        raise InputError("pnl must be a JSON object")
    revenue = num(pnl.get("revenue"), "pnl.revenue")
    cogs = num(pnl.get("cogs"), "pnl.cogs")
    sm_spend = num(pnl.get("sales_marketing"), "pnl.sales_marketing")
    variable = num(pnl.get("variable_costs"), "pnl.variable_costs")

    gross_margin = None
    if revenue is not None:
        m["revenue"] = revenue
        if cogs is not None:
            gross_margin = (revenue - cogs) / revenue
            m["gross_profit"] = revenue - cogs
        if variable is not None and cogs is not None:
            m["contribution_margin"] = (revenue - cogs - variable) / revenue

    if gross_margin is not None:
        m["gross_margin"] = gross_margin
    else:
        gm_assumed = num(assumptions.get("gross_margin"), "assumptions.gross_margin")
        if gm_assumed is not None:
            if gm_assumed > 1:
                gm_assumed = gm_assumed / 100.0
            if not 0 < gm_assumed <= 1:
                raise InputError("assumptions.gross_margin must be 0-1 or 0-100")
            gross_margin = gm_assumed
            m["gross_margin"] = gm_assumed
            m["gross_margin_assumed"] = True
            res["definitions"]["gross_margin"] = (
                "assumption supplied in input, not derived from P&L")

    arpa = m.get("arpa_begin")
    cac = div(sm_spend, c_new) if c_new else None
    if sm_spend is not None and not c_new:
        flag("medium", "cac",
             "Sales & marketing spend supplied but no new-customer count; "
             "blended CAC cannot be computed.")

    acq = data.get("acquisition") or {}
    paid_spend = num(acq.get("paid_spend"), "acquisition.paid_spend")
    paid_new = num(acq.get("paid_new_customers"), "acquisition.paid_new_customers")
    m["cac_blended"] = cac
    m["cac_paid"] = div(paid_spend, paid_new)

    monthly_churn = m.get("gross_revenue_churn_monthly")
    lifetime = num(assumptions.get("ltv_lifetime_months"),
                   "assumptions.ltv_lifetime_months")
    if lifetime is not None and lifetime <= 0:
        raise InputError("assumptions.ltv_lifetime_months must be > 0")

    ltv = None
    if arpa is not None and gross_margin is not None:
        if lifetime is None and monthly_churn:
            lifetime = 1.0 / monthly_churn
            res["definitions"]["ltv_lifetime"] = (
                "1 / monthly gross revenue churn ({:.1f} months)".format(lifetime))
        elif lifetime is not None:
            res["definitions"]["ltv_lifetime"] = (
                "assumed {:.0f} months".format(lifetime))
        if lifetime:
            ltv = arpa * gross_margin * lifetime
            m["ltv"] = ltv
            m["ltv_lifetime_months"] = round(lifetime, 1)
            m["ltv_cac"] = div(ltv, cac)
            m["cac_payback_months"] = div(cac, arpa * gross_margin)
            res["definitions"]["ltv"] = (
                "ARPA x gross margin x lifetime (margin-based)")

    # -- Layer 4: efficiency and cash ------------------------------------
    cash = data.get("cash") or {}
    if not isinstance(cash, dict):
        raise InputError("cash must be a JSON object")
    balance = num(cash.get("balance"), "cash.balance")
    net_burn = num(cash.get("net_burn_monthly"), "cash.net_burn_monthly")
    if net_burn is None and cash.get("net_burn") is not None:
        net_burn = num(cash.get("net_burn"), "cash.net_burn")
        res["checks"]["burn_basis"] = "monthly (field 'net_burn')"
    else:
        res["checks"]["burn_basis"] = "monthly"

    if net_burn is not None:
        m["net_burn_monthly"] = net_burn
        res["definitions"]["burn"] = (
            "net burn per month; use a trailing 3-month average for planning")
    if balance is not None and net_burn:
        m["cash_balance"] = balance
        m["runway_months"] = balance / net_burn

    net_new_arr = m.get("net_new_arr")
    if net_new_arr is not None and net_burn is not None:
        m["burn_multiple"] = div(net_burn * (months or 1), net_new_arr)
    if net_burn is not None and revenue is not None and revenue > 0:
        m["fcf_margin"] = (-net_burn * (months or 1)) / revenue

    growth_annual = None
    if months:
        g = 1 + m["mrr_growth_pct"]
        growth_annual = g ** (12.0 / months) - 1 if g > 0 else -1.0
        m["mrr_growth_annualised"] = growth_annual

    if growth_annual is not None and m.get("fcf_margin") is not None:
        m["rule_of_40"] = (growth_annual + m["fcf_margin"]) * 100
        res["definitions"]["rule_of_40"] = (
            "annualised ARR growth % + FCF margin % for the period")
    if net_new_arr is not None and sm_spend:
        m["magic_number"] = net_new_arr / sm_spend
        res["definitions"]["magic_number"] = (
            "net new ARR over the period / S&M spend in the same period")

    # -- Layer 5: benchmarks and consistency -----------------------------
    res["benchmarks"] = benchmark_position(m, res["segment"])
    benchmark_flags(m, res["segment"], flag)
    consistency_flags(m, flag)

    return res


# ---------------------------------------------------------------------------
# benchmarks and flags
# ---------------------------------------------------------------------------

def benchmark_position(m: dict, segment: str) -> list:
    rows = []

    def add(name, value, good, great, direction, fmt):
        if value is None:
            return
        if direction == "higher":
            band = ("great" if value >= great else
                    "good" if value >= good else "below")
        else:
            band = ("great" if value <= great else
                    "good" if value <= good else "above")
        rows.append({"metric": name, "value": fmt(value),
                     "good_threshold": fmt(good), "band": band})

    add("NRR", m.get("nrr"), 1.0, 1.10, "higher", pct)
    add("GRR", m.get("grr"), 0.85, 0.90, "higher", pct)
    add("Quick ratio", m.get("quick_ratio"), 2.0, 4.0, "higher", ratio)
    add("LTV/CAC", m.get("ltv_cac"), 3.0, 4.0, "higher", ratio)
    add("Magic number", m.get("magic_number"), 0.75, 1.0, "higher", ratio)
    add("Burn multiple", m.get("burn_multiple"), 2.0, 1.0, "lower", ratio)
    add("Rule of 40", m.get("rule_of_40"), 40.0, 60.0, "higher",
        lambda v: "{:.0f}".format(v))

    payback = m.get("cac_payback_months")
    if payback is not None:
        good = {"smb": 12, "mid-market": 18, "enterprise": 24}.get(segment, 18)
        rows.append({"metric": "CAC payback (months)",
                     "value": "{:.1f}".format(payback),
                     "good_threshold": "<= {}".format(good),
                     "band": "good" if payback <= good else "above"})
    return rows


def benchmark_flags(m: dict, segment: str, flag) -> None:
    nrr = m.get("nrr")
    if nrr is not None:
        if nrr < 0.90:
            flag("high", "nrr",
                 "NRR {:.0f}% is well below 100%: the existing base is shrinking "
                 "and new logos are only masking it.".format(nrr * 100))
        elif nrr < 1.0:
            flag("medium", "nrr",
                 "NRR {:.0f}% is below 100%: expansion does not yet offset "
                 "contraction and churn.".format(nrr * 100))

    grr = m.get("grr")
    if grr is not None and grr < 0.80:
        flag("high", "grr",
             "GRR {:.0f}% means more than a fifth of the base leaks over the "
             "period before expansion; fix retention before scaling spend."
             .format(grr * 100))

    qr = m.get("quick_ratio")
    if qr is not None:
        if qr < 1.0:
            flag("high", "quick_ratio",
                 "Quick ratio {:.2f} is below 1.0: churn and contraction exceed "
                 "new and expansion revenue.".format(qr))
        elif qr < 2.0:
            flag("medium", "quick_ratio",
                 "Quick ratio {:.2f} is below the 2.0 reference; growth is not "
                 "comfortably outrunning leakage.".format(qr))

    lc = m.get("ltv_cac")
    if lc is not None:
        if lc < 1.0:
            flag("high", "ltv_cac",
                 "LTV/CAC {:.2f} is below 1.0: each customer destroys value. "
                 "Stop scaling acquisition.".format(lc))
        elif lc < 3.0:
            flag("high", "ltv_cac",
                 "LTV/CAC {:.2f} is below the 3.0 floor: fix retention, margin or "
                 "channel mix before adding spend.".format(lc))
        elif lc > 5.0:
            flag("medium", "ltv_cac",
                 "LTV/CAC {:.2f} is above 5.0: either the business is "
                 "under-investing in growth or the lifetime assumption is "
                 "optimistic. Verify the inputs.".format(lc))

    payback = m.get("cac_payback_months")
    if payback is not None:
        limit = {"smb": 12, "mid-market": 18, "enterprise": 24}.get(segment)
        if limit and payback > limit:
            flag("medium", "cac_payback",
                 "CAC payback {:.1f} months exceeds the {} norm of {} months."
                 .format(payback, segment, limit))

    bm = m.get("burn_multiple")
    if bm is not None:
        if bm < 0:
            flag("high", "burn_multiple",
                 "Negative burn multiple: net new ARR is negative while the "
                 "company is burning cash.")
        elif bm > 3.0:
            flag("high", "burn_multiple",
                 "Burn multiple {:.2f} means more than $3 burned per $1 of new "
                 "ARR. Growth is being bought.".format(bm))
        elif bm > 2.0:
            flag("medium", "burn_multiple",
                 "Burn multiple {:.2f} is above 2.0; acceptable only with a "
                 "stated reason.".format(bm))

    runway = m.get("runway_months")
    if runway is not None:
        if runway < 6:
            flag("high", "runway",
                 "Runway {:.1f} months is triage territory. Fundraise, cut, or "
                 "both now.".format(runway))
        elif runway < 12:
            flag("high", "runway",
                 "Runway {:.1f} months is below 12: this is a fundraising "
                 "trigger, not a planning detail.".format(runway))
        elif runway < 18:
            flag("medium", "runway",
                 "Runway {:.1f} months is thin for a company still hiring; model "
                 "the planned burn.".format(runway))

    r40 = m.get("rule_of_40")
    if r40 is not None and r40 < 40:
        flag("medium", "rule_of_40",
             "Rule of 40 score {:.0f} is below 40; name whether the fix is "
             "growth or margin.".format(r40))


def consistency_flags(m: dict, flag) -> None:
    cr = m.get("gross_revenue_churn_rate")
    lr = m.get("logo_churn_rate")
    if cr and lr:
        if lr > cr * 2:
            flag("medium", "churn_mix",
                 "Logo churn ({:.1f}%) is more than double revenue churn "
                 "({:.1f}%): small accounts are leaving and masking the trend. "
                 "Segment the cohort.".format(lr * 100, cr * 100))
        elif cr > lr * 2:
            flag("medium", "churn_mix",
                 "Revenue churn ({:.1f}%) is more than double logo churn "
                 "({:.1f}%): large accounts are downgrading. Check "
                 "concentration.".format(cr * 100, lr * 100))

    nrr = m.get("nrr")
    if nrr is not None and nrr > 1.5:
        flag("medium", "nrr",
             "NRR above 150% is unusual; verify that new business or "
             "reactivation is not in the numerator.")

    gm = m.get("gross_margin")
    if gm is not None and gm < 0.50:
        flag("high", "gross_margin",
             "Gross margin {:.0f}% is below 50%: the unit economics may not "
             "support a SaaS model at this price point.".format(gm * 100))


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def render_markdown(res: dict) -> str:
    m = res["metrics"]
    cur = res["currency"]
    out = []
    add = out.append

    add("# SaaS Metrics Pack — {}".format(res["company"]))
    add("")
    period = res.get("period") or {}
    if period:
        add("**Period:** {} → {}  ·  **Currency:** {}  ·  **Months:** {}  ·  "
            "**Segment:** {}".format(period.get("start", "?"), period.get("end", "?"),
                                     cur, res.get("months") or "?",
                                     res["segment"]))
    else:
        add("**Currency:** {}  ·  **Months:** {}  ·  **Segment:** {}"
            .format(cur, res.get("months") or "?", res["segment"]))
    add("")

    add("## Revenue")
    add("")
    add("| Metric | Value |")
    add("|---|---|")
    for label, value in [
        ("MRR (begin → end)", "{} → {}".format(money(m.get("mrr_begin"), cur),
                                               money(m.get("mrr_end"), cur))),
        ("ARR (begin → end)", "{} → {}".format(money(m.get("arr_begin"), cur),
                                               money(m.get("arr_end"), cur))),
        ("Net new MRR", money(m.get("net_new_mrr"), cur)),
        ("Net new ARR", money(m.get("net_new_arr"), cur)),
        ("MRR growth (period)", pct(m.get("mrr_growth_pct"))),
        ("ARPA (begin)", money(m.get("arpa_begin"), cur)),
        ("Customers (begin → end)", "{} → {}".format(
            count(m.get("customers_begin")), count(m.get("customers_end")))),
    ]:
        add("| {} | {} |".format(label, value))
    add("")

    if any(m.get(k) is not None for k in
           ("nrr", "grr", "quick_ratio", "gross_revenue_churn_rate")):
        add("## Retention")
        add("")
        add("| Metric | Value | Definition |")
        add("|---|---|---|")
        for label, value, definition in [
            ("Gross revenue churn (period)",
             pct(m.get("gross_revenue_churn_rate")),
             "(contraction + churn) / begin MRR"),
            ("Gross revenue churn (monthly)",
             pct(m.get("gross_revenue_churn_monthly")),
             "period rate de-annualised, not divided by 12"),
            ("Logo churn (period)", pct(m.get("logo_churn_rate")),
             "customers churned / customers begin"),
            ("GRR", pct(m.get("grr")),
             "(begin − contraction − churn) / begin"),
            ("NRR", pct(m.get("nrr")),
             "(begin + expansion − contraction − churn) / begin"),
            ("NRR incl. reactivation", pct(m.get("nrr_incl_reactivation")),
             "adds reactivation MRR to the numerator"),
            ("Quick ratio", ratio(m.get("quick_ratio")),
             "(new + expansion) / (churn + contraction)"),
        ]:
            if value != "n/a":
                add("| {} | {} | {} |".format(label, value, definition))
        add("")

    if any(m.get(k) is not None for k in
           ("cac_blended", "ltv", "ltv_cac", "cac_payback_months")):
        add("## Unit Economics")
        add("")
        add("| Metric | Value |")
        add("|---|---|")
        for label, value in [
            ("Gross margin", pct(m.get("gross_margin"))),
            ("Contribution margin", pct(m.get("contribution_margin"))),
            ("CAC (blended)", money(m.get("cac_blended"), cur)),
            ("CAC (paid)", money(m.get("cac_paid"), cur)),
            ("LTV (gross-margin basis)", money(m.get("ltv"), cur)),
            ("LTV lifetime", months_fmt(m.get("ltv_lifetime_months"))),
            ("LTV / CAC", ratio(m.get("ltv_cac"))),
            ("CAC payback", months_fmt(m.get("cac_payback_months"))),
            ("Magic number", ratio(m.get("magic_number"))),
        ]:
            if value != "n/a":
                add("| {} | {} |".format(label, value))
        add("")

    if any(m.get(k) is not None for k in
           ("runway_months", "burn_multiple", "rule_of_40")):
        add("## Cash and Efficiency")
        add("")
        add("| Metric | Value |")
        add("|---|---|")
        for label, value in [
            ("Cash balance", money(m.get("cash_balance"), cur)),
            ("Net burn (monthly)", money(m.get("net_burn_monthly"), cur)),
            ("Runway", months_fmt(m.get("runway_months"))),
            ("Burn multiple", ratio(m.get("burn_multiple"))),
            ("FCF margin", pct(m.get("fcf_margin"))),
            ("Rule of 40", ("{:.0f}".format(m["rule_of_40"])
                            if m.get("rule_of_40") is not None else "n/a")),
        ]:
            if value != "n/a":
                add("| {} | {} |".format(label, value))
        add("")

    if res.get("benchmarks"):
        add("## Benchmark Position")
        add("")
        add("Directional bands only — population: {} SaaS.".format(res["segment"]))
        add("")
        add("| Metric | Value | Good threshold | Band |")
        add("|---|---|---|---|")
        for row in res["benchmarks"]:
            add("| {metric} | {value} | {good_threshold} | {band} |".format(**row))
        add("")

    residual = res["checks"].get("mrr_bridge_residual")
    if residual is not None:
        add("**MRR bridge residual:** {}".format(money(residual, cur)))
        add("")

    add("## Flags")
    add("")
    if res["flags"]:
        for f in res["flags"]:
            add("- **{}** `{}` — {}".format(f["severity"].upper(),
                                           f["metric"], f["message"]))
    else:
        add("- No threshold breaches in the supplied inputs.")
    add("")

    if res.get("definitions"):
        add("## Definitions Used")
        add("")
        for key, value in sorted(res["definitions"].items()):
            add("- **{}**: {}".format(key, value))
        add("")

    add("---")
    add("Generated by `scripts/metrics_calculator.py`. Benchmarks are directional; "
        "cite the population before comparing.")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute a SaaS metrics pack from JSON input.")
    parser.add_argument("--input", required=True,
                        help="path to metrics input JSON")
    parser.add_argument("--output", choices=("json", "markdown"),
                        default="markdown",
                        help="output format (default: markdown)")
    parser.add_argument("--pretty", action="store_true",
                        help="pretty-print JSON output")
    args = parser.parse_args(argv)

    try:
        with open(args.input, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print("error: no such file: {}".format(args.input), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: {} is not valid JSON: {}".format(args.input, exc),
              file=sys.stderr)
        return 2

    try:
        result = calculate(data)
    except InputError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    if args.output == "json":
        print(json.dumps(result, indent=2 if args.pretty else None,
                         sort_keys=args.pretty, default=str))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
