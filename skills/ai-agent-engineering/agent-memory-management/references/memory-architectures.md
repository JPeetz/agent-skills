# Memory Architectures: Comparison and Selection

Reference for choosing between agent memory architectures. Companion to
`SKILL.md`; the skill teaches the decisions, this document is the lookup table.

---

## 1. Architecture comparison

Four families. Each is defined by **how many stores exist** and **who writes to
them**.

### 1.1 Single-store

```
  turns / tools / documents ──▶ [ ONE store ] ──▶ top-k ──▶ context
                                 (vector | table | KV)
```

Everything — conversation history, documents, user facts — goes into one index
and comes back through one similarity search.

| Dimension | Assessment |
|---|---|
| Cost | Lowest. One service, one bill, one index. |
| Latency | 10–60 ms per query; one hop. |
| Accuracy | Good until memory classes conflict. Then it degrades unpredictably. |
| Complexity | Trivial to build, easy to debug. |
| Ceiling | Expresses only *relevance*. Cannot encode "a user's live correction outranks the policy document". |

**Choose when:** prototype, single-user tool, stateless-per-task agent, a pure
RAG question-answering bot with no personalization, or fewer than ~10k memories.

**Do not choose when:** you need recency to beat similarity, you need per-tenant
isolation, or you need a durable record of decisions rather than a bag of text.

**Known failure:** the "similarity soup" — a 2024 policy chunk, a stale user fact,
and last turn's correction all score 0.78 and the model averages them into a
confident wrong answer. If you see that, you have outgrown this tier.

### 1.2 Dual-store (working + long-term)

The professional default. Working memory is structured and lives in the context
window; long-term memory is external and pulled in on demand.

```
        ┌─────────────────────┐
 turns ─▶│ working memory      │◀── retrieve ──┐
        │ goal / plan / facts │               │
        │ last-N turns        │               │
        └──────────┬──────────┘               │
                   │ compact + promote        │
                   ▼                          │
        ┌─────────────────────┐      ┌────────┴──────────┐
        │ summarizer          │─────▶│ long-term store    │
        └─────────────────────┘ write│ vector + KV/ledger │
                                      └────────────────────┘
```

| Dimension | Assessment |
|---|---|
| Cost | Low-medium: one summarization call + one retrieval call per turn. |
| Latency | 50–150 ms with rerank. |
| Accuracy | Best accuracy-per-effort for conversational agents. Explicit promotion policy prevents the similarity soup. |
| Complexity | Moderate. The hard part is not the code, it is the **boundary**: what gets promoted vs discarded. |
| Ceiling | Two surfaces (summary and store) can drift; needs source pointers to stay reconcilable. |

**Choose when:** support assistants, coding agents, sales agents — anything with
sessions longer than ~10 turns or a retrievable corpus, one or a few tenants.

**Design decisions that matter:**

1. **Promotion trigger.** End of task, end of session, or on an explicit
   `remember()` tool call. Prefer explicit: the model is a poor judge of what
   will matter later, but a stated preference is unambiguous.
2. **What is promoted.** Durable facts, stated preferences, decisions, outcomes.
   Never raw tool chatter or retries.
3. **What is never summarized.** Pinned constraints, identifiers, numbers.
4. **Compaction cadence.** Every N turns or at a token threshold (say 70% of the
   conversation budget), whichever comes first. Compaction on the critical path
   adds a latency spike; do it in a pre-step when the threshold is crossed.

### 1.3 Hierarchical (tiered)

Memory as a cache hierarchy with promotion and demotion, borrowed from CPU
design.

```
L0  context window      ~8–200k tokens    ns           effectively free per read
L1  session/process cache  ~1M tokens     sub-ms       cheap, volatile
L2  vector store        ~100M chunks      ~50 ms       per-query + storage
L3  cold archive        unbounded         seconds      cheapest, slowest
```

| Dimension | Assessment |
|---|---|
| Cost | Scales well: hot data is small and fast, cold data is huge and cheap. |
| Latency | Bimodal — 5 ms on a cache hit, 100 ms on a promotion. Tail latency is the risk. |
| Accuracy | Highest ceiling, because you can afford to keep everything and still retrieve fast. |
| Complexity | High. Two policies (promotion, demotion) to tune, and both fail silently. |
| Ceiling | A bad promotion threshold produces perfectly plausible, quietly worse answers. |

**Choose when:** a large corpus (>1M chunks) *and* long or unbounded history, high
concurrency (thousands of sessions), or explicit cost pressure on a large index.

**Design decisions that matter:**

1. **Promotion signal.** Access count in a window, explicit importance, or
   recency — pick one primary and one tiebreak. Access-count promotion is the
   most defensible and the least surprising.
2. **Demotion signal.** Age plus never-read. Demote, don't delete.
3. **Eviction from L1.** Must be rebuildable from L2, or it is data loss, not a
   cache miss. Assert this in a test.
