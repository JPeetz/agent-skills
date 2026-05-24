# Contributing to Agent Skills

We accept skill submissions, improvements, and bug reports. Every contribution is reviewed against our quality framework before merging.

## Submission Process

1. **Fork** this repository
2. **Create** your skill as a directory with `SKILL.md` + optional `scripts/`, `references/`, `evals/`
3. **Validate** with `python3 scripts/validate_skill.py your-skill/`
4. **Open a Pull Request**

## Skill Requirements

Every skill must:
- Follow the [Agent Skills specification](https://agentskills.io/specification)
- Include YAML frontmatter with `name` and `description`
- Keep body under 500 lines / 5,000 tokens
- Be cross-platform compatible (or document platform limitations)
- Not duplicate an existing skill without material improvement

## Quality Standards

Strong skills include:
- Clear, imperative description ("Use this skill when...")
- Actionable step-by-step instructions
- Real examples with expected inputs/outputs
- Self-contained scripts with inline dependencies
- Eval suite (evals/evals.json with 5+ test cases)
- Corrections log (references/corrections.md)

## Review Process

1. Automated validation against the skills spec
2. Manual review by Skill Foundry (or maintainer) against the 10-dimension scoring framework
3. Feedback and iteration if improvements needed
4. Merge and catalog update

## Issues

- **Bug reports:** Include the skill name, expected behavior, and what happened
- **Feature requests:** Describe the workflow the skill would enable
- **Skill requests:** What task do you want a skill for? Include examples of how you'd use it