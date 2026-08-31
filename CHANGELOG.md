# Changelog — Agent Skills Repository

All notable changes to the agent-skills repository. Maintained by Skill Foundry (AgentForge). Published twice weekly.

---

## v1.5.0 — 2026-08-31

### 🏗️ Repository Structure

- **Category-organized layout:** All 37 skills moved from repo root into `skills/<category>/<skill>/`.
- Categories: devops-infrastructure (6), security (2), api-backend (5), qa-testing (2), frontend (2), data (3), documentation-content (3), skill-development (2), business-strategy (2), development (5), marketing (2), compliance-legal (1), git-release (1), code-quality (1).
- README catalog links, install instructions, and CONTRIBUTING submission process updated for the new paths.
- Structure matches the agentskills.io / `gh skill` discovery conventions (`skills/*/SKILL.md`, `skills/{scope}/*/SKILL.md`) — install/publish resolution unchanged.
- Catalog now includes 5 previously uncatalogued skills: anti-over-engineering, finding-unknowns, hermes-bot-team-design, betterlife-image-generation, skill-miner.
- `gh skill publish --dry-run` verifies all nested skills resolve (0 errors after fixing 3 colon-in-YAML frontmatter descriptions on dbt-data-transformation, kubernetes-operations, observability-engineering).

---

## v1.4.2 — 2026-08-24

### 🚀 Skills Added (SKILLS pipeline run)

- **skill-lifecycle-foundry** (v1.0.0) — The meta-skill for the full agent-skill lifecycle: mine session/archive history for repeated workflows, author new `SKILL.md` files, personalize existing skills to local tools and phrasing, and generalize private skills for public release (secret/path redaction). Ships `scripts/scan_sessions.py` (stdlib-only), a release checklist, and a progressive-disclosure reference structure. 144-line SKILL.md, 8 eval cases.

- **model-routing-cost-optimizer** (v1.0.0) — Cost-aware model tiering: ROUTINE/MODERATE/COMPLEX classifier, vision guard against routing image work to text-only models, and anti-pattern coverage. Ships `scripts/classify_task.py` (stdlib-only) for deterministic tier recommendations and a `references/model-pricing.md` snapshot. 126-line SKILL.md, 8 eval cases.

- **linear-project-management** (v1.0.0) — Drive Linear issues, projects, and teams from an agent via the official MCP server and Linear GraphQL API: discovery-before-create, type/domain/scope label taxonomy, workspace-specific status handling, and the `description` vs `content` rule. `references/linear-graphql.md` with copy-paste operations. 111-line SKILL.md, 8 eval cases.

### 📚 Documentation

- README catalog: +3 skills under Documentation & Content, Business & Strategy, and Development
- Added `.gitignore` (Python + Node build artifacts)
- Per-skill LICENSE (MIT), CHANGELOG, evals, and references for each new package

---

## v1.4.1 — 2026-07-02

### 📚 Documentation

- **Category-collapsible bundling:** Skills Catalog reorganized into emoji-categorized sections
- DevOps & Infrastructure (6 skills) wrapped in `<details>`/`<summary>` — only category with >2 skills
- All other categories (≤2 skills) remain flat with `###` headers
- Permanent rule: re-evaluate category counts on every run; >2 → collapsible

---

## v1.4.0 — 2026-07-02

### 🚀 Skills Added (Run 005)

- **code-review** (v1.1.0) — AI-powered code review and PR analysis. Systematic reviews covering security vulnerabilities (OWASP patterns), code quality, style compliance, architectural integrity, test coverage, and performance considerations. Works with PR diffs, commit ranges, file changes, or raw code snippets. 475-line SKILL.md, 8 eval cases (5 positive + 3 near-miss negatives).

- **data-analysis** (v1.0.0) — Comprehensive data analysis for loading, cleaning, exploring, visualizing, and reporting on structured datasets. Supports CSV, JSON, Excel, and SQL data sources. Statistical summaries, correlation matrices, time series analysis, regression models, hypothesis tests, and publication-quality visualizations via matplotlib, seaborn, and plotly. 301-line SKILL.md, 5 eval cases.

- **database-schema-designer** (v1.0.0) — Production-grade database schema design covering normalization (1NF to BCNF), indexing strategy with anti-pattern detection, safe migration design with rollback patterns (8 safe-migration rules), query optimization via EXPLAIN ANALYZE, and multi-tenant architecture patterns across PostgreSQL, MySQL, SQLite, MongoDB, and Vitess. 250-line SKILL.md, 5 eval cases with near-miss negatives.

