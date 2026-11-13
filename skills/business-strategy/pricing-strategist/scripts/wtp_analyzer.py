#!/usr/bin/env python3
"""Van Westendorp Price Sensitivity Meter (PSM) over survey responses.

Stdlib only. Computes the four canonical intersection points and the Range of
Acceptable Prices. Emits a range, never a single recommended price.

Usage:
    python3 wtp_analyzer.py --input survey.json --output markdown
    python3 wtp_analyzer.py --input survey.json --output json

survey.json:
    {
      "currency": "USD",
      "respondents": [
        {"too_cheap": 50, "bargain": 150, "expensive": 400, "too_expensive": 900,
         "purchase_intent": 4}
      ]
    }

purchase_intent (1-5) is optional and enables the Newton-Miller-Smith extension.
"""
from __future__ import annotations

import argparse
import json
import sys

FIELDS = ["too_cheap", "bargain", "expensive", "too_expensive"]
MIN_N = 30


def _pct(share: float) -> float:
    return round(share * 100.0, 2)


def load_respondents(path: str):
    """Return (respondents, currency, warnings) or raise ValueError."""
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        respondents = payload
        currency = "USD"
    elif isinstance(payload, dict):
        respondents = payload.get("respondents", [])
        currency = payload.get("currency", "USD")
    else:
        raise ValueError("survey.json must be an object with 'respondents' or a bare array")

    if not isinstance(respondents, list):
        raise ValueError("'respondents' must be a list")

    warnings = []
    clean = []
    dropped = 0
    for index, row in enumerate(respondents):
        if not isinstance(row, dict):
            dropped += 1
            continue
        try:
            values: dict = {field: float(row[field]) for field in FIELDS}
        except (KeyError, TypeError, ValueError):
            dropped += 1
            continue
        if any(v < 0 for v in values.values()):
            dropped += 1
            continue
        intent = row.get("purchase_intent")
        try:
            values["purchase_intent"] = float(intent) if intent is not None else None
        except (TypeError, ValueError):
            values["purchase_intent"] = None
        clean.append(values)

    if dropped:
        warnings.append("Dropped {} malformed respondent(s) (missing/non-numeric/negative fields).".format(dropped))
    if not clean:
        raise ValueError("no usable respondents after cleaning")
    return clean, currency, warnings


def check_ordering(respondents: list) -> dict:
    """Count respondents whose four thresholds violate the expected monotonic order."""
    violations = 0
    examples = []
    for row in respondents:
        if not (row["too_cheap"] <= row["bargain"] <= row["expensive"] <= row["too_expensive"]):
            violations += 1
            if len(examples) < 3:
                examples.append({f: row[f] for f in FIELDS})
    return {
        "count": violations,
        "share": round(violations / len(respondents) * 100.0, 2),
        "examples": examples,
    }


def build_grid(respondents: list, steps: int = 400) -> list:
    values = [row[f] for row in respondents for f in FIELDS]
    low, high = min(values), max(values)
    if high <= low:
        return [low]
    step = (high - low) / steps
    return [round(low + i * step, 4) for i in range(steps + 1)]


def curves_at(respondents: list, price: float) -> dict:
    """Cumulative PSM curves at a given price, as proportions in [0, 1]."""
    n = float(len(respondents))
    # A price is 'too cheap' while it sits at or below the respondent's too_cheap threshold.
    too_cheap = sum(1 for r in respondents if price <= r["too_cheap"]) / n
    # A price is 'a bargain' while it sits at or below the respondent's bargain threshold.
    bargain = sum(1 for r in respondents if price <= r["bargain"]) / n
    # A price is 'expensive' once it reaches the respondent's expensive threshold.
    expensive = sum(1 for r in respondents if price >= r["expensive"]) / n
    # A price is 'too expensive' once it reaches the respondent's too_expensive threshold.
    too_expensive = sum(1 for r in respondents if price >= r["too_expensive"]) / n
    return {
        "too_cheap": too_cheap,
        "bargain": bargain,
        "expensive": expensive,
        "too_expensive": too_expensive,
    }


def _interpolate(p1, v1, p2, v2) -> float:
    if v2 == v1:
        return round(p1, 2)
    return round(p1 + (0.0 - v1) * (p2 - p1) / (v2 - v1), 2)


