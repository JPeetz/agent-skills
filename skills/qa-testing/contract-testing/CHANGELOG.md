# Changelog — Contract Testing Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-11-13

### Added
- Initial release by Skill Foundry.
- Consumer-driven contract testing principles: consumer defines the contract, pairwise scoping, assert-only-what-you-consume.
- Pact consumer test patterns in JavaScript/TypeScript (`PactV3` + `MatchersV3`), JVM (JUnit 5 `PactDslWithProvider`), and Python.
- Provider verification patterns: JS `Verifier` with `stateHandlers`, JVM `@Provider` / `PactBroker` / `PactVerificationContext`, plus a verification checklist.
- Pact Broker operations: docker setup, `pact-broker publish`, branch support, retention policy, webhook triggers, pacticipant naming rules.
- `can-i-deploy` deployment gates with pipeline ordering, `record-deployment` / `record-release`, environment vs legacy tag usage.
- API drift detection and OpenAPI conformance testing with the Drift CLI (`drift.yaml`, `drift verify --generate-result`).
- Bi-directional contract testing (BDCT): drift self-verification, `pactflow publish-provider-contract`, cross-contract `can-i-deploy`, and decision criteria for when BDCT fits.
- Event-driven contract testing: `MessageConsumerPact` / `asynchronousBodyHandler` for async messaging, `@PactVerifyProvider` on the provider side.
- Webhook contract testing: modeling outbound calls as pacts, signature-header regex matching, idempotency and retry semantics.
- CI/CD integration patterns: split consumer/provider/deploy pipelines, webhook-triggered verification, pending and WIP pacts, fail-loud config checks.
- Common pitfalls table (12 entries) covering exact-value assertions, shared mutable test data, `{ all: true }` selectors, tag-based environments, and slow suites.
- Verification checklist for auditing an existing contract-testing setup.
- `scripts/pact_ci_gate.sh` — config-validated `can-i-deploy` gate with actionable failure output.
- `references/sources.md` — Pact, Pact Broker, can-i-deploy, Drift, BDCT, and messaging documentation links.
- 3 eval scenarios covering gate diagnosis, matcher fragility, and BDCT adoption.
