# Changelog — Performance Testing Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-11-13

### Added
- Initial release of the Performance Testing skill
- Test-type decision matrix covering smoke, load, stress, soak/endurance, spike, scalability,
  and browser/RUM testing, with load shapes and pass criteria for each
- Goal-definition template requiring numeric SLOs, baseline, environment, and abort conditions
- k6 scripting guidance: options, stages, thresholds (including per-tag and custom-metric
  thresholds), scenarios and all seven executors, checks vs thresholds semantics
- Custom metrics (Trend, Rate, Counter, Gauge) and business-level gating
- Data and auth realism: `SharedArray`, `setup()` token caching, `__ENV` configuration,
  deterministic data selection
- k6 execution guidance: summary export for baseline diffing, Prometheus remote write,
  JSON output, cloud runs
- Lighthouse CI configuration with `lighthouserc.js`, numeric assertions, median-run
  aggregation, and performance budgets file
- Core Web Vitals thresholds table (LCP, INP, CLS, FCP, TTFB) with the INP-replaced-FID note
  and lab-vs-field guidance (TBT as lab proxy)
- GitHub Actions workflows for Lighthouse CI on PRs and smoke-level k6 gates
- RUM instrumentation with the `web-vitals` library and k6 browser module journeys
- Bottleneck identification playbooks for frontend, backend, database, and network layers,
  including the throughput-knee concept
- Six-step capacity planning methodology with headroom and N+1 guidance
- Anti-pattern catalog with twelve common mistakes and concrete fixes
- Performance report structure requirements
- `scripts/k6-helpers.js` with ramp/stress/spike stage builders, SLO threshold factory,
  tagged API helpers, think-time jitter, deterministic data selection, and `requireEnv()`
- 3 eval cases: k6 load test authoring, Lighthouse CI budget gating, soak-test diagnosis
- `references/sources.md` with authoritative k6, Lighthouse CI, Web Vitals, and SRE links

### Notes
- Targets k6 v0.50+ (stable `k6/browser`) and `@lhci/cli` 0.13+
- MIT licensed
