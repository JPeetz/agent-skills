---
name: test-driven-development
description: Use this skill when implementing any logic, fixing any bug, or changing any behavior. Write a failing test before writing the code that makes it pass — PROVE it works before you trust it. Required for production code changes; skip only for pure configuration, documentation, or static content changes with no behavioral impact.
---

# Test-Driven Development

## Overview

Write a failing test before writing the code that makes it pass. For bug fixes, reproduce the bug with a test before attempting a fix. Tests are proof — "seems right" is not done. A codebase with good tests is an AI agent's superpower; a codebase without tests is a liability.

TDD applies to any language and any framework. The commands change; the cycle does not.

## When to Use

- Implementing any new logic or behavior
- Fixing any bug (the Prove-It Pattern)
- Modifying existing functionality
- Adding edge case handling
- Any change that could break existing behavior

**When NOT to use:** Pure configuration changes, documentation updates, or static content changes that have no behavioral impact.

**Related:** For browser-based changes, combine TDD with runtime verification using Chrome DevTools — see the `browser-testing-with-devtools` skill.

## Discover the Stack First

The TDD cycle is universal; the commands are not. Before writing the first test, discover how *this* repository tests, and use its commands for every RED, GREEN, and verification step:

- **Language and build system** — `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `Makefile`, `pom.xml`/`build.gradle`
- **Checked-in wrappers** — prefer `./gradlew`, `./mvnw`, `make test`, or a repo script over globally installed tools
- **Test framework and configuration** — and how it runs a single focused test vs the full suite
- **Existing conventions** — where tests live, how files are named, what patterns neighboring tests follow
- **Documented commands** — README, CONTRIBUTING, and CI workflows show the commands that actually gate merges

Run the repository's focused-test command during the loop and its full-suite command before completion. Never assume a default like `npm test` — a Gradle, Cargo, or pytest project has its own equivalent.

The examples below use TypeScript for illustration; the workflow is identical in any language once you've discovered the project's own tooling.

## The TDD Cycle

```
RED               GREEN               REFACTOR
Write a test      Write minimal code   Clean up the
that fails ──────→ to make it pass ───→ implementation ──→ (repeat)
   │                    │                     │
   ▼                    ▼                     ▼
Test FAILS          Test PASSES          Tests still PASS
```

### Step 1: RED — Write a Failing Test

Write the test first. It must fail. A test that passes immediately proves nothing.

```typescript
// RED: This test fails because createTask doesn't exist yet
describe('TaskService', () => {
  it('creates a task with title and default status', async () => {
    const task = await taskService.createTask({ title: 'Buy groceries' });
    expect(task.id).toBeDefined();
    expect(task.title).toBe('Buy groceries');
    expect(task.status).toBe('pending');
    expect(task.createdAt).toBeInstanceOf(Date);
  });
});
```

### Step 2: GREEN — Make It Pass

Write the minimum code to make the test pass. Do not over-engineer:

```typescript
// GREEN: Minimal implementation
export async function createTask(input: { title: string }): Promise<Task> {
  const task = {
    id: generateId(),
    title: input.title,
    status: 'pending' as const,
    createdAt: new Date(),
  };
  await db.tasks.insert(task);
  return task;
}
```

### Step 3: REFACTOR — Clean Up

With tests green, improve the code without changing behavior:
- Extract shared logic
- Improve naming
- Remove duplication
- Optimize if necessary

Run tests after every refactor step to confirm nothing broke.

## The Prove-It Pattern (Bug Fixes)

When a bug is reported, **do not start by trying to fix it.** Start by writing a test that reproduces it.

```
Bug report arrives
│
▼
Write a test that demonstrates the bug
│
▼
Test FAILS (confirming the bug exists)
│
▼
Implement the fix
│
▼
Test PASSES (proving the fix works)
│
▼
Run full test suite (no regressions)
```

**Example:**

```typescript
// Bug: "Completing a task doesn't update the completedAt timestamp"
// Step 1: Write the reproduction test (it should FAIL)
it('sets completedAt when task is completed', async () => {
  const task = await taskService.createTask({ title: 'Test' });
  const completed = await taskService.completeTask(task.id);
  expect(completed.status).toBe('completed');
  expect(completed.completedAt).toBeInstanceOf(Date); // This fails → bug confirmed
});

