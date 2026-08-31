---
name: technical-documentation
description: >
  AI-powered technical documentation creation, maintenance, and auditing
  across README, ADR, API docs, runbooks, onboarding guides, changelogs,
  knowledge bases, and AI agent context files (AGENTS.md/CLAUDE.md).
  Primary keywords: technical documentation writing automation, ADR
  architecture decision record, API docs OpenAPI generation, README quality
  template, documentation-driven development, runbook automation, knowledge
  base maintenance, markdown best practices, onboarding guide, changelog
  format, documentation audit completeness accuracy, AI agent documentation
  AGENTS.md. For all major agentic platforms.
version: 1.0.0
author: Skill Foundry
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
tags:
  - documentation
  - technical-writing
  - adr
  - architecture-decision-records
  - api-docs
  - readme
  - markdown
  - knowledge-base
  - onboarding
geo:
  primary_workflows:
    - readme_composition
    - adr_generation
    - api_documentation
    - runbook_creation
    - onboarding_guide_writing
    - changelog_maintenance
    - documentation_audit
    - knowledge_base_management
    - agent_facing_documentation
  target_roles:
    - software_engineer
    - tech_lead
    - devops_engineer
    - engineering_manager
    - technical_writer
    - developer_experience_engineer
  complexity_level: intermediate
  prerequisite_knowledge:
    - markdown_syntax
    - basic_software_architecture
    - version_control_with_git
    - api_concepts
---

# /technical-documentation — Create, maintain, and audit technical
# documentation: READMEs, ADRs, API docs, runbooks, onboarding guides,
# changelogs, knowledge bases, and AI-agent-facing context files.

# Technical Documentation Agent Skill

Create, maintain, and audit technical documentation with an AI agent that
understands audience, structure, and long-term maintenance. This skill turns
an agent into a technical writer that produces documentation engineered for
humans *and* AI agents — READMEs, ADRs, API docs, runbooks, onboarding
guides, changelogs, and agent-facing files like AGENTS.md.

---

## Quick Reference

| Document Type | Purpose | Key Audience | Lifecycle |
|---|---|---|---|
| 📘 **README** | Project entry point | New contributors, evaluators | Updated with every release |
| 🏛️ **ADR** | Record architectural decisions | Future maintainers | Immutable once accepted |
| 🔌 **API Docs** | Describe endpoints/schemas | API consumers, integrators | Updated with every API change |
| 🚨 **Runbook** | Incident response procedures | On-call engineers | Reviewed after every incident |
| 🚀 **Onboarding Guide** | Ramp up new team members | New hires, transfers | Updated quarterly |
| 📋 **Changelog** | User-facing release notes | End users, downstream teams | Updated with every release |
| 🧠 **Knowledge Base** | Long-lived reference material | Entire organization | Continuous curation |
| 🤖 **AI Agent Docs** | Context for AI coding agents | AI agents (Claude, Copilot, etc.) | Updated with structural changes |

**Severity Scale (for documentation audits):**

- 🔴 **CRITICAL** — Missing or dangerously wrong. Could cause production incidents or security issues.
- 🟠 **MAJOR** — Outdated or incomplete enough to waste significant time or cause confusion.
- 🟡 **MINOR** — Minor inaccuracies, unclear phrasing, formatting issues.
- ⚪ **NIT** — Style preferences, consistency nits, polish.

---

## When to Use This Skill

Activate this skill when the user asks you to:

- "Write a README for this project" / "Improve our README"
- "Create an ADR for <decision>" / "Document this architectural decision"
- "Generate API documentation" / "Document this endpoint"
- "Write a runbook for <service>" / "Create incident response docs"
- "Make an onboarding guide for new engineers"
- "Audit our documentation" / "Is our documentation complete?"
- "Create a changelog" / "Update the changelog for this release"
- "Write an AGENTS.md for this project" / "Set up AI agent context files"
- "Organize our knowledge base" / "Review our docs for freshness"
- "Document this module" / "Explain this system in writing"
- Any request containing "document", "docs", "README", "write up", "explain in writing"

Additionally, activate proactively when a conversation involves a new
project, module, or system that lacks documentation, and the user's tone
suggests they would benefit from having it documented.

