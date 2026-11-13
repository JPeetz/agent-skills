#!/usr/bin/env python3
"""Lint commit messages against Conventional Commit rules.

Checks structure only: type, scope, description, subject length, and breaking
change footers. It cannot judge whether a description is a good description.

Stdlib only. No third-party dependencies.

Examples:
    python3 commit_linter.py --range origin/main..HEAD
    python3 commit_linter.py --input - < commits.txt
    python3 commit_linter.py --input commits.txt --strict --format json
    echo "feat(api): add pagination" | python3 commit_linter.py --input -

Exit codes: 0 clean (or warnings only), 1 violations, 2 usage or input error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ALLOWED_TYPES = (
    "feat", "fix", "perf", "refactor", "docs", "test", "build", "ci",
    "chore", "security", "deprecated", "remove", "revert", "style",
)

HEADER_RE = re.compile(
    r"^(?P<type>[A-Za-z]+)"
    r"(?:\((?P<scope>[^()\r\n]+)\))?"
    r"(?P<bang>!)?"
    r":\s*(?P<description>.*)$"
)

SCOPE_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
BREAKING_RE = re.compile(r"^BREAKING[ -]CHANGE:", re.IGNORECASE | re.MULTILINE)
MERGE_RE = re.compile(r"^(merge|rebase)\b", re.IGNORECASE)
WIP_RE = re.compile(r"\b(wip|fixup!|squash!|tmp)\b", re.IGNORECASE)

DEFAULT_MAX_SUBJECT = 100
DEFAULT_MAX_BODY_LINE = 100


class InputError(Exception):
    """Raised when commits cannot be read."""


def lint_message(
    raw: str,
    index: int = 1,
    max_subject: int = DEFAULT_MAX_SUBJECT,
    max_body_line: int = DEFAULT_MAX_BODY_LINE,
    allow_merge: bool = True,
) -> dict:
    """Lint one commit message. Returns a result record with errors and warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    text = raw.replace("\r\n", "\n").strip()
    if not text:
        return {"index": index, "subject": "", "errors": ["empty commit message"],
                "warnings": [], "ok": False, "skipped": False}

    lines = text.split("\n")
    subject = lines[0].rstrip()
    body = "\n".join(lines[1:])

    if allow_merge and MERGE_RE.match(subject):
        return {"index": index, "subject": subject, "errors": [], "warnings": [],
                "ok": True, "skipped": True}

    match = HEADER_RE.match(subject)
    if not match:
        errors.append(
            "missing Conventional Commit header; expected '<type>(<scope>): <description>'"
        )
        return {"index": index, "subject": subject, "errors": errors,
                "warnings": warnings, "ok": False, "skipped": False}

    ctype = match.group("type").lower()
    scope = match.group("scope")
    description = match.group("description").strip()

    if ctype not in ALLOWED_TYPES:
        errors.append(
            f"unknown type '{match.group('type')}'; allowed: {', '.join(ALLOWED_TYPES)}"
        )
    if match.group("type") != ctype:
        warnings.append("type should be lowercase")

    if scope is not None:
        if scope != scope.strip():
            errors.append("scope must not contain leading or trailing whitespace")
        elif not SCOPE_RE.match(scope.strip()):
            warnings.append(
                f"scope '{scope}' should be lowercase alphanumeric (dots, dashes, slashes allowed)"
            )
        if not scope.strip():
            errors.append("empty scope '()'")

    if not description:
        errors.append("empty description after the colon")
    else:
        if description.endswith("."):
            warnings.append("description should not end with a period")
        if description[:1].isupper():
            warnings.append("description should start lowercase")
        if len(description) < 4:
            errors.append("description too short to be meaningful")

    if len(subject) > max_subject:
        errors.append(f"subject is {len(subject)} chars (max {max_subject})")

    if WIP_RE.search(subject):
        errors.append("work-in-progress marker in subject; squash or amend before merge")

    if re.match(r"^[A-Z][a-z]+(\(|:| )", subject) and not HEADER_RE.match(subject):
        warnings.append("subject looks like a sentence, not a Conventional Commit")

    # Body checks
    if body.strip():
        if lines[1].strip() != "":
            warnings.append("body should be separated from the subject by a blank line")
        for offset, line in enumerate(body.split("\n"), start=2):
            if len(line.rstrip()) > max_body_line:
                warnings.append(
                    f"body line {offset} is {len(line.rstrip())} chars (max {max_body_line})"
                )
                break

    has_breaking_footer = bool(BREAKING_RE.search(body))
    if has_breaking_footer and not body.strip().startswith("BREAKING"):
        if not re.search(r"\n\nBREAKING", "\n" + body):
            warnings.append("BREAKING CHANGE footer should be a separate paragraph")

    if has_breaking_footer and not description:
        errors.append("breaking change needs a description of what changed")

    return {
        "index": index,
        "subject": subject,
        "type": ctype,
        "scope": scope.strip() if scope else None,
        "errors": errors,
        "warnings": warnings,
        "breaking": bool(match.group("bang")) or has_breaking_footer,
        "ok": not errors,
        "skipped": False,
    }


