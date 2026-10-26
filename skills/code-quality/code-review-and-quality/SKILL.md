---
name: code-review-and-quality
description: Use this skill when reviewing any code change, PR, or diff before merge — whether written by yourself, another agent, or a human. Conducts multi-axis code review across correctness, readability, architecture, security, and performance with structured severity labeling and verification gates.
---

# Code Review & Quality

## Overview

Multi-dimensional code review with quality gates. Every change gets reviewed before merge — no exceptions. Review covers five axes: correctness, readability, architecture, security, and performance.

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Perfect code doesn't exist — the goal is continuous improvement. Don't block a change because it isn't exactly how you would have written it. If it improves the codebase and follows the project's conventions, approve it.

**Distinction from code-review skill:** This skill covers the *quality framework and standards* for what constitutes a good review. The `code-review` skill covers the PR review *workflow and tooling*. Load both for complete coverage.

## When to Use

- Before merging any PR or change
- After completing a feature implementation
- When another agent or model produced code you need to evaluate
- When refactoring existing code
- After any bug fix (review both the fix and the regression test)
- When asked to evaluate code quality across multiple dimensions

## The Five-Axis Review

Every review evaluates code across these dimensions:

### 1. Correctness

Does the code do what it claims to do?

- Does it match the spec or task requirements?
- Are edge cases handled (null, empty, boundary values)?
- Are error paths handled (not just the happy path)?
- Does it pass all tests? Are the tests actually testing the right things?
- Are there off-by-one errors, race conditions, or state inconsistencies?
- What happens when inputs are malicious, not just malformed?

### 2. Readability & Simplicity

Can another engineer (or agent) understand this code without the author explaining it?

