---
name: repo-recon
description: >
  Use this skill when you need to map an unfamiliar codebase before changing
  anything. Runs a systematic five-step recon pass — read the map, learn the
  commands, trace one flow end-to-end, note conventions then match them, and
  write it down — so you understand architecture, build/test commands, and
  code conventions before making a single edit. Prevents broken builds,
  misfiled changes, and convention-violating PRs caused by search-before-
  assuming. Activates on "where do I start", "understand this codebase",
  "how do I build/test this", "what are the conventions here", and first-time
  work in any repository.
version: 1.0.0
author: JPeetz
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - codebase-navigation
  - code-reading
  - onboarding
  - repository-analysis
  - code-quality
  - conventions
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
---

# Repo Recon

Systematically map an unfamiliar codebase before changing anything. The recon
pass is a short, bounded sequence — minutes, not hours — that front-loads the
understanding you would otherwise pay for painfully later in broken builds,
rejected PRs, and rewrites. It is the "before" half of every safe edit.

## Overview

Reconnaissance is cheap; guessing is expensive. Before you touch a single
line, spend a few minutes answering five questions:

1. What is this repo and how is it laid out?
2. How do I build, test, and run it?
3. Where does one real flow live, and how does it work end-to-end?
4. What conventions must my code match?
5. Where did I write all of this down?

The five-step pass below answers them in order. The output is a written
recon note: a map, a command cheat-sheet, one traced flow, and a convention
list. That note is the deliverable — not code changes.

## When to Use

Use this skill when:

- You are working in a repository for the first time.
- You are returning to a repo after a long absence (memory is stale).
- The codebase is large, old, or has no documentation.
- You must make a change that crosses module boundaries (new feature,
  refactor, migration, or a bug whose cause is unknown).
- You are reviewing or extending code written by someone else.
- You need to give another agent or teammate a fast, accurate orientation.

Do NOT use it when:

- The change is a one-liner in a self-contained script — the "map" is the
  file itself.
- You already hold the map, commands, and conventions in working notes from
  a recent pass (recon fresh, not ritual).

## The Recon Pass

Five steps, in order. Each step ends with a concrete output to record.

### Step 1 — Read the map

Grok the shape of the repo before reading any implementation.

- Read `README`, `ARCHITECTURE`, `docs/`, and any ADRs first.
- List the top-level directory tree; identify entry points (`main`,
  `index`, `server`, CLI entry, worker, `App` component).
- Skim the manifest: `package.json`, `pyproject.toml`, `go.mod`,
  `Cargo.toml`, `composer.json`, `Gemfile`, `pom.xml`, etc. — it names the
  real dependencies and scripts.
- Note what the repo is NOT (no tests? no docs? monorepo? library vs app?).

**Output:** a one-paragraph mental model: *"This is a FastAPI service that
ingests webhooks, transforms them into events, and writes them to
Postgres. Entry point is `app/main.py`; it has no test suite."*

### Step 2 — Learn the commands

Find the exact commands before running anything guessed.

- Check `README`/`CONTRIBUTING`, `Makefile`, `Justfile`, `Taskfile`, and
  the package-manifest `scripts` block.
- Identify: install, build, test, lint, and run/dev commands.
- Verify at least one command end-to-end (usually the test suite, or build
  if tests are slow). A command that "should work" is not a command that
  works.

**Output:** a cheat-sheet of verified commands with their working directory:

```
npm install && npm test        # from repo root
uv run pytest tests/ -x        # fast subset for iteration
```

### Step 3 — Trace one flow end-to-end

Pick ONE representative flow (a user-facing feature, a request lifecycle, a
job) and follow it from entry point to output, database, or side effect.

- Jump from call site to definition with search; read the actual code.
- Note file:line anchors for each hop.
- One flow is enough for reconnaissance — do not trace three.

**Output:** a written trace, e.g.:

```
POST /orders -> app/routes/orders.py:12 -> OrderService.create() (services/orders.py:41)
  -> validates via schemas/order.py -> writes Order (models/order.py:88)
  -> enqueues email job (jobs/email.py:30)
```

### Step 4 — Note conventions, then match them

Identity the local style and follow it, even when you would write it
differently. Your taste is not the repo's law.

- Naming: `snake_case`? `camelCase`? prefixes? file-per-class?
- Structure: where do errors get handled? Where do types/schemas live?
- Testing style: unit vs integration, framework, test-file placement.
- Error handling and logging patterns; commit/PR style if visible.

**Output:** a short convention list you will consciously match on every edit.

### Step 5 — Write it down

Commit the recon to durable notes, not memory.

- Write `RECON.md` at the repo root (or `.gitignore` it) for team/other-agent
  reuse, or keep a session note if the repo is private and throwaway.
- Include: the map paragraph, verified commands, the flow trace, the
  convention list, and any open questions.
- If your recon uncovered a TODO or landmine, record it here — do not fix it
  yet (see Cross-reference).

**Output:** the file you (or the next agent) will read to skip this pass next
time.

## Standing Rules

1. **Search before assuming.** Never assume a helper, pattern, or file
   exists — grep for it first. The cost of one `rg` is trivial; the cost of
   a wrong assumption is a broken build.
2. **Verify before believing.** Reading the README is not understanding the
   code. Confirm claims against the actual sources and a real command run.
3. **Do not change code during recon.** No drive-by fixes, no refactors, no
   "quick improvements." During the pass, code is read-only; your only
   artifact is the recon note.
4. **Match, don't impose.** When local convention conflicts with your
   preference, the convention wins.
5. **Read the file you are about to modify** — fully, not just the hunks
   around your edit.
6. **Ask when the map contradicts reality.** If docs say X and code does Y,
   trust code, flag the drift, and ask if the intended behavior is X or Y.

## Definition of Done

The recon pass is complete when you can answer all five questions from the
overview, and the answers are written down:

- [ ] One-paragraph map: what the repo does and its top-level structure.
- [ ] Verified install/build/test/run commands.
- [ ] One flow traced end-to-end with file:line anchors.
- [ ] Convention list that your edits will match.
- [ ] Recon note written to disk (or session notes for throwaway repos).
- [ ] Zero source changes made during the pass.

## Common Mistakes

- **Skipping the map and diving into a random file.** You will misread
  intent and misfile changes. Read the map first, always.
- **Guessing commands instead of reading the manifest or Makefile.** A
  guessed command that half-works wastes more time than reading it.
- **Tracing too many flows.** One traced flow beats three half-traced ones;
  reconnaissance is breadth-first by design.
- **"Fixing" things you find during recon.** Resisting the drive-by fix is
  the whole point — record, defer, and let the fix clear its own review.
- **Trusting stale memory of a similar repo.** Same framework does not mean
  same conventions. Every repo gets its own pass.
- **Keeping the recon in your head.** Unwritten recon evaporates with the
  session; the note is what makes the next session (yours or another
  agent's) fast.

## Cross-reference

- **anti-over-engineering** — pair with this skill. Recon exists to
  understand, not to add or remove abstraction. When the pass surfaces
  over-built code, record it in the recon note and defer any simplification
  to a scoped cleanup, evaluated against the anti-over-engineering skill's
  criteria. A cleanup that starts during recon is an over-engineering
  failure in disguise.
- **understand / codebase-inspection** — deeper long-form codebase analysis
  for large migrations or onboarding docs; repo-recon is the fast,
  change-oriented variant.