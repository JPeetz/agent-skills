---
name: llm-observability
description: Use this skill when instrumenting, tracing, evaluating, or monitoring LLM and agent applications — capturing prompts and tool calls as traces, tracking token cost and latency, running LLM-as-judge evaluations, building quality dashboards and alerts, or gating model/prompt changes with regression tests. Implements OpenTelemetry GenAI conventions with Langfuse, Phoenix, LangSmith, Opik, or Weave backends.
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
domain: DevOps/LLM Observability
version: 1.0.0
created: 2026-11-14
license: MIT
tags:
  - llm-observability
  - opentelemetry-genai
  - llm-tracing
  - llm-evaluation
  - llm-as-judge
  - token-cost-tracking
  - langfuse
  - langsmith
  - arize-phoenix
  - agent-observability
  - prompt-regression-testing
  - quality-gates
triggers:
  - instrument LLM calls
  - trace LLM application
  - LLM observability
  - token cost tracking
  - LLM-as-judge evaluation
  - eval dataset
  - prompt regression test
  - hallucination monitoring
  - Langfuse setup
  - LangSmith tracing
  - Arize Phoenix
  - OpenTelemetry GenAI
  - gen_ai semantic conventions
  - agent tracing
  - quality gate for prompts
near_miss_negatives:
  - general application monitoring without LLM calls
  - fixing a model accuracy bug in training code
  - prompt engineering without measurement intent
  - deploying a vector database
seo:
  primary: llm observability agent skill
  clusters:
    - opentelemetry-genai-instrumentation
    - llm-evaluation-and-quality-gates
    - llm-cost-and-token-tracking
    - agent-trace-monitoring
---

# LLM Observability

Production-grade observability for generative AI systems: tracing, evaluation, monitoring, cost attribution, and quality gates. LLM applications fail silently — an HTTP 200 can carry a confident hallucination, and the same request can cost $0.004 or $0.42 depending on routing. Classic APM (RED metrics, error rates) cannot see any of that.

## When to Use This Skill

Invoke when the user asks to:

- **Trace** an LLM app, agent, or RAG pipeline — see the exact prompt, response, tool calls, retrieval steps, tokens, and latency per request
- **Instrument with OpenTelemetry** using GenAI semantic conventions, or export LLM spans to an existing OTLP backend
- **Pick a platform** (Langfuse, Phoenix, LangSmith, Opik, Weave, or plain OTLP → Tempo/Datadog/Grafana)
- **Evaluate quality** — build datasets, run LLM-as-judge or code evaluators, calibrate judges, score production traffic
- **Track cost** — attribute spend per model, tenant, feature, and request; alert on budget burn
- **Set up dashboards and alerts** for latency, error rate, token usage, judge scores, refusal/hallucination rate
- **Gate changes** — run prompt/model regression tests in CI and block deploys that regress

## Boundary With `observability-engineering`

`observability-engineering` covers host/service telemetry: HTTP spans, SLOs, Prometheus, Grafana, logs, incident response. This skill covers the **semantic layer those tools cannot express** — prompt and completion content, token economics, judge scores, and dataset-based regression. Use both when an LLM service is part of a larger system: service SLOs live in `observability-engineering`, model quality and cost live here. Traces should nest — an HTTP span from the parent skill becomes the parent of your `gen_ai.client.inference` spans.

## Core Concepts

| Concept | Meaning | Practical consequence |
|---|---|---|
| **Trace** | One end-to-end request (user turn → answer) | One trace per user request, not per process. Carry `session.id` for multi-turn |
| **Span / observation** | A timed step: LLM call, retrieval, tool exec, guardrail | Nest per step. One giant span makes latency attribution impossible |
| **Generation** | Span subtype carrying model, tokens, cost | Only generations/embeddings carry usage; other spans do not |
| **Dataset** | Versioned set of inputs + expected outputs | The unit of regression testing. Lives in the platform, not a spreadsheet |
| **Evaluator / score** | Function or judge producing a number/label on a trace or dataset item | Two classes: code (deterministic) and model-graded (probabilistic) |
| **Prompt version** | Named, immutable prompt revision referenced by traces | Without it, "quality dropped" is unanswerable |
| **Cost** | `usage × price` per token class (input, output, cache read/write, reasoning) | Ingest provider-reported usage; infer only as fallback |
| **Online eval** | Scoring live production traces | Trend detection and drift alarms |
| **Offline eval** | Scoring a dataset before deploy | The only defensible merge gate |

