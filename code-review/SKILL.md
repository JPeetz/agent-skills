---
name: code-review
description: >
  AI-powered code review and PR analysis. Performs systematic reviews
  covering security vulnerabilities, code quality, style compliance,
  architectural integrity, test coverage, and performance considerations.
  Works with PR diffs, commit ranges, file changes, or raw code snippets.
  Primary keyword clusters: AI code review automation, automated PR review
  security, code quality analysis static, pull request review checklist,
  OWASP code review patterns, architectural review automation, test coverage
  analysis review, performance code review, style guide compliance checker,
  code smell detection automated. Designed for agentic platforms — Claude
  Code, Codex, Cursor, Gemini CLI, OpenClaw, GitHub Copilot, Windsurf, and
  OpenCode.
version: 1.1.0
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
  - code-review
  - security
  - quality
  - pr-analysis
  - static-analysis
  - best-practices
  - architecture
  - test-coverage
geo:
  primary_workflows:
    - pr_review
    - security_audit
    - code_quality_assessment
    - architectural_review
    - test_coverage_evaluation
    - performance_analysis
  target_roles:
    - senior_developer
    - tech_lead
    - security_engineer
    - devops_engineer
    - engineering_manager
  complexity_level: advanced
  prerequisite_knowledge:
    - multiple_programming_languages
    - security_patterns_owasp
    - software_architecture_principles
    - testing_strategies
    - git_workflows
---

# Code Review Agent Skill

Perform structured, thorough AI-powered code reviews for pull requests, diffs,
commit ranges, or standalone code. This skill turns an agent into a systematic
reviewer that checks security, style, architecture, test coverage, and
performance — not just a linter.

---

## Quick Reference

| Dimension | What to Check | Key Indicators |
|---|---|---|
| 🔴 Security | OWASP Top 10, secrets, injection, auth | Hardcoded keys, unsanitized input, weak crypto |
| 🟠 Correctness | Logic, edge cases, error handling | Off-by-one, missing null checks, unhandled promises |
| 🟡 Quality | Readability, naming, DRY, comments | Single-letter vars, >50 line functions, dead code |
| ⚪ Style | Indentation, line length, imports | PEP8, ESLint, gofmt violations |
| 🏗️ Architecture | SRP, coupling, layering, API compat | New patterns conflicting with existing conventions |
| 🧪 Tests | Coverage, edge cases, determinism | Untested critical paths, flaky tests, missing mocks |
| ⚡ Performance | Complexity, N+1 queries, memory | O(n²) on unbounded input, missing indexes |
| 📝 Docs | API docs, logging, observability | Undocumented public APIs, absent error logging |

**Severity Scale:**
- 🔴 **BLOCKER** — Must fix before merge. Security, data loss, crash, broken core.
- 🟠 **MAJOR** — Should fix before merge. Bug, significant perf, violated patterns.
- 🟡 **MINOR** — Nice to fix. Code smell, minor duplication, unclear naming.
- ⚪ **NIT** — Optional. Style preference, formatting, personal taste.

**Recommendation Rules:**
- Any BLOCKER or MAJOR → ❌ **Request changes**
- Only MINOR and NIT → ⚠️ **Approve with suggestions**
- No findings → ✅ **Approve**

---

## When to Use This Skill

Activate this skill when the user asks you to:

- "Review this PR" / "Review this diff" / "Code review this"
- "Check my code for issues" / "Does this look secure?"
- "Code review this commit / branch" / "Analyze this pull request"
- "Look over these changes before I merge"
- "Find bugs / security issues in this code" / "Audit this code for vulnerabilities"
- "Is this code production-ready?" / "Can you do a thorough review of this?"
- Any request containing "review" + code, diff, PR, or patch

Additionally, activate proactively when a conversation includes a code diff
or patch and the user's tone suggests they want feedback.

### Do NOT Activate For

The following inputs are **near-miss negatives** — they mention review-like
language but are not code reviews:

