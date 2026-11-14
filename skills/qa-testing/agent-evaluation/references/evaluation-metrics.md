# Evaluation Metrics Reference

## Dimension → metric → evaluator

| Dimension | Metric | Evaluator | Score range | Typical gate |
|---|---|---|---|---|
| Correctness (closed) | exact match / normalized match | code | 0/1 | ≥ 0.95 |
| Correctness (open) | answer accuracy | judge vs reference | 0–1 | floor 0.85, non-inferior |
| Groundedness | faithfulness | RAG judge over context | 0–1 | floor 0.90 |
| Retrieval quality | contextual recall / precision | RAG judge with reference | 0–1 | diagnostic, not gate |
| Task success (agent) | completion rate | environment check or trajectory judge | 0–1 | floor 0.85 |
| Tool selection | tool correctness | trace compare vs expected tools | 0–1 | ≥ 0.95 |
| Tool arguments | argument correctness | judge over args + input | 0–1 | ≥ 0.90 |
| Efficiency | step efficiency / tool calls per task | count from trace | int | ≤ baseline × 1.25 |
| Safety | violation rate | classifier + judge | 0–1 | exactly 0 |
| Instruction adherence | schema/format pass rate | code | 0/1 | exactly 1.0 |
| Helpfulness | pairwise win rate vs baseline | pairwise judge | 0–1 | ≥ 0.50 |
| Tone/policy | rubric pass rate | rubric judge | 0–1 | floor 0.90 |
| Cost | USD per request/task | usage × price | float | ≤ budget |
| Latency | p50/p95 ms | timer on request | ms | ≤ budget |

## RAG metric definitions (DeepEval / Ragas vocabulary)

| Metric | Question it answers | Needs |
|---|---|---|
| **Answer relevancy** | Does the answer address the question asked? | input, actual_output |
| **Faithfulness** | Is every claim supported by retrieved context? | actual_output, retrieval_context |
| **Contextual precision** | Are the most relevant chunks ranked first? | input, retrieval_context, expected_output |
| **Contextual recall** | Did retrieval fetch everything needed? | input, retrieval_context, expected_output |
| **Hallucination** | Does output contradict supplied context? | actual_output, context |
| **Answer correctness** | Does output match the reference answer? | actual_output, expected_output |

Faithfulness and answer relevancy are gate material. Contextual precision/recall
are diagnostic: when faithfulness drops, they tell you whether the retriever or
the generator is at fault.

## Agent trajectory metrics

| Metric | Definition | Failure it catches |
|---|---|---|
| Task completion | End state satisfies the user's goal | Right text, no action taken |
| Tool correctness | Called tools ⊆ expected tools | Wrong tool, hallucinated tool |
| Argument correctness | Arguments match the values in the input | Refund for wrong order/amount |
| Step efficiency | Steps used vs minimum needed | Loops, redundant retries |
| Plan adherence | Actions consistent with stated plan | Silent scope drift |

Agents need at least task completion and one tool metric. Output-only scoring
marks an agent that issued three duplicate refunds as correct.

## Threshold guidance

1. **Derive floors from the current accepted system**, not from aspiration. Run
   the suite on the deployed version, take the mean, set the floor 2–3 points
   below it, then raise it as the system improves.
2. **Zero-tolerance only for binary policy facts** (PII leak, forbidden action,
   schema violation). Applying zero tolerance to a judge metric guarantees a
   flaky gate.
3. **Non-inferiority beats absolute improvement** for iteration: `new >= old -
   tolerance`. Absolute-only gates either block every change or get lowered
   until they mean nothing.
4. **Judge metrics need wider tolerances than code metrics** — 3–5 points
   versus 0–1 — because judge variance is real.
5. **Cost/latency budgets are ratios to baseline** (+10% cost, +20% p95) unless
   the product has a hard SLA, in which case use the SLA.

## Reporting template

```text
suite=v3 n=214  pass=0.882 CI95=(0.833,0.919)  baseline=0.897
  slice billing/refund      n=48  pass=0.833 CI95=(0.704,0.913)  Δ -0.062  <-- regressed
  slice account/security    n=31  pass=0.935 CI95=(0.793,0.982)  Δ +0.010
  slice general             n=135 pass=0.889 CI95=(0.825,0.933)  Δ -0.004
cost usd/req=0.0024 (+9.1%)  p95=3120ms (+4.0%)
GATE: FAIL (G3 billing/refund)
```

The delta and the interval, side by side, are what make the report honest. A
slice with `n=12` should be printed but excluded from gating.
