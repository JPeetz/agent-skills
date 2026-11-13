---
name: performance-testing
description: "Use this skill when planning, executing, or analyzing performance tests — load testing with k6, stress testing, soak/endurance testing, spike testing, Lighthouse CI for Core Web Vitals, performance budgets as CI gates, bottleneck identification, and capacity planning. Covers k6 scripting, thresholds, scenarios, browser-level metrics, and Lighthouse audit configuration."
license: MIT
---

# Performance Testing

Performance work is measurement, not guesswork. Every test must answer a specific question
("can we hold 2× Black Friday traffic?", "did this release regress LCP?"), have a pass/fail
criterion defined *before* it runs, and produce numbers you can compare against a baseline.

## 1. Choose the right test type

| Type | Question answered | Load shape | Duration | Pass criterion |
|---|---|---|---|---|
| **Smoke** | Does the system work under minimal load? | 1–5 VUs | 1–2 min | No errors, sane latency |
| **Load** | Do we meet SLOs at expected peak? | Ramp to expected peak, hold | 15–60 min | p95/p99 within SLO, error rate < 1% |
| **Stress** | Where does it break, and how? | Step or ramp beyond peak until failure | 30–60 min | Find breaking point; graceful degradation |
| **Soak / endurance** | What breaks over time? | 60–80% of peak, held | 2–24 h | No memory growth, no latency drift, no connection leaks |
| **Spike** | Can we survive sudden bursts? | Instant jump 1→10×, hold, drop | 5–15 min | Recovery time, error burst bounded |
| **Scalability** | Does throughput scale linearly with resources? | Repeat load test at N, 2N, 4N capacity | Varies | Throughput/cost curve, identify knee |
| **Browser / RUM** | What does the user actually experience? | Real or synthetic browsers | Continuous | Core Web Vitals "good" at p75 |

Rules of thumb:
- Always start with a **smoke test**. A failing smoke test invalidates everything downstream.
- **Never** run stress or spike tests against production without an approved window, a
  kill switch, and someone watching dashboards.
- Test **one variable at a time**. Changing script, data, and infrastructure together makes
  results uninterpretable.
- Model **think time** and realistic user mixes; hammering an endpoint with zero pause measures
  a throughput ceiling nobody experiences.

## 2. Define goals before writing scripts

Write these down in the test plan (or a comment block at the top of the script):

```text
Goal:      Validate checkout API at 3× current peak (900 rps) for 30 min
SLO:       p95 < 400 ms, p99 < 900 ms, error rate < 0.5%
Baseline:  release 2026-11-01, 300 rps, p95 210 ms
Env:       staging, same instance class as prod, seeded with 1M orders
Data:      10k unique users, cart with 1–5 items, 5% payment failures injected
Abort if:  error rate > 10% for 60 s, or DB CPU > 95%
```

If you cannot state the SLO numerically, you are not ready to test.

## 3. k6 fundamentals

### 3.1 Minimal script

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
  },
};

