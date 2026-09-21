# Browser Performance Metrics — Diagnostics and Tooling

## Core Web Vitals — Deep Dive

### LCP (Largest Contentful Paint)

**Target:** ≤ 2.5 s

**What it measures:** Render time of the largest image, text block, or video visible in the viewport.

**Diagnostics:**
- Lighthouse: See "LCP Element" in the report
- Chrome DevTools Performance: Record → find "LCP" marker in the Timings track
- `new PerformanceObserver((list) => { ... })` observing `largest-contentful-paint` entries

**Common causes of slow LCP:**
- Slow server response (TTFB) → optimize server, CDN, early hints
- Render-blocking resources → inline critical CSS, defer JS
- Slow image load → responsive images, preload LCP image, serve WebP/AVIF
- Client-side rendering (CSR) → add SSR or pre-rendering

### INP (Interaction to Next Paint)

**Target:** ≤ 200 ms

**What it measures:** Responsiveness of all user interactions (clicks, taps, key presses).

**Diagnostics:**
- Chrome DevTools Performance: long tasks show red in the main thread
- `long-animation-frame` API (replaces Long Tasks API for INP attribution)
- Lighthouse: "Total Blocking Time" (TBT) correlates with INP

**Common causes of poor INP:**
- Long JavaScript tasks (>50 ms) → split, defer, or yield via `setTimeout` / `scheduler.yield()`
- Large DOM size → virtualize lists, reduce DOM depth
- Expensive event handlers → debounce, throttle, memoize
- Third-party scripts → load async, defer non-critical

### CLS (Cumulative Layout Shift)

**Target:** ≤ 0.1

**What it measures:** Visual stability — how much the page moves after initial render.

**Diagnostics:**
- Lighthouse: "Avoid large layout shifts" shows specific elements
- Chrome DevTools Performance: record → select a layout shift entry → see "Impact Region"
- `PerformanceObserver` observing `layout-shift` entries

**Common causes of high CLS:**
- Images/embeds without dimensions → always set `width` / `height`
- Late-loading ads/embeds → reserve space or use placeholders
- Dynamic content injected above existing content → use explicit containers
- Web fonts causing FOIT/FOUT → `font-display: swap` / `font-display: optional`
- Animations using properties that trigger layout → prefer `transform` and `opacity` only

## Tooling

| Tool | Type | Use Case |
|------|------|----------|
| Lighthouse CI | Synthetic | PR-level performance budgets |
| PageSpeed Insights | Synthetic + RUM | Public URL analysis |
| CrUX Dashboard | RUM | Real-user aggregated data |
| `web-vitals` library | RUM | In-browser analytics |
| Chrome DevTools | Lab | Detailed profiling |
| WebPageTest | Lab | Multi-location filmstrip |
| Sitespeed.io | Synthetic | Automated CI dashboards |

## Running a Measurement

Always take 3+ runs and use the median (not the fastest). Variance between runs of 10–20% is normal.

```
lighthouse https://example.com --output=json --quiet
```