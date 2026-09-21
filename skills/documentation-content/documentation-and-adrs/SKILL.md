---
name: documentation-and-adrs
description: >-
  Use this skill when you need to record an architecture decision (ADR) or
  document the reasoning behind a design choice — when changing public APIs,
  shipping features that change behavior, or recording context that future
  engineers (human or agent) will need to understand the codebase. Does NOT
  replace code comments or inline docstrings; targets strategic documentation
  and decision capture. Primary keywords: ADR architecture decision record,
  technical documentation, design rationale, decision log, API documentation,
  README writing, changelog, documentation-driven development, inline
  documentation best practices, specification writing. For all major agentic
  platforms.
version: 1.0.0
author: JPeetz (based on documentation-and-adrs by addyosmani, MIT)
license: MIT
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, OpenCode, and any SKILL.md-compatible agent.
tags:
  - documentation
  - adr
  - architecture-decision-records
  - technical-writing
  - api-docs
  - readme
  - changelog
  - design-rationale
  - decision-log
  - documentation-driven-development
platforms:
  - claude-code
  - codex
  - opencode
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
  - windsurf
  - copilot
---

# Documentation and ADRs

Records decisions and documents the *why* — context, constraints, trade-offs, and rejected alternatives that code alone cannot express.

---

## Overview

Code tells you *what* was built. Documentation tells you *why* it was built that way, *what alternatives were rejected*, and *what constraints governed the decision*. The most valuable documentation captures the reasoning, not the mechanics.

This skill covers four documentation layers, from most to least strategic:

| Layer | What | When | Effort |
|-------|------|------|--------|
| **🏛️ ADRs** | Architecture Decision Records — capture *why* a decision was made | Every significant architectural choice | 10-30 min |
| **📘 README** | Project entry point — what, why, how | New projects, major releases | 15-60 min |
| **🔌 API Docs** | Endpoint/schema documentation | Every public API change | Per-endpoint |
| **📝 Inline Docs** | Comments explaining *why*, not *what* | Continuously | Seconds |

**Core principle: document decisions, not mechanics.** A comment explaining *why* a rate limit uses a sliding window is valuable. A comment that says `// Increment counter by 1` above `counter += 1` is noise.

---

## When to Use

- Making a significant architectural decision (framework, database, protocol, infra)
- Choosing between competing approaches with meaningful trade-offs
- Adding or changing a public API
- Shipping a feature that changes user-facing behavior
- Onboarding new team members (or agents) — they need the *why*, not just the code
- When you find yourself explaining the same thing repeatedly — write it down once
- Any decision you expect someone to question in 6 months

### Do NOT Use For

- **Obvious code**: `// Increment counter` above `counter++` — restates the code
- **Throwaway prototypes** that will be deleted in days
- **Code-level docstrings** — those belong in the code, not in separate docs
- **Tutorials or blog posts** — instructional content is not technical documentation
- **Legal documents** — privacy policies, terms of service
- **Marketing materials** — landing pages, product brochures

---

## Process: Documentation-Driven Development

Write documentation *before* code — it forces clarity and surfaces assumptions early.

### Step 1 — Write the ADR First

Before making a significant architectural decision:

1. Identify the decision drivers — what's the problem, what forces are at play?
2. List at least 2-3 viable alternatives including "do nothing"
3. Evaluate each: pros, cons, risks, opportunity cost
4. State the decision and the single most important reason for it
5. Log the consequences — positive AND negative (accept the trade-offs)

Best practice: 10 minutes writing an ADR prevents a 2-hour re-litigation debate later.

### Step 2 — Write README / API Docs Before Implementation

1. Draft the README from the user's perspective — if you can't describe what the system does in prose, you can't code it
2. Write the OpenAPI spec before implementing endpoints — review the contract with consumers first
3. Update the changelog entry as part of every PR — no merged PR without one

### Step 3 — Add Inline Docs During Implementation

Comment the *why*, not the *what*:

- **Bad**: `// Fetch user by ID` above `db.users.findById(id)`
- **Good**: `// Use findById instead of findOne because user IDs are unique and a missing user should throw, not return null`

### Step 4 — Verify

Run the verification checklist below before closing any documentation task.

---

## ADR Template (Progressive)

Start minimal; add depth only when the decision warrants it.

### Minimal ADR (for quick, low-risk decisions)

```
# ADR-NNNN: [Title]

## Status
[proposed | accepted | superseded by ADR-NNNN | deprecated]

## Context
[Problem and constraints — 2-3 sentences]

## Decision
[What we decided, in one sentence]

## Rationale
[Why this over alternatives — 2-3 sentences]

## Consequences
[What this means going forward — 1-2 bullet points]
```

### Full ADR (for significant decisions with lasting impact)

For complex decisions, use the template in `references/adr-template.md` which includes: Context and Problem Statement, Decision Drivers, Considered Options with detailed pros/cons, Decision Outcome with positive/negative consequences and mitigations, Implementation Plan, and Links.

### ADR Lifecycle

```
PROPOSED → ACCEPTED → (SUPERSEDED by ADR-NNNN or DEPRECATED)
```

- Never delete ADRs. When a decision changes, write a new ADR that supersedes the old one.
- Rejected ADRs are still valuable — they prevent re-litigating the same question.

### When to Write an ADR

