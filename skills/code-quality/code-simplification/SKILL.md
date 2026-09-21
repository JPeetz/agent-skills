---
name: code-simplification
description: "Use this skill when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. Use when reviewing code that has accumulated unnecessary complexity — deep nesting, long functions, unclear names, duplication, or over-engineering."
version: "1.0.0"
author: "Skill Foundry"
license: "MIT"
metadata:
  hermes:
    tags: [code-simplification, refactoring, code-quality, readability, complexity-reduction, clean-code]
    related_skills: [systematic-debugging, github-code-review]
---

# Code Simplification

> Reduce complexity while preserving exact behavior. The goal is not fewer lines — it's code that is easier to read, understand, modify, and debug.

## Quick Reference

| When to apply | What to check | Key heuristic |
|---|---|---|
| After feature is done, tests pass | Implementation feels heavier than needed | "Would a new team member understand this faster?" |
| During code review | Readability or complexity flags | Each simplification must be a clear net improvement |
| When encountering deep nesting | Conditional complexity | Flatten with guard clauses, not by removing checks |
| When names are unclear | Variable, function, class names | A good name removes the need for a comment |
| After merging duplicated code | Logic repeated across files | Extract once, reference everywhere |
| When an abstraction seems unnecessary | Indirection that obscures the flow | YAGNI: remove it, re-add when needed |

## When to Use

Use this skill when:

- **After a feature is working and tests pass** — but the implementation feels heavier than it needs to be
- **During code review** — when readability or complexity issues are flagged
- **You encounter deeply nested logic, long functions, or unclear names** — the code works but costs too much to understand
- **Refactoring code written under time pressure** — hackathon code, prototypes, experimental branches
- **Consolidating related logic scattered across files** — duplication that has drifted apart over time
- **After merging changes that introduced duplication or inconsistency** — merge conflicts sometimes produce copy-paste residue

**DO NOT use when:**

- Code is already clean and readable — don't simplify for the sake of it
- You don't understand what the code does yet — comprehend before you simplify (Chesterton's Fence)
- The code is performance-critical and a simpler version would be measurably slower — complexity is a justified trade-off
- You're about to rewrite the module entirely — simplifying throwaway code is wasted effort
- You haven't run the existing tests — simplification without a passing test suite is guessing

## The Five Principles

### 1. Preserve Behavior Exactly

Don't change what the code does — only how it expresses it. All inputs, outputs, side effects, error behavior, and edge cases must remain identical. The exception: if the existing code has a demonstrable bug, fix it in a separate commit with its own test, then simplify.

### 2. Follow Project Conventions

Simplification means making code more consistent with the codebase, not imposing external preferences. If the project uses Builder pattern everywhere, don't replace a Builder with a constructor. If the project prefers named parameters over options objects, follow that.

### 3. Prefer Clarity Over Cleverness

Explicit code is better than compact code when the compact version requires a mental pause to parse. Simplicity is about comprehension speed, not line count. A 10-line function a teammate can read in 10 seconds is better than a 3-line function that takes 30 seconds to decipher.

### 4. Maintain Balance

Watch for over-simplification traps:

- **Inlining too aggressively** — extracting a well-named helper improves readability, even if you could inline the logic
- **Combining unrelated logic** — if two things change for different reasons, keep them separate
- **Removing necessary abstraction** — interfaces, adapters, and wrappers exist for a reason (testing, swapping implementations)
- **Optimizing for line count** — `x = a ? b ? c ? d : e : f : g` is fewer lines, not simpler

### 5. Scope to What Changed

Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code. Every unrelated simplification is a risk of regression and a noisy diff. If you see systemic issues, log them as tech debt and handle in a dedicated refactoring pass.

## The Simplification Process

### Step 1: Understand Before Touching (Chesterton's Fence)

Before changing or removing anything, understand why it exists. Answer these questions:

- What is this code's responsibility? What calls it? What calls what it calls?
- What are the edge cases? Empty collections, null values, boundary conditions.
- Why was it written this way? Check `git blame` — there may be a reason in the commit message.
- Could a bug be hiding behind the complexity? If so, fix it separately.

**The rule:** If you can't explain what a piece of code does to a junior developer in one sentence, don't simplify it yet. Comprehend first, simplify second.

### Step 2: Identify Simplification Opportunities

Scan for these categories:

**Structural complexity:**
- Deep nesting (>3 levels) — flatten with guard clauses / early returns
- Long functions (>30 lines visible on screen) — extract cohesive groups to named helpers
- Nested ternaries — convert to if/else or switch
- Boolean flags passed through multiple layers — consider Options object or split functions
- Repeated conditions — extract to a named predicate

**Naming and readability:**
- `data`, `temp`, `result`, `val` — names that don't convey meaning
- Abbreviations that aren't project-standard (`usr` vs `user`, `cfg` vs `config`)
- Names that contradict what the code actually does
- Comments that restate what the code does (`// increment i` above `i++`) — rename instead

**Redundancy:**
- Duplicated logic — extract to shared function/module
- Dead code — commented-out blocks, unreachable branches, unused parameters
- Unnecessary abstractions — wrappers that wrap nothing, factories that produce one thing
- Over-engineered patterns — Strategy pattern with one strategy, Observer with one subscriber

