# Changelog

All notable changes to the dbt-data-transformation agent skill.

## [1.0.0] — 2026-06-18

### Initial Release

Consolidated from the dbt-labs/dbt-agent-skills collection (10+ separate skills) into a single comprehensive, progressively-disclosed skill covering the complete dbt analytics engineering workflow.

### What's Included

- **5-Level Progressive Disclosure Architecture**
  - Level 1: Analytics Engineering — model patterns, materializations, Jinja macros, sources, seeds
  - Level 2: Testing — data tests, unit tests, singular tests, custom generic tests, severity thresholds
  - Level 3: Semantic Layer — MetricFlow, semantic models, metrics, dimensions, measures, saved queries
  - Level 4: dbt Mesh — cross-project refs, model contracts, access controls, groups, versions, governance
  - Level 5: Platform & Operations — job troubleshooting, CLI commands, MCP server, migration, warehouse optimization

### Key Improvements Over Source Collection

| Original (dbt-labs/dbt-agent-skills) | This Skill |
|---|---|
| 10+ separate granular skills | 1 consolidated skill with progressive disclosure |
| No domain routing / trigger mapping | Explicit trigger → domain routing table |
| No evaluation framework | Integrated eval suite (5 trigger + 2 near-miss cases) |
| No cost optimization | Warehouse cost optimization guide |
| No performance tuning | Query performance patterns + materialization decision matrix |
| No troubleshooting guide | Comprehensive job error reference table |
| No MCP server config | Full dbt MCP server configuration documentation |
| No migration guidance | v1.5+ → v1.9+ migration checklist |

### Artifacts

- `SKILL.md` — Comprehensive cross-platform skill definition (all major AI coding platforms)
- `LICENSE` — MIT
- `CHANGELOG.md` — This file
- `evals/eval_cases.json` — 7 evaluation test cases (5 trigger-positive, 2 near-miss negative)
- `scripts/validate-dbt-project.sh` — Project structure validation + compile + DAG check
- `scripts/dbt-test-runner.sh` — Test runner with severity filtering + structured reports
- `references/dbt-model-patterns.md` — Staging/intermediate/marts patterns, materialization matrix, incremental strategies
- `references/dbt-mesh-governance.md` — Cross-project refs, contracts, access controls, group/version management
- `references/dbt-semantic-layer.md` — MetricFlow patterns, semantic models, metrics, dimensions, saved queries