### Do NOT Activate For

The following inputs are **near-miss negatives** — they mention
documentation-like language but are not documentation work:

- **Code comments / docstrings**: "Add docstrings to this function" —
  code-level comments, not standalone documentation. Refer to coding-agent.
- **Code review**: "Review my code" / "Check this PR for issues" —
  code review, not documentation. Refer to code-review skill.
- **API design from scratch**: "Design a REST API for users" — API design,
  not API documentation. Refer to api-design-first.
- **General Q&A**: "What does microservices mean?" — definitions, not docs.
- **Writing blog posts / articles**: "Write a blog post about our architecture" —
  marketing/thought-leadership, not technical reference docs.
- **Legal documents**: "Write our privacy policy" — legal, not technical.
  Refer to ai-legal-content or gdpr-compliance-expert.
- **Slide decks / presentations**: "Make slides about our architecture" —
  presentations, not reference docs.
- **Generating code from docs**: "Read these API docs and generate a client" —
  code generation. The docs are input, not the output.

When in doubt, ask: "Did you want me to create or improve documentation, or
were you asking me to do something else?"

---

## Documentation Types & Patterns

### 1. README Composition

Every README is a project's first impression. A README must answer, in this
order: *What is this? Why does it exist? How do I use it? How do I
contribute?*

**The Standard README Structure:**

```markdown
# Project Name
> One-line description — what it does and why someone should care.

## Badges
[build status] [coverage] [version] [license] [platform support]

## Overview
2-3 sentences on what the project is and the problem it solves.

## Quick Start
The absolute minimum to get running. Copy-paste-able commands that work.
If it takes more than 5 commands or 2 minutes, it's too long.

## Installation
Detailed install instructions. Per-platform if needed. Prerequisites first.

## Usage
Common use cases with code examples. Link to full API docs, don't inline them.

## Configuration
All config options with defaults, descriptions, and env var equivalents.

## Architecture
High-level diagram or description. How the pieces fit together. Link to ADRs.

## Contributing
How to set up a dev environment, run tests, and submit changes. Link to
CONTRIBUTING.md if it exists.

## License
License name and link to LICENSE file.
```

**RED FLAGS — fix these immediately (🔴 CRITICAL):**

- No "Quick Start" section or Quick Start that doesn't work when copy-pasted
- Stale install instructions referencing removed dependencies
- Missing license information
- No indication of what the project actually does in the first 3 sentences

**YELLOW FLAGS — improve these (🟠 MAJOR):**

- No architecture section for projects with >3 modules
- Examples that use placeholder values without explaining how to get real ones
- Configuration section that lists options but doesn't explain what they do
- Badges pointing to broken CI/dead services

### 2. Architecture Decision Records (ADRs)

ADRs capture *why* a decision was made — the context, alternatives, and
tradeoffs. They live in `docs/adr/` and are numbered sequentially.

**ADR Workflow:**

1. **Propose**: Create a new ADR with status "proposed"
2. **Review**: Team discusses. ADRs are lightweight — a PR review is usually
   enough.
3. **Accept or Reject**: If accepted, status becomes "accepted". If rejected,
   status becomes "rejected" with a note explaining why. Rejected ADRs are
   still valuable — they prevent re-litigation.
4. **Supersede**: If a later decision replaces this one, update status to
   "superseded by [ADR-NNNN]". Never delete ADRs.

**When to Write an ADR:**

- Choosing between multiple viable approaches (e.g., PostgreSQL vs MongoDB)
- Introducing a new pattern or technology into the codebase
- Deprecating an existing pattern or technology
- Making a decision with significant cost, risk, or cross-team impact
- Any decision you expect someone to question in 6 months

**ADR File Naming:**
```
docs/adr/0001-use-postgresql-as-primary-database.md
docs/adr/0002-use-jwt-for-api-authentication.md
docs/adr/0003-adopt-trunk-based-development.md
```

Use the full ADR template from `references/adr-template.md`.

### 3. API Documentation

API docs must be the single source of truth. Generate them from the API
specification, not from prose. Never maintain API docs and API specs
separately — they will diverge.