export default function () {
  const res = http.get('https://staging.example.com/api/products');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body is JSON': (r) => r.headers['Content-Type'].includes('application/json'),
    'has items': (r) => r.json('items').length > 0,
  });
  sleep(1);
}
```

### 3.2 Options that matter

- `stages` — ramp profile for `ramping-vus` / `ramping-arrival-rate`.
- `thresholds` — SLO assertions; a breached threshold exits non-zero (your CI gate).
- `scenarios` — multiple independent workloads in one run (browse + checkout + search).
- `discardResponseBodies: true` — big memory win when you only need status/latency.
- `summaryTrendStats` — control which percentiles appear in the summary.
- `tags` / `group()` — slice metrics by endpoint or user journey.
- `noConnectionReuse: false` — keep default keep-alive; disabling it changes results massively.
- `userAgent`, `insecureSkipTLSVerify` — only when the environment requires it.

### 3.3 Thresholds (the CI gate)

```javascript
export const options = {
  thresholds: {
    // Global
    http_req_failed:   ['rate<0.01'],
    http_req_duration: ['p(95)<400', 'p(99)<900'],
    // Per-tag
    'http_req_duration{endpoint:checkout}': ['p(95)<800'],
    'http_req_duration{endpoint:search}':   ['p(95)<250'],
    // Custom metrics
    'http_reqs': ['rate>500'],
    'order_success_rate': ['rate>0.995'],
    // Abort early to save time and money
    checks: [{ threshold: 'rate>0.95', abortOnFail: true, delayAbortEval: '10s' }],
  },
};
```

`abortOnFail` prevents a 2-hour soak from burning time after a catastrophic break.

### 3.4 Scenarios and executors

| Executor | Use for | Key params |
|---|---|---|
| `constant-vus` | Steady load, fixed concurrency | `vus`, `duration` |
| `ramping-vus` | Load with ramps | `stages` |
| `constant-arrival-rate` | Fixed request rate independent of latency | `rate`, `timeUnit`, `preAllocatedVUs`, `maxVUs` |
| `ramping-arrival-rate` | Arrival-rate ramps (better for capacity curves) | `startRate`, `stages` |
| `per-vu-iterations` | Fixed iterations per VU | `vus`, `iterations` |
| `shared-iterations` | Fixed total iterations across VUs | `vus`, `iterations` |
| `externally-controlled` | Drive VUs/rate at runtime via REST | `maxVUs`, `duration` |

**Arrival-rate executors are usually correct for capacity testing.** Constant VUs conflate
concurrency with throughput: as latency degrades, a `constant-vus` test silently sends fewer
requests, hiding the problem.

```javascript
export const options = {
  scenarios: {
    browse: {
      executor: 'ramping-arrival-rate',
      startRate: 20, timeUnit: '1s',
      preAllocatedVUs: 100, maxVUs: 800,
      stages: [
        { target: 100, duration: '2m' },  // ramp
        { target: 100, duration: '10m' }, // hold
        { target: 0,   duration: '1m' },  // ramp down
      ],
      exec: 'browse',
      tags: { journey: 'browse' },
    },
    checkout: {
      executor: 'constant-arrival-rate',
      rate: 10, timeUnit: '1s',
      duration: '13m',
      preAllocatedVUs: 50, maxVUs: 200,
      exec: 'checkout',
      startTime: '2m',
      tags: { journey: 'checkout' },
    },
  },
};

export function browse() { /* ... */ }
export function checkout() { /* ... */ }
```

### 3.5 Custom metrics

```javascript
import { Trend, Rate, Counter, Gauge } from 'k6/metrics';

const cartValue   = new Trend('cart_value_usd', true);  // true = unit ms-style percentiles ok
const loginOk     = new Rate('login_success_rate');
const orders      = new Counter('orders_created');
const queueDepth  = new Gauge('queue_depth');

export default function () {
  const t0 = Date.now();
  const res = http.post(`${__ENV.BASE_URL}/api/login`, payload, params);
  loginOk.add(res.status === 200);
  if (res.status === 200) orders.add(1);
  cartValue.add(res.json('cart.total') || 0);
}
```

Custom metrics can be thresholded exactly like built-ins — this is how you gate on
**business** outcomes (orders/min, login success) rather than only HTTP mechanics.

### 3.6 Data, auth, and realism

```javascript
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

const users = new SharedArray('users', () =>
  papaparse.parse(open('./data/users.csv'), { header: true }).data);

export function setup() {
  const res = http.post(`${__ENV.BASE_URL}/api/auth/token`, JSON.stringify({
    client_id: __ENV.CLIENT_ID, client_secret: __ENV.CLIENT_SECRET,
  }), { headers: { 'Content-Type': 'application/json' } });
  return { token: res.json('access_token') };
}

export default function (data) {
  const user = randomItem(users);
  const res = http.get(`${__ENV.BASE_URL}/api/orders`, {
    headers: { Authorization: `Bearer ${data.token}` },
    tags: { endpoint: 'orders' },
  });
  check(res, { 'ok': (r) => r.status === 200 });
}
```

- `SharedArray` keeps one copy of large datasets across VUs. A plain array is copied **per VU**
  and will exhaust memory at a few hundred VUs.
- Use `setup()` for expensive one-time auth; **never** log in every iteration unless you are
  explicitly testing the auth path.
- Seed data deterministically (`__VU`, `__ITER` or a seeded RNG) so failures are reproducible.
- Use environment variables (`__ENV`) for URLs, credentials, and profile switches. Never
  commit secrets.

### 3.7 Checks vs thresholds

`check()` records pass/fail but **does not fail the test**. Only thresholds fail a run. Use
checks for diagnostics, and mirror anything important into a threshold.

## 4. Running k6

```bash
# Local
k6 run --vus 50 --duration 2m script.js

# Named environment + summary export
k6 run -e BASE_URL=https://staging.example.com \
       --summary-export=results/summary.json script.js

# Stream raw metrics to Prometheus / InfluxDB / Grafana Cloud
K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
  k6 run -o experimental-prometheus-rw script.js

# Machine-readable output for regression diffing
k6 run --out json=results/raw.json script.js

