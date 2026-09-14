---
name: "mattpocock-dev-workflows"
description: "Use when you need Matt Pocock's engineering workflow patterns: spec synthesis, deep-module design, domain modeling, two-axis code review, or disciplined bug diagnosis. A meta-skill covering five complementary sub-patterns for real engineering — not vibe coding."
version: "1.0.0"
author: "JPeetz (adapted from mattpocock/skills)"
license: "MIT"
metadata:
  hermes:
    tags: [engineering, code-review, debugging, domain-modeling, specifications, architecture, tdd, quality]
    related_skills: [test-driven-development, systematic-debugging, github-code-review, superpowers-writing-plans, superpowers-receiving-code-review]
---

# Matt Pocock Dev Workflows

A meta-skill packaging five engineering disciplines from [Matt Pocock's skills repository](https://github.com/mattpocock/skills) (130K+ stars, TypeScript expert). These skills are designed to be **small, composable, and adaptable** — they work with any model on any codebase.

## Overview

Matt Pocock built these skills to fix common failure modes with coding agents. The five sub-patterns here address five distinct failure modes:

| # | Failure Mode | Sub-Pattern | Trigger |
|---|-------------|-------------|---------|
| 1 | The agent didn't do what you wanted (misalignment) | **to-spec** | Synthesize conversation into a spec on the tracker |
| 2 | The agent builds a ball of mud (code entropy) | **codebase-design** | Design deep modules with clean interfaces |
| 3 | The agent is way too verbose (no shared language) | **domain-modeling** | Build a shared domain glossary (CONTEXT.md) |
| 4 | The code doesn't work (no feedback loops) | **diagnosing-bugs** | Disciplined 6-phase debug loop |
| 5 | You can't tell if the change is good (no review discipline) | **code-review** | Two-axis review: Standards + Spec |

Each sub-pattern can be used independently. The meta-skill routes you to the right one based on what you're trying to do.

## When to Use

Use this meta-skill when:

1. **Starting a new feature** — combine `to-spec` (capture requirements) + `domain-modeling` (establish terminology) + `codebase-design` (plan module interfaces)
2. **Bug or regression** — use `diagnosing-bugs` exclusively; don't mix patterns
3. **Reviewing code** — use `code-review` after changes are made
4. **Cleaning up architecture** — use `codebase-design` to find deepening candidates
5. **Improving agent communication** — use `domain-modeling` to build shared language

Do NOT use when:

- The codebase has no CONTEXT.md and you just need a quick fix
- You need to scaffold a project from scratch (use `app-scaffolding` instead)
- You're exploring unknown unknowns in a codebase (use `finding-unknowns` instead)
- You need to optimize model routing costs (use `model-routing-cost-optimizer` instead)

## Workflow Selection Guide

```
┌─────────────────────────────────────────────────────────────┐
│          What do you need to do?                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "Turn this conversation into a plan"                       │
│  → to-spec: synthesize spec from discussion                 │
│                                                             │
│  "Design how this module should work"                       │
│  → codebase-design: deep modules vocabulary + deepening     │
│                                                             │
│  "Build a shared language for this project"                 │
│  → domain-modeling: CONTEXT.md + ADRs                       │
│                                                             │
│  "Something is broken / slow / throwing errors"             │
│  → diagnosing-bugs: 6-phase disciplined debug loop          │
│                                                             │
│  "Review this code / PR / branch"                           │
│  → code-review: two-axis (Standards + Spec)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# Sub-Pattern 1: to-spec

Synthesize the current conversation and codebase understanding into a structured spec, then publish it to the project issue tracker. No interview — just synthesis of what you've already discussed.

## When to Use

- After a planning conversation where requirements are already clear
- Before starting implementation (feeds into `implement` workflow)
- When you need a written record of decisions before coding begins

## How to Use

1. Explore the repo to understand the current state
2. Sketch the test seams (highest possible seam; prefer existing ones)
3. Check seams with the user
4. Write spec using the template below
5. Publish to issue tracker with appropriate label

### Spec Template

```
## Problem Statement
The problem from the user's perspective.

## Solution
The solution from the user's perspective.

## User Stories
1. As an <actor>, I want a <feature>, so that <benefit>
2. ...

## Implementation Decisions
- Modules to build/modify
- Module interfaces
- Technical clarifications
- Architectural decisions
- Schema changes
- API contracts

Do NOT include specific file paths or code snippets (except prototype-
validated state machines, reducers, schemas, or type shapes).

## Testing Decisions
- What makes a good test (external behavior, not implementation)
- Which modules will be tested
- Prior art (similar tests in the codebase)

## Out of Scope

## Further Notes
```

---

# Sub-Pattern 2: codebase-design

Shared vocabulary and discipline for designing **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface.

## When to Use

- Designing a new module's public API
- Refactoring a shallow module into a deeper one
- Deciding where a seam should go
- Making code more testable or AI-navigable

## Glossary (Use these terms exactly)

| Term | Definition | Avoid |
|------|-----------|-------|
| **Module** | Anything with an interface and implementation (function, class, package, tier-spanning slice) | unit, component, service |
| **Interface** | Everything a caller must know: type signature, invariants, ordering, error modes, config, perf | API, signature |
| **Implementation** | What's inside a module | — |
| **Depth** | Leverage at the interface: behaviour per unit of interface a caller must learn | — |
| **Seam** (Feathers) | Where behaviour can be altered without editing in that place | boundary |
| **Adapter** | Concrete thing that satisfies an interface at a seam | — |
| **Leverage** | Capability per unit of interface | — |
| **Locality** | Change/knowledge/verification concentrated in one place | — |

## Deep vs Shallow

**Deep module** = small interface + lots of implementation (desired).  
**Shallow module** = large interface + little implementation (avoid).

When designing an interface, ask:
- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

### Principles

1. **Depth is a property of the interface, not the implementation.** Internal seams are fine; they stay private.
2. **The deletion test.** If the module vanishes, does complexity reappear across N callers? If yes, it earns its keep.
3. **The interface is the test surface.** Callers and tests cross the same seam.
4. **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a seam unless something varies across it.

### Designing for Testability

1. Accept dependencies, don't create them
2. Return results, don't produce side effects
3. Small surface area = fewer tests needed

### Deepening Process (from DEEPENING.md)

Classify dependencies:
- **In-process**: pure computation, no I/O — always deepenable
- **Local-substitutable**: has local test stand-in (PGLite, in-memory FS)
- **Remote but owned** (Ports & Adapters): define a port, inject adapters
- **True external** (Mock): third-party services, inject mock adapters

Seam discipline:
- Internal vs external seams — don't expose internal seams just because tests use them
- Replace, don't layer: old unit tests on shallow modules become waste; delete them

### Design It Twice (from DESIGN-IT-TWICE.md)

When designing alternative interfaces:
1. Frame the problem space (constraints, dependencies, code sketch)
2. Spawn 3+ sub-agents in parallel, each with a different design constraint:
   - Agent 1: Minimize interface (1-3 entry points, max leverage)
   - Agent 2: Maximize flexibility
   - Agent 3: Optimize for the most common caller
   - Agent 4 (optional): Ports & adapters design
3. Present designs sequentially, compare by depth, locality, seam placement
4. Give a strong opinionated recommendation or hybrid

---

# Sub-Pattern 3: domain-modeling

Actively build and sharpen the project's domain model. Challenge terms against the glossary, stress-test with edge-case scenarios, and update CONTEXT.md and ADRs inline.

## When to Use

- Discussing codebase terminology that feels fuzzy or overloaded
- Writing or editing a CONTEXT.md glossary
- Recording or editing an ADR for a non-trivial decision
- When the agent uses 20 words where 1 will do (shared language concision)

## How to Use

### File Structure (Single Context)
```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

### File Structure (Multiple Contexts)
```
/
├── CONTEXT-MAP.md
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

### Active Discipline

1. **Challenge against the glossary** — When the user uses a term that conflicts with existing language in CONTEXT.md, call it out immediately
2. **Sharpen fuzzy language** — Propose precise canonical terms for vague/overloaded ones
3. **Stress-test with concrete scenarios** — Invent edge-case scenarios that force precision about boundaries between concepts
4. **Cross-reference with code** — When the user states how something works, check whether the code agrees
5. **Update CONTEXT.md inline** — Capture resolved terms immediately, not batched at the end
6. **Offer ADRs sparingly** — Only when ALL three are true:
   - Hard to reverse
   - Surprising without context
   - Result of a real trade-off

### CONTEXT.md Format

```markdown
# {Context Name}

{One or two sentence description}

## Language

**Term**:
{One or two sentence definition}
_Avoid_: Synonymous terms

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

Rules:
- Be opinionated: pick the best term, list others under `_Avoid_`
- Keep definitions tight: one or two sentences
- Only include project-specific concepts, not general programming ones
- Group under subheadings when natural clusters emerge

### ADR Format

```markdown
# {Short title of the decision}

{1-3 sentences: context, decision, and why.}
```

An ADR can be a single paragraph. Optional sections (use sparingly): Status frontmatter, Considered Options, Consequences.

---

# Sub-Pattern 4: code-review

Two-axis review of the diff between HEAD and a fixed point the user supplies. Both axes run as parallel sub-agents so they don't pollute each other's context.

## When to Use

- Reviewing a branch or PR before merge
- Reviewing work-in-progress changes
- When the user asks "review since X" (commit, tag, branch, merge-base)
- After implementation is complete, before commit

## How to Use

### 1. Pin the fixed point

Capture: `git diff <fixed-point>...HEAD` (three-dot) and `git log <fixed-point>..HEAD --oneline`

Confirm the ref resolves and the diff is non-empty.

### 2. Identify the spec source

Order of precedence:
1. Issue references in commit messages (#123, Closes #45)
2. A path the user passed as argument
3. A spec file under docs/, specs/, or .scratch/ matching the branch name
4. Ask the user; if none exists, Spec sub-agent reports "no spec available"

### 3. Identify the standards sources

Anything in the repo that documents how code should be written (CODING_STANDARDS.md, CONTRIBUTING.md). Plus the **smell baseline** below.

### Smell Baseline (Fowler, Refactoring ch.3)

Each smell is a labelled heuristic, never a hard violation. Documented repo standards override the baseline.

- **Mysterious Name** — rename; if no honest name comes, design is murky
- **Duplicated Code** — extract shared shape
- **Feature Envy** — move method onto the data it envies
- **Data Clumps** — bundle travelling fields into one type
- **Primitive Obsession** — give domain concepts their own type
- **Repeated Switches** — replace with polymorphism or a shared map
- **Shotgun Surgery** — gather scattered edits into one module
- **Divergent Change** — split so each module changes for one reason
- **Speculative Generality** — delete abstractions added for needs the spec doesn't have
- **Message Chains** — hide the walk behind one method on the first object
- **Middle Man** — cut the delegator, call the real target direct
- **Refused Bequest** — drop inheritance, use composition

### 4. Spawn both sub-agents in parallel

**Standards sub-agent**: full diff + standards sources + smell baseline. Report per file/hunk: (a) violations citing the standard, (b) baseline smells. Distinguish hard violations from judgement calls. Under 400 words.

**Spec sub-agent**: diff + spec contents. Report: (a) missing requirements, (b) scope creep, (c) wrong-looking implementations. Quote the spec line for each. Under 400 words.

### 5. Aggregate

Present under `## Standards` and `## Spec` headings verbatim. End with one-line summary: total findings per axis and the worst issue within each axis. Don't merge or rerank across axes.

---

# Sub-Pattern 5: diagnosing-bugs

A disciplined 6-phase loop for hard bugs and performance regressions. Skip phases only when explicitly justified.

## When to Use

- The user says "diagnose this" or "debug this"
- Something is broken, throwing, failing, or slow
- Performance regression needs investigation

## The Six Phases

### Phase 1: Build a feedback loop

**THIS IS THE SKILL.** Everything else is mechanical. Spend disproportionate effort here.

Ways to construct one (in roughly this order):
1. Failing test at the seam that reaches the bug
2. Curl/HTTP script against a running dev server
3. CLI invocation with fixture input
4. Headless browser script (Playwright/Puppeteer)
5. Replay a captured trace (HAR, payload, event log)
6. Throwaway harness (minimal subset of system)
7. Property/fuzz loop (1000 random inputs)
8. Bisection harness (git bisect run -able)
9. Differential loop (old vs new version)
10. HITL bash script (last resort)

**Tighten the loop**: faster, sharper signal, more deterministic.
**Non-deterministic bugs**: aim for higher reproduction rate (50% is debuggable; 1% is not).

Completion criteria — the loop is:
- [ ] **Red-capable**: asserts the user's exact symptom
- [ ] **Deterministic**: same verdict every run
- [ ] **Fast**: seconds not minutes
- [ ] **Agent-runnable**: you can run it unattended

### Phase 2: Reproduce + minimise

Run the loop. Confirm it reproduces the user's symptom. Then shrink the repro to the **smallest scenario that still goes red** — cut inputs, callers, config, data one at a time. Done when every remaining element is load-bearing.

### Phase 3: Hypothesise

Generate 3-5 ranked falsifiable hypotheses before testing any. Each must state a prediction: "If X is the cause, then changing Y will make the bug disappear."

Show the ranked list to the user before testing (cheap checkpoint).

### Phase 4: Instrument

Test predictions by changing one variable at a time. Tool preference:
1. Debugger/REPL inspection
2. Targeted logs at boundary points (tag each with a unique prefix like `[DEBUG-a4f2]`)
3. Never "log everything and grep"

For performance regressions: establish a baseline measurement first, then bisect.

### Phase 5: Fix + regression test

Write the regression test BEFORE the fix, but only at a correct seam. If no correct seam exists, flag the architecture issue.

1. Turn minimised repro into failing test at that seam
2. Watch it fail
3. Apply the fix
4. Watch it pass
5. Re-run the Phase 1 feedback loop against the original scenario

### Phase 6: Cleanup

- [ ] Original repro no longer reproduces
- [ ] Regression test passes (or absence of seam documented)
- [ ] All `[DEBUG-...]` instrumentation removed
- [ ] Throwaway prototypes deleted or moved
- [ ] Correct hypothesis stated in commit/PR message

### Redact Secrets

Every time you show commands, outputs, or captured artifacts: **redact every secret first**. Write `<REDACTED>` in place. Build loops against env vars, so credentials stay in the environment rather than in what you show.

## Pitfalls

### to-spec
- Interviewing the user when they asked for synthesis — DON'T interview, just synthesise what's been discussed
- Including file paths and code snippets that will become outdated quickly
- Missing the "Out of Scope" section — it's as important as what's in scope

### codebase-design
- Introducing seams without two adapters (premature abstraction)
- Using "boundary" instead of "seam" (conflicts with DDD)
- Testing past the interface — tests should survive internal refactors
- Exposing internal seams through the public interface just because tests use them

### domain-modeling
- Including general programming concepts in CONTEXT.md (only project-specific terms)
- Using CONTEXT.md as a spec or scratch pad — it is a glossary and nothing else
- Creating ADRs for easily-reversible decisions (wasteful)
- Adding implementation details to CONTEXT.md

### code-review
- Merging or reranking findings from the two axes — they are deliberately separate
- Missing the spec source and proceeding without it
- Forgetting the smell baseline when the repo documents no standards

### diagnosing-bugs
- Jumping straight to a hypothesis before building a red-capable feedback loop
- Proceeding to hypothesise without a tight loop
- Logging everything and grepping instead of targeted instrumentation
- Fixing without a regression test at a correct seam
- Leaving tagged debug logs (`[DEBUG-...]`) in the codebase

## Verification

Use the verification checklist for each sub-pattern:

### to-spec
- [ ] Spec has all sections: Problem, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope
- [ ] User stories cover all aspects of the feature
- [ ] No file paths or code snippets (except prototype-validated shapes)
- [ ] Test seams identified and checked with user
- [ ] Published to issue tracker with appropriate label

### codebase-design
- [ ] Interface is small (few methods, simple params)
- [ ] Module passes the deletion test
- [ ] Dependencies classified by category
- [ ] Two adapters for every introduced seam
- [ ] Adapter/interface separation correct

### domain-modeling
- [ ] CONTEXT.md updated inline with resolved terms
- [ ] Each term has a tight definition and `_Avoid_` list
- [ ] No general programming concepts in glossary
- [ ] ADRs created only for hard-to-reverse, surprising, trade-off decisions

### code-review
- [ ] Fixed point confirmed and diff non-empty
- [ ] Spec identified (or "no spec" noted)
- [ ] Standards sources identified
- [ ] Two parallel sub-agents spawned
- [ ] Findings presented under separate headings (Standards / Spec)
- [ ] No merging of findings across axes

### diagnosing-bugs
- [ ] Phase 1 loop is red-capable and has been run at least once
- [ ] Phase 2: reproduced and minimised
- [ ] Phase 3: 3-5 falsifiable hypotheses ranked before testing
- [ ] Phase 4: one variable changed at a time, tagged logs
- [ ] Phase 5: regression test before fix (at correct seam)
- [ ] Phase 6: all debug tags removed, correct hypothesis in commit message

## References

See the `references/` directory for supporting files:
- `to-spec-template.md` — Full spec template
- `context-format.md` — CONTEXT.md format rules
- `adr-format.md` — ADR format rules
- `codebase-design-glossary.md` — Expanded glossary
- `deepening.md` — Deepening process for dependency categories
- `design-it-twice.md` — Alternative interface design technique
- `code-review-smell-baseline.md` — Fowler smell baseline
- `diagnosing-bugs-phases.md` — Phase detail reference
