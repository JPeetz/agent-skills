# Changelog — Agent Evaluation Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-11-14

### Added
- Initial release by Skill Foundry.
- Five-phase evaluation workflow: define quality dimensions → build the dataset →
  choose and calibrate evaluators → run and report honestly → gate changes in CI.
- Dimension → metric → evaluator → gate-style matrix covering correctness,
  groundedness, task success, tool use, safety, instruction adherence,
  helpfulness, and cost/latency.
- Dataset guidance: four sourcing channels (production traces, hand-authored edge
  cases, business rules, synthetic fill), size-by-decision table (smoke 20–30 →
  benchmark 500+), JSONL schema with slice/difficulty/source metadata, holdout
  split, deduplication, and leakage checks.
- Evaluator ladder (rung 1 deterministic → rung 7 human) with a stop-at-first-rung
  rule, binary rubric templates, and judge hygiene: different model family,
  `temperature=0`, pinned versions, structured `{pass, score, reason}` output,
  candidate-output-as-untrusted-input, one dimension per call, order-swapped
  pairwise judging.
- Judge calibration thresholds: agreement ≥ 0.80, Cohen's κ ≥ 0.60, false-pass
  ≤ 10%, swap consistency ≥ 0.80, repeat consistency ≥ 0.90.
- Statistical honesty rules: Wilson 95% interval half-width table (n=20 → ±13.7
  pts, n=500 → ±2.6 pts), n ≥ 3 repetitions for comparisons, per-slice reporting,
  and hash-stamped run artifacts.
- CI gate model G1–G4 (absolute floors, non-inferiority with a statistically
  derived tolerance, per-slice regression limits, cost/latency budgets) plus
  committed baselines, online canaries, and a rollback path via version tags.
- Three worked examples: a promptfoo gate for a RAG support assistant, a DeepEval
  trajectory suite for a tool-using ops agent, and a model-upgrade decision
  combining lm-evaluation-harness screening with the in-house suite.
- Anti-patterns section (15 entries) covering vibes-based evaluation, uncalibrated
  judges, tuning on the whole dataset, per-item judge assertions in CI, unpinned
  judge models, and editing dataset items to make CI pass.
- Verification checklist for auditing an existing eval setup.
- `scripts/eval_gate.py` — applies G1–G4 to a run against a baseline, prints
  per-slice rates with Wilson intervals, exits non-zero on failure, and ships a
  `--selftest` that proves the gate catches a 30-point regression.
- `references/evaluation-metrics.md` — dimension/metric matrix and RAG and agent
  metric definitions.
- `references/judge-design.md` — rubric templates, calibration procedure, and bias
  controls.
- `references/tooling.md` — promptfoo, DeepEval, LangSmith, Inspect, and lm-eval
  commands with a selection matrix.
- 8 eval scenarios (5 trigger, 3 near-miss) including explicit boundaries with
  `test-driven-development`, `llm-observability`, and `agentic-eval`.