- **agentic-security-scanner** (v1.0.0) — OWASP Agentic Skills Top 10 (AST10) security framework implementation. Static analysis scanner detecting malicious skills, prompt injection sinks, data exfiltration paths, supply chain risks, and cross-platform metadata loss. CI/CD-ready with SARIF output for GitHub Code Scanning integration. 186-line SKILL.md, 7 eval cases.

- **sre-runbooks** (v1.0.0) — Safe-by-default DevOps/SRE runbook automation. Incident response workflow (Triage → Investigation → Mitigation → Resolution), Google SRE Four Golden Signals diagnostics, Five Whys RCA, blameless postmortem templates, on-call handover generation, and Never-Automate safety lists. Dry-run modes and human approval gates built in. 239-line SKILL.md, 5 eval cases with near-miss negatives.

### 📚 Documentation

- README catalog: 25 skills (+5) — fully alphabetized, 5 new domains added
- FAQ updated: code quality, data science, database, agent security, SRE domains
- DEVLOG entry for 2026-07-02 (Run 005)
- Per-skill CHANGELOG entries for publication date

### 🔧 Improvements

- All 5 skills fully packaged: SKILL.md, CHANGELOG.md, LICENSE (MIT), evals/, scripts/, references/
- Cross-platform verified: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, GitHub Copilot, Windsurf, OpenCode
- All validation scripts pass: code-review ✅, data-analysis ✅, database-schema-designer ✅, agentic-security-scanner ✅, sre-runbooks ✅

### 📋 Remaining Local Skills (Queued)

- llm-security-redteaming (v1.0.0, 224 lines, 7 eval cases) — target Run 006
- api-contract-testing (v1.0.0, 182 lines, 5 eval cases) — target Run 006
- agent-skill-creator (v1.0.0, 636 lines, has own .git) — review and decide
- ai-legal-content (skeleton: 30 lines) — requires full build
- apple-app-store-compliance (skeleton: 30 lines) — requires full build
- gdpr-compliance-expert (skeleton: 27 lines) — requires full build (partially subsumed by privacy-compliance)

### 🔮 Next Targets

- llm-security-redteaming + api-contract-testing publication (Run 006)
- Privacy-compliance near-miss negative eval improvement
- Full build of ai-legal-content or apple-app-store-compliance
- Incident response & SRE (partially covered by sre-runbooks, observability-engineering)
- Helm chart scaffolding
- Python logging & observability

---

## v1.3.0 — 2026-06-25

### 🚀 Skills Added (Published from Local)

- **design-to-code** (v1.0.0) — AI-powered design-to-code conversion covering Figma, Sketch, Adobe XD, and screenshot ingestion. Design token extraction, component hierarchy mapping, responsive breakpoint strategy, accessibility-first implementation (WCAG 2.1 AA), framework-agnostic patterns (React, Vue, Svelte, HTML/CSS), CSS architecture selection (Tailwind, CSS Modules, styled-components), visual regression testing. 857-line SKILL.md, 10 eval cases (6 positive + 4 near-miss negatives).

- **graphql-api-development** (v1.0.0) — Complete GraphQL API design, implementation, and optimization. Schema-first design, resolver architecture with DataLoader N+1 prevention, mutation patterns with idempotency, real-time subscriptions, Apollo Federation for distributed graphs, security hardening (depth/rate limiting, authorization), production performance (persisted queries, CDN caching). 1,201-line SKILL.md, 9 eval cases (6 positive + 3 near-miss negatives).

- **privacy-compliance** (v1.0.0) — Comprehensive global privacy compliance covering GDPR, CCPA/CPRA, HIPAA Privacy Rule, EU AI Act, LGPD (Brazil), cross-border data transfer mechanisms (SCCs, BCRs, EU-US DPF), PII identification and classification, data minimization, consent management, privacy-by-design patterns, DPIA workflows, DSAR handling, breach notification procedures. Procedural knowledge — NOT legal advice. 1,240-line SKILL.md, 7 eval cases.