// Step 2: Fix the bug
export async function completeTask(id: string): Promise<Task> {
  return db.tasks.update(id, {
    status: 'completed',
    completedAt: new Date(), // This was missing
  });
}

// Step 3: Test passes → bug fixed, regression guarded
```

## The Test Pyramid

Invest testing effort according to the pyramid — most tests should be small and fast, with progressively fewer tests at higher levels:

```
        ╱╲
       ╱ ╲  E2E Tests (~5%)
      ╱   ╲  Full user flows, real browser
     ╱─────╲
    ╱       ╲  Integration Tests (~15%)
   ╱         ╲  Component interactions, API boundaries
  ╱───────────╲
 ╱              ╲  Unit Tests (~80%)
╱────────────────╲  Pure logic, isolated, milliseconds each
```

**The Beyoncé Rule:** If you liked it, you should have put a test on it. Infrastructure changes, refactoring, and migrations are not responsible for catching your bugs — your tests are. If a change breaks your code and you didn't have a test for it, that's on you.

### Test Sizes (Resource Model)

Beyond the pyramid levels, classify tests by what resources they consume:

| Size | Constraints | Speed | Example |
|------|-------------|-------|---------|
| **Small** | Single process, no I/O, no network, no database | Milliseconds | Pure function tests, data transforms |
| **Medium** | Multi-process OK, localhost only, no external services | Seconds | API tests with test DB, component tests |
| **Large** | Multi-machine OK, external services allowed | Minutes | E2E tests, performance benchmarks, staging integration |

Small tests should make up the vast majority of your suite. They're fast, reliable, and easy to debug when they fail.

### Decision Guide

```
Is it pure logic with no side effects?
  → Unit test (small)
Does it cross a boundary (API, database, file system)?
  → Integration test (medium)
Is it a critical user flow that must work end-to-end?
  → E2E test (large) — limit these to critical paths
```

## Writing Good Tests

### Test State, Not Interactions

Assert on the *outcome* of an operation, not on which methods were called internally. Tests that verify method call sequences break when you refactor, even if the behavior is unchanged.

```typescript
// Good: Tests what the function does (state-based)
it('returns tasks sorted by creation date, newest first', async () => {
  const tasks = await listTasks({ sortBy: 'createdAt', sortOrder: 'desc' });
  expect(tasks[0].createdAt.getTime())
    .toBeGreaterThan(tasks[1].createdAt.getTime());
});

// Bad: Tests how the function works internally (interaction-based)
it('calls db.query with ORDER BY created_at DESC', async () => {
  await listTasks({ sortBy: 'createdAt', sortOrder: 'desc' });
  expect(db.query).toHaveBeenCalledWith(
    expect.stringContaining('ORDER BY created_at DESC')
  );
});
```

### DAMP Over DRY in Tests

In production code, DRY (Don't Repeat Yourself) is usually right. In tests, **DAMP (Descriptive And Meaningful Phrases)** is better. A test should read like a specification — each test should tell a complete story without requiring the reader to trace through shared helpers.

```typescript
// DAMP: Each test is self-contained and readable
it('rejects tasks with empty titles', () => {
  const input = { title: '', assignee: 'user-1' };
  expect(() => createTask(input)).toThrow('Title is required');
});
it('trims whitespace from titles', () => {
  const input = { title: '  Buy groceries  ', assignee: 'user-1' };
  const task = createTask(input);
  expect(task.title).toBe('Buy groceries');
});

// Over-DRY: Shared setup obscures what each test actually verifies
// (Don't do this just to avoid repeating the input shape)
```

Duplication in tests is acceptable when it makes each test independently understandable.

### Prefer Real Implementations Over Mocks

Use the simplest test double that gets the job done. The more your tests use real code, the more confidence they provide.

```
Preference order (most to least preferred):
1. Real implementation → Highest confidence, catches real bugs
2. Fake → In-memory version of a dependency (e.g., fake DB)
3. Stub → Returns canned data, no behavior
4. Mock (interaction) → Verifies method calls — use sparingly
```

**Use mocks only when:** the real implementation is too slow, non-deterministic, or has side effects you can't control (external APIs, email sending). Over-mocking creates tests that pass while production breaks.

### Use the Arrange-Act-Assert Pattern

```typescript
it('marks overdue tasks when deadline has passed', () => {
  // Arrange: Set up the test scenario
  const task = createTask({
    title: 'Test',
    deadline: new Date('2025-01-01'),
  });

  // Act: Execute the behavior under test
  const result = markOverdue(task);

  // Assert: Verify the outcome
  expect(result.status).toBe('overdue');
  expect(result.overdueNotified).toBe(true);
});
```

### Test Names as Documentation

A test name is a specification line. It should describe the expected behavior, not the implementation:

```typescript
// Good: Describes the behavior
it('rejects tasks with titles exceeding 100 characters')
it('preserves task order when reordering within the same priority')
it('returns 404 when the task does not exist')

