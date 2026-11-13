# Sources

Upstream specifications and host documentation behind the portability rules in
this skill. Host paths and CLI flags change; re-check these before publishing a
package that depends on an exact path.

## Specification and format

- **Agent Skills specification** — https://agentskills.io/specification
  Canonical layout, `name` constraints (1–64 chars, `a-z0-9-`, no leading/trailing
  hyphen, no `--`, must match parent dir), `description` 1–1024 chars,
  `compatibility` ≤500 chars, `metadata` string map, experimental `allowed-tools`,
  progressive disclosure (~100-token metadata, <5000-token body, <500 lines).
- **Agent Skills reference implementation** — https://github.com/agentskills/agentskills
  `skills-ref validate ./my-skill`.

## Host paths and behavior

- **Skills Paths for Other AI Coding Assistants** (VoltAgent/awesome-agent-skills
  README) — https://github.com/VoltAgent/awesome-agent-skills#skills-paths-for-other-ai-coding-assistants
  Table of project/global roots for Claude Code, Codex, Cursor, Gemini CLI,
  Antigravity, GitHub Copilot, OpenCode, Windsurf; quality criteria including the
  "no absolute paths" rule.
- **Claude Code skills** — https://code.claude.com/docs/en/skills
- **Codex skills** — https://developers.openai.com/codex/skills
- **Cursor skills** — https://cursor.com/docs/context/skills
- **Gemini CLI skills** — https://geminicli.com/docs/cli/skills/
- **GitHub Copilot skills** — https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- **OpenCode skills** — https://opencode.ai/docs/skills
- **Windsurf Cascade skills** — https://docs.windsurf.com/windsurf/cascade/skills
- **Antigravity skills** — https://antigravity.google/docs/skills
- **OpenClaw — creating skills** — https://docs.openclaw.ai/tools/creating-skills
  Workspace `skills/` layout, `{baseDir}` placeholder, OpenClaw-only frontmatter
  keys (`user-invocable`, `command-dispatch`, `requires.bins`).
- **OpenClaw — skills config** — https://docs.openclaw.ai/tools/skills-config
  Root precedence, `skills.load.extraDirs`, symlink containment and
  `allowSymlinkTargets`.

## Packaging and distribution

- **vercel-labs/skills (npx skills)** — https://github.com/vercel-labs/skills
  `add` / `use` / `list` / `find` / `remove` / `update` / `init`, `-g`, `-a`,
  `-s`, `--copy`, symlink-vs-copy install methods, download and extract caps.
- **skills.sh directory** — https://skills.sh
- **anthropics/skills** — https://github.com/anthropics/skills
  Reference skill collection (docx, pdf, pptx, skill-creator, template); layout
  and frontmatter conventions used by first-party skills.
- **Claude Code plugins overview** — https://code.claude.com/docs/en/plugins/overview
  `.claude-plugin/plugin.json`, root-level `skills/`, `agents/`, `hooks/`,
  `.mcp.json`; `/plugin-name:skill-name` invocation.
- **Claude Code — create a marketplace** — https://code.claude.com/docs/en/plugins/create-marketplace
  `.claude-plugin/marketplace.json` with `name`, `owner`, `plugins[]`; relative
  `source` paths without `..`; `plugin@marketplace` install ids.

## Repo-local conventions

- **JPeetz/agent-skills** — https://github.com/JPeetz/agent-skills
  Category layout `skills/<category>/<skill>/`, 60-character description budget,
  `LICENSE` / `CHANGELOG.md` / `evals/evals.json` / `references/` package shape,
  `scripts/validate_skill.py` gate.
