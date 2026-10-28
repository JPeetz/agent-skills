#!/usr/bin/env python3
"""
scan_sessions.py — first-pass scanner for skill-miner.

Scans local agent session history (or exported transcripts) and emits a
sanitized cluster report: repeated user asks grouped by intent/trigger
phrasing, with occurrence counts, so repeated skill-worthy workflows can be
shortlisted. This is a FIRST-PASS tool — always review its output manually
before creating skills (see SKILL.md and references/discovery-rubric.md).

Usage:
    python3 scripts/scan_sessions.py --days 30 --limit 300 --min-count 3
    python3 scripts/scan_sessions.py --export ~/Downloads/cursor-chat-export.json --export ./opencode-transcripts/
    python3 scripts/scan_sessions.py --patterns ./my-patterns.json

Stdlib only. On JSONL session transcripts it reads the "role"/"user"-side
messages; on exported .json/.md/.txt it treats lines as candidate asks.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_PATTERNS = {
    "date/time formatting": r"\bdate|time\s*format|format (the )?date",
    "shell automation": r"\bshell|bash|zsh|script|automate",
    "data extraction": r"\bextract|scrape|parse|csv|json",
    "debugging": r"\bdebug|fix (a |the )?bug|error|traceback|not working",
    "testing": r"\btest|pytest|jest|unit test|e2e",
    "documentation": r"\bdocs|documentation|readme|docstring|comment",
    "deployment": r"\bdeploy|release|ci/cd|pipeline",
    "review": r"\breview|code review|pr review|critique",
    "refactoring": r"\brefactor|clean up|simplify|modularize",
    "security": r"\bsecurity|vulnerab|audit|hardening|secret",
}

# Sensitive tokens to redact from examples before printing.
REDACT_PATTERNS = [
    (re.compile(r"(/Users/|/home/)[^\s\"']+"), "<user-path>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<email>"),
    (re.compile(r"\b(sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{16,}|AKIA[A-Z0-9]{16})\b"), "<token>"),
    (re.compile(r"(api[_-]?key|password|secret|token)\s*[:=]\s*\S+", re.I), r"\1=<redacted>"),
]


def redact(text: str) -> str:
    for rx, repl in REDACT_PATTERNS:
        text = rx.sub(repl, text)
    return text


def iter_ask_lines(paths, export_paths, days, limit):
    """Yield candidate user-ask lines from session files/exported files."""
    cutoff = datetime.now() - timedelta(days=days) if days else None
    yielded = 0
    seen_files = set()

    def emit(line):
        nonlocal yielded
        if yielded >= limit:
            return
        line = line.strip()
        if line and not line.startswith(("#", "//", "```")):
            yielded += 1
            yield line

    def scan_file(path):
        nonlocal yielded
        if yielded >= limit:
            return
        if cutoff is not None:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        if path.suffix.lower() == ".jsonl":
            for ln in text.splitlines():
                try:
                    obj = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                msg = obj.get("message") or {}
                if isinstance(msg, dict):
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role in ("user", "human") and isinstance(content, str):
                        for line in content.splitlines():
                            yield from emit(line)
                else:
                    for line in str(obj).splitlines():
                        yield from emit(line)
        elif path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                return
            stack = [data]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    if node.get("role") in ("user", "human") and isinstance(node.get("content"), str):
                        for line in node["content"].splitlines():
                            yield from emit(line)
                    for v in node.values():
                        stack.append(v)
                elif isinstance(node, list):
                    stack.extend(node)
        else:  # .md / .txt exports
            for line in text.splitlines():
                yield from emit(line)

    for raw in list(paths) + list(export_paths):
        p = Path(raw).expanduser()
        if p.is_dir():
            for fp in sorted(p.rglob("*")):
                if fp.is_file() and fp.suffix.lower() in (".jsonl", ".json", ".md", ".txt"):
                    key = os.path.abspath(fp)
                    if key not in seen_files:
                        seen_files.add(key)
                        yield from scan_file(fp)
        elif p.is_file():
            key = os.path.abspath(p)
            if key not in seen_files:
                seen_files.add(key)
                yield from scan_file(p)


def build_matchers(patterns_path):
    if patterns_path and Path(patterns_path).expanduser().exists():
        with open(Path(patterns_path).expanduser()) as f:
            patterns = json.load(f)
        if isinstance(patterns, dict):
            return [(name, re.compile(rx, re.I)) for name, rx in patterns.items()]
    return [(name, re.compile(rx, re.I)) for name, rx in DEFAULT_PATTERNS.items()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "Session scanner").splitlines()[0])
    ap.add_argument("--days", type=int, default=30, help="Only scan files modified within the last N days (default 30; 0 = all)")
    ap.add_argument("--limit", type=int, default=300, help="Max candidate lines to scan (default 300)")
    ap.add_argument("--min-count", type=int, default=3, help="Only report clusters with >= N occurrences (default 3)")
    ap.add_argument("--export", action="append", default=[], help="Exported transcript file or directory (repeatable)")
    ap.add_argument("--patterns", default=None, help="JSON file mapping workflow names to trigger regexes")
    args = ap.parse_args(argv)

    # Default evidence sources (only those that exist).
    paths = []
    for p in (
        Path.home() / ".codex/sessions",
        Path.home() / ".codex/archived_sessions",
        Path.home() / ".codex/memories/rollout_summaries",
        Path.home() / ".claude/projects",
        Path.home() / ".claude/sessions",
        Path.home() / ".gemini",
        Path.home() / ".agents/memories",
        Path.home() / ".codex/memories",
    ):
        if p.exists():
            paths.append(str(p))

    matchers = build_matchers(args.patterns)
    clusters = defaultdict(list)
    totals = Counter()
    scanned = 0
    for line in iter_ask_lines(paths, args.export, args.days, args.limit):
        scanned += 1
        for name, rx in matchers:
            if rx.search(line):
                clusters[name].append(line)
                totals[name] += 1

    print(f"# Scan report (first-pass — review manually before creating skills)")
    print(f"Scanned {scanned} candidate lines; reporting clusters with >= {args.min_count} occurrences\n")
    if not totals:
        print("No clusters found. Try more days, a smaller --min-count, or pass --export transcripts.")
        return 0
    for name, count in totals.most_common():
        if count < args.min_count:
            continue
        print(f"## {name} ({count}x)")
        for ex in clusters[name][:3]:
            print(f"  - {redact(ex)[:300]}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())