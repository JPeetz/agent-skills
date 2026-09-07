# Gate 1: Code Quality — LLM Failure Modes & Clean Code

## Overview

This gate catches the systematic ways LLMs produce bad production code. It combines classic clean-code principles (Clean Code, SOLID, DRY/KISS/YAGNI) with 15 research-backed AI failure modes. This is the primary gate — run it on every code change.

## The 15 AI Failure Modes

These are the systematic ways LLMs produce bad code, each backed by published research.

| # | Failure Mode | Key Research | The Rule |
|---|-------------|--------------|----------|
| 1 | Swallowed errors (broad catch-all) | Karpathy | Catch only the specific error type you can recover from |
| 2 | Defensive guards for impossible cases | arXiv 2409.19182 | Trust the type system; no null checks on non-nullable types |
| 3 | Premature abstraction (factories, interfaces for one impl) | Fowler | No interface/abstract/factory without 2+ concrete users |
| 4 | Comment pollution (what-comments, step scaffolding) | arXiv 2402.13013 | Comments explain *why*, never *what* |
| 5 | Code duplication instead of reuse | GitClear (8× growth 2021-2024) | Search for existing helper before writing inline copy |
| 6 | Hallucinated APIs and packages | USENIX Security '25 (~19.7%) | Verify every import against the installed version |
| 7 | Generic, intent-less naming | arXiv 2512.01141 | Names reveal intent — ban `data`, `result`, `temp`, `helper` |
| 8 | Long functions doing many things | GitClear (142→267 LoC, 4.2→8.1 cyclomatic) | One function, one thing. Target ≤20 lines |
| 9 | Parameter explosion (6+ positional args) | Fowler's overeagerness | At 5 params, extract a config/request object |
| 10 | Inconsistency with surrounding code | Stipe Minions, Honeycomb | Read neighbor files before writing; match style |
| 11 | Dead code, unused imports, half-implementations | arXiv 2411.01414 | Run linter pass; remove anything without a caller |
| 12 | Mock fallbacks / "declares success" | Fowler, Claude Code #6984 | Never return hardcoded success from a real-work function |
| 13 | Plausible-but-wrong code (off-by-one, wrong null semantics) | arXiv 2411.01414 | Enumerate boundary cases in comment before writing |
| 14 | YAGNI violations (speculative configurability) | Fowler's overeagerness | No `enable_*`, `use_*_v2`, optional param without caller |
| 15 | Async/concurrency hazards (dropped promises, sync-in-async) | Field reports | Every promise awaited; no blocking I/O in async paths |

## Cross-Cutting Root Cause

Eight of the 15 failure modes (1, 2, 3, 9, 12, 14, plus pieces of 8 and 11) trace to one root cause: **the model is biased toward emitting more code, more parameters, more guards, more abstractions** — anything but the minimum required by the spec. The cure is restraint, not knowledge. Before writing each line, ask: *does the spec require this, today?* If no, do not write it.

## Always-Applied Imperatives (Gate 1)

### Functions and Names
1. **Names reveal intent.** Never use `data`, `data2`, `result`, `result_final`, `item`, `temp`, `value`, `obj`, `info`, `helper`, `manager`, `utils`, or `handle_*`/`process_*`/`do_*` without a qualifier.
2. **Functions stay small.** Target ≤20 lines, one level of abstraction, one thing.
3. **Four arguments is the hard ceiling.** At five, introduce a request/config object. Never use boolean flag arguments.
4. **No output arguments.** A function either returns a value (query) or has a side effect (command). Never both.

### Comments and Structure
5. **Comments explain *why*, never *what*.** Delete paraphrasing, scaffolding, and commented-out code.
6. **Match the file's existing style.** Read the file and at least one neighbor before writing.

### SOLID
7. **One actor per module** (SRP). A class answerable to one stakeholder group.
8. **Extension via new code, not edits** (OCP). New variants = registry/strategy/polymorphism, not type-tag branches.
9. **No subclass refuses its parent's contract** (LSP). No "not implemented" in overrides.
10. **Abstractions live with the client** (DIP). Interface in the consuming package, not the implementation's.

### DRY, KISS, YAGNI
11. **Delete duplicated *knowledge*, not duplicated *text*.** One rule in code + docs + schema = violation.
12. **The wrong abstraction is worse than duplication.** Re-inline then re-abstract.
13. **Complexity ceiling: cyclomatic ≤10, nesting depth ≤5.**
14. **No speculative anything.** No optional param, config flag, feature toggle without a present-day caller.

### AI-Specific Guardrails
15. **Never swallow errors with broad catch-all handling.**
16. **No defensive guards for impossible cases.**
17. **Verify every import and external call against the installed version.**
18. **No hardcoded "success" returns or mock fixtures in production code.**
19. **Re-derive, do not copy from similar** — off-by-one bugs enter through copy-from-similar.
20. **Enumerate boundary cases before writing them** for any range, null, or off-by-one.
21. **Strip dead code before delivery** — unused imports, unreachable branches, no-caller functions.
22. **Read before write** — read the target file and a neighbor before editing.
23. **No dropped promises, no blocking in async** — every future awaited, no sync I/O in async paths.

### Refactoring Discipline
24. **Preserve observable behavior when refactoring.** Bug fixes and refactors are two operations — never bundle them.

## Self-Check (Gate 1)
1. Walk imperatives 1–24 against your diff. Fix every violation.
2. For new functions: ≤20 lines? ≤4 params? complexity ≤10? names reveal intent?
3. For new comments: explains *why*? If *what*, delete.
4. For new error handling: specific caught type? handler does something other than silently return?
5. For new abstractions: second concrete user *today*? If no, inline.
6. Did you read the neighbor files? Does your style match?
7. Any hardcoded "ok" return or fixture data? Replace with real impl or explicit unimplemented-trap.
8. If this is a refactor: did you change observable behavior? If yes, split out the bug fix.