- Are names descriptive and consistent with project conventions? (No `temp`, `data`, `result` without context)
- Is the control flow straightforward (avoid nested ternaries, deep callbacks)?
- Is the code organized logically (related code grouped, clear module boundaries)?
- Are there any "clever" tricks that should be simplified?
- Could this be done in fewer lines? (1000 lines where 100 suffice is a failure)
- Are abstractions earning their complexity? (Don't generalize until the third use case)
- Would comments help clarify non-obvious intent? (But don't comment obvious code.)
- Are there dead code artifacts: no-op variables, backwards-compat shims, or commented-out code?
- Is a new conditional bolted onto an unrelated flow? That's a design smell, not a nit.
- Do repeated conditionals on the same shape appear? They signal a missing model or dispatcher.

### 3. Architecture

Does the change fit the system's design?

- Does it follow existing patterns or introduce a new one? If new, is it justified?
- Does it maintain clean module boundaries?
- Is there code duplication that should be shared?
- Are dependencies flowing in the right direction (no circular dependencies)?
- Is the abstraction level appropriate (not over-engineered, not too coupled)?
- Does this refactor reduce complexity or just relocate it? Count the concepts a reader must hold to follow the change. If a "cleaner" version leaves that count unchanged, it isn't cleaner.
- Is feature-specific logic leaking into a shared or general-purpose module?
- Are type boundaries explicit? Question gratuitous `any`/`unknown`/casts.
- Does the change add new dependencies? Every dependency is a liability — review each one.

### 4. Security

Does the change introduce vulnerabilities?

- Is user input validated and sanitized?
- Are secrets kept out of code, logs, and version control?
- Is authentication/authorization checked where needed?
- Are SQL queries parameterized (no string concatenation)?
- Are outputs encoded to prevent XSS?
- Are dependencies from trusted sources with no known vulnerabilities?
- Is data from external sources treated as untrusted?
- Are file paths validated to prevent path traversal?
- Is there proper rate limiting or validation on mutation endpoints?

### 5. Performance

Does the change introduce performance problems?

- Any N+1 query patterns?
- Any unbounded loops or unconstrained data fetching?
- Any synchronous operations that should be async?
- Any unnecessary re-renders in UI components?
- Any missing pagination on list endpoints?
- Any large objects created in hot paths?
- Any unnecessary allocations or copies in performance-critical paths?

## Structural Remedies

When you flag a structural problem, propose the move — not just the problem:

- **Replace a chain of conditionals** with a typed model or an explicit dispatcher.
- **Collapse duplicate branches** into a single clearer flow.
- **Separate orchestration from business logic** so each reads on its own.
- **Move feature-specific logic** out of a shared module into the package that owns the concept.
- **Reuse the canonical helper** instead of a bespoke near-duplicate.
- **Make a type boundary explicit** so downstream branching disappears.
- **Delete a pass-through wrapper** that adds indirection without clarifying the API.
- **Split a large file** into focused modules.

Prefer the remedy that removes moving pieces over one that spreads the same complexity around.

## Change Sizing

Small, focused changes are easier to review, faster to merge, and safer to deploy:

| Size | Assessment | Action |
|------|-----------|--------|
| ~100 lines changed | Good. Reviewable in one sitting. | Proceed |
| ~300 lines changed | Acceptable if it's a single logical change | Review carefully |
| ~1000+ lines changed | Too large. Split it. | Request split |

**What counts as "one change":** A single self-contained modification that addresses one thing, includes related tests, and keeps the system functional after submission.

**Separate refactoring from feature work.** A change that refactors existing code and adds new behavior is two changes — submit them separately.

## Review Process

### Step 1: Understand the Context
Before looking at code, understand the intent:
- What is this change trying to accomplish?
- What spec or task does it implement?
- What is the expected behavior change?

### Step 2: Review the Tests First
Tests reveal intent and coverage:
- Do tests exist for the change?
- Do they test behavior (not implementation details)?
- Are edge cases covered?
- Would the tests catch a regression if the code changed?

### Step 3: Review the Implementation
Walk through the code with the five axes in mind.

### Step 4: Categorize Findings
Label every comment with its severity:

| Prefix | Meaning | Author Action |
|--------|---------|---------------|
| *(no prefix)* | Required change | Must address before merge |
| **Critical:** | Blocks merge | Security vulnerability, data loss, broken functionality |
| **Nit:** | Minor, optional | Author may ignore |
| **Consider:** | Suggestion | Worth considering but not required |
| **FYI** | Informational only | No action needed |

### Step 5: Verify the Verification
Check the author's verification story:
- What tests were run?
- Did the build pass?
- Was the change tested manually?
- Are there screenshots for UI changes?

## Review Checklist

```
## Review: [PR/Change Title]

### Context
- [ ] I understand what this change does and why

### Correctness
- [ ] Change matches spec/task requirements
- [ ] Edge cases handled
- [ ] Error paths handled

### Readability
- [ ] Names are clear and consistent
- [ ] Logic is straightforward
- [ ] No unnecessary complexity

### Architecture
- [ ] Follows existing patterns
- [ ] No unnecessary coupling or dependencies
- [ ] Appropriate abstraction level

### Security
- [ ] No secrets in code or logs
- [ ] Input validated at boundaries
- [ ] No injection vulnerabilities
- [ ] Auth checks in place

### Performance
- [ ] No N+1 patterns
- [ ] No unbounded operations
- [ ] Pagination on list endpoints

### Verification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Manual verification done

### Verdict
- [ ] Approve — Ready to merge
- [ ] Request changes — Issues must be addressed
```

## Dead Code Hygiene

After any refactoring, check for orphaned code:

1. Identify code that is now unreachable or unused
2. List it explicitly
3. Ask before deleting: "Should I remove these now-unused elements?"

Don't leave dead code lying around — it confuses future readers and agents. But don't silently delete things you're not sure about.

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() in src/utils/date.ts — replaced by formatDate()
- OLD_API_URL in src/config.ts — no remaining references
→ Safe to remove these?
```

## Review Speed

Slow reviews block entire teams:

- Respond within one business day — this is the maximum, not the target
- Prioritize fast individual responses over quick final approval
- Large changes: ask the author to split them rather than reviewing one massive changeset

## Handling Disagreements

When resolving review disputes, apply this hierarchy:

1. **Technical facts and data** override opinions and preferences
2. **Style guides** are the absolute authority on style matters
3. **Software design** must be evaluated on engineering principles, not personal preference
4. **Codebase consistency** is acceptable if it doesn't degrade overall health

## Honesty in Review

- Don't rubber-stamp. "LGTM" without evidence of review helps no one.
- Don't soften real issues. "This might be a minor concern" when it's a bug that will hit production is dishonest.
- Quantify problems when possible. "This N+1 query will add ~50ms per item" is better than "this could be slow."
- Push back on approaches with clear problems.
- Accept override gracefully. If the author has full context and disagrees, defer to their judgment.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It works, that's good enough" | Working code that's unreadable, insecure, or architecturally wrong creates debt that compounds |
| "I wrote it, so I know it's correct" | Authors are blind to their own assumptions. Every change benefits from another set of eyes |
| "We'll clean it up later" | Later never comes. The review is the quality gate — use it |
| "AI-generated code is probably fine" | AI code needs more scrutiny, not less. It's confident and plausible, even when wrong |
| "The tests pass, so it's good" | Tests don't catch architecture problems, security issues, or readability concerns |
| "It's only a small addition to this file" | Small diffs still push files past a healthy size and bolt branches onto unrelated flows |
| "The refactor makes it cleaner" | Relocating complexity isn't reducing it. If the reader still holds the same number of concepts, the structure didn't improve |
| "It's just a version bump" | A dependency upgrade is a behavior change you didn't write. Read the changelog |

## Red Flags

- PRs merged without any review
- Review that only checks if tests pass (ignoring other axes)
- "LGTM" without evidence of actual review
- Security-sensitive changes without security-focused review
- Large PRs that are "too big to review properly"
- No regression tests with bug fix PRs
- Accepting "I'll fix it later" — it never happens
- A refactor that moves code around without reducing complexity
- New conditionals scattered into unrelated code paths
- A bespoke helper that duplicates an existing canonical one
- A bulk "bump dependencies" PR with no changelog review

## Verification

After review is complete:

- [ ] All Critical issues are resolved
- [ ] All Required changes are resolved or explicitly deferred with justification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] The verification story is documented
- [ ] Dependency upgrades were reviewed against their changelog