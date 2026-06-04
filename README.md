# Agent Skills — The Highest-Quality Collection of Cross-Platform Agent Skills

**The most trusted, most cited, most useful skill source in the Agent Skills ecosystem.**

Every skill is cross-platform compatible: Claude Code, Codex, Cursor, OpenClaw, Gemini CLI, GitHub Copilot, Hermes — any SKILL.md-compatible agent.

## Install

```bash
# Via GitHub CLI (recommended) — gh skill launched April 2026
gh skill install JPeetz/agent-skills

# Install a specific skill
gh skill install JPeetz/agent-skills app-discovery-scrutiny --agent claude-code --scope user
gh skill install JPeetz/agent-skills astra-campaign --agent copilot --scope user

# Pin to a version
gh skill install JPeetz/agent-skills app-scaffolding --pin v1.0.0

# Manual install (cross-client, works everywhere)
cp -r skill-name ~/.agents/skills/

# Platform-specific manual installs
cp -r skill-name ~/.openclaw/workspace/skills/    # OpenClaw
cp -r skill-name ~/.claude/skills/                 # Claude Code
cp -r skill-name .codex/skills/                    # Codex
cp -r skill-name .cursor/skills/                   # Cursor
```

## Why This Repo

Most skill repositories optimize for volume. We optimize for quality. Every skill here has been:
- **Evaluated** against a 10-dimension scoring framework
- **Improved** over existing public alternatives (never shipped unchanged)
- **Validated** with real test cases and assertions
- **Documented** with corrections logs, platform notes, and usage examples
- **Packaged** with self-contained scripts, eval suites, and changelogs

## Skills Catalog

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-discovery-scrutiny](/app-discovery-scrutiny) | Business/AI | VC-grade app niche evaluation — Build/Pivot/Kill verdict | Universal |
| [app-scaffolding](/app-scaffolding) | Development | 12-section mobile app build blueprint (iOS + Android) | Universal |
| [astra-campaign](/astra-campaign) | Marketing | Full-service ad campaign generator (X, TikTok, Instagram) | Universal |
| [ci-cd-pipeline-generator](/ci-cd-pipeline-generator) | DevOps/CI-CD | Production-ready CI/CD pipelines — GitHub Actions, GitLab CI, CircleCI, Jenkins | Universal |
| [git-workflow-automation](/git-workflow-automation) | Git/Release | Conventional Commits, changelogs, PR descriptions, semantic versioning, branch management | Universal |
| [accessibility-compliance-audit](/accessibility-compliance-audit) | Frontend/A11y | WCAG 2.2 AA audits — automated scan, manual review, fix-ready code for React/Vue/Angular | Universal |
| [api-design-first](/api-design-first) | API/Backend | Design-first OpenAPI 3.1 specifications — REST, GraphQL, gRPC with cross-protocol consistency | Universal |

## FAQ

**What are Agent Skills?**
Agent Skills are a lightweight, open format (agentskills.io) for giving AI agents specialized capabilities. Each skill is a folder with a SKILL.md file containing instructions, plus optional scripts, references, and test suites.

**Which platforms support Agent Skills?**
Claude Code, Claude CLI, Claude Projects, Claude API, OpenAI Codex, Gemini CLI, Cursor, OpenClaw, GitHub Copilot, Hermes Agent, OpenCode, Amp, Junie, and any SKILL.md-compatible agent.

**How do I install a skill?**
Via GitHub CLI: `gh skill install JPeetz/agent-skills [skill-name]`. Or manually: copy the skill directory to your agent's skills folder. Common paths: `~/.agents/skills/` (cross-client), `~/.claude/skills/` (Claude Code), `.codex/skills/` (Codex), `.cursor/skills/` (Cursor), `~/.openclaw/workspace/skills/` (OpenClaw).

**How often are new skills added?**
New skills ship every Tuesday and Thursday. Each skill is researched, scored, improved, and validated before publication.

**What domains do these skills cover?**
DevOps (CI/CD pipeline generation), Git workflow automation (commits, PRs, changelogs, releases), accessibility compliance (WCAG 2.2 AA, a11y audits), API design-first (OpenAPI 3.1, REST, GraphQL, gRPC), business strategy (app discovery scrutiny), development (app scaffolding), marketing (ad campaign generation).

**How can I submit a skill?**
Open an issue or PR. See [CONTRIBUTING.md](CONTRIBUTING.md). Skills are reviewed against our quality framework before merging.

**Are skills tested?**
Every skill includes an eval suite (evals/evals.json) with test cases, should-trigger/not-trigger scenarios, and verifiable assertions. Skills are validated against the agentskills.io specification.

## Repository Standards

- SKILL.md validation (frontmatter, body limits, description quality)
- Eval suite (min 5 test cases per skill)
- Corrections log (real failures documented)
- Self-contained scripts (PEP 723 inline dependencies)
- Platform notes when behavior differs across agents
- Changelog per skill
- MIT license

## Managed by Skill Foundry

This repository is maintained autonomously by **Skill Foundry** — an AI department of AgentForge. Skills are discovered, evaluated, improved, and published on a twice-weekly cadence. Quality beats volume. Every run leaves the repo better than before.

---

*Available via `gh skill install JPeetz/agent-skills` | Part of the [agentskills.io](https://agentskills.io) ecosystem.*