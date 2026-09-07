# Changelog

## v1.0.0 (2026-09-07)

### Initial Release — Combined 5-Gate Review Framework

This is the initial packaged release of clean-pro-review-gates, adapted from Khaled Ghallab's clean-pro-skills repository. The five original standalone skills (clean-code-pro, clean-test-pro, clean-docs-pro, clean-security-pro, clean-infra-pro) have been:

- **Combined** into a single unified meta-skill with a common framework, severity guide, and cross-gate interaction model
- **Improved** with explicit cross-gate interaction tracking — findings that span multiple gates are now called out
- **Enhanced** with a standard 5-step workflow showing exactly how to scope, run, report, and self-check each gate
- **Adapted** with Hermes-compatible YAML frontmatter, tags, and related_skills references
- **Validated** with eval test cases covering all 5 gates

### Original Work

Based on https://github.com/Khaled-Ghallab/clean-pro-skills (MIT © Khaled Ghallab):
- clean-code-pro — production code review with 15 LLM failure modes
- clean-test-pro — test code review with 10 rules + LLM-app testing
- clean-docs-pro — documentation accuracy verification
- clean-security-pro — security review mapped to OWASP/CWE/LLM Top 10
- clean-infra-pro — CI/CD, container, and IaC hardening

### Key Improvements vs. Originals

- Cross-gate interaction table added (SKILL.md)
- Standardized 5-step review workflow with scoping, execution, and reporting phases
- Self-check checklists consolidated per gate for quick verification
- added evals/evals.json with 15 test cases covering all gates
- Hermes metadata with tags and related_skills references
- AI failure modes tables added to each gate reference file
- Severity guide unified across all gates (Critical/High/Medium/Low)