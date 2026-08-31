#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""App Discovery scoring engine. Weighted scoring with kill-floor elimination."""
import json, sys

SCORING = {
    "market_signal":      {"weight": 0.20, "kill_floor": 4.0, "label": "Market Signal"},
    "competition_gap":    {"weight": 0.20, "kill_floor": 4.0, "label": "Competition Gap"},
    "seo_aso":            {"weight": 0.20, "kill_floor": 4.0, "label": "SEO/ASO Opportunity"},
    "monetization":       {"weight": 0.20, "kill_floor": 4.0, "label": "Monetization Feasibility"},
    "urgency":            {"weight": 0.10, "kill_floor": 4.0, "label": "Urgency/Timing"},
    "mobile_first":       {"weight": 0.10, "kill_floor": 6.0, "label": "Mobile-First Fit"},
}

def score_candidate(name: str, scores: dict[str, float]) -> dict:
    """Score one candidate. Returns score dict with pass/fail."""
    total = 0.0
    details = {}
    eliminations = []

    for key, config in SCORING.items():
        raw = scores.get(key, 0)
        weighted = raw * config["weight"]
        total += weighted
        passed = raw >= config["kill_floor"]
        details[key] = {
            "raw": raw,
            "weighted": round(weighted, 2),
            "kill_floor": config["kill_floor"],
            "passed": passed,
            "label": config["label"],
        }
        if not passed:
            eliminations.append(f"{config['label']}: {raw}/10 (floor {config['kill_floor']})")

    return {
        "name": name,
        "total": round(total, 2),
        "max_possible": 10.0,
        "passed": len(eliminations) == 0,
        "eliminations": eliminations,
        "details": details,
    }

def score_all(candidates: list[dict]) -> list[dict]:
    """Score all candidates, sort by total descending."""
    results = [score_candidate(c["name"], c["scores"]) for c in candidates]
    results.sort(key=lambda r: r["total"], reverse=True)
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    results = score_all(data["candidates"])
    print(json.dumps({"results": results, "scoring_config": {k: {"weight": v["weight"], "kill_floor": v["kill_floor"]} for k, v in SCORING.items()}}, indent=2))