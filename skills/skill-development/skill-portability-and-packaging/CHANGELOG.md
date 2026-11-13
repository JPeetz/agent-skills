# Changelog

## [1.0.0] - 2026-11-13

- Initial release of the Skill Portability and Packaging skill.
- Covers the spec's hard rules (name/folder equality, 64-char name, 1024-char
  description) and the canonical directory layout.
- Documents the per-host install matrix for Claude Code, Codex, Cursor, Gemini
  CLI, Antigravity, GitHub Copilot, OpenCode, Windsurf, OpenClaw (including its
  root precedence and symlink containment rule), and Hermes.
- Adds description budgeting guidance: routing triggers first, tail trimming per
  host truncation limits.
- Adds packaging routes for loose skills, Claude Code plugins
  (`.claude-plugin/plugin.json`), and marketplaces (`.claude-plugin/marketplace.json`),
  plus `npx skills add` installation.
- Adds portability hazard sweep (absolute paths, host tool names, interpreters,
  frontmatter dialects, file modes, case sensitivity, precedence collisions,
  size caps).
- Adds the install verification loop that proves the loaded copy is the edited copy,
  and security packaging rules for published skills.
- Ships `scripts/check_package.py`, a stdlib-only pre-flight check (name/folder,
  charset, description budget, version format, secret and absolute-path sweep,
  plugin-layout mistake detection).
- Includes `evals/evals.json` with three grading scenarios and
  `references/sources.md` with the upstream specifications and host docs.
