---
name: spec-writer
description: >
  Use this skill when a vague feature request, ticket, PRD fragment, or rough idea
  needs to be turned into a structured specification, technical plan, and ordered
  task breakdown for AI coding agents. Generates all three output sections
  immediately, then flags every implicit decision as an inline [ASSUMPTION: ...]
  marker with an impact rating and correction guidance — no back-and-forth
  questions needed before drafting. Primary keywords: spec-driven development
  SDD, feature specification generation, technical planning, task breakdown,
  assumption flagging, acceptance criteria Given When Then, requirements
  engineering, feature request refinement, specification writing agent,
  plan-first development. For all major agentic platforms.
version: 1.0.0
author: JPeetz (based on spec-writer by dannwaneri)
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, OpenCode, and any SKILL.md-compatible agent.
tags:
  - spec-writing
  - technical-planning
  - task-breakdown
  - requirements-engineering
  - spec-driven-development
  - sdd
  - feature-specification
  - assumption-tracking
  - acceptance-criteria
  - plan-first
  - documentation
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

# Spec Writer

Turns a vague feature request into a structured spec, technical plan, and task breakdown — ready for any coding agent to implement without guessing.

---

## Overview

AI coding agents don't fail because the model is weak. They fail because the instructions are ambiguous. This skill closes that gap **before** the agent starts.

Given any feature description — a sentence, a ticket, a PRD fragment, a rough idea — spec-writer produces three deliverables in a single output:

1. **A Spec** — functional, technology-agnostic. What the feature does, who uses it, what must be true, what can go wrong, and binary acceptance criteria in Given/When/Then format.
2. **A Plan** — technical and concrete. Architecture decisions, data model changes, API contracts, testing strategy, security constraints.
3. **A Task breakdown** — ordered, self-contained tasks. Each completable in a single agent session. Each with its own acceptance criteria.

The key methodology: **generate first, flag assumptions inline**. Instead of asking clarifying questions before drafting, the skill produces a complete output and marks every decision made without user input as `[ASSUMPTION: ...]` — impact-rated, with guidance on when to correct it.

---

## When to Use

- A stakeholder or user sends a vague feature request ("add export", "build a dashboard", "let users invite teammates")
- You have a Jira ticket, Linear issue, or GitHub issue that says *what* but not *how*, and needs decomposing into agent-ready work
- You need to validate scope and surface hidden assumptions before implementation starts
- You're handing work to another agent or developer and want to eliminate ambiguity
- You want acceptance criteria that are **binary pass/fail**, not "works correctly"
- You need a plan-first methodology for Spec Driven Development (SDD)

Do **not** use this skill when:
- The requirements are already a complete, unambiguous spec with acceptance criteria
- You need a quick one-line answer rather than a structured document
- You're asking a question rather than requesting a feature

---

## How to Invoke

```
/spec-writer [feature description]
```

Pass anything — a feature description, a ticket, a PRD fragment, a rough idea:

```
/spec-writer Add password reset via email
/spec-writer Build an admin dashboard showing daily active users
/spec-writer Let users invite teammates to their workspace
/spec-writer Add rate limiting to the public API
```

The skill produces a complete spec, plan, and task breakdown in one shot. No intermediate questions.

---

## Output Format

The output is a single document with three sections, each clearly delimited:

### Spec Section

The Spec section contains:

- **Purpose** — one or two sentences describing the feature's goal
- **Use case(s)** — who uses this feature and what they accomplish
- **Functional requirements** — what the system must do (numbered)
- **Non-functional requirements** — performance, security, compliance constraints
- **Acceptance criteria** — binary Given/When/Then scenarios
- **Edge cases** — what happens at boundaries, with empty states, with errors

### Plan Section

The Plan section contains:

- **Architecture decisions** — components, interactions, data flow
- **Data model changes** — new/modified entities, fields, relationships
- **API contracts** — endpoints, methods, request/response shapes
- **UI changes** — components, states, navigation flow
- **Testing strategy** — unit, integration, E2E coverage requirements
- **Security & performance constraints** — auth, rate limiting, caching, SLAs

### Task Breakdown Section

The Task breakdown section contains:

- A numbered list of **ordered, self-contained tasks**, each with:
  - **Dependencies** — which tasks must complete first
  - **Acceptance criteria** — binary pass/fail conditions unique to that task
  - **Estimated complexity** — (small / medium / large)
- No task says "implement the feature" — every task is independently verifiable

---

## Assumption Markers

Every decision the skill makes without explicit user input is marked inline with an `[ASSUMPTION: ...]` annotation:

```
When the export contains more than 1,000 rows
  [ASSUMPTION: async for large exports — Impact: HIGH]
Then the export is generated asynchronously and the user is notified by email
```

At the end of the output, all assumptions are collected into a prioritized summary:

```
## Assumptions to Review
1. Async generation for exports over 1,000 rows — Impact: HIGH
   Correct this if: your order volumes are low and synchronous is fine
2. Date range filter is required — Impact: MEDIUM
   Correct this if: the first version should export all orders with no filtering
```

### Assumption Impact Levels

| Impact | Meaning |
|--------|---------|
| **HIGH** | Changing this assumption could significantly alter the architecture or effort |
| **MEDIUM** | Changing this assumption would affect the design but not the overall approach |
| **LOW** | Changing this assumption is a minor adjustment with no architectural impact |

---

## Common Pitfalls

1. **Over-specifying technology in the Spec section.** The Spec must remain technology-agnostic. Framework choices, database decisions, and library selections belong in the Plan section only.
2. **Acceptance criteria that aren't binary.** "Works correctly" is not a criterion. "Returns 401 when unauthenticated" is. Every criterion must be testable as pass/fail.
3. **Tasks that are too large.** If a task's acceptance criteria read like a mini-spec, break it down further. Every task should be completable in a single agent session.
4. **Missing edge cases.** Always include empty states, error states, boundary conditions (pagination limits, max file size, timeout duration), and concurrent access.
5. **Skipping the assumptions review.** The generated assumptions are a feature, not a bug. Always explicitly review and either confirm or override each HIGH/MEDIUM assumption before handing the output to an implementer.
6. **Mixing spec with plan details.** If an acceptance criterion mentions a specific library or framework, it belongs in the Plan. Keep the Spec pure functional requirements.
7. **No non-functional requirements.** Storage limits, latency targets, concurrency expectations, and accessibility requirements are often assumed but must be explicit.

---

## Verification

After generating the output, verify the following before considering it complete:

- [ ] **Every [ASSUMPTION] marker is impact-rated** — HIGH, MEDIUM, or LOW — with correction guidance
- [ ] **Assumptions are collected** into a single summary section at the end
- [ ] **Spec is technology-agnostic** — no framework, library, or infrastructure choices in functional requirements or acceptance criteria
- [ ] **Acceptance criteria are binary** — every scenario is a clear Given/When/Then that can pass or fail
- [ ] **Plan contains concrete decisions** — architecture, data model, API contracts, testing strategy
- [ ] **Tasks are self-contained** — each has unique acceptance criteria and clear dependencies
- [ ] **No task says "implement the feature"** — the largest task should be implementable in a single agent session
- [ ] **Edge cases are covered** — empty states, error states, boundary conditions, concurrent access
- [ ] **Non-functional requirements are present** — performance, security, storage, latency