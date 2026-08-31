#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Validate a skill's SKILL.md format against the Agent Skills spec."""
import yaml, sys, os, re

def validate_skill(skill_dir: str) -> dict:
    """Validate a skill directory against the spec."""
    issues = []
    warnings = []

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        return {"valid": False, "issues": [{"type": "missing_file", "message": "No SKILL.md found"}]}

    with open(skill_md) as f:
        content = f.read()

    # Check frontmatter
    if not content.startswith("---"):
        return {"valid": False, "issues": [{"type": "no_frontmatter", "message": "SKILL.md missing YAML frontmatter"}]}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"valid": False, "issues": [{"type": "malformed_frontmatter", "message": "Frontmatter not properly closed"}]}

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return {"valid": False, "issues": [{"type": "yaml_error", "message": f"Frontmatter parse error: {e}"}]}

    # Required fields
    if "name" not in fm:
        issues.append({"type": "missing_name", "message": "Missing required 'name' field"})
    elif fm["name"] != os.path.basename(skill_dir):
        issues.append({"type": "name_mismatch", "message": f"name '{fm['name']}' doesn't match folder '{os.path.basename(skill_dir)}'"})

    if "description" not in fm:
        issues.append({"type": "missing_description", "message": "Missing required 'description' field"})
    elif len(fm.get("description", "")) > 1024:
        warnings.append({"type": "description_long", "message": f"Description is {len(fm['description'])} chars (spec max: 1024)"})

    # Body length (recommendation, not spec requirement)
    body = parts[2].strip()
    body_lines = body.count("\n") + 1
    body_chars = len(body)
    if body_lines > 500:
        warnings.append({"type": "body_long", "message": f"Body is {body_lines} lines (recommendation: <500)"})

    # Script references
    if "scripts/" in body:
        scripts_dir = os.path.join(skill_dir, "scripts")
        if not os.path.exists(scripts_dir):
            issues.append({"type": "missing_scripts_dir", "message": "Body references scripts/ but no scripts/ directory exists"})

    # Description quality check
    desc = fm.get("description", "")
    if not desc.startswith("Use this skill when"):
        warnings.append({"type": "description_style", "message": "Description should start with 'Use this skill when' for better triggering"})

    return {
        "valid": len(issues) == 0,
        "name": fm.get("name", "unknown"),
        "body_lines": body_lines,
        "body_chars": body_chars,
        "description_chars": len(desc),
        "issues": issues,
        "warnings": warnings,
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = "."

    result = validate_skill(skill_dir)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)