def find_intersection(grid: list, series_a: list, series_b: list):
    """First genuine sign change between the two series.

    Plateaus where both curves sit at the same value (commonly 0 below the
    expensive zone) are not crossings -- an intersection exists only where the
    difference actually changes sign between two non-zero values.
    """
    prev = None
    for price, a, b in zip(grid, series_a, series_b):
        diff = a - b
        if abs(diff) < 1e-12:
            # Equal at this price: hold the last non-zero anchor so the plateau
            # is not mistaken for an intersection.
            continue
        if prev is not None and (prev[1] < 0) != (diff < 0):
            return _interpolate(prev[0], prev[1], price, diff)
        prev = (price, diff)
    return None


def analyze(respondents: list, nms_lambda=None) -> dict:
    grid = build_grid(respondents)
    rows = [curves_at(respondents, p) for p in grid]

    too_cheap = [r["too_cheap"] for r in rows]
    bargain = [r["bargain"] for r in rows]
    expensive = [r["expensive"] for r in rows]
    too_expensive = [r["too_expensive"] for r in rows]

    points = {
        "OPP": find_intersection(grid, too_cheap, too_expensive),
        "IDP": find_intersection(grid, bargain, expensive),
        "PMC": find_intersection(grid, too_cheap, expensive),
        "PME": find_intersection(grid, bargain, too_expensive),
    }

    # Sanity: PMC is the floor, PME the ceiling.
    if points["PMC"] is not None and points["PME"] is not None and points["PMC"] > points["PME"]:
        points["PMC"], points["PME"] = points["PME"], points["PMC"]

    sampled = []
    for i in range(0, len(grid), max(1, len(grid) // 10)):
        row = dict(rows[i])
        row["price"] = round(grid[i], 2)
        sampled.append(row)

    result = {
        "n": len(respondents),
        "points": points,
        "range_of_acceptable_prices": [points["PMC"], points["PME"]],
        "acceptable_band": [points["IDP"], points["OPP"]],
        "ordering_check": check_ordering(respondents),
        "curves": sampled,
        "warnings": [],
    }

    if points["PMC"] and points["PME"]:
        result["range_ratio"] = round(points["PME"] / points["PMC"], 2)

    if nms_lambda is not None:
        result["newton_miller_smith"] = _nms(respondents, points, nms_lambda)

    return result


def _nms(respondents: list, points: dict, lam: float) -> dict:
    """Newton-Miller-Smith purchase-intent discount applied to the PSM points.

    Interpreting lam as the expected share of respondents who actually buy at a
    given point, the NMS price is the PSM point scaled toward the marginal buyer.
    Reported as a guide, not a prescription.
    """
    scale = 1.0 - max(0.0, min(1.0, lam))
    adjusted = {}
    for key, value in points.items():
        adjusted[key] = round(value * scale, 2) if value is not None else None
    return {
        "lambda": lam,
        "scale_factor": round(scale, 4),
        "adjusted_points": adjusted,
        "note": "Newton-Miller-Smith discounts the PSM points by expected purchase intent; "
                "use it to test downside scenarios, not to set the list price.",
    }


def infer_lambda(respondents: list):
    intents = [r["purchase_intent"] for r in respondents if r.get("purchase_intent") is not None]
    if len(intents) < max(5, int(0.5 * len(respondents))):
        return None
    return round(sum(intents) / len(intents) / 5.0, 4)


def render_markdown(result: dict, currency: str) -> str:
    pts = result["points"]
    lines = []
    fmt = lambda v: "n/a" if v is None else "{:,.2f} {}".format(v, currency)

    lines.append("# Willingness to Pay — Van Westendorp PSM")
    lines.append("")
    lines.append("N = **{}** respondents · currency `{}`".format(result["n"], currency))
    if result["n"] < MIN_N:
        lines.append("")
        lines.append("> ⚠️ N is below 30. Directional only — do not treat these curves as evidence.")
    lines.append("")
    lines.append("## Intersection Points")
    lines.append("")
    lines.append("| Point | Meaning | Price |")
    lines.append("|-------|---------|-------|")
    lines.append("| PMC | Point of Marginal Cheapness — too cheap vs. expensive | {} |".format(fmt(pts["PMC"])))
    lines.append("| PME | Point of Marginal Expensiveness — not a bargain vs. too expensive | {} |".format(fmt(pts["PME"])))
    lines.append("| OPP | Optimal Price Point — too cheap vs. too expensive | {} |".format(fmt(pts["OPP"])))
    lines.append("| IDP | Indifference Price Point — bargain vs. expensive | {} |".format(fmt(pts["IDP"])))
    lines.append("")
    if result["range_of_acceptable_prices"][0] is not None:
        lines.append("## Range of Acceptable Prices")
        lines.append("")
        lines.append(
            "**{} → {}**".format(fmt(pts["PMC"]), fmt(pts["PME"]))
        )
        if "range_ratio" in result:
            lines.append("")
            lines.append("Ceiling is {:.2f}x the floor.".format(result["range_ratio"]))
            if result["range_ratio"] > 2.0:
                lines.append("")
                lines.append("A ceiling more than 2x the floor usually means the sample is bimodal — "
                             "split it by segment and run the analysis twice.")
    else:
        lines.append("## Range of Acceptable Prices")
        lines.append("")
        lines.append("Could not resolve a range — the curves do not cross within the observed data. "
                     "Check for identical or inverted thresholds.")
    lines.append("")
    lines.append("## How to Read This")
    lines.append("")
    lines.append("- **Floor** (PMC): below this, buyers doubt quality.")
    lines.append("- **Ceiling** (PME): above this, buyers stop considering you.")
    lines.append("- **List price** sits at or just under IDP; discount down toward PMC, never below.")
    lines.append("- **OPP is not the price.** It is the point where equal shares call you cheap and expensive.")
    lines.append("")
    lines.append("## Curve Sample")
    lines.append("")
    lines.append("| Price | Too cheap | Bargain | Expensive | Too expensive |")
    lines.append("|-------|-----------|---------|-----------|---------------|")
    for row in result["curves"]:
        lines.append("| {:,.2f} | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% |".format(
            row["price"], _pct(row["too_cheap"]), _pct(row["bargain"]),
            _pct(row["expensive"]), _pct(row["too_expensive"])))
    lines.append("")

    ordering = result["ordering_check"]
    if ordering["count"]:
        lines.append("## Data Quality")
        lines.append("")
        lines.append(
            "{} respondents ({:.2f}%) reported thresholds out of order "
            "(expected too_cheap ≤ bargain ≤ expensive ≤ too_expensive). "
            "They were kept, but review the raw rows.".format(ordering["count"], ordering["share"])
        )
        for example in ordering["examples"]:
            lines.append("- `{}`".format(json.dumps(example)))
        lines.append("")

    if "newton_miller_smith" in result:
        nms = result["newton_miller_smith"]
        lines.append("## Newton-Miller-Smith Extension")
        lines.append("")
        lines.append("Discount factor λ = {} (mean purchase intent / 5).".format(nms["lambda"]))
        lines.append("")
        for key, value in nms["adjusted_points"].items():
            lines.append("- {} adjusted: {}".format(key, fmt(value)))
        lines.append("")
        lines.append(nms["note"])
        lines.append("")

    for warning in result["warnings"]:
        lines.append("- ⚠️ " + warning)
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Van Westendorp Price Sensitivity Meter.")
    parser.add_argument("--input", required=True, help="Path to survey.json")
    parser.add_argument("--output", default="markdown", choices=["markdown", "json"], help="Output format")
    parser.add_argument("--min-n", type=int, default=MIN_N, help="Minimum respondents before a warning (default 30)")
    parser.add_argument("--nms", action="store_true", help="Force the Newton-Miller-Smith extension")
    args = parser.parse_args(argv)

    try:
        respondents, currency, warnings = load_respondents(args.input)
    except OSError as exc:
        print("error: cannot read {}: {}".format(args.input, exc), file=sys.stderr)
        return 2
    except (json.JSONDecodeError, ValueError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    lam = infer_lambda(respondents) if args.nms else None
    if args.nms and lam is None:
        warnings.append("--nms requested but too few respondents supplied 'purchase_intent'; extension skipped.")

    result = analyze(respondents, nms_lambda=lam)
    result["warnings"] = warnings + result["warnings"]

    if result["n"] < args.min_n:
        result["warnings"].insert(
            0,
            "N = {} is below the minimum of {}. Results are directional only.".format(result["n"], args.min_n),
        )

    if args.output == "json":
        payload = dict(result)
        payload["currency"] = currency
        print(json.dumps(payload, indent=2))
    else:
        print(render_markdown(result, currency))
    return 0


if __name__ == "__main__":
    sys.exit(main())
