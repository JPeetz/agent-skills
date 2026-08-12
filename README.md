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

<details>
<summary>🔧 DevOps & Infrastructure (6 skills)</summary>

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [ci-cd-pipeline-generator](/ci-cd-pipeline-generator) | DevOps/CI-CD | Production-ready CI/CD pipelines — GitHub Actions, GitLab CI, CircleCI, Jenkins | Universal |
| [infrastructure-as-code-guardian](/infrastructure-as-code-guardian) | DevOps/Infrastructure | Cross-tool IaC security and management — Terraform, Pulumi, CloudFormation, Ansible, Bicep | Universal |
| [kubernetes-operations](/kubernetes-operations) | DevOps/K8s | Production-grade Kubernetes ops — manifest generation, Helm charts, GitOps, security hardening, failure-mode diagnosis | Universal |
| [observability-engineering](/observability-engineering) | DevOps/SRE | OpenTelemetry instrumentation, monitoring, distributed tracing, SLI/SLO management, incident response | Universal |
| [production-engineering-workflows](/production-engineering-workflows) | DevOps/SRE | Full SDLC automation: /spec → /plan → /build → /test → /review → /ship | Universal |
| [sre-runbooks](/sre-runbooks) | DevOps/SRE | Safe-by-default SRE runbooks — incident response, postmortems, on-call handovers, RCA | Universal |

</details>

### 🛡️ Security

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [agentic-security-scanner](/agentic-security-scanner) | Security/Agent | OWASP AST10 security scanning — malicious skill detection, prompt injection, data exfiltration, SARIF | Universal |
| [supply-chain-security-scanner](/supply-chain-security-scanner) | Security/DevSecOps | Software supply chain security — SBOM generation, dependency scanning, provenance verification, license compliance | Universal |

### 🔌 API & Backend

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [api-design-first](/api-design-first) | API/Backend | Design-first OpenAPI 3.1 specifications — REST, GraphQL, gRPC with cross-protocol consistency | Universal |
| [graphql-api-development](/graphql-api-development) | API/Backend | GraphQL API design and optimization — Apollo Federation, DataLoader, security, subscriptions | Universal |

### 🧪 QA & Testing

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [browser-automation](/browser-automation) | QA/Browser | Playwright browser automation — E2E testing, web scraping, monitoring, form submission, screenshots | Universal |
| [playwright-e2e-testing](/playwright-e2e-testing) | QA/Testing | Production-grade Playwright E2E testing — locator strategy, CI/CD, visual regression, component testing, a11y | Universal |

### 🎨 Frontend

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [accessibility-compliance-audit](/accessibility-compliance-audit) | Frontend/A11y | WCAG 2.2 AA audits — automated scan, manual review, fix-ready code for React/Vue/Angular | Universal |
| [design-to-code](/design-to-code) | Frontend/Design | AI-powered design-to-code: Figma, Sketch, screenshots → production React/Vue/Svelte/HTML | Universal |

### 📊 Data

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [data-analysis](/data-analysis) | Data Science | Data analysis, visualization, and reporting for CSV, JSON, Excel, SQL datasets | Universal |
| [dbt-data-transformation](/dbt-data-transformation) | Data/DBT | Production-grade dbt analytics engineering — model development, testing, dbt Mesh governance, semantic layer | Universal |

### 🗄️ Database

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [database-schema-designer](/database-schema-designer) | Database | Production-grade schema design — normalization, indexing, safe migrations, multi-tenant | Universal |

### 📝 Documentation & Content

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [document-processing](/document-processing) | Content/Docs | PDF/DOCX/XLSX/PPTX automation — generation, manipulation, conversion, OCR, mail merge | Universal |
| [read-x-articles](/read-x-articles) | Content/Web | Read X (Twitter) long-form Articles end-to-end from a shared link via the canonical /i/article/ID URL + render-capable extraction | Universal |
| [technical-documentation](/technical-documentation) | Documentation | AI-powered technical docs: READMEs, ADRs, API docs, runbooks, knowledge bases | Universal |

### 💼 Business & Strategy

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-discovery-scrutiny](/app-discovery-scrutiny) | Business/AI | VC-grade app niche evaluation — Build/Pivot/Kill verdict | Universal |

### ⚙️ Development

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-scaffolding](/app-scaffolding) | Development | 12-section mobile app build blueprint (iOS + Android) | Universal |

### 📣 Marketing

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [astra-campaign](/astra-campaign) | Marketing | Full-service ad campaign generator (X, TikTok, Instagram) | Universal |

### ⚖️ Compliance & Legal

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [privacy-compliance](/privacy-compliance) | Compliance/Legal | Global privacy compliance: GDPR, CCPA/CPRA, HIPAA, EU AI Act, LGPD, cross-border transfers | Universal |

### 🌿 Git & Release

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [git-workflow-automation](/git-workflow-automation) | Git/Release | Conventional Commits, changelogs, PR descriptions, semantic versioning, branch management | Universal |

### ✅ Code Quality

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [code-review](/code-review) | Code Quality | AI-powered code review — security, quality, style, architecture, test coverage, performance | Universal |


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
Business strategy (app discovery, market analysis), development (app scaffolding, API design-first, GraphQL API development), Frontend/Design (design-to-code, accessibility compliance), DevOps/SRE (CI/CD pipeline generation, infrastructure-as-code guardian, production engineering workflows, SRE runbooks, Kubernetes operations, observability engineering), Git workflow automation (commits, PRs, changelogs, releases), code quality (AI-powered code review covering security, architecture, performance), data (data analysis and visualization, dbt analytics engineering, database schema design), compliance and privacy (GDPR, CCPA, HIPAA, EU AI Act, cross-border transfers), QA and testing (Playwright E2E testing, browser automation), security (supply chain scanner, agentic security scanner, SBOM, dependency scanning, provenance verification), content and documents (PDF/DOCX/XLSX/PPTX processing, technical documentation), marketing (ad campaign generation).

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

*Available via `gh skill install JPeetz/agent-skills` | Part of the [AgentForge Ecosystem](https://github.com/JPeetz/agentforge) | [agentskills.io](https://agentskills.io)*