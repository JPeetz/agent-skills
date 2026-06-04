# DevLog — Agent Skills Repository Development History

_Narrative development log. Maintained by Skill Foundry. Every run adds an entry. Searchable by skill name, domain, keyword, and date._

---

## 2026-06-04 — Run 002: DevOps, Git, A11y, API Domains

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