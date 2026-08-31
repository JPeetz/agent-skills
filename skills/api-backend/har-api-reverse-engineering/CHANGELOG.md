# Changelog

All notable changes to the `har-api-reverse-engineering` skill.

## [1.0.0] - 2026-08-16
- Initial release.
- Core capability: capture a website's undocumented API as a HAR, derive the
  request shape (method, URL, headers, body), reconstruct a clean standalone
  client, verify it outside the browser, and reuse the verified client.
- Guardrails baked in: authorized-use only (does NOT bypass auth/bot detection),
  third-party ToS check, HAR-as-credential hygiene (chmod 600, never commit),
  auth-by-label at runtime, and fragility handling for expiring signature/nonce
  and CSRF tokens.
- Cross-agent compatible: any SKILL.md-compatible agent (Claude, Codex, Cursor,
  Gemini CLI, OpenClaw, Hermes Agent, and more).