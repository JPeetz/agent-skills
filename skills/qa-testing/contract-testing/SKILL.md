---
name: contract-testing
description: "Use this skill when implementing or maintaining consumer-driven contract tests — Pact contract testing, provider verification, API drift detection, consumer-driven contracts, Pact Broker integration, can-i-deploy gates, bi-directional contract testing (BDCT), OpenAPI spec conformance testing, and webhook/event contract testing."
license: MIT
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
  - contract-testing
  - pact
  - pact-broker
  - consumer-driven-contracts
  - api-testing
  - openapi
  - bdct
  - drift
  - ci-cd
  - qa
---

# Contract Testing — Agent Skill

Consumer-driven contract testing with [Pact](https://docs.pact.io), the Pact Broker, `can-i-deploy` deployment gates, OpenAPI conformance checking with the Drift CLI, and bi-directional contract testing (BDCT). Use it when services talk to each other over HTTP or messaging and you want to replace brittle end-to-end suites with fast, versioned contracts.

---

## When to Use This Skill

Use it when:

- A consumer team needs a test proving what it *requires* from a provider API (not what the provider happens to return today).
- A provider team needs to verify it still honours every published contract before shipping.
- You are wiring `can-i-deploy` gates so a deploy is blocked when consumer and provider versions are incompatible.
- You need to detect API drift: implementation diverging from the OpenAPI spec, or spec diverging from reality.
- You are adopting BDCT because the provider cannot or will not run Pact verification.
- You need contract tests for async messaging (Kafka/SNS/SQS handlers) or provider-side webhooks.
- A pipeline is green but production integration still breaks — that is usually a missing contract, not a missing E2E test.

Do **not** use it when:

- Only one application exists and there is no separate consumer/provider boundary — unit and integration tests are cheaper.
- You need to prove a full user journey works through five services — that is E2E; contract tests cover pairwise interfaces only.
- The "contract" is a database schema shared by two services — that is a coupling problem to fix, not a contract to bless.
- You need performance or load characteristics — contracts assert shape and semantics, not latency.

---

## Quick Reference

| Task | Tool / Command | Where it runs |
|---|---|---|
| Define consumer expectations | `PactV3` + `MatchersV3` (JS) / `PactBuilder` (JVM, Python, Go, .NET) | Consumer unit test suite |
| Publish pacts | `pact-broker publish ./pacts --consumer-app-version=$SHA --branch=$BRANCH` | Consumer CI |
| Verify provider | `Verifier` (JS) / `PactVerificationContext` (JVM) | Provider CI |
| Compatibility gate | `pact-broker can-i-deploy --pacticipant X --version $SHA --to-environment production` | Before every deploy |
| Record what is live | `pact-broker record-deployment --pacticipant X --version $SHA --environment production` | After every deploy |
| Spec conformance | `drift verify -f drift.yaml --server-url $URL --generate-result` | Provider CI |
| BDCT publish | `pactflow publish-provider-contract openapi.yaml --verification-results ...` | Provider CI |
| Message contracts | `MessageConsumerPact` / `@PactVerifyProvider` | Consumer / provider CI |

---

## Principles

1. **The consumer defines the contract.** The consumer writes a test asserting the subset of the response it actually uses. The provider must satisfy it. A provider-authored spec that no consumer needs is documentation, not a contract.
2. **Contracts are pairwise.** One pact per consumer-provider pair. Do not build a "contract for the platform".
3. **Only assert what you consume.** Matching a field you never read converts an unrelated provider change into a false failure — the fastest way to get contract testing deleted from a repo.
4. **The mock is the specification.** Consumer tests run against an in-process Pact mock server, never the real provider. If the test needs the real provider, it is an integration test.
5. **Version everything, tag nothing permanent.** Publish pacts with the git SHA and branch. Environment membership is recorded by `record-deployment`, not by mutable tags.
6. **Verification results are the source of truth.** A pact nobody verified is a wish. `publishVerificationResult: true` is not optional in CI.
7. **Contracts complement, not replace, tests.** Contract tests catch interface breakage; unit tests catch logic; a small E2E smoke suite catches wiring and config.

---

## Consumer Tests

### JavaScript / TypeScript (Pact JS v12+)

```ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import path from 'path';
import { getOrder } from '../src/orders';

const { like, integer, string, eachLike, regex, iso8601DateTime } = MatchersV3;

const provider = new PactV3({
  consumer: 'web-checkout',
  provider: 'orders-api',
  dir: path.resolve(process.cwd(), 'pacts'),
});

describe('orders-api contract', () => {
  it('returns an order by id', async () => {
    provider
      .given('order 42 exists')
      .uponReceiving('a request for order 42')
      .withRequest({
        method: 'GET',
        path: '/orders/42',
        headers: { Accept: 'application/json' },
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: integer(42),
          status: regex(/^(pending|paid|shipped)$/, 'paid'),
          total: like(1999),
          createdAt: iso8601DateTime('2026-01-04T10:00:00Z'),
          items: eachLike({ sku: string('ABC-1'), qty: integer(2) }, { min: 1 }),
        },
      });

    await provider.executeTest(async (mockServer) => {
      const order = await getOrder(mockServer.url, 42);
      expect(order.status).toBe('paid');
    });
  });
});
```

Rules that keep this maintainable:

- Pass `mockServer.url` into the code under test through its base-URL parameter. Never hard-code a port.
- Use `given(...)` to name provider state precisely (`'order 42 exists'`), and keep the state list in a shared doc so provider engineers can implement each one.
- One `describe` per provider; one `it` per interaction. Interaction names must be stable — the broker keys history on them.
- Write one happy path per endpoint plus the error paths the consumer actually handles (404, 401, 422). Do not mirror the provider's whole error catalogue.

### JVM (JUnit 5)

```java
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "orders-api", port = "8080")
class OrderClientContractTest {

  @Pact(consumer = "web-checkout")
  public RequestResponsePact getOrder(PactDslWithProvider builder) {
    return builder.given("order 42 exists")
      .uponReceiving("a request for order 42")
        .path("/orders/42").method("GET")
      .willRespondWith().status(200)
        .headers(Map.of("Content-Type", "application/json"))
        .body(newJsonBody(o -> o
          .integerType("id", 42)
          .stringMatcher("status", "pending|paid|shipped", "paid")
          .array("items", a -> a.object(i -> i.stringType("sku", "ABC-1")))))
      .toPact();
  }

  @Test
  @PactTestFor(pactMethod = "getOrder")
  void fetchesOrder(MockServer mockServer) {
    var client = new OrderClient(mockServer.getUrl());
    assertEquals("paid", client.getOrder(42).status());
  }
}
```

### Python

```python
from pact import Consumer, Provider

pact = Consumer("web-checkout").has_pact_with(Provider("orders-api"), pact_dir="./pacts")

def test_get_order():
    (pact.given("order 42 exists").upon_receiving("a request for order 42")
         .with_request("get", "/orders/42")
         .will_respond_with(200, body={"id": 42, "status": "paid"}))
    with pact:
        assert get_order(pact.uri, 42)["status"] == "paid"
```

Whatever the language: the generated `pacts/*.json` file is the deliverable. Commit it? No — publish it. Commit only if you deliberately cannot run a broker.

---

## Provider Verification

Provider verification replays every pact interaction against a running instance of the provider, honouring `given()` states.

### JavaScript

```ts
import { Verifier } from '@pact-foundation/pact';

await new Verifier({
  provider: 'orders-api',
  providerBaseUrl: process.env.PROVIDER_URL ?? 'http://localhost:8080',
  pactBrokerUrl: process.env.PACT_BROKER_BASE_URL,
  pactBrokerToken: process.env.PACT_BROKER_TOKEN,
  publishVerificationResult: process.env.CI === 'true',
  providerVersion: process.env.GIT_SHA,
  providerVersionBranch: process.env.GIT_BRANCH,
  consumerVersionSelectors: [
    { mainBranch: true },
    { deployedOrReleased: true },
  ],
  enablePending: true,
  includeWipPactsSince: '2023-01-01',
  stateHandlers: {
    'order 42 exists': async () => { await seedOrder(42); },
    'no orders exist': async () => { await db.orders.deleteAll(); },
  },
}).verifyProvider();
```

### JVM

```java
@Provider("orders-api")
@PactBroker(url = "${PACT_BROKER_BASE_URL}",
            authentication = @PactBrokerAuth(token = "${PACT_BROKER_TOKEN}"))
class OrdersProviderVerificationTest {

  @BeforeEach
  void before(PactVerificationContext context) { context.setTarget(new HttpTestTarget("localhost", 8080)); }

  @TestTemplate
  @ExtendWith(PactVerificationInvocationContextProvider.class)
  void verify(PactVerificationContext context) { context.verifyInteraction(); }

  @State("order 42 exists")
  void order42Exists() { repository.save(OrderFixtures.order(42)); }
}
```

### Provider verification checklist

- [ ] Provider runs from a real HTTP server with real routing, serialisation, and auth middleware — not a mocked controller layer.
- [ ] `stateHandlers` / `@State` methods reset state between interactions. Leaked state is the number one cause of order-dependent, flaky verification.
- [ ] `consumerVersionSelectors` selects `mainBranch` + `deployedOrReleased`; never `{ all: true }` in a big estate.
- [ ] `enablePending: true` plus `includeWipPactsSince` so a new consumer contract does not turn the provider's main red on day one.
- [ ] `publishVerificationResult: true` only in CI (locally it pollutes the matrix with workstation versions).
- [ ] Failure output is read, not silenced: a mismatch prints expected vs actual JSON paths — fix the provider or correct an over-strict matcher.

---

## Pact Broker

Run the broker (or use a hosted one) and treat it as the system of record for the compatibility matrix.

```bash
docker run -d --name pact-broker -p 9292:9292 \
  -e PACT_BROKER_DATABASE_URL="$DATABASE_URL" \
  -e PACT_BROKER_BASE_URL="https://pact.example.com" \
  pactfoundation/pact-broker:latest
```

Publish in consumer CI, verify in provider CI:

```bash
pact-broker publish ./pacts --consumer-app-version="$GIT_SHA" --branch="$GIT_BRANCH" \
  --broker-base-url="$PACT_BROKER_BASE_URL" --broker-token="$PACT_BROKER_TOKEN"
```

Operational rules:

- Enable **branch support** and set `mainBranch` per pacticipant; branch-aware selectors are what make the matrix tractable.
- Set a **pact retention policy** (e.g. keep all from main + last 10 feature branches). Unbounded brokers rot.
- Use **webhooks** on `contract_published` and `provider_verification_published` to trigger the counterpart pipeline instead of polling.
- Names are contracts: `--pacticipant` identifiers must match the `consumer`/`provider` strings in code forever. Rename only via a broker migration.

---

## Can-I-Deploy Gates

`can-i-deploy` answers: "is this version compatible with everything already in the target environment?" It reads the matrix, not the code.

```bash
pact-broker can-i-deploy \
  --pacticipant orders-api \
  --version "$GIT_SHA" \
  --to-environment production \
  --broker-base-url "$PACT_BROKER_BASE_URL" \
  --broker-token "$PACT_BROKER_TOKEN"

pact-broker record-deployment \
  --pacticipant orders-api --version "$GIT_SHA" \
  --environment production \
  --broker-base-url "$PACT_BROKER_BASE_URL" --broker-token "$PACT_BROKER_TOKEN"
```

Pipeline order that actually works:

1. Consumer: test → publish pacts (with version + branch).
2. Provider: verify → publish results.
3. Deploy candidate: `can-i-deploy --to-environment <env>` → exit non-zero blocks the deploy.
4. Deploy.
5. `record-deployment` (or `record-release` for mobile/desktop that ships to app stores).
6. Optional: `record-environment` / `create-environment` must exist before step 3 — a missing environment makes the gate silently permissive in older brokers.

Notes:

- `--to-environment` requires the environment to be defined; `--to <tag>` is the legacy equivalent. Prefer environments.
- Mobile/single-version consumers: use `--all prod` for the consumer side so any live app version is considered.
- The gate is only as good as the matrix. If a provider never verifies, `can-i-deploy` says yes and means nothing. Alert on pacticipants with no verification in N days.

---

## API Drift Detection and Spec Conformance

Drift catches the case Pact does not: the implementation diverging from the **published OpenAPI spec**, even when no consumer notices yet.

```yaml
# drift.yaml
# yaml-language-server: $schema=https://download.pactflow.io/drift/schemas/drift.testcases.v1.schema.json
drift-testcase-file: v1
title: "orders-api conformance"

sources:
  - { name: source-oas, path: openapi.yaml }

plugins:
  - { name: oas }
  - { name: json }

operations:
  listOrders_Success:
    target: source-oas:listOrders
    tags: [smoke]
    expected: { response: { statusCode: 200 } }

  getOrder_NotFound:
    target: source-oas:getOrder
    tags: [errors]
    parameters: { path: { orderId: "does-not-exist" } }
    expected: { response: { statusCode: 404 } }   # spec must declare 404 or this fails
```

```bash
drift verify -f drift.yaml --server-url http://localhost:8080 --output-dir ./output --generate-result
drift verify -f drift.yaml --server-url https://staging.example.com --tags smoke
```

What Drift gives you:

- Request/response bodies validated against the OpenAPI schema (required fields, types, enums, formats), not just status codes.
- Coverage gaps: operations in the spec with no test case, and operations in code with no spec entry.
- A machine-readable result bundle (`application/vnd.smartbear.drift.result`) that BDCT can publish.

Run it on every provider build. Treat unexplained drift as an incident: either the spec is stale (fix the spec, bump the version) or the code regressed.

---

## Bi-Directional Contract Testing (BDCT)

BDCT removes the need for the provider to run Pact verification. Consumer pacts and a provider-published OpenAPI spec + self-verification results are compared in the broker.

Flow:

1. **Consumers** publish pacts as usual (or publish OpenAPI-based consumer contracts).
2. **Provider** publishes its OpenAPI spec plus Drift verification results:

```bash
drift verify -f drift.yaml --server-url "$PROVIDER_URL" \
  --output-dir ./output --generate-result
EXIT=$?

pactflow publish-provider-contract openapi.yaml \
  --provider orders-api \
  --provider-app-version "$GIT_SHA" \
  --branch "$GIT_BRANCH" \
  --content-type application/yaml \
  --specification openapi \
  --verification-exit-code $EXIT \
  --verification-results "$(ls output/results/verification.*.result | head -n1)" \
  --verification-results-content-type application/vnd.smartbear.drift.result
```

3. `can-i-deploy` now performs **cross-contract** comparison: provider spec vs consumer pact. No provider test run per consumer, no provider-side Pact dependency.

When BDCT is the right call:

- Provider is third-party, legacy, or another org that will not add Pact.
- Dozens of consumers would make per-consumer verification slow.
- The team already treats OpenAPI as the contract of record.

When it is not:

- The provider's spec is inaccurate — BDCT compares the spec, so an inaccurate spec gives false confidence. Fix spec fidelity first (that is what Drift is for).
- You need message/event contracts — BDCT is HTTP/OpenAPI only.
- Consumer expectations are semantically narrower than the spec (e.g. "status is one of three values") — only Pact captures that.

---

## Event-Driven and Webhook Contract Testing

### Message contracts (Kafka, SNS/SQS, RabbitMQ)

Consumer side asserts the shape it can handle; provider side asserts what it emits.

```ts
import { MessageConsumerPact, MatchersV3, asynchronousBodyHandler } from '@pact-foundation/pact';

const messagePact = new MessageConsumerPact({
  consumer: 'inventory-service', provider: 'orders-service',
  dir: path.resolve(process.cwd(), 'pacts'),
});

it('handles order-created', async () => {
  await messagePact
    .given('an order was created')
    .expectsToReceive('an order-created event')
    .withContent({
      eventId: MatchersV3.uuid(),
      type: MatchersV3.string('order.created'),
      payload: MatchersV3.like({ orderId: MatchersV3.integer(42), total: MatchersV3.integer(1999) }),
    })
    .withMetadata({ contentType: 'application/json' })
    .verify(asynchronousBodyHandler(async (event) => {
      await inventory.apply(event);
      expect(inventory.reserved(event.payload.orderId)).toBe(true);
    }));
});
```

Provider side (JVM): annotate the emitter method with `@PactVerifyProvider("an order-created event")`. Verification is in-process — no broker or queue required.

### Webhooks (provider calls consumer)

A webhook is an outbound HTTP call, so model it as a pact where the **consumer is the webhook receiver** and the "provider" is the sender:

- Receiver writes a consumer test asserting the payload it accepts and the response it must return (usually `2xx` fast).
- Give each webhook event type its own interaction (`order.shipped`, `order.cancelled`).
- Assert signature-header presence via regex, not a literal HMAC value — the value is time-dependent.
- Test retry semantics separately: webhook providers retry on non-2xx, so the receiver must be idempotent. Assert idempotency by replaying the same event id twice and checking one side effect.
- Broker webhooks (the Pact Broker's own feature) are a different thing: `pact-broker create-or-update-webhook` notifies CI when contracts change.

```bash
pact-broker create-or-update-webhook "https://ci.example.com/hooks/provider-verify" \
  --request POST --header "Content-Type: application/json" --data @webhook-body.json \
  --consumer web-checkout --provider orders-api \
  --description "trigger provider verification on pact change" \
  --broker-base-url "$PACT_BROKER_BASE_URL" --broker-token "$PACT_BROKER_TOKEN"
```

---

## CI/CD Integration Patterns

**Split the pipeline by responsibility.** Consumer pipeline publishes; provider pipeline verifies; deploy pipeline gates.

```yaml
# .github/workflows/consumer.yml (excerpt)
- run: npm test -- --testPathPattern=pact
- run: npx pact-broker publish ./pacts
    --consumer-app-version=${{ github.sha }} --branch=${{ github.ref_name }}
    --broker-base-url=${{ secrets.PACT_BROKER_BASE_URL }}
    --broker-token=${{ secrets.PACT_BROKER_TOKEN }}

# deploy job — required check, runs before the deploy step
- run: pact-broker can-i-deploy --pacticipant ${{ vars.PACTICIPANT }}
    --version ${{ github.sha }} --to-environment production
    --broker-base-url=${{ secrets.PACT_BROKER_BASE_URL }}
    --broker-token=${{ secrets.PACT_BROKER_TOKEN }}
```

Patterns worth adopting:

- **Webhook-triggered verification:** broker fires on `contract_published`, provider CI runs verification against `mainBranch` + `deployedOrReleased` selectors. Keeps a busy provider from verifying every consumer branch.
- **Pending pacts:** `enablePending` lets a new consumer contract land without blocking the provider. Merge the consumer first, provider catches up, then the contract becomes enforced.
- **Work-in-progress pacts:** `includeWipPactsSince` verifies contracts from unmerged consumer branches against the provider's feature branch — catches breakage before either side merges.
- **Gate before deploy, record after:** a `can-i-deploy` with no `record-deployment` leaves the matrix blind about production.
- **Fail loudly on missing config:** if `PACT_BROKER_BASE_URL` is unset, the job must fail, not silently skip publishing.
- **Keep suites fast:** consumer pacts run in-process (milliseconds). If verification takes >5 minutes, you are selecting too many pacts — narrow the selectors.

See `scripts/pact_ci_gate.sh` for a copy-paste gate that checks config, runs `can-i-deploy`, and prints an actionable failure message.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Exact-value assertions | Provider bumps a `total` or timestamp, contract fails for no user-visible reason | Use type/regex matchers (`like`, `integer`, `iso8601DateTime`); assert values only where the consumer branches on them |
| Asserting unused fields | Every provider refactor breaks every consumer | Contract the response subset the consumer reads; ignore the rest |
| Shared mutable test data | Verification passes locally, fails in CI, passes on retry | Per-interaction `given()` state, seeded and torn down; never share rows across interactions |
| `{ all: true }` selectors | Verification takes 20+ minutes and fails on ancient pacts | `mainBranch` + `deployedOrReleased` + `enablePending` |
| Real provider in consumer tests | Tests need a running stack, are slow, and encode provider bugs | Consumer test hits the Pact mock; provider bugs are provider verification's job |
| Publishing without verifying | Matrix shows green, integration still breaks | `publishVerificationResult: true` on the provider, and alert on stale pacticipants |
| Overly broad provider state | `given("data exists")` seeds everything; tests interfere | One focused state per interaction, named after the scenario |
| Tags as environments | `can-i-deploy --to prod` checks a stale tag | `record-deployment` + `--to-environment` |
| Contract tests in the E2E suite | 40-minute feedback loop, flaky | Contract tests live in the fast unit-test tier |
| Renaming interactions casually | Broker loses history, pending logic misfires | Interaction descriptions are stable identifiers |
| Testing the provider's whole error catalogue | Suite balloons, provider owns the assertions | Contract only the errors the consumer actually handles |
| One giant pact for a whole API | Any change touches every consumer | One pact per consumer/provider pair, split by resource if large |

---

## Verification Checklist

Before declaring contract testing "in place":

- [ ] Every consumer/provider pair has at least one pact covering each endpoint in use.
- [ ] `pacts/*.json` are published with git SHA and branch on every consumer build.
- [ ] Provider verification runs in CI and publishes results (`publishVerificationResult: true`).
- [ ] `can-i-deploy --to-environment production` is a required check in the deploy pipeline.
- [ ] `record-deployment` runs after successful deploys.
- [ ] Broker environments exist and `mainBranch` is configured per pacticipant.
- [ ] A deliberate breaking change on a branch fails `can-i-deploy` (test the gate, don't assume it).
- [ ] Pending/WIP pacts are enabled so new contracts do not red-line the provider.
- [ ] If BDCT: Drift runs on every provider build and the spec + result bundle are published; `can-i-deploy` reports cross-contract results.
- [ ] Message contracts exist for every event the consumer depends on.
- [ ] Stale-pacticipant alerting: any pair with no verification in 30 days is flagged.
- [ ] Consumer pact suite runs in the fast tier (<60s).

---

## References

- `references/sources.md` — Pact docs, broker, can-i-deploy, Drift CLI, BDCT, and messaging links.
- `scripts/pact_ci_gate.sh` — config-validated `can-i-deploy` gate for CI.
