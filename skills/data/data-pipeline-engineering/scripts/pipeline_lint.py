#!/usr/bin/env python3
"""Static lint for a data pipeline spec. Stdlib only, no installs.

Catches the design mistakes that cause production incidents (double-counted
revenue, silent data loss, unbackfillable pipelines) rather than style nits.

Usage:
    python3 pipeline_lint.py spec.json
    python3 pipeline_lint.py --json-stdin < spec.json
    python3 pipeline_lint.py spec.json --format text

Exit codes: 0 = no errors (warnings allowed), 1 = errors found, 3 = bad input.
"""

import argparse
import json
import re
import sys

REQUIRED_TOP = ["name", "owner", "tier", "sla_minutes"]
VALID_TIERS = {1, 2, 3}
VALID_MODES = {"incremental", "full_refresh", "append", "cdc"}
VALID_IDEMPOTENCY = {"merge", "partition_overwrite", "dedupe_view", "none"}
VALID_CHECKS = {"freshness", "volume", "uniqueness", "not_null",
                "referential", "distribution", "range", "enum"}
LARGE_TABLE_ROWS = 10_000_000
NON_DETERMINISTIC = re.compile(r"\bnow\(\)|CURRENT_TIMESTAMP|current_date|today\(\)",
                               re.IGNORECASE)


class Result:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, code, msg, hint=None):
        self.errors.append({"code": code, "message": msg, "hint": hint})

    def warn(self, code, msg, hint=None):
        self.warnings.append({"code": code, "message": msg, "hint": hint})

    def note(self, code, msg):
        self.info.append({"code": code, "message": msg})


