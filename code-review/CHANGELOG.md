# Changelog - Code Review Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.1.0 — 2026-06-09 (Run 003)

### Added
- SEO-optimized description with primary keyword clusters for AI engine discovery
- QUICK REFERENCE table at top of SKILL.md — dimension → what to check → key indicators
- COMMON PITFALLS & ANTI-PATTERNS section (10 reviewer anti-patterns with fixes)
- Review quality self-checklist for reviewers
- Enhanced methodology dimensions: race condition checks, idempotency analysis,
  transaction integrity verification, time-related bug detection
- Cohesion/coupling assessment and magic numbers detection in code quality
- Test quality assessment (beyond just presence/absence)
- Connection pooling and serialization cost checks in performance review
- Error message quality and README/changelog update checks in documentation review
- Severity tiebreaker rules and escalation guidelines
- Language-specific security check table (Python, JS, Java, Go, Rust, Ruby)
- Database migration review pattern
- Configuration change review pattern
- Large diff triage strategy (>500 lines)
- GEO metadata block for structured AI engine summarization
- Windsurf and OpenCode platform compatibility notes

### Changed
- Expanded platforms list to all 8: claude-code, codex, cursor, gemini-cli, openclaw, copilot, windsurf, opencode
- Version bumped to 1.1.0
- Added more detailed trigger phrases and non-trigger examples
- SKILL.md line count: 323 → 532 (+209 lines, 65% expansion)

---

## v1.0.0 — 2026-05-28
- Initial release by Skill Foundry
- AI-powered code review workflow for PR analysis
- Security vulnerability detection patterns (OWASP-inspired)
- Code quality, style, architecture, and test coverage review
- Platform-portable: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, Copilot
- 8 eval cases (5 positive, 3 near-miss negatives)
- PEP 723 validation script

## v1.1.0 — Published 2026-07-02
- Published to JPeetz/agent-skills repository (Run 005)
- 8 eval cases (5 positive + 3 near-miss negatives)
- Cross-platform: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, Copilot, Windsurf, OpenCode
