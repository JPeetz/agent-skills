# SDLC Patterns & Best Practices

A reference guide to software development lifecycle patterns, anti-patterns,
and production engineering best practices. Used by the Production Engineering
Workflows skill to ground every command in established engineering knowledge.

---

## The Core SDLC Loop

```
    ┌──────────────────────────────────────────────┐
    │                                              │
    ▼                                              │
  SPECIFY ──► PLAN ──► BUILD ──► TEST ──► REVIEW ──┤
                                              │     │
                                              ▼     │
                                            SHIP ───┘
```

Each phase gates the next. The loop is continuous — shipping feeds data
back into specifying through metrics, incidents, and user feedback.

---

## Spec-Driven Development

### Why Spec First?

Writing code before defining what to build is the most common source of
rework in software engineering. A spec forces clarity before investment.

**Research backing:**
- DORA research: teams with lightweight specification practices deploy
  2.5x more frequently.
- Standish Group: unclear requirements are the #1 cause of project failure.
- NASA SEL: every dollar spent on requirements engineering saves $10-100
  downstream.

### The Rule of Three

A spec should answer exactly three questions:

1. **What** problem does this solve? (Problem statement)
2. **How** will we solve it? (Proposed solution, at architecture level)
3. **When** is it done? (Acceptance criteria, measurable)

If you can't answer all three, the spec isn't ready.

### Spec Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| **The Novel** | 50-page spec with pseudocode | Trim to 1-3 pages. Pseudocode goes in `/plan`. |
| **The Wish List** | "And also it should automatically..." — scope creep during spec | Move to non-goals. Create a separate spec. |
| **The Crystal Ball** | "In phase 3, we'll migrate to microservices" | Only spec what you're building now. YAGNI. |
| **The Vacuum** | No mention of existing system, dependencies, or constraints | Add dependencies section. Ground in reality. |

---

## Task Planning & Decomposition

### The Atomic Task Principle

A task is atomic when:
- It cannot be split further without losing coherence.
- It has one clear acceptance criterion.
- It can be implemented, tested, and committed independently.

### Estimation Heuristics

| Size | Time | Lines Changed | Risk |
|------|------|---------------|------|
| **XS** | <15 min | <10 lines | Trivial — typo, config, constant |
| **S** | 15-30 min | 10-50 lines | Low — single function, simple endpoint |
| **M** | 30-60 min | 50-150 lines | Medium — new component, migration, integration |
| **L** | 1-2 hours | 150-400 lines | High — new service, complex algorithm |
| **XL** | >2 hours | >400 lines | Split it — this is a feature, not a task |

**The 400-line rule:** If a task produces more than 400 lines of diff,
split it. Reviewers cannot effectively review larger changes, and
rollback becomes riskier.

### Dependency Ordering

```
Task A (no deps) ──► Task B (depends on A) ──► Task D (depends on B)
                  └─► Task C (depends on A) ──┘

Critical path: A → B → D (longest chain)
Parallelizable: B and C (independent after A)
```

Always identify the critical path. Parallelize where possible.

---

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

```
RED:    Write a failing test that defines the desired behavior.
        Stop. Do not write implementation code yet.

GREEN:  Write the minimum code to make the test pass.
        No more. No "I might need this later."

REFACTOR: Improve the code structure without changing behavior.
          Tests stay green throughout.
```

### Why TDD?

- **Forces testability.** Code written after tests is inherently testable.
- **Prevents over-engineering.** You only write code that tests demand.
- **Creates a safety net.** Every line of behavior is covered.
- **Enables fearless refactoring.** You know within seconds if you broke something.

### Common TDD Objections & Responses

| Objection | Response |
|-----------|----------|
| "TDD slows me down" | Writing tests after code takes longer (you have to reverse-engineer testability). Net time is the same or better with TDD. |
| "I don't know the design yet" | TDD helps you discover the design. Writing tests first clarifies the interface. |
| "This code is too simple to test" | If it's trivial, the test is trivial. If the test is hard, the design is telling you something. |
| "UI code can't be tested" | Component tests, snapshot tests, and E2E tests all work for UI. The hard part was never testing — it was testable architecture. |

### Test Pyramid (80/15/5)

```
Unit tests (80%):    Fast, isolated, run on every save.
                     Test pure logic, algorithms, validation.

Integration tests (15%): Test how units connect.
                         Database, API, cache, file system.

E2E tests (5%):      Test critical user journeys.
                     Signup, login, checkout, core flows.
```

The pyramid is a heuristic, not a law. Adjust ratios based on the system.
A data pipeline may need more integration tests; a UI library may need
more snapshot/e2e tests.

### Test Quality: DAMP over DRY

Tests should be **DAMP** (Descriptive And Meaningful Phrases), not DRY.

