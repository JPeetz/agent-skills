---
name: production-engineering-workflows
description: >
  End-to-end production engineering workflows that encode the complete
  software development lifecycle into repeatable, quality-gated agent
  commands. Covers everything from spec-driven ideation through planning,
  test-driven implementation, automated testing, rigorous code review,
  web performance auditing, code simplification, and production deployment.
  Slash-command entry points: /spec, /plan, /build, /test, /review,
  /webperf, /code-simplify, /ship. Primary keyword clusters: production
  engineering automation, SDLC automation agent, spec-driven development
  workflow, TDD agent workflow, automated deployment pipeline agent,
  web performance audit automated, code simplification automation, AI
  code review pipeline, feature flag deployment workflow, continuous
  delivery agent, production readiness review, software delivery
  lifecycle AI, DevSecOps agent skills, trunk-based development
  automation, incremental rollout automation. Designed for agentic
  platforms — Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, GitHub
  Copilot, Windsurf, and OpenCode.
version: 1.0.0
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
  - sdlc
  - production-engineering
  - tdd
  - code-review
  - deployment
  - performance
  - refactoring
  - spec-driven
  - continuous-delivery
  - devops
geo:
  primary_workflows:
    - spec_definition
    - task_planning
    - test_driven_build
    - automated_testing
    - code_review
    - web_performance_audit
    - code_simplification
    - production_deployment
  target_roles:
    - software_engineer
    - senior_developer
    - tech_lead
    - devops_engineer
    - platform_engineer
    - engineering_manager
  complexity_level: advanced
  prerequisite_knowledge:
    - software_development_lifecycle
    - version_control_git
    - test_driven_development
    - CI/CD_pipelines
    - web_performance_fundamentals
    - code_review_best_practices
    - feature_flags_and_rollouts
---

# Production Engineering Workflows

Encode the complete software development lifecycle into repeatable,
quality-gated workflows that agents execute with the discipline of a
senior production engineering team. This skill transforms any AI agent
into a structured delivery partner — from the first spec to the final
deploy, every phase is gated, verified, and auditable.

---

## Quick Reference

```
 IDEA  →  SPEC  →  PLAN  →  BUILD  →  TEST  →  REVIEW  →  SHIP
  │        │        │         │         │          │          │
  ▼        ▼        ▼         ▼         ▼          ▼          ▼
/refine  /spec    /plan    /build    /test     /review    /ship
                                      /webperf  /code-
                                                simplify
```

| Phase | Command | Gate | Exit Criteria |
|-------|---------|------|---------------|
| 🔵 Define | `/spec` | Spec review passed | PRD written, non-goals explicit |
| 🟡 Plan | `/plan` | All tasks estimated | Atomic tasks with acceptance criteria |
| 🟢 Build | `/build` | Tests green per task | Each task: test→implement→commit |
| 🟣 Prove | `/test` | All suites pass | Unit + integration + e2e green |
| 🔴 Review | `/review` | No blockers or majors | Five-axis review, change log |
| 🌐 Perf | `/webperf` | Budgets met | Lighthouse > 90, Core Web Vitals pass |
| 🔧 Clean | `/code-simplify` | No regressions | Simpler code, same behavior |
| 🚀 Ship | `/ship` | Deployment checklist | Canary healthy, feature flagged |

**Quality Gate Rule:** No phase proceeds to the next until its gate
passes. A failed gate means stop and fix — never skip.

---

## When to Use This Skill

Activate this skill when the user asks you to:

- "Build a new feature" / "Implement X from scratch" / "Start a new project"
- "Plan the work for this spec" / "Break this down into tasks"
- "Deploy to production" / "Ship this change" / "Push to prod"
- "Run the performance audit" / "Check Core Web Vitals"
- "Simplify this code" / "Clean up this module" / "Refactor without breaking"
- "Walk me through the SDLC" / "What's the right way to ship this?"
- "Set up CI/CD for this project" / "Automate the deploy pipeline"
- "How do I make this production-ready?"

Additionally, activate proactively when:
- A conversation spans multiple phases of development and needs structured
  workflow management.
- The user is about to merge or deploy and hasn't followed a review/test
  workflow.
- Code quality or performance issues are surfacing repeatedly — suggest
  the relevant command as a gate.

### Do NOT Activate For

