#!/usr/bin/env python3
"""Design Good / Better / Best packaging from a feature-value inventory.

Stdlib only. Assigns features to cumulative tiers, then flags packaging
anti-patterns (feature dump, empty tier, decoy tier, no upgrade trigger,
orphan feature). Emits price *indexes*, never absolute prices.

Usage:
    python3 packaging_designer.py --input features.json --output markdown
    python3 packaging_designer.py --input features.json --output json

features.json:
    {
      "product": "AI support triage",
      "segments": ["smb", "mid", "enterprise"],
      "features": [
        {"name": "Core dashboard", "cost": 1,
         "value": {"smb": 8, "mid": 6, "enterprise": 4}, "table_stakes": true}
      ]
    }

Values are relative units (1-10 is fine). Cost is cost-to-serve / build effort
in the same relative units. The ratio value/cost is what drives tier placement.
"""
from __future__ import annotations

import argparse
import json
import sys

TIERS = ["good", "better", "best"]
TIER_LABEL = {"good": "Good", "better": "Better", "best": "Best"}

# Which tier a feature belongs in when its strongest segment is S/M/E.
SEGMENT_TIER = {
    "smb": "good",
    "small": "good",
    "startup": "good",
    "mid": "better",
    "mid-market": "better",
    "midmarket": "better",
    "growth": "better",
    "enterprise": "best",
    "ent": "best",
    "large": "best",
}

# Value elasticity applied to the ladder: price rises slightly slower than value,
# so higher tiers read as better deals per unit of value.
LADDER_ELASTICITY = 0.85


def _num(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalise(features: list, segments: list) -> list:
    """Coerce raw feature dicts into a consistent internal shape."""
    clean = []
    for index, raw in enumerate(features):
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "feature_{}".format(index)).strip()
        cost = _num(raw.get("cost"), 1.0)
        if cost <= 0:
            cost = 1.0
        raw_value = raw.get("value") or {}
        if isinstance(raw_value, (int, float)):
            raw_value = {seg: float(raw_value) for seg in segments}
        if not isinstance(raw_value, dict):
            raw_value = {}
        value = {}
        for seg in segments:
            value[seg] = _num(raw_value.get(seg), 0.0)
        if not value:
            value = {"default": _num(raw_value.get("default"), 1.0)}
        clean.append(
            {
                "name": name,
                "cost": cost,
                "value": value,
                "table_stakes": bool(raw.get("table_stakes", False)),
                "max_value": max(value.values()) if value else 0.0,
                "sum_value": sum(value.values()),
            }
        )
    return clean


def dominant_segment(feature: dict) -> str:
    value = feature["value"]
    return max(value.items(), key=lambda kv: kv[1])[0]


def assign_tiers(features: list, segments: list) -> tuple:
    """Return (assignment {name: tier}, method, notes)."""
    notes = []
    if not features:
        return {}, "none", ["No features supplied."]

    ordered_segments = [s.lower() for s in segments] if segments else ["smb", "mid", "enterprise"]

    # Pass 1: table stakes always land in the entry tier, then segment affinity.
    primary = {}
    for feature in features:
        if feature["table_stakes"]:
            primary[feature["name"]] = "good"
            continue
        seg = dominant_segment(feature).lower()
        primary[feature["name"]] = SEGMENT_TIER.get(seg, "better")

    counts = {tier: sum(1 for t in primary.values() if t == tier) for tier in TIERS}
    method = "segment-affinity"

    # Pass 2: if any tier is empty, fall back to value-per-cost quantiles.
    if any(counts[tier] == 0 for tier in TIERS) and len(features) >= 3:
        notes.append(
            "Segment affinity produced an empty tier; rebalanced by value-per-cost quantiles."
        )
        ranked = sorted(
            features,
            key=lambda f: (-(f["sum_value"] / f["cost"]), -f["max_value"], f["name"]),
        )
        total = sum(f["sum_value"] for f in ranked) or 1.0
        primary = {}
        cumulative = 0.0
        for feature in ranked:
            cumulative += feature["sum_value"]
            share = cumulative / total
            if share <= 0.50:
                tier = "good"
            elif share <= 0.80:
                tier = "better"
            else:
                tier = "best"
            if feature["table_stakes"]:
                tier = "good"
            primary[feature["name"]] = tier
        method = "value-quantile"

    # Pass 3: make tiers cumulative — a feature in Best is also in Better.
    by_name = {f["name"]: f for f in features}
    floor = {name: TIERS.index(tier) for name, tier in primary.items()}
    members = {tier: [] for tier in TIERS}
    for tier_index, tier in enumerate(TIERS):
        for name, lowest in floor.items():
            if lowest <= tier_index:
                members[tier].append(by_name[name])

    for tier in TIERS:
        members[tier].sort(key=lambda f: (-f["sum_value"], f["name"]))
    return members, method, notes


def tier_value(members: dict) -> dict:
    return {tier: round(sum(f["sum_value"] for f in members[tier]), 2) for tier in TIERS}


