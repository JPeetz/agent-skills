# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Added
- Initial release: `ai-agent-architecture` skill (new `ai-agent-engineering` category)
- Five topology patterns — single agent, supervisor, swarm, pipeline, mesh — with ASCII diagrams, use-when guidance, and the contract rules each implies
- Topology selection matrix keyed on design-time signals, with the rule "justify with a named pressure"
- Five-step architecture design process: scope → topology → contract → eval → iterate, each step producing an artifact
- Node-boundary contract table (input/output schema, error classes, idempotency key, timeout/retry, budget, version) and typed-envelope rule
- RFC-style design document skeleton
- Audit framework across four dimensions — completeness, security, observability, cost — with checklists, S1–S4 severity ranking, finding format, and report skeleton
- ADR template with context, decision, consequences, rejected alternatives, and signals that would reopen the decision
- Anti-pattern table with symptom, cause, and replacement for twelve common agent-architecture failures
- Evaluation design: five layers (unit, step, trajectory, end-to-end, online), golden-set construction rules, metrics table, pass-criteria discipline
- Execution continuity section: checkpointing, tested resume paths, partial results, compounding timeout budgets
- Red flags and dual verification checklists for completed designs and completed audits
- `evals/evals.json` with 4 trigger cases and 2 near-miss cases
- `references/sources.md` with upstream, vendor, and standards sources
