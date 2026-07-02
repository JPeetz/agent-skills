# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "jsonschema>=4.20.0",
# ]
# description = "Validate that AI code review output follows the correct structure, severity levels, and completeness requirements."
# ///

"""
Code Review Validator

Validates that AI-generated code review output adheres to the expected format
and quality standards defined in the code-review skill. Designed for use in
pre-commit hooks, CI pipelines, and manual validation.

Usage:
    python validate_code_review.py <review.md>         # Validate a review file
    python validate_code_review.py <review.md> --json  # Output results as JSON
    python validate_code_review.py --schema            # Print the JSON schema

The script checks:
  - Presence of required structure sections
  - Valid severity levels in findings
  - Actionable fix suggestions for BLOCKER and MAJOR issues
  - Matching recommendation vs findings
  - No hardcoded secret patterns in output
  - Conciseness of summary section
  - File/line references are present on findings
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SEVERITIES = {"BLOCKER", "MAJOR", "MINOR", "NIT"}
SEVERITY_EMOJI = {
    "BLOCKER": "🔴",
    "MAJOR": "🟠",
    "MINOR": "🟡",
    "NIT": "⚪",
}

RECOMMENDATIONS = {
    "APPROVE",
    "APPROVE WITH SUGGESTIONS",
    "APPROVE_WITH_SUGGESTIONS",
    "REQUEST CHANGES",
    "REQUEST_CHANGES",
}

REQUIRED_SECTIONS = [
    "Summary",
    "Findings",
    "Test Coverage Assessment",
    "Security Assessment",
    "Recommendation",
]

SECRET_PATTERNS = [
    re.compile(r"sk[-_]live[_-][a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)\s+PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access keys
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub tokens
    re.compile(r"xox[bpras]-[a-zA-Z0-9-]+"),  # Slack tokens
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),  # Google API keys
]

FINDING_LINE_PATTERN = re.compile(
    r"^\s*[-*]\s+\*\*(.+?)\*\*\s*[-—]\s*(.+)",
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
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


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def extract_section(text: str, header: str) -> str | None:
    """Extract the content of a markdown section by its header name.
    Stops at headings of the same or higher level (same or fewer #)."""
    pattern = rf"^(#{{2,4}})\s+{re.escape(header)}\s*$"
    lines = text.split("\n")
    start_idx: int | None = None
    section_level: int = 0

    for i, line in enumerate(lines):
        m = re.match(pattern, line, re.IGNORECASE)
        if m:
            start_idx = i + 1
            section_level = len(m.group(1))  # count of # characters
            break

    if start_idx is None:
        return None

    # Collect lines until a heading of same or higher level (same or fewer #)
    content_lines: list[str] = []
    for line in lines[start_idx:]:
        heading_match = re.match(r"^(#{2,4})\s+\S", line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            if heading_level <= section_level:
                break
        content_lines.append(line)

    return "\n".join(content_lines).strip()


def parse_findings(text: str) -> dict[str, list[dict[str, Any]]]:
    """Parse findings into a dict by severity level."""
    findings: dict[str, list[dict[str, Any]]] = {
        "BLOCKER": [],
        "MAJOR": [],
        "MINOR": [],
        "NIT": [],
    }

    current_severity: str | None = None
    lines = text.split("\n")

    for i, line in enumerate(lines):
        # Detect severity headers like "#### 🔴 Blockers (2)"
        sev_match = re.match(
            r"^#+\s+(?:🔴|🟠|🟡|⚪)\s*(\w+)",
            line,
        )
        if sev_match:
            sev_name = sev_match.group(1).upper().rstrip("S")  # "Blockers" -> "BLOCKER"
            if sev_name in VALID_SEVERITIES:
                current_severity = sev_name
            continue

        # Also match without emoji: "#### Blockers"
        sev_match_no_emoji = re.match(
            r"^#+\s+(Blockers?|Majors?|Minors?|Nits?)\b",
            line,
            re.IGNORECASE,
        )
        if sev_match_no_emoji:
            sev_name = sev_match_no_emoji.group(1).upper().rstrip("S")
            if sev_name in VALID_SEVERITIES:
                current_severity = sev_name
            continue

        # Detect finding bullet: "- **file:line** — description"
        if current_severity:
            finding_match = FINDING_LINE_PATTERN.match(line)
            if finding_match:
                location = finding_match.group(1).strip()
                description = finding_match.group(2).strip()
                has_fix = False

                findings[current_severity].append({
                    "location": location,
                    "description": description,
                    "line_number": i + 1,
                    "has_fix": has_fix,  # Checked later
                })

    # Post-process: check if following lines contain "Fix:" for each finding
    for _severity, items in findings.items():
        for item in items:
            # Look ahead from finding line for a fix suggestion
            fix_line_start = item["line_number"]
            for j in range(fix_line_start, min(fix_line_start + 5, len(lines))):
                if re.match(r"^\s*[-*]\s+\*\*Fix[:*]", lines[j]):
                    item["has_fix"] = True
                    break

    return findings


def detect_secrets_in_text(text: str) -> list[dict[str, Any]]:
    """Scan text for patterns resembling hardcoded secrets."""
    findings = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append({
                "pattern": pattern.pattern,
                "match": match.group()[:30] + "...",
                "position": match.start(),
            })
    return findings


# ---------------------------------------------------------------------------
# Main validation logic
# ---------------------------------------------------------------------------

def validate_review(text: str, filepath: str = "<review>") -> ValidationResult:
    """Run all validation checks against a code review document."""
    result = ValidationResult()

    lines = text.split("\n")
    result.stats["total_lines"] = len(lines)
    result.stats["file_path"] = filepath

    # ------------------------------------------------------------------
    # 1. Required sections
    # ------------------------------------------------------------------
    missing_sections = []
    present_sections = []
    for section in REQUIRED_SECTIONS:
        content = extract_section(text, section)
        if content is not None and len(content.strip()) > 0:
            present_sections.append(section)
        else:
            missing_sections.append(section)
            result.add_error(
                f"Missing or empty required section: '{section}'",
                section=section,
            )

    result.stats["present_sections"] = present_sections
    result.stats["missing_sections"] = missing_sections

    # ------------------------------------------------------------------
    # 2. Summary conciseness
    # ------------------------------------------------------------------
    summary = extract_section(text, "Summary")
    if summary:
        summary_sentences = [s.strip() for s in re.split(r"[.!\?]+", summary) if s.strip()]
        sentence_count = len(summary_sentences)
        result.stats["summary_sentences"] = sentence_count
        if sentence_count > 5:
            result.add_warning(
                f"Summary has {sentence_count} sentences (target: 2-3). Consider condensing.",
                section="Summary",
            )
        elif sentence_count == 0:
            result.add_error("Summary section is present but appears empty.", section="Summary")

    # ------------------------------------------------------------------
    # 3. Findings parsing and validation
    # ------------------------------------------------------------------
    findings_section = extract_section(text, "Findings")
    if findings_section:
        findings = parse_findings(findings_section)

        total_findings = sum(len(v) for v in findings.values())
        result.stats["total_findings"] = total_findings
        result.stats["findings_by_severity"] = {
            sev: len(items) for sev, items in findings.items()
        }

        for severity, items in findings.items():
            for item in items:
                # Check location format: should reference a file or file:line
                location = item["location"]
                if not re.search(r"[\.\/\w]+", location):
                    result.add_warning(
                        f"Finding location '{location}' doesn't look like a file reference.",
                        section="Findings",
                        line=item["line_number"],
                    )

                # Check description length
                if len(item["description"]) < 10:
                    result.add_warning(
                        f"Finding description too short: '{item['description']}'",
                        section="Findings",
                        line=item["line_number"],
                    )

                # BLOCKER and MAJOR must have fix suggestions
                if severity in ("BLOCKER", "MAJOR") and not item["has_fix"]:
                    result.add_error(
                        f"{severity} finding at '{location}' is missing a 'Fix:' suggestion.",
                        section="Findings",
                        line=item["line_number"],
                    )

    else:
        result.add_warning(
            "No 'Findings' section found. Empty review or section not parseable.",
            section="Findings",
        )

    # ------------------------------------------------------------------
    # 4. Recommendation validation
    # ------------------------------------------------------------------
    recommendation = extract_section(text, "Recommendation")
    if recommendation:
        rec_text = recommendation.upper()
        matched = False
        for rec in RECOMMENDATIONS:
            if rec.replace("_", " ") in rec_text or rec in rec_text:
                matched = True
                result.stats["recommendation"] = rec.replace("_", " ")
                break

        if not matched:
            result.add_error(
                f"Recommendation not recognized. Expected one of: {', '.join(RECOMMENDATIONS)}",
                section="Recommendation",
            )
    # Recommendation validation handled above

    # ------------------------------------------------------------------
    # 5. Recommendation vs Findings consistency
    # ------------------------------------------------------------------
    if findings_section and recommendation:
        findings = parse_findings(findings_section)
        rec_text = recommendation.upper()
        has_blockers = len(findings.get("BLOCKER", [])) > 0
        has_majors = len(findings.get("MAJOR", [])) > 0

        is_approve = "APPROVE" in rec_text and "CHANGE" not in rec_text
        is_request_changes = "REQUEST CHANGES" in rec_text or "REQUEST_CHANGES" in rec_text

        if has_blockers and not is_request_changes:
            result.add_error(
                "Review has BLOCKER findings but recommendation is not 'Request Changes'.",
                section="Recommendation",
            )
        if has_majors and is_approve and "WITH SUGGESTIONS" not in rec_text:
            result.add_warning(
                "Review has MAJOR findings but recommends 'Approve' without 'with suggestions'.",
                section="Recommendation",
            )

    # ------------------------------------------------------------------
    # 6. Secret detection
    # ------------------------------------------------------------------
    detected_secrets = detect_secrets_in_text(text)
    if detected_secrets:
        for secret in detected_secrets:
            result.add_error(
                f"Potential hardcoded secret detected: pattern matched '{secret['match']}'",
                section=None,
            )
        result.stats["secrets_detected"] = len(detected_secrets)
    else:
        result.stats["secrets_detected"] = 0

    # ------------------------------------------------------------------
    # 7. Structure: header format
    # ------------------------------------------------------------------
    header_match = re.match(r"^## Code Review:", lines[0]) if lines else None
    if not header_match:
        # Try first few lines
        header_found = any(
            re.match(r"^## Code Review:", line)
            for line in lines[:5]
        )
        if not header_found:
            result.add_warning(
                "Review should start with '## Code Review: <title>' header.",
                section="Header",
            )

    # ------------------------------------------------------------------
    # 8. Metadata line
    # ------------------------------------------------------------------
    has_metadata = any(
        re.search(r"\*\*Reviewed by\*\*", line) for line in lines[:20]
    )
    if not has_metadata:
        result.add_warning(
            "Missing 'Reviewed by' metadata line near the top of the review.",
            section="Header",
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

    parts.append(f"\nFile: {result.stats.get('file_path', 'unknown')}")
    parts.append(f"Total lines: {result.stats.get('total_lines', 0)}")
    parts.append(f"Sections present: {', '.join(result.stats.get('present_sections', []))}")

    missing = result.stats.get('missing_sections', [])
    if missing:
        parts.append(f"Sections MISSING: {', '.join(missing)}")

    findings_stats = result.stats.get('findings_by_severity', {})
    if findings_stats:
        parts.append(
            f"Findings: {result.stats.get('total_findings', 0)} total "
            f"({', '.join(f'{k}: {v}' for k, v in findings_stats.items() if v > 0)})"
        )

    if 'recommendation' in result.stats:
        parts.append(f"Recommendation: {result.stats['recommendation']}")

    secrets = result.stats.get('secrets_detected', 0)
    if secrets:
        parts.append(f"⚠️  Secrets detected: {secrets}")

    if result.issues:
        parts.append(f"\n--- Issues ({len(result.issues)}) ---")
        for i, issue in enumerate(result.issues, 1):
            prefix = "❌" if issue.severity == "error" else "⚠️"
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


def print_schema() -> None:
    """Print the expected JSON schema for a valid review."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CodeReview",
        "description": "Expected structure for an AI-generated code review",
        "type": "object",
        "required": [
            "summary",
            "findings",
            "test_coverage_assessment",
            "security_assessment",
            "recommendation",
        ],
        "properties": {
            "summary": {
                "type": "string",
                "description": "2-3 sentence summary of the change and assessment",
                "maxLength": 1000,
            },
            "findings": {
                "type": "object",
                "properties": {
                    "BLOCKER": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/finding"},
                    },
                    "MAJOR": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/finding"},
                    },
                    "MINOR": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/finding"},
                    },
                    "NIT": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/finding"},
                    },
                },
            },
            "test_coverage_assessment": {"type": "string"},
            "security_assessment": {"type": "string"},
            "recommendation": {
                "type": "string",
                "enum": [
                    "Approve",
                    "Approve with suggestions",
                    "Request changes",
                ],
            },
        },
        "$defs": {
            "finding": {
                "type": "object",
                "required": ["location", "description"],
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "File and line reference, e.g. src/auth.py:42",
                    },
                    "description": {
                        "type": "string",
                        "description": "Clear description of the issue",
                    },
                    "fix": {
                        "type": "string",
                        "description": "Required for BLOCKER and MAJOR; optional otherwise",
                    },
                },
            },
        },
    }
    print(json.dumps(schema, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate AI code review output structure and quality.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to the review markdown file to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print the expected JSON schema for a valid review and exit",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit non-zero on warnings too)",
    )

    args = parser.parse_args()

    if args.schema:
        print_schema()
        sys.exit(0)

    if not args.file:
        parser.error("FILE is required unless --schema is specified")

    path = Path(args.file)
    if not path.exists():
        print(f"❌ File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"❌ File is not valid UTF-8: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = validate_review(text, str(path))

    if args.json:
        print(format_json_output(result))
    else:
        print(format_text_output(result))

    # Exit code
    if not result.passed:
        sys.exit(1)
    if args.strict:
        # Check for any warnings
        has_warnings = any(i.severity == "warning" for i in result.issues)
        if has_warnings:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()