- **production-engineering-workflows** (v1.0.0) — End-to-end production engineering encoding the complete SDLC into repeatable agent commands. Slash-command entry points: /spec, /plan, /build, /test, /review, /webperf, /code-simplify, /ship. Covers spec-driven ideation, test-driven implementation, automated testing, code review, performance auditing, simplification, deployment automation, feature flags, trunk-based development, incremental rollouts. 897-line SKILL.md, 10 eval cases.

- **technical-documentation** (v1.0.0) — AI-powered technical documentation creation, maintenance, and auditing. README quality templates, ADR (Architecture Decision Records), API docs (OpenAPI generation), runbooks, onboarding guides, changelogs (Keep a Changelog format), knowledge bases, AI agent context files (AGENTS.md/CLAUDE.md), documentation-driven development patterns. 830-line SKILL.md, 8 eval cases (5 positive + 3 near-miss negatives).

### 📚 Documentation

- README catalog: 17 skills (+5) — full table with descriptions, domains, platform compatibility
- FAQ domains expanded: Frontend/design-to-code, API/GraphQL, Compliance/Privacy, SRE/Production Engineering, Documentation
- DEVLOG entry for 2026-06-25 (Run 004)
- Per-skill CHANGELOG entries for publication date

### 🔧 Improvements

- All 5 skills fully packaged: SKILL.md, CHANGELOG.md, LICENSE (MIT), evals/, scripts/validate_skill.py, references/
- Cross-platform verified: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, GitHub Copilot, Windsurf, OpenCode
- All validation scripts pass: design-to-code ✅, graphql-api-development ✅, privacy-compliance ✅, production-engineering-workflows ✅, technical-documentation ✅ (1 minor: body length advisory)

### 📋 Remaining Local Skills (Queued)

- code-review (v1.0.0, 532 lines, 8 eval cases) — target Run 005
- data-analysis (v1.0.0, 332 lines, 8 eval cases) — target Run 005
- agent-skill-creator — review and decide on publication
- ai-legal-content (skeleton: 30 lines) — requires full build
- apple-app-store-compliance (skeleton: 30 lines) — requires full build
- gdpr-compliance-expert (skeleton: 27 lines) — requires full build (partially subsumed by privacy-compliance)

### 🔮 Next Targets

- code-review + data-analysis publication (Run 005)
- Database schema design / migrations skill
- Kubernetes operations (KubeShark)
- Incident response & SRE runbooks
- Terraform infrastructure provisioning
- dbt data transformation

---

## v1.2.0 — 2026-06-16

### 🚀 Skills Added

- **playwright-e2e-testing** — Production-grade Playwright E2E testing skill. Complete test architecture with Page Object Model patterns, locator strategy priority hierarchy, authentication and session management, visual regression testing, component testing (React/Vue/Svelte), mobile/device emulation, CI/CD configuration (GitHub Actions, GitLab CI, CircleCI with sharding), debugging and flaky test detection, accessibility testing (axe-core), performance testing (Lighthouse/Web Vitals), i18n testing, security testing (XSS/CSRF/CSP), WebSocket/real-time testing, Electron and browser extension testing. 8 eval cases + 3 near-miss negatives. Materially improved from currents-dev source.

### 📦 Existing Skills Published (Previously Local-Only)

- **browser-automation** (v1.1.0) — Playwright browser automation for testing, scraping, monitoring, form submission, screenshots, multi-page flows. Page Object Model, CI/CD integration. 8 eval cases.
- **document-processing** (v1.1.0) — PDF/DOCX/XLSX/PPTX automation — generation, manipulation, conversion, OCR, mail merge. 8 eval cases.
- **supply-chain-security-scanner** (v1.0.0) — SBOM generation (SPDX/CycloneDX), multi-ecosystem dependency scanning, provenance verification (cosign/slsa-verifier), license compliance. OWASP AST10 aligned. 10 eval cases.
- **infrastructure-as-code-guardian** (v1.0.0) — Universal IaC security across Terraform, Pulumi, CloudFormation, Ansible, Bicep. 40+ item security checklist, drift detection, state management, migration patterns. 7 eval cases.

### 📚 Documentation

- README catalog: 12 skills (+5) — full table with descriptions and domain classification
- FAQ domain coverage expanded: QA/testing, security/DevSecOps, infrastructure, content/documents
- DEVLOG entry for 2026-06-16 (Run 003)
- GitHub Topics at 20-topic limit — topic rotation roadmap noted

