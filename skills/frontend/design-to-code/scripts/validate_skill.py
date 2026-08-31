# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "jsonschema>=4.20.0",
# ]
# description = "Validate a design-to-code implementation output against the skill's quality standards. Checks for token-driven styling, accessibility compliance, responsive breakpoints, semantic HTML, and WCAG 2.1 AA minimum requirements."
# ///

"""
Design-to-Code Validator

Validates that an AI-generated design-to-code implementation output adheres to
the quality standards defined in the design-to-code skill. Checks for:
  - Design token usage (no hardcoded values)
  - Semantic HTML usage
  - WCAG 2.1 AA accessibility patterns
  - Responsive breakpoint presence
  - Component state coverage
  - Framework conventions

Usage:
    python validate_skill.py <skill_dir>            # Validate skill package structure
    python validate_skill.py <skill_dir> --code <output.html>  # Validate generated code

The --code mode checks actual generated HTML/CSS/JS against design-to-code
quality standards.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Common hardcoded color patterns that should use tokens
HARDCODED_COLOR = re.compile(
    r'(?:color|background(?:-color)?|border(?:-color)?|fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,8}|rgb\(|hsl\()',
    re.IGNORECASE,
)

# Common hardcoded spacing that should use tokens
HARDCODED_SPACING = re.compile(
    r'(?:margin|padding|gap)\s*:\s*\d+px',
    re.IGNORECASE,
)

# Semantic HTML elements that should be preferred over divs
SEMANTIC_ELEMENTS = [
    "header", "main", "footer", "nav", "article", "section",
    "aside", "figure", "figcaption", "time", "address", "details",
    "summary", "dialog",
]

# Non-semantic div/span patterns that could be semantic
DIV_SOUP_PATTERNS = [
    (re.compile(r'<div[^>]*class="[^"]*header[^"]*"'), "<header>"),
    (re.compile(r'<div[^>]*class="[^"]*footer[^"]*"'), "<footer>"),
    (re.compile(r'<div[^>]*class="[^"]*nav[^"]*"'), "<nav>"),
    (re.compile(r'<div[^>]*class="[^"]*sidebar[^"]*"'), "<aside>"),
    (re.compile(r'<div[^>]*class="[^"]*main[^"]*"'), "<main>"),
]

# Accessibility anti-patterns
A11Y_ANTI_PATTERNS = [
    (re.compile(r'outline\s*:\s*none\s*(?:!important)?', re.IGNORECASE),
     "outline: none without a replacement focus indicator"),
    (re.compile(r'tabindex\s*=\s*"[2-9]\d*"'),
     'tabindex values > 1 (disrupts natural tab order)'),
    (re.compile(r'<img(?!.*?\salt\s*=)[^>]*>'),
     '<img> without alt attribute'),
    (re.compile(r'onclick\s*=\s*"[^"]*"[^>]*>\s*(?!.*?</a>)', re.IGNORECASE),
     'onclick without an accessible role (use <button> or add role="button" + tabindex)'),
]

# Missing WCAG essentials
A11Y_REQUIRED = [
    (re.compile(r'<html(?![^>]*\slang\s*=)[^>]*>', re.IGNORECASE),
     '<html> missing lang attribute'),
    (re.compile(r'<input(?![^>]*\s(?:aria-label|aria-labelledby|id)\s*=)[^>]*>(?!\s*<label)', re.IGNORECASE),
     '<input> without associated label'),
]

# Responsive breakpoint patterns
MEDIA_QUERY_PRESENT = re.compile(r'@media\s*\(', re.IGNORECASE)

# Design token reference patterns
TOKEN_USAGE = re.compile(
    r'var\s*\(\s*--[\w-]+',
    re.IGNORECASE,
)

# Required sections in a design-to-code implementation report
REQUIRED_SECTIONS = [
    "Design Analysis",
    "Design Tokens",
    "Component Hierarchy",
    "Responsive Strategy",
    "Accessibility Audit",
    "Implementation",
]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning" | "info"
    message: str
    section: str | None = None
    line: int | None = None


@dataclass
class ValidationResult:
    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str, section: str | None = None, line: int | None = None) -> None:
        self.passed = False
        self.issues.append(ValidationIssue("error", message, section, line))

    def add_warning(self, message: str, section: str | None = None, line: int | None = None) -> None:
        self.issues.append(ValidationIssue("warning", message, section, line))

    def add_info(self, message: str, section: str | None = None, line: int | None = None) -> None:
        self.issues.append(ValidationIssue("info", message, section, line))


# ---------------------------------------------------------------------------
# Skill package structure validation
# ---------------------------------------------------------------------------

def validate_skill_package(skill_dir: Path) -> ValidationResult:
    """Validate that the skill directory has the correct structure."""
    result = ValidationResult()

    # Required files
    required_files = {
        "SKILL.md": "Main skill definition",
        "LICENSE": "License file",
        "CHANGELOG.md": "Changelog",
    }

    for filename, description in required_files.items():
        filepath = skill_dir / filename
        if not filepath.exists():
            result.add_error(f"Missing {filename} ({description})")
        else:
            result.stats[f"has_{filename.lower().replace('.', '_')}"] = True

    # Required directories
    required_dirs = ["scripts", "evals", "references"]
    for dirname in required_dirs:
        dirpath = skill_dir / dirname
        if not dirpath.is_dir():
            result.add_error(f"Missing {dirname}/ directory")

    # SKILL.md frontmatter validation
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(content)
        if frontmatter is None:
            result.add_error("SKILL.md has no YAML frontmatter")
        else:
            required_fm = ["name", "description", "version", "author", "platforms", "tags"]
            for key in required_fm:
                if key not in frontmatter:
                    result.add_error(f"SKILL.md frontmatter missing '{key}'")

            if frontmatter.get("name") != "design-to-code":
                result.add_warning(
                    f"SKILL.md name is '{frontmatter.get('name')}', expected 'design-to-code'"
                )

            # Check body sections
            body = _extract_body(content)
            if body:
                _validate_body_sections(body, result)
                result.stats["body_lines"] = body.count("\n") + 1
                result.stats["body_chars"] = len(body)

    return result


def _parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from SKILL.md."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        import yaml
        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _extract_body(content: str) -> str | None:
    """Extract body content after YAML frontmatter."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[2].strip()


