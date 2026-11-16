---
name: agent-memory-management
description: >-
  Use this skill when designing, implementing, or debugging AI agent memory
  systems — long-term memory, working memory, episodic memory, vector stores,
  summarization strategies, state persistence, context window optimization.
  Activates on "agent memory", "long-term memory", "working memory", "memory
  architecture", "state management", "context window", "vector store", "memory
  retrieval", "RAG", "summarization", "memory persistence", "conversation
  memory", "episodic memory", or "memory optimization".
version: 1.0.0
author: Skill Foundry
license: MIT
category: ai-agent-engineering
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - ai-agents
  - memory
  - state-management
  - context
  - vector-store
  - RAG
  - retrieval
  - summarization
  - persistence
  - architecture
  - embeddings
  - working-memory
  - episodic-memory
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
permissions:
  files.read: true
  files.write: true
  network: false
  shell.execute: true
  dangerous: false
metadata:
  tags:
    - memory-architecture
    - context-engineering
    - state-persistence
    - retrieval
  related_skills:
    - ai-agent-architecture
    - agentic-eval
---

# Agent Memory Management

## Overview

An agent without memory is an expensive stateless function: every session it
relearns the user, re-reads the same documents, and forgets the decision it made
four turns ago. An agent with *bad* memory is worse — it confidently recalls stale
facts, injects chunks that contradict the conversation, and burns 60% of its window
on a transcript nobody reads. Memory is the discipline of deciding **what to keep,
where to put it, when to fetch it back, and what to throw away**.

Three constraints shape every design decision:

- **The context window is finite and priced per token.** More context is not better
  context: attention degrades with length (lost-in-the-middle), cost scales
  linearly, and latency grows with prefill. Every retrieved token should earn its
  place.
- **Memory has a lifecycle.** Write → store → index → retrieve → rank → inject →
  decay → prune. Most broken systems skip the last three steps and become a
  landfill with a search box.
- **Persistence is a correctness problem, not a convenience.** If an agent crashes
  mid-workflow, what it remembers decides whether it resumes or repeats a side
  effect (a sent email, a charged card).

The governing rule: **memory is a retrieval problem, not a storage problem.** You
will rarely fail because you stored too little; you fail because the right thing
was not in context when the model needed it. Design for recall at the moment of use.

## When to Use

- Designing a new agent and deciding whether it needs memory at all, and which kind
- An agent forgets preferences between sessions, or contradicts a decision from earlier in the same session
- The context window overflows on long conversations, documents, or tool traces
- Retrieval returns plausible-but-irrelevant chunks and the agent answers from stale context
- Building RAG over a corpus and choosing chunking, embeddings, index type, and reranking
- A workflow must survive a crash, restart, or human-in-the-loop pause and resume idempotently
- Memory costs are climbing and you need to cut them without losing quality
- Multiple agents or sessions must share state across a store, bus, or blackboard

**When not to use:** a single-turn, stateless transformation (classify this text,
extract these fields) needs no memory layer — adding one is pure overhead. Prompt
improvements without state belong to prompt engineering. Measuring whether memory
*helped* belongs to `agentic-eval`; this skill builds the system, that one measures it.

## Memory Types

Four kinds of memory, distinguished by **lifetime** and **what they store**. Most agents
need two or three, not all four.

| Type | Stores | Lifetime | Typical medium | Use when |
|---|---|---|---|---|
| **Working** | Current task state, scratchpad, recent turns, active plan | Seconds–minutes, one task | Context window, in-process dict | Always. This is the only non-optional one |
| **Episodic** | Specific past events: "on Tuesday the user asked X and we did Y" | Days–months | Event log, append-only table, vector store with timestamps | Personalization, debugging, learning from past runs |
| **Semantic** | Facts and knowledge independent of when learned: "the refund policy is 30 days" | Months–years, versioned | Vector DB, knowledge graph, document store | RAG over a corpus, entity facts, domain knowledge |
| **Procedural** | How to do things: playbooks, tool-use patterns, learned routines | Long, revised slowly | Prompt library, skill files, fine-tune, code | Repeated multi-step tasks; the agent should get better at a task it has done before |

### Working memory

The agent's desk: current goal, plan, last N turns, intermediate tool results.
Scoped to one task and discarded when it ends, except the small piece you
deliberately promote. It is the only memory you cannot avoid, and it is where
context budgeting happens. Design it explicitly — a fixed structure (goal, plan,
facts, open questions, recent turns) beats an ever-growing message list, because a
structured scratchpad can be *rewritten* in place while a message list can only grow.

