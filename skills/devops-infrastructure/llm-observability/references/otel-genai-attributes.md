# OpenTelemetry GenAI Conventions — Attribute and Metric Reference

Status: **Development** (not stable). The conventions live in `open-telemetry/semantic-conventions-genai` after being split out of the main semantic-conventions repo. Names WILL drift; pin instrumentation library versions and re-run `scripts/check_genai_attrs.py` after upgrades.

## Span structure

```
handle-support-question            (INTERNAL, your app)
├── retrieval kb-refunds           (CLIENT, gen_ai.operation.name=retrieval)
├── chat gpt-4o                   (CLIENT, gen_ai.operation.name=chat)
│   └── execute_tool get_order     (INTERNAL, gen_ai.operation.name=execute_tool)
└── embeddings text-embedding-3-small (CLIENT, gen_ai.operation.name=embeddings)
```

Span name pattern: `{gen_ai.operation.name} {gen_ai.request.model}`. Span kind `CLIENT` for remote model calls, `INTERNAL` for in-process model execution, `CLIENT` for retrieval against a vector store.

## Required / recommended attributes

| Attribute | Requirement | Type | Example |
|---|---|---|---|
| `gen_ai.operation.name` | Required | string | `chat`, `text_completion`, `generate_content`, `embeddings`, `retrieval`, `execute_tool`, `invoke_agent`, `create_memory` |
| `gen_ai.provider.name` | Required | string | `openai`, `anthropic`, `aws.bedrock`, `gcp.vertex_ai`, `azure.ai.openai`, `mistral_ai` |
| `gen_ai.request.model` | Required for cost attribution | string | `gpt-4o`, `claude-sonnet-4-5` |
| `gen_ai.response.model` | Recommended | string | `gpt-4o-2024-08-06` (the alias actually served) |
| `gen_ai.usage.input_tokens` | Required for inference | int | `1204` |
| `gen_ai.usage.output_tokens` | Required for inference | int | `186` |
| `gen_ai.usage.cache_read.input_tokens` | Opt-in | int | `1024` (billed at a fraction) |
| `gen_ai.usage.cache_write.input_tokens` | Opt-in | int | `1024` |
| `gen_ai.usage.reasoning.output_tokens` | Opt-in | int | `512` (reasoning models) |
| `gen_ai.response.finish_reasons` | Recommended | string[] | `["stop"]`, `["length"]`, `["content_filter"]` |
| `gen_ai.response.id` | Opt-in | string | provider response id |
| `gen_ai.conversation.id` | Recommended for chat apps | string | session identifier |
| `gen_ai.request.temperature` / `top_p` / `top_k` / `max_tokens` / `seed` / `stop_sequences` | Recommended | various | sampling configuration |
| `gen_ai.output.type` | Recommended | string | `text`, `json`, `image` |
| `gen_ai.prompt.name` / `gen_ai.prompt.version` | Recommended | string | `refund-policy` / `v2.3` |
| `gen_ai.retrieval.top_k` | Recommended | int | `5` |
| `gen_ai.data_source.id` | Conditionally required | string | `kb-refunds-prod` |
| `error.type` | Conditionally required on failure | string | `timeout`, `429`, `invalid_request`, `content_filter` |
| `server.address` / `server.port` | Recommended | string/int | `api.openai.com` / `443` |

### Content attributes (opt-in, sensitive, large)

| Attribute | Purpose |
|---|---|
| `gen_ai.system_instructions` | System prompt as structured messages |
| `gen_ai.input.messages` | Full prompt messages |
| `gen_ai.output.messages` | Completion messages |
| `gen_ai.tool.definitions` | Tool schemas offered to the model |
| `gen_ai.retrieval.documents` | Retrieved doc ids + scores |
| `gen_ai.retrieval.query.text` | Retrieval query |
| `gen_ai.system_instructions_ref`, `gen_ai.input.messages_ref`, `gen_ai.output.messages_ref`, `gen_ai.tool.definitions_ref` | Pointers to externally stored content (S3/GCS/local path) instead of inline |

The `*_ref` form is the production default when content must be inspectable but not stored in the observability backend. Upload hooks are configured with `OTEL_INSTRUMENTATION_GENAI_CONTENT_HOOK`, `OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH`, `OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT` (json/jsonl), `OTEL_INSTRUMENTATION_GENAI_UPLOAD_MAX_QUEUE_SIZE`.

## Metrics

| Metric | Type | Unit | Use |
|---|---|---|---|
| `gen_ai.client.inference.duration` | histogram | s | Latency SLO; bucket boundaries 0.01→81.92 |
| `gen_ai.client.inference.time_to_first_chunk` | histogram | s | Streaming perceived latency |
| `gen_ai.client.inference.time_per_output_chunk` | histogram | s | Generation throughput |
| `gen_ai.client.inference.usage.input_tokens` | counter | tokens | Cost and volume per model |
| `gen_ai.client.inference.usage.output_tokens` | counter | tokens | Cost and volume per model |
| `gen_ai.client.inference.usage.cache_read.input_tokens` | counter | tokens | Cache-hit economics |
| `gen_ai.client.operation.duration` | histogram | s | Non-inference operations only (tool, agent, retrieval covered separately) |
| `gen_ai.invoke_agent.duration` / `.inference_calls` / `.tool_calls` | hist/counter | s/count | Agent cost-of-orchestration |
| `gen_ai.server.time_to_first_token` | histogram | s | Only if you serve a model |

Never put `user.id`, `conversation.id`, or `request.id` on metrics. Cardinality explosion is the #1 way to break a metrics backend with LLM data.

## Legacy name drift (handle explicitly)

| Older / widely deployed | Current direction |
|---|---|
| `gen_ai.system` | `gen_ai.provider.name` |
| `gen_ai.usage.prompt_tokens` / `completion_tokens` | `gen_ai.usage.input_tokens` / `output_tokens` |
| `gen_ai.client.token.usage` (histogram) | `gen_ai.client.inference.usage.*` counters |
| `gen_ai.client.operation.duration` for inference | `gen_ai.client.inference.duration` |
| `gen_ai.request.max_tokens` on older libs | unchanged, but check per-library mapping |
| Vendor attrs: `openinference.*`, `langfuse.*`, `llm.*` | keep two layers: emit `gen_ai.*` for portability, let the backend add its own |

Practical rule: emit **both** the modern `gen_ai.*` attribute and the vendor attribute your backend prefers during migration, then delete the vendor one once queries are ported.

## Instrumentation library map

| Library | Covers | Notes |
|---|---|---|
| `opentelemetry-instrumentation-openai` (OpenLLMetry) | OpenAI, Anthropic, Bedrock, Cohere, LangChain, LlamaIndex | Broadest coverage; version-pin |
| `openinference-instrumentation-*` (Arize) | OpenAI, LangChain, LlamaIndex, DSPy, CrewAI | Default for Phoenix, works with any OTLP backend |
| `openlit` | Python/TS SDKs, many frameworks | Also emits GPU/vector-DB telemetry |
| Vendor SDKs (Langfuse, LangSmith, Weave, Opik) | Custom + native integrations | Best DX, least portable |

## Validation

Run `python3 scripts/check_genai_attrs.py export.json` on an OTLP/JSON export. It flags missing required attributes, missing token counts, unclassifiable errors, high-cardinality attributes, and captured prompt content (an INFO reminder to confirm retention).
