---
name: performance-optimization
description: >-
  Use this skill when optimizing application performance across frontend (Core Web Vitals,
  bundles), backend (N+1 queries, connection pools, caching), and database (indexes,
  query plans). Profiles before fixing, pinpoints actual bottlenecks rather than assumed
  ones, verifies improvements by re-measuring the same way as baseline.
version: 1.0.0
platforms: [openclaw, claude, codex, cursor, gemini, copilot, opencode, windsurf]
author:
  name: JPeetz
  source: Google Web Vitals, WebPageTest, Lighthouse, usehooks-ts, addyosmani/agent-skills
license: MIT
risk_tier: L1
tags: [devops, performance, web-vitals, optimization, profiling, lighthouse, core-web-vitals, query-optimization]
requires:
  binaries: []
---

# Performance Optimization

Measure before optimizing. Performance work without measurement is guessing — and guessing leads to premature optimization that adds complexity without improving what matters. Profile first, identify the actual bottleneck, fix it, measure again. Optimize only what measurements prove matters.

## When to Use This Skill

Use this skill when:

- Performance requirements exist in the spec (load time budgets, response time SLAs, LCP/INP/CLS targets)
- Users or monitoring report slow behavior (high latency, sluggish interactions, jank)
- Core Web Vitals scores are below 'Good' thresholds
- You suspect a recent change introduced a performance regression
- Building features that handle large datasets or high traffic volumes
- Profiling or tracing reveals a bottleneck that needs addressing
- An N+1 query pattern is discovered in data-fetching code
- Bundle size analysis shows large, unnecessary dependencies

**When NOT to use:** Do not optimize before you have empirical evidence of a problem. Premature optimization is a known source of bugs, complexity, and wasted effort. If you're guessing at what's slow, measure first.

## Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5 s | ≤ 4.0 s | > 4.0 s |
| **INP** (Interaction to Next Paint) | ≤ 200 ms | ≤ 500 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| **FCP** (First Contentful Paint) | ≤ 1.8 s | ≤ 3.0 s | > 3.0 s |
| **TTFB** (Time to First Byte) | ≤ 800 ms | ≤ 1.8 s | > 1.8 s |

## The Optimization Workflow

```
 1. MEASURE   → Establish a baseline with real data (Lighthouse, RUM, EXPLAIN ANALYZE)
 2. IDENTIFY  → Find the actual bottleneck — not the assumed one
 3. FIX       → Address the specific bottleneck with a targeted change
 4. VERIFY    → Re-measure using the same method as the baseline
 5. GUARD     → Add monitoring, budgets, or regression tests
```

### Step 1: MEASURE — Establish Baseline

Use **synthetic** tools for repeatable, controlled measurements:

- **Lighthouse / PageSpeed Insights** — lab-based scoring for Core Web Vitals
- **Chrome DevTools Performance tab** — flame graphs, network waterfall, bundle analysis
- **WebPageTest** — multi-location RUM-like testing with filmstrips
- **`EXPLAIN ANALYZE`** — for database query performance baselines
- **`profile` / `perf` / `py-spy`** — for backend process profiling

Complement with **Real User Monitoring (RUM)** to capture real-world conditions:

- `web-vitals` library — JavaScript library reporting live LCP, INP, CLS
- CrUX (Chrome User Experience Report) — aggregated field data from real Chrome users
- APM tools (Datadog, New Relic, Sentry) — backend latency distributions

**Record the baseline numbers.** Without a specific before-value, you cannot know if an optimization worked.

### Step 2: IDENTIFY — Find the Actual Bottleneck

Diagnose by symptom:

| Symptom | Common Causes | Diagnostic Tool |
|---------|---------------|-----------------|
| **Slow LCP** | Large images, render-blocking resources, slow server response | Lighthouse, network waterfall |
| **High CLS** | Missing image dimensions, late-loading ads/fonts, dynamic embeds | Lighthouse CLS diagnostic, layout shift tracker |
| **Poor INP** | Long tasks (heavy JS), large DOM, slow event handlers | Performance tab, Long Tasks API |
| **Large bundle size** | Unused dependencies, no code splitting, duplicated modules | `vite-bundle-analyzer`, `webpack-bundle-analyzer` |
| **N+1 queries** | ORM lazy loading in loops | `EXPLAIN ANALYZE`, Rails/ActiveRecord logs, Django Debug Toolbar |
| **Slow API responses** | Missing indexes, inefficient joins, connection pool exhaustion | `EXPLAIN ANALYZE`, connection pool metrics |
| **High memory** | Unbounded caches, memory leaks, large datasets in memory | Heap snapshots, `malloc` profiling |

### Step 3: FIX — Address Anti-Patterns

Apply targeted fixes based on the identified bottleneck. Each fix must be justified by data from Step 2, not by intuition.

#### Frontend