### 🔧 Improvements

- playwright-e2e-testing materially improved over source (+7 testing domains, eval suite, executable scripts)
- All 5 skills fully packaged: SKILL.md, CHANGELOG.md, LICENSE, evals/, scripts/, references/
- Cross-platform: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, Copilot, Windsurf, OpenCode

### 🔮 Next Targets

- Database management (PostgreSQL, MySQL, migrations) — planetscale/database-skills
- Kubernetes operations — KubeShark (#1 K8s skill by GitHub stars)
- Incident response & SRE runbooks
- Data engineering (ETL, dbt) — vaquarkhan/data-engineering-agent-skills
- Package remaining local skills (code-review, data-analysis)

---

## v1.1.0 — 2026-06-04

### 🚀 Skills Added

- **ci-cd-pipeline-generator** — Production-ready CI/CD configuration for GitHub Actions, GitLab CI, CircleCI, Jenkins. Multi-stage parallel pipelines with security validation, canary deployments, rollback strategies, Docker caching, secrets management, and environment promotion. Includes Mermaid pipeline diagrams and provider-specific templates (Node.js+K8s, Python+ECS, Go+Kube, Static Site).
- **git-workflow-automation** — Full Git workflow lifecycle: Conventional Commits, branch naming, PR template generation, changelog generation (Keep a Changelog format), semantic versioning engine, release flow automation, merge conflict resolution. Includes commitlint config, semantic-release config, and helper scripts.
- **accessibility-compliance-audit** — WCAG 2.2 AA compliance auditor. 3-phase process (automated scan, manual review, fix generation). Framework-specific patterns for React, Vue, Angular. 4-tier severity classification. Color contrast analysis with exact ratio computation. Screen reader UX checklist, keyboard support checklist, reduced motion support.
- **api-design-first** — Design-first API development. Complete OpenAPI 3.1 specification generation. REST resource modeling, pagination (cursor + offset), RFC 7807 error handling, API versioning with deprecation headers, authentication patterns (JWT, API Key, OAuth2), rate limiting, idempotency. Cross-protocol design for REST + GraphQL + gRPC.

### 📚 Documentation

- README catalog updated with 4 new skills (7 total)
- FAQ expanded with domain coverage question
- DEVLOG entry for 2026-06-04 run
- Each skill includes: CHANGELOG.md, LICENSE (MIT), evals/evals.json (5-6 test cases + near-miss negatives), scripts/ (shell + Python with PEP 723), references/ (domain-specific guides)

### 🔧 Improvements

- All 4 skills feature comprehensive edge case handling (monorepo, multi-language, database migrations, empty commits, detached HEAD, etc.)
- Security mandates embedded: SHA-pinned actions, OIDC auth, token permission limits, secret management, commit signing
- Cross-platform compatibility verified: Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, Copilot, Windsurf
- eval suites include 5-6 positive triggers and 2 near-miss negatives per skill

---

## v1.0.0 — 2026-05-24

### 🚀 Initial Release

**Skills shipped:**
- **app-discovery-scrutiny** — VC-grade mobile app niche evaluation. 5-section Zero-Day Dominance Report. 10-dimension scoring with kill-floor elimination. Build/Pivot/Kill verdict.
- **app-scaffolding** — 12-section mobile app build blueprint. iOS (SwiftUI) + Android (Jetpack Compose). SEO/GEO, Hooked Model, financial architecture, virality engine, 30-day sprint.
- **astra-campaign** — Full-service ad campaign generator. X, TikTok, Instagram. 7-phase: Diagnose → Research → Strategize → Create → Optimize → QC → Export. Engine-aware production prompts.

**Repo setup:**
- README with install instructions (gh skill + manual), skill catalog, FAQ, platform compatibility
- CONTRIBUTING.md with submission guidelines and quality standards
- GitHub Topics: agent-skills, skill-pack, claude-code, opencode, cursor, openclaw, codex, gemini, copilot, hermes-agent, agentskills, ai-agent-skills
- Published via `gh skill publish` — installable with `gh skill install JPeetz/agent-skills`
- Immutable release v1.0.0

**Quality framework established:**
- 10-dimension scoring for all future skills
- Eval suites with near-miss negative test cases
- Corrections logs documenting real failures
- Self-contained scripts with inline dependencies (PEP 723)
- validate_skill.py for spec compliance checking