#!/usr/bin/env python3
"""Classify a task description into a cost tier: ROUTINE / MODERATE / COMPLEX.

A small, stdlib-only classifier used by the model-routing cost optimizer. It
reads a task description plus optional complexity keywords and returns the
recommended tier mapping (ROUTINE -> Tier 1, MODERATE -> Tier 2, COMPLEX ->
Tier 3). It is a heuristic aid, not a substitute for the vision/escalation
overrides in SKILL.md.

Usage:
    python3 scripts/classify_task.py "<task description>" [keyword...]

Examples:
    python3 scripts/classify_task.py "read the config file and log it"
    python3 scripts/classify_task.py "debug this crash and fix the cause" debug
"""

from __future__ import annotations

import re
import sys

ROUTINE = "ROUTINE"
MODERATE = "MODERATE"
COMPLEX = "COMPLEX"

ROUTINE_SIGNALS = {
    "read", "fetch", "check", "list", "format", "status", "heartbeat",
    "cron", "lookup", "transform", "filter", "sort", "convert",
}
MODERATE_SIGNALS = {
    "write", "generate", "summar", "summarize", "draft", "analyze",
    "refactor", "implement", "extract",
}
COMPLEX_SIGNALS = {
    "debug", "architect", "design", "security", "adversarial", "ambiguous",
    "novel", "debugging", "reason", "why", "migrate", "review",
}


def classify(text: str, extra_keywords: list[str] | None = None) -> str:
    """Classify a task description into a complexity bucket."""
    lower = text.lower()
    tokens = set(re.findall(r"[a-z0-9_]+", lower))
    if extra_keywords:
        tokens.update(k.lower() for k in extra_keywords)

    if tokens & COMPLEX_SIGNALS:
        return COMPLEX
    if tokens & ROUTINE_SIGNALS and not tokens & MODERATE_SIGNALS:
        return ROUTINE
    if tokens & MODERATE_SIGNALS:
        return MODERATE
    # fallback: no strong signals -> call it routine, keep it cheap
    return ROUTINE


def tier_of(bucket: str) -> str:
    """Map a complexity bucket to a tier label."""
    return {
        ROUTINE: "Tier 1 (cheap)",
        MODERATE: "Tier 2 (mid)",
        COMPLEX: "Tier 3 (premium)",
    }[bucket]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: classify_task.py <task> [keyword...]")
    task = sys.argv[1]
    extra = sys.argv[2:]
    bucket = classify(task, extra)
    print(f"task:     {task}")
    print(f"bucket:   {bucket}")
    print(f"recommend {tier_of(bucket)}")


if __name__ == "__main__":
    main()