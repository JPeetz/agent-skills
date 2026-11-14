# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-14

### Added
- `SKILL.md` — five core workflows: RICE prioritization, customer interview synthesis, PRD authoring, OKR design, and decision frameworks. Each section ends in a decision artifact, not a template dump.
- `scripts/rice_scorer.py` — stdlib-only RICE calculator. Reads a JSON file or stdin, validates every input (impact must be one of the five canonical multipliers, confidence accepts 0–1 or 0–100, effort must be > 0, duplicate names rejected), and emits a ranked markdown table or JSON. Flags low-confidence items (`≤50%`, treated as research not build) and effort outliers (>3× median or median+5). The score is never silently altered by a flag — flags annotate, they do not reorder.
- `references/sources.md` — provenance for RICE, JTBD, Ulwick opportunity scoring, DACI, DARE, and OKR practice, plus a reading list and a note on which thresholds are heuristics.
- `evals/evals.json` — four positive scenarios (RICE ranking with an override, interview synthesis, PRD with a missing kill criterion, OKR output-vs-outcome test) and two negative scenarios (out-of-scope routing).
- `LICENSE` — MIT.

### Design notes
- RICE section enforces absolute reach and a single effort unit; both are the most common ways the score gets quietly gamed.
- Interview synthesis requires a participant count per theme and a counter-evidence section, so the output cannot drift into confirmation.
- PRD template mandates a named "won't have" list and kill criteria — the two sections whose absence causes scope creep.
- OKR section separates leading from lagging KRs and requires a baseline before a target, with output KRs explicitly banned.
- Decision frameworks are selected by the shape of the decision (many comparable candidates → RICE; one accountable human → DACI; 2–4 contested options → DARE; survey data → opportunity scoring).
