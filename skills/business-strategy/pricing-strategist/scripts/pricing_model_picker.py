#!/usr/bin/env python3
"""Score five SaaS pricing models against a product brief.

Stdlib only. Emits a ranked fit score (0-100) per model plus rationale and
trade-offs. Never emits a price -- use wtp_analyzer.py for the range.

Usage:
    python3 pricing_model_picker.py --input brief.json --output markdown
    python3 pricing_model_picker.py --input brief.json --output json
"""
from __future__ import annotations

import argparse
import json
import sys

MODELS = ["seat", "usage", "value", "freemium", "hybrid"]

BASE_SCORES = {
    "seat": 50,
    "usage": 50,
    "value": 50,
    "freemium": 50,
    "hybrid": 50,
}

PROFILE_WEIGHTS = {
    "saas": {"seat": 6, "usage": 2, "value": 3, "freemium": 4, "hybrid": 4},
    "api": {"seat": -4, "usage": 10, "value": 4, "freemium": 6, "hybrid": 5},
    "marketplace": {"seat": -2, "usage": 6, "value": 6, "freemium": 5, "hybrid": 6},
}

TRADEOFFS = {
    "seat": (
        "Predictable revenue, easy to forecast and to explain; aligns with headcount growth.",
        "Punishes adoption -- customers ration seats and share logins, which suppresses usage "
        "and hides value; breaks down when one seat can serve a whole team via automation.",
    ),
    "usage": (
        "Revenue scales with delivered value and the entry price can be near zero.",
        "Revenue becomes volatile and customers become cost-anxious, throttling usage exactly "
        "when they would otherwise form a habit; requires metering you must actually build.",
    ),
    "value": (
        "Captures the surplus you create and survives procurement scrutiny with a measured metric.",
        "Requires a value metric you can meter and the buyer accepts; hard to explain at "
        "purchase time and hard to re-baseline when the customer's economics shift.",
    ),
    "freemium": (
        "Removes top-of-funnel friction and gives a self-serve path into the product.",
        "Free users consume real cost-to-serve; conversion is typically 2-5%, and a weak gate "
        "turns the free tier into the product for most of the market.",
    ),
    "hybrid": (
        "A platform fee plus a usage dimension hedges forecasting risk while keeping upside.",
        "Two dimensions to explain raises sales friction and billing complexity; the platform "
        "fee must be low enough not to deter trial, high enough to cover cost-to-serve.",
    ),
}

