# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [0.1.0] — 2026-11-13

### Added
- Initial release, adapted from `alirezarezvani/claude-skills` (`commercial/skills/pricing-strategist`) and reworked to this repo's conventions.
- `SKILL.md` — five-step workflow: brief → model → willingness to pay → packaging → committee decision.
- `scripts/pricing_model_picker.py` — scores seat, usage, value-based, freemium and hybrid models 0–100 against a product brief; emits rationale, requirements and trade-offs per model. Stdlib only.
- `scripts/wtp_analyzer.py` — Van Westendorp Price Sensitivity Meter: cumulative curves, all four intersection points (OPP, IDP, PMC, PME), Range of Acceptable Prices, threshold-ordering data-quality check, and the optional Newton-Miller-Smith extension. Stdlib only.
- `scripts/packaging_designer.py` — cumulative Good/Better/Best assignment by segment affinity with a value-per-cost quantile fallback, relative price ladder indexes, and six anti-pattern detectors (feature dump, empty tier, decoy tier, no upgrade trigger, top-heavy, orphan feature, ladder gap). Stdlib only.
- `references/pricing_canon.md` — model selection heuristics, PSM mechanics and pitfalls, tier design rules, and a reading list.
- `evals/evals.json` — three evaluation scenarios covering model selection, the PSM range, and tier anti-patterns.

### Changed from source
- Frontmatter reduced to `name`, `description`, `version`, `author`, `license`, `platforms`, and repo-standard `metadata.hermes` tags. Removed source-only keys (`compatible_tools`, `tags` at top level).
- Description rewritten to lead with "Use this skill when" for trigger reliability.
- Scripts written from scratch as runnable stdlib implementations with `--output json|markdown`, input validation and non-zero exit codes on bad input; the source shipped them as references only.
- Added explicit "do not use for" routing table, anti-patterns section, and verification checklist.
- Added LICENSE, CHANGELOG and evals to match repo conventions.