| Anti-Pattern | Recommended Fix |
|---|---|
| **Images too large for display size** | Use `<picture>` / `srcset` with responsive breakpoints; serve WebP/AVIF |
| **Render-blocking CSS/JS** | Inline critical CSS; defer non-critical JS with `type="module"` or `defer` |
| **Missing image dimensions** | Always set `width` and `height` attributes to reserve layout space |
| **Heavy client-side JS** | Code-split by route with dynamic `import()`; tree-shake unused exports |
| **Unnecessary re-renders** (React) | `React.memo`, `useMemo`, `useCallback`; stable references for props |
| **Font loading causes CLS** | Use `font-display: swap` or `font-display: optional` with `size-adjust` |
| **Large third-party scripts** | Load async; defer if not critical; evaluate removal |

#### Backend

| Anti-Pattern | Recommended Fix |
|---|---|
| **N+1 queries** | Use eager loading (joins, includes); batch in a single query |
| **Unbounded data fetching** | Paginate with cursor-based or offset-based limits |
| **Missing database indexes** | Add composite indexes matching query patterns; verify with `EXPLAIN` |
| **Connection pool exhaustion** | Tune pool size (`max_connections`); add PgBouncer or proxy multiplexing |
| **No caching** | Add HTTP caching headers; application-level cache for expensive + cold data |
| **Serializing large responses** | Project only needed fields; use pagination + streaming |

#### Database

| Anti-Pattern | Recommended Fix |
|---|---|
| **Table scan on large table** | Add index; rewrite query to use index; partition table |
| **Inefficient JOIN order** | Restructure query to filter most selective conditions first |
| **Over-fetching columns** | `SELECT *` → `SELECT needed_columns` |
| **No query plan check before index** | Always run `EXPLAIN (ANALYZE, BUFFERS)` before and after adding an index |

### Step 4: VERIFY — Re-measure the Same Way

1. Run the **exact same measurement** (same tool, same page, same location)
2. Compare numbers against the baseline
3. If the change did NOT improve the metric → **revert it**
4. If the change improved one metric but regressed another → **decide by SLA priority**

### Step 5: GUARD — Prevent Regression

- **Performance budgets** — set thresholds in Lighthouse CI (e.g. "LCP must stay under 2.5s")
- **Lighthouse CI** — fail PR builds that exceed budgets
- **Bundle size checks** — compare PR bundle diffs with tools like `bundlewatch`
- **Custom RUM dashboards** — monitor P75, P95, and P99 of key metrics
- **Database migration guard** — run `EXPLAIN ANALYZE` on slow queries before deployment

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll optimize later" | Performance debt compounds. Fix obvious anti-patterns now. |
| "It's fast on my machine" | Profile on representative hardware + throttled network. Dev machines are not production. |
| "This optimization is obvious" | If you didn't measure, you don't know. Assumptions are wrong >50% of the time. |
| "The query is slow, add an index" | Read the query plan first. The index may already be unusable, or the issue may be different. |
| "Just cache it" | Cache only what is expensive to compute AND re-read far more often than written. A cache that never hits is dead weight. |
| "A CDN will fix the speed" | CDNs improve TTFB for global users but don't fix bloated bundles, N+1 queries, or layout shifts. |
| "We'll lazy-load everything" | Over-lazy-loading delays interactivity. Critical above-fold content should load eagerly. |
| "Let's rewrite in [framework]" | Framework rewrites are the most expensive performance "fix." Profile first; a targeted change is cheaper by orders of magnitude. |
| "It passed Lighthouse, we're good" | Lighthouse is a synthetic lab test. Real-user conditions (2G, older devices, ad blockers) will differ. Always validate with RUM. |

## Red Flags

- Optimization work performed **without profiling data**
- N+1 query patterns in any new or changed data-fetching code
- An index added **without reviewing the query plan before and after**
- A cache implementation with **no stated staleness window or eviction policy**
- List endpoints without pagination or with unbounded `LIMIT`
- Images rendered without explicit `width` and `height` dimensions
- Optimizations kept in production **without re-measurement** confirming improvement
- Performance improvements claimed based on a single measurement (variance is real — average 3+ runs)
- A framework migration proposed as a performance fix without profiling evidence

## Verification

- [ ] Before and after measurements exist with specific numbers (not "felt faster")
- [ ] The result was re-measured using the same tool/method as the baseline
- [ ] Changes that didn't meaningfully beat baseline variance were reverted
- [ ] Core Web Vitals are within 'Good' thresholds on the optimized page(s)
- [ ] No N+1 queries exist in new or modified data-fetching code
- [ ] Every new index is justified by a query plan (EXPLAIN ANALYZE before + after)
- [ ] Cache implementations document: what is cached, TTL/staleness, max size, eviction policy
- [ ] All paginated endpoints have bounded limits and cursor/offset documentation
- [ ] Images have explicit width/height attributes and format for responsive delivery
- [ ] Bundle size is verified — no unexpected growth vs. baseline
- [ ] Existing functional tests still pass after optimization changes
- [ ] RUM data confirms lab improvements hold under real-world conditions

## References

- `references/browser-performance-metrics.md` — detailed Core Web Vitals diagnostics and tooling
- `references/query-optimization.md` — database query profiling and index design guidelines
- `references/image-optimization-guidelines.md` — responsive images, format selection, lazy loading