### Episodic memory

A timestamped log of what happened, used for two things people conflate:
**personalization** ("last time you asked for metric units", "we already tried that
and it failed") and **debugging/audit** — replay what the agent knew when it acted.
It must be timestamped and **never silently rewritten**; an event log you mutate is
not an event log. When a fact changes, append the correction with a new timestamp
and let recency ranking resolve the conflict.

### Semantic memory

Facts, not events. "The contract renews in March" is episodic (dated); "our SLA is
99.9%" is semantic (true regardless of when learned). Normally a vector index or
knowledge graph over documents — this is where RAG lives. The critical property is
**versioning**: a store that overwrites old policy text makes it impossible to
explain why the agent cited last quarter's rules. Keep effective dates and
supersede rather than delete.

### Procedural memory

How-to knowledge: the steps for a recurring task, the tool that actually works, the
query that returns the right rows. **Declarative** (playbooks and skill files loaded
when the task appears) is cheap, inspectable, and editable — prefer it. **Learned**
(patterns distilled from past trajectories into a prefix, examples, or weights) is
powerful but can encode a bad habit as policy; gate it behind review.

## Memory Architectures

Pick the smallest architecture that satisfies the requirement; memory-layer complexity
is paid for forever in debugging.

### Single-store

One store, usually a vector DB or a message table, serving everything.

```
agent ──write/read──▶ [ single store ]
```

Good for prototypes, single-user assistants, short-lived agents, RAG-only systems.
Fails when you need "recent turn beats old document" or "user preference beats
corpus fact" — one similarity score cannot express priority across memory classes.

### Dual-store (working + long-term)

The default professional choice. Working memory lives in the context window as a
structured scratchpad; long-term memory is external and retrieved on demand.

```
        ┌────────────────────┐
 turns ─▶│ working memory     │◀── retrieve ──┐
        │ (context window)   │               │
        └─────────┬──────────┘               │
                  │ compress / promote       │
                  ▼                          │
        ┌────────────────────┐      ┌────────┴─────────┐
        │ summarizer         │─────▶│ long-term store  │
        └────────────────────┘ write│ (vector + KV)    │
                                     └──────────────────┘
```

Good for most production assistants, coding agents, and support agents. The design
point is **the boundary**: what gets promoted on task completion (durable facts,
preferences, outcomes) versus discarded (tool chatter, retries).

### Hierarchical

Tiers with different latencies and costs, promoted and demoted by importance.

```
L0  context window      ~10k tokens   nanoseconds   free-ish
L1  session cache       ~1M tokens    ms            cheap
L2  vector store        ~100M chunks  ~50ms         per-query cost
L3  cold archive / S3   unbounded     seconds       cheapest
```

Good for long-running assistants with large corpora and multi-session products. The
design point is the **promotion/demotion policy** — without one, everything ends up
in L0 and you have reinvented "stuff it all in the prompt" with extra services.

### Distributed / agentic

Multiple agents share memory through a blackboard, event bus, or shared store.

```
  agent A ──┐                  ┌──▶ [ shared store ] ◀── agent C
            ├─▶ event bus ─────┤
  agent B ──┘                  └──▶ [ blackboard ]
```

Good for multi-agent systems, long-running pipelines, and human-in-the-loop. Fails
when concurrent writers have no ownership rule: two agents writing conflicting
"current plan" entries produce a system that argues with itself. Assign ownership
per key, or make writes append-only with a single reducer.

See `references/memory-architectures.md` for the full comparison with cost, latency,
accuracy, and operational-complexity tradeoffs, plus patterns by agent type.

## Context Window Management

The context window is the scarcest resource in the system. Manage it like a budget with
line items, not a bucket you pour into.

### Budget the window explicitly

Allocate before you fill. A workable default:

| Segment | Share | Notes |
|---|---|---|
| System prompt + tool schemas | 10–15% | Fixed; trim tool descriptions before anything else |
| Retrieved memory / documents | 25–35% | The part that actually makes the answer good |
| Conversation / working state | 20–30% | Recent turns + structured scratchpad |
| Output reserve | 15–25% | Never let generation get truncated mid-JSON |
| Safety margin | 5% | Tokenizer drift, tool results larger than expected |

If the sum exceeds 100%, cut retrieved memory first (rerank harder), then conversation (summarize) — never the output reserve.

### Strategies

**Sliding window.** Keep the last N turns verbatim, drop the rest. Cheap, and it
loses the beginning of the conversation — exactly where the user stated the
requirement. Use it for chit-chat, never for task work; pin the first message and the
system prompt outside the window.

**Summarization.** Replace old turns with a rolling summary at a fraction of the
tokens. Lossy in precisely the details that matter (numbers, names, constraints), so
keep a separate structured facts block that is never summarized — only appended to
and deduplicated.

**Selective retrieval.** Keep no history in context; store every turn and retrieve on
relevance to the current query. Scales to unbounded history and is the right default
for long-lived assistants. It can surface a stale turn that contradicts the live
conversation, so always blend in the last 2–4 turns unconditionally.

**Priority-based retention.** Score each candidate and keep the top of the budget:
`score = w1·relevance + w2·recency + w3·importance + w4·pinned`. Pinning is the escape
hatch — user-stated constraints ("never use my full name") are pinned and never
evicted, whatever the score says.

### Compaction order

When you must shrink, compact in this order — cheapest and least damaging first:

1. **Tool output → digest.** Replace raw JSON/HTML results with a 3-line summary plus
   a pointer to the full artifact on disk.
2. **Old turns → summary.** Keep the structured facts block intact.
3. **Retrieved chunks → fewer, better.** Rerank and cut the tail; never truncate a
   chunk mid-sentence.
4. **Duplicate elimination.** The same document retrieved twice, the system prompt
   restated in a tool result, the plan quoted in three places.
5. **Only then** drop low-priority history.

Never compact the system prompt, the original task statement, pinned constraints, or
the output reserve.

## Vector Store Integration

### Embeddings

- **Match the model to the task.** General-purpose models are fine for prose; code,
  tables, and multilingual corpora need models trained for them.
- **Never mix embedding models in one index.** Vectors from different models are not
  comparable. Changing the model means re-embedding the whole corpus — treat it as a
  migration, and store `embedding_model` and `dim` as metadata so a mismatch is
  detectable rather than silently wrong.
- **Normalize if the metric expects it.** Cosine similarity on unnormalized vectors
  makes the ranking partly a length artifact.
- **Query and document asymmetry.** Many models want different prefixes for queries
  versus passages; getting this wrong costs 5–15% recall and is invisible in testing.

### Chunking

Chunking is the highest-leverage decision in RAG, and the least glamorous.

| Strategy | When | Watch out |
|---|---|---|
| Fixed-size + overlap | Baseline, unstructured prose | Splits sentences and tables mid-row |
| Recursive / structure-aware | Markdown, HTML, code | Needs a sane separator hierarchy |
| Semantic (sentence-group) | Dense prose, long arguments | Slower to build, marginal gain over good recursive |
| Parent-child / small-to-big | Need precision retrieval + broad context | Retrieve small chunk, inject its parent |
| Per-record | Tabular data, tickets, API objects | One row per unit beats any splitter |

Practical defaults: 300–800 tokens per chunk with 10–20% overlap for prose; keep headings
with their content; never split a table; prepend the document title and section path so
an isolated chunk still says what it is about.

### Similarity search

- **HNSW** for low-latency approximate search at scale. Tune `M` and
  `ef_construction` for recall vs memory; `ef_search` for recall vs latency.
- **IVF-PQ** when the index must fit in RAM and some recall loss is acceptable.
  Needs a training pass and periodic retraining as the corpus drifts.
- **Flat / exact** under ~100k vectors. Fast enough, and it removes a whole class of
  "why did it miss that" bugs. Do not build an ANN index you do not need.
- **Measure recall against exact search** before shipping an ANN index; 70%
  recall@10 will feel randomly bad and you will blame the model.

### Hybrid search

Dense vectors miss exact identifiers (SKUs, error codes, function names); BM25
misses paraphrase. Combine them.

```
query ──┬─▶ dense  top-50 ──┐
        └─▶ sparse top-50 ──┴─▶ RRF fuse ─▶ cross-encoder rerank ─▶ top-5
```

Reciprocal Rank Fusion needs no score calibration between two incomparable scales:
`score = Σ 1/(k + rank_i)` with `k ≈ 60`. Then rerank the fused list with a
cross-encoder — usually the biggest quality win per unit of effort after chunking.

### Metadata filtering

Filter **before** or **during** vector search, never after. Post-filtering top-k
means a restrictive filter can silently return 2 results.

Always store and filter on `tenant_id` (mandatory in multi-tenant — a missing tenant
filter is a data-leak bug, not a relevance bug), `source`, `doc_type`, `effective_date`,
`version`, `author`, `acl`. Enforce scope in the query builder: a model must never be
able to widen its own reach.

## Memory Persistence Patterns

| Pattern | Latency | Durability | Good for | Limits |
|---|---|---|---|---|
| **In-process dict** | ns | none | Working memory, caches | Dies with the process |
| **File / JSONL** | ms | strong per-write | Single-node agents, dev, small state | No concurrency, no query, grows unbounded |
| **Relational DB** | ms | strong, transactional | Sessions, workflow state, audit | Schema migrations; not a similarity index |
| **Vector DB** | ~10–100ms | strong | Semantic/episodic retrieval at scale | Not for exact state; eventual consistency |
| **Distributed cache** (Redis etc.) | sub-ms | configurable | Session cache, locks, rate state | Eviction can silently drop state; not a source of truth |
| **Object store** | 10–100ms | strong | Artifacts, transcripts, embeddings backup | Not queryable without a catalog |

Rules that prevent most persistence bugs: **one source of truth per fact** (choose
the system of record and treat every other copy as a cache — two writable stores
always diverge); **append, don't overwrite, for history** (transcripts and event logs
are append-only; current state is a materialized view derived from them);
**write-ahead the decision, not just the result** (log intent before the side effect,
so a crash is recoverable and deduplicable); **persist the plan, not only the
messages** (resuming from a transcript requires re-deriving intent; resuming from a
stored plan is deterministic); and **namespace by agent, session, and tenant**
(retro-fitting tenancy into an existing store is a rewrite).

