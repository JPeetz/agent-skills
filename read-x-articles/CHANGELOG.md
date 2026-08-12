# Changelog

All notable changes to the `read-x-articles` skill.

## [1.0.0] - 2026-08-12
- Initial release.
- Core capability: read X long-form Articles end-to-end via the canonical
  `/i/article/<ID>` URL with a **render-capable web-extractor/browser tool**,
  instead of giving up on the login/JS wall that hits profile and `/status/`.
- Corrected nuance (same day): a bare HTTP fetch (urllib/curl) of the article
  can still return a login shell; the canonical URL is necessary but a plain
  request is NOT sufficient — you need a JS-executing extractor. Documented
  in SKILL.md + references/url-forms.md.
- Cross-agent compatible: any SKILL.md-compatible agent (Claude, Codex,
  Cursor, Gemini CLI, OpenClaw, Hermes Agent, and more).