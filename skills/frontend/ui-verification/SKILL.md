---
name: ui-verification
description: Use this skill when asked to verify UI in the browser, reproduce a UI finding, re-measure after a fix, or try to break a feature with browser probes.
version: 0.1.0
author: Matthew Blode (mblode), Skill Foundry
license: MIT
compatibility: Requires access to the target app and browser automation (Playwright or a DevTools-protocol driver).
platforms:
  - linux
  - macos
tags:
  - frontend
  - testing
  - browser
  - accessibility
  - performance
  - qa
---

# UI Verification

Owns the browser session. Every other UI skill reasons about source and infers
what the user will see; this one loads the page and measures it.

- **IS:** booting the app, driving it with a browser, and running probes that
  decide a rule at runtime — computed boxes, injected failures, observed layout
  shift, a scripted Tab walk, an axe scan per theme. Output is findings keyed to
  rule ids with reproducible evidence, plus the clearing re-run after a fix. Also
  the exploratory pass: a fresh tester driving a finished feature like a user to
  find the cases its contract never listed.
- **IS NOT:** finding defects by reading source or deciding their tier and ship
  verdict (a static UI audit owns both); building or restyling UI; authoring a
  durable test suite (write Playwright tests); building or maintaining a whole
  app's persistent verify CLI, doctor command, and feature map; persistent
  pixel-baseline approval workflows (Chromatic, Percy); field performance (RUM or
  CrUX — Lighthouse and Web Vitals here are lab measurements).

The division of labour is the point. A static audit reports what the code will
probably do; it cannot see a 40px control whose hit area a pseudo-element
already expands to 44px, or a retry button wired to nothing. This skill
reproduces or kills each of those, so a finding arrives with a measurement
instead of a confidence.

## Contents