**REST API Documentation Pattern:**

- **Use OpenAPI 3.1 (Swagger)** as the canonical API description. Generate
  human-readable docs from the spec, not the other way around.
- Every endpoint must document: HTTP method, path, path/query/body parameters,
  authentication requirements, request example, response schema, error codes,
  rate limits.
- Use RFC 7807 Problem Details for error responses.
- Document deprecations with `Sunset` and `Deprecation` headers.

**GraphQL API Documentation Pattern:**

- Use schema introspection to generate docs. Tools: GraphiQL, SpectaQL,
  GraphQL Playground, Apollo Studio.
- Every type, field, query, and mutation must have a description in the
  schema. Treat schema descriptions as the canonical documentation.
- Document: queries, mutations, subscriptions, types, enums, input objects,
  deprecation reasons (`@deprecated` directive).

**gRPC Documentation Pattern:**

- Use protobuf comments as the canonical documentation source. Generate
  docs with `protoc-gen-doc`.
- Every service, RPC, and message field must have a comment.
- Document: streaming (unary, server, client, bidirectional), error codes,
  deadlines/timeouts, authentication metadata.

**Cross-Protocol Consistency Rules:**

- Use `camelCase` for field names across all protocols
- Use ISO 8601 for all date/time values
- Use consistent pagination across protocols (cursor-based preferred)
- Use consistent error shapes

### 4. Runbooks

Runbooks are procedural documents for responding to known incidents. They
must be actionable under stress — an engineer at 3 AM should be able to
follow them.

**Runbook Structure:**

```markdown
# Runbook: <Incident Name>

## Symptoms
- Alert: <alert name and source>
- User reports: "I see X error"
- Metrics: <metric> exceeds <threshold>

## Impact
What breaks? Who is affected? What's the blast radius?

## Severity Levels
- SEV1: <conditions> — page on-call immediately
- SEV2: <conditions> — page during business hours
- SEV3: <conditions> — create ticket

## Prerequisites
- Access to: <dashboards, tools, SSH hosts>
- Permissions: <required IAM roles / access levels>

## Diagnostic Steps
1. Check <dashboard> for <metric>.
   - Normal range: <X-Y>. If outside: proceed to step 2.
2. Run: `<diagnostic command>` on <host>.
   - Expected output: <X>. If different: proceed to mitigation.

## Mitigation
1. **First response (≤5 min):** <immediate action to stop bleeding>
2. **Short-term fix:** <temporary workaround>
3. **Long-term fix:** <link to issue/ticket>

## Verification
- <metric> should return to <normal range>
- <endpoint> should return 200
- Users should be able to <action>

## Escalation
- If mitigation fails after <N> minutes: escalate to <team/person>
- If <condition>: escalate to <person/team>

## Post-Incident
- Create a postmortem in <location>
- File follow-up issues for long-term fixes
- Update this runbook with lessons learned
```

**Runbook Red Flags (🔴 CRITICAL):**

- Hardcoded credentials or IP addresses in commands
- Commands that are destructive without clear warnings (`DROP`, `DELETE`,
  `TERMINATE`)