The following inputs are **near-miss negatives** — they sound like
workflow requests but are not production engineering concerns:

- **Trivial one-liner changes**: "Change this string constant" — not a
  workflow, just a direct edit. No need for spec/plan/deploy cycle.
- **Purely conversational tech discussion**: "What's the best way to
  structure a React app?" — opinion/advice, not a build task.
- **Code explanation**: "What does this regex do?" — teaching, not building.
- **Documentation-only work**: "Write a README for this module" — no
  production change to ship.
- **Debugging a single bug with known fix**: "This function returns the
  wrong sign, swap the `>` for `<`" — trivial fix, not a workflow.
- **Data exploration**: "Query the DB and tell me how many users signed
  up today" — analysis, not engineering.
- **Third-party service configuration**: "Set up a new GitHub repo" —
  admin task, not a production code change.
- **Experimental spike/prototype**: "Let me try a few ideas and see what
  works" — exploration, not delivery. (Use `/spec` only after the spike
  when committing to build.)

If uncertain, ask: "This looks like it could use a structured workflow.
Would you like me to start with `/spec`, or is this more of an ad-hoc
change?"

---

## Workflow Commands

Each command is a self-contained phase. They can be used independently
or as a complete pipeline. When chaining, respect gate rules — never
skip a phase whose gate is red.

### /spec — Define What to Build

**Principle: Spec before code.** Write the specification before writing
any implementation. The spec is the source of truth for everything that
follows.

#### Input Sources

- User's natural language description of the feature or change.
- Existing project documentation, README, or architecture docs.
- Issue tracker tickets (GitHub Issues, Jira, Linear).
- Product requirements documents or user stories.

#### Specification Template

Generate a specification covering:

```markdown
## Feature Specification: <Title>

### Problem Statement
<1-2 sentences: What problem does this solve? For whom?>

### Proposed Solution
<High-level approach. Technology choices. Architectural decisions.>

### Functional Requirements
1. <Requirement — testable, unambiguous>
2. <Requirement>
...

### Acceptance Criteria (BDD Format)
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>

### Non-Goals (Explicit Scope Boundaries)
- We are NOT doing X
- We are NOT changing Y

### Dependencies
- Requires: <library/service/team>
- Blocks: <nothing / ticket #Z>

### Success Metrics
- <Measurable outcome — e.g., "API response p95 < 200ms">

### Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| ...  | ...    | ...        |

### Timeline Estimate
- <Rough sizing: S/M/L/XL. Not a commitment, a planning input.>
```

#### Spec Review Gates

Before `/plan` can begin, the spec must pass these gates:

- [ ] **Completeness**: Every functional requirement is testable.
- [ ] **Clarity**: A new team member could read it and understand the goal.
- [ ] **Bounded scope**: Non-goals are explicit. No scope creep on day one.
- [ ] **Dependency check**: All dependencies are known and available.
- [ ] **Risk awareness**: At least one risk is identified and mitigated.
- [ ] **Stakeholder alignment**: If the user is not the sole stakeholder,
      ask: "Has this been reviewed by <name>?"

#### Anti-Patterns

- **Writing a novel**: The spec should be 1-3 pages, not 50. It's a
  blueprint, not the building.
- **Premature implementation details**: "Use a hash map with quadratic
  probing" belongs in `/plan` or `/build`, not `/spec`.
- **No non-goals**: A spec without non-goals is an invitation to scope
  creep. Always define what you won't do.
- **Vague acceptance criteria**: "It should work well" is not testable.
  Use BDD format.

---

### /plan — Plan How to Build It

**Principle: Small, atomic tasks.** Decompose the spec into the smallest
verifiable units of work. Each task must be independently buildable,
testable, and committable.

#### Task Decomposition Rules

1. **Atomic**: One task = one clear change. If you can't describe it in
   one sentence, split it.
2. **Verifiable**: Every task has a concrete acceptance test. "Task done"
   means the test passes.
3. **Ordered**: Tasks list dependencies explicitly. No circular deps.
4. **Small**: A task should take 15-60 minutes. If it takes longer,
   split further.
5. **Committable**: Each task produces a clean, green commit.

#### Task Template