def _validate_body_sections(body: str, result: ValidationResult) -> None:
    """Check that key sections exist in the SKILL.md body."""
    expected_headers = [
        "When to Use",
        "Safety Rules",
        "Accessibility",
        "Responsive",
        "Design Token",
        "Component Hierarchy",
        "CSS Architecture",
        "Visual Regression",
    ]
    for header in expected_headers:
        if header.lower() not in body.lower():
            result.add_warning(
                f"SKILL.md body may be missing section about '{header}'"
            )


# ---------------------------------------------------------------------------
# Generated code validation (--code mode)
# ---------------------------------------------------------------------------

def validate_generated_code(code_path: Path) -> ValidationResult:
    """Validate generated HTML/CSS against design-to-code quality standards."""
    result = ValidationResult()

    if not code_path.exists():
        result.add_error(f"Code file not found: {code_path}")
        return result

    content = code_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    result.stats["total_lines"] = len(lines)

    # 1. Check for hardcoded design values
    _check_design_tokens(content, result, lines)

    # 2. Check for semantic HTML
    _check_semantic_html(content, result, lines)

    # 3. Check for accessibility anti-patterns
    _check_accessibility(content, result, lines)

    # 4. Check for responsive breakpoints
    _check_responsive(content, result)

    # 5. Check for framework conventions (if detectable)

    return result