- Missing prerequisites section (engineer can't follow steps without access)
- Diagnostic steps that don't explain what normal output looks like

### 5. Onboarding Guides

Onboarding guides reduce time-to-first-commit. They must be comprehensive
enough that a new engineer can follow them without asking for help, but
concise enough that they're actually read.

**Onboarding Guide Structure:**

```markdown
# Onboarding Guide: <Team/Project>

## Welcome
Link to team charter, mission, and who's who.

## Day 0 — Before You Start
- Hardware/software you'll need
- Accounts to request (and how to request them)
- Reading material (architecture docs, ADRs, team wiki)

## Week 1 — Get Set Up
- Dev environment setup (step-by-step, copy-paste-able)
- Clone repos and build locally
- Run the test suite
- Make your first commit (a tiny one — fix a typo, add a test)

## Week 2-4 — Ramp Up
- Key systems to understand (with links to docs)
- Pairing sessions to schedule
- Good first issues to tackle
- Team rituals: standups, planning, retros

## Reference
- Glossary of team-specific terms
- Important links (dashboards, CI, wiki, chat channels)
- Who to ask for what
```

### 6. Changelogs

Changelogs are for *humans*, not git logs. Follow
[Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [1.2.0] - 2026-06-15

### Added
- New feature X for Y use case
- Support for Z protocol

### Changed
- Upgraded dependency A from v2 to v3
- Renamed `oldMethod()` to `newMethod()` (old name deprecated)

### Deprecated
- `oldMethod()` — use `newMethod()` instead. Will be removed in v2.0.0.

### Removed
- Dropped support for Node.js 16

### Fixed
- Race condition in payment processing (#1234)
- Memory leak in WebSocket handler (#1245)

### Security
- Patched CVE-2026-XXXXX in dependency B
```

**Changelog Rules:**

- Always include a link to the full diff at the bottom:
  `[1.2.0]: https://github.com/owner/repo/compare/v1.1.0...v1.2.0`
- Use semantic versioning. Breaking changes get a MAJOR bump.
- Group entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`,
  `Security`. Never use a catch-all "Misc" or "Other" category.
- Never include internal refactors that have no user impact.

### 7. Knowledge Base Maintenance

A knowledge base rots if not maintained. Establish a maintenance cadence:

**Freshness Review Schedule:**

| Content Type | Review Frequency | Owner |
|---|---|---|
| Runbooks | After every incident + quarterly | On-call rotation |
| Onboarding guides | Quarterly | Engineering manager |
| API docs | Every release | API team |
| ADRs | N/A (immutable) | N/A |
| README | Every release | Project maintainer |
| Agent context files | Monthly + on structural changes | Tech lead |
| General wiki pages | Bi-annual | Rotating ownership |

**Documentation Audit Checklist:**

- [ ] Every service has a README with Quick Start that works
- [ ] Every API endpoint is documented (check OpenAPI coverage)
- [ ] Every architectural decision from the past 6 months has an ADR
- [ ] Every runbook has been tested in the past 6 months
- [ ] Onboarding guide reflects current tooling and processes
- [ ] Changelog is up to date for the latest release
- [ ] Agent context files (AGENTS.md, CLAUDE.md) exist and are current
- [ ] No documentation references removed/deprecated tools or endpoints
- [ ] No hardcoded credentials, tokens, or internal IPs in any doc
- [ ] Cross-links between documents are not broken
- [ ] Dates on time-sensitive docs are within their review window

### 8. Documentation for AI Agents

AI coding agents need context. Files like `AGENTS.md`, `CLAUDE.md`, and
`CURSOR.md` provide that context — they are the README for machines.

**AGENTS.md Pattern (Universal Agent Context):**

```markdown
# AGENTS.md — Project Context for AI Agents

## Project Identity
- **Name**: <project>
- **Purpose**: <one-line mission>
- **Stack**: <languages, frameworks, databases>
- **Repository**: <link>

## Architecture
- <High-level description of how components fit together>
- <Key design patterns used>
- <Data flow diagram or description>

## Conventions
- Code style: <formatter, linter config>
- Commit style: <conventional commits, etc.>
- Testing: <framework, patterns, coverage requirements>
- Branching: <strategy>

## Constraints
- <Things agents must NOT do — e.g., never modify schema without migration>
- <Security boundaries — e.g., never hardcode secrets>
- <Performance constraints — e.g., max response time targets>

## Key Files
- <file>: <what it contains and why it matters>
- <file>: <what it contains and why it matters>

## External Dependencies
- <service>: <purpose, link to docs>
- <API>: <purpose, link to docs>

## Common Tasks
- <task>: <how to do it, what to watch out for>
- <task>: <how to do it, what to watch out for>
```

**AI Context File Best Practices:**

- Keep it under 500 lines. Agents have context windows — be concise.
- Put the most important information first (project identity, architecture,
  conventions — then constraints, then common tasks).
- Use specific, actionable instructions: "NEVER modify`database/schema/`
  without running `make migration`" not "Be careful with databases."
- Update on every architectural change. A stale AGENTS.md is worse than no
  AGENTS.md — it gives agents false confidence.
- If the project has a contributing guide, link to it — don't duplicate.

**Platform-Specific Patterns:**

| Platform | Context File | Notes |
|---|---|---|
| **Universal** | `AGENTS.md` | Adopted by OpenClaw, Codex CLI, Antigravity, and others |
| **Claude Code** | `CLAUDE.md` | Same format; can also read AGENTS.md |
| **Cursor** | `.cursorrules` or `CURSOR.md` | Supports `.cursor/rules/*.mdc` for multiple rule files |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Workspace-level instructions |
| **Windsurf** | `.windsurfrules` | Global or per-workspace |
| **OpenCode** | `AGENTS.md` or `OPENCODE.md` | Standard AGENTS.md format |

---

## Documentation-Driven Development (DDD)

Write the documentation *before* the code. This forces clarity:

1. **Write the README first.** Describe what the system will do from the
   user's perspective. If you can't explain it clearly in prose, you can't
   code it clearly.
2. **Write the API docs (OpenAPI spec) before implementing endpoints.**
   Review the API contract with consumers before writing a single line.
3. **Write the ADR before making the architectural decision.** Forces you to
   articulate the problem, alternatives, and tradeoffs.
4. **Write the runbook before the system goes to production.** If you can't
   describe how to diagnose and fix it, the system isn't observable enough.
5. **Write the changelog entry as part of the PR template.** No merged PR
   without a changelog entry.

**DDD PR Template:**
```markdown
## Summary
<what and why>

## Documentation Checklist
- [ ] README updated (if new features, changed usage, or new config)
- [ ] API docs updated (if API changed)
- [ ] ADR created (if architectural decision made)
- [ ] Changelog entry added
- [ ] Runbook updated (if operational behavior changed)
- [ ] Agent context files updated (if conventions/architecture changed)
```

---

## Markdown Best Practices

Technical documentation lives in Markdown. Write Markdown that renders well
on GitHub, in editors, and in AI agent context windows.

**Structural Rules:**

- Use ATX-style headers (`#`, `##`, `###`) — never setext-style (`===`, `---`)
- One H1 per file (the title). Use H2-H6 for sections.
- Put a blank line before and after headers, lists, and code blocks.
- Use reference-style links for repeated URLs:
  `[text][ref]` ... `[ref]: https://example.com`
- Wrap long lines at 100 characters. Exceptions: URLs, code blocks, tables.
- Use `inline code` for: file names, commands, env vars, code identifiers.
- Use **bold** for emphasis, *italics* for secondary emphasis.
- Never use bold and italics together (`***not this***`).

**Code Blocks:**

- Always specify a language for syntax highlighting: ` ```python ` not ` ``` `
- Use ` ```text ` or ` ``` ` (no language) for plain text output, logs, etc.
- Show both the command and its output when demonstrating CLI usage:
  ````markdown
  ```bash
  $ npm test
  ```
  ```text
  ✓ 42 tests passed
  ```
  ````

**Tables:**

- Use tables only for reference data, not for layout.
- Keep tables under 10 columns. Wider tables are unreadable.
- Align columns for readability in source:
  ```markdown
  | Column A | Column B | Column C |
  |----------|----------|----------|
  | value    | value    | value    |
  ```

**Links:**

- Use descriptive link text: "See the [Authentication Guide](auth.md)" not
  "Click [here](auth.md)"
- Always use relative links for internal files (within the repo)
- Always use absolute URLs for external references
- For Discord/Slack delivery: wrap multiple links in `<>` to suppress embeds

**Images & Diagrams:**

- Prefer Mermaid for diagrams (renders natively on GitHub):
  ````markdown
  ```mermaid
  graph TD
    A[Client] --> B[API Gateway]
    B --> C[Service]
  ```
  ````
- If Mermaid can't express it, use a diagram tool (Excalidraw, draw.io) and
  embed as an image. Always include alt text.

---

## Documentation Auditing

Regularly audit documentation for three dimensions: **completeness**,
**accuracy**, and **freshness**.

### Completeness Audit

Does documentation exist for everything that needs it?

1. List every service/module in the codebase
2. For each, check: README? API docs? Runbook? ADRs for key decisions?
3. Identify gaps and prioritize by business criticality
4. Create tickets for missing documentation

### Accuracy Audit

Is the documentation correct?

1. For each runbook: execute the diagnostic commands. Do they still work? Is
   the output what's documented?
2. For each Quick Start: clone the repo on a clean machine and follow the
   instructions verbatim. If it fails, the docs are wrong.
3. For API docs: diff the OpenAPI spec against actual endpoint behavior.
   Test every documented endpoint.
4. For config docs: diff documented env vars against actual usage in code.

### Freshness Audit

Is the documentation current?

1. Check the `last_updated` date on every document (add a date footer if
   documents don't have one)
2. Flag any document older than its review interval
3. For ADRs: check that accepted ADRs haven't been implicitly superseded
   (code changed, ADR didn't)
4. For agent context files: diff against actual project structure. Have new
   modules, patterns, or conventions emerged since the last update?

**Audit Report Format:**

```markdown
# Documentation Audit: <Project> — <Date>

## Summary
- Documents audited: N
- Complete: N | Accurate: N | Fresh: N
- Critical findings: N | Major: N | Minor: N

## Critical Findings 🔴
- **<file>**: <issue> — <fix recommendation>

## Major Findings 🟠
- **<file>**: <issue> — <fix recommendation>

## Minor Findings 🟡
- **<file>**: <issue> — <fix recommendation>

## Recommendations
<prioritized list of actions>
```

---

## Common Pitfalls & Anti-Patterns

### ❌ Documentation Anti-Patterns

1. **Writing docs that explain *how* without *why*** — A README that says
   "Run `npm start`" without explaining what the project does is useless.
   Lead with purpose, then procedure.

2. **Duplicating information across documents** — The same setup instructions
   in README.md, CONTRIBUTING.md, and docs/setup.md. Pick one canonical
   location and link to it from others.

3. **Writing documentation as an afterthought** — "I'll document it after the
   release." No you won't. Documentation must be part of the definition of
   done, not a separate task.

4. **Using documentation as a substitute for clean code** — If your code
   needs 200 lines of docs to explain, the code might be the problem.
   Documentation supplements clarity; it doesn't replace it.

5. **One-person documentation** — If only one person can maintain the docs,
   they will rot when that person leaves. Distribute documentation ownership
   across the team.

6. **Writing for yourself, not your audience** — A README written by the
   author for the author. Assume the reader knows nothing about your project.
   Define acronyms. Explain concepts. Provide context.

7. **Screenshots without alt text or descriptions** — Screenshots go stale
   faster than text. If you use them, describe what they show in alt text so
   the description survives even when the screenshot doesn't.

8. **Treating ADRs as heavyweight RFCs** — ADRs should be 1-2 pages. If it
   takes a week to write, it's an RFC, not an ADR. ADRs capture decisions
   that have already been discussed. RFCs propose decisions for discussion.

9. **Including credentials, tokens, or secrets in documentation** — Even in
   examples. Use placeholders like `<YOUR_API_KEY>` or env var references.
   See Safety Rules below.

10. **Neglecting agent-facing documentation** — AI agents are now part of the
    development team. If your project has conventions, constraints, and
    patterns that agents should follow, document them in AGENTS.md.

### ✅ Documentation Quality Checklist

Before publishing any document, verify:

- [ ] The first paragraph answers "what is this and why should I care?"
- [ ] Copy-paste-able commands actually work when copy-pasted
- [ ] No hardcoded credentials, tokens, or internal IPs
- [ ] Links are not broken (test them)
- [ ] Code blocks have language specifiers
- [ ] File is under 500 lines (split longer docs into multiple files)
- [ ] The target audience is clear (new user? API consumer? on-call engineer?)
- [ ] Date or version information is present
- [ ] Acronyms are expanded on first use
- [ ] Cross-references use relative links (within repo) or absolute URLs
      (external)

---

## Safety Rules

**ABSOLUTE RULES — never violate these:**

1. **Never document credentials, secrets, API keys, tokens, or passwords.**
   Use placeholders: `<YOUR_API_KEY>`, `$DATABASE_URL`, `<REDACTED>`. Even in
   examples. Even in "non-production" contexts. Secrets in docs leak — through
   copy-paste, screenshots, search indexing, and agent context windows.

2. **Never document internal network details publicly.** Private IPs
   (`10.x.x.x`, `192.168.x.x`), internal hostnames, and VPN endpoints should
   not appear in public-facing or widely-shared documentation.

3. **Never include destructive commands without clear warnings.** If a runbook
   includes `DROP TABLE`, `DELETE FROM`, `TERMINATE`, `rm -rf`, or similar
   commands, precede them with a ⚠️ warning explaining what they destroy and
   how to verify you're targeting the right environment.

4. **Never claim documentation is "complete" without an audit.** "Our docs are
   comprehensive" is a statement of fact, not aspiration. Only make it after
   running the completeness audit.

5. **Never commit documentation changes without review.** Documentation that
   describes system behavior is as critical as code that implements it. Review
   docs with the same rigor as code.

6. **Respect the audience's time.** A 50-page onboarding guide that nobody
   reads is not documentation — it's a filing exercise. Write for skimming.
   Put the important information first. Use headers generously.

7. **Agent-facing docs must not contain instructions that violate safety
   policies.** AGENTS.md and similar files are prompts for AI agents. They
   must not instruct agents to bypass security, exfiltrate data, or ignore
   safeguards.

---

## Platform Compatibility Notes

This skill is designed to work across AI coding platforms with minor
adaptations:

| Platform | Notes |
|---|---|
| **Claude Code** | Can read entire codebase for context. Excellent for auditing and generating comprehensive docs. Use file-reading tools to gather context before writing. |
| **Codex (OpenAI)** | Good at generating structured documentation from code. Provide the code context and spec before asking for docs. |
| **Cursor** | IDE integration means docs can be generated alongside code. Use CURSOR.md for agent context. |
| **Gemini CLI** | Large context window is useful for processing entire codebases at once. Good for documentation audits. |
| **OpenClaw** | Access to multiple skills. Combine with api-design-first for API docs, git-workflow-automation for changelogs. |
| **GitHub Copilot** | Works best within IDE context. Use `.github/copilot-instructions.md` for agent context. |
| **Windsurf** | Can read workspace files natively. Use `.windsurfrules` for agent context. |
| **OpenCode** | Terminal-based with full file access. Use AGENTS.md for agent context. |

### Platform-Specific Adjustments

- **For Discord/Slack delivery**: Use bullet lists, not markdown tables. Wrap
  multiple links in `<>` to suppress embeds. Split long docs across multiple
  messages.
- **For API docs**: Prefer generating the OpenAPI spec, not just prose
  descriptions. The spec is machine-readable and can be rendered by tools.
- **For large codebases**: Audit one module at a time. Don't try to document
  everything in one session.
- **If the codebase has no existing docs**: Start with README + AGENTS.md.
  These are the two highest-leverage documents to create first.
- **For diagram generation**: Prefer Mermaid (text-based, version-controllable)
  over images. Use the diagram-maker skill if complex diagrams are needed.

---

## References

- `references/adr-template.md` — Complete ADR template with all sections
- `references/markdown-style-guide.md` — Detailed Markdown style guide
  (loaded on demand)
- `references/runbook-template.md` — Runbook template with incident
  response patterns
- `references/api-docs-checklist.md` — API documentation completeness
  checklist

---

## Verification Checklist

Before finalizing any documentation task, confirm:

- [ ] The document type is appropriate for the audience and purpose
- [ ] The first 3 sentences explain what the document covers and who it's for
- [ ] All code blocks have language specifiers and work when copy-pasted
- [ ] No credentials, secrets, or internal IPs are exposed
- [ ] Links are tested and not broken
- [ ] Cross-references use relative links where appropriate
- [ ] The document is under 500 lines (or split into multiple files if needed)
- [ ] Date or version information is included
- [ ] Acronyms are expanded on first use
- [ ] Destructive commands in runbooks have ⚠️ warnings
- [ ] If this is an agent context file, it does not contain unsafe
      instructions
- [ ] The tone is appropriate for the audience (technical but accessible)