```markdown
### Task N: <Short Title>
- **Depends on**: Task N-1, Task N-3 (or "None")
- **Files affected**: src/foo.ts, tests/foo.test.ts
- **Description**: <What to build. 1-2 sentences.>
- **Acceptance**: <BDD format — Given/When/Then>
- **Estimated effort**: <S:15min / M:30min / L:60min>
- **Risk level**: <Low / Medium / High>
- **Rollback plan**: <How to undo if it goes wrong>
```

#### Example Task Breakdown

```markdown
Spec: User email verification on signup

Task 1: Add `email_verified` column to users table
  - Files: migrations/004_email_verified.sql
  - Acceptance: Column exists, default=false, not null
  - Effort: S | Risk: Low | Rollback: Down migration

Task 2: Generate verification token on user create
  - Depends on: Task 1
  - Files: src/services/user_service.ts
  - Acceptance: Token is crypto-random, stored with user, expires in 24h
  - Effort: M | Risk: Low | Rollback: Revert commit

Task 3: Send verification email
  - Depends on: Task 2
  - Files: src/services/email_service.ts, src/templates/verify.html
  - Acceptance: Email sent with valid link containing token
  - Effort: M | Risk: Medium | Rollback: Disable email send in config

Task 4: Verify endpoint — mark user as verified
  - Depends on: Task 2
  - Files: src/routes/verify.ts
  - Acceptance: GET /verify?token=X marks user verified, redirects
  - Effort: M | Risk: Low | Rollback: Revert route

Task 5: Gate login on email_verified
  - Depends on: Task 4
  - Files: src/services/auth_service.ts
  - Acceptance: Unverified users get 403 with "verify email" message
  - Effort: S | Risk: Medium | Rollback: Feature flag off
```

#### Plan Review Gates

- [ ] All tasks are atomic and independently verifiable.
- [ ] No task exceeds 60-minute estimate.
- [ ] Dependency ordering is correct and acyclic.
- [ ] Every task has acceptance criteria in BDD format.
- [ ] High-risk tasks have explicit rollback plans.
- [ ] The plan covers all functional requirements from the spec.

#### Anti-Patterns

- **The monolith task**: "Implement user email verification" as one
  task. This hides complexity and makes rollback impossible.
- **Tasks without acceptance criteria**: "Refactor the service layer" —
  how do you know when you're done?
- **Ignoring dependencies**: Building the verification endpoint before
  the token generation exists.
- **Gold-plating**: Adding "also improve the logging framework" to a
  feature plan. Separate concerns.

---

### /build — Build Incrementally (Test-Driven)

**Principle: One slice at a time, test-first.** Implement each planned
task using the Red-Green-Refactor cycle. Every task produces its own
clean, green commit.

#### Build Cycle Per Task

```
TEST FIRST → WATCH IT FAIL → IMPLEMENT → WATCH IT PASS → REFACTOR → COMMIT
    │              │               │             │           │          │
    ▼              ▼               ▼             ▼           ▼          ▼
  Write the    Confirm the     Write the     Confirm      Clean up    Atomic
  test case    test fails      minimal       tests        the code    commit
  first        (red)           code to    pass (green)   without     with
                               pass it                   changing    message
                                                         behavior
```

#### Commit Convention

Every task commit follows this format:

```
<type>(<scope>): <short description>

<optional body — what and why>

Task: <task number> / <total tasks>
Acceptance: <BDD>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`

#### Build Rules

1. **Test first. Always.** No implementation code without a failing test
   first. The only exception is pure config/boilerplate.
2. **Minimal implementation.** Write only the code needed to make the
   test pass. No "I might need this later."
3. **One commit per task.** If you need two commits, split the task.
4. **Green before moving on.** Never start Task N+1 if Task N's tests
   are red.
5. **Commit on green, not on red.** Never commit failing tests to main.
   Feature branches can hold red tests temporarily.
6. **Small commits.** Each commit should be reviewable in under 5
   minutes.

#### Build Gates (Per Task)

- [ ] Tests written first and observed failing (red).
- [ ] Implementation written (minimal, correct).
- [ ] All tests passing (green) — not just the new ones, the full suite.
- [ ] Any dead code or debug logging removed.
- [ ] Commit message follows convention.
- [ ] No unrelated changes crept in ("while I'm here...").

#### Common Build Pitfalls

- **Skipping the red phase**: If you write the test and it passes
  immediately, either the test is wrong or the code already does it.
  Investigate before proceeding.
