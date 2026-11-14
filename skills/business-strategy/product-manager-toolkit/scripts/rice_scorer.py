#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""RICE scorer — rank product backlog items by (Reach x Impact x Confidence) / Effort.

Input: JSON file (or stdin) with a list of items, either bare or under "items".
    {
      "cycle": "2026-Q1",
      "items": [
        {"name": "Bulk CSV import", "reach": 1400, "impact": 2,
         "confidence": 0.8, "effort": 6, "notes": "12 tickets + 3 interviews"}
      ]
    }

impact     : 3 | 2 | 1 | 0.5 | 0.25   (massive | high | medium | low | minimal)
confidence : 0-1, or 0-100 (a value > 1 is read as a percentage)
effort     : person-weeks, > 0

Usage:
    python3 rice_scorer.py features.json
    python3 rice_scorer.py features.json --output json
    python3 rice_scorer.py - < features.json

Exit codes: 0 ok, 1 invalid input, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import sys

VALID_IMPACT = {3.0: "massive", 2.0: "high", 1.0: "medium", 0.5: "low", 0.25: "minimal"}

LOW_CONFIDENCE = 0.5   # at or below: treat as a research task, not a build task
LOW_REACH = 0          # sanity floor


class InputError(ValueError):
    """Raised when the input document is structurally or numerically invalid."""


def _as_number(value, field: str, idx: int):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"item {idx}: '{field}' must be a number, got {type(value).__name__}")
    return float(value)


def load_items(raw: str) -> tuple[list[dict], str]:
    """Parse and validate the input document. Returns (items, cycle_label)."""
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"input is not valid JSON: {exc}") from exc

    cycle = ""
    if isinstance(doc, dict):
        cycle = str(doc.get("cycle", "") or "")
        items = doc.get("items")
        if items is None:
            raise InputError("input object has no 'items' array")
    elif isinstance(doc, list):
        items = doc
    else:
        raise InputError("input must be a JSON array of items or an object with 'items'")
    if not isinstance(items, list) or not items:
        raise InputError("'items' must be a non-empty array")

    seen = set()
    cleaned = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise InputError(f"item {idx}: must be an object")
        name = str(item.get("name", "") or "").strip()
        if not name:
            raise InputError(f"item {idx}: missing 'name'")
        if name in seen:
            raise InputError(f"item {idx}: duplicate name '{name}'")
        seen.add(name)

        for field in ("reach", "impact", "confidence", "effort"):
            if field not in item:
                raise InputError(f"item '{name}': missing '{field}'")

        reach = _as_number(item["reach"], "reach", idx)
        impact = _as_number(item["impact"], "impact", idx)
        confidence = _as_number(item["confidence"], "confidence", idx)
        effort = _as_number(item["effort"], "effort", idx)

        if reach < LOW_REACH:
            raise InputError(f"item '{name}': reach must be >= 0 (got {reach:g})")
        if impact not in VALID_IMPACT:
            allowed = ", ".join(f"{k:g}" for k in sorted(VALID_IMPACT, reverse=True))
            raise InputError(f"item '{name}': impact must be one of {allowed} (got {impact:g})")
        if confidence > 1:
            if confidence > 100:
                raise InputError(f"item '{name}': confidence must be 0-1 or 0-100 (got {confidence:g})")
            confidence = confidence / 100.0
        if confidence < 0:
            raise InputError(f"item '{name}': confidence must be >= 0 (got {confidence:g})")
        if effort <= 0:
            raise InputError(f"item '{name}': effort must be > 0 (got {effort:g})")

        cleaned.append(
            {
                "name": name,
                "reach": reach,
                "impact": impact,
                "confidence": round(confidence, 4),
                "effort": effort,
                "notes": str(item.get("notes", "") or "").strip(),
                "score": round((reach * impact * confidence) / effort, 2),
            }
        )

    return cleaned, cycle


