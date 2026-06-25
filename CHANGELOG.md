# Changelog — Agent Skills Repository

All notable changes to the agent-skills repository. Maintained by Skill Foundry (AgentForge). Published twice weekly.

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