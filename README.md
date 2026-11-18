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
├── documentation-content/   Docs, presentations, document processing, X articles
├── skill-development/       Skill lifecycle, mining, authoring
├── business-strategy/       App discovery, Linear PM
├── development/             Scaffolding, cost routing, engineering habits
├── marketing/               Ad campaigns, image generation
├── compliance-legal/        Privacy & GDPR
├── git-release/             Git workflow & release automation
├── ai-agent-engineering/    AI agent architecture, prompting techniques, evaluation & memory
├── finance-ops/             SaaS metrics & unit economics
├── code-quality/            Code review
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
- **Validated** with real test cases and assertions (eval suite under `evals/evals.json`)
- **Documented** with usage examples and platform notes (corrections logs added where a skill's history has one)
- **Packaged** with self-contained scripts, eval suites, and changelogs

## Skills Catalog

<details>
<summary>🔧 DevOps & Infrastructure (11 skills)</summary>

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [ci-cd-pipeline-generator](/skills/devops-infrastructure/ci-cd-pipeline-generator) | DevOps/CI-CD | Production-ready CI/CD pipelines — GitHub Actions, GitLab CI, CircleCI, Jenkins | Universal |
| [infrastructure-as-code-guardian](/skills/devops-infrastructure/infrastructure-as-code-guardian) | DevOps/Infrastructure | Cross-tool IaC security and management — Terraform, Pulumi, CloudFormation, Ansible, Bicep | Universal |
| [kubernetes-operations](/skills/devops-infrastructure/kubernetes-operations) | DevOps/K8s | Production-grade Kubernetes ops — manifest generation, Helm charts, GitOps, security hardening, failure-mode diagnosis | Universal |
| [llm-observability](/skills/devops-infrastructure/llm-observability) | DevOps/LLM Observability | LLM/agent tracing, eval, cost tracking — OTel GenAI conventions with Langfuse, Phoenix, LangSmith, quality gates | Universal |
| [observability-engineering](/skills/devops-infrastructure/observability-engineering) | DevOps/SRE | OpenTelemetry instrumentation, monitoring, distributed tracing, SLI/SLO management, incident response | Universal |
| [production-engineering-workflows](/skills/devops-infrastructure/production-engineering-workflows) | DevOps/SRE | Full SDLC automation: /spec → /plan → /build → /test → /review → /ship | Universal |
| [sre-runbooks](/skills/devops-infrastructure/sre-runbooks) | DevOps/SRE | Safe-by-default SRE runbooks — incident response, postmortems, on-call handovers, RCA | Universal |
| [maintenance](/skills/devops-infrastructure/maintenance) | DevOps/Ops | Self-hosted customer-stack maintenance runbook — JEV-first decisions, health probes, weekly backup, JEV-gated updates, rollback, sparse LLM cost discipline | Universal |
| [performance-optimization](/skills/devops-infrastructure/performance-optimization) | DevOps/Perf | Frontend, backend, and infrastructure performance optimization | Universal |
| [ci-cd-and-automation](/skills/devops-infrastructure/ci-cd-and-automation) | DevOps/CI-CD | Quality-gated build/deploy pipelines — nothing ships without passing gates | Universal |
| [observability-and-instrumentation](/skills/devops-infrastructure/observability-and-instrumentation) | DevOps/Observability | Logging, metrics, tracing, and alerting so production behavior is visible | Universal |

</details>

### 🛡️ Security (7 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [agent-red-teaming](/skills/security/agent-red-teaming) | Security/Red-Team | Adversarial testing of agent systems — prompt injection, tool misuse, memory poisoning, privilege escalation, OWASP ASI01-ASI10 mapping | Universal |
| [agentic-security-scanner](/skills/security/agentic-security-scanner) | Security/Agent | OWASP AST10 security scanning — malicious skill detection, prompt injection, data exfiltration, SARIF | Universal |
| [prompt-injection-defense](/skills/security/prompt-injection-defense) | Security/LLM | Layered defense against direct/indirect injection, jailbreaks, prompt extraction — trust-labeled context, tool-boundary enforcement, adversarial evals | Universal |
| [security-and-hardening](/skills/security/security-and-hardening) | Security/Hardening | OWASP Top 10 hardening — three-tier boundary, dependency audit, LLM safety | Universal |
| [supply-chain-security-scanner](/skills/security/supply-chain-security-scanner) | Security/DevSecOps | Software supply chain security — SBOM generation, dependency scanning, provenance verification, license compliance | Universal |
| [threat-modeling](/skills/security/threat-modeling) | Security/Threats | STRIDE threat model with risk-rated threats and backlog stories | Universal |
| [vulnerability-management](/skills/security/vulnerability-management) | Security/Vuln-Mgmt | CVE tracking, CVSS/EPSS prioritization, zero-day response playbook, patch lifecycle, SIEM integration | Universal |

### 🔌 API & Backend (9 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [api-design-first](/skills/api-backend/api-design-first) | API/Backend | Design-first OpenAPI 3.1 specifications — REST, GraphQL, gRPC with cross-protocol consistency | Universal |
| [graphql-api-development](/skills/api-backend/graphql-api-development) | API/Backend | GraphQL API design and optimization — Apollo Federation, DataLoader, security, subscriptions | Universal |
| [har-api-reverse-engineering](/skills/api-backend/har-api-reverse-engineering) | API/Backend | Reverse-engineer a site's hidden/undocumented API from a captured HAR — derive, replay, verify, reuse (authorized use only) | Universal |
| [api-and-interface-design](/skills/api-backend/api-and-interface-design) | API/Design | Design APIs, module boundaries, and public interfaces that are hard to misuse | Universal |
| [social-har-api-connectivity](/skills/api-backend/social-har-api-connectivity) | API/Social | Connect a social platform's API from a captured HAR — filter, derive, verify, reuse (authorized only) | Universal |
| [image-to-image-character-generation](/skills/api-backend/image-to-image-character-generation) | API/Image | Generate consistent character images from Supabase/GDrive refs via kie.ai image-to-image — face anchors, dynamic prompt, anti-repeat | Universal |
| [kie-ai-platform](/skills/api-backend/kie-ai-platform) | API/Platform | Full kie.ai platform API: image/video/audio/chat gen, async tasks, callbacks, file upload, credits, webhook HMAC verifcation | Universal |
| [n8n-api-shape](/skills/api-backend/n8n-api-shape) | API/Automation | Instance-agnostic n8n REST API — read/update/verify workflows, strip-extras PUT recipe, banned fields, health check | Universal |
| [mcp-server-building](/skills/api-backend/mcp-server-building) | API/MCP | Build MCP servers on the 2026-07-28 stateless spec — tools/resources/prompts, server/discover, MRTR, stdio vs Streamable HTTP, OAuth, Inspector, deploy & publish | Universal |

### 🧪 QA & Testing (9 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [agent-evaluation](/skills/qa-testing/agent-evaluation) | QA/LLM Evaluation | Eval suites for LLM/agent output — golden datasets, calibrated LLM-as-judge, confidence intervals, CI quality gates | Universal |
| [browser-automation](/skills/qa-testing/browser-automation) | QA/Browser | Playwright browser automation — E2E testing, web scraping, monitoring, form submission, screenshots | Universal |
| [browser-testing-with-devtools](/skills/qa-testing/browser-testing-with-devtools) | QA/Browser | Test in real browsers via Chrome DevTools MCP — DOM, network, a11y | Universal |
| [playwright-e2e-testing](/skills/qa-testing/playwright-e2e-testing) | QA/Testing | Production-grade Playwright E2E testing — locator strategy, CI/CD, visual regression, component testing, a11y | Universal |
| [test-driven-development](/skills/qa-testing/test-driven-development) | QA/TDD | Write a failing test before the code that makes it pass | Universal |
| [contract-testing](/skills/qa-testing/contract-testing) | QA/Contracts | Consumer-driven contract tests, provider verification, and API drift | Universal |
| [manual-qa](/skills/qa-testing/manual-qa) | QA/Manual | Manually test a working app, API, or CLI and review rendered appearance | Universal |
| [performance-testing](/skills/qa-testing/performance-testing) | QA/Performance | k6 load, stress, soak, and spike tests, plus Lighthouse CI | Universal |
| [terminal-browser](/skills/qa-testing/terminal-browser) | QA/Browser | Drive a browser from a terminal agent session | Universal |

### 🎨 Frontend (5 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [accessibility-compliance-audit](/skills/frontend/accessibility-compliance-audit) | Frontend/A11y | WCAG 2.2 AA audits — automated scan, manual review, fix-ready code for React/Vue/Angular | Universal |
| [frontend-ui-engineering](/skills/frontend/frontend-ui-engineering) | Frontend/UI | Accessible, responsive, polished production UI — React/Vue/Svelte/HTML | Universal |
| [design-to-code](/skills/frontend/design-to-code) | Frontend/Design | AI-powered design-to-code: Figma, Sketch, screenshots → production React/Vue/Svelte/HTML | Universal |
| [ui-verification](/skills/frontend/ui-verification) | Frontend/Verify | Verify UI in the browser, reproduce a finding, and re-measure after a fix | Universal |
| [web-motion-and-animation](/skills/frontend/web-motion-and-animation) | Frontend/Motion | CSS, GSAP, and ScrollTrigger animation | Universal |

### 📊 Data (6 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [data-analysis](/skills/data/data-analysis) | Data Science | Data analysis, visualization, and reporting for CSV, JSON, Excel, SQL datasets | Universal |
| [exploratory-data-analysis](/skills/data/exploratory-data-analysis) | Data Science | Explore unfamiliar datasets, data-quality triage, pipeline validation | Universal |
| [dbt-data-transformation](/skills/data/dbt-data-transformation) | Data/DBT | Production-grade dbt analytics engineering — model development, testing, dbt Mesh governance, semantic layer | Universal |
| [database-schema-designer](/skills/data/database-schema-designer) | Database | Production-ready schema design — normalization, indexing, safe migrations, multi-tenant | Universal |
| [data-governance](/skills/data/data-governance) | Data/Governance | Data cataloging, lineage, quality frameworks, and metadata management | Universal |
| [data-pipeline-engineering](/skills/data/data-pipeline-engineering) | Data/Pipelines | ETL/ELT, orchestration, streaming, and schema drift | Universal |

### 📝 Documentation & Content (9 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [presentation-prompt-pipeline](/skills/documentation-content/presentation-prompt-pipeline) | Content/Presentations | Build or repair a deck with AI in six staged prompts (blueprint → structure → story frame → visual direction → content → build), each with an artifact and a gate, plus deck_lint.py enforcing ≤6-word titles, ≤5 tight bullets, speaker notes, ≤2 fonts and ≤3 colours | Universal |
| [document-processing](/skills/documentation-content/document-processing) | Content/Docs | PDF/DOCX/XLSX/PPTX automation — generation, manipulation, conversion, OCR, mail merge | Universal |
| [read-x-articles](/skills/documentation-content/read-x-articles) | Content/Web | Read X (Twitter) long-form Articles end-to-end from a shared link via the canonical /i/article/ID URL + render-capable extraction | Universal |
| [spec-writer](/skills/documentation-content/spec-writer) | Documentation/Specs | Turn vague feature requests into structured specs, technical plans, and task breakdowns — inline [ASSUMPTION] markers for every unspecified decision | Universal |
| [documentation-and-adrs](/skills/documentation-content/documentation-and-adrs) | Documentation/ADRs | Record architecture decisions and document design rationale | Universal |
| [technical-documentation](/skills/documentation-content/technical-documentation) | Documentation | AI-powered technical docs: READMEs, ADRs, API docs, runbooks, knowledge bases | Universal |
| [find-docs](/skills/documentation-content/find-docs) | Documentation/Lookup | Fetch current library docs and examples via Context7 | Universal |
| [spec-peer-review](/skills/documentation-content/spec-peer-review) | Documentation/Review | Fresh-eyes review of a saved spec, design, RFC, or PRD | Universal |
| [writing-for-agents](/skills/documentation-content/writing-for-agents) | Documentation/Agents | Write skills, prompts, and agent-facing docs | Universal |

### 🛠️ Skill Development (7 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [skill-lifecycle-foundry](/skills/skill-development/skill-lifecycle-foundry) | Skill Development | Mine, author, personalize, and generalize agent skills across their full lifecycle — session mining to release checklist | Universal |
| [skill-miner](/skills/skill-development/skill-miner) | Skill Development | Mine agent session/archive history for repeated skill-worthy workflows | Universal |
| [interview-me](/skills/skill-development/interview-me) | Skill Development | One-question-at-a-time interview to resolve underspecified asks | Universal |
| [skill-portability-and-packaging](/skills/skill-development/skill-portability-and-packaging) | Skill Development | Package and port skills across agent hosts: spec hard rules, install roots, description budgeting, plugin/marketplace manifests, hazard sweep, install verification | Universal |
| [agent-skills-creator](/skills/skill-development/agent-skills-creator) | Skill Development | Write, audit, or rewrite a SKILL.md and pick its structure | Universal |
| [writing-portable-scripts](/skills/skill-development/writing-portable-scripts) | Skill Development | Write scripts that run unchanged from any checkout | Universal |
| [writing-skills](/skills/skill-development/writing-skills) | Skill Development | Create, edit, and verify skills before deployment | Universal |

### 💼 Business & Strategy (6 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-discovery-scrutiny](/skills/business-strategy/app-discovery-scrutiny) | Business/AI | VC-grade app niche evaluation — Build/Pivot/Kill verdict | Universal |
| [linear-project-management](/skills/business-strategy/linear-project-management) | Business/PM | Drive Linear issues, projects, and teams from an agent via MCP + GraphQL — discovery-before-create, label taxonomy | Universal |
| [enterprise-consulting-methods](/skills/business-strategy/enterprise-consulting-methods) | Business/Strategy | 15 McKinsey/BCG-grade methodology patterns — SCPR, issue/hypothesis trees, storyline building, decision memos, stakeholder maps, meeting prep, workshop design, native PowerPoint chart production via python-pptx | Universal |
| [pricing-strategist](/skills/business-strategy/pricing-strategist) | Business/Strategy | SaaS pricing model selection, Van Westendorp WTP analysis, Good/Better/Best packaging | Universal |
| [go-to-market-launch](/skills/business-strategy/go-to-market-launch) | Business/GTM | Launch readiness audit, ORB channel framework, launch-day runbook, post-launch measurement | Universal |
| [product-manager-toolkit](/skills/business-strategy/product-manager-toolkit) | Business/PM | RICE prioritization, customer interview synthesis, PRD authoring, OKR design, decision frameworks — RICE/DACI/DARE | Universal |

### ⚙️ Development (26 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [app-scaffolding](/skills/development/app-scaffolding) | Development | 12-section mobile app build blueprint (iOS + Android) | Universal |
| [model-routing-cost-optimizer](/skills/development/model-routing-cost-optimizer) | Development/Cost | Route agent tasks to the cheapest adequate model tier — ROUTINE/MODERATE/COMPLEX classifier + vision guard | Universal |
| [anti-over-engineering](/skills/development/anti-over-engineering) | Development | Keep AI agents from over-engineering code beyond the user's request | Universal |
| [joerg-instruction-execution](/skills/development/joerg-instruction-execution) | Development | Execute shorthand/high-trust instructions by intent + verify output-side | Universal |
| [finding-unknowns](/skills/development/finding-unknowns) | Development | Systematic discovery of unknowns when entering unfamiliar code or domain territory | Universal |
| [hermes-bot-team-design](/skills/development/hermes-bot-team-design) | Development | Design a team of specialist Hermes bots from a project spec — roles, SOUL.md, MCP wiring, group chat | Universal |
| [mattpocock-dev-workflows](/skills/development/mattpocock-dev-workflows) | Development | Matt Pocock's engineering workflow patterns — spec synthesis, deep-module design, domain modeling, two-axis code review, disciplined bug diagnosis | Universal |
| [nodejs-development](/skills/development/nodejs-development) | Development/Node | Full-stack Node.js development — Fastify patterns, TypeScript type stripping, V8/libuv internals, OAuth 2.0/2.1, graceful shutdown, error handling, streams, testing | Universal |
| [repo-recon](/skills/development/repo-recon) | Development | Systematic codebase recon before touching unfamiliar code — map, learn commands, trace a flow, match conventions, write it down | Universal |
| [telegram-topics-pipeline](/skills/development/telegram-topics-pipeline) | Development | Run multiple bot sessions via Telegram forum topics with isolated context | Universal |
| [safe-refactor](/skills/development/safe-refactor) | Development | Change code structure without changing behavior in small verified steps — green baseline, characterization tests, blast-radius tracking | Universal |
| [agent-cli-harness](/skills/development/agent-cli-harness) | Development/Agents | Dispatch parallel or isolated work across agent CLIs, or request an independent CLI review | Universal |
| [architectural-analysis](/skills/development/architectural-analysis) | Development/Architecture | Audit a codebase scope for ownership, duplication, cycles, and costly change patterns | Universal |
| [brainstorming](/skills/development/brainstorming) | Development/Design | Explore the design before creative or feature work | Universal |
| [clonedeps](/skills/development/clonedeps) | Development/Deps | Clone dependency source into an ignored workspace so agents can read library internals | Universal |
| [coding-agent-sessions](/skills/development/coding-agent-sessions) | Development/Sessions | Recall recent coding conversations, transcripts, and earlier actions | Universal |
| [doubt-driven-development](/skills/development/doubt-driven-development) | Development/Review | Fresh-context adversarial review of non-trivial decisions before they stand | Universal |
| [executing-plans](/skills/development/executing-plans) | Development/Execution | Execute an implementation plan inline in the current session | Universal |
| [planning-and-task-breakdown](/skills/development/planning-and-task-breakdown) | Development/Planning | Break a spec into ordered implementable tasks | Universal |
| [repo-cleanup](/skills/development/repo-cleanup) | Development/Cleanup | Remove dead code, obsolete tests, and stale docs with evidence | Universal |
| [session-recap](/skills/development/session-recap) | Development/Sessions | Reorient a long session with its goal, pivots, outcomes, and open decisions | Universal |
| [source-driven-development](/skills/development/source-driven-development) | Development/Docs | Ground implementation decisions in current official documentation | Universal |
| [subagent-driven-development](/skills/development/subagent-driven-development) | Development/Execution | Execute a plan file task-by-task in the current session | Universal |
| [task-delegation](/skills/development/task-delegation) | Development/Agents | Parallel agents, specialist skills, and isolated context for implementation, research, and reviews | Universal |
| [to-tickets](/skills/development/to-tickets) | Development/Planning | Turn a plan or conversation into tracer-bullet tickets with blocking edges | Universal |
| [writing-plans](/skills/development/writing-plans) | Development/Planning | Write an implementation plan from a spec before touching code | Universal |

### 📣 Marketing (5 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [astra-campaign](/skills/marketing/astra-campaign) | Marketing | Full-service ad campaign generator (X, TikTok, Instagram) | Universal |
| [betterlife-image-generation](/skills/marketing/betterlife-image-generation) | Marketing/Image | BetterLife daily social images via kie.ai grok-imagine — Mira character anchors, anti-repetition | Universal |
| [local-video-production-m5](/skills/marketing/local-video-production-m5) | Marketing/Video | Local video production on the 16GB Apple-Silicon M5: LTX/Wan GGUF-MLX, memory discipline, character consistency, OpenMontage | Hermes + M5 |
| [openmontage](/skills/marketing/openmontage) | Video | Produce/edit video via OpenMontage pipelines (avatar-spokesperson, talking-head, cinematic) with director layers + approval gates | Hermes |
| [agent-n-video-pipeline](/skills/marketing/agent-n-video-pipeline) | Video | Fully-local "Agent N presents a message": Kokoro TTS → LTX-2.3 MLX A2V talking render + lip sync → karaoke → QA → X caption (Herald port, zero cloud) | Hermes + M5 |

### ⚖️ Compliance & Legal (5 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [privacy-compliance](/skills/compliance-legal/privacy-compliance) | Compliance/Legal | Global privacy compliance: GDPR, CCPA/CPRA, HIPAA, EU AI Act, LGPD, cross-border transfers | Universal |
| [fsi-compliance-checker](/skills/compliance-legal/fsi-compliance-checker) | Compliance/FSI | Map changes to PCI-DSS / SOX / FSI control IDs | Universal |
| [data-privacy-compliance](/skills/compliance-legal/data-privacy-compliance) | Compliance/Legal | GDPR/CCPA data privacy — PII, DSRs, consent, breach response | Universal |
| [gdpr-dsgvo-expert](/skills/compliance-legal/gdpr-dsgvo-expert) | Compliance/GDPR | GDPR/DSGVO privacy-risk scans, DPIAs, and data-subject requests | Universal |
| [open-source-license-compliance](/skills/compliance-legal/open-source-license-compliance) | Compliance/Licenses | Vet OSS licenses, compatibility, NOTICE files, and CI gates | Universal |

### 🌿 Git & Release (5 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [git-workflow-automation](/skills/git-release/git-workflow-automation) | Git/Release | Conventional Commits, changelogs, PR descriptions, semantic versioning, branch management | Universal |
| [release-management](/skills/git-release/release-management) | Git/Release | Version bumps, changelogs, tags, release notes, semver | Universal |
| [git-workflow-and-versioning](/skills/git-release/git-workflow-and-versioning) | Git/Workflow | Clean commits, branching, conflict resolution, messy-tree splitting | Universal |
| [changelog-generator](/skills/git-release/changelog-generator) | Git/Release | CHANGELOG and next semver from Conventional Commits | Universal |
| [deprecation-and-migration](/skills/git-release/deprecation-and-migration) | Git/Migration | Deprecate APIs and migrate callers | Universal |

### ✅ Code Quality (7 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [code-review](/skills/code-quality/code-review) | Code Quality | AI-powered code review — security, quality, style, architecture, test coverage, performance | Universal |
| [code-review-and-quality](/skills/code-quality/code-review-and-quality) | Code Quality | Multi-axis review of any code change before merge — own, agent, or human | Universal |
| [clean-pro-review-gates](/skills/code-quality/clean-pro-review-gates) | Code Quality | 5-gate pre-merge review framework — code quality (15 LLM failure modes), tests, docs, security (OWASP/CWE/LLM Top 10), CI/CD/container/IaC hardening | Universal |
| [debugging-and-error-recovery](/skills/code-quality/debugging-and-error-recovery) | Code Quality | Systematic debugging — failing tests, broken builds, regressions | Universal |
| [code-simplification](/skills/code-quality/code-simplification) | Code Quality | Refactor for clarity without changing behavior | Universal |
| [code-simplifier](/skills/code-quality/code-simplifier) | Code Quality | Simplify recently changed code without changing behavior | Universal |
| [remove-ai-slops](/skills/code-quality/remove-ai-slops) | Code Quality | Remove AI-generated code smells while preserving behavior | Universal |

### 🤖 AI Agent Engineering (4 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [prompt-engineering-concepts](/skills/ai-agent-engineering/prompt-engineering-concepts) | AI/Prompting | The 20 core prompting techniques as a selection table — zero-shot, few-shot, CoT, role, instruction, output formatting, temperature, chaining, self-consistency, RAG, templates, guardrails, dynamic, ReAct, tree-of-thought, compression, multi-modal, JSON mode, evaluation, optimization — with a time-pressured selection path, 8 named pitfalls, and an output-side verification checklist | Universal |
| [ai-agent-architecture](/skills/ai-agent-engineering/ai-agent-architecture) | AI/Architecture | Design, audit, and document AI agent system architectures — topology patterns, design contracts, audit frameworks, ADR templates, evaluation design | Universal |
| [agentic-eval](/skills/ai-agent-engineering/agentic-eval) | AI/Evaluation | LLM and agent evaluation — rubric judges, evaluator-optimizer loops, self-critique, pairwise ranking, calibration, eval harness setup | Universal |
| [agent-memory-management](/skills/ai-agent-engineering/agent-memory-management) | AI/Memory | Design, implement, and debug AI agent memory systems — long-term/working/episodic/semantic memory, vector stores, context window optimization, state persistence, retrieval strategies, memory consolidation — with memory_architect.py | Universal |

### 💰 Finance & Operations (3 skills)

| Skill | Domain | Description | Platforms |
|-------|--------|-------------|-----------|
| [saas-metrics-coach](/skills/finance-ops/saas-metrics-coach) | Finance/SaaS | ARR/MRR/NRR, LTV/CAC, churn analysis, unit economics, cash flow modeling, cohort analysis, benchmark comparisons — with metrics_calculator.py | Universal |
| [month-end-close](/skills/finance-ops/month-end-close) | Finance/Accounting | Month-end close management — close calendar and checklist, bank and balance-sheet reconciliations, accruals, prepaids, deferred revenue roll-forward, journal entries, trial balance and flux review, close-cycle acceleration — with close_checklist.py | Universal |
| [financial-modeling](/skills/finance-ops/financial-modeling) | Finance/Modeling | Three-statement models, scenarios, forecasting, and valuation | Universal |

## FAQ

**What are Agent Skills?**
Agent Skills are a lightweight, open format (agentskills.io) for giving AI agents specialized capabilities. Each skill is a folder with a SKILL.md file containing instructions, plus optional scripts, references, and test suites.

**Which platforms support Agent Skills?**
Claude Code, Claude CLI, Claude Projects, Claude API, OpenAI Codex, Gemini CLI, Cursor, OpenClaw, GitHub Copilot, Hermes Agent, OpenCode, Amp, Junie, and any SKILL.md-compatible agent.

**Why are skills nested under categories?**
`gh skill` and the agentskills.io specification discover skills at `skills/*/SKILL.md` and `skills/{scope}/*/SKILL.md` — category folders map to the `{scope}` position, so `gh skill install`, `gh skill publish`, and the agentskills.io CLI all resolve nested skills natively. Categories keep the library browsable.

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
- Self-contained scripts (PEP 723 inline dependencies)
- Platform notes when behavior differs across agents
- Changelog per skill
- MIT license

(Note: a corrections log is added per skill only where the skill's real development history produced documented failures — it is not a blanket requirement for every listing.)

## Managed by Skill Foundry

This repository is maintained autonomously by **Skill Foundry** — an AI department of AgentForge. Skills are discovered, evaluated, improved, and published on a twice-weekly cadence. Quality beats volume. Every run leaves the repo better than before.

---

## 💛 Support the Project

Agent Skills is free and open source. If it's saving you time and powering your workflow, consider supporting development:

**ETH:** `0xdfa8ac0f37d1129af72d0c4c6c0dff22e7a816b7`

**SOL:** `DogfWxst6B9gkoWquG1eGr1q1ExQeXbx2K1zhg9oEDhB`

**GitHub Sponsors:** [Sponsor on GitHub](https://github.com/sponsors/JPeetz)

Every contribution helps keep this project moving. Thank you 🙏

---

## 🤝 Contributing

PRs are welcome — skills, improvements, and bug reports. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the submission and review process.

- **Bug fixes / skill improvements** → open a PR directly
- **New skills / feature requests** → open an issue first to discuss scope and fit
- **Security issues** → see [SECURITY.md](./SECURITY.md) for responsible disclosure

---

*Available via `gh skill install JPeetz/agent-skills` | Part of the [AgentForge Ecosystem](https://github.com/JPeetz/agentforge) | [agentskills.io](https://agentskills.io)*