## The Five-Phase Workflow

### Phase 1 — Choose the Backend

Ask three questions first: (1) may prompt/completion data leave our infrastructure? (2) is the team already standardised on an LLM framework? (3) what is monthly call volume and retention need?

| Backend | Best when | Trade-offs |
|---|---|---|
| **Langfuse** | Self-hosting required, framework-agnostic, MIT core | Less polished dataset/prompt UX than LangSmith; storage sizing is on you |
| **Arize Phoenix** | RAG/retrieval evaluation depth, drift analysis, local notebook work | ELv2 licence (not OSI); UI less productised |
| **LangSmith** | All-in on LangChain/LangGraph, tight prompt→dataset→eval loop | Proprietary, no self-host, cost scales with events |
| **Opik (Comet)** | Open-source, agent trajectory evals, guardrails in one tool | Smaller ecosystem than Langfuse |
| **Weave (W&B)** | Team already on W&B for ML tracking | Best value inside W&B, weaker standalone |
| **Plain OTLP** (Tempo/Jaeger/Datadog/Grafana) | One pane of glass, strict EU data rules, existing platform team | No datasets, judges, or prompt versioning — you build or bolt on evals |

Default recommendation: **Langfuse self-hosted** for regulated/framework-agnostic teams, **Phoenix** when retrieval quality is the core problem, **LangSmith** when the stack is LangGraph.

Whatever you choose, instrument with **OpenTelemetry first**. A vendor SDK in application code is a one-way door; OTLP spans can be re-pointed at a different backend in an afternoon.

### Phase 2 — Instrument the LLM Calls

**Step 2.1 — Turn on auto-instrumentation, then add manual spans only where it fails.**

```bash
# Python: model-client instrumentation (emits gen_ai.* spans)
pip install opentelemetry-sdk opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-openai
# Frameworks: LangChain/LlamaIndex have equivalent packages; OpenLLMetry and
# OpenLIT cover Java/Go and extra frameworks.
```

```python
# instrumentation.py — import this BEFORE any LLM client import
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))  # reads OTEL_EXPORTER_OTLP_* env
trace.set_tracer_provider(provider)
OpenAIInstrumentor().instrument()
```

Never let the exporter block a response: `BatchSpanProcessor` with a bounded queue and a hard timeout. If the backend is down, drop spans — do not add latency to the user path.

**Step 2.2 — Emit the required `gen_ai.*` attributes** (OTel GenAI semantic conventions are **Development** status — pin your instrumentation library version and re-check names on upgrade):

| Attribute | Notes |
|---|---|
| `gen_ai.operation.name` | `chat`, `text_completion`, `embeddings`, `retrieval`, `execute_tool`, `invoke_agent` |
| `gen_ai.provider.name` | `openai`, `anthropic`, `gcp.vertex_ai`, `aws.bedrock`, `azure.ai.openai` |
| `gen_ai.request.model` / `gen_ai.response.model` | Requested vs actually served (aliases move) — record both |
| `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` | Required for cost; add `cache_read`, `cache_write`, `reasoning` buckets when present |
| `gen_ai.response.finish_reasons` | Detect truncation and refusals — a `length` finish is a silent quality failure |
| `gen_ai.conversation.id` | Multi-turn session correlation |
| `gen_ai.prompt.name` / `gen_ai.prompt.version` | Ties a trace back to an exact prompt revision |
| `gen_ai.input.messages` / `gen_ai.output.messages` / `gen_ai.system_instructions` | Content. Opt-in only; can be sensitive and large |
| `gen_ai.retrieval.documents`, `gen_ai.retrieval.query.text` | Opt-in retrieval detail |
| `error.type` | Low-cardinality failure class (`timeout`, `429`, `invalid_request`) |

Span name convention: `{gen_ai.operation.name} {gen_ai.request.model}` → `chat gpt-4o`. Span kind `CLIENT`.

**Step 2.3 — Wrap the application step that auto-instrumentation cannot see.** A RAG pipeline needs a root span, a retrieval span, and a generation child.

