# Changelog

## [1.0.0] - 2026-11-14

### Added
- Initial release: agentic-eval skill under the new `ai-agent-engineering` category
- Eval pyramid (unit → component → integration → system → human) with guidance on testing at the lowest level that can catch the failure
- Eval-driven development loop: real cases, written criteria, saved baseline, one variable per run, per-case diffs, human reads, frozen regressions
- Rubric design: independent dimensions, anchored score levels, small scales, evidence-quoting prompts, chain-of-thought before the label
- Evaluator-optimizer architecture with bounded iterations, fresh-context re-scoring, best-artifact retention, and cost-ratio guidance
- Self-critique loops covering what they reliably catch, what they miss (confident factual errors, shared blind spots, sycophantic revision), and role separation
- Pairwise ranking with position-bias controls: both-order agreement, randomized order, blinded labels, legitimate ties; win rate, Bradley–Terry, Elo, and sample-size caveats
- Calibration: human-labeled sets, human–human ceiling, Cohen's κ / weighted κ / Spearman ρ, disagreement inspection, judge-swap invalidation
- Judge bias probes for verbosity, self-preference, position, format, and confidence/authority bias
- Overfitting defenses: holdout splits, production refresh, trajectory metrics, case rotation
- Eval harness setup: JSONL dataset schema, pinned configurations, caching, failure isolation, deterministic gate before the judge, per-case reporting, CI tiering with regression gates
- Anti-patterns table, red flags, and a pre-trust verification checklist
- Eval cases: four positive triggers across rubric, harness, pairwise bias, and evaluator-optimizer; two near-miss negatives
- `references/sources.md` with upstream skill, primary papers, and vendor documentation