def analyse(items: list[dict]) -> tuple[list[dict], dict]:
    """Attach flags and rank. Flags never change the score — they annotate it."""
    efforts = sorted(i["effort"] for i in items)
    mid = len(efforts) // 2
    median_effort = efforts[mid] if len(efforts) % 2 else (efforts[mid - 1] + efforts[mid]) / 2
    outlier_cut = max(median_effort * 3, median_effort + 5) if len(items) >= 3 else float("inf")

    for item in items:
        flags = []
        if item["confidence"] <= LOW_CONFIDENCE:
            flags.append("low_confidence")
        if item["effort"] >= outlier_cut:
            flags.append("effort_outlier")
        if item["reach"] == 0:
            flags.append("zero_reach")
        item["flags"] = flags

    ranked = sorted(items, key=lambda i: (-i["score"], -i["reach"], i["effort"], i["name"]))
    for rank, item in enumerate(ranked, 1):
        item["rank"] = rank

    stats = {
        "median_effort": round(median_effort, 2),
        "effort_outlier_threshold": None if outlier_cut == float("inf") else round(outlier_cut, 2),
        "low_confidence_count": sum(1 for i in items if "low_confidence" in i["flags"]),
        "flagged_count": sum(1 for i in items if i["flags"]),
    }
    return ranked, stats


def render_markdown(items: list[dict], cycle: str, stats: dict) -> str:
    header = f"# RICE ranking — {cycle}" if cycle else "# RICE ranking"
    out = [header, "", "Formula: `(Reach x Impact x Confidence) / Effort`", ""]
    out.append("| # | Item | Reach | Impact | Conf. | Effort | Score | Flags |")
    out.append("|---|------|-------|--------|-------|--------|-------|-------|")
    for i in items:
        impact_label = f"{i['impact']:g} ({VALID_IMPACT[i['impact']]})"
        flags = ", ".join(i["flags"]) if i["flags"] else "—"
        notes = f" — {i['notes']}" if i["notes"] else ""
        out.append(
            f"| {i['rank']} | {i['name']}{notes} | {i['reach']:,.0f} | {impact_label} "
            f"| {i['confidence']*100:.0f}% | {i['effort']:g} | {i['score']:.2f} | {flags} |"
        )
    out.append("")
    out.append(f"Items: {len(items)} · median effort: {stats['median_effort']:g} person-weeks")
    if stats["effort_outlier_threshold"] is not None:
        out.append(f"Effort outlier threshold: > {stats['effort_outlier_threshold']:g} person-weeks")
    if stats["low_confidence_count"]:
        out.append(
            f"⚠ {stats['low_confidence_count']} item(s) at or below "
            f"{LOW_CONFIDENCE*100:.0f}% confidence — treat these as research tasks, "
            "not build commitments."
        )
    out.append("")
    out.append(
        "RICE ranks; it does not decide. Record any override (strategy, dependency, "
        "reversibility) with its reason."
    )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rice_scorer.py",
        description="Rank backlog items by RICE score.",
        epilog=(
            "impact: 3=+ massive, 2=high, 1=medium, 0.5=low, 0.25=minimal. "
            "confidence: 0-1 or 0-100. effort: person-weeks > 0."
        ),
    )
    parser.add_argument("input", help="JSON file with items, or '-' for stdin")
    parser.add_argument(
        "--output", "-o", choices=("markdown", "json"), default="markdown",
        help="output format (default: markdown)",
    )
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            raw = sys.stdin.read()
        else:
            with open(args.input, encoding="utf-8") as fh:
                raw = fh.read()
        items, cycle = load_items(raw)
    except FileNotFoundError:
        print(f"error: no such file: {args.input}", file=sys.stderr)
        return 1
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    ranked, stats = analyse(items)
    if args.output == "json":
        print(json.dumps(
            {"cycle": cycle, "stats": stats, "items": ranked},
            indent=2,
        ))
    else:
        print(render_markdown(ranked, cycle, stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