def added_features(members: dict) -> dict:
    """Features that are new at each tier, relative to the tier below."""
    added = {}
    previous = set()
    for tier in TIERS:
        current = {f["name"] for f in members[tier]}
        added[tier] = [f for f in members[tier] if f["name"] not in previous]
        previous = current
    return added


def added_value(members: dict, added: dict) -> dict:
    """Incremental value contributed by each tier's new features."""
    return {tier: round(sum(f["sum_value"] for f in added[tier]), 2) for tier in TIERS}


def ladder_index(values: dict) -> dict:
    """Relative price index per tier, anchored at Good = 1.00."""
    base = values["good"] or 1.0
    index = {}
    for tier in TIERS:
        ratio = values[tier] / base if base else 1.0
        index[tier] = round(max(1.0, ratio) ** LADDER_ELASTICITY, 3)
    return index


def detect_anti_patterns(members: dict, values: dict, added: dict, features: list) -> list:
    flagged = []
    names = {tier: {f["name"] for f in members[tier]} for tier in TIERS}
    # Tiers are cumulative, so the increment -- not the total -- is what a buyer compares.
    increments = added_value(members, added)
    total_value = values["best"] or 1.0

    # Empty tier (no features at all, or nothing new relative to the tier below)
    for tier in TIERS:
        if not added[tier]:
            flagged.append(
                {
                    "type": "empty_tier",
                    "severity": "high",
                    "message": "The {} tier adds no features over the tier below; it cannot be priced or "
                               "sold as a distinct package.".format(TIER_LABEL[tier]),
                }
            )

    # Feature dump: Best's *incremental* value dominates the package
    best_share = increments["best"] / total_value * 100.0
    if best_share > 60:
        flagged.append(
            {
                "type": "feature_dump",
                "severity": "high",
                "message": "Best's new features carry {:.0f}% of total feature value. Buyers read this as "
                           "'Good is crippled'. Move value down until Best is under ~60%.".format(best_share),
            }
        )

    # Decoy tier: middle tier adds too little over the entry tier
    if values["good"] and increments["better"] / values["good"] < 0.15 and names["better"] != names["good"]:
        flagged.append(
            {
                "type": "decoy_tier",
                "severity": "medium",
                "message": "Better adds under 15% value over Good. It will be treated as a decoy "
                           "or ignored; either widen it or collapse to two tiers.",
            }
        )

    # No upgrade trigger: adjacent tiers identical in feature set
    if names["better"] == names["good"]:
        flagged.append(
            {
                "type": "no_upgrade_trigger",
                "severity": "high",
                "message": "Good and Better ship the same features. Differentiate with a limit "
                           "(seats, volume, retention) or merge the tiers.",
            }
        )
    if names["best"] == names["better"]:
        flagged.append(
            {
                "type": "no_upgrade_trigger",
                "severity": "high",
                "message": "Best and Better ship the same features. There is no rational upgrade path.",
            }
        )

    # Top-heavy: Best is a longer list than Good
    if members["good"] and len(added["best"]) > len(members["good"]) * 1.5:
        flagged.append(
            {
                "type": "top_heavy",
                "severity": "medium",
                "message": "Best lists {:.1f}x the features of Good. Long enterprise lists usually hide "
                           "features nobody pays for.".format(len(added["best"]) / len(members["good"])),
            }
        )

    # Segment skew: nearly all value sits with the top segment, so the entry tier
    # cannot be credible however the features are grouped.
    by_dominance = {}
    for feature in features:
        seg = dominant_segment(feature)
        by_dominance[seg] = by_dominance.get(seg, 0) + 1
    if by_dominance and features:
        top_seg, top_count = max(by_dominance.items(), key=lambda kv: kv[1])
        top_share = top_count / len(features) * 100.0
        entry_tier = SEGMENT_TIER.get(top_seg.lower())
        if top_share > 60 and entry_tier == "best":
            flagged.append(
                {
                    "type": "segment_skew",
                    "severity": "high",
                    "message": "{:.0f}% of features are dominated by '{}' buyers. The entry tier will look "
                               "crippled no matter how you group them -- move at least a third of that value "
                               "to the lower segments, or sell the enterprise block as an add-on.".format(
                                   top_share, top_seg),
                }
            )

    # Orphan feature: no segment values it above cost
    for feature in features:
        if feature["max_value"] <= feature["cost"]:
            flagged.append(
                {
                    "type": "orphan_feature",
                    "severity": "low",
                    "message": "'{}' never exceeds its cost-to-serve (max value {:.1f} vs cost {:.1f}). "
                               "It is not a pricing lever — consider dropping it.".format(
                                   feature["name"], feature["max_value"], feature["cost"]),
                }
            )

    # Ladder gap: entry to mid step far larger than mid to top
    index = ladder_index(values)
    step_one = index["better"] - index["good"]
    step_two = index["best"] - index["better"]
    if step_one > 0 and step_two > 0 and step_one / step_two > 2.5:
        flagged.append(
            {
                "type": "ladder_gap",
                "severity": "medium",
                "message": "The Good → Better step is {:.1f}x the Better → Best step. The middle tier "
                           "will absorb demand and cap expansion revenue.".format(step_one / step_two),
            }
        )

    return flagged