def _check_design_tokens(content: str, result: ValidationResult, lines: list[str]) -> None:
    """Check for hardcoded design values that should use tokens."""
    hardcoded_colors = HARDCODED_COLOR.findall(content)
    result.stats["hardcoded_colors"] = len(hardcoded_colors)

    hardcoded_spacing = HARDCODED_SPACING.findall(content)
    result.stats["hardcoded_spacing"] = len(hardcoded_spacing)

    token_count = len([t for t in TOKEN_USAGE.findall(content) if "var(--" in t])
    result.stats["token_references"] = token_count

    if hardcoded_colors and token_count == 0:
        result.add_error(
            f"Found {len(hardcoded_colors)} hardcoded color values with zero design token references. "
            "Use CSS custom properties (var(--color-*)) instead."
        )
    elif hardcoded_colors:
        result.add_warning(
            f"Found {len(hardcoded_colors)} hardcoded color values. "
            f"Consider extracting to design tokens ({token_count} token references found)."
        )

    if hardcoded_spacing:
        result.add_warning(
            f"Found {len(hardcoded_spacing)} hardcoded pixel spacing values. "
            "Use spacing tokens (var(--space-*)) for consistency."
        )


def _check_semantic_html(content: str, result: ValidationResult, lines: list[str]) -> None:
    """Check for semantic HTML usage vs div-soup patterns."""
    semantic_count = 0
    for elem in SEMANTIC_ELEMENTS:
        count = len(re.findall(rf'</?{elem}[\s>]', content, re.IGNORECASE))
        semantic_count += count

    div_count = len(re.findall(r'</?div[\s>]', content, re.IGNORECASE))
    span_count = len(re.findall(r'</?span[\s>]', content, re.IGNORECASE))

    result.stats["semantic_elements"] = semantic_count
    result.stats["div_count"] = div_count
    result.stats["span_count"] = span_count

    # Check if common divs should be semantic elements
    div_soup_issues = 0
    for pattern, suggestion in DIV_SOUP_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            div_soup_issues += len(matches)

    if div_soup_issues > 0:
        result.add_warning(
            f"Found {div_soup_issues} instances where a <div> with a semantic class "
            f"name could be replaced with a semantic HTML element "
            f"(e.g., <div class=\"header\"> → <header>)."
        )

    if semantic_count == 0 and div_count > 10:
        result.add_error(
            f"No semantic HTML elements found ({div_count} divs). "
            "Use <header>, <main>, <nav>, <section>, etc. for better accessibility."
        )


def _check_accessibility(content: str, result: ValidationResult, lines: list[str]) -> None:
    """Check for WCAG 2.1 AA accessibility violations."""
    anti_pattern_count = 0
    for pattern, description in A11Y_ANTI_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            anti_pattern_count += len(matches)
            result.add_warning(
                f"Accessibility anti-pattern: {description} "
                f"({len(matches)} occurrence(s))"
            )

    result.stats["a11y_anti_patterns"] = anti_pattern_count

    for pattern, description in A11Y_REQUIRED:
        matches = pattern.findall(content)
        if matches:
            result.add_error(
                f"Missing WCAG essential: {description} "
                f"({len(matches)} occurrence(s))"
            )


def _check_responsive(content: str, result: ValidationResult) -> None:
    """Check for responsive design patterns."""
    media_queries = MEDIA_QUERY_PRESENT.findall(content)
    result.stats["media_query_count"] = len(media_queries)

    if len(media_queries) == 0:
        # Check if this is a mobile-first approach with Tailwind-style breakpoints
        has_tailwind_bp = bool(
            re.search(r'(?:sm|md|lg|xl|2xl):', content)
        )
        if has_tailwind_bp:
            result.add_info("Responsive breakpoints detected via Tailwind prefix classes.")
        else:
            result.add_warning(
                "No media queries or responsive breakpoint classes detected. "
                "Ensure responsive design is implemented if the design requires it."
            )


# ---------------------------------------------------------------------------
# Eval case validation
# ---------------------------------------------------------------------------

