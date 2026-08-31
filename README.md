# Agent Skills — The Highest-Quality Collection of Cross-Platform Agent Skills

**The most trusted, most cited, most useful skill source in the Agent Skills ecosystem.**

Every skill is cross-platform compatible: Claude Code, Codex, Cursor, OpenClaw, Gemini CLI, GitHub Copilot, Hermes — any SKILL.md-compatible agent.

## Structure

Skills are organized by category under `skills/`:

```
skills/
├── devops-infrastructure/   CI/CD, IaC, Kubernetes, observability, SRE
├── security/                Agent & supply-chain security
├── api-backend/             API design, GraphQL, HAR reverse-engineering
├── qa-testing/              Playwright E2E, browser automation
├── frontend/                a11y audits, design-to-code
├── data/                    Analysis, dbt, database schema design
├── documentation-content/   Docs, document processing, X articles
├── skill-development/       Skill lifecycle, mining, authoring
├── business-strategy/       App discovery, Linear PM
├── development/             Scaffolding, cost routing, engineering habits
├── marketing/               Ad campaigns, image generation
├── compliance-legal/        Privacy & GDPR
├── git-release/             Git workflow & release automation
└── code-quality/            Code review
```

## Install

```bash
# Via GitHub CLI (recommended) — gh skill launched April 2026
gh skill install JPeetz/agent-skills

# Install a specific skill (discovered under skills/<category>/<skill>)
gh skill install JPeetz/agent-skills app-discovery-scrutiny --agent claude-code --scope user
gh skill install JPeetz/agent-skills astra-campaign --agent copilot --scope user

# Pin to a version
gh skill install JPeetz/agent-skills app-scaffolding --pin v1.0.0

# Manual install (cross-client, works everywhere) — pick the category path
cp -r skills/<category>/skill-name ~/.agents/skills/

# Examples
cp -r skills/development/app-scaffolding ~/.agents/skills/
cp -r skills/devops-infrastructure/ci-cd-pipeline-generator ~/.agents/skills/

# Platform-specific manual installs
cp -r skills/<category>/skill-name ~/.openclaw/workspace/skills/    # OpenClaw
cp -r skills/<category>/skill-name ~/.claude/skills/                 # Claude Code
cp -r skills/<category>/skill-name .codex/skills/                    # Codex
cp -r skills/<category>/skill-name .cursor/skills/                   # Cursor
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
| [ci-cd-pipeline-generator](/skills/devops-infrastructure/ci-cd-pipeline-generator) | DevOps/CI-CD | Production-ready CI/CD pipelines — GitHub Actions, GitLab CI, CircleCI, Jenkins | Universal |
| [infrastructure-as-code-guardian](/skills/devops-infrastructure/infrastructure-as-code-guardian) | DevOps/Infrastructure | Cross-tool IaC security and management — Terraform, Pulumi, CloudFormation, Ansible, Bicep | Universal |
| [kubernetes-operations](/skills/devops-infrastructure/kubernetes-operations) | DevOps/K8s | Production-grade Kubernetes ops — manifest generation, Helm charts, GitOps, security hardening, failure-mode diagnosis | Universal |
| [observability-engineering](/skills/devops-infrastructure/observability-engineering) | DevOps/SRE | OpenTelemetry instrumentation, monitoring, distributed tracing, SLI/SLO management, incident response | Universal |
| [production-engineering-workflows](/skills/devops-infrastructure/production-engineering-workflows) | DevOps/SRE | Full SDLC automation: /spec → /plan → /build → /test → /review → /ship | Universal |
| [sre-runbooks](/skills/devops-infrastructure/sre-runbooks) | DevOps/SRE | Safe-by-default SRE runbooks — incident response, postmortems, on-call handovers, RCA | Universal |

</details>

### 🛡️ Security

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [agentic-security-scanner](/skills/security/agentic-security-scanner) | Security/Agent | OWASP AST10 security scanning — malicious skill detection, prompt injection, data exfiltration, SARIF | Universal |
| [supply-chain-security-scanner](/skills/security/supply-chain-security-scanner) | Security/DevSecOps | Software supply chain security — SBOM generation, dependency scanning, provenance verification, license compliance | Universal |

### 🔌 API & Backend

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [api-design-first](/skills/api-backend/api-design-first) | API/Backend | Design-first OpenAPI 3.1 specifications — REST, GraphQL, gRPC with cross-protocol consistency | Universal |
| [graphql-api-development](/skills/api-backend/graphql-api-development) | API/Backend | GraphQL API design and optimization — Apollo Federation, DataLoader, security, subscriptions | Universal |
| [har-api-reverse-engineering](/skills/api-backend/har-api-reverse-engineering) | API/Backend | Reverse-engineer a site's hidden/undocumented API from a captured HAR — derive, replay, verify, reuse (authorized use only) | Universal |
| [social-har-api-connectivity](/skills/api-backend/social-har-api-connectivity) | API/Social | Connect a social platform's API from a captured HAR — filter, derive, verify, reuse (authorized only) | Universal |
| [image-to-image-character-generation](/skills/api-backend/image-to-image-character-generation) | API/Image | Generate consistent character images from Supabase/GDrive refs via kie.ai image-to-image — face anchors, dynamic prompt, anti-repeat | Universal |

### 🧪 QA & Testing

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [browser-automation](/skills/qa-testing/browser-automation) | QA/Browser | Playwright browser automation — E2E testing, web scraping, monitoring, form submission, screenshots | Universal |
| [playwright-e2e-testing](/skills/qa-testing/playwright-e2e-testing) | QA/Testing | Production-grade Playwright E2E testing — locator strategy, CI/CD, visual regression, component testing, a11y | Universal |

### 🎨 Frontend

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [accessibility-compliance-audit](/skills/frontend/accessibility-compliance-audit) | Frontend/A11y | WCAG 2.2 AA audits — automated scan, manual review, fix-ready code for React/Vue/Angular | Universal |
| [design-to-code](/skills/frontend/design-to-code) | Frontend/Design | AI-powered design-to-code: Figma, Sketch, screenshots → production React/Vue/Svelte/HTML | Universal |

### 📊 Data

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [data-analysis](/skills/data/data-analysis) | Data Science | Data analysis, visualization, and reporting for CSV, JSON, Excel, SQL datasets | Universal |
| [dbt-data-transformation](/skills/data/dbt-data-transformation) | Data/DBT | Production-grade dbt analytics engineering — model development, testing, dbt Mesh governance, semantic layer | Universal |
| [database-schema-designer](/skills/data/database-schema-designer) | Database | Production-ready schema design — normalization, indexing, safe migrations, multi-tenant | Universal |

### 📝 Documentation & Content

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [document-processing](/skills/documentation-content/document-processing) | Content/Docs | PDF/DOCX/XLSX/PPTX automation — generation, manipulation, conversion, OCR, mail merge | Universal |
| [read-x-articles](/skills/documentation-content/read-x-articles) | Content/Web | Read X (Twitter) long-form Articles end-to-end from a shared link via the canonical /i/article/ID URL + render-capable extraction | Universal |
| [technical-documentation](/skills/documentation-content/technical-documentation) | Documentation | AI-powered technical docs: READMEs, ADRs, API docs, runbooks, knowledge bases | Universal |

### 🛠️ Skill Development

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [skill-lifecycle-foundry](/skills/skill-development/skill-lifecycle-foundry) | Skill Development | Mine, author, personalize, and generalize agent skills across their full lifecycle — session mining to release checklist | Universal |
| [skill-miner](/skills/skill-development/skill-miner) | Skill Development | Mine agent session/archive history for repeated skill-worthy workflows | Universal |

### 💼 Business & Strategy

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-discovery-scrutiny](/skills/business-strategy/app-discovery-scrutiny) | Business/AI | VC-grade app niche evaluation — Build/Pivot/Kill verdict | Universal |
| [linear-project-management](/skills/business-strategy/linear-project-management) | Business/PM | Drive Linear issues, projects, and teams from an agent via MCP + GraphQL — discovery-before-create, label taxonomy | Universal |

### ⚙️ Development

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-scaffolding](/skills/development/app-scaffolding) | Development | 12-section mobile app build blueprint (iOS + Android) | Universal |
| [model-routing-cost-optimizer](/skills/development/model-routing-cost-optimizer) | Development/Cost | Route agent tasks to the cheapest adequate model tier — ROUTINE/MODERATE/COMPLEX classifier + vision guard | Universal |
| [anti-over-engineering](/skills/development/anti-over-engineering) | Development | Keep AI agents from over-engineering code beyond the user's request | Universal |
| [finding-unknowns](/skills/development/finding-unknowns) | Development | Systematic discovery of unknowns when entering unfamiliar code or domain territory | Universal |
| [hermes-bot-team-design](/skills/development/hermes-bot-team-design) | Development | Design a team of specialist Hermes bots from a project spec — roles, SOUL.md, MCP wiring, group chat | Universal |

### 📣 Marketing

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [astra-campaign](/skills/marketing/astra-campaign) | Marketing | Full-service ad campaign generator (X, TikTok, Instagram) | Universal |
| [betterlife-image-generation](/skills/marketing/betterlife-image-generation) | Marketing/Image | BetterLife daily social images via kie.ai grok-imagine — Mira character anchors, anti-repetition | Universal |

### ⚖️ Compliance & Legal

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [privacy-compliance](/skills/compliance-legal/privacy-compliance) | Compliance/Legal | Global privacy compliance: GDPR, CCPA/CPRA, HIPAA, EU AI Act, LGPD, cross-border transfers | Universal |

### 🌿 Git & Release

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [git-workflow-automation](/skills/git-release/git-workflow-automation) | Git/Release | Conventional Commits, changelogs, PR descriptions, semantic versioning, branch management | Universal |

### ✅ Code Quality

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [code-review](/skills/code-quality/code-review) | Code Quality | AI-powered code review — security, quality, style, architecture, test coverage, performance | Universal |

## FAQ

**What are Agent Skills?**
Agent Skills are a lightweight, open format (agentskills.io) for giving AI agents specialized capabilities. Each skill is a folder with a SKILL.md file containing instructions, plus optional scripts, references, and test suites.

**Which platforms support Agent Skills?**
Claude Code, Claude CLI, Claude Projects, Claude API, OpenAI Codex, Gemini CLI, Cursor, OpenClaw, GitHub Copilot, Hermes Agent, OpenCode, Amp, Junie, and any SKILL.md-compatible agent.

**Why are skills nested under categories?**
`gh skill` and the agentskills.io specification discover skills at `skills/*/SKILL.md` and `skills/{scope}/*/SKILL.md` — category folders map to the `{scope}` position, so `gh skill install`, `gh skill publish`, and the agentskills.io CLI all resolve nested skills natively. Categories keep a 40-skill library browsable.

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