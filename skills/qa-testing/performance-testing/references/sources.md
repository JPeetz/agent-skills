# Sources

Authoritative references for the material in this skill. Prefer these over blog posts;
vendor blogs and tutorials are useful for examples but drift from the spec.

## k6 (load testing)

- k6 documentation home — https://grafana.com/docs/k6/latest/
- Test scripts and lifecycle (`default`, `setup`, `teardown`) — https://grafana.com/docs/k6/latest/using-k6/test-lifecycle/
- Options reference (all fields used in `export const options`) — https://grafana.com/docs/k6/latest/using-k6/k6-options/reference/
- Thresholds — https://grafana.com/docs/k6/latest/using-k6/thresholds/
- Scenarios and executors — https://grafana.com/docs/k6/latest/using-k6/scenarios/
- Executor comparison table — https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/
- Metrics reference (`http_req_duration`, `http_req_failed`, `http_reqs`, …) — https://grafana.com/docs/k6/latest/using-k6/metrics/reference/
- Custom metrics (Trend/Rate/Counter/Gauge) — https://grafana.com/docs/k6/latest/using-k6/metrics/create-custom-metrics/
- Checks — https://grafana.com/docs/k6/latest/using-k6/checks/
- Test data and `SharedArray` — https://grafana.com/docs/k6/latest/using-k6/test-authoring/test-data/
- Environment variables (`__ENV`) — https://grafana.com/docs/k6/latest/using-k6/environment-variables/
- k6 browser module (real Chromium, Web Vitals) — https://grafana.com/docs/k6/latest/using-k6-browser/
- Results output (JSON, Prometheus remote write, Grafana Cloud) — https://grafana.com/docs/k6/latest/results-output/
- k6 OSS vs Cloud feature matrix — https://grafana.com/docs/k6/latest/testing-guides/

## Lighthouse CI

- Lighthouse CI overview — https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/getting-started.md
- Configuration reference (`lighthouserc.js`) — https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/configuration.md
- Assertions reference (`ci.assert.assertions`) — https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/assertions.md
- Lighthouse performance budgets — https://developer.chrome.com/docs/lighthouse/performance/performance-budgets
- Lighthouse CI on GitHub Actions — https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/getting-started.md#github-actions
- Lighthouse scoring and throttling — https://developer.chrome.com/docs/lighthouse/overview/
- Lighthouse audit catalog (metric definitions) — https://developer.chrome.com/docs/lighthouse/performance/performance-scoring

## Core Web Vitals and web performance

- Web Vitals overview — https://web.dev/articles/vitals
- LCP — https://web.dev/articles/lcp
- INP — https://web.dev/articles/inp
- CLS — https://web.dev/articles/cls
- TTFB — https://web.dev/articles/ttfb
- FCP — https://web.dev/articles/fcp
- `web-vitals` JavaScript library — https://github.com/GoogleChrome/web-vitals
- Chrome UX Report (field data) — https://developer.chrome.com/docs/crux/
- PageSpeed Insights — https://pagespeed.web.dev/
- Optimize LCP — https://web.dev/articles/optimize-lcp
- Optimize INP — https://web.dev/articles/optimize-inp
- Optimize CLS — https://web.dev/articles/optimize-cls
- Resource hints (`preload`, `preconnect`) — https://web.dev/articles/preconnect-and-dns-prefetch

## Methodology and practice

- Google SRE Book, "Handling Overload" — https://sre.google/sre-book/handling-overload/
- Google SRE Workbook, "Non-Abstract Large System Design" (capacity) — https://sre.google/workbook/non-abstract-large-system-design/
- "The USE Method" (Utilization, Saturation, Errors) — https://www.brendangregg.com/usemethod.html
- Brendan Gregg, Systems Performance (book) — methodology for bottleneck analysis
- PostgreSQL `EXPLAIN` documentation — https://www.postgresql.org/docs/current/using-explain.html
- PostgreSQL slow query / statistics views — https://www.postgresql.org/docs/current/monitoring-stats.html
- HTTP caching (RFC 9111) — https://www.rfc-editor.org/rfc/rfc9111

## Tooling around k6 and Lighthouse

- xk6 extensions (build custom k6 binaries) — https://github.com/grafana/xk6
- k6 utility library (`k6-utils`) — https://jslib.k6.io/k6-utils/
- Lighthouse plugin ecosystem — https://github.com/GoogleChrome/lighthouse#lighthouse-plugins
- Chrome DevTools Performance panel — https://developer.chrome.com/docs/devtools/performance/