### Step 3: Apply Changes Incrementally

| Guideline | Why |
|---|---|
| One simplification per commit | Reviewers can understand each change independently |
| Run tests after each change | Catches broken assumptions immediately |
| Separate refactoring from feature work | A single commit that "adds features AND simplifies" is un-reviewable |
| The Rule of 500 | If a refactoring touches 500+ lines, use automation (codemod, sed, jscodeshift) instead of hand-editing. Hand-edits at scale introduce inconsistencies. |
| When in doubt, add a test first | Tests document the behavior you're preserving. They are the proof that your simplification didn't break anything. |

### Step 4: Verify the Result

Before you mark the task done:

- **Diff quality:** Is every change clearly a net improvement? Could any change be argued either way? If so, revert that change.
- **Test suite:** All existing tests pass without modification. If you need to change a test, you changed behavior and should undo that change.
- **Teammate test:** Would a teammate approve each simplification in code review? When in doubt, read your diff as if someone else wrote it.
- **Self-test:** For each simplification, can you articulate exactly what made the original code more complex and how your version is better?

### Step 5: Document What Changed

For each simplification, note:

- **What you changed** — file, function, pattern
- **Why it was complex** — the specific quality (nesting, naming, duplication)
- **What you simplified it to** — the specific technique used
- **What you preserved** — verification that behavior is unchanged

This documentation lives in the commit message or PR description, not in code comments.

## Language-Specific Patterns

Detailed before/after examples for TypeScript, Python, React, and Go are in [`references/language-patterns.md`](references/language-patterns.md). Key highlights:

| Language | Common pattern | Guidance |
|---|---|---|
| TypeScript | Nested ternaries | Convert to early returns or if/switch blocks |
| Python | Manual dict get + default | Use `dict.get(key, default)` |
| React | Derived state via `useEffect` | Compute during render instead |
| Go | Error check chains | Keep explicit — Go idiom is intentional |

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's working, no need to touch it" | Working code that's hard to read will be hard to fix when it breaks. Complexity is a deferred cost that compounds. |
| "Fewer lines is always simpler" | Simplicity is about comprehension speed, not line count. A one-liner with two nested ternaries and a void operator is not simple. |
| "I'll just quickly simplify this unrelated code too" | Unscoped simplification creates noisy diffs and risks regressions in code you don't fully understand. Stick to what changed. |
| "This abstraction might be useful later" | YAGNI — "You Aren't Gonna Need It." Add the abstraction when the second consumer actually appears. |
| "I'll refactor while adding this feature" | Separate refactoring from feature work. A single commit that does both is impossible to review and revert. |
| "It passes tests so the simplification must be correct" | Tests only verify what they assert. If the simplified code introduces a subtle bug in an un-tested edge case, tests won't catch it. Use tests as a safety net, not the sole verification. |
| "The code looks fine to me, it's just long" | Long functions that look fine often violate the Single Responsibility Principle. Extract groups of related logic into named functions that reveal intent. |
| "I'm just removing comments" | Comments are a code smell, but removing them without improving the code they describe makes the code worse. Rename first, delete comments second. |

## Red Flags

| Red Flag | What to do instead |
|---|---|
| Simplification requires modifying tests to pass | Revert. You changed behavior, not just expression. |
| "Simplified" code is longer and harder to follow | Revert that change. Not every attempt wins. |
| Removing error handling because "it makes the code cleaner" | Error handling is complexity you need. The fix is to reduce complexity elsewhere. |
| Simplifying code you don't fully understand | Stop. Go back to Step 1. |
| Batching many simplifications into one large commit | Break it up. One change per commit. |
| Simplifying generated or boilerplate code | Leave it. The predictability of generated patterns is itself a simplification. |
| Simplifying code in a language you're not fluent in | Get a native speaker to review. Idioms differ significantly across languages. |

## Verification

Before finalizing any simplification work:

- [ ] All existing tests pass without modification
- [ ] Build or type-check succeeds with no new warnings
- [ ] Each simplification is in its own commit — no batching
- [ ] No error handling was removed or weakened
- [ ] No dead code was left behind (if you removed dead code, confirm it was actually dead)
- [ ] No inline comments were removed without improving the names they restated
- [ ] Performance: if the simplified path is in a hot loop, benchmark before and after
- [ ] The diff is scoped to the change area — no drive-by refactors
- [ ] A teammate reading the diff would approve each change
- [ ] For each change: what was complex, what simplified it, what was preserved?

## Sources

- **Clean Code** (Martin, 2008) — naming, functions, comments, formatting
- **Refactoring** (Fowler, 2nd ed.) — behavior-preserving transformations
- **The Pragmatic Programmer** (Hunt & Thomas) — DRY principle, YAGNI
- **Code Complete** (McConnell, 2nd ed.) — complexity measurement, table-driven methods
- **A Philosophy of Software Design** (Ousterhout, 2018) — deep modules, complexity theory
- **Working Effectively with Legacy Code** (Feathers, 2004) — safe refactoring, characterization tests
- **Claude Code Simplifier plugin** — conceptual inspiration for this skill