```python
from opentelemetry import trace
tracer = trace.get_tracer("support-agent")

def answer(question: str, user_id: str):
    with tracer.start_as_current_span("handle-support-question") as root:
        root.set_attribute("app.user.tier", "pro")          # low cardinality OK
        root.set_attribute("app.feature", "billing_help")
        docs = retrieve(question)                          # its own gen_ai.retrieval span
        with tracer.start_as_current_span("chat gpt-4o") as s:
            s.set_attribute("gen_ai.operation.name", "chat")
            s.set_attribute("gen_ai.provider.name", "openai")
            s.set_attribute("gen_ai.request.model", "gpt-4o")
            reply = call_model(question, docs)
            s.set_attribute("gen_ai.usage.input_tokens", reply.usage.input_tokens)
            s.set_attribute("gen_ai.usage.output_tokens", reply.usage.output_tokens)
        root.set_attribute("app.outcome", "answered")
        return reply.text
```

**Step 2.4 — Propagate trace-level attributes to every span.** Backends aggregate on span attributes, so `user.id`, `session.id`, `prompt.version`, `release`, and `tags` must be on all spans in the trace, not just the root. In OTel use baggage:

```python
from opentelemetry import baggage, context
ctx = context.get_current()
for k, v in {"user.id": user_id, "session.id": sid, "deployment.environment": "prod"}.items():
    ctx = baggage.set_baggage(k, v, context=ctx)
```

Add a `SpanProcessor` that copies baggage onto every `on_start` span, or set them with Langfuse's `propagate_attributes(user_id=..., session_id=...)` helper.

**Step 2.5 — Send through a Collector, not directly from the app.** The Collector is where you redact, sample, and fan out to two backends during migration.

```yaml
# otel-collector.yaml
receivers:
  otlp:
    protocols: { http: { endpoint: 0.0.0.0:4318 } }
processors:
  memory_limiter: { check_interval: 1s, limit_mib: 400 }
  attributes/drop_content:            # content stays out of the observability store
    actions:
      - { key: gen_ai.input.messages, action: delete }
      - { key: gen_ai.output.messages, action: delete }
      - { key: gen_ai.system_instructions, action: delete }
  transform/cost:                     # derive a per-span cost attribute from usage
    trace_statements:
      - context: span
        statements:
          - set(attributes["llm.cost.usd"], attributes["gen_ai.usage.input_tokens"] * 0.0000025)
            where attributes["gen_ai.request.model"] == "gpt-4o"
  tail_sampling:
    policies:
      - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow,   type: latency,     latency: { threshold_ms: 8000 } }
      - { name: sample, type: probabilistic, probabilistic: { sampling_percentage: 10 } }
  batch: { timeout: 5s }
exporters:
  otlphttp/langfuse:
    endpoint: https://cloud.langfuse.com/api/public/otel
    headers:
      Authorization: "Basic ${LANGFUSE_AUTH_B64}"
      x-langfuse-ingestion-version: "4"   # real-time v4 ingestion
service:
  pipelines:
    traces: { receivers: [otlp], processors: [memory_limiter, attributes/drop_content, transform/cost, tail_sampling, batch], exporters: [otlphttp/langfuse] }
```

Keep **token metrics unsampled** even when traces are sampled, or cost dashboards become fiction. `gen_ai.client.inference.duration` (histogram, seconds) and the token counters are the two instruments to get right.

### Phase 3 — Evaluate

**Step 3.1 — Build the dataset before you need it.** 30–100 items is enough to start: real support questions, edge cases from production traces, adversarial/refusal cases, and one item per business rule. Each item: `input`, `expected_output` (or `context` + `expected_facts`), and `metadata` (difficulty, source, tenant). Version it in the platform and export to git as JSONL.

**Step 3.2 — Pick the cheapest evaluator that can catch the failure.**

| Failure class | Evaluator | Cost |
|---|---|---|
| Format/schema violations | Code assertion (`json.loads`, schema check) | ~0 |
| Missing citation / wrong tool used | Code assertion on trace structure | ~0 |
| Factual grounding (RAG) | Faithfulness / context-recall judge over retrieved docs | 1 judge call |
| Answer relevance | Answer-relevance judge | 1 judge call |
| Tone/policy compliance | Rubric judge with explicit pass/fail criteria | 1 judge call |
| Toxicity / PII leakage | Classifier or regex + judge | low |
| Latency/cost budget | Code assertion on span metrics | ~0 |