- Choosing a framework, library, or major dependency
- Designing a data model or database schema
- Selecting an authentication strategy
- Deciding on an API architecture (REST vs GraphQL vs tRPC)
- Choosing between build tools, hosting platforms, or infrastructure
- Any decision that would be expensive to reverse

---

## Documentation Layers in Detail

### README Structure

Every README must answer, in order:

| Section | Content |
|---------|---------|
| **Title + description** | One-line: what it does and why someone cares |
| **Quick Start** | Copy-paste-able commands that work. If it takes >2 minutes or >5 commands, simplify |
| **Installation** | Prerequisites first, then per-platform instructions |
| **Usage** | Common use cases with code examples. Link to full API docs |
| **Configuration** | All options with defaults, descriptions, env var equivalents |
| **Architecture** | High-level — how pieces fit. Link to ADRs |
| **Contributing** | Dev setup, tests, how to submit changes |
| **License** | Name + link to LICENSE |

### API Documentation

- **REST**: Use OpenAPI 3.1 as the canonical spec — generate human-readable docs from it. Document method, path, parameters, auth, request/response examples, errors, rate limits
- **GraphQL**: Use schema introspection. Every type, field, and mutation must have a description in the schema itself
- **Never** maintain API docs and API specs separately — they will diverge

### Inline Documentation

- Comment invariants, gotchas, and non-obvious constraints — not what the code does
- Document the *reason* for a non-obvious approach, not the approach itself
- If you need >3 lines of comment to explain a block, extract it into a well-named function

### Changelogs

Follow [Keep a Changelog](https://keepachangelog.com/) format with `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security` sections. Never use a catch-all "Misc" category. Include diff links at the bottom.

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The code is self-documenting" | Code shows *what*, not *why*, what alternatives were rejected, or what constraints governed the decision. |
| "We'll write docs when the API stabilizes" | APIs stabilize faster when you document them — writing the spec forces you to think about the contract. |
| "Nobody reads docs" | Agents do. Future engineers do. Your future self in 6 months does. Stale docs cost more than missing docs — they actively mislead. |
| "ADRs are overhead" | A 10-minute ADR prevents a 2-hour debate later. Even rejected ADRs pay off — they prevent re-litigation. |
| "We'll remember why we chose this" | No, you won't. Two months later, the constraints that drove the decision are gone and the choice looks arbitrary. |
| "Writing docs slows us down" | Wrong framing. Docs *accelerate* by reducing re-explanation, onboarding time, and miscommunication. |
| "Our team is small, we don't need docs" | Small teams *especially* need docs — one person leaves and the context leaves with them. |
| "We can generate docs from code" | Tools can generate API references from code. They cannot generate *rationale*, *context*, or *rejected alternatives*. |

---

## Red Flags

- **Architectural decisions with no written rationale** — if the team can't point to an ADR for a major choice, that choice is undocumented
- **Public APIs with no documentation** — consumers can't integrate without guessing
- **No ADRs in a project with significant choices** — no ADR for a database choice, auth strategy, framework selection
- **Documentation that restates code instead of explaining intent** — `// Increment counter by 1` is worse than no comment (it's visual noise)
- **Stale documentation that contradicts code** — actively misleading; worse than missing docs
- **A single person owns all the documentation** — when they leave, the knowledge leaves
- **ADRs that list options but skip the rationale** — "we chose PostgreSQL" without explaining why not MySQL, CockroachDB, SQLite, etc.
- **Changelog entries that mirror git log** — "Fixed bug" is not a changelog entry; "Fixed race condition in payment processing (#1234)" is

---

## Verification

Before completing any documentation task:

- [ ] ADRs exist for all significant architectural decisions
- [ ] README covers quick start, commands, and architecture overview
- [ ] API functions have parameter and return type documentation
- [ ] Known gotchas are documented inline where they matter, not restating the code
- [ ] No commented-out code remains
- [ ] No hardcoded credentials, tokens, or internal IPs in any doc
- [ ] Links are tested and work (relative links for internal, absolute URLs for external)
- [ ] Code blocks have language specifiers and produce correct output when run
- [ ] The document answers *why* (rationale/context), not just *what* (mechanics)
- [ ] Acronyms are expanded on first use
- [ ] Architecture decisions list the alternatives considered and the reason for rejection
- [ ] Old ADRs are never deleted — superseded ADRs get a status update and link to the new one
- [ ] The changelog entry is written as part of the PR, not after merge
- [ ] One person is not the sole owner of documentation — ownership is distributed

---

## References

- `references/adr-template.md` — Full ADR template with decision drivers, considered options, mitigations, and implementation plan
- `references/readme-template.md` — README structure template
- `references/api-docs-checklist.md` — API documentation completeness checklist

---

## Platform Compatibility Notes

| Platform | Notes |
|----------|-------|
| **Claude Code** | Can read entire codebase for context. Use file-reading tools before writing ADRs or auditing docs. |
| **Codex (OpenAI)** | Strong at generating structured docs from code. Provide code context first. |
| **OpenClaw / Hermes** | Combine with spec-writer for documentation-driven development workflows. Use changelog maintenance as part of PR lifecycle. |
| **Cursor / Windsurf** | IDE integration — generate docs alongside code. Use `.cursorrules` or `.windsurfrules` for agent context. |
| **GitHub Copilot** | Works best within IDE. Use `.github/copilot-instructions.md` for agent context. |