REQUIREMENTS = {
    "seat": ["multi-user product", "clear per-user value", "team-based buying"],
    "usage": ["meterable consumption", "variable cost-to-serve", "spiky or elastic demand"],
    "value": ["measurable value metric", "buyer accepts the metric", "outcome attribution"],
    "freemium": ["self-serve onboarding", "low marginal cost per free user", "viral or PLG loop"],
    "hybrid": ["meterable consumption", "predictable baseline usage", "sales-assisted motion"],
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _num(brief: dict, key: str, default: float = 0.0) -> float:
    value = brief.get(key, default)
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_models(brief: dict, profile: str = "saas") -> list:
    """Return a ranked list of {model, score, rationale[], trade_off_for, trade_off_against}."""
    profile = profile if profile in PROFILE_WEIGHTS else "saas"
    weights = PROFILE_WEIGHTS[profile]

    buyer = str(brief.get("buyer", "mid-market")).lower()
    pattern = str(brief.get("consumption_pattern", "")).lower()
    adoption = str(brief.get("adoption", "")).lower()
    value_measurable = bool(brief.get("value_measurable", False))
    value_metric = str(brief.get("value_metric", "")).strip()
    deal_size = _num(brief, "avg_deal_size")
    customers = _num(brief, "customer_count")
    competitors = [str(c).lower() for c in brief.get("competitor_models", []) or []]
    self_serve = bool(brief.get("self_serve", False))
    marginal_cost = _num(brief, "marginal_cost_per_user")

    results = []
    for model in MODELS:
        score = float(BASE_SCORES[model]) + weights.get(model, 0)
        rationale = []

        # Declared consumption pattern is the strongest single signal.
        if pattern:
            if pattern == model:
                score += 18
                rationale.append(f"Brief declares consumption pattern '{pattern}', matching this model directly.")
            elif pattern == "hybrid" and model in ("seat", "usage"):
                score += 4
                rationale.append("Declared hybrid consumption; this model can serve as one of the two dimensions.")
            elif model == "hybrid" and pattern in ("seat", "usage", "value"):
                score += 6
                rationale.append(f"Hybrid can wrap the declared '{pattern}' pattern with a second dimension.")
            else:
                score -= 6
                rationale.append(f"Declared consumption pattern '{pattern}' does not match this model.")

        # Value-based pricing is only credible with a meterable metric.
        if model == "value":
            if value_measurable and value_metric:
                score += 16
                rationale.append(f"Value is measurable via '{value_metric}'.")
            elif value_measurable:
                score += 6
                rationale.append("Value is claimed measurable but no value metric is named; define one before committing.")
            else:
                score -= 18
                rationale.append("No measurable value metric; value-based pricing would be aspirational.")

        # Usage needs variable cost-to-serve and elastic demand.
        if model == "usage":
            if marginal_cost > 0:
                score += 5
                rationale.append("Positive marginal cost-to-serve makes metering economically necessary.")
            else:
                score -= 3
                rationale.append("Near-zero marginal cost weakens the case for metering.")

        # Freemium needs a self-serve path and cheap free users.
        if model == "freemium":
            if self_serve or "bottom-up" in adoption or "plg" in adoption:
                score += 12
                rationale.append("Self-serve or product-led adoption supports a free tier.")
            else:
                score -= 12
                rationale.append("Sales-led adoption means free users rarely convert without a rep.")
            if marginal_cost > 0 and deal_size >= 10000:
                score -= 8
                rationale.append("High deal size with real cost-to-serve makes a free tier expensive.")

        # Seat pricing scales with organisation size.
        if model == "seat":
            if buyer in ("enterprise", "mid-market"):
                score += 6
                rationale.append(f"'{buyer}' buyers are accustomed to per-seat procurement.")
            elif buyer == "smb":
                score -= 4
                rationale.append("SMB buyers resist seat expansion and share logins.")

        # Hybrid suits mid-market and above with a sales-assisted motion.
        if model == "hybrid":
            if buyer in ("mid-market", "enterprise"):
                score += 7
                rationale.append(f"'{buyer}' buyers tolerate a two-part price structure.")
            if deal_size >= 25000:
                score += 4
                rationale.append("Deal size supports a platform fee plus usage component.")

        # Competitor parity is a signal of buyer expectations, not of correctness.
        matching = sum(1 for c in competitors if c == model)
        if matching:
            score += 3
            rationale.append("At least one competitor uses this model; buyers will benchmark against it.")

        # Scale signal: freemium needs volume to pay for itself.
        if model == "freemium" and customers < 50:
            score -= 6
            rationale.append("Customer count under 50 gives a free tier too little base to convert from.")

        if not rationale:
            rationale.append("Neutral fit -- no brief field discriminated for or against this model.")

        results.append(
            {
                "model": model,
                "score": round(_clamp(score), 1),
                "rationale": rationale,
                "supports": REQUIREMENTS[model],
                "trade_off_for": TRADEOFFS[model][0],
                "trade_off_against": TRADEOFFS[model][1],
            }
        )

    results.sort(key=lambda r: (-r["score"], MODELS.index(r["model"])))
    return results


def confidence(brief: dict) -> str:
    keys = [
        "buyer",
        "consumption_pattern",
        "value_measurable",
        "avg_deal_size",
        "customer_count",
        "adoption",
    ]
    present = sum(1 for k in keys if brief.get(k) not in (None, "", []))
    if present >= 6:
        return "high"
    if present >= 4:
        return "medium"
    return "low"


def render_markdown(brief: dict, ranked: list, profile: str) -> str:
    top = ranked[0]
    second = ranked[1]
    lines = []
    lines.append("# Pricing Model Fit — {}".format(brief.get("product", "Untitled product")))
    lines.append("")
    lines.append("Profile: `{}` · Confidence: **{}**".format(profile, confidence(brief)))
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(
        "**{}** ({} / 100). Runner-up: **{}** ({} / 100). "
        "Treat the runner-up as the migration target if the primary model stalls.".format(
            top["model"], top["score"], second["model"], second["score"]
        )
    )
    lines.append("")
    lines.append("This skill recommends a model and a range, not a price.")
    lines.append("")
    lines.append("## Ranking")
    lines.append("")
    lines.append("| # | Model | Score | Fit |")
    lines.append("|---|-------|-------|-----|")
    for i, row in enumerate(ranked, 1):
        fit = "strong" if row["score"] >= 70 else "defensible" if row["score"] >= 55 else "weak"
        lines.append("| {} | {} | {} | {} |".format(i, row["model"], row["score"], fit))
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for row in ranked:
        lines.append("### {} — {}".format(row["model"], row["score"]))
        lines.append("")
        lines.append("**Why:**")
        for reason in row["rationale"]:
            lines.append("- " + reason)
        lines.append("")
        lines.append("**Requires:** " + ", ".join(row["supports"]))
        lines.append("")
        lines.append("**For:** " + row["trade_off_for"])
        lines.append("")
        lines.append("**Against:** " + row["trade_off_against"])
        lines.append("")
    lines.append("## Next Step")
    lines.append("")
    lines.append(
        "Run `wtp_analyzer.py` on survey data to bound the price range before "
        "designing packaging. Do not design tiers first."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Score five SaaS pricing models against a product brief.")
    parser.add_argument("--input", required=True, help="Path to brief.json")
    parser.add_argument("--profile", default="saas", choices=sorted(PROFILE_WEIGHTS), help="Business profile")
    parser.add_argument("--output", default="markdown", choices=["markdown", "json"], help="Output format")
    args = parser.parse_args(argv)

    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            brief = json.load(handle)
    except OSError as exc:
        print("error: cannot read {}: {}".format(args.input, exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: {} is not valid JSON: {}".format(args.input, exc), file=sys.stderr)
        return 2

    if not isinstance(brief, dict):
        print("error: brief.json must be a JSON object", file=sys.stderr)
        return 2

    ranked = score_models(brief, args.profile)

    if args.output == "json":
        payload = {
            "product": brief.get("product", "Untitled product"),
            "profile": args.profile,
            "confidence": confidence(brief),
            "recommended": ranked[0]["model"],
            "runner_up": ranked[1]["model"],
            "ranking": ranked,
            "note": "Model recommendation only. Price range comes from wtp_analyzer.py.",
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_markdown(brief, ranked, args.profile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
