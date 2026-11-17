# Changelog — presentation-prompt-pipeline

## v1.0.0 — 2026-11-17

- Initial release. Six staged prompts (blueprint → structure → story frame →
  visual direction → content → build), each with the artifact it produces and a
  checkable gate, plus copy-ready prompt templates for every stage.
- `scripts/deck_lint.py`: enforces title ≤6 words, ≤5 bullets, ≤10 words per
  bullet, speaker notes on every slide, ≤2 font families and ≤3 explicit text
  colours; exits 0 clean / 1 findings / 2 unreadable, with tunable ceilings.
  Verified against a compliant and a violating deck before release.
- Eight named failure modes, including the one-mega-prompt failure and
  decoration-before-storyline.
- `references/six-prompts-cheatsheet.md`: transcription of the source infographic
  (Cyberman AI, "How to build a presentation using AI: 6 powerful prompts").
- Deliberately scoped to planning and review: `.pptx` creation itself is plain
  `python-pptx`, and format conversion is out of scope.
