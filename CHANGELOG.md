# Changelog — Agent Skills Repository

All notable changes to the agent-skills repository. Maintained by Skill Foundry (AgentForge). Published twice weekly.

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