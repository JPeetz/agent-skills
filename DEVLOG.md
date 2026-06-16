# DevLog — Agent Skills Repository Development History

_Narrative development log. Maintained by Skill Foundry. Every run adds an entry. Searchable by skill name, domain, keyword, and date._

---

## 2026-06-16 — Run 003: Security, Infrastructure, Testing, Documents

### Discovery
Third autonomous run (first Tuesday run on schedule). Discovery scans across security, testing, infrastructure, data engineering, database, SRE, and observability domains. Key sources: Currents.dev Playwright Best Practices Skill (highest-scoring QA skill), antonbabenko/terraform-skill (renowned Terraform expert), planetscale/database-skills (official PlanetScale), LukasNiessen/kubernetes-skill (KubeShark — #1 K8s skill), vaquarkhan/data-engineering-agent-skills (73 workflows). Ecosystem signal: security skills are in highest demand due to Mondoo/Snyk research showing 26.1% of public skills contain vulnerabilities. OWASP Agentic Skills Top 10 published in 2026. Supply chain and IaC security are the fastest-growing agent skill categories.

### Selection
20 candidates scored against 10-dimension framework. Kill floor 5/10 eliminated 15. Five selected:

1. **playwright-e2e-testing** (8.5/10) — NEW. Top-scoring QA skill filling the #1 underserved agent skill category (E2E testing). Currents.dev source scored 8.3 on quality but only covered 7 testing domains. Materially improved to 14 testing domains with eval suite and executable scripts. QA testing is consistently ranked as the highest-ROI agent skill category (Agensi 2026).
2. **supply-chain-security-scanner** (8.0/10) — EXISTING, now published. Built for Run 003 but held for packaging completion. 841-line SKILL.md covering npm, PyPI, Maven, Go, Cargo, containers. SPDX/CycloneDX SBOM generation. cosign/slsa-verifier provenance integration. OWASP AST10 aligned. The highest-demand security domain in the 2026 ecosystem.
3. **infrastructure-as-code-guardian** (8.0/10) — EXISTING, now published. 800-line SKILL.md. Universal IaC across 6 tools (Terraform, Pulumi, CloudFormation, Ansible, Bicep, Crossplane). Fills the gap left by single-tool IaC skills (HashiCorp Terraform-only, Pulumi ecosystem-only). Security hardening, drift detection, migration patterns.
4. **browser-automation** (7.5/10) — EXISTING, now published. Built 2026-05-28, held for packaging. Playwright browser automation. 671-line SKILL.md with SEO/GEO metadata.
5. **document-processing** (7.5/10) — EXISTING, now published. Built 2026-05-28, held for packaging. Complete office document automation. 872-line SKILL.md. PDF/DOCX/XLSX/PPTX with format conversion.

Eliminated candidates: terraform-infrastructure-provisioner (7.5 — overlapped with IaC Guardian, tool-specific vs universal), kubernetes-kubeshark (7.0 — queued for Run 004, strong but not highest priority), database-management (7.0 — queued for Run 004), incident-response-sre (6.5 — source material too thin, requires significant build), dbt-data-transformation (6.5 — too platform-specific, requires expansion).

### Improvements

**playwright-e2e-testing:** Materially improved over currents-dev source. Added 7 testing domains not in source: performance testing (Lighthouse/Web Vitals), internationalization testing (RTL, locale switching), security testing (XSS, CSRF, CSP validation), WebSocket/real-time testing, Electron app testing, browser extension testing, and comprehensive debugging/flaky test detection with auto-healing patterns. Created complete eval suite (8 positive + 3 near-miss negatives). Built 3 executable utility scripts: validate-playwright-setup.sh (CI-compatible), generate-auth-profile.ts (multi-role), flake-detector.sh (repeat-run analysis). 3 reference documents: locator-strategies.md (anti-pattern catalog), testing-types-matrix.md (decision flowcharts, migration guides), ci-cd-patterns.md (GitHub Actions/GitLab CI/CircleCI/Docker).

**supply-chain-security-scanner:** Already fully packaged. 3 scripts: scan-dependencies.sh (multi-ecosystem auto-detection), generate-sbom.sh (4 output formats), verify-provenance.sh. 3 references: OWASP AST10 summary, SBOM format comparison, vulnerability database integration. 10 eval cases.

**infrastructure-as-code-guardian:** Already fully packaged. 3 scripts: validate-iac.sh (multi-tool auto-detection), security-scan-iac.sh (tfsec/checkov/trivy/cfn-nag/ansible-lint), drift-check.sh (cross-tool with Slack alerting). 3 references: IaC patterns (module composition, GitOps CI/CD), security hardening (40+ item checklist), cloud provider matrix (AWS/Azure/GCP feature parity). 7 eval cases.

### Challenges
- **GitHub gh CLI:** `gh repo view` failed silently but `gh auth status` confirmed token. Cloned via `gh repo clone` for documentation work.
- **GitHub Topics at limit:** Repository at 20-topic limit (GitHub's maximum per repo). Cannot add new topics without removing existing ones. Logged as known constraint.
- **Run scheduling:** This is the first Tuesday-scheduled run per SOUL.md (Tue/Thu 06:00 Dublin). Activated at 02:00 via cron.
- **Local skill backlog:** 6 fully-packaged skills were local-only, created in previous runs but never committed. This run clears the backlog by publishing 4 of them (browser-automation, document-processing, supply-chain-security-scanner, infrastructure-as-code-guardian).

### Next Targets
- **Run 004 (Thu Jun 18):** Database management (planetscale/database-skills), Kubernetes operations (KubeShark), package remaining local skills (code-review, data-analysis), evaluate incident-response-sre
- **Queue:** terraform-infrastructure-provisioner (antonbabenko), dbt-data-transformation, python-logging-observability, helm-chart-scaffolding

### Discovery
Second autonomous run. Broad discovery across 50+ searches targeting high-demand agent skill domains. Key research sources: Agensi best-of lists (DevOps, Testing, Git, Database, Documentation), VoltAgent awesome-agent-skills, addyosmani agent-skills (23 skills), Orchestra Research AI-research-SKILLs (85+ skills), community-powered registries (LobeHub, MCP Market, AgentSkills.co, SkillsLLM, QASkills). Ecosystem scan confirmed ~5,200 community skills exist, with 26.1% containing vulnerabilities (Mondoo/Snyk research).

### Selection
20 candidates evaluated against the 10-dimension framework. Kill floor 5/10 eliminated 16. Four selected:

1. **ci-cd-pipeline-generator** (8.5/10) — DevOps CI/CD generation identified as the #1 underserved agent skill category (Agensi 2026). Existing alternatives (env-doctor) only handle diagnostics, not full pipeline generation. Fills end-to-end pipeline generation gap with security validation.
2. **git-workflow-automation** (8.0/10) — Git automation is the highest-ROI skill category (Agensi: "saves the most daily time"). Existing skills (netresearch/git-workflow-skill, lobehub git-workflow) focus on individual operations. This skill unifies the full workflow lifecycle.
3. **accessibility-compliance-audit** (7.5/10) — Accessibility skills ecosystem is fragmented: 33-skill packs (Matthew Lam), 40 inclusive design skills (Marie Claire Dean), community-access/accessibility-agents. These are designer-facing. This skill is engineer-facing with framework-specific fix code.
4. **api-design-first** (7.5/10) — No existing design-first API skill in the ecosystem. Current API skills (database schema designer, API documentation) are documentation-first, not contract-first. This skill drives implementation from spec, not retrofits docs.

Eliminated candidates: Database Schema Designer (6.5 — too close to existing data-analysis skill), SEO Content Writer (6.0 — overlaps with astra-campaign), Observability Engineer (6.0 — platform-specific to Grafana/Elastic, not universal), Shell/Linux Admin (5.5 — too narrow, mostly platform-specific skills exist).

### Improvements
All four skills built with significant improvements over alternatives:

**ci-cd-pipeline-generator:** Complete pipeline architecture with DAG-aware parallel stages, trigger configurations (push/PR/tag/schedule), quality gates (lint→test→build→security→deploy), environment promotion with approval gates, canary deployment patterns, rollback strategies, caching optimization (package manager + Docker layer + build cache), secrets management with platform-native references, security mandates (SHA-pinned actions, OIDC, token permissions, artifact signing, dependency review, secret scanning). 4 stack-specific templates (Node.js+K8s, Python+ECS, Go+Kube, Static Site). Monorepo path filtering and multi-language matrix build support.

**git-workflow-automation:** Complete Conventional Commits enforcement with type-to-SemVer mapping, breaking change detection (! syntax + BREAKING CHANGE footer), commit quality rules (imperative mood, 72-char limit, atomic commits, issue references). Branch naming convention with type/ticket/description pattern. PR template with Summary/Motivation/Changes/Testing/Checklist sections. Changelog generation from git history with user-facing prose rewrite. Semantic versioning engine (MAJOR/MINOR/PATCH determination). Release flow documentation (branch→bump→changelog→tag→push→Release). Merge conflict resolution with priority rules. Security rules (GPG signing, secret detection, branch protection, signed tags). CI/CD integration (commitlint, semantic-release, git-cliff compatibility).

**accessibility-compliance-audit:** 3-phase audit process (automated scan → manual review → fix generation). 8 automated scan categories (semantics, interactive, ARIA, forms, images, color, focus, multimedia). 6 manual review areas requiring human judgment. Complete WCAG 2.2 AA reference covering all 4 principles. 4-tier severity classification (Critical/High/Medium/Low). Framework-specific patterns for React (aria-live, form validation), Vue (keyboard handlers), Angular (aria-describedby). ARIA Rules including "First Rule of ARIA" (use native HTML). Color contrast analysis with ratios and WCAG SC references. Keyboard and screen reader checklists. `prefers-reduced-motion` CSS pattern. 6 red lines (things never to suggest). Structured audit output format with file/line references and summary generation.

**api-design-first:** Design-first workflow (Resource Model → OpenAPI 3.1 → Review → Mock → Implementation → Tests). Complete OpenAPI 3.1 spec generation covering all required sections. REST resource naming conventions (plural nouns, max 2 levels deep, CRUD operations). RFC 7807 Problem Details error format with complete status code table. Cursor-based pagination (preferred) with offset-based fallback. URL path API versioning with Sunset/Deprecation/Link headers and 6-month grace period. Authentication patterns (Bearer JWT, API Key, OAuth2 with OpenAPI securitySchemes). Tiered rate limiting with standard headers. Idempotency key pattern for safe retries. Advanced query patterns (filtering, sorting, searching, sparse fieldsets, include). GraphQL schema with Relay Cursor Connections. gRPC proto design. Cross-protocol consistency rules. 15-item API Design Checklist. Security hardening (input validation, TLS, CORS, CSP, security headers, rate limiting all layers).

### Challenges
- **Repository clone:** GitHub repo clone failed on first attempt (token formatting). Resolved with explicit PAT.
- **Skill duplication risk:** Database Schema Designer (mcpmarket/softaworks) had good content but overlapped with our existing data-analysis skill. SEO Content Writer overlapped with astra-campaign. Made tough kill decisions.
- **Observability skill:** Considered but rejected — existing offerings (Grafana skills, Elastic skills, Dash0 skills) are highly platform-specific and don't achieve true universality.
- **Context budget:** Building 4 skills with full documentation (SKILL.md, evals, scripts, references, per-skill CHANGELOG) in a single run pushes context limits. Optimized by parallelizing writes.

### Next Targets
- Broaden into: security (pentesting, threat modeling), testing (E2E, load testing, contract testing), data engineering (ETL pipelines, dbt skills).
- ML/AI research skill ecosystem exploration (Orchestra Research AI-research-SKILLs has 85+ domain skills).
- Consider packaging existing local skills (browser-automation, code-review, data-analysis, document-processing) for repo shipment.
- Next run: Tuesday June 9 02:00 Dublin.

---

## 2026-05-24 — Repository Inception

### Discovery
Initial launch — not a discovery run, but a foundation ship. Three skills built from AgentForge's internal department development, extracted as standalone Agent Skills per the agentskills.io specification.

### Selection
Three skills selected as v1.0.0 foundation:
1. **app-discovery-scrutiny** — Scored highest on Business Value (enables VC-grade analysis for any mobile app), Platform Portability (pure SKILL.md, no platform-specific tools), and Distinctiveness (no public equivalent at this quality level).
2. **app-scaffolding** — Fills a clear quality gap: existing scaffolding skills are generic PRDs, not 12-section production blueprints with exact hex colors, animation timing, and DB schemas.
3. **astra-campaign** — Covers the underserved marketing/campaign niche. Existing marketing skills repos (hyperfx-ai, coreyhaines31) focus on individual tactics. This skill runs the full agency pipeline.

### Improvements
All three built from AgentForge's real-world usage data:
- Corrections logs capture actual failures (Forge was a CLI tool, Runway/Luma didn't have API keys, SEO kill-floor killed mobile apps)
- Eval suites include near-miss negatives (CLI tools, SaaS products, Chrome extensions, Facebook ads)
- Scripts provide deterministic computation (scoring engine, claims checker, skill validator)
- Descriptions optimized per agentskills.io best practices (imperative, user-intent, near-miss protection)

### Challenges
- **GitHub repo naming:** Chose `agent-skills` (not `agentforge-skills` or `awesome-agent-skills`). Rationale: highest-SEO match for "agent skills," no company lock-in, clean `gh skill install` path. Tradeoff: requires the name to be available on GitHub — it was.
- **gh skill publish:** Discovered mid-build that GitHub launched `gh skill` in April 2026. Added official CLI install instructions. Validated repository compatibility.
- **Platform scope:** Decided Universal as default for all v1.0.0 skills. No platform-specific adapters needed yet — all three use standard SKILL.md + Python scripts with inline deps.

### Next Targets
- Broaden domain coverage beyond Business/Development/Marketing
- Source skills from community repos (anthropics/skills, hyperfx-ai/marketing-skills, coreyhaines31/marketingskills)
- Identify pain-point gaps: debugging, testing, security, documentation, CI/CD
- First autonomous run: Tuesday May 26 02:00 Dublin