- **General Q&A**: "What do you think of React vs Vue?" — opinion, not code review.
- **Code explanation requests**: "Can you explain what this function does?" — teaching, not reviewing.
- **Write/generate code**: "Write a function that sorts a list" — generation, not review.
- **Debugging help**: "Why is this code throwing a TypeError?" — debugging, not review.
- **Architecture design from scratch**: "Design a microservice for user auth" — design, not review.
- **Documentation requests**: "Write docs for this API" — documentation, not review.
- **Refactoring without review context**: "Rewrite this in functional style" — rewrite, not review.
- **Pure linting/formatting**: "Run prettier on this file" — formatting, not review.

When in doubt, ask: "Did you want me to review this for quality/security, or
were you asking me to do something else with this code?"

---

## Common Pitfalls & Anti-Patterns

### ❌ Reviewer Anti-Patterns

1. **Nit-picking without context** — Don't drown the author in formatting nits when there are real bugs. Flag nits as NIT-severity and prioritize BLOCKERs.

2. **"This is wrong" without saying why or how to fix it** — Every BLOCKER and MAJOR finding must include a concrete, actionable fix suggestion with a code example if helpful.

3. **Reviewing code you haven't fully read** — Read the entire diff before forming opinions. Context from later in the diff may explain something that looks odd early on.

4. **Demanding changes that reflect personal preference, not team standards** — If the project uses `single quotes` and the team standard is `double quotes`, flag the style inconsistency. If the project has no standard, don't impose yours.

5. **Ignoring the PR description and linked issues** — The PR description tells you what the author intended. Review against intent, not in a vacuum.

6. **Assuming the author's intent without asking** — If something looks suspicious but could be intentional, say "This appears to do X, but based on the PR description I expected Y. Can you clarify?"

7. **Reviewing the entire codebase, not just the diff** — Respect scope. Only review code outside the diff if it's directly relevant to the change.

8. **Using harsh or judgemental language** — "This is broken" → "This could return null if `user` is undefined, which would cause a TypeError on the next line." Be specific, factual, and empathetic.

9. **Approving a PR with BLOCKER findings** — Never. If there are security issues or broken core functionality, the recommendation MUST be "Request changes."

10. **Exposing secrets found during review** — Flag: `**BLOCKER: Hardcoded secret at src/auth.ts:15**`. Never echo the full secret value in shared channels. In 1:1 sessions, show redacted form: `sk-...abc123`.

### ✅ Review Quality Checklist

Before publishing your review, verify:

- [ ] All 8 analysis dimensions were considered (security, correctness, quality, style, architecture, tests, performance, docs)
- [ ] Every finding has a severity label (🔴🟠🟡⚪)
- [ ] Every BLOCKER and MAJOR has a concrete fix suggestion
- [ ] No hardcoded secrets are echoed in the output
- [ ] Recommendation matches findings (BLOCKER/MAJOR → Request Changes)
- [ ] Summary is 2-3 sentences and accurate
- [ ] File/line references in findings actually exist
- [ ] Review tone is constructive, factual, and respectful
- [ ] Scope is appropriate — reviewing the diff, not the codebase
- [ ] If re-review, previous findings were checked for resolution

---

## Workflow

### Phase 1: Gather Input

1. **Identify the review target** — is it a PR, a diff, a commit range, a set of
   changed files, or pasted code?

2. **Collect context**:
   - For PRs: use `gh pr view <number> --json title,body,additions,deletions,files`
     and `gh pr diff <number>` (see the GitHub skill if available).
   - For commits: `git diff <base>...<head>` or `git show <commit>`.
   - For pasted diffs: capture the full diff text.
   - For files: read the changed files alongside any related unchanged files
     for context.

3. **Determine the base branch or baseline** so you can assess what changed vs
   what existed before. Never review changes in a vacuum.

4. **Ask the user for any special concerns**: "Any particular areas you want me
   to focus on? Security? Performance? Specific modules?"

