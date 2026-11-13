# Changelog

All notable changes to this skill are documented here. This project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-11-13)

- Initial release
- Adapted from mblode/agent-skills `agent-skills-creator` (MIT), original by Matthew Blode
- Full lifecycle coverage: creation workflow (Steps 1-8), audit-before-rewrite scoring, and the keep, cut, merge, or retire decision
- IS / IS NOT contract scoping the skill to SKILL.md containers rather than domain content
- Validation step retargeted to this repository's `validate_skill.py`, replacing the upstream shell validator
- Added Gotchas from observed failures: stale installed copies, descriptions that pass validation and never route, sibling budget overrun, reference chains
- Added `references/authoring-tips.md` (descriptions, frontmatter, body structure)
- Added `references/skill-patterns.md` (simple/hub, workflow, rules-based, mixed)
- Added `evals/evals.json` with four behavioural scenarios
