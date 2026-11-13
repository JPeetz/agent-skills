#!/usr/bin/env python3
"""Generate a Keep a Changelog entry from Conventional Commits.

Reads commits either from a git range or from a file/stdin, groups them into
changelog sections, and detects the semantic version bump they imply.

Stdlib only. No third-party dependencies.

Examples:
    python3 generate_changelog.py --from v1.4.0 --to HEAD
    python3 generate_changelog.py --from v1.4.0 --next --format json
    git log --format='%s%n%b%n---COMMIT---' v1.4.0..HEAD \
        | python3 generate_changelog.py --input - --version 1.5.0
    python3 generate_changelog.py --from v1.4.0 --version 1.5.0 --update CHANGELOG.md

Exit codes: 0 success, 2 usage or input error.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

# type -> changelog section. None means "not user-facing, omit by default".
TYPE_TO_SECTION = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "docs": "Documentation",
    "security": "Security",
    "deprecated": "Deprecated",
    "remove": "Removed",
    "revert": "Changed",
    "build": "Changed",
    "test": None,
    "ci": None,
    "chore": None,
    "style": None,
}

SECTION_ORDER = [
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
    "Documentation",
]

KNOWN_TYPES = sorted(TYPE_TO_SECTION)

# <type>(<scope>)!<optional whitespace>: <description>
HEADER_RE = re.compile(
    r"^(?P<type>[A-Za-z]+)"
    r"(?:\((?P<scope>[^()\r\n]+)\))?"
    r"(?P<bang>!)?"
    r":\s*(?P<description>\S.*)$"
)

BREAKING_RE = re.compile(r"^BREAKING[ -]CHANGE:\s*(?P<text>.+)$", re.IGNORECASE | re.MULTILINE)

MERGE_PREFIXES = ("merge ", "revert \"", "rebase ")


class InputError(Exception):
    """Raised when commits cannot be read or parsed."""


def parse_commit(raw: str) -> dict | None:
    """Parse one raw commit message into a structured record.

    Returns None for messages that cannot or should not become changelog lines
    (empty blocks, merge commits, non-conventional messages).
    """
    text = raw.replace("\r\n", "\n").strip()
    if not text:
        return None

    lines = text.split("\n")
    header = lines[0].strip()

    if header.lower().startswith(MERGE_PREFIXES):
        return None

    match = HEADER_RE.match(header)
    if not match:
        return None

    ctype = match.group("type").lower()
    if ctype not in TYPE_TO_SECTION:
        return None

    body = "\n".join(lines[1:]).strip()
    breaking_notes = [m.group("text").strip() for m in BREAKING_RE.finditer(body)]
    breaking = bool(match.group("bang")) or bool(breaking_notes)

    description = match.group("description").strip()
    scope = match.group("scope").strip() if match.group("scope") else None

    return {
        "type": ctype,
        "scope": scope,
        "description": description,
        "breaking": breaking,
        "breaking_notes": breaking_notes,
        # A breaking change belongs under Changed regardless of its type: the
        # consumer-relevant fact is that behavior changed, not that it was a feat.
        "section": "Changed" if breaking else TYPE_TO_SECTION[ctype],
        "raw": text,
    }


def split_input(text: str) -> list[str]:
    """Split raw input into commit blocks.

    Primary format is blocks separated by a ---COMMIT--- marker (as produced by
    `git log --format='%s%n%b%n---COMMIT---'`). Without a marker, a block only
    breaks at a blank line whose next line starts a known Conventional Commit
    header -- otherwise multi-paragraph bodies would be shredded into
    "commits" (a BREAKING CHANGE footer paragraph, for instance).
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
            if current and match and match.group("type").lower() in TYPE_TO_SECTION:
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


def _git(args: list[str], repo: str | None) -> str:
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=repo or None,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise InputError("git executable not found on PATH") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        message = detail[0] if detail else f"git {' '.join(args)} failed"
        raise InputError(message)
    return result.stdout