// Bad: Describes implementation
it('calls taskService.create')
it('validates createTaskInput length')
it('throws NotFoundError')
```

## Testing Edge Cases Systematically

Use the **REACT** heuristic to find what to test:

| Letter | Category | Examples |
|--------|----------|----------|
| **R** | **R**ange | Boundaries, empty/null, max/min, overflow |
| **E** | **E**rrors | Expected errors, unexpected failures, error recovery |
| **A** | **A**uth | Different roles, permissions, unauthenticated access |
| **C** | **C**oncurrency | Race conditions, duplicates, timeout handling |
| **T** | **T**ime | Date boundaries, timezone handling, staleness |

## Test-Driven Debugging Workflow

When a test fails and the cause isn't obvious:

```
Failing test
│
▼
Read the error message and stack trace
│
▼
Read the test — what is it asserting?
│
▼
Read the code under test — what is it doing?
│
▼
Form a hypothesis about the mismatch
│
▼
Add a focused debugging test or assertion
│
▼
Does it pass or fail as expected?
│
├── Passes as expected → Apply the fix, re-run the original test
├── Fails unexpectedly → Form new hypothesis, loop
└── Neither → The hypothesis is wrong, re-read the code
```

## CI Integration

Tests are only useful if they run consistently. Ensure:

- **Every PR runs the full suite** via CI (see `ci-cd-and-automation` skill)
- **Branch protection** requires all tests to pass before merge
- **Flaky tests are fixed, not re-run** — a flaky test masks real bugs

## When to Use Subagents for Testing

For complex bug fixes, spawn a subagent to write the reproduction test:

```
Main agent: "Spawn a subagent to write a test that reproduces this bug:
  [bug description]. The test should fail with the current code."
Subagent: Writes the reproduction test
Main agent: Verifies the test fails, then implements the fix,
  then verifies the test passes.
```

This separation ensures the test is written without knowledge of the fix, making it more robust.

## Anti-Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll write tests after the code works" | You won't. And tests written after the fact test implementation, not behavior. |
| "This is too simple to test" | Simple code gets complicated. The test documents the expected behavior. |
| "Tests slow me down" | Tests slow you down now. They speed you up every time you change the code later. |
| "I tested it manually" | Manual testing doesn't persist. Tomorrow's change might break it with no way to know. |
| "The code is self-explanatory" | Tests ARE the specification. They document what the code should do, not what it does. |
| "It's just a prototype" | Prototypes become production code. Tests from day one prevent the "test debt" crisis. |
| "Let me run the tests again just to be extra sure" | After a clean test run, repeating the same command adds nothing unless the code has changed since. Run again after subsequent edits, not as reassurance. |

## Red Flags

- Writing code without any corresponding tests
- Reaching for a default test command (`npm test`) without checking what this repository actually uses
- Tests that pass on the first run (they may not be testing what you think)
- "All tests pass" but no tests were actually run
- Bug fixes without reproduction tests
- Tests that test framework behavior instead of application behavior
- Test names that don't describe the expected behavior
- Skipping tests to make the suite pass
- Running the same test command twice in a row without any intervening code change

## Verification

After completing any implementation:

- [ ] Every new behavior has a corresponding test
- [ ] The full suite passes, run with the repository's own test command (`npm test`, `./gradlew test`, `pytest`, `go test ./...`, etc.)
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] Test names describe the behavior being verified
- [ ] No tests were skipped or disabled
- [ ] Coverage hasn't decreased (if tracked)

**Note:** Run each test command after a change that could affect the result. After a clean run, don't repeat the same command unless the code has changed since — re-running on unchanged code adds no confidence.