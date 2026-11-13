# Sources — Contract Testing

Primary documentation for the patterns in `SKILL.md`. Every command and code shape in this skill is traceable to one of these.

## Pact — core documentation

| Topic | URL |
|---|---|
| Pact docs home | https://docs.pact.io |
| Consumer-driven contract testing — concepts | https://docs.pact.io/getting_started/how_pact_works |
| Choosing a Pact language library | https://docs.pact.io/implementation_guides |
| Pact JS (v12+) implementation guide | https://docs.pact.io/implementation_guides/javascript/readme |
| Pact JVM implementation guide | https://docs.pact.io/implementation_guides/jvm/readme |
| Pact Python implementation guide | https://docs.pact.io/implementation_guides/python/readme |
| Pact Go implementation guide | https://docs.pact.io/implementation_guides/go/readme |
| Pact .NET implementation guide | https://docs.pact.io/implementation_guides/dotnet/readme |
| Matching / matcher reference | https://docs.pact.io/getting_started/matching |
| Provider states | https://docs.pact.io/getting_started/provider_states |
| Handling auth in provider verification | https://docs.pact.io/provider/handling_auth |
| Message / asynchronous contract testing | https://docs.pact.io/getting_started/how_to_write_message_pact_tests |
| Pact JS repository (examples) | https://github.com/pact-foundation/pact-js |
| Pact JVM repository | https://github.com/pact-foundation/pact-jvm |
| Pact specification (v3/v4) | https://github.com/pact-foundation/pact-specification |

## Pact Broker

| Topic | URL |
|---|---|
| Pact Broker overview | https://docs.pact.io/pact_broker |
| Broker docker image and configuration | https://github.com/pact-foundation/pact_broker |
| Publishing pacts / CLI reference | https://docs.pact.io/pact_broker/publishing_and_retrieving_pacts |
| Branching and version selectors | https://docs.pact.io/pact_broker/branches |
| Consumer version selectors | https://docs.pact.io/pact_broker/advanced_topics/consumer_version_selectors |
| Recording deployments and releases | https://docs.pact.io/pact_broker/recording_deployments_and_releases |
| Environments | https://docs.pact.io/pact_broker/environments |
| Webhooks | https://docs.pact.io/pact_broker/webhooks |
| Pending pacts | https://docs.pact.io/pact_broker/advanced_topics/pending_pacts |
| Work-in-progress pacts | https://docs.pact.io/pact_broker/advanced_topics/wip_pacts |
| Pact CLI docker image | https://github.com/pact-foundation/pact-cli |
| Broker client tools (Ruby gem, docker, standalone) | https://docs.pact.io/pact_broker/client_cli |

## Can-I-Deploy

| Topic | URL |
|---|---|
| Can I Deploy — full reference | https://docs.pact.io/pact_broker/can_i_deploy |
| Deploying with tags (legacy path) | https://docs.pact.io/pact_broker/can_i_deploy#using-can-i-deploy-with-tags |
| Matrix and compatibility reasoning | https://docs.pact.io/pact_broker/advanced_topics/contract_matrix |

## Drift CLI — OpenAPI conformance and drift detection

| Topic | URL |
|---|---|
| Drift documentation home | https://pactflow.github.io/drift-docs |
| What is API drift | https://pactflow.github.io/drift-docs/docs/concepts/api-drift |
| Test case / `drift.yaml` schema | https://pactflow.github.io/drift-docs/docs/reference/testcases |
| Lua scripting and lifecycle hooks | https://pactflow.github.io/drift-docs/docs/reference/lua |
| Datasets | https://pactflow.github.io/drift-docs/docs/reference/datasets |
| Provider verification with Drift in BDCT | https://pactflow.github.io/drift-docs/docs/how-to/provider-verification-bdct |
| Publishing Drift results to PactFlow | https://support.smartbear.com/swagger/contract-testing/docs/en/drift/how-to-guides/publishing-drift-results-to-pactflow.html |
| Drift JSON schema (editor autocomplete) | https://download.pactflow.io/drift/schemas/drift.testcases.v1.schema.json |

## Bi-directional contract testing (BDCT)

| Topic | URL |
|---|---|
| BDCT overview | https://docs.pact.io/bi-directional-contract-testing |
| BDCT — when to use it | https://docs.pact.io/bi-directional-contract-testing/when_to_use |
| BDCT — how it works / cross-contract verification | https://docs.pact.io/bi-directional-contract-testing/how_it_works |
| `publish-provider-contract` reference | https://docs.pact.io/pact_broker/publishing_provider_contracts |
| OpenAPI specification | https://spec.openapis.org/oas/latest.html |

## Tooling and adjacent references

| Topic | URL |
|---|---|
| SmartBear / PactFlow contract testing docs (hosted broker) | https://support.smartbear.com/swagger/contract-testing/docs/ |
| PactFlow agent skills (Drift + Pact reference skills) | https://github.com/pactflow/pactflow-agent-skills |
| Pact Slack community | https://pact-foundation.slack.com |
| Pact best practices (consumer side) | https://docs.pact.io/best_practices/consumer |
| Pact best practices (provider side) | https://docs.pact.io/best_practices/provider |

## Notes on naming

PactFlow is now documented under SmartBear Swagger Contract Testing branding. The Drift CLI, its YAML schema, the result content type (`application/vnd.smartbear.drift.result`), and the `pact-broker` / `pactflow` CLI verbs are unchanged. Both `docs.pact.io` and `pactflow.github.io/drift-docs` remain the canonical references.
