#!/usr/bin/env python3
"""Freshness, gap and volume checks over pipeline partition records. Stdlib only.

Input (JSON):
    {
      "tables": [
        {
          "table": "warehouse.orders",
          "cadence_minutes": 1440,
          "sla_minutes": 2880,
          "partitions": [
            {"date": "2026-11-11", "rows": 41200, "max_event_ts": "2026-11-12T00:05:00Z"},
            {"date": "2026-11-12", "rows": 39880, "max_event_ts": "2026-11-13T00:07:00Z"}
          ]
        }
      ]
    }

Usage:
    python3 data_freshness_check.py state.json --as-of 2026-11-13T09:00:00Z
    python3 data_freshness_check.py state.json --cadence-minutes 60 --sla-multiple 2

Exit codes: 0 = all ok, 1 = warnings only, 2 = failures (stale / missing / volume).
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone

VOLUME_LOW = 0.5    # fail below 50% of trailing median
VOLUME_HIGH = 2.0   # fail above 200% of trailing median
VOLUME_WARN_LOW = 0.75
VOLUME_WARN_HIGH = 1.5
BASELINE_WINDOW = 7


def parse_ts(value):
    """Parse ISO-8601 into an aware UTC datetime. Returns None on failure."""
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            try:
                dt = datetime.strptime(text[:10], "%Y-%m-%d")
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_date(value):
    dt = parse_ts(value)
    return dt.date() if dt else None


def expected_dates(observed, as_of, cadence_minutes):
    """Partition dates whose window has already closed by `as_of` (UTC datetime).

    A daily partition dated D is due once as_of >= D + 1 day, so the in-progress
    period is never reported as missing.
    """
    dates = sorted(d for d in set(observed) if d is not None)
    if not dates:
        return []
    start = dates[0]
    step = timedelta(days=1 if cadence_minutes >= 1440
                     else max(1, round(cadence_minutes / 1440)))
    out, cur = [], start
    while cur <= as_of.date() and len(out) < 5000:
        # window for partition `cur` closes at cur 00:00 + cadence
        closes = datetime.combine(cur, datetime.min.time(), tzinfo=timezone.utc) \
            + timedelta(minutes=cadence_minutes)
        if closes <= as_of:
            out.append(cur)
        cur = cur + step
    return out


def analyze_table(tbl, as_of, defaults):
    cadence = tbl.get("cadence_minutes", defaults["cadence"])
    sla = tbl.get("sla_minutes") or cadence * defaults["sla_multiple"]
    dated = []
    for p in tbl.get("partitions", []):
        day = parse_date(p.get("date"))
        if day is not None:
            dated.append((day, p))
    dated.sort(key=lambda pair: pair[0])
    parts = [p for _, p in dated]

    findings = {"table": tbl.get("table", "<unnamed>"), "cadence_minutes": cadence,
                "sla_minutes": sla, "status": "ok", "warnings": [], "failures": [],
                "metrics": {}}

    if not parts:
        findings["status"] = "fail"
        findings["failures"].append("no usable partition records")
        return findings

    # --- freshness: lag between newest event and now ---------------------------
    event_times = [parse_ts(p.get("max_event_ts")) for p in parts]
    event_times = [t for t in event_times if t]
    newest = max(event_times) if event_times else None
    if newest is None:
        findings["warnings"].append("no max_event_ts on any partition; freshness unknown")
        lag = None
    else:
        lag = (as_of - newest).total_seconds() / 60.0
        findings["metrics"]["lag_minutes"] = round(lag, 1)
        findings["metrics"]["last_event_ts"] = newest.isoformat().replace("+00:00", "Z")
        if lag > sla:
            findings["failures"].append(
                f"stale: lag {lag:.0f}m exceeds SLA {sla:.0f}m")
        elif lag > sla * 0.75:
            findings["warnings"].append(
                f"approaching SLA: lag {lag:.0f}m vs {sla:.0f}m")

    # --- gaps ------------------------------------------------------------------
    exp = expected_dates([d for d, _ in dated], as_of, cadence)
    have = {d for d, _ in dated}
    missing = [d.isoformat() for d in exp if d not in have]
    findings["metrics"]["partitions_present"] = len(have)
    findings["metrics"]["partitions_expected"] = len(exp)
    if missing:
        findings["failures"].append(
            f"missing {len(missing)} partition(s): {', '.join(missing[:5])}"
            + (" ..." if len(missing) > 5 else ""))

    # --- volume anomalies vs trailing median -----------------------------------
    anomalies, checked = [], 0
    rows_series = [(day, p.get("rows")) for day, p in dated]
    for i, (day, rows) in enumerate(rows_series):
        if not isinstance(rows, (int, float)) or i < 2:
            continue
        window = [r for _, r in rows_series[max(0, i - BASELINE_WINDOW):i]
                  if isinstance(r, (int, float))]
        if len(window) < 2:
            continue
        baseline = statistics.median(window)
        if baseline <= 0:
            continue
        checked += 1
        ratio = rows / baseline
        if ratio < VOLUME_LOW or ratio > VOLUME_HIGH:
            anomalies.append({"date": day.isoformat(), "rows": rows,
                              "baseline_median": baseline, "ratio": round(ratio, 3),
                              "severity": "fail"})
        elif ratio < VOLUME_WARN_LOW or ratio > VOLUME_WARN_HIGH:
            anomalies.append({"date": day.isoformat(), "rows": rows,
                              "baseline_median": baseline, "ratio": round(ratio, 3),
                              "severity": "warn"})
    findings["metrics"]["partitions_volume_checked"] = checked
    if anomalies:
        findings["metrics"]["volume_anomalies"] = anomalies
        for a in anomalies:
            msg = (f"volume {a['severity']}: {a['date']} rows={a['rows']} "
                   f"({a['ratio']:.2f}x median {a['baseline_median']:.0f})")
            (findings["failures"] if a["severity"] == "fail"
             else findings["warnings"]).append(msg)

    if findings["failures"]:
        findings["status"] = "fail"
    elif findings["warnings"]:
        findings["status"] = "warn"
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description="Freshness/volume/gap check for pipeline partitions.")
    ap.add_argument("path", nargs="?", help="state.json (omit with --json-stdin)")
    ap.add_argument("--json-stdin", action="store_true")
    ap.add_argument("--as-of", default=None, help="ISO timestamp to evaluate against (default: now UTC)")
    ap.add_argument("--cadence-minutes", type=int, default=1440,
                    help="default partition cadence (default 1440 = daily)")
    ap.add_argument("--sla-multiple", type=float, default=2.0,
                    help="default SLA as a multiple of cadence (default 2x)")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args(argv)

    as_of = parse_ts(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if as_of is None:
        print(json.dumps({"error": f"unparseable --as-of value: {args.as_of!r}"}))
        return 3

    try:
        raw = sys.stdin.read() if args.json_stdin or not args.path else open(args.path).read()
        state = json.loads(raw)
        tables = state["tables"] if isinstance(state, dict) else state
        if not isinstance(tables, list):
            raise ValueError("expected a list of tables (or {'tables': [...]})")
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(json.dumps({"error": f"cannot read state: {exc}"}))
        return 3

    defaults = {"cadence": args.cadence_minutes, "sla_multiple": args.sla_multiple}
    results = [analyze_table(t, as_of, defaults) for t in tables]
    overall = "ok"
    if any(r["status"] == "fail" for r in results):
        overall = "fail"
    elif any(r["status"] == "warn" for r in results):
        overall = "warn"

    report = {"as_of": as_of.isoformat().replace("+00:00", "Z"),
              "overall_status": overall, "tables": results}

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"as of {report['as_of']}  ->  {overall.upper()}")
        for r in results:
            m = r["metrics"]
            print(f"\n{r['table']}  [{r['status']}]  cadence={r['cadence_minutes']}m "
                  f"sla={r['sla_minutes']}m")
            if "lag_minutes" in m:
                print(f"  lag: {m['lag_minutes']}m  last event: {m.get('last_event_ts')}")
            if "partitions_expected" in m:
                print(f"  partitions: {m['partitions_present']}/{m['partitions_expected']}")
            for f in r["failures"]:
                print(f"  FAIL {f}")
            for w in r["warnings"]:
                print(f"  WARN {w}")

    if overall == "fail":
        return 2
    if overall == "warn":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