- **Implementing more than the test requires**: Over-engineering at the
  task level. Build exactly what the test demands, then iterate.
- **Mixing concerns**: A "feat" commit that also refactors unrelated
  code. Separate PRs for separate concerns.
- **Large commits**: A commit touching 15 files is not a task, it's a
  feature. Split it.

---

### /test — Prove It Works

**Principle: Tests are proof, not decoration.** Every piece of behavior
has a test that proves it works. Tests are the living specification of
the system.

#### Test Pyramid

```
         ╱  E2E  ╲          ~5%  — Critical user journeys
        ╱─────────╲
       ╱Integration ╲       ~15% — Service boundaries, DB, APIs
      ╱───────────────╲
     ╱   Unit Tests    ╲     ~80% — Logic, edge cases, pure functions
    ╱───────────────────╲
```

#### Test Types & When to Use

| Type | Scope | Speed | When |
|------|-------|-------|------|
| **Unit** | Single function/module | <10ms | Logic, calculations, validation, transformation |
| **Integration** | Service + DB/API/Cache | <500ms | Repository layer, API handlers, middleware |
| **E2E** | Full user journey | 1-30s | Signup flow, checkout, critical paths |
| **Snapshot** | UI component output | <100ms | Component rendering (review changes carefully) |
| **Property-based** | Invariants over random inputs | varies | Data structures, parsers, serializers |
| **Performance** | Throughput/latency thresholds | seconds | Hot paths, endpoints, expensive queries |

#### Test Quality Standards