### Phase 2: Structured Analysis

Work through these dimensions in order. Do not skip any unless the review
scope explicitly excludes it.

#### 2.1 Security (Highest Priority)

- Scan for OWASP Top 10 patterns: injection (SQL, OS command, LDAP, XPath),
  broken authentication, sensitive data exposure, XXE, broken access control,
  security misconfiguration, XSS, insecure deserialization, vulnerable
  components, insufficient logging.
- Check for hardcoded secrets: API keys, tokens, passwords, private keys.
  Flag these with **BLOCKER** severity — never let them merge.
- Review input validation: is all user input sanitized? Parameterized queries?
  Output encoding?
- Check authentication/authorization changes: are new endpoints properly gated?
  Is there a privilege escalation path?
- For crypto: are weak algorithms used (MD5, SHA-1 for security, DES, RC4)?
  Are random values from crypto-secure sources?
- File operations: path traversal risks, unsafe deserialization (`pickle`,
  `yaml.load`), zip slip.
- Dependency changes: if `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`
  etc. changed, flag new dependencies for supply-chain review.

Use `references/security-patterns.md` for a comprehensive checklist.

#### 2.2 Correctness & Logic

- Will the change do what it claims to do?
- Edge cases: null/undefined/empty inputs, boundary conditions, concurrency.
- Error handling: are errors caught and handled appropriately? No silent
  swallowing without justification?
- Off-by-one errors, inverted conditions, missing `await`/`async`.
- Type safety issues in dynamically-typed code.
- **Race conditions:** Check for shared mutable state accessed concurrently.
  Are locks/mutexes used correctly? Are channel operations non-blocking when
  expected?
- **Idempotency:** If the operation is called twice (e.g., duplicate API
  request, retried message), does it produce the same result? Check for
  idempotency keys or deduplication logic.
- **Transaction integrity:** For multi-step operations, are they wrapped in a
  transaction? What happens if step 3 fails after step 2 succeeds?
- **Time-related bugs:** Leap seconds, timezone offsets, DST transitions.
  Does the code handle `datetime` correctly across timezones?

#### 2.3 Code Quality & Maintainability

- Is the code readable and self-documenting? Would a new team member
  understand it?
- Naming: are variables, functions, and classes named clearly? No single-letter
  names outside of tight loop/closure scopes.
- Functions: are they small and single-purpose? Flag functions over ~50 lines
  or with cyclomatic complexity above ~10.
- DRY violations: is there duplicated logic that should be extracted?
- Comments: do comments explain *why*, not *what*? Flag commented-out code.
- Dead code: unreachable branches, unused imports, unused variables.
- Appropriate use of language idioms (list comprehensions in Python,
  destructuring in JS, etc.).
- **Cohesion vs coupling:** Does the new code belong in the module it's in?
  Is it importing 15 modules just to do one thing?
- **Magic numbers/strings:** Are there unexplained numeric literals or string
  constants? Should they be named constants or configuration values?

#### 2.4 Style Guide Compliance

- Check against the relevant style guide (see `references/style-guides.md`):
  - Python: PEP 8
  - JavaScript/TypeScript: Airbnb or Standard
  - Go: Effective Go / `gofmt`
  - Rust: `rustfmt` / official style
  - Java: Google Java Style
- Indentation, line length, whitespace, brace placement, import ordering.
- Note: flag style issues as **NIT** severity unless they obscure intent.

#### 2.5 Architecture & Design

- Does the change fit the existing architecture? Does it introduce new
  patterns that conflict with established conventions?
- Single Responsibility Principle: is the new code in the right place?
- Coupling: does the change introduce tight coupling between unrelated modules?
- Does it respect existing abstractions and layering?
- **Database changes:** New migrations, schema changes — are they backward
  compatible? No data loss? Are rollback scripts provided?
