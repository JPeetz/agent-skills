---
name: remove-ai-slops
description: "Clean AI-generated code smells from branch changes or an explicit file list while preserving behavior, including junk tests proven before each cut. Use when the user asks to deslop or tidy recent code."
---

# Remove AI slops

Remove unnecessary complexity from a bounded change while preserving behavior.
Green regression checks protect deletions; the smell checklist helps identify
candidates and does not itself prove that code is dispensable.

## Scope and ownership

Use the caller's explicit file list when supplied. Otherwise discover the
repository's base branch and use its merge-base with the current branch to
identify changed files. Record the base revision and affected paths so the
scope can be reproduced. Avoid assuming a branch named `main` exists.

Stay within that set. Report unrelated findings without editing them. Read the
current diff and affected source before choosing a change; preserve other
contributors' work. When there is nothing eligible to improve, say so.

For a coordinator, `task-delegation` owns available host dispatch and lifecycle.
Split only genuinely independent file scopes. An assigned cleanup worker
performs its own pass and checks directly; it does not recursively delegate
cleanup agents. Keep publication with the repository's delivery owner.

## Lock behavior first

Find the affected tests and run a baseline. Add focused characterization tests
for behavior that a proposed deletion or simplification could break, including
return values, error paths, side effects, boundaries, and malformed input where
relevant. Confirm those tests pass before removing code.

An existing passing test is useful only if it exercises the behavior at risk.
Use the real runtime surface when tests cannot expose wiring, integration, or
rendering failures. If behavior cannot be established, retain the code and
report the verification gap. Diagnose existing failures before treating them as
permission to proceed with an unverified cleanup.