Deterministic checks first — they are cheap, stable, and catch most production incidents. A judge is for what code cannot express.

**Step 3.3 — Calibrate judges or do not trust them.** Label 50 traces by hand, run the judge, and require ≥0.8 agreement (Cohen's kappa where labels are categorical) before the judge gates anything. Pin `temperature=0`, pin the judge model version, use a different model family from the one under test (self-preference bias inflates scores), and require a structured verdict (`{score, reason}`) so failures are debuggable.

**Step 3.4 — Score production traffic (online eval).** Run judges on a sample — 5–10% plus 100% of thumbs-down and error traces. Write scores back onto the trace so they appear next to latency and cost. Collect user feedback (`thumbs`, ratings, corrections) as its own score source; it is the only ground truth you get for free.

**Step 3.5 — Close the loop.** Failing production traces become dataset items; dataset items drive experiments; winning experiments become prompt versions; prompt versions are what production traces reference. If that loop is broken anywhere, observability is just expensive logging.

### Phase 4 — Dashboards and Alerts

Six panels, one per decision:

1. **Volume** — requests/hour by `app.feature`, split by model
2. **Quality** — judge score p50 over time, by `prompt.version`; user thumbs-down rate
3. **Cost** — USD/hour, USD per 1k requests, split by model and tenant; cache-hit share
4. **Latency** — p50/p95/p99 of `gen_ai.client.inference.duration`, plus time-to-first-chunk for streaming
5. **Reliability** — error rate by `error.type`, plus `finish_reasons=length` rate (truncation) and refusal rate
6. **Tokens** — tokens/request distribution; long-tail requests above 4× median

Alert on **rates and deltas, not absolutes**, with a stated action for each:

| Alert | Condition | Action |
|---|---|---|
| Error spike | `error.type` rate > 5% for 10 min | Check provider status, then fallback model |
| Cost burn | hourly spend > 2× 7-day same-hour baseline | Check routing/retry loop; page owner if > 3× |
| Latency | p95 > 2× 7-day baseline for 15 min | Inspect slow traces; check provider region |
| Quality drop | judge score p50 down > 10% vs 7-day baseline, n ≥ 100 | Compare by `prompt.version` — roll back if a version correlates |
| Truncation | `finish_reasons=length` > 2% | Raise max_tokens or shorten prompt |
| Refusal spike | refusal rate > 3× baseline | Check prompt/safety-filter change |

Every alert needs an owner, a runbook link, and a "known false positive" note. Alert fatigue kills LLM observability faster than missing data.

### Phase 5 — Regression Gates in CI

**Step 5.1 — Freeze a golden dataset** (≥30 items) in `evals/golden.jsonl`, committed to the repo.

**Step 5.2 — Run the app against it and score it** in a test that fails on regression:

```python
# tests/test_quality_gate.py
import json, statistics
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval

FAITHFULNESS = GEval(name="Faithfulness",
                     criteria="Answer must be supported only by the provided context.",
                     evaluation_params=[...], threshold=0.7)

def test_golden_set():
    for row in map(json.loads, open("evals/golden.jsonl")):
        out = run_app(row["input"])                      # your pipeline
        assert_test(LLMTestCase(input=row["input"],
                                actual_output=out.text,
                                retrieval_context=out.contexts),
                    [FAITHFULNESS])
```

**Step 5.3 — Gate on aggregate, not per-item, for judge metrics.** A single flaky judge verdict must not fail a build; a 5-point mean drop must. Assert `mean(score) >= baseline - tolerance` and `pass_rate >= 0.9`.

**Step 5.4 — Compare to the deployed baseline.** Store the last accepted score set in the repo (`evals/baseline.json`); a PR updates it only when it improves or holds. Run experiments in the platform (Langfuse experiment CI action, LangSmith dataset comparison, Phoenix experiments) so reviewers see item-level diffs.

**Step 5.5 — Gate the prompt, not just the code.** Prompt text is code. A prompt change without an experiment run is an unreviewed production change.

## Worked Examples

### Example 1 — Quick start: Langfuse self-hosted, first trace in 10 minutes

```yaml
# docker-compose.yml (minimal Langfuse v3/v4 stack)
services:
  langfuse-web:
    image: langfuse/langfuse:3
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/langfuse
      CLICKHOUSE_URL: http://clickhouse:8123
      REDIS_HOST: redis
      NEXTAUTH_SECRET: change-me
      SALT: change-me
      NEXTAUTH_URL: http://localhost:3000
    depends_on: [db, clickhouse, redis]
  db:         { image: postgres:16, environment: { POSTGRES_PASSWORD: postgres } }
  clickhouse: { image: clickhouse/clickhouse-server:24, environment: { CLICKHOUSE_DB: langfuse } }
  redis:      { image: redis:7 }
```

Create a project in the UI → copy `pk-lf-…` / `sk-lf-…`, then:

```python
import os
os.environ["LANGFUSE_HOST"] = "http://localhost:3000"
from langfuse import get_client, observe
langfuse = get_client()

@observe(as_type="generation", name="chat gpt-4o-mini")
def ask(q: str) -> str:
    r = client.chat.completions.create(model="gpt-4o-mini",
                                       messages=[{"role": "user", "content": q}])
    langfuse.update_current_generation(
        model="gpt-4o-mini",
        usage_details={"input": r.usage.prompt_tokens, "output": r.usage.completion_tokens},
        output=r.choices[0].message.content)
    return r.choices[0].message.content

ask("Why did my invoice change?")
langfuse.flush()      # required in scripts/lambdas before exit
```

Expected: one trace in the UI with prompt, completion, token counts, latency, and inferred USD cost. **Verify** the cost row is non-zero — a zero means the model name did not match a price definition; add a custom model definition. The SDK helper names change between Langfuse majors (`@observe`, `update_current_generation`, `start_as_current_observation`); pin the package version and check the trace shape, which is stable.

### Example 2 — Production: OTel-native, multi-service, cost-aware

Requirement: agent service (Python) + retrieval service (Node) + existing Datadog APM; prompts may not be stored; finance needs per-tenant cost.

1. Both services emit OTLP/HTTP to one Collector; the Collector fans out to Langfuse (quality/debug) and Datadog (SLOs), dropping `gen_ai.input.messages`/`gen_ai.output.messages` on the Datadog route only.
2. Retrieval service sets `gen_ai.operation.name=retrieval`, `gen_ai.data_source.id`, `gen_ai.retrieval.top_k`, and a document count — no document text.
3. Tenant attribution: `tenant.id` in baggage, copied onto every span; a `transform` statement derives `llm.cost.usd` from usage attributes using contract prices, including separate rates for cache-read tokens.
4. W3C `traceparent` is injected into the internal HTTP call between services so the retrieval span is a **child** of the agent root span — one trace, two services.
5. Sampling: 100% of errors and >8s traces retained; 10% of the rest. Token counters are exported as metrics on a separate unsampled pipeline.
6. Finance queries `sum(llm.cost.usd) by tenant.id` weekly; the per-tenant alert fires at 80% of plan budget.

Common failure here: two independent trace roots because the HTTP client was not instrumented. Verify with a trace that shows both `service.name` values under one trace ID.

### Example 3 — Eval-driven development: ship a prompt change safely

Task: improve a refund-policy assistant without regressing refusal correctness.

1. **Capture** 60 production traces spanning 3 weeks; hand-label 40 as good/bad.
2. **Dataset**: 40 items (`input`, `expected_facts`, `must_refuse: bool`), exported to `evals/refund.jsonl`, committed.
3. **Evaluators**: code check for `must_refuse` compliance; `Faithfulness` judge for grounded answers; `Tone` rubric judge. Judge calibrated to 0.85 agreement on the 40 hand labels before use.
4. **Baseline**: run current prompt → mean faithfulness 0.81, refusal compliance 0.95, cost/request $0.0031. Save as `evals/baseline.json`.
5. **Iterate**: three prompt variants tested as separate experiments; variant B reaches 0.88 faithfulness, 1.00 refusal compliance, $0.0029.
6. **Gate**: CI job runs the golden set on every PR; fails if faithfulness mean < baseline − 0.03 or refusal compliance < 0.95. Variant B's PR passes and updates `baseline.json`.
7. **Deploy** with `prompt.version=v2.3` on every trace; watch the quality panel for 24h against the v2.2 cohort.
8. **Rollback rule**: if v2.3's judge p50 drops >10% with n ≥ 100 or thumbs-down doubles, revert the version tag — no code deploy needed.

## Anti-Patterns

- **Tracing only the HTTP layer.** You get latency and status codes and learn nothing about quality. The prompt/response/tool-call spans are the point.
- **One mega-span per request.** No per-step attribution; a 9-second request with a 0.2s LLM call and an 8.5s retry looks identical to a slow model.
- **Head sampling at 1% then reporting cost.** Sampled traces cannot be extrapolated to spend. Sample traces, never token metrics.
- **Storing raw prompts and completions by default.** They contain PII, secrets, and customer data with different retention rules. Redact at the Collector; opt in per environment.
- **High-cardinality attributes as metric labels.** `user.id`, `request.id`, `session.id` on metrics will melt your TSDB. Keep them on spans; use `user.tier` on metrics.
- **Unversioned prompts.** Without `gen_ai.prompt.version` / a prompt registry, a quality drop is unattributable and rollback is a code deploy.
- **Judging with the model under test.** Self-preference bias; use a different family and `temperature=0`.
- **Uncalibrated judges as merge gates.** A judge that agrees with humans 60% of the time is a random number generator with a UI.
- **Asserting per-item judge scores in CI.** Flaky red builds teach the team to ignore the gate. Gate on aggregate deltas with tolerances.
- **Evaluating only the happy path.** Refusals, prompt injection, empty retrievals, and 429s are where incidents live.
- **Cost inferred from character counts.** Ingest provider-reported usage; tokenizers differ per model and reasoning/cache tokens break naive math.
- **Dashboards with no owner or action.** If nobody knows what to do when a panel is red, delete the panel.
- **Exporting synchronously or unbounded.** A slow observability backend must never become your outage. Batch, bound the queue, drop on overflow.
- **Treating the platform as the source of truth for datasets.** Export datasets and baselines to git, or your regression suite disappears with the vendor.
- **Logging eval scores with no trace link.** A score that cannot be opened next to its trace cannot be debugged.

## Verification Checklist

Instrumentation
- [ ] A real request produces exactly one trace with the expected span tree (root → retrieval → generation → tool)
- [ ] `gen_ai.request.model`, `gen_ai.provider.name`, `gen_ai.operation.name` present on every inference span
- [ ] Input and output token counts match the provider response for a spot-checked call
- [ ] Cost per request is non-zero and plausible for the model's published price
- [ ] `session.id` groups a multi-turn conversation into one session view
- [ ] Cross-service calls share one trace ID (W3C `traceparent` propagated)
- [ ] No prompt/PII content in the observability store unless explicitly opted in and retention-approved

Evaluation
- [ ] Dataset exists, is versioned, committed as JSONL, and ≥30 items with edge cases
- [ ] At least one deterministic evaluator and one judge; judge calibrated ≥0.8 agreement on hand labels
- [ ] Judge model and prompt are pinned; verdicts include a reason
- [ ] Online scoring runs on a defined sample and writes scores back onto traces
- [ ] A failing production trace can be added to the dataset in under a minute

Operations
- [ ] Six dashboards panels exist with a named owner
- [ ] Every alert has a threshold, duration, owner, and runbook link
- [ ] Alerts fire on rate/delta, not raw absolute values
- [ ] Token metrics are exported without sampling
- [ ] Exporter failure degrades to dropped spans, not added latency (bounded queue verified)
- [ ] Cost is attributable per tenant/feature, and a budget alert exists

Quality gate
- [ ] CI runs the golden set on every prompt or model change and fails on regression
- [ ] Baseline scores are stored in the repo and updated only deliberately
- [ ] `prompt.version` appears on production traces and matches the deployed revision
- [ ] A rollback path exists that does not require a code deploy

## References

- `references/platform-selection.md` — detailed matrix, self-host sizing, migration paths
- `references/otel-genai-attributes.md` — attribute and metric reference, version drift notes
- `references/evaluation-playbook.md` — judge design, calibration protocol, dataset curation
- `scripts/langfuse-compose.sh` — bring up a local Langfuse stack and smoke-test ingestion
- `scripts/check_genai_attrs.py` — lint spans for missing required GenAI attributes