- **API changes:** Are they backward compatible? Versioned if breaking?
  Is the API contract versioned? Are deprecation headers/notices included?
- **Event/message schema changes:** If this is an event-driven system, do
  schema changes propagate correctly? Are consumers updated?
- **Circular dependencies:** Does the new code create cycles between modules,
  packages, or services?
- **Feature flags:** For large changes, are feature flags used to decouple
  deployment from release?

#### 2.6 Test Coverage

- Are there tests for the new/changed behavior?
- Do tests cover happy path, edge cases, and error conditions?
- Are tests deterministic (no flaky timeouts, no external dependencies without
  mocking)?
- Check that test descriptions/names clearly describe what is being tested.
- Flag if critical paths have zero test coverage.
- **Test quality, not just presence:** A test that only checks `assert True`
  is worse than no test — it creates false confidence.
- **Snapshot tests:** Are snapshot changes intentional, or are they capturing
  unintended side effects?
- **Integration vs unit:** Does the test level match the change? A pure
  logic change should have unit tests; an API change should have integration
  tests.

#### 2.7 Performance

- **Algorithmic complexity:** Any O(n²) operations on unbounded inputs?
  Check for nested loops over user-controlled collections.
- **Database: N+1 queries in loops?** Missing indexes on new columns?
  Are queries paginated? Is there a risk of full table scans?
- **Memory:** Large allocations, unbounded collections, potential leaks.
  Are streams/large files read entirely into memory? Are caches unbounded?
- **Network:** Unnecessary API calls, missing caching, chatty I/O.
  Are retries configured with exponential backoff? Is there a circuit breaker?
- **Blocking operations on event loops** (Node.js, asyncio). Is synchronous
  I/O being used on an async event loop?
- **Large assets or dependencies being pulled in.**
- **Connection pooling:** Are database/HTTP connections pooled or created
  per request?
- **Serialization cost:** Is large data being serialized/deserialized
  unnecessarily?

#### 2.8 Documentation & Observability

- Are public APIs documented?
- Are complex algorithms or business rules explained?
- **Logging:** Are important state transitions and errors logged at
  appropriate levels? Are PII/sensitive values being logged?
- **Metrics/tracing:** Are there hooks for observability if the codebase
  uses them? Are key operations instrumented with spans?
- **Error messages:** Can a developer or operator understand what went
  wrong from the error? Or will they need to grep the source?
- **README/docs updates:** If the change introduces new behavior, are the
  docs updated? Is there a changelog entry?

### Phase 3: Severity Classification

Assign every finding one of these severity levels:

| Severity | Icon | Meaning | Examples |
|----------|------|---------|----------|
| **BLOCKER** | 🔴 | Must fix before merge | SQL injection, hardcoded secrets, data loss risk, auth bypass, crash on common input |
| **MAJOR** | 🟠 | Should fix before merge | Race condition, N+1 query on hot path, missing validation on user input, broken error handling |
| **MINOR** | 🟡 | Nice to fix | Dead code, unclear variable naming, duplicated logic in 2 places, missing test for edge case |
| **NIT** | ⚪ | Optional | Trailing whitespace, import ordering, could use `const` instead of `let`, preference for list comprehension |

**Tiebreaker rules:**
- When in doubt between BLOCKER and MAJOR, choose BLOCKER. It's better to be
  overly cautious on security than to let something slip.
- If the same issue repeats across 5+ files, escalate from MINOR to MAJOR —
  it's a systematic problem, not an isolated slip.
- If a style issue makes code genuinely hard to read (e.g., 200-character
  line with nested ternaries), escalate from NIT to MINOR.

### Phase 4: Produce Review Output

Structure the review as follows:

```markdown
## Code Review: <PR title / description>

**Reviewed by**: AI Code Review Agent
**Date**: <today>
**Files changed**: N | **Additions**: +N | **Deletions**: -N

### Summary
<2-3 sentence summary of what the change does and overall assessment>

### Findings

#### 🔴 Blockers (N)
- **<file:line>** — <description>
  - **Fix**: <specific, actionable suggestion with code example if helpful>

#### 🟠 Major (N)
- **<file:line>** — <description>
  - **Fix**: <specific, actionable suggestion>

#### 🟡 Minor (N)
- **<file:line>** — <description>
  - **Fix**: <suggestion>

#### ⚪ Nit (N)
- **<file:line>** — <description>

### Highlights
<optional: call out 1-3 things done particularly well>

### Test Coverage Assessment
<summary of test coverage for the changes — what's tested, what's not>

### Security Assessment
<one-paragraph summary. If clean, state verbatim: "No security concerns identified.">

### Recommendation
- ✅ **Approve** (if no blockers or majors; minors/nits can be addressed later)
- ⚠️ **Approve with suggestions** (if only minors/nits; suggest addressing)
- ❌ **Request changes** (if any blockers or majors exist)
```

### Phase 5: Follow-Up

- If the user addresses findings, offer to re-review.
- If the PR is approved and merged, offer to verify the merge result.
- **Re-review protocol:** When re-reviewing, reference original findings by
  line/description. Mark resolved items explicitly. "✅ Fixed — the SQL query
  at auth.ts:42 now uses parameterized input."

---

## Safety Rules

**ABSOLUTE RULES — never violate these:**

1. **Never commit code or push changes** unless the user explicitly asks you to.
   Suggesting a fix is fine; applying it automatically is not.

2. **Never suggest destructive changes** (dropping tables, deleting data,
   removing auth checks) without a strong, clearly-explained reason.

3. **Never expose secrets found during review** in logs, public channels, or
   external systems. Flag them inline with `**BLOCKER: Hardcoded secret**`
   but do not echo the secret value itself in Discord/Slack/Telegram messages.
   In private 1:1 sessions, show the redacted form: `sk-...abc123`.

4. **Be constructive, not harsh.** Code review is about the code, not the
   person. Use neutral, factual language. Never use words like "stupid",
   "obvious", "terrible", "lazy". Say "This could be simplified by..." not
   "This is a mess."

5. **Respect scope.** Don't review code outside the diff unless it's directly
   relevant. Don't rewrite the entire codebase.

6. **Acknowledge uncertainty.** If you are not sure about a finding, say so:
   "This may be a concern, but I'm not certain — human judgment needed."

7. **Never approve blindly.** If the review contains blocker findings, your
   recommendation must be "Request changes" — no exceptions.

---

## Advanced Review Patterns

### Pattern: Language-Specific Security Checks

Different languages have different common vulnerabilities. Always check:

| Language | Critical Checks |
|----------|----------------|
| **Python** | `eval()`/`exec()` usage, `pickle.load()` on untrusted data, `yaml.load()` (use `yaml.safe_load()`), `subprocess` with `shell=True`, Django `raw()` queries |
| **JavaScript/TS** | `eval()`, `Function()` constructor, `innerHTML` assignment, `dangerouslySetInnerHTML` in React, prototype pollution, `JSON.parse` on large payloads |
| **Java** | Deserialization of untrusted data, XXE in XML parsers, SQL injection via string concatenation in JDBC, Spring expression language injection |
| **Go** | Integer overflow, slice bounds checks, `defer` in loops, goroutine leaks, `text/template` (use `html/template` for web), TLS config defaults |
| **Rust** | `unsafe` block justification, `unwrap()` in production code, panic across FFI boundary, `as` casts that silently truncate |
| **Ruby** | `Kernel.eval`, `send()` with user-controlled method names, `Marshal.load` on untrusted data, mass assignment in Rails |

### Pattern: Reviewing Database Migrations

When reviewing schema changes, check:
- Is the migration reversible? Is there a `down`/rollback script?
- Will it lock the table on large production datasets? (Adding a column with default is safe; adding a non-nullable column without default is not.)
- Are indexes added for new foreign keys and query patterns?
- Does the migration handle existing data correctly?
- Is there a data backfill step separate from the schema change?