def latest_tag(repo: str | None) -> str | None:
    """Return the most recent reachable tag, or None if the repo has none."""
    try:
        out = _git(["describe", "--tags", "--abbrev=0"], repo).strip()
    except InputError:
        return None
    return out or None


def read_git_range(start: str | None, end: str, repo: str | None) -> list[str]:
    """Read commit messages from a git range using an ASCII record separator."""
    rng = f"{start}..{end}" if start else end
    # %x1f (unit separator) terminates each record; %B is the raw body.
    out = _git(["log", "--no-merges", "--format=%B%x1f", rng], repo)
    return [chunk.strip() for chunk in out.split("\x1f") if chunk.strip()]


def detect_bump(commits: list[dict]) -> str | None:
    """Return 'major', 'minor', 'patch', or None for a commit list."""
    relevant = [c for c in commits if c["section"] is not None or c["breaking"]]
    if not relevant:
        return None
    if any(c["breaking"] for c in relevant):
        return "major"
    if any(c["type"] == "feat" for c in relevant):
        return "minor"
    return "patch"


def bump_version(current: str | None, bump: str | None) -> str | None:
    """Apply a semver bump to a version string, ignoring pre-release/build metadata."""
    if not bump:
        return current
    if not current:
        raise InputError("--next requires a current version (--current or a tag)")
    core = current.lstrip("vV").split("-")[0].split("+")[0]
    parts = core.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise InputError(f"not a semantic version: {current!r}")
    major, minor, patch = (int(p) for p in parts)
    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def group_commits(commits: list[dict]) -> dict[str, list[dict]]:
    """Group parsed commits by changelog section, preserving input order."""
    grouped: dict[str, list[dict]] = {}
    for commit in commits:
        section = commit["section"]
        if section is None:
            continue
        grouped.setdefault(section, []).append(commit)
    return grouped


def _entry_line(commit: dict) -> str:
    scope = f"**{commit['scope']}:** " if commit["scope"] else ""
    return f"- {scope}{commit['description']}"


def render_markdown(
    commits: list[dict],
    version: str,
    release_date: str,
    include_empty: bool = False,
) -> str:
    """Render a Keep a Changelog section."""
    grouped = group_commits(commits)
    heading = f"## [{version}] - {release_date}"
    out = [heading, ""]

    if not grouped and not include_empty:
        out.append("No user-facing changes in this release.")
        out.append("")
        return "\n".join(out)

    for section in SECTION_ORDER:
        entries = grouped.get(section)
        if not entries:
            continue
        out.append(f"### {section}")
        out.append("")
        for commit in entries:
            out.append(_entry_line(commit))
        out.append("")

    breaking = [c for c in commits if c["breaking"] and c["breaking_notes"]]
    if breaking:
        out.append("### Migration Notes")
        out.append("")
        for commit in breaking:
            for note in commit["breaking_notes"]:
                out.append(f"- {note}")
        out.append("")

    return "\n".join(out)


def render_json(
    commits: list[dict],
    version: str,
    release_date: str,
    bump: str | None,
) -> str:
    grouped = group_commits(commits)
    payload = {
        "version": version,
        "date": release_date,
        "bump": bump,
        "counts": {section: len(grouped.get(section, [])) for section in SECTION_ORDER},
        "breaking": [
            {"description": c["description"], "notes": c["breaking_notes"]}
            for c in commits
            if c["breaking"]
        ],
        "sections": {
            section: [
                {
                    "type": c["type"],
                    "scope": c["scope"],
                    "description": c["description"],
                    "breaking": c["breaking"],
                }
                for c in grouped.get(section, [])
            ]
            for section in SECTION_ORDER
            if grouped.get(section)
        },
        "skipped": sum(1 for c in commits if c["section"] is None),
    }
    return json.dumps(payload, indent=2)


