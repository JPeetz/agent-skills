# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-16

### Added
- Initial release.
- `SKILL.md` — the month-end close workflow: three-phase calendar model
  (pre-close D-5→D-1, core close D+1→D+5, review D+6→D+8), day-by-day checklist
  with owners and evidence artifacts, bank reconciliation procedure with tiered
  matching rules and tolerances, accrual schedules with reversal and true-up
  discipline, prepaid amortization and deferred revenue roll-forward, trial
  balance review (out-of-balance detection, unusual movements, flux vs prior
  period), budget-vs-actual variance analysis, journal entry anatomy and approval
  matrix, close efficiency metrics, workflow optimization levers, and a
  14-row anti-patterns table.
- `scripts/close_checklist.py` — stdlib-only checklist generator. Scopes the
  task library to the entity's active modules, computes status against the
  current close day (overdue / due today / upcoming / done), totals estimated
  hours by owner, warns on uncovered modules and unassigned roles, and emits
  markdown or JSON. Validates entity, period format, module ids, materiality,
  team values and day tokens; exits non-zero on bad input. 34 built-in
  self-test checks via `--self-test`.
- `references/close-framework.md` — the phase model with exit criteria per
  phase, the full task inventory, role and segregation-of-duties matrix, the
  close-calendar contract and its failure modes, acceleration strategies in
  return-on-effort order, soft-close vs hard-close guidance, and interactions
  with adjacent processes.
- `evals/evals.json` — four positive and two negative evaluation cases covering
  scoped checklist generation, a bank rec with an unexplained residual, accrual
  and reversal discipline, close-efficiency diagnosis, and two near-miss
  routing cases (revenue-recognition policy, vendor payment dispute).
- `LICENSE` (MIT), `CHANGELOG.md`.

### Notes
- Extends the `finance-ops` category alongside `saas-metrics-coach`; the two are
  complementary (recognised revenue and reported metrics vs. the close
  procedure that produces them).
- Materiality, tolerances and day offsets are parameters, not defaults to be
  silently assumed — the script warns when materiality is unset.
- The skill states accounting procedure, not accounting policy. Policy decisions
  (revenue recognition treatment, capitalisation thresholds, restatement calls)
  route to technical accounting review.