def _get(d, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def lint(spec: dict) -> Result:
    r = Result()

    # ---- identity / ownership -------------------------------------------------
    for field in REQUIRED_TOP:
        if spec.get(field) in (None, "", []):
            r.error("missing_field", f"required field '{field}' is missing or empty",
                    "every pipeline needs an owner and an SLA, or nobody maintains it")

    tier = spec.get("tier")
    if tier is not None and tier not in VALID_TIERS:
        r.error("bad_tier", f"tier {tier!r} not in {sorted(VALID_TIERS)}",
                "use 1=pages, 2=ticket, 3=best effort")

    sla = spec.get("sla_minutes")
    if isinstance(sla, (int, float)) and sla <= 0:
        r.error("bad_sla", "sla_minutes must be > 0")

    schedule = spec.get("schedule")
    if not schedule:
        r.warn("no_schedule", "no schedule declared (event-driven pipeline?)",
               "if it is event-driven, add trigger metadata so freshness can be reasoned about")

    mode = spec.get("mode", "incremental")
    if mode not in VALID_MODES:
        r.error("bad_mode", f"mode {mode!r} not in {sorted(VALID_MODES)}")
    if mode == "append":
        r.warn("append_mode", "append mode duplicates rows on rerun unless the reader dedupes",
               "pair with a dedupe view keyed on the business key")

    # ---- partitioning ---------------------------------------------------------
    part_col = _get(spec, "partition", "column")
    scoped = _get(spec, "partition", "scoped_writes", default=None)
    if mode in {"incremental", "append", "cdc"} and not part_col:
        r.error("no_partition", f"{mode} pipeline has no partition.column",
                "partition by event_date or ingest_date; unpartitioned incremental loads cannot be replayed")
    if scoped is False:
        r.error("unscoped_writes", "partition.scoped_writes is false",
                "every run must write exactly one window; otherwise a rerun corrupts neighbours")
    if part_col and NON_DETERMINISTIC.search(str(part_col)):
        r.error("nondeterministic_partition",
                "partition column expression uses now()/CURRENT_TIMESTAMP",
                "derive the partition from the run's logical timestamp")

    if _get(spec, "determinism", "uses_now_for_partition") is True:
        r.error("nondeterministic_partition",
                "determinism.uses_now_for_partition is true",
                "reruns would target a different window than the original run")

    # ---- idempotency ----------------------------------------------------------
    strategy = _get(spec, "idempotency", "strategy")
    keys = _get(spec, "idempotency", "keys") or []
    if strategy is None:
        r.error("no_idempotency", "idempotency.strategy not declared",
                "declare merge | partition_overwrite | dedupe_view")
    elif strategy not in VALID_IDEMPOTENCY:
        r.error("bad_idempotency", f"idempotency.strategy {strategy!r} not in {sorted(VALID_IDEMPOTENCY)}")
    elif strategy == "none":
        r.error("no_idempotency", "idempotency.strategy is 'none' — reruns will duplicate data",
                "use partition_overwrite, merge on a business key, or a dedupe view")
    elif strategy in {"merge", "dedupe_view"}:
        if not keys:
            r.error("no_keys", f"{strategy} strategy requires idempotency.keys",
                    "e.g. [\"order_id\"] or a composite [\"account_id\", \"event_date\"]")
        elif len(set(keys)) != len(keys):
            r.error("duplicate_keys", f"idempotency.keys contains duplicates: {keys}")
        if strategy == "merge" and not any("updated" in str(k) or "ts" in str(k) for k in keys):
            r.warn("merge_keys", "merge keys look like pure identifiers, no version/timestamp column",
                   "verify the merge cannot let an older record overwrite a newer one")

    # ---- incremental state ----------------------------------------------------
    if mode == "incremental":
        wm_col = _get(spec, "watermark", "column")
        if not wm_col:
            r.error("no_watermark", "incremental pipeline has no watermark.column",
                    "read the high-watermark from the target and use a half-open window")
        if _get(spec, "watermark", "source") == "config":
            r.warn("watermark_from_config", "watermark is read from config rather than the target",
                   "config drifts from reality; read MAX(col) from the target")
        lookback = _get(spec, "watermark", "lookback_minutes", default=0)
        if isinstance(lookback, (int, float)) and lookback == 0:
            r.warn("no_lookback", "watermark lookback is 0 minutes — late-arriving rows will be lost",
                   "a small lookback plus an idempotent merge is the cheap fix")
    if mode == "cdc" and not _get(spec, "cdc", "delete_handling"):
        r.warn("cdc_deletes", "cdc pipeline does not declare delete_handling",
               "state how tombstones are applied (soft delete / hard delete)")

    # ---- deletes / append-only -------------------------------------------------
    if mode in {"incremental", "full_refresh"} and _get(spec, "deletes") is None:
        r.warn("no_delete_policy", "no deletes policy declared",
               "incremental loads silently lose source deletes; declare soft_delete | cdc | reconciliation")

    # ---- target size / cost ----------------------------------------------------
    rows = _get(spec, "target", "estimated_rows")
    if mode == "full_refresh" and isinstance(rows, (int, float)) and rows > LARGE_TABLE_ROWS:
        r.error("full_refresh_large",
                f"full_refresh on a ~{int(rows):,}-row target",
                "convert to partition-scoped incremental; a full refresh per run will dominate the warehouse bill")
    if isinstance(rows, (int, float)) and rows > LARGE_TABLE_ROWS:
        if not _get(spec, "target", "partition_filter_required", default=False):
            r.warn("no_partition_filter", "large target without a required partition filter",
                   "BigQuery: require_partition_filter=TRUE; Snowflake/Redshift: enforce in the query template")
        if not spec.get("cost_guardrail"):
            r.warn("no_cost_guardrail", "large target with no cost_guardrail declared",
                   "set maximum_bytes_billed / resource monitor / statement timeout")

    # ---- quality checks --------------------------------------------------------
    checks = spec.get("quality_checks") or []
    if not checks:
        r.error("no_quality_checks", "quality_checks is empty",
                "at minimum: freshness, volume, uniqueness on the business key")
    else:
        types = set()
        for i, chk in enumerate(checks):
            ctype = chk.get("type") if isinstance(chk, dict) else chk
            if ctype not in VALID_CHECKS:
                r.error("bad_check", f"quality_checks[{i}].type {ctype!r} not recognised",
                        f"valid: {sorted(VALID_CHECKS)}")
            types.add(ctype)
            if isinstance(chk, dict):
                if chk.get("blocking") is None and ctype in {"freshness", "volume"}:
                    r.warn("check_no_blocking", f"check '{ctype}' does not declare blocking true/false",
                           "block on freshness/volume for tier-1 tables, warn otherwise")
                if chk.get("threshold") is None and ctype in {"volume", "distribution", "not_null"}:
                    r.warn("check_no_threshold", f"check '{ctype}' has no threshold",
                           "a check without a number cannot fail")
        if "freshness" not in types and tier == 1:
            r.error("no_freshness", "tier-1 pipeline has no freshness check",
                    "staleness is the failure users notice first")
        if "volume" not in types:
            r.warn("no_volume", "no volume check",
                   "row-count vs trailing median catches 'upstream produced nothing'")

    # ---- backfill --------------------------------------------------------------
    bf = spec.get("backfill") or {}
    if not bf:
        r.warn("no_backfill", "no backfill config",
               "declare max_parallel and isolated_table so replay is a feature, not an incident")
    else:
        mp = bf.get("max_parallel")
        if mp is None:
            r.warn("backfill_unbounded", "backfill.max_parallel not set",
                   "an unbounded 400-partition backfill starves production queries")
        elif isinstance(mp, (int, float)) and mp > 16:
            r.warn("backfill_wide", f"backfill.max_parallel={mp}",
                   "check warehouse concurrency limits and use a separate compute pool/warehouse")
        if bf.get("isolated_table") is False:
            r.warn("backfill_in_place", "backfill writes directly to the live table",
                   "write to table_backfill and swap atomically")

    # ---- alerts / lineage ------------------------------------------------------
    if not spec.get("alerting") and tier == 1:
        r.warn("no_alerting", "tier-1 pipeline declares no alerting target",
               "alerts without a destination are not alerting")
    if not spec.get("lineage"):
        r.warn("no_lineage", "no lineage declared",
               "name upstream assets/tables so a wrong mart can be traced")

    # ---- determinism in SQL ----------------------------------------------------
    for i, sql in enumerate(spec.get("sql") or []):
        if NON_DETERMINISTIC.search(str(sql)):
            r.warn("sql_nondeterministic", f"sql[{i}] contains now()/CURRENT_TIMESTAMP",
                   "bind the logical run timestamp as a parameter instead")

    if not r.errors and not r.warnings:
        r.note("clean", "no issues found")
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint a data pipeline spec (JSON).")
    ap.add_argument("path", nargs="?", help="path to spec.json (omit with --json-stdin)")
    ap.add_argument("--json-stdin", action="store_true", help="read spec from stdin")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args(argv)

    try:
        raw = sys.stdin.read() if args.json_stdin or not args.path else open(args.path).read()
        spec = json.loads(raw)
        if not isinstance(spec, dict):
            raise ValueError("spec root must be a JSON object")
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(json.dumps({"valid": False, "error": f"cannot read spec: {exc}"}, indent=2))
        return 3

    r = lint(spec)
    report = {
        "valid": not r.errors,
        "pipeline": spec.get("name", "<unnamed>"),
        "errors": r.errors,
        "warnings": r.warnings,
        "info": r.info,
        "summary": {
            "errors": len(r.errors),
            "warnings": len(r.warnings),
        },
    }
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"pipeline: {report['pipeline']}")
        for e in r.errors:
            print(f"  ERROR   [{e['code']}] {e['message']}")
            if e.get("hint"):
                print(f"          -> {e['hint']}")
        for w in r.warnings:
            print(f"  WARN    [{w['code']}] {w['message']}")
            if w.get("hint"):
                print(f"          -> {w['hint']}")
        print(f"{report['summary']['errors']} error(s), {report['summary']['warnings']} warning(s)")
    return 0 if not r.errors else 1


if __name__ == "__main__":
    sys.exit(main())