def upsell_triggers(members: dict) -> dict:
    """Name the gate that should separate each tier from the next."""
    triggers = {}
    if not members["good"]:
        return triggers
    good_names = {f["name"] for f in members["good"]}
    for tier in ("better", "best"):
        new = [f["name"] for f in members[tier] if f["name"] not in good_names]
        if new:
            triggers[tier] = "unlocks: " + ", ".join(new[:3])
        else:
            triggers[tier] = "no new feature — gate on a limit instead (seats, volume, retention, SLA)"
    return triggers


def render_markdown(result: dict) -> str:
    lines = []
    values = result["tier_value"]
    index = result["ladder_index"]
    members = result["members"]
    added = result["added"]
    increments = result["added_value"]

    lines.append("# Tier Packaging — {}".format(result["product"]))
    lines.append("")
    lines.append("Method: `{}` · Segments: {}".format(result["method"], ", ".join(result["segments"]) or "n/a"))
    lines.append("")
    lines.append("## Tiers")
    lines.append("")
    lines.append("| Tier | New features | Total features | Value added | Cumulative value | Price index |")
    lines.append("|------|--------------|----------------|-------------|------------------|-------------|")
    for tier in TIERS:
        lines.append("| {} | {} | {} | {:.0f} | {:.0f} | {:.2f} |".format(
            TIER_LABEL[tier], len(added[tier]), len(members[tier]),
            increments[tier], values[tier], index[tier]))
    lines.append("")
    lines.append("Price indexes are relative, anchored at Good = 1.00. Multiply by your Good-tier "
                 "price once the PSM range is set.")
    lines.append("")

    lines.append("## Assignment")
    lines.append("")
    for tier in TIERS:
        inherited = len(members[tier]) - len(added[tier])
        lines.append("### {} — {} new features, {:.0f} value added".format(
            TIER_LABEL[tier], len(added[tier]), increments[tier]))
        if inherited:
            lines.append("")
            lines.append("_Includes {} feature(s) carried down from the tier below._".format(inherited))
        if not added[tier]:
            lines.append("")
            lines.append("_No new features — gate this tier on a limit, not on features._")
        for feature in added[tier]:
            seg = dominant_segment(feature)
            lines.append("- **{}** — strongest for `{}`, value {:.1f}, cost {:.1f}, ratio {:.2f}".format(
                feature["name"], seg, feature["sum_value"], feature["cost"],
                feature["sum_value"] / feature["cost"]))
        if tier in result["upsell_triggers"]:
            lines.append("")
            lines.append("_Upgrade trigger:_ " + result["upsell_triggers"][tier])
        lines.append("")

    lines.append("## Anti-Patterns")
    lines.append("")
    if result["anti_patterns"]:
        for flag in result["anti_patterns"]:
            lines.append("- **[{} · {}]** {}".format(flag["severity"], flag["type"], flag["message"]))
    else:
        lines.append("None detected.")
    lines.append("")

    if result["notes"]:
        lines.append("## Adjustments Applied")
        lines.append("")
        for note in result["notes"]:
            lines.append("- " + note)
        lines.append("")

    lines.append("## Next Step")
    lines.append("")
    lines.append("Set the Good-tier price from the PSM Range of Acceptable Prices (`wtp_analyzer.py`), "
                 "then apply the price index to derive Better and Best. Do not reverse the order.")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Design Good/Better/Best pricing tiers.")
    parser.add_argument("--input", required=True, help="Path to features.json")
    parser.add_argument("--profile", default="saas", help="Business profile (informational)")
    parser.add_argument("--output", default="markdown", choices=["markdown", "json"], help="Output format")
    args = parser.parse_args(argv)

    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        print("error: cannot read {}: {}".format(args.input, exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: {} is not valid JSON: {}".format(args.input, exc), file=sys.stderr)
        return 2

    if isinstance(payload, list):
        payload = {"features": payload}
    if not isinstance(payload, dict):
        print("error: features.json must be an object or an array of features", file=sys.stderr)
        return 2

    segments = payload.get("segments") or []
    if not isinstance(segments, list):
        segments = []
    if not segments:
        keys = set()
        for raw in payload.get("features", []) or []:
            if isinstance(raw, dict) and isinstance(raw.get("value"), dict):
                keys.update(raw["value"].keys())
        segments = sorted(keys) or ["smb", "mid", "enterprise"]

    features = normalise(payload.get("features", []) or [], segments)
    if not features:
        print("error: no usable features in input", file=sys.stderr)
        return 2

    members, method, notes = assign_tiers(features, segments)
    added = added_features(members)
    values = tier_value(members)

    result = {
        "product": payload.get("product", "Untitled product"),
        "profile": args.profile,
        "segments": segments,
        "method": method,
        "notes": notes,
        "tier_value": values,
        "added_value": added_value(members, added),
        "ladder_index": ladder_index(values),
        "members": members,
        "added": added,
        "upsell_triggers": upsell_triggers(members),
        "anti_patterns": detect_anti_patterns(members, values, added, features),
        "note": "Relative indexes only. Absolute prices come from the PSM range.",
    }

    if args.output == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