def update_changelog(path: str, entry: str, version: str) -> None:
    """Prepend an entry to an existing CHANGELOG.md, preserving all prior content."""
    if not os.path.exists(path):
        raise InputError(f"--update target does not exist: {path}")

    with open(path, encoding="utf-8") as handle:
        existing = handle.read()

    if re.search(rf"^##\s*\[{re.escape(version)}\]", existing, re.MULTILINE):
        raise InputError(f"version {version} already present in {path}")

    lines = existing.split("\n")
    insert_at = None
    for index, line in enumerate(lines):
        if re.match(r"^##\s", line):
            insert_at = index
            break

    block = entry.rstrip("\n").split("\n") + [""]

    if insert_at is None:
        # No prior release sections: append after the title block.
        if not lines or not lines[0].startswith("#"):
            lines = ["# Changelog", ""] + lines
        while len(lines) > 1 and lines[-1].strip() == "":
            lines.pop()
        new_lines = lines + [""] + block
    else:
        # Collapse runs of blank lines before the first section to exactly one,
        # so the new entry stays separated from the title without doubling gaps.
        while (
            insert_at > 1
            and lines[insert_at - 1].strip() == ""
            and lines[insert_at - 2].strip() == ""
        ):
            insert_at -= 1
            del lines[insert_at]
        new_lines = lines[:insert_at] + block + lines[insert_at:]

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(new_lines).rstrip("\n") + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_changelog.py",
        description="Render a Keep a Changelog entry from Conventional Commits.",
        epilog="Reads from git when --input is omitted.",
    )
    parser.add_argument("--from", dest="start", metavar="REF",
                        help="start ref, exclusive (default: most recent tag)")
    parser.add_argument("--to", dest="end", default="HEAD", metavar="REF",
                        help="end ref, inclusive (default: HEAD)")
    parser.add_argument("--input", metavar="PATH",
                        help="read commits from PATH instead of git ('-' for stdin)")
    parser.add_argument("--version", metavar="X.Y.Z",
                        help="version to render in the heading (default: Unreleased)")
    parser.add_argument("--current", metavar="X.Y.Z",
                        help="current version, used to compute the next one")
    parser.add_argument("--next", action="store_true",
                        help="print the next version implied by the commits and exit")
    parser.add_argument("--date", metavar="YYYY-MM-DD", default=None,
                        help="release date (default: today)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown",
                        help="output format (default: markdown)")
    parser.add_argument("--repo", metavar="DIR", default=None,
                        help="repository directory (default: current directory)")
    parser.add_argument("--update", metavar="PATH", default=None,
                        help="prepend the entry to an existing CHANGELOG.md")
    parser.add_argument("--include-empty", action="store_true",
                        help="emit empty sections instead of the no-changes notice")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.input:
            raw_blocks = split_input(read_input(args.input))
        else:
            start = args.start or latest_tag(args.repo)
            raw_blocks = read_git_range(start, args.end, args.repo)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    commits = [c for c in (parse_commit(block) for block in raw_blocks) if c]
    bump = detect_bump(commits)
    release_date = args.date or datetime.date.today().isoformat()

    if args.date:
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            print(f"error: --date must be YYYY-MM-DD, got {args.date!r}", file=sys.stderr)
            return 2

    version = args.version
    if args.next:
        current = args.current or args.start or latest_tag(args.repo)
        try:
            next_version = bump_version(current, bump)
        except InputError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.format == "json":
            print(json.dumps(
                {"bump": bump, "current": current, "version": next_version},
                indent=2,
            ))
        else:
            print(next_version if next_version else "no-release")
        return 0

    if version is None:
        computed = bump_version(args.current, bump) if (args.current and bump) else None
        version = computed or "Unreleased"

    if args.format == "json":
        output = render_json(commits, version, release_date, bump)
    else:
        output = render_markdown(commits, version, release_date, args.include_empty)

    if args.update:
        try:
            update_changelog(args.update, output, version)
        except InputError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"updated {args.update} with [{version}]", file=sys.stderr)
        return 0

    print(output.rstrip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
