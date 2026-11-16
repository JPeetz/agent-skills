# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-16

### Added
- `SKILL.md` — the full modelling stack: driver-tree discipline, bottoms-up P&L construction by channel (with rep ramp and seasonality), COGS decomposition, headcount-led OPEX with burden and hire lag, the P&L → balance sheet → cash flow link table and build order, scenario design as a single driver switch, tornado and breakeven sensitivity, unit economics on gross-margin dollars, SaaS stock-and-flow modelling with cohort decay, DCF with terminal-value cross-checks, fundraising mechanics (pre/post-money, option-pool shuffle, stacked SAFEs, liquidation waterfall), the twelve metrics every model must emit, a data-quality checklist, a seventeen-row anti-pattern table, an investor-presentation order, and a verification checklist.
- `scripts/financial_model_builder.py` — stdlib-only three-statement engine taking a JSON spec and emitting monthly P&L, cash flow and balance sheet for 1–60 months plus annual roll-up. Driver-based MRR roll-forward with seasonality, headcount plan by department with per-month additions and COGS/OPEX bucketing, per-vintage straight-line depreciation, working capital from DSO/DPO/deferred-revenue drivers, debt schedule, tax with NOL carry-forward, indirect cash flow, derived balance sheet with a per-month balance residual, twelve operating metrics, severity-tagged flags, and a `--self-test` that verifies twenty invariants including six negative input validations. Exits non-zero on bad input and warns (exit 3) when the model does not foot.
- `references/model-framework.md` — the four model types (three-statement, bottoms-up, top-down, cohort), fit by company stage from pre-seed to pre-IPO, the fourteen-step three-statement build sequence, the six-step revenue build, the distinction between scenario/sensitivity/stress test, ten model-architecture rules, and a structural-error table by model type.
- `evals/evals.json` — four positive and two negative evaluation cases covering the three-statement build, survivable scenario planning, fundraising dilution with pool shuffle and SAFEs, sensitivity ranking, refusal to back-solve to a target, and the audit/tax/investment-advice boundary.
- `LICENSE` (MIT), `CHANGELOG.md`.

### Notes
- Complements rather than duplicates `saas-metrics-coach`: that skill computes and interprets a metrics pack from historical data, this one builds the forward-looking model that produces those metrics.
- The balance-residual check, cash-to-statement tie, ARR-to-MRR tie and retained-earnings tie are hard gates in the script, not advisory warnings, because a model that does not foot has no evidentiary value.
