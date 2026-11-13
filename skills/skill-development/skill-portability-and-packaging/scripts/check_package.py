#!/usr/bin/env python3
"""Pre-flight check for a skill package before it is published or ported.

Stdlib only, no network. Complements the repo-level validator: this one also
sweeps the body for the portability hazards that break on other machines
(absolute user paths, secret-shaped tokens, host-only packaging mistakes).

Usage:
    python3 scripts/check_package.py <skill-dir>

Exit code 0 = no issues, 1 = issues found. Warnings do not fail the run.
"""
import json
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ABS_PATH_RE = re.compile(
    r"(/Users/[A-Za-z0-9._-]+[/\"']|/home/[A-Za-z0-9._-]+[/\"']|[A-Za-z]:\\\\Users\\\\[A-Za-z0-9._-]+\\\\)"
)
SECRET_RES = [
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("linear_key", re.compile(r"lin_api_[A-Za-z0-9]{10,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
PACKAGE_FILES = ["LICENSE", "CHANGELOG.md", "evals/evals.json", "references"]


def frontmatter(text):
    """Return the raw frontmatter block, or None if absent/unclosed."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def scalar(fm, key):
    """Grab a simple top-level `key: value` without requiring PyYAML."""
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def check(skill_dir):
    issues, warnings = [], []
    slug = os.path.basename(os.path.abspath(skill_dir))
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.exists(skill_md):
        return {"valid": False, "issues": [{"type": "missing_skill_md", "message": "No SKILL.md"}]}

    with open(skill_md, encoding="utf-8") as f:
        text = f.read()

    fm_pair = frontmatter(text)
    if not fm_pair:
        issues.append({"type": "frontmatter", "message": "missing or unclosed YAML frontmatter"})
        return {"valid": False, "slug": slug, "issues": issues, "warnings": warnings}
    fm, body = fm_pair

    name = scalar(fm, "name")
    if name != slug:
        issues.append({"type": "name_mismatch", "message": f"name '{name}' != folder '{slug}'"})
    if name and (len(name) > 64 or not NAME_RE.match(name)):
        issues.append({"type": "name_charset", "message": f"'{name}' must be 1-64 chars of a-z0-9- with single hyphens"})

    desc = scalar(fm, "description") or ""
    if not desc:
        issues.append({"type": "description", "message": "missing description"})
    elif len(desc) > 1024:
        issues.append({"type": "description_long", "message": f"{len(desc)} chars (spec max 1024)"})
    elif len(desc) > 160:
        warnings.append({"type": "description_budget", "message": f"{len(desc)} chars; hosts truncate early, keep triggers in the first 160"})
    if desc and not desc.lower().startswith(("use when", "use this skill when")):
        warnings.append({"type": "description_style", "message": "open with a trigger clause ('Use when ...')"})

    version = scalar(fm, "version")
    if version is None:
        warnings.append({"type": "version_missing", "message": "no version field"})
    elif not re.match(r"^\d+\.\d+\.\d+", version):
        warnings.append({"type": "version_format", "message": f"'{version}' is not semver; quote it or fix it"})

    for pkg in PACKAGE_FILES:
        if not os.path.exists(os.path.join(skill_dir, pkg)):
            warnings.append({"type": "package_file", "message": f"missing {pkg}"})

    lines = body.count("\n") + 1
    if lines > 500:
        warnings.append({"type": "body_long", "message": f"{lines} body lines (recommendation: <500)"})

    for label, rx in SECRET_RES:
        if rx.search(text):
            issues.append({"type": "secret", "message": f"{label}-shaped token in SKILL.md"})

    hits = sorted(set(m.group(0) for m in ABS_PATH_RE.finditer(body)))
    if hits:
        issues.append({"type": "absolute_path", "message": f"absolute user paths: {hits}"})

    if re.search(r"\.claude-plugin/(?:skills|hooks|agents)/", body):
        issues.append({"type": "plugin_layout", "message": "components belong at the plugin root, not inside .claude-plugin/"})

    if os.path.exists(os.path.join(skill_dir, "scripts")) and not any(
        os.access(os.path.join(skill_dir, "scripts", f), os.X_OK)
        for f in os.listdir(os.path.join(skill_dir, "scripts"))
        if os.path.isfile(os.path.join(skill_dir, "scripts", f))
    ):
        warnings.append({"type": "script_mode", "message": "no executable bits in scripts/; document explicit interpreter invocation"})

    return {
        "valid": not issues,
        "slug": slug,
        "body_lines": lines,
        "description_chars": len(desc),
        "issues": issues,
        "warnings": warnings,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: check_package.py <skill-dir>", file=sys.stderr)
        sys.exit(2)
    result = check(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