```python
# ❌ DRY test — clever, unreadable, hides intent
def run_scenario(amount, balance, expected):
    acct = Account(balance)
    result = acct.withdraw(amount)
    assert_result(result, expected)

run_scenario(100, 50, "insufficient_funds")
run_scenario(50, 100, "success")

# ✅ DAMP test — each test tells a story
def test_withdraw_fails_when_balance_insufficient():
    account = Account(balance=50)
    with pytest.raises(InsufficientFundsError):
        account.withdraw(100)

def test_withdraw_succeeds_when_balance_sufficient():
    account = Account(balance=100)
    result = account.withdraw(50)
    assert result.balance == 50
```

### The Beyoncé Rule

> "If you liked it then you should have put a test on it."

Every code change must either have a test or be a pure refactoring
(behavior identical, verified by existing tests). No exceptions.

---

## Code Review Best Practices

### Change Sizing

| Size | Review Time | Risk | Recommendation |
|------|-------------|------|----------------|
| <100 lines | 5-10 min | Low | Standard review |
| 100-400 lines | 15-30 min | Medium | Acceptable for a feature |
| 400-800 lines | 30-60 min | High | Should be split. Justify if not. |
| >800 lines | >60 min | Very High | Split. Period. |

### Review Speed Norms

- **No review should wait >24 hours.** Code review is the #1 bottleneck
  in continuous delivery. Prioritize it.
- **Review within 4 hours** for small changes (<100 lines).
- **Review within the same day** for medium changes.
- **Schedule time for large reviews.** Don't squeeze them between meetings.

### Five-Axis Review Framework

Every review must consider all five axes. Skip none.

1. **Security** — OWASP Top 10, injection, auth, secrets, input validation.
2. **Correctness** — Logic, edge cases, error handling, concurrency.
3. **Quality** — Readability, naming, DRY, comments, dead code.
4. **Architecture** — SRP, coupling, layering, backward compatibility.
5. **Performance** — Algorithmic complexity, N+1 queries, memory, I/O.

### Review Language Guidelines

| Instead of | Say |
|-----------|-----|
| "This is broken" | "This could return null if `user` is undefined, causing a TypeError on line 45." |
| "Why didn't you..." | "What was the reasoning behind this approach? I'm curious because..." |
| "This is wrong" | "I think this might have an issue — when X happens, Y would occur. Is that intentional?" |
| "Just use X instead" | "Have you considered X? It handles Y case more gracefully because..." |
| "This is terrible" | (Never say this.) |
| "Obviously..." | (Never say this.) |

---

## Web Performance

### Core Web Vitals Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | ≤4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | ≤200ms | ≤500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | ≤0.25 | >0.25 |

### The Performance Budget

Every page should have a performance budget. Example:

```
Budget:         200KB total page weight (gzipped)
JS:             100KB max
CSS:            30KB max
Images:         50KB max (above-the-fold only)
Fonts:          20KB max
TTFB:           <800ms
Time to Interactive: <3.5s on 3G
```

Exceeding the budget is a build failure, not a suggestion.

### The RAIL Model

| Interaction | Goal | User Perception |
|-------------|------|----------------|
| **Response** (click/tap) | <100ms | Instant |
| **Animation** (scroll/drag) | 16ms/frame (60fps) | Smooth |
| **Idle** (background work) | 50ms chunks | Non-blocking |
| **Load** (page load) | <1s | Seamless |

---

## Code Simplification

### Chesterton's Fence

> "In the matter of reforming things, as distinct from deforming them,
> there is one plain and simple principle; a principle which will probably
> be called a paradox. There exists in such a case a certain institution
> or law; let us say, for the sake of simplicity, a fence or gate erected
> across a road. The more modern type of reformer goes gaily up to it and
> says, 'I don't see the use of this; let us clear it away.' To which the
> more intelligent type of reformer will do well to answer: 'If you don't
> see the use of it, I certainly won't let you clear it away. Go away and
> think. Then, when you can come back and tell me that you do see the use
> of it, I may allow you to destroy it.'"
>
> — G.K. Chesterton, *The Thing* (1929)

In code: don't remove a pattern until you understand why it exists.
Seemingly redundant code often handles an edge case you haven't considered.

### Complexity Metrics

| Metric | Warning Level | Critical Level |
|--------|--------------|----------------|
| **Cyclomatic complexity** | >10 | >20 |
| **Function length** | >30 lines | >50 lines |
| **Nesting depth** | >3 levels | >5 levels |
| **Parameter count** | >4 params | >7 params |
| **File length** | >500 lines | >1000 lines |
| **Cognitive complexity** | >15 | >25 |

### Simplification Heuristics

1. **Inline the simple**: If a function is called once and has <5 lines,
   inline it.
2. **Extract the deep**: Deeply nested code is hard to follow. Extract
   inner blocks into named functions.
3. **Replace conditional with polymorphism**: Long if/else chains on
   type codes are a sign that polymorphism is missing.
4. **Remove dead code**: If it's not reachable, delete it. Git history
   is your undo.
5. **Reduce parameter count**: More than 4 parameters → group into an
   options/config object.
6. **Replace magic numbers**: Every unexplained literal should be a
   named constant.
7. **Simplify boolean expressions**: De Morgan's laws. Extract complex
   conditions into named functions.

---

## Production Deployment

