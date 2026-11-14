# Platform Selection — LLM Observability Backends

Decision aid for Phase 1. Prices and licences change; verify before committing.

## Hard questions first

1. **May prompt/completion content leave your infrastructure?** If no (regulated, EU data residency, healthcare, legal), the answer is self-hosted or a plain OTLP pipeline into your own store. This single question eliminates most SaaS options.
2. **Does the team already live in a framework?** LangGraph → LangSmith's trace UI renders graph state natively; raw SDK/HTTP → framework-agnostic backends win.
3. **What is the monthly event volume?** Above ~2M traces/month, per-event SaaS pricing becomes the dominant cost; self-hosting ClickHouse is usually cheaper.
4. **Who consumes the output?** Platform team → Datadog/Grafana. AI engineers iterating on prompts → a purpose-built LLM tool. Both → OTLP fan-out from a Collector.

## Comparison

| Capability | Langfuse | Phoenix (Arize) | LangSmith | Opik | Weave | Plain OTLP |
|---|---|---|---|---|---|---|
| Licence | MIT core (EE features paid) | Elastic License 2.0 | Proprietary SaaS | Apache-2.0 | Apache-2.0 client, hosted platform | n/a |
| Self-host | Yes (Postgres + ClickHouse + Redis) | Yes (single container or Postgres) | No | Yes (Docker/K8s) | Partial | Yes |
| Ingestion | SDK + OTLP/HTTP (HTTP/JSON, HTTP/protobuf; no gRPC) | OTLP + OpenInference | SDK + OTLP | SDK + OTLP | SDK | OTLP |
| Prompt management | Yes, with versions/labels | Minimal | Strong, playground + commit | Yes | Basic | No |
| Datasets/experiments | Yes, SDK + CI action | Yes, strong for RAG | Strongest, incl. dataset comparison | Yes | Yes | No |
| LLM-as-judge | Templates + custom | Yes, plus drift analysis | Templates, polished | Yes | Yes | No |
| Dashboards/alerts | Custom dashboards + alerts | Dashboards + monitors | Dashboards | Dashboards | W&B dashboards | You build them |
| Session/multi-turn view | Yes | Yes | Yes | Yes | Yes | Manual |
| Cost tracking | Built-in model defs + pricing tiers | Yes | Yes | Yes | Yes | Derive yourself |

## Selection shortcuts

- **Regulated or self-host required, framework-agnostic** → Langfuse self-hosted.
- **RAG quality is the core problem** (retrieval recall, grounding, drift) → Phoenix.
- **LangGraph/LangChain everywhere, data may leave** → LangSmith.
- **Want OSS plus agent-trajectory evals and guardrails in one tool** → Opik.
- **Already running W&B for model training** → Weave (one vendor for train + serve).
- **Existing Datadog/Grafana estate and no appetite for a new tool** → OTLP to the existing backend, plus a small eval harness (DeepEval/promptfoo) in CI.

## Self-host sizing (rough)

| Volume | Stack | Notes |
|---|---|---|
| < 100k traces/mo | 2 vCPU / 4 GB, single node, Postgres + ClickHouse colocated | Fine for dev/staging; do not run HA |
| 100k–1M traces/mo | 4 vCPU / 8 GB app + 4 vCPU / 16 GB ClickHouse + 8 GB Postgres | Separate volumes; back up Postgres nightly |
| 1M–10M traces/mo | 8 vCPU / 16 GB app ×2 behind LB, ClickHouse 3-node cluster, managed Postgres | Budget real ops time; retention policy mandatory |
| > 10M traces/mo | Sample traces aggressively, keep all metrics, tiered retention (7d hot / 90d cold) | Content storage is the cost driver, not span count |

Retention drives cost more than ingestion. Decide content retention (often 7–30 days) separately from score/metric retention (often 12 months).

## Migration paths

- **Vendor SDK → OTLP:** replace the vendor SDK with plain OTel + GenAI instrumentation, point the exporter at a Collector, fan out to old and new backends, compare for a week, then cut over. Attributes survive if you use `gen_ai.*` names rather than vendor-specific ones.
- **Langfuse → Phoenix or vice versa:** both accept OTLP; scores/datasets do not transfer automatically — export via API to JSONL first.
- **SaaS → self-host:** expect to re-ingest nothing; historical traces usually stay behind. Export datasets and scores, drop raw history.

## Migration risks

- Vendor-specific attribute names (`langfuse.observation.*`, `openinference.*`) do not map 1:1 to `gen_ai.*`. Write the mapping down.
- Sampling policy changes silently alter cost dashboards. Version the sampling config with the app.
- If the backend is also your dataset store, migration means rebuilding the regression suite. Export datasets to git continuously.
