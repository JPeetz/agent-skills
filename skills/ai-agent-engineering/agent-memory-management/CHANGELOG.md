# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-16

### Added

- Initial release: `agent-memory-management` skill under the `ai-agent-engineering`
  category.
- Memory taxonomy with lifetimes and selection criteria: working, episodic,
  semantic, and procedural memory, plus the distinction between episodic events
  and semantic facts and why it changes the store design.
- Four architecture families with ASCII diagrams and explicit failure modes:
  single-store, dual-store (working + long-term), hierarchical (L0–L3), and
  distributed/agentic (event bus + blackboard).
- Context window management: an explicit segment budget with protected output
  reserve and safety margin, four retention strategies (sliding window,
  summarization, selective retrieval, priority-based retention), and a
  five-step compaction order that cuts the least damaging thing first.
- Vector store integration: embedding model discipline (no mixed models per
  index, query/document asymmetry, normalization), a chunking strategy table
  with concrete token defaults, ANN index selection (HNSW / IVF-PQ / flat) with
  recall measurement guidance, hybrid search with RRF and cross-encoder
  reranking, and pre-filter metadata requirements including mandatory tenant
  scoping.
- Persistence pattern comparison across in-process dict, JSONL/file, relational
  DB, vector DB, distributed cache, and object store, with the four rules that
  prevent divergence (single source of truth, append for history, write-ahead
  intent, namespace by agent/session/tenant).
- Retrieval strategy table (last-N, semantic, hybrid, importance-weighted,
  recency-weighted, graph traversal) with a concrete tunable ranking function,
  dedupe-before-budget, pinned-set injection, and per-step query rewriting.
- Memory consolidation as a six-step offline pass: cluster, deduplicate, resolve
  conflicts by superseding, promote episodic→semantic and procedural→declarative,
  roll up old episodes, and prune by documented rule — idempotent and reversible.
- Summarization approach comparison (extractive, abstractive, recursive,
  hierarchical, map-reduce) plus the rules that keep summaries faithful:
  verbatim identifiers, provenance, bounded recursion depth, and the
  narrative-summary + facts-ledger split.
- State management: session state, workflow state schema, self-sufficient
  checkpoints, and five-rule idempotent resumption including derived
  idempotency keys and lease-based fencing; names the phantom-checkpoint and
  optimistic-checkpoint failure patterns.
- Sixteen anti-patterns with description, impact, and fix — including unscoped
  multi-tenant retrieval, post-filtering top-k, mixed embedding models, random
  idempotency keys, similarity-score-as-priority, and summarize-only memory.
- Five reference architectures: personal assistant, support/RAG agent, coding
  agent, long-running pipeline, and multi-agent blackboard.
- `scripts/memory_architect.py` — stdlib-only advisor that validates a JSON
  requirement profile and emits a markdown recommendation covering tier,
  components, retrieval strategy, summarization, context budget, consolidation
  policy, cost estimates, tradeoffs, risks, and first build steps. Includes
  `--help`, `--print-schema`, `--json`, `--out`, and `--self-test` (5 profiles,
  8 invalid-config cases, 45 assertions), plus tolerant parsing so the output of
  `--print-schema` can be edited and fed straight back in.
- `references/memory-architectures.md` — full architecture comparison with a
  scoring matrix, patterns by agent type, cost/latency/accuracy/complexity
  tradeoff axes, migration paths, and a selection checklist.
- `evals/evals.json` — four positive activation cases (architecture selection,
  recall failure, crash-safe resumption, retrieval quality) and two near-miss
  negatives (unit testing, document summarization).