# Distributed / cloud (optional)
k6 cloud run script.js
```

Keep a **baseline artifact** (`summary.json`) per release and diff p95/p99 and throughput.
Absolute numbers across machines are meaningless; deltas against the same rig are not.

## 5. Lighthouse CI and Core Web Vitals

### 5.1 Core Web Vitals thresholds (p75, mobile)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s |
| **INP** (Interaction to Next Paint) | ≤ 200 ms | 200–500 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| **FCP** (supporting) | ≤ 1.8 s | 1.8–3.0 s | > 3.0 s |
| **TTFB** (supporting) | ≤ 800 ms | 0.8–1.8 s | > 1.8 s |

Notes:
- **INP replaced FID in March 2024.** Do not gate on FID.
- Lab tools (Lighthouse) cannot measure INP faithfully; they approximate with TBT
  (Total Blocking Time, target < 200 ms). Gate lab INP/TBT and validate INP with RUM.
- Field data (CrUX / RUM) is truth; lab data is the fast proxy. Use both.

### 5.2 lighthouserc.js

```javascript
module.exports = {
  ci: {
    collect: {
      url: ['https://staging.example.com/', 'https://staging.example.com/pricing'],
      numberOfRuns: 3,                  // median smooths noise; never trust 1 run
      settings: {
        preset: 'desktop',              // or omit for mobile (mobile is the default gate)
        throttlingMethod: 'simulate',
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      },
      startServerCommand: 'npm run start',
      startServerReadyPattern: 'ready on',
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9, aggregationMethod: 'median-run' }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 1800 }],
        'server-response-time': ['warn', { maxNumericValue: 800 }],
        'uses-responsive-images': 'warn',
        'unused-javascript': ['warn', { maxNumericValue: 40000 }],
        'budgetsFile': 'budgets.json',
      },
    },
    upload: {
      target: 'temporary-public-storage',
      // or: target: 'lhci', serverBaseUrl: 'https://lhci.example.com'
    },
  },
};
```

Run locally: `npx @lhci/cli autorun`. Failures exit non-zero — that is the CI gate.

### 5.3 Performance budgets file

```json
[
  {
    "path": "/*",
    "resourceSizes": [
      { "resourceType": "script", "budget": 170 },
      { "resourceType": "stylesheet", "budget": 50 },
      { "resourceType": "image", "budget": 300 },
      { "resourceType": "font", "budget": 100 },
      { "resourceType": "total", "budget": 700 }
    ],
    "resourceCounts": [
      { "resourceType": "third-party", "budget": 5 },
      { "resourceType": "font", "budget": 2 }
    ],
    "timingBudget": [
      { "metric": "interactive", "budget": 3500 },
      { "metric": "first-contentful-paint", "budget": 1800 }
    ]
  }
]
```

Budgets are in **KiB**. Set them from today's measured baseline minus a stretch target, not
from an aspirational number nobody meets — a permanently red gate gets ignored.

### 5.4 GitHub Actions

```yaml
name: performance
on: [pull_request]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm run build
      - name: Lighthouse CI
        run: npx @lhci/cli autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: lighthouse-report
          path: .lighthouseci/
  k6:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - run: k6 run --summary-export=summary.json tests/load/smoke.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
```

Run **smoke-level k6 on PRs** (1–2 min) and **full load/soak on a schedule** against staging.
Nobody wants a 30-minute gate on every push.

### 5.5 Measuring Web Vitals in the browser

```javascript
// RUM: web-vitals library
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';
const send = (m) => navigator.sendBeacon('/rum', JSON.stringify({
  name: m.name, value: m.value, id: m.id, rating: m.rating, path: location.pathname,
}));
onLCP(send); onINP(send); onCLS(send); onFCP(send); onTTFB(send);
```

k6 browser module for synthetic user journeys with real rendering:

```javascript
import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    ui: { executor: 'constant-vus', vus: 5, duration: '2m',
          options: { browser: { type: 'chromium' } } },
  },
  thresholds: { browser_web_vital_lcp: ['p(95)<2500'] },
};