## Memory Retrieval Strategies

Retrieval is where memory systems are won or lost. Measure it — recall@k, MRR, nDCG on a
labeled set — rather than eyeballing answers.

| Strategy | How | Best for | Fails when |
|---|---|---|---|
| **Last-N** | Most recent N turns | Live conversation continuity | Long-range dependencies |
| **Semantic** | Embedding similarity to the current query | Large corpora, paraphrase | Exact IDs, rare terms, stale-vs-live conflicts |
| **Hybrid** | Dense + sparse fused, then reranked | Default for RAG | Overkill for tiny corpora; needs tuning |
| **Importance-weighted** | Score by salience (pinned, user-stated, decision) | Long-lived assistants | Importance is hard to estimate at write time |
| **Recency-weighted** | Exponential decay on age | Preferences that change, evolving facts | Stable facts get needlessly deprioritized |
| **Graph traversal** | Follow entity relations from a seed | Multi-hop questions ("who approves X for Y?") | Costly to build and maintain |

Bake the blend into one function so it is tunable and testable:

```python
def rank(candidates, query_vec, now, budget_tokens):
    ranked = []
    for c in candidates:
        rel = cosine(query_vec, c.vec)                     # 0..1
        rec = math.exp(-DECAY * age_days(c.ts, now))       # 0..1
        imp = c.importance                                 # 0..1, set at write
        score = 0.55*rel + 0.25*rec + 0.15*imp + (1.0 if c.pinned else 0.0)
        ranked.append((score, c))
    ranked.sort(key=lambda t: t[0], reverse=True)
    return fill_budget(ranked, budget_tokens)              # dedupe by doc_id first
```