4. **Warm-up.** Cold start on a new node means every request goes to L2. Budget
   for it or you will see a p99 spike on deploy.

### 1.4 Distributed / shared (agentic)

Multiple agents read and write shared memory — a blackboard, an event bus, or a
shared store.

```
  agent A ──┐                      ┌──▶ agent C
            ├──▶ [ event bus ] ────┤
  agent B ──┘         │            └──▶ agent D
                      ▼
            [ shared state view ]   single reducer, per-key owner
```

| Dimension | Assessment |
|---|---|
| Cost | Highest: coordination, locks/leases, and usually two services minimum. |
| Latency | Event bus hop adds 5–50 ms; cross-agent consistency adds more. |
| Accuracy | Can be very high (specialists share findings) or terrible (conflicting writes). |
| Complexity | Highest. Causality spans processes; without correlation ids you cannot explain an outcome. |
| Ceiling | Conflict resolution is a design problem, not a tuning problem. |

**Choose when:** multiple agents must genuinely share findings (research fan-out,
review panels), a long-running pipeline has parallel workers, or a human in the
loop needs to inspect and correct shared state.

**Non-negotiable rules:**

1. **Per-key ownership.** Exactly one agent may write a given field. Everyone
   else proposes changes. Without this the system argues with itself.
2. **Append-only events, materialized view.** Writes are events; the readable
   state is a projection. Then conflict resolution is a deterministic reducer,
   not a race.
3. **Correlation id on every read and write**, propagated from the originating
   task, so a trace reconstructs the causal chain.
4. **Idempotent writers.** Re-delivery is normal in an event bus; a handler that
   is not idempotent will double-apply.

---

## 2. Scoring matrix

Relative ratings for a mid-size production workload. `●●●●●` best.

| Criterion | Single-store | Dual-store | Hierarchical | Distributed |
|---|---|---|---|---|
| Build effort | ●●●●● | ●●●● | ●● | ● |
| Operational simplicity | ●●●●● | ●●●● | ●● | ● |
| Latency (p95) | ●●●●● | ●●●● | ●●● | ●● |
| Cost efficiency at scale | ● | ●●● | ●●●●● | ●● |
| Retrieval accuracy ceiling | ●● | ●●●● | ●●●●● | ●●●● |
| Personalization | ● | ●●●●● | ●●●●● | ●●●● |
| Resumability / durability | ● | ●●●● | ●●●● | ●●●●● |
| Multi-tenant isolation | ● | ●●● | ●●●●● | ●●●● |
| Debuggability | ●●●●● | ●●●● | ●● | ● |
| Handles unbounded history | ● | ●●● | ●●●●● | ●●●● |

Read the matrix as "where does this tier fall over", not "which is best". Every
step right buys accuracy and scale with complexity and money.

---

## 3. Memory patterns by agent type

### Conversational assistant (single user, months of history)

- **Architecture:** hierarchical, or dual-store with a strict compaction policy.
- **Stores:** facts ledger (relational, append-only) + vector index over turns and
  documents; session cache for the active conversation.
- **Retrieval:** recency-weighted semantic, blended with always-on last 2–4 turns.
- **Never compress:** pinned preferences, names, identifiers, medical/legal
  constraints.
- **Watch:** preference drift. "I moved" must supersede the old address, not sit
  beside it. Use `superseded_by`, and prefer newer on conflict.

### Support / customer-service agent (multi-tenant, RAG)

- **Architecture:** dual-store; flat or HNSW index depending on corpus size.
- **Stores:** versioned document index (effective dates mandatory) + ticket
  transcript for audit. Episodic memory is optional; per-user personalization is
  often a policy risk, so scope it deliberately.
- **Retrieval:** hybrid + cross-encoder rerank; filter `tenant_id` and
  `effective_date <= now` **before** search.
- **Watch:** policy versioning. Answering from last quarter's policy is the
  classic failure, and it is invisible without a version filter.

### Coding agent (repo-aware)

- **Architecture:** dual-store with a code-aware L1 (symbol index).
- **Stores:** current file + plan + failing tests in working memory; semantic
  index over the repo chunked by function/class with the file path and symbol
  name attached; recent diffs as a short log.
- **Retrieval:** symbol/graph lookup and stack-trace frames beat similarity.
  Retrieve the *file being edited* unconditionally.
- **Never summarize code.** Link to it. A summarized function is a bug factory.
- **Watch:** index staleness. Invalidate changed files on write, or the agent
  will confidently edit a version that no longer exists.

### Long-running pipeline / workflow agent

- **Architecture:** dual-store plus durable workflow state; hierarchical if the
  document volume is large.
- **Stores:** workflow table (source of truth) + effect log + document index.
- **Retrieval:** per-step, not per-task. Each step retrieves what it needs.
- **Mandatory:** checkpoints at step boundaries, idempotency keys derived from
  `run_id + step + target`, TTL lease per run, resume-from-cursor.
