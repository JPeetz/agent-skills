# CHANGELOG — ui-verification

## v0.1.0 — 2026-11-14

### Added
- Initial release of the UI Verification skill.
- IS / IS NOT contract: owns the browser session; does not read source to find
  defects, build UI, author durable test suites, or issue ship verdicts.
- Nine-probe catalogue with inline playbooks (no separate probe files, since
  this repo ships no browser test infrastructure):
  - `axe-scan` — axe-core violations per route and theme, computed contrast.
  - `target-size` — bounding box and effective hit area for every visible
    interactive element, including pseudo-element expansion.
  - `focus-walk` — scripted Tab traversal, focus-ring pixel delta, dialog trap
    and focus restoration.
  - `layout-shift` — attributed `layout-shift` entries with the data response
    held open.
  - `viewport-stress` — horizontal overflow and clipped text from 320px up,
    plus tripled-string passes.
  - `failure-injection` — 500, `[]`, malformed, and aborted responses, with
    retry call counting.
  - `theme-locale-matrix` — one route across viewport, theme, pseudo-locale,
    and direction.
  - `console-network` — console errors, page errors, failed requests, hydration
    mismatch warnings.
  - `web-vitals` — LCP with attributed element, CLS, INP on a scripted
    interaction.
- Six-step workflow: session, probe selection, execution, decision
  (`reproduced` / `not-reproduced` / `unknown`), clearing re-run with
  `clearedBy`, report.
- Feature-to-probe minimum sets for forms, lists, modals, dashboards, checkout.
- Honesty rules: skipped is not passed; screenshots are evidence not verdicts;
  the app is the subject, not the harness; numbers carry units and conditions.
- Cross-probe gotchas: dark-mode emulation misses attribute theming, dev-mode
  perf numbers, unsettled animations, leaked browser state, late console
  listeners.
- `references/exploratory-test.md` — fresh-context exploratory pass against a
  test environment.
- `references/visual-review.md` — matched before/after screenshot comparison
  and suspicious-duplicate detection.
- Eval scenarios covering triggering, probe selection, and near-miss negatives.

### Why
Static UI audits infer what a user will see. Two classes of defect survive that
inference every time: the control that looks too small but has a pseudo-element
hit area, and the action that looks wired but goes nowhere. Both are one browser
measurement away from being settled. This skill supplies the measurement, the
evidence shape, and the honesty rules that keep a skipped probe from being read
as a pass.
