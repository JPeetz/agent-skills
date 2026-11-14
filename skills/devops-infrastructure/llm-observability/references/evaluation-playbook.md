# Evaluation Playbook — Judges, Datasets, and Gates

## Dataset curation

- **Start from production, not imagination.** 40 real traces beats 400 synthetic cases. Sort by cost, by latency, by thumbs-down, and by longest conversation; sample across all four.
- **Include the ugly cases:** empty retrieval, prompt injection attempt, off-topic question, ambiguous request, non-English input, very long input, request that must be refused.
- **One row per business rule.** If a policy says "never quote a refund timeline without an order id", there is a test case for it.
- **Schema:** `{"id", "input", "expected_output"|"expected_facts", "context", "must_refuse", "metadata": {"source", "difficulty", "tenant"}}`.
- **Version in git:** `evals/<feature>.jsonl`, plus `evals/baseline.json` with accepted aggregate scores. The platform copy is a working set; git is the contract.
- **Size:** 30 items to start, 100–300 once the product has real usage. Beyond 300, per-item judging gets expensive — sample stratified by failure class.

## Evaluator ladder (cheapest first)

1. **Schema/format assertion** — parse JSON, check required keys, check length bounds. Free, exact, catches format regressions.
2. **Structural trace assertions** — was a tool called? was retrieval non-empty? was the citation present? Free, uses the trace you already have.
3. **Reference-based string metrics** — exact match, normalized match, BLEU/ROUGE for constrained outputs. Free, weak for free text.
4. **Embedding similarity** vs expected answer — cheap, good for "same meaning", bad at catching contradictions.
5. **LLM-as-judge, rubric-based** — one call per item per criterion. Covers tone, grounding, policy compliance.
6. **Human review** — annotation queues on a sample. Expensive; the calibration source of truth.

If a cheaper rung catches the failure, do not climb. Most production "quality incidents" are format violations, empty retrievals, or refusals — all rung 1–2.

## Judge design rules

- **One criterion per judge.** "Is the answer good?" is unactionable. Use faithfulness, relevance, completeness, tone, policy-compliance separately.
- **Rubric with explicit pass/fail anchors**, not a 1–10 scale. Binary or 3-point (fail/partial/pass) has far better human agreement.
- **Structured output:** `{"verdict": "pass"|"fail", "score": 0.0-1.0, "reason": "...", "evidence": ["..."]}`. The reason is what makes failures debuggable.
- **Pin everything:** judge model version, prompt text, temperature 0, seed where supported.
- **Different family than the system under test.** A model grading its own output shows measurable self-preference bias.
- **Provide the context the judge needs** (retrieved docs, not just the question) — otherwise faithfulness judging is guesswork.
- **Cost-control:** judge 5–10% of traffic online plus 100% of error and negative-feedback traces; judge 100% of the golden set offline (cheap at n ≤ 300).

## Calibration protocol

1. Hand-label 50 items (binary pass/fail) from the same distribution.
2. Run the judge on the same 50.
3. Compute agreement; require **≥ 0.80** raw agreement and **Cohen's kappa ≥ 0.6** for categorical labels.
4. Inspect every disagreement. Usually the rubric is ambiguous or the judge lacks context — fix the rubric, not the labels.
5. Re-calibrate after any change to judge model, prompt, or rubric. Record the agreement number next to the judge version.
6. If you cannot reach 0.80, the criterion is not judgeable at this granularity. Rework it into something deterministic or accept a coarser label.

## Gate design

| Metric type | Gate on | Threshold form |
|---|---|---|
| Deterministic (format, refusal, tool use) | Per-item pass rate | `pass_rate >= 0.95`, hard fail |
| Judge score | Mean over dataset | `mean >= baseline - 0.03`, hard fail |
| Judge score | Distribution shift | p10 not below baseline p10 by > 0.1 |
| Cost | Mean cost/request | `<= baseline * 1.15`, warn then fail |
| Latency | p95 | `<= baseline * 1.2`, warn |

Rules that keep the gate alive:

- Never fail a build on a single judge verdict — LLM judges are stochastic.
- Run judge-based tests with `n ≥ 30` so the mean is meaningful.
- Retry once on provider error; never silently skip a failed judge call (that hides corruption).
- Baseline updates belong in the same PR as the improvement, with the score diff in the description.
- Keep a `--update-baseline` escape hatch, and require a second reviewer for it.

## Online evaluation

- Sample by hash of trace id so the same traffic mix is scored each run.
- Score every thumbs-down, every error, and every `finish_reasons=length`.
- Write scores back onto the trace — a score without a trace link cannot be debugged.
- Alert on the **delta vs 7-day baseline at equal n**, never on a single hour's absolute score.
- Review the lowest-scoring traces weekly and promote 2–3 into the golden dataset. That is the loop that keeps the dataset representative.

## Tooling notes

| Tool | Best use |
|---|---|
| Platform judges (Langfuse/Phoenix/LangSmith/Opik) | Online scoring, annotation queues, score analytics |
| DeepEval | Pytest-native offline evals, G-Eval rubrics, agent trajectory metrics |
| Ragas | RAG-specific metrics (faithfulness, context precision/recall, answer relevancy) |
| promptfoo | YAML-declared eval suites, multi-model comparison, CI-friendly |
| OpenAI Evals / Inspect | Research-grade eval harnesses, standardized benchmarks |
| Custom Python | Anything deterministic; keep it in the repo next to the prompt |

Pick one offline harness. Two harnesses means two baselines and no gate.
