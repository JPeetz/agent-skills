# Changelog

All notable changes to the `social-har-api-connectivity` skill.

## [1.0.0] - 2026-08-16
- Initial release.
- Combines HAR-capture API reverse-engineering with social-platform specifics:
  capture → filter → derive → verify → reuse for any social media platform's
  posting/data API.
- Includes `scripts/har_derive.py` — CLI tool that filters a captured HAR to a
  target host + action, prints minimal request shape (method, URL, headers, body),
  redacts tokens, and flags dynamic/expiring values.
- Per-platform guidance for auth, character limits, anti-automation policies, and
  embed verification (from existing `social-platform-api-integration` knowledge).
- Authorized-use guardrails, HAR-as-credential hygiene, and noise-control (live
  record filtering) baked in.
- Cross-agent compatible: any SKILL.md-compatible agent (Claude, Codex, Cursor,
  Gemini CLI, OpenClaw, Hermes Agent, and more).