def split_input(text: str) -> list[str]:
    """Split input into commit blocks.

    A ---COMMIT--- marker is authoritative. Without one, blocks break only at a
    blank line followed by a known Conventional Commit header, so a body or a
    BREAKING CHANGE footer stays attached to its commit.
    """
    if "---COMMIT---" in text:
        chunks = text.split("---COMMIT---")
    else:
        lines = text.replace("\r\n", "\n").split("\n")
        chunks: list[str] = []
        current: list[str] = []
        for index, line in enumerate(lines):
            if line.strip():
                current.append(line)
                continue
            nxt = next((l for l in lines[index + 1:] if l.strip()), "")
            match = HEADER_RE.match(nxt.strip())
            if current and match and match.group("type").lower() in ALLOWED_TYPES:
                chunks.append("\n".join(current))
                current = []
            elif current:
                current.append(line)
        if current:
            chunks.append("\n".join(current))
    return [c for c in (chunk.strip() for chunk in chunks) if c]


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def read_git_range(rng: str, repo: str | None) -> list[str]:
    cmd = ["git", "log", "--no-merges", "--format=%B%x1f", rng]
    try:
        result = subprocess.run(cmd, cwd=repo or None, capture_output=True,
                                text=True, check=False)
    except FileNotFoundError as exc:
        raise InputError("git executable not found on PATH") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        raise InputError(detail[0] if detail else f"git log {rng} failed")
    return [chunk.strip() for chunk in result.stdout.split("\x1f") if chunk.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="commit_linter.py",
        description="Lint commit messages against Conventional Commit rules.",
    )
    parser.add_argument("--range", dest="rng", metavar="A..B",
                        help="git range to lint (default: HEAD~1..HEAD)")
    parser.add_argument("--input", metavar="PATH",
                        help="read commit messages from PATH ('-' for stdin)")
    parser.add_argument("--repo", metavar="DIR", default=None,
                        help="repository directory (default: current directory)")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as violations")
    parser.add_argument("--allow-merge", action="store_true", default=True,
                        help="skip merge commits (default: on)")
    parser.add_argument("--max-subject", type=int, default=DEFAULT_MAX_SUBJECT,
                        metavar="N", help=f"max subject length (default: {DEFAULT_MAX_SUBJECT})")
    parser.add_argument("--max-body-line", type=int, default=DEFAULT_MAX_BODY_LINE,
                        metavar="N", help=f"max body line length (default: {DEFAULT_MAX_BODY_LINE})")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="output format (default: text)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.input:
            blocks = split_input(read_input(args.input))
        else:
            blocks = read_git_range(args.rng or "HEAD~1..HEAD", args.repo)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = [
        lint_message(block, index=i, max_subject=args.max_subject,
                     max_body_line=args.max_body_line, allow_merge=args.allow_merge)
        for i, block in enumerate(blocks, start=1)
    ]

    failures = [
        r for r in results
        if r["errors"] or (args.strict and r["warnings"])
    ]
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)

    if args.format == "json":
        print(json.dumps({
            "checked": len(results),
            "passed": len(results) - len(failures),
            "failed": len(failures),
            "errors": total_errors,
            "warnings": total_warnings,
            "strict": args.strict,
            "results": results,
        }, indent=2))
    else:
        for r in results:
            if not r["errors"] and not (args.strict and r["warnings"]):
                continue
            label = r["subject"] or "(empty)"
            print(f"[{r['index']}] {label}")
            for err in r["errors"]:
                print(f"    error:   {err}")
            if args.strict:
                for warn in r["warnings"]:
                    print(f"    error:   {warn} (warning promoted by --strict)")
            else:
                for warn in r["warnings"]:
                    print(f"    warning: {warn}")
        if results:
            summary = (
                f"{len(results)} commit(s) checked, {len(failures)} failed, "
                f"{total_errors} error(s), {total_warnings} warning(s)"
            )
            print(summary)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
