#!/usr/bin/env python3
"""eval_gate.py — apply G1-G4 quality gates to an eval run.

Usage:
  python3 eval_gate.py --results run.json --baseline baseline.json [--json]
  python3 eval_gate.py --selftest

Expected run/baseline shape (metrics optional except pass_rate):
{
  "suite": "support",
  "n": 200,
  "metrics": {"pass_rate": 0.91, "safety_violations": 0,
              "format_pass_rate": 1.0, "usd_per_request": 0.0021,
              "p95_latency_ms": 3100},
  "items": [{"id": "refund-014", "slice": "billing/refund", "passed": true}, ...]
}

Exit code 0 = all gates pass, 1 = gate failure, 2 = bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

DEFAULT_TOLERANCE = 0.03          # 3 points
MIN_SLICE_N = 20


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - margin) / denom, (centre + margin) / denom)


def load_rates(run: dict) -> tuple[float, int]:
    """Derive pass rate from items when present, else trust metrics."""
    items = run.get("items") or []
    if items:
        n = len(items)
        k = sum(1 for i in items if i.get("passed"))
        return (k / n, n)
    n = int(run.get("n") or 0)
    rate = run.get("metrics", {}).get("pass_rate")
    if rate is None:
        raise ValueError("run has neither items nor metrics.pass_rate")
    return (float(rate), n)


def slice_rates(items: list[dict]) -> dict[str, tuple[int, int]]:
    out: dict[str, list[int]] = {}
    for item in items:
        bucket = out.setdefault(item.get("slice", "unspecified"), [0, 0])
        bucket[0] += 1
        bucket[1] += 1 if item.get("passed") else 0
    return {k: (v[1], v[0]) for k, v in sorted(out.items())}


def evaluate_gates(run: dict, baseline: dict, tolerance: float) -> tuple[list[dict], dict]:
    checks: list[dict] = []
    rate, n = load_rates(run)
    b_rate, b_n = load_rates(baseline)
    metrics = run.get("metrics", {})
    b_metrics = baseline.get("metrics", {})

    def add(gate: str, ok: bool, detail: str) -> None:
        checks.append({"gate": gate, "pass": bool(ok), "detail": detail})

    # G1 — absolute floors
    safety = metrics.get("safety_violations")
    if safety is not None:
        add("G1.safety", safety == 0, f"safety_violations={safety} (require 0)")
    fmt = metrics.get("format_pass_rate")
    if fmt is not None:
        add("G1.format", fmt >= 1.0, f"format_pass_rate={fmt:.3f} (require 1.0)")

    # G2 — non-inferiority, statistical floor
    se = math.sqrt(rate * (1 - rate) / max(n, 1) + b_rate * (1 - b_rate) / max(b_n, 1))
    stat_tol = max(tolerance, 1.96 * se)
    lo, hi = wilson(round(rate * n), n)
    add(
        "G2.non_inferiority",
        rate >= b_rate - stat_tol,
        f"pass_rate={rate:.3f} vs baseline={b_rate:.3f} "
        f"tol={stat_tol:.3f} (stat {1.96 * se:.3f}) n={n} CI=({lo:.3f},{hi:.3f})",
    )

    # G3 — per-slice regression
    items = run.get("items") or []
    b_items = baseline.get("items") or []
    if items and b_items:
        cur, base = slice_rates(items), slice_rates(b_items)
        for name, (k, total) in cur.items():
            if name not in base or total < MIN_SLICE_N:
                continue
            bk, bt = base[name]
            cur_rate, base_rate = k / total, bk / bt
            se_s = math.sqrt(
                cur_rate * (1 - cur_rate) / total + base_rate * (1 - base_rate) / bt
            )
            allowed = max(0.05, 1.96 * se_s)
            add(
                f"G3.slice:{name}",
                cur_rate >= base_rate - allowed,
                f"{cur_rate:.3f} vs {base_rate:.3f} allowed_drop={allowed:.3f} n={total}",
            )

    # G4 — budget
    usd, b_usd = metrics.get("usd_per_request"), b_metrics.get("usd_per_request")
    if usd is not None and b_usd is not None:
        add("G4.cost", usd <= b_usd * 1.10, f"usd/req={usd:.5f} baseline={b_usd:.5f} (max +10%)")
    p95, b_p95 = metrics.get("p95_latency_ms"), b_metrics.get("p95_latency_ms")
    if p95 is not None and b_p95 is not None:
        add("G4.latency", p95 <= b_p95 * 1.20, f"p95={p95}ms baseline={b_p95}ms (max +20%)")

    summary = {
        "suite": run.get("suite", "unknown"),
        "n": n,
        "pass_rate": round(rate, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "baseline_pass_rate": round(b_rate, 4),
        "applied_tolerance": round(stat_tol, 4),
        "slices": {
            name: {
                "n": total,
                "pass_rate": round(k / total, 4),
                "ci95": [round(x, 4) for x in wilson(k, total)],
            }
            for name, (k, total) in (slice_rates(items).items() if items else [])
        },
        "gate_pass": all(c["pass"] for c in checks),
    }
    return checks, summary


def selftest() -> int:
    baseline = {
        "suite": "support",
        "items": [
            {"id": f"a{i}", "slice": "billing/refund" if i % 2 else "general", "passed": True}
            for i in range(40)
        ],
        "metrics": {"safety_violations": 0, "format_pass_rate": 1.0,
                    "usd_per_request": 0.0020, "p95_latency_ms": 3000},
    }
    good = json.loads(json.dumps(baseline))
    bad = json.loads(json.dumps(baseline))
    for item in bad["items"][:12]:          # 30% of the set now fails
        item["passed"] = False

    c1, s1 = evaluate_gates(good, baseline, DEFAULT_TOLERANCE)
    c2, s2 = evaluate_gates(bad, baseline, DEFAULT_TOLERANCE)
    print("good:", s1["gate_pass"], [c["gate"] for c in c1 if not c["pass"]])
    print("bad :", s2["gate_pass"], [c["gate"] for c in c2 if not c["pass"]])
    ok = s1["gate_pass"] and not s2["gate_pass"]
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results")
    ap.add_argument("--baseline")
    ap.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not (args.results and args.baseline):
        ap.error("--results and --baseline are required (or use --selftest)")

    try:
        run = json.load(open(args.results))
        baseline = json.load(open(args.baseline))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    checks, summary = evaluate_gates(run, baseline, args.tolerance)
    if args.json:
        print(json.dumps({"summary": summary, "checks": checks}, indent=2))
    else:
        print(f"suite={summary['suite']} n={summary['n']} "
              f"pass={summary['pass_rate']:.3f} CI95={summary['ci95']} "
              f"baseline={summary['baseline_pass_rate']:.3f}")
        for name, s in summary["slices"].items():
            print(f"  slice {name:<24} n={s['n']:<4} pass={s['pass_rate']:.3f} CI95={s['ci95']}")
        print("-" * 64)
        for c in checks:
            print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['gate']:<28} {c['detail']}")
        print("-" * 64)
        print("GATE:", "PASS" if summary["gate_pass"] else "FAIL")
    return 0 if summary["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
