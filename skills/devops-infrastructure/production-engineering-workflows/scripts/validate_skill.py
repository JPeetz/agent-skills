#!/usr/bin/env python3
"""PEP 723 compliant validation script for SKILL.md.

Validates that the Production Engineering Workflows SKILL.md contains all
required frontmatter fields and body sections per the Agent Skills standard.

Usage:
    python scripts/validate_skill.py [--path PATH] [--verbose]

Returns exit code 0 on success, 1 on validation failure.
"""

# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

import re
import sys
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

REQUIRED_FRONTMATTER_FIELDS = [
    "name",
    "description",
    "version",
    "author",
    "platforms",
    "tags",
    "geo",
]

REQUIRED_PLATFORMS = [
    "claude-code",
    "codex",
    "cursor",
    "gemini-cli",
    "openclaw",
    "copilot",
    "windsurf",
    "opencode",
]

REQUIRED_BODY_SECTIONS = [
    "Production Engineering Workflows",
    "Quick Reference",
    "When to Use This Skill",
    "Do NOT Activate For",
    "Workflow Commands",
    "/spec",
    "/plan",
    "/build",
    "/test",
    "/review",
    "/webperf",
    "/code-simplify",
    "/ship",
    "Integrated Pipeline",
    "Common Pitfalls",
    "Safety Rules",
    "Verification Checklist",
    "Platform Compatibility Notes",
    "References",
]

MIN_WORD_COUNT = 3000


# ── Validation Functions ────────────────────────────────────────────────────

def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    raw = match.group(1)
    fields = {}
    current_key = None
    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        kv_match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", stripped)
        if kv_match:
            current_key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if value.startswith(">"):
                fields[current_key] = value
            elif value:
                fields[current_key] = value
            else:
                # Empty value — could be start of a list or mapping.
                # Initialize as list (most common case for empty-value keys).
                fields[current_key] = []
        elif current_key and stripped.startswith("-"):
            if current_key not in fields:
                fields[current_key] = []
            if isinstance(fields[current_key], list):
                fields[current_key].append(stripped.lstrip("- ").strip())
    return fields


def count_words(content: str) -> int:
    """Count words in markdown body (excluding frontmatter)."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if match:
        body = content[match.end():]
    else:
        body = content
    return len(re.findall(r"\b\w+\b", body))


def validate_skill(skill_path: Path, verbose: bool = False) -> tuple[bool, list[str]]:
    """Validate SKILL.md at the given path. Returns (passed, errors)."""
    errors: list[str] = []

    if not skill_path.exists():
        errors.append(f"SKILL.md not found at {skill_path}")
        return False, errors

    content = skill_path.read_text(encoding="utf-8")

    # ── Frontmatter validation ──────────────────────────────────────────

    frontmatter = extract_frontmatter(content)
    if frontmatter is None:
        errors.append("No valid YAML frontmatter found (expected --- delimiters)")
    else:
        for field in REQUIRED_FRONTMATTER_FIELDS:
            if field not in frontmatter:
                errors.append(f"Missing required frontmatter field: '{field}'")
            elif verbose:
                print(f"  ✓ frontmatter.{field} = {frontmatter[field][:60]}...")

        # Validate version follows semver
        if "version" in frontmatter:
            ver = frontmatter["version"]
            if not re.match(r"^\d+\.\d+\.\d+$", str(ver)):
                errors.append(f"version '{ver}' does not follow semver (x.y.z)")

        # Validate platforms
        if "platforms" in frontmatter:
            platforms = frontmatter.get("platforms", [])
            if isinstance(platforms, str):
                errors.append("platforms should be a list, not a string")
            elif isinstance(platforms, list):
                for p in REQUIRED_PLATFORMS:
                    if p not in platforms:
                        errors.append(f"Missing required platform: '{p}'")

        if verbose:
            print(f"  Frontmatter: {len(frontmatter)} fields found")

    # ── Body section validation ─────────────────────────────────────────

    body_lower = content.lower()
    for section in REQUIRED_BODY_SECTIONS:
        if section.lower() not in body_lower:
            errors.append(f"Missing required body section: '{section}'")
        elif verbose:
            print(f"  ✓ section: {section}")

    # ── Word count validation ───────────────────────────────────────────

    wc = count_words(content)
    if wc < MIN_WORD_COUNT:
        errors.append(
            f"Word count {wc} is below minimum of {MIN_WORD_COUNT}"
        )
    elif verbose:
        print(f"  ✓ word count: {wc} (minimum: {MIN_WORD_COUNT})")

    # ── Content quality checks ──────────────────────────────────────────

    # Check for empty/placeholder sections
    placeholder_patterns = [
        r"TODO",
        r"FIXME",
        r"write this",
        r"add content",
    ]
    for pattern in placeholder_patterns:
        if re.search(pattern, content):
            errors.append(f"SKILL.md contains placeholder: '{pattern}'")

    # ── Summary ─────────────────────────────────────────────────────────

    if verbose:
        if errors:
            print(f"\n❌ Validation FAILED with {len(errors)} error(s):")
        else:
            print(f"\n✅ Validation PASSED ({wc} words, {len(frontmatter or {})} frontmatter fields)")

    return len(errors) == 0, errors


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Production Engineering Workflows SKILL.md"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to SKILL.md (default: ../SKILL.md relative to this script)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation output",
    )
    args = parser.parse_args()

    if args.path is None:
        script_dir = Path(__file__).resolve().parent
        args.path = script_dir.parent / "SKILL.md"

    passed, errors = validate_skill(args.path, verbose=args.verbose)

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)
    else:
        print("✅ SKILL.md validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()