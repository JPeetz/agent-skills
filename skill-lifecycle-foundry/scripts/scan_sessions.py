#!/usr/bin/env python3
"""Scan a directory of session/archive files for repeated workflow intents.

A deterministic first-pass miner: walk the given root, read each text file
(.md, .txt, .json, .jsonl, .log, .yaml, .yml), and report how many distinct
files contain each workflow-signal keyword. Use it to shortlist candidate
workflows before drafting a SKILL.md.

Stdlib only. Invoke through the Hermes terminal tool:

    python3 scripts/scan_sessions.py <root_dir> [--min-files 3] [--top 10]

Example:

    python3 scripts/scan_sessions.py ~/.hermes --top 8
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re

DEFAULT_KEYWORDS = [
    "review",
    "migrate",
    "refactor",
    "summary",
    "report",
    "build",
    "deploy",
    "triage",
    "optimize",
    "backup",
]

TEXT_EXT = {".md", ".txt", ".json", ".jsonl", ".log", ".yaml", ".yml"}


def tokens(text: str) -> set[str]:
    """Return the set of lowercase alphanumeric tokens in a text blob."""
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def scan(root: pathlib.Path, min_files: int, top: int) -> None:
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    hits: dict[str, set] = collections.defaultdict(set)
    file_count = 0

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXT:
            continue
        file_count += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found = tokens(text) & set(DEFAULT_KEYWORDS)
        for kw in found:
            hits[kw].add(str(path))

    for kw in DEFAULT_KEYWORDS:
        hits.setdefault(kw, set())  # stable output even when a word is unseen

    print(f"scanned {file_count} files under {root}")
    print(f"{'keyword':<14}{'files':>7}  intent")
    ranked = sorted(hits.items(), key=lambda kv: len(kv[1]), reverse=True)
    for kw, files in ranked[:top]:
        marker = "  *candidate*" if len(files) >= min_files else ""
        print(f"{kw:<14}{len(files):>7}{marker}")


def main() -> None:
    parser = argparse.ArgumentParser(description="session intent scanner")
    parser.add_argument("path", type=pathlib.Path, help="directory to scan")
    parser.add_argument("--min-files", type=int, default=3,
                        help="distinct-file threshold to call a candidate")
    parser.add_argument("--top", type=int, default=10, help="rows to print")
    args = parser.parse_args()
    scan(args.path, args.min_files, args.top)


if __name__ == "__main__":
    main()