Two non-negotiables: **deduplicate by source id** before filling the budget, and **always
include the pinned set and the last 2 turns** outside the ranking, so continuity survives
a bad similarity result. Retrieve for *the upcoming step*, not the whole task — an agent
about to edit a file needs that file, not the architecture doc. Query rewriting (2–3
retrieval queries) reliably beats a single raw query.

## Memory Consolidation

Consolidation is the offline pass that keeps a memory store from becoming a junkyard.
Run it on a schedule or at session end, never on the request path.

1. **Cluster.** Group near-duplicate memories by embedding similarity plus entity
   overlap. Ten turns saying "user prefers metric units" are one memory.
2. **Deduplicate.** Merge each cluster into one canonical entry, keeping the earliest
   timestamp as `first_seen`, the latest as `last_confirmed`, and the count as a
   confidence signal.
3. **Resolve conflicts.** When two entries disagree (old address vs new), prefer the
   newer, mark the older `superseded_by`, and keep both for audit — never delete the
   loser silently.
4. **Promote.** Recurring episodic patterns become semantic facts ("this user always
   asks for SQL, not prose"); frequent procedures become declarative playbooks.
5. **Summarize.** Roll old episodes into coarser summaries that keep pointers to the
   raw records, so detail stays recoverable.
6. **Prune.** Delete by documented rule: below an importance threshold and older than
   N days; never retrieved and older than M days; tool chatter immediately. Pinned and
   legally-required records are exempt. Pruning is a policy, not a cleanup script.

Consolidation needs an **idempotency key** (content hash + scope) so a re-run does
not duplicate entries, and it must be **reversible** — soft-delete with a grace
period, because a pass that hard-deletes user preferences is a support incident.

## Summarization Approaches

| Approach | How | Cost | Risk |
|---|---|---|---|
| **Extractive** | Select and keep original sentences | Low | Reads choppy; misses synthesis |
| **Abstractive** | Rewrite in fewer words | Medium | Invents or drops detail; unverifiable |
| **Recursive** | Summarize, then summarize the summaries | Low per level | Error compounds each level |
| **Hierarchical** | Section summaries + document summary | Medium | Needs structure in the source |
| **Map-reduce** | Summarize chunks in parallel, then merge | High but parallel | Loses cross-chunk relationships |

Rules that keep summaries trustworthy:

- **Keep numbers, names, dates, and constraints verbatim.** A summary that rounds
  "€4,250" to "about €4k" destroyed the only part a downstream agent needed.
- **Require provenance.** Each summary line points to a source id; anything
  unverifiable is dropped rather than smoothed.
- **Never summarize the constraints block.** User-stated rules live in a separate,
  never-compressed structure.
- **Bound recursion to 2–3 levels.** Beyond that, information loss dominates and you
  cannot trace the error.
- **Summarize for a purpose.** "Summarize this conversation" produces mush; "extract
  decisions, open questions, and stated preferences" produces something usable.

For conversation memory, keep **two structures**: a rolling narrative summary and an
append-only **facts ledger** of decisions, preferences, and identifiers. The ledger
survives every compaction pass; the narrative does not.

## State Management

Working memory is *what the model sees*; state is *what the system knows*. Conflating
them is a common source of "it resumed but did the wrong thing".

### Session state

Per-conversation: a durable row keyed by `session_id` holding the message list (or its
summary), the facts ledger, and the plan. Load on start, write on every turn that
changes a decision — never lose an irreversible action.

### Workflow state and checkpoints

Per-task execution: which step, which inputs, which outputs, which side effects have
fired. This is what makes resumption possible. Persist at step boundaries, before any
irreversible action, and on a timer for long steps. A checkpoint must be
**self-sufficient** — everything needed to resume without replaying history: the
plan, the cursor, accumulated results, and completed effects.

```json
{
  "run_id": "run_8f21",
  "step": "match_payments",
  "status": "in_progress",
  "attempts": {"match_payments": 2},
  "completed_effects": ["email_sent:msg_44", "ledger_posted:tx_91"],
  "cursor": {"invoice_id": "INV-1042"},
  "updated_at": "2026-11-16T10:22:31Z"
}
```

### Idempotent resumption

1. **Every side effect gets an idempotency key** derived from `run_id + step +
   target` — not a random UUID, which defeats the purpose on retry.
2. **Check completions before acting:** `if key in completed_effects: skip`.
3. **Pass the key through** where the provider supports idempotent calls, so a crash
   between "called" and "recorded" is harmless.
4. **Fence concurrent runs** with a lease per `run_id` and a TTL, so a dead worker
   does not block forever.
5. **Resume from the cursor, not the top.** Re-running a 40-step workflow from step 1
   because step 27 failed is how agents double-charge customers.

Two patterns to name: the **phantom checkpoint** (state written before the effect, so
resumption re-fires it) and the **optimistic checkpoint** (written after the effect
but before it succeeded, so resumption skips work that never happened). Write after
confirmation, and make the effect idempotent so the window between is harmless.

## Anti-Patterns

| # | Anti-pattern | Description | Impact | Fix |
|---|---|---|---|---|
| 1 | **Stuff-everything context** | Concatenate all history and documents into the prompt | Cost and latency explode; attention degrades; model loses the actual ask | Budget the window; retrieve and rerank; compact old turns |
| 2 | **Summarize-only memory** | Replace all history with a prose summary, no facts ledger | Numbers, names, and constraints quietly vanish | Keep an append-only facts ledger that is never summarized |
| 3 | **Unscoped multi-tenant retrieval** | Query the vector store without a tenant filter | Cross-customer data leak; worst possible failure | Enforce `tenant_id` in the query builder, not the prompt |
| 4 | **Post-filtering top-k** | Retrieve top-10 then filter by metadata | Restrictive filters return near-empty results silently | Filter during search; assert result count |
| 5 | **Mixed embedding models in one index** | Add vectors from a new model without re-embedding | Similarity scores become meaningless; recall collapses | Version the model; full re-embed as a migration |
| 6 | **Unbounded memory growth** | Append everything, never prune or consolidate | Store cost grows forever, retrieval quality decays, duplicate memories crowd out good ones | Scheduled consolidation with documented prune policy |
| 7 | **Rewriting the event log** | Update past entries in place to "correct" them | Loses audit trail and the ability to explain past actions | Append corrections with timestamps; supersede, don't overwrite |
| 8 | **Memory written before the effect** | Checkpoint state, then perform the side effect | Crash causes double-send/double-charge on resume | Write after confirmation; make effects idempotent with derived keys |
| 9 | **Random idempotency keys** | Generate a fresh UUID per attempt | Retries look like new work; dedupe impossible | Derive the key from run+step+target |
| 10 | **Sliding window on task work** | Drop the oldest turns of a long task | The original requirement and constraints disappear first | Pin the first message and constraints; summarize middle turns |
| 11 | **Similarity score as priority** | One cosine score decides across memory classes | Stale document beats a live user correction | Blend relevance, recency, importance; pin hard constraints |
| 12 | **Retrieving for the whole task** | One retrieval pass at task start | Later steps lack the context they need; early context is noise | Retrieve per step, with query rewriting |
| 13 | **Trusting a summary over the source** | Act on a summary as if it were the record | Compounded errors, unverifiable claims | Keep pointers to raw records; verify before irreversible actions |
| 14 | **Memory in the prompt only** | Store "state" as text the model must re-read and trust | Model can forget, contradict, or be prompt-injected into ignoring it | Keep state in code/DB; inject only what the step needs |
| 15 | **No retrieval evaluation** | Ship RAG without a labeled query set | Every change is a guess; regressions invisible | Build 50–200 labeled queries; track recall@k and nDCG |
| 16 | **Chatter stored as memory** | Persist tool retries, stack traces, and greetings | Noise dominates the index; retrieval quality drops | Filter at write time; store digests with artifact pointers |

## Reference Architectures

| Pattern | Working memory | Long-term | Retrieval | Watch |
|---|---|---|---|---|
| **Personal assistant** (dual-store) | Scratchpad + last 6 turns | Vector store (episodic) + facts ledger in SQL | Hybrid, scoped to `user_id`, per turn | Preference drift: supersede, never overwrite |
| **Support / RAG** (dual-store) | Last 4 turns + current ticket | Versioned policy index, date-filtered chunks | Hybrid + cross-encoder rerank | Answering from a superseded policy version |
| **Coding agent** (hierarchical) | Current file + plan + failing tests | L1 symbol index; L2 code/docs chunked by function with path attached | Symbol reference and stack-trace frames beat similarity | Index staleness on edited files |
| **Long pipeline** (workflow state) | Current step inputs | SQL workflow row + effect log + document index | Per step, not per task | Double-fired side effects on resume |
| **Multi-agent** (blackboard) | Role-specific projection | Append-only event bus + materialized view | Read your projection only | Two writers on one key |

Budget shape for the assistant case: 30% retrieval, 25% conversation, 18% output, 12%
system, 4% pinned. For coding, swap retrieval for file contents and keep the output reserve.

## Tooling

`scripts/memory_architect.py` turns a requirements profile into a recommended architecture
with tradeoffs. Stdlib-only, read-only, no network.

```bash
python3 scripts/memory_architect.py --print-schema > requirements.json
python3 scripts/memory_architect.py --config requirements.json
python3 scripts/memory_architect.py --self-test
```

## Verification Checklist

Before calling a memory system done:

- [ ] Every memory class has a stated lifetime and a delete rule; the context budget is explicit and the output reserve is protected
- [ ] Retrieval is scoped by tenant/user in code, with a result-count assertion
- [ ] Pinned constraints and the original task survive every compaction pass; the facts ledger is append-only and separate from the prose summary
- [ ] Embedding model and dimension are stored as metadata; a mismatch fails loudly
- [ ] Concurrency: lease per session/run with TTL
- [ ] Side effects use derived idempotency keys; resume skips completed effects
- [ ] Consolidation is idempotent, reversible, and off the request path; retrieval has a labeled eval set with recall@k
- [ ] Cost per session and p95 retrieval latency are measured, not assumed
