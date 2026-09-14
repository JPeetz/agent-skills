---
name: safe-refactor
description: Use this skill when refactoring code — change structure without changing behavior, in small verified steps with tests green before and after each step.
author: adityaarakeri/senior-agent-skills + JPeetz
version: 1.0.0
tags: [refactoring, reliability, testing, code-quality]
---

# Safe Refactor

## Overview

Refactoring is restructuring code without changing its observable behavior. This skill enforces a **small-step, test-verified** workflow that minimises risk, keeps every commit behaviour-preserving, and integrates with existing code-review and testing skills.

## When to Use

Use this skill when:
- You need to restructure, rename, or reorganise code — not add features.
- A legacy module needs cleaning up before new work can begin.
- You're extracting a function, class, or file and must not break callers.
- Any change where "does it still work?" must have a reproducible answer.

---

## Ground Rules

1. **Green before you start.** Run the full test suite. If it's not green, stop — broken tests cannot tell you whether the refactor broke anything.
2. **Refactor commits contain zero behaviour change.** Every refactor commit is pure structural change. Feature additions, bugfixes, and documentation that changes meaning belong in separate commits.
3. **Small mechanical steps with tests between each.** No step changes more than one thing: rename one symbol, extract one function, move one file. Run the relevant tests after each step before committing.
4. **Use real tooling for renames.** Never manually sed/grep across the tree. Use language-aware refactoring tools — your IDE's rename, `git mv`, or language-specific codemods (`jscodeshift`, `comby`, `rope`).
5. **Watch the blast radius.** A rename in a shared module may affect dozens of files. Check imports/exports, type stubs, documentation, and generated files. When in doubt, trace the symbol's usages first.

---

## Definition of Done

The refactor is complete when ALL of the following hold:

| Criterion | Verification |
|---|---|
| All existing tests pass | `npm test` / `pytest` / equivalent returns exit 0 |
| No behaviour changes | Diff shows only structural change (move, rename, extract) — no logic edits |
| No orphaned references | Linter passes (`ruff`, `eslint`, `tsc --noEmit`), no unresolved imports |
| No dead code left | Coverage of refactored area is >= pre-refactor baseline |
| Git log is clean | Each refactor step is its own commit with a descriptive message (e.g. `refactor: rename Order.total() to Order.calculate_total()`) |
| CI is green | Push triggers a passing CI run on the final branch |

---

## The Refactor Workflow

### Step 1 — Baseline
- Checkout a fresh branch: `git checkout -b refactor/<description>`
- Run the full test suite. If it fails, fix the test environment first.
- Record the current coverage and test count.

### Step 2 — Plan the step sequence
- Write down each atomic transformation. Example sequence for renaming a function:
  1. Add new function alongside old one
  2. Update all internal callers to use new name
  3. Remove old function
  4. Update external/exported references
- A good heuristic: if you can't describe the step in one short sentence, it's not atomic enough.

### Step 3 — Execute one step
- Make exactly the change described in one step from the plan.
- Run the relevant test module (not the whole suite — this is a fast feedback loop).
- If tests pass, commit with message starting `refactor:` and describing *what* changed, not why.
- If tests fail, revert (`git checkout -- .`) and redo the step more carefully.
- **Never** fix a test failure by changing the test to match broken code — revert the code change.

### Step 4 — Iterate
- Repeat Step 3 for each atomic transformation in the plan.
- Run the full suite after every 3–5 steps, or whenever you touch a shared/public interface.

### Step 5 — Final verification
- Run the full test suite one last time.
- Run the linter with the strictest available config.
- Run the language type checker if available.
- Push the branch and confirm CI passes.
- Open a PR with the description "Refactor: <summary>" and link to the plan.

---

## Common Pitfalls

| Pitfall | How to avoid |
|---|---|
| Sneaking in a bugfix during refactor | Commit bugfixes first on a separate branch, *then* start the refactor branch |
| One commit touches 20 files for a rename | Use language-aware rename — most IDEs and `git mv` handle this automatically |
| "I'll just fix this one small thing while I'm here" | Stop. Commit the refactor first, then the fix on a new branch |
| Tests take 20 minutes to run | Isolate the test module under change for the quick inner loop; run the full suite only at checkpoints |
| Forgetting to update type stubs or docstrings | Include `.d.ts` / `.pyi` / docstring files in your pre-commit checklist |
| CI passes locally but fails on the server | Match the CI environment (Node version, OS, dependency locks) — use the CI Docker image or `act` locally |

---

## Cross-References

| When you need... | Use this skill |
|---|---|
| A code review before merging the refactor PR | `github-code-review` — review diffs, inline comments, approve |
| Tests to validate the refactor didn't break anything | `test-driven-development` — TDD lifecycle; or any project test framework |
| A deep-dive analysis of the codebase before planning | `understand` — analyse the codebase, produce a knowledge graph |
| A quick spike to validate the refactor approach | `spike` — throwaway experiment before committing to the full workflow |
| Writing a PR description for the refactor branch | `github-pr-workflow` — commit, open PR, CI, merge |