# Tooling Reference

## Selection matrix

| Tool | Best for | Datasets | Judges | CI story | Notes |
|---|---|---|---|---|---|
| **promptfoo** | Prompt/model comparison, red teaming, config-as-code | YAML/CSV/JSON inline or external | `llm-rubric`, `g-eval`, `factuality`, `select-best`, `model-graded-closedqa` | `promptfoo eval` exit code; GitHub Action | Node CLI, no server needed; strongest assertion vocabulary |
| **DeepEval** | Python test suites, RAG + agent trajectory metrics | `EvaluationDataset`, JSONL | 50+ built-in metrics, `GEval` custom criteria | `deepeval test run` under pytest | Pytest-native; cloud dashboard optional |
| **LangSmith** | Dataset/experiment management on LangChain stacks, annotation queues | Managed datasets, trace→dataset | LLM-as-judge, pairwise, code, human | SDK `evaluate()` + CI script | Proprietary SaaS; best trace→dataset loop |
| **Inspect** (UK AISI) | Agentic/security evals, sandboxed tool use, frontier benchmark replication | Custom datasets, 200+ prebuilt evals | Built-in scorers + model-graded | `inspect eval` + log files | Sandbox (Docker/K8s) for untrusted code; strong for agent trajectories |
| **lm-evaluation-harness** | Public academic benchmarks (MMLU, GSM8K, IFEval, HumanEval) | Fixed task definitions | Task-specific metrics | `lm_eval` CLI | Model capability screen, not product quality |
| **Ragas** | RAG-metric library only | Bring your own | Faithfulness, context precision/recall | Via pytest | Use when you want metrics without a runner |

Default stack for a small team: **promptfoo** for prompt-level comparison and
red teaming, **pytest + your own gate script** for the release gate, **DeepEval**
when RAG or trajectory metrics matter, **lm-eval** once per model change.
Whatever you pick, keep the dataset and baseline in git.

## promptfoo

```bash
npx promptfoo@latest init                      # scaffold promptfooconfig.yaml
npx promptfoo@latest validate config           # syntax + schema check
npx promptfoo@latest eval -o evals/runs/out.json --no-cache
npx promptfoo@latest eval --filter-failing evals/runs/out.json   # re-run only failures
npx promptfoo@latest eval --filter-sample 25 --filter-sample-seed 42
npx promptfoo@latest view                      # item-level browser UI
npx promptfoo@latest share                     # hosted result link (review only)
npx promptfoo@latest redteam run               # attack suite against the app
```

Config shape (abridged):

```yaml
prompts: [file://prompts/support_v3.txt]
providers:
  - id: openai:gpt-5-mini
    config: { temperature: 0 }
defaultTest:
  options:
    provider: openai:gpt-5.4        # judge
tests:
  - vars: { question: "..." }
    assert:
      - { type: is-json }
      - { type: contains-json, value: { required: [answer, citations] } }
      - { type: llm-rubric, value: file://evals/judges/policy.txt }
      - { type: factuality, value: "{{context}}" }
      - { type: select-best, value: "Which answer is better grounded?" }
      - { type: cost, threshold: 0.004 }
      - { type: latency, threshold: 4000 }
```

Assertion families: deterministic (`equals`, `contains`, `icontains`, `is-json`,
`contains-json`, `javascript`, `python`, `similar`, `levenshtein`), model-graded
(`llm-rubric`, `g-eval`, `factuality`, `answer-relevance`, `context-faithfulness`,
`select-best`, `model-graded-closedqa`), and operational (`cost`, `latency`).
`assert-set` groups assertions with its own pass `threshold` and `weight`.

Cost control: model-graded assertions can dominate spend. Run deterministic
checks in a pre-flight eval, or use `--filter-*` to grade only changed cases.

## DeepEval

```bash
pip install -U deepeval
deepeval login --api-key "$DEEPEVAL_API_KEY"    # only for the cloud dashboard
deepeval test run tests/test_ops_agent.py        # pytest-compatible runner
deepeval test run tests/ -n 8                    # parallel workers, version permitting
```

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.metrics import GEval, FaithfulnessMetric, AnswerRelevancyMetric

faithfulness = FaithfulnessMetric(threshold=0.8, model="gpt-5.4", include_reason=True)
test_case = LLMTestCase(
    input=q, actual_output=out, expected_output=ref, retrieval_context=chunks,
)
assert_test(test_case, [faithfulness, AnswerRelevancyMetric(threshold=0.7)])
```

Metric families: RAG (answer relevancy, faithfulness, contextual
precision/recall/relevancy), agent trajectory (task completion, tool
correctness, argument correctness, step efficiency, plan adherence), safety
(bias, toxicity, PII leakage, role violation), multi-turn (knowledge retention,
conversation completeness), custom (`GEval`, `DAG`, `JevEval`). All scores are
0–1 with a default `threshold` of 0.5 — set thresholds explicitly.

API drift is real: `evaluation_params` enums (`SingleTurnParams`,
`TurnParams`), test-case fields, and CLI flags have changed across majors. Pin
the version in `requirements.txt` and check `deepeval --help` on the installed
build instead of trusting a tutorial.

## LangSmith

```bash
pip install -U langsmith
export LANGSMITH_API_KEY=...
export LANGSMITH_TRACING=true
```

```python
from langsmith import Client, evaluate

client = Client()
ds = client.create_dataset("support-golden-v3")
client.create_examples(
    dataset_id=ds.id,
    examples=[{"inputs": {"question": q}, "outputs": {"answer": a}} for q, a in rows],
)

def target(inputs: dict) -> dict:
    return {"answer": run_app(inputs["question"])}

def policy_ok(run, example) -> dict:
    verdict = judge_policy(run.outputs["answer"])
    return {"key": "policy_pass", "score": float(verdict["pass"]), "comment": verdict["reason"]}

results = evaluate(
    target, data="support-golden-v3", evaluators=[policy_ok],
    experiment_prefix="support-v3", max_concurrency=8,
)
```

Use `aevaluate` for large async jobs, `evaluate_comparative` / pairwise
evaluators for A/B, and annotation queues for human labels. Cache/repetition
settings live in experiment configuration — set repetitions ≥ 3 before
comparing experiments.

## Inspect

```bash
pip install inspect-ai
inspect eval inspect_evals/gsm8k --model openai/gpt-5-mini
inspect eval my_task.py --model anthropic/claude-... --limit 50
inspect view                     # log viewer
```

Composable `dataset` + `solver` + `scorer` tasks; strong for agentic evals that
need a sandbox (Docker/K8s/Modal) and for running arbitrary external agents
(Claude Code, Codex CLI). Use Inspect when the eval itself is a program with
tools, not a single completion.

## lm-evaluation-harness

```bash
pip install lm-eval
lm-eval ls tasks
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-3.1-8B-Instruct,dtype=bfloat16 \
  --tasks mmlu,gsm8k,ifeval --num_fewshot 5 \
  --batch_size auto --output_path evals/runs/bench.jsonl
lm_eval --model vllm --model_args pretrained=<model>,tensor_parallel_size=1 \
  --tasks mmlu --batch_size auto
```

Code-executing tasks (HumanEval, MBPP) require `--confirm_run_unsafe_code`.
Keep `--num_fewshot` and task names identical across compared runs, or the
comparison is meaningless. Results are a capability screen: they justify
shortlisting a model, never adopting it for a product workload.
