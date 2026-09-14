# Gate 2: Test Review — Behavior-Over-Implementation Testing

## Overview

This gate catches the systematic ways LLMs produce bad test code. The common failure modes: mock-heavy unit tests that assert implementation details, near-duplicate test bodies that differ by one value, and tests that re-verify the framework instead of the project's logic. Each looks productive in a diff and costs maintenance forever.

## The 10 Rules

### Rule 1: Test behavior, not implementation
Test what code does from the caller's perspective. Assert return values and observable side effects. Never assert that an internal helper was called with specific arguments — that test breaks on every refactor while catching nothing.

**Violation pattern:** asserting a mock of an internal function was called, where that function is not a system boundary.

### Rule 2: Every mock must be justified
Mock only at system boundaries: network and HTTP calls, LLM APIs, databases, filesystem I/O on external files, clock and randomness, third-party SDKs. Never mock internal classes or helper functions.

### Rule 3: One scenario per test, data-driven for variants
If two or more tests share identical setup and differ only in input/output values, merge them into one data-driven test (`@pytest.mark.parametrize`, PHPUnit `#[DataProvider]`, Jest `test.each`).

**When separate tests ARE correct:** different setup, different assertions, different mock configurations.

### Rule 4: Every test must justify its existence
Ask: "What bug does this catch that no other test catches?" Delete tests that only catch typos, verify default values of data classes, or test trivial pass-through logic.

**Common unjustified tests:** constructors setting attributes, a function rejecting input the type system already forbids, string formatting of log messages.

### Rule 5: Name tests for the scenario
Pattern: `test_<scenario>_<expected_outcome>`. The name should read like a requirement, not echo the function signature.

| Bad | Good |
|-----|------|
| `test_parse_response_missing_field` | `test_malformed_response_falls_back_to_default` |
| `test_add_tags_single_string` | `test_single_tag_normalizes_to_list` |

### Rule 6: Production regression tests are sacred
Tests that reproduce a real production bug are always justified. Reference the incident in the name or a comment. Never delete them.

### Rule 7: No tests for framework guarantees
Don't test that the validation library validates, the ORM commits, the router returns 404. Test *your* logic.

**Violation pattern:** a test that would still pass if you deleted all the project's custom code.

### Rule 8: State and value objects are real, never mocked
Never mock a data model, DTO, entity, or state object. Construct a real instance. Mocking state hides field-name typos and validation errors — exactly the bugs worth catching.

### Rule 9: Infrastructure under test gets real infrastructure
When database queries, schema behavior, or persistence logic *is the subject*, run against a real test database with real migrations. Mocking the session there tests nothing.

### Rule 10: Tests are deterministic
A flaky test is worse than no test. Flag: sleep-based synchronization, real network calls, wall-clock dependency, uncontrolled randomness, execution-order dependence.

## LLM-App Testing Rules (extra)

When the project calls LLM APIs, uses agent frameworks, or wires up observability:

**Rule 11: Prompt contracts are versioned and tested.** A test that changes the prompt and passes without review is a regression waiting to happen. Assert prompt structure (or a hash) in a snapshot test.

**Rule 12: Observability wiring is tested.** If the app logs token counts, latencies, or model outputs for monitoring, test that the wiring exists and fires on the right events.

**Rule 13: Agent-flow transitions are tested.** If the app has an agent loop (tool selection → execution → result processing), test each transition: does the correct next tool get called based on the last result?

## Self-Check (Gate 2)
1. Every test justified? (Rule 4)
2. No mock of internal helpers? (Rule 2)
3. No framework re-testing? (Rule 7)
4. Near-duplicate tests merged into one data-driven? (Rule 3)
5. Tests name the scenario, not the function? (Rule 5)
6. No sleep-based synchronization, no wall-clock dependency? (Rule 10)
7. If LLM app: prompt contracts tested, observability wired, agent transitions covered? (Rules 11-13)
