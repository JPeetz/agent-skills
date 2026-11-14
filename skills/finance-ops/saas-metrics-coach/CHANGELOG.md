# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-14

### Added
- Initial release.
- `SKILL.md` — SaaS metrics stack (instrumentation → revenue base → retention → unit economics → efficiency/cash → narrative), fixed definitions for MRR/ARR/GRR/NRR/quick ratio, the LTV/CAC and CAC-payback framework, a per-customer P&L, cash-flow and runway rules, cohort triangle guidance, benchmark tables, and an anti-pattern table.
- `scripts/metrics_calculator.py` — stdlib-only calculator taking a JSON input and emitting JSON or a markdown pack: ARR/MRR bridge with residual check, gross revenue and logo churn (period and correctly annualised monthly), GRR, NRR (with and without reactivation), quick ratio, ARPA, blended and paid CAC, margin-based LTV, LTV/CAC, CAC payback, contribution margin, magic number, burn multiple, runway, Rule of 40, benchmark banding, and severity-tagged flags. Validates input and exits non-zero on malformed data.
- `references/sources.md` — provenance and caveats for the benchmark bands, plus the formula canon.
- `evals/evals.json` — four positive and two negative evaluation cases.
- `LICENSE` (MIT), `CHANGELOG.md`.

### Notes
- New category: `finance-ops`.
- Benchmarks are directional venture-backed B2B SaaS medians, not survey-exact figures; `references/sources.md` states the population and the comparison discipline.