- **Watch:** the phantom checkpoint and the optimistic checkpoint (see SKILL.md).

### Multi-agent research / review panel

- **Architecture:** distributed blackboard.
- **Stores:** append-only event bus + materialized per-role views + a findings
  store the synthesizer reads.
- **Retrieval:** each agent reads only its projection. Reading the whole board
  floods context and duplicates work.
- **Mandatory:** per-key ownership, correlation ids, idempotent handlers.
- **Watch:** convergence. Agents that can all write "final answer" produce
  competing answers; designate one synthesizer.

### Batch enrichment / classification (no memory)

- **Architecture:** none. In-process dict for the current record, nothing else.
- **Why:** adding a vector store here is pure cost. If you feel the urge, you
  probably want a cache instead.

---

## 4. Tradeoff axes

### Cost

The four cost drivers, in descending order of typical impact:

1. **Injected context tokens** — every retrieved token is paid on every turn.
   Cutting retrieval from 3,000 to 1,200 tokens per turn is usually a bigger
   saving than any infrastructure change, and often *improves* accuracy by
   removing distractors.
2. **Embedding of the corpus** — one-time, but repeated on every model change.
   Assume at least one full re-embed per year.
3. **Vector store** — roughly proportional to index size in RAM. ANN indexes
   trade RAM for latency; quantization trades recall for RAM.
4. **Reranking** — a per-query model call over the top-50. Cheap per call,
   meaningful at volume. Gate it by route: high-stakes queries rerank, casual
   ones don't.

### Latency

Budget it per hop:

| Hop | Typical p95 |
|---|---|
| Embed the query | 10–40 ms (cache repeats) |
| Vector search (HNSW, warm) | 5–30 ms |
| BM25 search | 5–20 ms |
| RRF fusion | <1 ms |
| Cross-encoder rerank, 50 candidates | 40–150 ms |
| Fetch payloads from DB | 5–30 ms |
| **Total realistic** | **70–250 ms** |

If your target is under 100 ms, drop the reranker or cache final results. If it
is under 50 ms at scale, you need a precomputed cache keyed by query embedding,
and you should question whether the target is real.

### Accuracy

Ranked by measured impact, from experience across RAG systems:

1. **Chunking** — largest single lever, and the least discussed.
2. **Reranking** — large, cheap, near-universal win.
3. **Hybrid vs dense-only** — large for corpora with identifiers.
4. **Metadata filtering correctness** — a missing filter is not "slightly worse",
   it is wrong answers and data leaks.
5. **Embedding model choice** — real but usually smaller than the above, and the
   most expensive to change later.
6. **Index parameters (M, ef_search)** — matters at the recall tail; measure it.

### Complexity

Each added store costs, permanently:

- a health check, a retry policy, and a failure mode in every request path
- a backfill and reconciliation job when schemas diverge
- a new way for data to be stale in a way nobody notices
- onboarding cost for the next engineer

Rule of thumb: **one store per memory class, and no more.** If a new store does
not own a distinct class of data with a distinct lifetime, it is a cache or it is
redundant.

---

## 5. Migration paths

Memory architectures are usually grown, not chosen once.

| From → To | Trigger | Work |
|---|---|---|
| Single → dual | Similarity soup: stale facts outrank live corrections | Add a facts ledger and a summarizer; backfill by extracting facts from stored transcripts; keep the old index as the semantic layer |
| Dual → hierarchical | p95 retrieval above target, or index cost above budget | Add a cache tier and a promotion policy; **do not** re-index — reuse the same store as L2 |
| Dual → distributed | A second agent needs the same memory | Introduce an event log; make the existing store a projection of it; add per-key ownership before adding agents |
| Any → narrower | Memory layer is not paying for itself | Instrument recall and cost per session for two weeks before removing anything; delete the tier that never wins a retrieval |

The last row is the one nobody writes down. An unnecessary memory tier is a
permanent tax on latency, cost, and debugging attention. Measure, then delete.

---

## 6. Selection checklist

Answer in order; stop at the first match.

1. Does more than one agent need to write shared state? → **distributed**
2. Is history unbounded, the corpus >1M chunks, or concurrency >2,000? → **hierarchical**
3. Do sessions exceed ~10 turns, or is there any external corpus, or must state
   survive restart? → **dual-store**
4. Otherwise → **single-store** (and consider whether you need memory at all)

Then fill in the second-order choices:

- Retrieval: none (short) → last-N → dense → **hybrid+rerank** (default for text corpora)
- Chunking: 300–800 tokens, 10–20% overlap, structure-aware, title prepended
- Summarization: none (short) → extractive trim → rolling abstractive + ledger → recursive + ledger
- Consolidation: nightly, idempotent, reversible
- Evaluation: 50–200 labeled queries, recall@k and nDCG, before and after every change