### Deployment vs. Release

**Deployment** = code is running in production.
**Release** = feature is visible to users.

These should be decoupled via feature flags. Deploy often, release when
ready.

### Feature Flag Lifecycle

```
CREATE → ROLLOUT → VERIFY → CLEANUP
  │        │         │         │
  ▼        ▼         ▼         ▼
 Flag     Flag      Flag      Remove
 created  ramped    verified  flag code
 0%       1→50→100% metrics   (within 30d)
```

Every feature flag must have:
- **Owner**: Who is responsible for it.
- **Expiry date**: When the flag code will be removed.
- **Rollout plan**: How it ramps from 0% to 100%.
- **Kill switch**: Can it be turned off instantly without deploy?

### Canary Analysis

Monitor these signals during canary:

| Signal | Comparison | Action if Degraded |
|--------|-----------|-------------------|
| **Error rate** | vs. baseline (non-canary) | Roll back if >2σ above baseline for >5 min |
| **P95 latency** | vs. baseline | Roll back if >50% increase for >5 min |
| **CPU/Memory** | vs. baseline | Investigate if >20% increase |
| **Business metrics** | vs. baseline | Roll back if conversion/signups drop >5% |

### The 5-Minute Rollback Rule

If you cannot roll back a deployment in under 5 minutes, you should not
deploy it. This means:
- Rollback is automated (one command, no manual steps).
- Database migrations are reversible or additive-only.
- Feature flags can disable the change without a code revert.
- The rollback itself does not introduce new risk.

### Deployment Frequency

| Cadence | Maturity Level | Characteristics |
|---------|---------------|-----------------|
| **On-demand** | Elite | Deploy within minutes of merge. Multiple times per day. |
| **Daily** | High | At least one deploy per day. Small batches. |
| **Weekly** | Medium | Sprint-based deploy cycle. Larger batches, higher risk. |
| **Monthly+** | Low | Infrequent deploys. Large batch size. High merge conflict risk. |

DORA research: elite performers deploy 208x more frequently than low
performers and have 7x lower change failure rate. Faster is safer.

---

## Trunk-Based Development

### The Model

```
main ──●────●────●────●────●────● (deployable at every commit)
        \   |   / \   |
         ●──●──●   ●──● (short-lived feature branches, <1 day)
```

**Rules:**
- Branches live <1 day. Merge to main frequently.
- Every commit to main is deployable.
- Feature flags hide incomplete work on main.
- Code review happens on short-lived branches before merge.
- If a branch lives >1 day, it should be split or flagged.

### Why Trunk-Based?

- **Continuous integration** actually means integrating continuously.
  Long-lived branches are the opposite of CI.
- **Reduces merge conflict surface.** Conflicts grow exponentially with
  branch lifetime.
- **Forces small, reviewable changes.** You can't hide a 2000-line PR
  if you merge daily.
- **Enables continuous delivery.** If main is always deployable, you
  can deploy at any time.

---

## Incident Response

### The Five Stages

1. **Detect** — Monitoring alerts, user report, or automated check.
2. **Triage** — Assess severity. Is this a production incident?
3. **Mitigate** — Stop the bleeding. Rollback, feature flag off, scale up.
4. **Resolve** — Fix the root cause. Deploy the fix.
5. **Learn** — Postmortem. What failed? How do we prevent recurrence?

### Blameless Postmortems

A postmortem is not about assigning blame. It's about understanding the
system's failure modes so they don't repeat.

**Structure:**
1. **Timeline** — What happened, when (UTC), who was involved.
2. **Impact** — What was the user impact? (Quantify: duration, affected
   users, data loss.)
3. **Root cause** — The technical chain of events that caused the failure.
4. **Contributing factors** — Process, tooling, or organizational gaps.
5. **Action items** — Concrete, assigned, time-bound fixes.
6. **Lessons learned** — What surprised us? What assumptions were wrong?

### Incident Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **SEV1** | Critical — service down, data loss | Immediate, all hands | Payment processing down, auth broken |
| **SEV2** | Major — degraded service, no data loss | <30 min | Slow response times, non-critical feature broken |
| **SEV3** | Minor — limited impact | <4 hours | Cosmetic issue, non-blocking bug |
| **SEV4** | Cosmetic — no user impact | Next business day | Typos, minor visual issues |

---

## References

### Industry Standards
- [DORA DevOps Capabilities](https://dora.dev/capabilities/) — Research-backed practices
- [Google SRE Book](https://sre.google/books/) — Production engineering
- [The Twelve-Factor App](https://12factor.net/) — SaaS methodology
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — Security risks

### Recommended Reading
- *Accelerate* by Nicole Forsgren, Jez Humble, Gene Kim — DORA research
- *Site Reliability Engineering* by Google — Production practices
- *Continuous Delivery* by Jez Humble, David Farley — Deployment patterns
- *Test-Driven Development: By Example* by Kent Beck — TDD fundamentals
- *Refactoring* by Martin Fowler — Simplification patterns
- *The Phoenix Project* by Gene Kim — DevOps narrative