**Good tests are DAMP** (Descriptive And Meaningful Phrases) — not DRY
(Don't Repeat Yourself). Readability beats cleverness in tests.

```typescript
// ❌ DRY test — hides intent behind abstractions
const user = createTestUser();
const result = service.processUser(user, { flag: true });
assertResult(result, { status: 'active', processed: true });

// ✅ DAMP test — the story is explicit
it('activates a verified user when the feature flag is on', () => {
  const verifiedUser = new User({ verified: true, status: 'pending' });
  const result = activationService.process(verifiedUser, { newFlow: true });
  expect(result.status).toBe('active');
  expect(result.processed).toBe(true);
  expect(result.activatedAt).toBeInstanceOf(Date);
});
```

**The Beyoncé Rule:** If you liked it then you should have put a test
on it. Every code change must either:
- Have a test, OR
- Be a refactoring that changes no behavior (and existing tests pass), OR
- Be explicitly excluded (config, docs, formatting).

#### Test Gates

- [ ] Test pyramid ratios are approximately correct (80/15/5).
- [ ] All unit tests pass (<10s total).
- [ ] All integration tests pass (<60s total).
- [ ] All E2E tests pass (critical paths only).
- [ ] New code has corresponding tests (Beyoncé Rule).
- [ ] No flaky tests — if a test fails intermittently, fix or remove it.
- [ ] Test coverage on changed lines is ≥80% (if measurable).
- [ ] Edge cases are tested: null, empty, boundary values, errors.

#### Anti-Patterns

- **Testing the framework, not your code**: `expect(1+1).toBe(2)` tests
  JavaScript arithmetic, not your business logic.
- **Tests without assertions**: A test that runs code but never checks
  anything is worse than no test — it creates false confidence.
- **Mocking everything**: If every dependency is mocked, you're testing
  a hollow shell. Balance mocks with integration tests.
- **Flaky tests in CI**: A test that passes "most of the time" erodes
  trust in the whole suite. Fix or quarantine.
- **Testing implementation details**: "It calls the `validateEmail`
  helper" — test the outcome, not the internal plumbing.

---

### /review — Review Before Merge

**Principle: Improve code health systematically.** Every change is
reviewed across five axes: security, correctness, quality, architecture,
and performance. No change merges with blocker or major findings.

#### Five-Axis Review

| Axis | Questions |
|------|-----------|
| **🔴 Security** | Injection risks? Secrets exposed? Auth bypass? Input validated? |
| **🟠 Correctness** | Logic errors? Edge cases? Error handling? Race conditions? |
| **🟡 Quality** | Readable? DRY violations? Appropriate naming? Dead code? |
| **🏗️ Architecture** | Fits existing patterns? SRP respected? Tight coupling? Circular deps? |
| **⚡ Performance** | Algorithmic complexity? N+1 queries? Memory pressure? Unnecessary I/O? |

#### Severity Scale

| Severity | Action |
|----------|--------|
| 🔴 **BLOCKER** | Must fix before merge. Security, data loss, crash, broken core. |
| 🟠 **MAJOR** | Should fix before merge. Bug, significant perf, pattern violation. |
| 🟡 **MINOR** | Nice to fix. Code smell, minor duplication, unclear naming. |
| ⚪ **NIT** | Optional. Style preference, formatting, personal taste. |

**Decision rule:**
- Any BLOCKER or MAJOR → ❌ Do not merge.
- Only MINOR and NIT → ⚠️ Approve with suggestions.
- No findings → ✅ Approved.

#### Review Gates

- [ ] Five-axis review completed for all changed files.
- [ ] All BLOCKER findings addressed with concrete fixes.
- [ ] All MAJOR findings either fixed or explicitly deferred with a ticket.
- [ ] No secrets echoed in the review output.
- [ ] Change is appropriately sized (ideally ≤400 lines; >400 requires justification).
- [ ] Test coverage on changed code is adequate.
- [ ] Review output includes an explicit merge recommendation.

#### Review Anti-Patterns

- **Rubber-stamping**: "LGTM" without reading the diff. Never.
- **Reviewing code you haven't fully read**: Read the entire diff.
  Context from line 120 might explain line 15.
- **Nit-picking without substance**: Don't drown the author in
  formatting nits when there are real bugs.
- **Scope creep**: Review the diff, not the codebase. Flag related
  concerns as separate issues.
- **Harsh language**: "This is broken" → "This could return null,
  causing a TypeError on line 45."

---

### /webperf — Audit Web Performance

**Principle: Measure before you optimize.** Run a structured performance
audit using Lighthouse, Core Web Vitals, and runtime profiling. Every
finding comes with a measurement, not a guess.

#### Audit Dimensions

| Dimension | Tool | Budget/Threshold |
|-----------|------|-----------------|
| **LCP** (Largest Contentful Paint) | Lighthouse / CrUX | <2.5s (good), <4.0s (needs work) |
| **INP** (Interaction to Next Paint) | Lighthouse / CrUX | <200ms (good), <500ms (needs work) |
| **CLS** (Cumulative Layout Shift) | Lighthouse / CrUX | <0.1 (good), <0.25 (needs work) |
| **TTFB** (Time to First Byte) | WebPageTest | <800ms |
| **JS Bundle Size** | webpack-bundle-analyzer | <200KB gzipped per route |
| **Image Waste** | Lighthouse image audit | All images appropriately sized |
| **Render-Blocking** | Lighthouse | Critical CSS inlined, non-critical deferred |
| **Runtime Performance** | Chrome DevTools Profiler | No long tasks >50ms on main thread |

#### Audit Workflow

1. **Measure**: Run Lighthouse on the changed pages (mobile + desktop).
2. **Profile**: Use browser DevTools to record runtime performance.
3. **Analyze Bundle**: If JS/CSS changed, analyze bundle size change.
4. **Compare**: Show before/after for each metric if baseline exists.
5. **Recommend**: For every metric below threshold, provide a concrete
   fix with estimated impact.

#### Performance Gates

- [ ] LCP < 2.5s on mobile (or no regression from baseline).
- [ ] CLS < 0.1 on mobile.
- [ ] INP < 200ms on mobile.
- [ ] No long tasks (>50ms) introduced.
- [ ] Bundle size did not increase by >10% without justification.
- [ ] All images are correctly sized and use modern formats (WebP/AVIF).
- [ ] No render-blocking resources blocking FCP.

#### Anti-Patterns

- **Optimizing without measuring**: "This loop looks slow, let me cache
  it." Measure first. You might be fixing the wrong thing.
- **Micro-optimizations at the expense of readability**: Saving 2ms on
  a non-interactive page by making the code unreadable.
- **Ignoring mobile**: Desktop-only performance testing misses the
  majority of users. Always measure mobile first.
- **Adding libraries for minor gains**: A 50KB library to save 1KB of
  custom code is a net loss.

---

### /code-simplify — Simplify Without Breaking

**Principle: Clarity over cleverness.** Reduce complexity while
preserving exact behavior. Every simplification is verified by tests,
not assumptions.

#### Chesterton's Fence

Before removing or simplifying anything, understand **why it exists**.
Chesterton's Fence: "Don't remove a fence until you know why it was put
up." If the reason is not obvious, investigate before removing.

#### Simplification Targets

| Pattern | Simplification |
|---------|---------------|
| Deep nesting (>4 levels) | Early returns, guard clauses, extract functions |
| Long functions (>50 lines) | Extract cohesive sub-functions |
| Complex conditionals | Replace with lookup tables, strategy pattern, or boolean decomposition |
| Duplicated logic | Extract shared function (only if truly identical) |
| Over-abstracted code | Inline unnecessary indirection |
| Dead code/commented-out code | Remove (git history preserves it) |
| Magic numbers/strings | Replace with named constants |
| Overly clever one-liners | Expand to readable multi-line with intent comments |

#### Simplification Workflow

1. **Identify**: Find the complexity hotspot (long function, deep
   nesting, duplicated logic).
2. **Verify behavior**: Ensure existing tests cover the code being
   simplified. If not, add characterization tests first.
3. **Simplify in small steps**: One refactoring move at a time. Each
   step is committable and verified by tests.
4. **Run full test suite after each step**: Never batch refactorings.
   If tests break, you know exactly which step caused it.
5. **Compare before/after**: Show the complexity reduction (lines,
   cyclomatic complexity, nesting depth).

#### Simplification Gates

- [ ] Behavior is identical (all tests pass, no new failures).
- [ ] Code is measurably simpler (fewer lines, lower complexity, shallower nesting).
- [ ] No new abstractions introduced unless they genuinely reduce complexity.
- [ ] Chesterton's Fence satisfied — removed code was understood and justified.
- [ ] No performance regression (run perf tests if applicable).
- [ ] Commit message explains **why** the simplification improves the code.

#### Anti-Patterns

- **Refactoring without test coverage**: You're not simplifying, you're
  rewriting with a blindfold.
- **Big-bang refactoring**: "Let me just restructure the entire module
  in one go." Incremental or nothing.
- **Adding abstraction instead of removing it**: Simplifying doesn't
  mean "wrap it in another layer." Often it means the opposite.
- **Changing behavior during simplification**: The only acceptable
  behavior change is fixing a bug found during simplification — and
  that gets its own commit.

---

### /ship — Deploy to Production

**Principle: Faster is safer.** Deploy frequently in small batches.
Every deployment is behind a feature flag, with monitoring, a rollback
plan, and a defined blast radius.

#### Pre-Deployment Checklist

- [ ] All tests pass on the CI pipeline — unit, integration, E2E.
- [ ] Code review complete with no BLOCKER findings.
- [ ] Performance audit shows no regressions.
- [ ] Database migrations tested against production-sized dataset
      (or staging replica).
- [ ] New feature is behind a feature flag (if any risk).
- [ ] Monitoring dashboards/alerting configured for new behavior.
- [ ] Runbook updated with new error patterns and mitigation steps.
- [ ] Rollback plan documented and tested in staging.
- [ ] Deployment window communicated (if applicable).
- [ ] On-call engineer notified (if applicable).

#### Deployment Strategy Selection

| Strategy | When to Use | Risk Level |
|----------|-------------|------------|
| **Direct deploy** | Trivial config/typo fixes, zero-risk changes | None |
| **Feature flag** | New features, behavioral changes, refactors | Low-Medium |
| **Canary deploy** | Performance-sensitive changes, new infrastructure | Medium |
| **Blue-green** | Database migrations, breaking schema changes | Medium-High |
| **Percentage rollout** | ML model updates, algorithm changes | Medium-High |
| **Dark launch** | New services, major architecture changes | High |

#### Canary Deployment Workflow

1. **Deploy to canary** (1-5% of traffic).
2. **Monitor for N minutes** (error rate, latency, saturation — USE method).
3. **If healthy**: Increase to 25%, monitor again.
4. **If healthy**: Increase to 100%.
5. **If unhealthy at any stage**: Roll back canary. Do not wait.
   Time to rollback should be measured in seconds, not minutes.

#### Monitoring Gates (Post-Deploy)

- [ ] Error rate within normal bounds (±2 standard deviations).
- [ ] P95/P99 latency within normal bounds.
- [ ] No new alerts triggered.
- [ ] Business metrics unaffected (conversion rate, signups, payments).
- [ ] Feature flag validation: new feature works for enabled users,
      nothing changes for disabled users.

#### Rollback Plan Template

```markdown
### Rollback Plan: <Change>

**Trigger**: Error rate >X%, latency p95 >Yms, or <specific alert name>
fires for >Z minutes.

**Action**: Revert commit <sha> or deploy previous version <tag>.
**Recovery time**: <N> minutes (automated / manual).
**Data rollback**: <Migration is reversible / no data change / manual
  script at scripts/rollback_xxx.sh>.
**Communication**: Notify #incidents channel. Update status page.
```

#### Anti-Patterns

- **Friday afternoon deployments**: The "read-only Friday" rule exists
  for a reason. Changes that break won't be noticed until Monday.
- **Deploying without a rollback plan**: If you can't roll back in
  under 5 minutes, you shouldn't deploy.
- **Big-bang releases**: Deploying 2 weeks of work in one push.
  Deploy daily, even if features are hidden.
- **No feature flags**: Coupling deployment from release is table stakes
  for production engineering.
- **Assuming staging == production**: Data volume, traffic patterns,
  edge cases — they differ. Monitor production specifically.
- **Alert fatigue**: Alerts that fire constantly and are ignored are
  worse than no alerts. They create noise that hides real issues.

---

## Integrated Pipeline: End-to-End

When the user wants to go from idea to production in one flow, chain
the commands:

```
/spec → /plan → /build (repeated per task) → /test → /review → /webperf → /code-simplify → /ship
```

**Gate enforcement at each phase:**

```
/spec     → Spec review gates ALL pass → proceed to /plan
/plan     → Plan review gates ALL pass → proceed to /build
/build    → Each task: red→green→commit → proceed to /test
/test     → All suites green            → proceed to /review
/review   → No BLOCKERS, no MAJORS      → proceed to /webperf
/webperf  → Budgets met                 → proceed to /code-simplify
/code-simplify → No regressions         → proceed to /ship
/ship     → Canary healthy              → Deployment complete
```

If any gate fails, the pipeline stops. The agent reports the failure
clearly: "Pipeline halted at `/review` — BLOCKER: SQL injection risk
in `src/search.ts:42`. Fix and re-run `/review` before proceeding."

---

## Common Pitfalls Across All Phases

### System-Level Anti-Patterns

1. **Skipping gates "because it's urgent"**: Urgency amplifies the
   cost of failure. The gates exist precisely to prevent the disasters
   that happen when we rush.

2. **Mixing phases**: Writing code during `/spec`, reviewing during
   `/build`, deploying before `/test`. Each phase has a purpose.
   Respect the boundaries.

3. **Vague exit criteria**: "It looks good" is not a gate. Every gate
   has explicit, binary criteria. Pass or fail — no maybe.

4. **Trusting the agent blindly**: The agent is a tool, not an
   authority. Review its output. Question its decisions. The agent
   follows the process; you're responsible for the outcome.

5. **Ignoring near-miss negatives**: Activating the full SDLC pipeline
   for a one-line config change is overhead, not engineering. Match
   the workflow to the risk.

6. **Feature flag abuse**: Feature flags that live for 6 months become
   technical debt. Every flag should have an owner and an expiry date.

7. **Alert fatigue**: Every alert should demand action. If an alert
   fires and the response is "yeah, it does that sometimes," remove or
   tune it.

8. **One-size-fits-all deployment**: A typo fix doesn't need canary
   deployment. A database migration does. Calibrate the strategy to
   the risk.

---

## Safety Rules

**ABSOLUTE RULES — never violate these:**

1. **Never skip a gate without explicit user approval.** If the user
   says "just deploy it, skip the review," say: "I can deploy without
   review, but this bypasses the safety gates. The change includes
   <N> modified files and <risk assessment>. Are you sure?" Document
   the override.

2. **Never deploy without a verified rollback plan.** Even if it's
   "revert the commit." The rollback must be tested or trivially
   executable.

3. **Never commit secrets.** Before every commit, scan for API keys,
   tokens, passwords, private keys. Use automated scanning where
   available.

4. **Never destroy data without a backup.** Schema changes, data
   migrations, bulk deletes — verify a recent backup exists before
   executing.

5. **Never deploy on unverified CI.** If the CI pipeline is red for
   any reason other than a known, documented flaky test, halt the
   pipeline.

6. **Never override production safety mechanisms without
   justification.** Read-only mode, rate limits, circuit breakers,
   auth gates — these exist for a reason.

7. **Be transparent about uncertainty.** If the agent is unsure about
   deployment risk, context switching, or rollback safety, state it
   explicitly. "I have medium confidence in this deployment. The risk
   areas are <X>. Human judgment needed."

8. **Respect team conventions.** If the team uses a different branch
   naming, commit format, or deploy workflow, adapt. Don't impose the
   skill's defaults over established team practice.

---

## Verification Checklist

Before finalizing any workflow execution, confirm:

- [ ] The correct command was activated for the task scope.
- [ ] All gates for the current phase have been checked.
- [ ] No gate was skipped without explicit user override.
- [ ] Output includes explicit pass/fail for each gate.
- [ ] If a gate failed, the output includes actionable next steps.
- [ ] The user was informed of any risks or uncertainties.
- [ ] Commit messages follow the project's conventions.
- [ ] No secrets, PII, or sensitive data in output.
- [ ] Feature flags are documented with owner and expiry.
- [ ] The rollback plan is current and tested.

---

## Platform Compatibility Notes

This skill is designed to work across AI coding platforms. Adaptations:

| Platform | Notes |
|----------|-------|
| **Claude Code** | Native `gh` integration. Use `gh pr` commands. Plugin marketplace install available. Slash commands map naturally. |
| **Codex (OpenAI)** | Good at structured task decomposition. For git operations, the user may need to run commands manually. Provide the commands to run. |
| **Cursor** | Can read/write workspace files directly. Use IDE context for file references. Slash commands work as custom rules. |
| **Gemini CLI** | Large context window excels at spec generation. Use native skill installation. Git via shell commands. |
| **OpenClaw** | Access to GitHub and Git skills. Use `exec` for CLI operations. Slash commands as skill triggers. |
| **GitHub Copilot** | Works within IDE context. Can access workspace files. Use `.github/copilot-instructions.md` for workflow rules. |
| **Windsurf** | Native workspace file access. Add skill as Windsurf rules. Git commands via terminal. |
| **OpenCode** | Terminal-based with git/shell access. AGENTS.md integration. Skill tool for workflow activation. |

### Platform-Specific Adjustments

- **If shell commands are unavailable**: Provide the exact commands for
  the user to run manually, with clear expected outputs.
- **If CI/CD integration is limited**: Document the pipeline steps and
  let the user configure CI manually.
- **If performance audit tools are unavailable**: Focus on static
  analysis — bundle size estimation, complexity analysis, image size
  checks — and provide recommendations for manual verification.
- **If feature flags are not configured**: Recommend a simple env-var
  toggle pattern as fallback. Document the migration path to a proper
  feature flag system.
- **For Discord/Slack delivery**: Use bullet lists, not tables. Wrap
  links in `<>`. Split long outputs across messages.

---

## References

- `references/sdlc-patterns.md` — SDLC best practices and anti-patterns
- `scripts/validate_skill.py` — Validation script for SKILL.md compliance
- `evals/test_cases.json` — Evaluation cases with near-miss negatives

### External References

- [DORA DevOps Capabilities](https://dora.dev/capabilities/) — Research-backed DevOps practices
- [Google SRE Book](https://sre.google/books/) — Production engineering fundamentals
- [Web Core Vitals](https://web.dev/vitals/) — Performance measurement standards
- [Trunk-Based Development](https://trunkbaseddevelopment.com/) — Branching strategy
- [Feature Toggles (Martin Fowler)](https://martinfowler.com/articles/feature-toggles.html) — Feature flag patterns
- [Chesterton's Fence](https://en.wikipedia.org/wiki/Wikipedia:Chesterton%27s_fence) — The principle behind `/code-simplify`
- [RFC 7807 — Problem Details](https://www.rfc-editor.org/rfc/rfc7807) — Error response standard
- [The Test Pyramid (Martin Fowler)](https://martinfowler.com/bliki/TestPyramid.html) — Test strategy