Preserve coverage and protection thresholds. Add or strengthen tests rather
than weakening assertions to make cleanup pass. Test deletion is in scope only
with the proof its class requires, under [Test files](#test-files-missing-and-junk).

## Test files: missing and junk

In-scope test files are judged like any other file, in two directions.

**Missing**: a behavior in the changed files that no test guards, where the
repository keeps tests for that kind of behavior and a regression would
otherwise pass unnoticed. Add the narrowest test; it must answer all four
gate questions — the contract it protects, the regression that fails it, why
existing coverage does not, and that it needs no production seam only a test
calls. A prose file (prompt, rule, markdown) has no behavioral seam: cover only
a machine-consumed value or leave it to review.

**Junk**: mark every in-scope test declaration `R` / `F` / `C` / `D` per
[`references/junk-classes.md`](references/junk-classes.md). A `D` or `C` needs
the proof that table names for its class before the cut: for behavior classes a
mutation of the production owner run against the candidate and its named keeper
on the unmodified test tree. Run proofs serially, never while other edits are
in flight; restore the owner byte for byte and never commit a mutation. Apply
`F` rows directly and report them; `C` moves the assertion into its named
keeper. A misnamed test is re-marked by what its assertions check, never cut
for its name. A test-only production seam (export, flag, getter, reset hook)
whose last test was deleted goes with it.

Keep everything under the retention bar in that table. A test red on the
unchanged base is a product bug to report, never a deletion. Static or slow is
never a reason to delete.

## Choose the smallest valid transformation

Apply this decision ladder to each candidate:

1. **Delete** when code has no required behavior or callers. Prove it is dead
   with source and usage evidence; account for exports, reflection, generated
   registration, framework hooks, and dynamic consumers.
2. **Replace with a language or standard-library facility** when equivalent
   behavior already exists. Confirm semantics, error handling, and edge cases.
3. **Flatten** a wrapper or abstraction that adds indirection without a useful
   contract. Preserve actual module boundaries and extension points in use.
4. **Simplify control flow** while preserving behavior and readability. An
   idiomatic small conditional may be clearer than a compact expression.
5. **Retain** code whose purpose or equivalence is uncertain. Default to KEEP,
   and record the evidence needed to revisit it.

Do not add speculative abstractions, dependencies, options, or configuration.
If an algorithm replacement needs a separate equivalence argument, treat it as
a refactor with its own scope and checks, rather than disguising it as cleanup.

## Smell passes

Inspect every scoped file against all applicable categories. The categories are
review lenses, not a fixed number of agents or a required number of findings.

| Category | Remove or simplify when proven redundant | KEEP when it serves a real contract |
| --- | --- | --- |
| Comments | Narration of obvious code, stale or misleading notes | WHY, non-obvious constraints, API documentation, linter directives, licenses, required markers |
| Defensive checks | Duplicate validation after a stronger enforced invariant, unreachable fallbacks | API, user-input and external-response validation; uncertain or untrusted values |
| Errors | Catch-and-rethrow with no effect, silent catch, pointless fallback, duplicate logging | Recovery, user-facing handling, useful context or actionable diagnostics |
| Dead code | Unused imports, variables, private functions, commented-out code, obsolete TODOs | Public/dynamic entry points, framework lifecycle hooks, intentional compatibility |
| Abstractions | Single-use helpers or wrapper layers that add no clarity or contract, speculative factories | Used extension points and meaningful module boundaries |
| Verbosity | Repeated literals, unnecessary intermediates, verbose forms with clear native equivalents | Named steps or explicit flow that improve understanding |
| Types | Redundant assertions or annotations, broad `any`/`unknown` used to avoid modeling, unjustified suppressions | Useful explicit signatures and deliberate validated assertions at boundaries |
| Performance | Repeated pure computation in a loop, quadratic membership checks with equivalent set semantics, avoidable copies | Allocations or ordering needed by callers, code whose equivalence is uncertain |
| Style | Patterns introduced by the change that conflict with nearby repository conventions | Existing conventions, even when personal preference differs |
| Dependencies | A scoped dependency use made unnecessary by the cleanup and safely replaceable by built-ins | External code whose behavior, compatibility, or removal impact remains unproven |

Read each candidate in context. Validation that appears repeated can protect a
separate trust boundary; a wrapper that looks trivial can own instrumentation
or registration. Keep deliberate exception handling and comments that explain
why. Change a suppression only after repairing its underlying type problem.

Language-specific constraints belong to the project's rules; load the relevant
guidance when editing Python, Rust, TypeScript, or Go. Those owners define
complexity, typing, and error-handling standards. Do not invent new thresholds
or mechanically rewrite correct code to fit a cleanup quota.

## Verify each slice

Group related changes into small, reviewable slices so a regression can be
attributed to a specific transformation. Read current files before editing,
apply the slice, then run the affected regression checks and applicable
compile, parse, type, and lint checks. Compare diagnostics with the baseline.

When a check fails, stop dependent cleanup and identify the cause. Repair or
undo only the responsible hunk, preserving unrelated work, and rerun the
failing check. Keep an uncertain candidate instead of repeatedly guessing.
After three failed fixes, reassess the assumption and return the evidence to
the coordinator or seek stronger analysis within scope.

## Final gate

Review the final diff for new complexity, scope drift, behavior changes, and
weakened tests. For substantial cleanup, have an independent read-only reviewer
challenge correctness and adherence to the original request. Reuse suitable
existing review evidence when it still matches the final diff.

Run the repository's required final checks plus the affected regression suite.
Use the actual project commands and read their output before reporting PASS.
For each applicable gate, retain its command, result, and relevant artifact:

- Regression behavior and relevant integration or runtime surface.
- Syntax/build, types, diagnostics, and repository lint or format requirements.
- Final diff review, including retained uncertain candidates.

Mark a gate `N/A` only with a reason. A failed or unavailable check remains a
reported gap, not a passing result. Continue authorized delivery through the
repository's workflow when that is part of the request.

## Report

State `CLEAN`, `ISSUES FIXED`, or `REQUIRES ATTENTION`, followed by the useful
evidence:

- Scope and base revision; files changed and smell categories addressed.
- What was deleted or simplified and which regression checks protect it.
- Actual gate results, with baseline failures and unavailable checks identified.
- Candidates kept, remaining risks, and any unfinished work with its next action.

A line-count reduction can describe the result, but it is never a target that
justifies removing functional code, useful explanation, or safety checks.
