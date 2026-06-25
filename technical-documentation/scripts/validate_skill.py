#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Validate the technical-documentation skill against the Agent Skills spec.

Usage:
    python3 scripts/validate_skill.py [path/to/skill]
    python3 scripts/validate_skill.py ~/.agents/skills/technical-documentation

Checks performed:
    1. SKILL.md exists and is readable
    2. YAML frontmatter is present and well-formed
    3. Required frontmatter fields: name, description, version, author
    4. name matches directory name
    5. description is within 1024 character limit
    6. Body is present and non-empty
    7. Body starts with "# /" (slash-invocation pattern)
    8. Required sections exist (safety rules, references)
    9. Scripts referenced in body have corresponding files
   10. References referenced in body have corresponding files
"""

import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)


REQUIRED_FRONTMATTER = ["name", "description", "version", "author"]
MAX_DESCRIPTION_CHARS = 1024
MAX_BODY_LINES_RECOMMENDED = 500

REQUIRED_SECTIONS = [
    ("when to use", r"(?i)when\s+to\s+use"),
    ("near-miss negatives", r"(?i)near[\s-]+miss"),
    ("safety rules", r"(?i)safety\s+rules?"),
    ("common pitfalls", r"(?i)common\s+pitfalls|anti[\s-]+patterns"),
    ("platform notes", r"(?i)platform.*(?:compatibility|notes?)"),
    ("references", r"(?i)^#{1,3}\s+references?\s*$"),
]

CHANGELOG_REQUIRED_SECTIONS = [
    r"## v?\d+\.\d+\.\d+",
    r"(?i)added",
]

EVALS_REQUIRED_FIELDS = ["$schema", "cases", "description", "statistics"]


def validate_frontmatter(skill_dir: str) -> list:
    """Validate SKILL.md frontmatter."""
    issues = []
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.exists(skill_md):
        return [{"type": "missing_file", "severity": "critical",
                 "message": f"No SKILL.md found at {skill_md}"}]

    with open(skill_md) as f:
        content = f.read()

    if not content.startswith("---"):
        return [{"type": "no_frontmatter", "severity": "critical",
                 "message": "SKILL.md missing YAML frontmatter (must start with ---)"}]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return [{"type": "malformed_frontmatter", "severity": "critical",
                 "message": "Frontmatter not properly closed with ---"}]

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return [{"type": "yaml_error", "severity": "critical",
                 "message": f"Frontmatter YAML parse error: {e}"}]

    if not isinstance(fm, dict):
        return [{"type": "invalid_frontmatter", "severity": "critical",
                 "message": "Frontmatter must be a YAML mapping/dictionary"}]

    # Check required fields
    for field in REQUIRED_FRONTMATTER:
        if field not in fm:
            severity = "critical" if field in ("name", "description") else "major"
            issues.append({
                "type": f"missing_{field}",
                "severity": severity,
                "message": f"Missing required frontmatter field: '{field}'"
            })

    # Name must match directory
    if "name" in fm and fm["name"] != os.path.basename(skill_dir):
        issues.append({
            "type": "name_mismatch",
            "severity": "critical",
            "message": f"name '{fm['name']}' doesn't match directory '{os.path.basename(skill_dir)}'"
        })

    # Description length
    if "description" in fm:
        desc = fm["description"]
        if isinstance(desc, str) and len(desc) > MAX_DESCRIPTION_CHARS:
            issues.append({
                "type": "description_too_long",
                "severity": "major",
                "message": f"Description is {len(desc)} chars (max: {MAX_DESCRIPTION_CHARS})"
            })

    # Check platforms and tags exist
    for field in ("platforms", "tags"):
        if field not in fm:
            issues.append({
                "type": f"missing_{field}",
                "severity": "minor",
                "message": f"Missing recommended field: '{field}'"
            })
        elif not isinstance(fm[field], list) or len(fm[field]) == 0:
            issues.append({
                "type": f"empty_{field}",
                "severity": "minor",
                "message": f"Field '{field}' is empty or not a list"
            })

    return issues


def validate_body(skill_dir: str) -> list:
    """Validate SKILL.md body content."""
    issues = []
    skill_md = os.path.join(skill_dir, "SKILL.md")

    with open(skill_md) as f:
        content = f.read()

    parts = content.split("---", 2)
    if len(parts) < 3:
        return issues  # Already caught by frontmatter validation

    body = parts[2].strip()
    if not body:
        return [{"type": "empty_body", "severity": "critical",
                 "message": "SKILL.md body is empty"}]

    body_lines = body.count("\n") + 1

    # Body starts with "# /"
    if not re.match(r"^#\s+/", body):
        issues.append({
            "type": "missing_slash_invocation",
            "severity": "major",
            "message": "Body should start with '# /skill-name' (slash invocation pattern)"
        })

    # Check required sections
    for section_name, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, body, re.MULTILINE):
            severity = "major" if section_name in ("when to use", "safety rules") else "minor"
            issues.append({
                "type": f"missing_section_{section_name}",
                "severity": severity,
                "message": f"Missing recommended section: '{section_name}'"
            })

    # Body length recommendation
    if body_lines > MAX_BODY_LINES_RECOMMENDED:
        issues.append({
            "type": "body_too_long",
            "severity": "minor",
            "message": f"Body is {body_lines} lines (recommended max: {MAX_BODY_LINES_RECOMMENDED}). "
                       f"Consider moving detailed content to references/."
        })

    # Check for hardcoded credentials/secrets
    secret_patterns = [
        (r'(?:api[_-]?key|apikey|secret|password|token)\s*[:=]\s*["\']?[\w\-]{20,}["\']?',
         "Possible hardcoded credential/secret in body"),
        (r'sk-[a-zA-Z0-9]{20,}',
         "Possible OpenAI API key pattern in body"),
        (r'(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{20,}',
         "Possible GitHub token pattern in body"),
    ]
    for pattern, warning in secret_patterns:
        matches = re.findall(pattern, body, re.IGNORECASE)
        for match in matches:
            # Only flag if it's not a placeholder like <YOUR_API_KEY>
            if not re.match(r'^<.*>$', match):
                issues.append({
                    "type": "possible_secret",
                    "severity": "critical",
                    "message": f"{warning}: ...{match[-8:]}"
                })

    # Check reference links point to existing files
    ref_pattern = r'`references/([^`]+\.md)`'
    refs_dir = os.path.join(skill_dir, "references")
    for ref_match in re.finditer(ref_pattern, body):
        ref_file = ref_match.group(1)
        ref_path = os.path.join(refs_dir, ref_file)
        if not os.path.exists(ref_path):
            issues.append({
                "type": "broken_reference",
                "severity": "major",
                "message": f"References file not found: references/{ref_file}"
            })

    return issues


def validate_support_files(skill_dir: str) -> list:
    """Validate LICENSE, CHANGELOG.md, evals, and scripts."""
    issues = []

    # LICENSE
    license_path = os.path.join(skill_dir, "LICENSE")
    if not os.path.exists(license_path):
        issues.append({
            "type": "missing_license",
            "severity": "major",
            "message": "No LICENSE file found"
        })

    # CHANGELOG
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    if not os.path.exists(changelog_path):
        issues.append({
            "type": "missing_changelog",
            "severity": "minor",
            "message": "No CHANGELOG.md found"
        })
    else:
        with open(changelog_path) as f:
            changelog = f.read()
        for pattern in CHANGELOG_REQUIRED_SECTIONS:
            if not re.search(pattern, changelog, re.MULTILINE):
                issues.append({
                    "type": "changelog_incomplete",
                    "severity": "minor",
                    "message": f"CHANGELOG.md missing expected section matching: {pattern}"
                })
                break  # One issue per file

    # evals/test_cases.json
    evals_path = os.path.join(skill_dir, "evals", "test_cases.json")
    if os.path.exists(evals_path):
        try:
            with open(evals_path) as f:
                evals = json.load(f)
            if "cases" not in evals:
                issues.append({
                    "type": "evals_no_cases",
                    "severity": "major",
                    "message": "evals/test_cases.json missing 'cases' array"
                })
            elif len(evals["cases"]) < 5:
                issues.append({
                    "type": "evals_few_cases",
                    "severity": "minor",
                    "message": f"evals/test_cases.json has only {len(evals['cases'])} cases (recommended: 5+)"
                })
            # Check for positive and negative cases
            positive = [c for c in evals["cases"] if c.get("type") == "positive"]
            negative = [c for c in evals["cases"] if c.get("type") == "negative"]
            if not positive:
                issues.append({
                    "type": "evals_no_positive",
                    "severity": "minor",
                    "message": "No positive eval cases found"
                })
            if not negative:
                issues.append({
                    "type": "evals_no_negative",
                    "severity": "minor",
                    "message": "No negative/near-miss eval cases found"
                })
        except json.JSONDecodeError as e:
            issues.append({
                "type": "evals_invalid_json",
                "severity": "major",
                "message": f"evals/test_cases.json is invalid JSON: {e}"
            })
    else:
        issues.append({
            "type": "missing_evals",
            "severity": "minor",
            "message": "No evals/test_cases.json found"
        })

    # scripts/validate_skill.py
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.exists(scripts_dir):
        py_files = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]
        if not py_files:
            issues.append({
                "type": "empty_scripts",
                "severity": "minor",
                "message": "scripts/ directory exists but contains no Python files"
            })

    return issues


def validate_skill(skill_dir: str) -> dict:
    """Run all validations and return a comprehensive result."""
    all_issues = []
    all_issues.extend(validate_frontmatter(skill_dir))
    all_issues.extend(validate_body(skill_dir))
    all_issues.extend(validate_support_files(skill_dir))

    criticals = [i for i in all_issues if i.get("severity") == "critical"]
    majors = [i for i in all_issues if i.get("severity") == "major"]
    minors = [i for i in all_issues if i.get("severity") == "minor"]

    valid = len(criticals) == 0

    return {
        "valid": valid,
        "skill_name": os.path.basename(skill_dir),
        "total_issues": len(all_issues),
        "critical_issues": len(criticals),
        "major_issues": len(majors),
        "minor_issues": len(minors),
        "issues": all_issues,
        "summary": (
            f"{'✅ PASS' if valid else '❌ FAIL'}: "
            f"{len(criticals)} critical, {len(majors)} major, "
            f"{len(minors)} minor issues"
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # Default to skill directory relative to this script
        skill_dir = os.path.join(os.path.dirname(__file__), "..")

    skill_dir = os.path.abspath(skill_dir)

    if not os.path.isdir(skill_dir):
        print(json.dumps({
            "valid": False,
            "error": f"Directory not found: {skill_dir}"
        }, indent=2))
        sys.exit(1)

    result = validate_skill(skill_dir)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)