- [When to run](#when-to-run)
- [Probe catalogue](#probe-catalogue)
- [Progress checklist](#progress-checklist)
- [1. Establish the session](#1-establish-the-session)
- [2. Select the probe set](#2-select-the-probe-set)
- [3. Run the probes](#3-run-the-probes)
- [Probe playbooks](#probe-playbooks)
- [4. Decide each finding](#4-decide-each-finding)
- [5. Clearing re-run](#5-clearing-re-run)
- [6. Report](#6-report)
- [Honesty rules](#honesty-rules)
- [Gotchas](#gotchas)
- [Related skills](#related-skills)

## When to run

| Situation | What this skill does |
|---|---|
| An audit emitted findings and the user wants them confirmed | Run only the probes those rule ids map to (see the catalogue) |
| No audit ran; the user points at a route or a running app | Detect the feature type, run the full battery on the resolved routes |
| A fix just landed for a previously reproduced finding | Run the clearing re-run only (step 5) |
| Acceptance checks pass and the user wants a feature tried like a real user, or asks to "try to break it" | Read [references/exploratory-test.md](references/exploratory-test.md) |
| The user asks for captures across themes or widths | Probe 7 (theme/locale matrix), then [references/visual-review.md](references/visual-review.md) |
| The user asks to review a UI change or named screenshot states | [references/visual-review.md](references/visual-review.md) for matched before/after inspection |
| A design system claims a type or spacing scale | Read the claimed values off computed styles on a real page; a theme value the build overrides never reaches the browser |

Nothing here assigns a tier or a ship verdict: hand reproduced findings back with
their evidence and let the audit skill tier them. Two skills tiering the same
finding is how the tiers drift apart.

## Probe catalogue

Nine probes. Each entry states what it measures, its primary rule coverage, and
the evidence shape. Recipes live in [Probe playbooks](#probe-playbooks) below —
there is no separate probe directory, because this repo ships no browser test
infrastructure of its own.

| # | Probe | Measures | Primary for |
|---|---|---|---|
| 1 | `axe-scan` | axe-core violations per route and theme, including computed contrast | contrast, accessible names, landmarks |
| 2 | `target-size` | Bounding box and effective hit area of every visible interactive element | `interaction-target-size` |
| 3 | `focus-walk` | Scripted Tab traversal, focus-ring pixel delta, dialog trap and restoration | `focus-*`, `interaction-focus-visible`, `interaction-keyboard-operable` |
| 4 | `layout-shift` | Attributed `layout-shift` entries with the data response held open | `states-layout-shift`, `perf-image-dimensions-and-priority` |
| 5 | `viewport-stress` | Horizontal overflow and clipped text at 320px and up, and under tripled strings | `layout-long-content-safety`, `mobile-viewport-scaling` |
| 6 | `failure-injection` | What renders when the data request returns 500, `[]`, malformed, or nothing | `states-no-error-state`, `states-no-empty-state`, `async-*`, `microcopy-*` |
| 7 | `theme-locale-matrix` | The same route captured across viewport, theme, pseudo-locale, and direction | `dark-i18n-untested`, `dark-i18n-rtl-untested` |
| 8 | `console-network` | Console errors, page errors, failed requests, hydration mismatch warnings | hydration mismatch, silent runtime failures |
| 9 | `web-vitals` | LCP with its attributed element, CLS, INP on a scripted interaction | perf attribution, never a budget verdict |

`axe-scan`, `console-network`, and `viewport-stress` run on every route
regardless of feature type: they are cheap, and they are the three that find
things nobody suspected.

## Progress checklist

```text
Verification progress:
- [ ] Step 1: Establish the session — driver, build mode, base URL, auth, resolved routes
- [ ] Step 2: Select the probe set from handed-over rule ids or from the routes
- [ ] Step 3: Run each probe; write evidence artifacts before interpreting any of them
- [ ] Step 4: Decide each finding reproduced / not-reproduced / unknown; repeat timing-sensitive results
- [ ] Step 5: For each fix applied, re-run the identical probe and record clearedBy
- [ ] Step 6: Report per finding with evidence paths, then render
- [ ] Step 7: List probes skipped and why. A probe that could not run is never a pass
```

## 1. Establish the session

Resolve four things; getting any of them wrong invalidates every probe
downstream.

- **Driver.** Playwright when the repo can run it, the DevTools browser tools
  when it cannot. Four probes (layout-shift, failure-injection, theme matrix,
  web-vitals) need request interception and network control, so they do not
  exist under a driver without them.
- **Build mode.** Perf and layout-shift probes run against a production build;
  dev-mode numbers measure the bundler. Failure injection and focus probes run
  fine in dev.
- **Auth and seeded data.** A route behind a login with no seeded session
  returns `unknown`, never a pass.
- **Routes.** Map the diff to URLs. A component with no reachable route falls
  back to the repo's Storybook, and to `unknown` if there is none.

Record the session before probing, e.g.:

```text
session:
  baseUrl: http://localhost:3000
  buildMode: production
  driver: playwright 1.x
  auth: seeded test user (fixture)
  routes: ["/", "/checkout", "/settings/profile"]
  viewports: [360, 1280]
  themes: [light, dark]
```

Stop here if the app will not boot. A verification run with no session produces
no findings, which is a reportable outcome and not a clean bill of health.

## 2. Select the probe set

**Handed a list of rule ids** (the normal case): take the probe each id maps to
from the catalogue and run only those. Ids with no probe stay source-only
findings and pass through untouched, marked as such.

**Given only routes:** detect the feature type (form, list, modal, dashboard,
checkout), then run the battery that surface earns:

| Feature | Minimum probe set |
|---|---|
| Form | axe, focus-walk, target-size, failure-injection, console |
| List / table | axe, viewport-stress, layout-shift, failure-injection |
| Modal / dialog | focus-walk (trap + restore), axe, target-size |
| Dashboard | axe, layout-shift, web-vitals, theme matrix |
| Checkout | axe, focus-walk, failure-injection, target-size, console |

Budget the matrix before running it. Routes × viewports × themes grows fast,
and a run that takes twenty minutes gets skipped next time. Two viewports (360
and 1280) and two themes cover the ground; add widths only where a probe
already found an edge.

## 3. Run the probes

Each playbook carries its own recipe. Three rules hold across all of them:

- **Capture evidence before interpreting it.** Write the screenshot, the JSON
  measurement, and the console log to disk first. A finding whose evidence was
  never written is unverifiable by the person reading the report.
- **One probe, one route, one viewport, one theme.** Never fold two conditions
  into one run: when the result surprises you, you need to know which axis
  produced it.
- **Repeat uncertain measurements.** Retry timing-sensitive or inconsistent
  results under controlled conditions. A deterministic failure with a captured
  trigger needs no duplicate run. A result that flips remains inconclusive until
  its conditions are understood.

For UI-change and named-state captures, inspect the images yourself before
reporting, following [references/visual-review.md](references/visual-review.md).
Record visual observations separately from measured probe results.

## Probe playbooks

Recipes use the Playwright page API. Under a DevTools driver, substitute the
equivalent CDP call and say so in the report — `Runtime.evaluate` for the
measurements, `Network.setRequestInterception` for the injections, and note
that no equivalent exists for `layout-shift` attribution without the Performance
domain.

### 1. axe-scan

Inject axe-core from the local dependency or a pinned CDN URL (never `latest`),
scan each route in each theme, and store the raw violations JSON.

```js
await page.addScriptTag({ path: require.resolve('axe-core/axe.min.js') });
const results = await page.evaluate(async () => await axe.run(document, {
  runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'] }
}));
```

- Run after the theme attribute is asserted and after fonts settle, or computed
  contrast reads the fallback font.
- Disable animations and wait for `document.fonts.ready` first.
- False positives to guard: colour-contrast node reports on elements hidden by
  `opacity: 0` but still in the a11y tree; `region` best-practice violations on
  intentional full-bleed pages.
- Evidence: `axe-<route>-<theme>.json` plus a screenshot of each violation node
  cropped to its bounding box.

### 2. target-size

Walk every visible interactive element and record its bounding box, plus the
effective hit area including pseudo-element expansion.

```js
const boxes = await page.evaluate(() => {
  const sel = 'a[href],button,input,select,textarea,[role="button"],[role="link"],[tabindex]:not([tabindex="-1"])';
  return [...document.querySelectorAll(sel)].filter(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.opacity !== '0';
  }).map(el => {
    const r = el.getBoundingClientRect();
    const before = getComputedStyle(el, '::before');
    const after = getComputedStyle(el, '::after');
    return { tag: el.tagName, text: (el.textContent || '').trim().slice(0, 40),
      w: +r.width.toFixed(1), h: +r.height.toFixed(1),
      pseudoBefore: before.content !== 'none', pseudoAfter: after.content !== 'none' };
  });
});
```

- Report size in px with the viewport width, e.g. `32x32px at 360px width, touch
  emulation on`.
- False positives to guard: elements enlarged by an absolutely positioned
  pseudo-element (check the pseudo's own box before failing); inline links
  inside a paragraph (WCAG 2.5.8 exempts inline targets); elements whose
  spacing alone satisfies 2.5.8's spacing exception.
- Evidence: `targets-<route>-<viewport>.json` plus a screenshot with outlined
  boxes when any element is under the threshold.

### 3. focus-walk

Script a Tab traversal, record the focused element at each step, and measure
the focus-ring delta as rendered pixels.

```js
const walk = [];
for (let i = 0; i < 40; i++) {
  await page.keyboard.press('Tab');
  walk.push(await page.evaluate(() => {
    const el = document.activeElement;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return { tag: el.tagName, id: el.id, name: el.getAttribute('aria-label') || el.textContent.trim().slice(0, 40),
      outline: `${cs.outlineStyle} ${cs.outlineWidth} ${cs.outlineColor}`,
      boxShadow: cs.boxShadow, rect: [r.x, r.y, r.width, r.height].map(n => +n.toFixed(1)) };
  }));
}
```

- For dialogs: open it, Tab past the last focusable element, assert focus wraps
  inside, press Escape, assert focus returns to the opener — capture
  `document.activeElement` before opening and after closing.
- Measure the ring with a screenshot diff of the element region focused vs
  unfocused; a computed `outline: none` with no `box-shadow` is a fail without
  needing pixels.
- False positives to guard: `:focus-visible` only engages on keyboard input, so
  never synthesize focus with `el.focus()` when testing the ring; skip hidden
  elements in the count.
- Evidence: `focus-walk-<route>.json` (ordered list) plus before/after crops of
  any element with no visible delta.

### 4. layout-shift

Hold the data response open, record attributed shift entries, and release.

```js
await page.evaluate(() => {
  window.__shifts = [];
  new PerformanceObserver(list => {
    for (const e of list.getEntries()) if (!e.hadRecentInput) window.__shifts.push({
      value: e.value, sources: (e.sources || []).map(s => ({
        node: s.node && s.node.nodeName, prev: s.previousRect, curr: s.currentRect }))
    });
  }).observe({ type: 'layout-shift', buffered: true });
});
```

- Delay the API route by 1500ms with `page.route`, navigate, wait for the
  response to render, then read `window.__shifts`.
- Production build only; dev-mode hydration and on-demand compilation inject
  shifts that do not ship.
- False positives to guard: shifts from a web font swap on a page whose font is
  already cached (run twice, use the second run); shifts caused by the probe's
  own injected banner.
- Evidence: `cls-<route>.json` with per-entry value and source selectors, plus a
  filmstrip of frames around the shift when it exceeds the reporting threshold.

### 5. viewport-stress

Check horizontal overflow and clipped text at 320px and up, then under tripled
strings.

```js
const overflow = await page.evaluate(() => ({
  scrollW: document.documentElement.scrollWidth,
  clientW: document.documentElement.clientWidth,
  offenders: [...document.querySelectorAll('*')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.right > document.documentElement.clientWidth + 1;
  }).slice(0, 20).map(el => `${el.tagName}.${el.className}`.slice(0, 80))
}));
```

- Sweep widths 320, 360, 414, 768, 1024, 1280 and record only widths where
  `scrollWidth > clientWidth`.
- For long content: set a pseudo-locale or multiply text nodes by 3
  (`el.textContent = el.textContent.repeat(3)`) in a throwaway pass, then check
  for `text-overflow` clipping and overlapping boxes.
- False positives to guard: intentional horizontal scrollers (carousels, code
  blocks) — assert `overflow-x: auto` on the ancestor before reporting; fixed
  decorative elements parked off-canvas.
- Evidence: `overflow-<route>-<width>.json` plus a full-page screenshot at each
  failing width.

### 6. failure-injection

Drive the same route under four data conditions and capture what renders.

```js
await page.route('**/api/**', route => route.fulfill({ status: 500, body: '{}' }));
// then: status 200 body '[]'; status 200 body '{"unexpected":true}'; route.abort('failed')
```

- One condition per run; reset routes between runs with `page.unroute`.
- Assert on rendered text and role, not just the absence of a spinner: an empty
  `[]` that renders a blank panel is `states-no-empty-state`, a 500 that renders
  nothing is `states-no-error-state`.
- Check the retry path actually re-requests: count network calls after clicking
  retry.
- False positives to guard: the app's global error boundary swallowing a
  localised failure (report it as a finding, not as a harness bug, if the
  boundary hides the whole page); cached service-worker responses answering
  after the route is intercepted (disable the SW or use a clean context).
- Evidence: `failure-<route>-<condition>.png` plus the captured response status
  and the retry call count.

### 7. theme-locale-matrix

Capture one route across viewport × theme × locale × direction.

```js
await page.evaluate(() => document.documentElement.setAttribute('lang', 'ar'));
await page.evaluate(() => document.documentElement.setAttribute('dir', 'rtl'));
```

- Prefer the app's own theme toggle. When setting the attribute directly,
  assert it landed (`document.documentElement.className` /
  `getAttribute('data-theme')`) before capturing, and re-run axe in that theme.
- Pseudo-locale: `en-XA` via the app's i18n config where available, else
  triple-length strings.
- Budget: 2 viewports × 2 themes × 2 directions = 8 captures per route. Add a
  locale only where a string-length failure is suspected.
- Evidence: `matrix-<route>-<vw>-<theme>-<dir>.png` named so a reviewer can sort
  them, plus the axe JSON per theme.

### 8. console-network

Collect from before the first navigation, not after.

```js
page.on('console', m => { if (['error', 'warning'].includes(m.type())) logs.push({ type: m.type(), text: m.text() }); });
page.on('pageerror', e => logs.push({ type: 'pageerror', text: e.message }));
page.on('requestfailed', r => logs.push({ type: 'requestfailed', url: r.url(), err: r.failure()?.errorText }));
page.on('response', r => { if (r.status() >= 400) logs.push({ type: 'http', url: r.url(), status: r.status() }); });
```

- Hydration mismatches surface as React/Vue warnings naming the mismatched
  node; capture the full text, not the first line.
- False positives to guard: favicon and source-map 404s; HMR noise in dev mode;
  extensions' console chatter (use a clean context).
- Evidence: `console-<route>.json`.

### 9. web-vitals

Measure LCP with its element, CLS, and INP on a scripted interaction.

```js
await page.evaluate(() => {
  window.__vitals = {};
  new PerformanceObserver(l => { const e = l.getEntries().at(-1);
    window.__vitals.lcp = { value: e.startTime, el: e.element && (e.element.tagName + '.' + e.element.className) }; })
    .observe({ type: 'largest-contentful-paint', buffered: true });
});
```

- Production build, cold cache, throttled CPU/network if the user asked for
  realistic numbers — and record the throttling in the report either way.
- INP needs a real interaction: click the primary control, measure from input
  to next paint.
- This probe attributes performance; it never issues a budget verdict. Report
  the number with its conditions and let the user decide.
- Evidence: `vitals-<route>.json` with the metric, value, attributed element,
  and throttling conditions.

## 4. Decide each finding

Three outcomes, and the middle one is the one that earns this skill its keep.

| Outcome | Meaning | What it does to the handed-over finding |
|---|---|---|
| `reproduced` | The probe measured the defect | Stays a `fail`, now carrying `observed` from the measurement rather than from the source read |
| `not-reproduced` | The tested conditions did not exhibit the defect | Withdraw only if the probe exercised the alleged trigger; otherwise retain the candidate with the remaining coverage gap |
| `unknown` | The probe could not run or could not decide | Finding survives as `unknown` with the probe's reason. Never converts to a pass |

A `not-reproduced` result is a real deliverable, not a wasted run. It is what
removes the false positives a large rule corpus asserts with `file:line`
confidence.

Where a probe finds something no static rule predicted, emit it as a new
finding against the rule id the probe is primary for. Where no rule covers it
(an axe violation with no corpus counterpart, a console error), emit it under
`axe:`, `runtime:`, or `explore:` from an exploratory pass, and say plainly that
it came from the browser and not the corpus.

## 5. Clearing re-run

A fix is not verified by reading the diff. Re-run the identical probe: same
route, same viewport, same theme, same seed, same injected failure. Record it as
`clearedBy` on the finding, keep the before-artifact, and never overwrite it
with the after.

Three outcomes worth naming:

- The probe now passes: the finding is `applied` and cleared.
- The probe still fails: the fix did not work. Report it as applied-unverified
  and say so; do not report the fix and stay silent about the re-run.
- The probe passes but a different probe on the same route now fails: the fix
  caused a regression, which is a new finding, not a footnote on the old one.

## 6. Report

Each finding carries a `verification` block; the run carries a `session` block.
Keep the finding object's existing schema and add only this delta:

```json
{
  "session": { "baseUrl": "...", "buildMode": "production", "driver": "playwright",
               "routes": ["/checkout"], "viewports": [360, 1280], "themes": ["light", "dark"] },
  "findings": [
    { "rule": "interaction-target-size", "status": "fail",
      "verification": { "outcome": "reproduced", "probe": "target-size",
        "observed": "28x28px at 360px width, touch emulation on",
        "evidence": ["artifacts/targets-checkout-360.json", "artifacts/targets-checkout-360.png"],
        "clearedBy": null } }
  ],
  "skipped": [ { "probe": "web-vitals", "reason": "dev build only; no production build available" } ]
}
```

Where this skill runs standalone, render the report without a `SHIP VERDICT`
line: the verdict is a property of a tiered audit, and printing one from probe
results alone invents a tier assignment nobody made.

## Honesty rules

- **A skipped probe is not a passed probe.** Report every probe that did not
  run, with the reason (no route, auth required, driver lacks interception, app
  would not build). A report that silently omits them reads as coverage it does
  not have.
- **A screenshot is evidence, not a verdict.** Probes decide on measurements.
  Inspect captures before handing them off; visual observations complement
  measured results without turning a screenshot into proof of flow correctness.
- **Do not widen into a redesign.** This skill reports what it measured. A
  finding that needs a new type scale names the mode to run next.
- **The app is the subject, not the harness.** A failure caused by the probe
  itself (a selector that never resolved, a route interception that swallowed
  the wrong request) is a harness bug. Fix the probe and re-run; never report it
  as a defect in the app.
- **Numbers carry their units and their conditions.** `44x44px at 360px width
  with touch emulation on` is a measurement. `too small` is the inference this
  skill exists to replace.

## Gotchas

The ones that cut across probes; each playbook lists its own false positives.

- `page.emulateMedia({ colorScheme: 'dark' })` does nothing for an app that
  themes with a `class="dark"` or `data-theme` attribute, which is most Tailwind
  apps. The probe reports a clean dark pass while never having left light mode.
  Drive the app's own toggle, and assert the attribute landed before capturing.
- Running perf or layout-shift probes against `next dev` measures on-demand
  compilation. The first navigation to a route can spend seconds in the
  bundler, which lands in LCP and dwarfs anything real.
- Animations that never settle keep a screenshot probe waiting until timeout.
  Set `prefers-reduced-motion: reduce` for captures, then run motion-sensitive
  checks in a separate pass with it off, because reduced motion is also a code
  path that can be broken.
- A fresh browser context per route, or cookies and service workers leak state
  between probes and make the second route's result depend on the first.

## Related skills

- `accessibility-compliance-audit`: the source-side WCAG audit whose findings
  this skill reproduces at runtime.
- `design-to-code` and `frontend-ui-engineering`: build and restyle UI; this
  skill measures what they shipped.
- Playwright test authoring: durable suites belong in the repo's test directory,
  not here. These probes are one-off evidence, not regression tests.

Maintenance only: `evals/evals.json` holds the behavioural scenarios for anyone
changing this skill. It never loads during a verification run.