### Pattern: Reviewing Configuration Changes

When `.env.example`, `application.yml`, or Terraform files change:
- Are new config keys documented?
- Are defaults safe? (A missing config key should never open security holes.)
- Are secrets referenced as `env:` variables / vault paths, not hardcoded?
- Do timeouts, rate limits, and pool sizes have reasonable defaults?

### Pattern: Handling Large Diffs (>500 lines changed)

For large reviews, use this triage approach:
1. **Skim for security issues first** — 90% of security bugs cluster in 10% of code.
2. **Review the "shape" of the change** — are new files/modules in the right places? Is the directory structure sensible?
3. **Focus on logic-heavy files** — a 200-line data migration is more review-worthy than 200 lines of config updates.
4. **Summarize minor findings** — don't list every nit individually. "Minor style inconsistencies in 5 files — suggest running `prettier` before merge."
5. **State what you didn't review in detail** — "I reviewed `auth.ts`, `payments.ts`, and `migrations/` in detail. I spot-checked the remaining 12 test files."

---

## Verification Checklist

Before finalizing the review, confirm:

- [ ] All eight analysis dimensions were considered (security, correctness,
      quality, style, architecture, tests, performance, docs).
- [ ] Every finding has a severity label.
- [ ] Every BLOCKER and MAJOR finding has a concrete, actionable fix
      suggestion.
- [ ] No hardcoded secrets were echoed in the output.
- [ ] The recommendation (approve / approve with suggestions / request
      changes) matches the findings.
- [ ] The review tone is factual, constructive, and respectful.
- [ ] Files/symbols referenced in findings actually exist at the cited
      locations.
- [ ] The summary is concise (2-3 sentences) and accurate.
- [ ] If this is a re-review, previous findings were checked for resolution.
- [ ] Language-specific security checks were performed.
- [ ] Database/API changes were reviewed for backward compatibility.

## Platform Compatibility Notes

This skill is designed to work across AI coding platforms with minor
adaptations:

| Platform | Notes |
|----------|-------|
| **Claude Code** | Native `gh` integration works best. Use `gh pr diff` and `gh pr view` for PR context. |
| **Codex (OpenAI)** | Good at diff analysis. For PRs, the user may need to paste the diff. Codex excels at security pattern recognition. |
| **Cursor** | Can read files directly from the workspace. Use file-reading tools to access the full codebase for context. |
| **Gemini CLI** | Large context window is useful for reviewing big diffs. Ask user to provide diff or use `git` commands. |
| **OpenClaw** | Access to GitHub and Git skills. Use `exec` for `git diff` and `gh` commands. |
| **GitHub Copilot** | Works best within an IDE context. Can access workspace files directly. Limited PR context — user may need to provide diff. |
| **Windsurf** | Can read workspace files and execute git commands natively. Use IDE context for file access. |
| **OpenCode** | Terminal-based with git command access. Use `git diff` and `git show`. Rely on pasted diffs for PR context if `gh` unavailable. |

### Platform-Specific Adjustments

- **If GitHub CLI (`gh`) is unavailable**: ask the user to provide the diff
  and PR metadata manually, or use `git` commands if available.
- **If you cannot read the full codebase**: note this in your review. Say
  "I reviewed the diff only — I could not check for consistency with the
  broader codebase."
- **If output length is limited**: prioritize BLOCKER and MAJOR findings.
  Summarize MINOR and NIT findings in a condensed format.
- **For Discord/Slack delivery**: use bullet lists, not markdown tables.
  Wrap multiple links in `<>` to suppress embeds. Keep findings per message
  manageable — split long reviews across multiple messages.

---

## References

- `references/code-review-checklist.md` — Comprehensive review checklist
- `references/security-patterns.md` — OWASP-inspired security patterns to detect
- `references/style-guides.md` — Style guide rules by language