export default async function () {
  const page = await browser.newPage();
  try {
    await page.goto('https://staging.example.com/');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    check(page, { 'cart badge visible': async (p) => !!(await p.locator('.cart-count').textContent()) });
  } finally {
    await page.close();
  }
}
```

Browser tests are expensive (each VU ≈ one Chromium). Use a handful of VUs for journey
validation, not for load.

## 6. Bottleneck identification

Work top-down: is time spent in the client, the network, the app, the DB, or a dependency?
Never optimize without evidence from one of these sources.

**Frontend**
- LCP element is slow → check server TTFB, render-blocking CSS/JS, unoptimized hero image
  (use `srcset`, AVIF/WebP, `fetchpriority="high"`, preload).
- High TBT/INP → long tasks from hydration or third-party scripts; code-split, defer, and
  break up long tasks (`scheduler.yield`, `setTimeout` chunking).
- CLS → missing image dimensions, injected banners/ads, late-loading fonts (`font-display`,
  size-adjust metrics).

**Backend**
- p50 fine, p99 bad → queueing, lock contention, GC pauses, cold starts, noisy neighbors.
- CPU saturated with low throughput → N+1 queries, synchronous serialization, blocking I/O in
  an async path.
- Thread/worker pool exhaustion → check pool sizes, connection limits, and timeouts first.
- Look for the **knee**: throughput rises linearly then flattens while latency explodes. That
  inflection, not the failure point, is your real capacity.

**Database**
- Enable slow query log; inspect `EXPLAIN (ANALYZE, BUFFERS)` for seq scans on large tables.
- Missing/incorrect indexes show as high rows-examined-to-rows-returned ratios.
- Connection pool saturation: requests waiting on `pg_stat_activity` or an exhausted pool
  manifests as latency with *idle* CPU.
- Lock waits and long transactions turn a read-heavy test into a serial queue.

**Network / infrastructure**
- TTFB high but server app time low → DNS, TLS handshake, proxy/LB, CDN miss.
- Throughput capped exactly at a round number → load balancer, bandwidth limit, or connection
  limit, not application logic.
- Errors clustered at ramp changes → autoscaling lag, readiness probe failures, rate limiting.

Diagnostic discipline: correlate k6 timeline (ramp start, hold start) with Grafana/APM graphs
at the same timestamps. The causal step change is the bottleneck.

## 7. Capacity planning

1. **Measure unit cost** — requests/sec per instance at the knee, with p95 ≤ SLO.
2. **Project demand** — peak RPS now, growth rate, and known events (launch, campaign,
   Black Friday). Use p95 of the last 30 days × growth × event multiplier.
3. **Compute headroom** — `required_instances = peak_rps / per_instance_rps × (1 + headroom)`.
   Standard headroom is 30–50%; N+1 redundancy is on top of that, not inside it.
4. **Verify at scale** — run a load test at the projected instance count, not just the current
   one. Scaling is rarely linear (shared DB, cache, locks).
5. **Define autoscaling triggers** from measured signals (RPS per pod, p95 latency, queue
   depth), not CPU alone, and account for scale-up latency in the spike test.
6. **Record it** — a capacity table (instance class, RPS at SLO, headroom, cost per 1k req)
   that product and finance can read.

Re-derive the table after every significant architecture change. Stale capacity numbers cause
outages more often than bad code.

## 8. Anti-patterns and fixes

| Anti-pattern | Why it misleads | Fix |
|---|---|---|
| Testing only with 1–10 VUs | Hides queueing and connection pool limits | Ramp past expected peak until the knee |
| No think time | Unrealistic throughput ceiling, no cache realism | `sleep()` 0.5–5 s per journey step |
| Identical data for every VU | Cache hits everywhere; DB never stressed | Unique IDs from `SharedArray`, randomized |
| Ignoring `http_req_failed` | 500s return fast and look "performant" | Threshold error rate; check body content |
| Judging by average latency | Averages hide the p99 that users feel | Gate on p95/p99, report distribution |
| One Lighthouse run | ±10 score noise from a single run | `numberOfRuns: 3`, median aggregation |
| Desktop-only Lighthouse | Mobile is the slower, real-world case | Gate mobile; test desktop separately |
| Soak test on a laptop | Thermal throttling and shared CPU pollute results | Dedicated load generator, stable network |
| Load generator and target on one host | You measure the generator's limit | Separate hosts; watch generator CPU |
| Threshold set after seeing results | Guarantees a green build, teaches nothing | Define SLO first, then tune the system |
| Testing against a shared staging DB | Other teams' writes skew results | Isolated, seeded environment |
| No baseline | Cannot distinguish regression from noise | Store `summary.json` per release, diff it |

## 9. Reporting

Every performance report should contain: test type and load shape, environment and data,
SLO vs measured (p50/p95/p99, error rate, throughput), baseline delta, bottleneck evidence
(graph or query plan), verdict (pass/fail against thresholds), and a prioritized
recommendation list with expected impact. A report without a verdict is a dashboard, not a
test result.

## 10. Bundled files

- `scripts/k6-helpers.js` — reusable stages, thresholds, auth setup, and data helpers.
- `references/sources.md` — authoritative documentation links (k6, Lighthouse, Web Vitals).
- `evals/evals.json` — trigger and behavior evals for this skill.