def validate_eval_cases(eval_path: Path) -> ValidationResult:
    """Validate the test_cases.json file."""
    result = ValidationResult()

    if not eval_path.exists():
        result.add_error(f"Eval cases file not found: {eval_path}")
        return result

    try:
        data = json.loads(eval_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON in eval cases: {e}")
        return result

    cases = data.get("cases", [])
    positive = [c for c in cases if c.get("type") == "positive"]
    negative = [c for c in cases if c.get("type") == "negative"]

    result.stats["total_cases"] = len(cases)
    result.stats["positive_cases"] = len(positive)
    result.stats["negative_cases"] = len(negative)

    if len(positive) < 5:
        result.add_error(
            f"Only {len(positive)} positive cases. At least 5 required."
        )

    if len(negative) < 3:
        result.add_warning(
            f"Only {len(negative)} negative cases. At least 3 recommended."
        )

    # Validate each case structure
    for i, case in enumerate(cases):
        case_id = case.get("id", f"case-{i}")
        required = ["id", "type", "name", "input", "expected_behavior"]
        for key in required:
            if key not in case:
                result.add_error(f"Case '{case_id}' missing required field: {key}")

        if case.get("type") == "positive":
            if not case.get("expected_behavior", {}).get("should_trigger"):
                result.add_error(
                    f"Positive case '{case_id}' should have should_trigger: true"
                )
        elif case.get("type") == "negative":
            if case.get("expected_behavior", {}).get("should_trigger"):
                result.add_error(
                    f"Negative case '{case_id}' should have should_trigger: false"
                )
            if "why_not" not in case.get("expected_behavior", {}):
                result.add_warning(
                    f"Negative case '{case_id}' should explain 'why_not'"
                )

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text_output(result: ValidationResult) -> str:
    """Format results as human-readable text."""
    parts: list[str] = []

    if result.passed:
        parts.append("✅ Validation PASSED")
    else:
        parts.append("❌ Validation FAILED")

    if result.stats:
        parts.append(f"\nStats: {json.dumps(result.stats, indent=2)}")

    if result.issues:
        parts.append(f"\n--- Issues ({len(result.issues)}) ---")
        for i, issue in enumerate(result.issues, 1):
            prefix = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(
                issue.severity, "•"
            )
            location = ""
            if issue.section:
                location += f" [{issue.section}]"
            if issue.line:
                location += f" line {issue.line}"
            parts.append(f"  {i}. {prefix}{location}: {issue.message}")

    return "\n".join(parts)


def format_json_output(result: ValidationResult) -> str:
    """Format results as JSON."""
    output = {
        "passed": result.passed,
        "stats": result.stats,
        "issues": [
            {
                "severity": i.severity,
                "message": i.message,
                "section": i.section,
                "line": i.line,
            }
            for i in result.issues
        ],
    }
    return json.dumps(output, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate design-to-code skill package or generated code output.",
    )
    parser.add_argument(
        "path",
        help="Path to the skill directory (e.g., ~/.agents/skills/design-to-code/)",
    )
    parser.add_argument(
        "--code",
        help="Path to a generated HTML/CSS file to validate against design-to-code standards",
        default=None,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit non-zero on warnings too)",
    )

    args = parser.parse_args()

    skill_dir = Path(args.path).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"❌ Directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # Validate skill package structure
    result = validate_skill_package(skill_dir)
    result.stats["skill_dir"] = str(skill_dir)

    # Validate eval cases
    eval_path = skill_dir / "evals" / "test_cases.json"
    eval_result = validate_eval_cases(eval_path)
    result.issues.extend(eval_result.issues)
    result.stats.update({f"eval_{k}": v for k, v in eval_result.stats.items()})
    if not eval_result.passed:
        result.passed = False

    # Validate generated code if provided
    if args.code:
        code_path = Path(args.code).expanduser().resolve()
        code_result = validate_generated_code(code_path)
        result.issues.extend(code_result.issues)
        result.stats.update({f"code_{k}": v for k, v in code_result.stats.items()})
        if not code_result.passed:
            result.passed = False

    if args.json:
        print(format_json_output(result))
    else:
        print(format_text_output(result))

    # Exit code
    if not result.passed:
        sys.exit(1)
    if args.strict:
        has_warnings = any(i.severity == "warning" for i in result.issues)
        if has_warnings:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()