---
name: ai-agent-architecture
description: >-
  Use this skill when designing, auditing, or diagnosing an AI agent's system
  architecture. Activates on "agent architecture", "agent design", "agent audit",
  "multi-agent system", "agent orchestration", "agent topology", "agent
  evaluation design", or "agent execution flow". Covers agent topology design,
  reference architecture patterns, audit frameworks, evaluation design,
  execution continuity, and architectural decision records. Outputs architecture
  diagrams, RFC-style design docs, audit reports with severity-ranked findings,
  and migration plans.
version: 1.0.0
author: Skill Foundry
license: MIT
category: ai-agent-engineering
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - agent-architecture
  - agent-design
  - multi-agent
  - orchestration
  - audit
  - evaluation
  - AI-agents
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
  shell.execute: false
  dangerous: false
metadata:
  tags:
    - agent-architecture
    - agent-design
    - multi-agent
    - agent-audit
    - evaluation-design
    - topology
  related_skills:
    - agentic-eval
    - threat-modeling
    - prompt-engineering
---

# AI Agent Architecture

## Overview

An agent architecture is the set of decisions that determine what an agent can do, what it cannot do, what happens when it fails, and how you will find out. Most agent failures in production are not model failures. They are architecture failures: an unbounded loop with no stop condition, a supervisor that cannot tell a subagent's failure from its success, a tool contract that returns a plausible string where a typed error was needed, a state machine whose recovery path nobody ever executed.

This skill is for the design half and the audit half of that problem. It gives you a small set of topology patterns with real trade-offs, a design process that forces the expensive decisions before code (scope → topology → contract → eval → iterate), a severity-ranked audit framework, an ADR template so decisions survive their authors, and an evaluation design that measures the architecture rather than the demo.

The core stance: **an agent is a distributed system with a probabilistic component inside it.** Everything you know about distributed systems still applies — partial failure, idempotency, retries, observability, contract versioning — and the probabilistic component makes the failure modes worse, not different. Design for the failure, not the happy path.

## When to Use

- Designing a new agent or multi-agent system, or writing its design document
- Auditing an existing agent before it gets production traffic, a new owner, or a bigger tool budget
- Diagnosing an agent that "sometimes does the wrong thing" and nobody can reproduce it
- Choosing a topology: single agent, supervisor, swarm, pipeline, mesh
- Defining what an agent is allowed to do: tool surface, permissions, escalation, human gates
- Designing the evaluation suite, or arguing about whether an eval proves anything
- Writing the ADR that records why the architecture looks like this
- Planning a migration from one topology to another

**When not to use:** tuning a prompt belongs to `prompt-engineering`; writing one system prompt or tool description belongs to prompt authoring; building the eval harness's scoring code belongs to `agentic-eval`; threat-modelling a specific attack surface belongs to `threat-modeling`. This skill owns the *shape* — who talks to whom, what the contract is, where state lives, how you know it works.

## Agent Topology Patterns

Five patterns cover nearly everything. Pick deliberately and write down why; the default failure is arriving at swarm by accretion.

### 1. Single agent (with tools)

One model, one loop, a bounded tool set. The loop is: observe → decide → act → observe.

```
┌─────────────────────────────┐
│  Controller (one loop)      │
│  ┌────────┐   ┌──────────┐  │
│  │ Model  │──▶│ Tool call│  │
│  └────▲───┘   └────┬─────┘  │
│       │            │        │
│       └── result ◀─┘        │
└─────────────────────────────┘
```

- **Use when:** one clear job, tools under ~15, task fits in one context window, failure is cheap to retry.
- **Strengths:** simplest to debug, cheapest per task, one place for policy and logging.
- **Weaknesses:** context saturation on long tasks, no parallelism, tool selection degrades past ~15-20 tools.
- **Non-negotiable:** explicit stop condition (max turns), explicit budget (tokens/time/cost), explicit failure return.

> Most systems that "need multi-agent" are one agent with a bad tool contract. Prove the single agent fails before adding a second one.

### 2. Supervisor (router / orchestrator–worker)

A lead agent decomposes the task, dispatches to specialists, and synthesizes their results. The supervisor is the only agent that talks to the user.

```
              ┌────────────┐
   user ─────▶│ Supervisor │
              └──┬───┬───┬─┘
        ┌────────┘   │   └────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Worker A│  │ Worker B│  │ Worker C│
   └─────────┘  └─────────┘  └─────────┘
        └────────── results ─────────┘
```

- **Use when:** subtasks are heterogeneous (research vs. code vs. review), or workers need different tools/models/permissions.
- **Strengths:** isolation (a worker's context pollution stays local), per-worker model choice, per-worker permission scoping.
- **Weaknesses:** the supervisor becomes a bottleneck and a single point of misinterpretation; result synthesis is where quality dies silently.
- **Contract rules:** every worker returns a **typed envelope** (status, output, error class, cost, confidence), never free text. The supervisor must distinguish "worker failed" from "worker returned nothing" from "worker returned the wrong shape".

### 3. Swarm (peer delegation)

Agents hand off control to peers; no fixed lead. Handoff is a tool call: `transfer_to(agent, reason)`.

```
   ┌────────┐ ⇄ ┌────────┐
   │Agent A │   │Agent B │
   └───┬────┘   └────┬───┘
       │  ⇄  ┌───────▼──┐
       └────▶│ Agent C  │
             └──────────┘
```

- **Use when:** the task path is genuinely unknown up front and each specialist knows best who should handle the next step (triage → billing → refund).
- **Strengths:** no central bottleneck, natural for routing-heavy workloads.
- **Weaknesses:** unbounded handoff loops (A→B→A), no global view, hard to attribute cost, hard to evaluate.
- **Contract rules:** a **global handoff budget** (max N transfers) and a **visited set** so an agent cannot be re-entered without new information. Every handoff carries a serialized state object, not a conversation replay.

### 4. Pipeline (deterministic stages)

Fixed sequence of stages; each stage may be an agent, a tool, or plain code. Control flow is code, not model judgement.

```
extract ──▶ classify ──▶ plan ──▶ execute ──▶ verify
   │            │           │          │          │
 typed        typed      typed      typed      typed
 output       output     output     output     gate
```

- **Use when:** the workflow is known and mostly stable; you want reproducibility, per-stage retries, and per-stage evaluation.
- **Strengths:** debuggable, cacheable, each stage independently testable and replaceable, cheap to re-run one stage.
- **Weaknesses:** brittle on inputs the designer didn't anticipate; the model cannot reroute.
- **Contract rules:** every boundary is a **typed artifact** on disk or in a store, with a schema and a version. A stage must be idempotent given the same input artifact.

### 5. Mesh (shared blackboard / event bus)

Agents publish to and subscribe from shared state; coordination is emergent. No direct calls.

```
   ┌────────┐      ┌──────────────┐      ┌────────┐
   │Agent A │─────▶│  Blackboard  │◀─────│Agent B │
   └────────┘      │ (task queue, │      └────────┘
                   │  facts, log) │
   ┌────────┐      └──────┬───────┘      ┌────────┐
   │Agent C │◀────────────┘              │Agent D │
   └────────┘                             └────────┘
```

- **Use when:** long-running, many independent work items, agents of different kinds contributing to one evolving artifact (research corpus, incident response).
- **Strengths:** highest parallelism and extensibility; add an agent without touching others.
- **Weaknesses:** emergent behavior is the hardest thing to debug; duplicate work; no clear completion condition; cost scales non-linearly.
- **Contract rules:** the blackboard schema **is** the architecture — version it, validate writes, define claim/lease semantics so two agents cannot do the same work.

### Choosing a topology

| Signal | Single | Supervisor | Swarm | Pipeline | Mesh |
|---|---|---|---|---|---|
| Subtasks known at design time | ✓ | ✓ | ✗ | ✓✓ | ✗ |
| Needs parallelism | ✗ | ✓ | ~ | ✓ | ✓✓ |
| Needs different tools/models per step | ~ | ✓✓ | ✓ | ✓ | ✓ |
| Reproducibility required | ✓ | ~ | ✗ | ✓✓ | ✗ |
| Failure must be attributable to one component | ✓✓ | ✓ | ✗ | ✓✓ | ✗ |
| Task path unknown up front | ✗ | ✓ | ✓✓ | ✗ | ~ |
| Team is new to agents | ✓✓ | ✓ | ✗ | ✓ | ✗ |

Start at the top-left and move right only under a named pressure. Write the pressure down — "we chose swarm because X" is an ADR; "we chose swarm because it's the modern pattern" is how you inherit a system nobody can debug.

## Architecture Design Process

Five steps, in order. Each step produces an artifact; skipping one moves its cost into production.

### Step 1 — Scope: what the agent may and may not do

Write the boundary before the diagram.

- **One-sentence job statement.** If it needs "and", you have two agents or two tasks.
- **Inputs and outputs**, with types. "Takes a support email, returns a categorized ticket with citations."
- **Explicit non-goals.** What the agent must refuse, and what it must escalate. Non-goals prevent scope creep more effectively than any prompt.
- **Blast radius:** what is the worst thing this agent can do with its tools? Name it, then decide whether it is acceptable, gated, or scoped away.
- **Success criteria, measurable.** "85% of tickets categorized correctly with zero fabricated policy citations", not "works well".

### Step 2 — Topology: who exists and who talks to whom

- Pick a pattern from the table above, with the pressure that justifies it.
- Draw the graph: nodes are agents/tools/stores, edges are calls. Label each edge with the **contract** (what is passed) and whether it is **sync or async**.
- Mark every **human gate**: where a human must approve before an irreversible action.
- Mark every **persistence boundary**: where state leaves memory and becomes durable.
- Count the **maximum number of hops** from user input to final output. That number is your worst-case latency and cost multiplier; if you cannot state it, the topology is unbounded.

### Step 3 — Contract: the interfaces, not the prompts

This is the step teams skip, and it is the one that decides whether the system is debuggable.

For every node boundary define:

| Element | Required | Example |
|---|---|---|
| Input schema | yes | `{ticket_id: str, body: str, locale: enum}` |
| Output schema | yes | `{category: enum, confidence: float, citations: list[Citation]}` |
| Error classes | yes | `retryable`, `terminal`, `needs_human`, `contract_violation` |
| Idempotency key | for any side effect | `hash(ticket_id, step)` |
| Timeout + retry policy | yes | 30s, 2 retries, exponential backoff, jitter |
| Token/cost budget | yes | 50k tokens, $0.10 per invocation |
| Version | yes | `categorizer/v2` |

Rules that prevent most agent bugs:

- **Typed envelopes, not prose.** A subagent that answers in prose forces the parent to parse intent; a parent that parses intent invents it.
- **Absence of output is a distinct state** from empty output and from failure. Model all three.
- **Side-effecting tools need idempotency keys.** Agents retry; without keys you double-charge the customer.
- **Tool descriptions are contracts.** Ambiguous descriptions are the single largest source of wrong-tool selection; write them like docstrings with preconditions and failure modes.
- **Every tool declares what it does NOT do.** Negative space is where the model guesses.

### Step 4 — Eval: how you will know it works

Design the eval at the same time as the architecture, not after (see [Evaluation Design](#evaluation-design)). At minimum, before writing implementation code:

- 20–50 **golden tasks** with expected outcomes, including at least 5 adversarial ones.
- A **failure taxonomy** you expect, so the eval can measure the classes you fear.
- A **decision threshold**: what pass rate ships, what blocks, what needs human review.

### Step 5 — Iterate: instrument, then change one thing

- Ship with tracing from day one. An agent without per-step spans is undebuggable at the second failure.
- Change one architectural variable per iteration (topology, model, tool surface, prompt). Two at once and you learn nothing.
- Record each iteration as an ADR amendment, not a Slack thread.

### Design document skeleton (RFC style)

```markdown
# RFC: <agent name>

## Status
Draft | In review | Accepted <date> | Superseded by <link>

## Problem
<the job, in one paragraph, with the measurable success criterion>

## Non-goals
- <what this agent must refuse>
- <what stays human>

## Proposed architecture
<topology diagram; node and edge table with contracts>

## State and persistence
<what is durable, where, schema, retention>

## Failure model
| Failure | Detection | Response | Owner |
|---|---|---|---|

## Security and permissions
<tool surface, credential scope, human gates, blast radius>

## Evaluation plan
<golden set, metrics, thresholds, cadence>

## Cost model
<per-task token and tool cost, expected volume, ceiling>

## Rollout and rollback
<phases, flags, kill switch, what "off" means>

## Open questions
## Decision record
<links to ADRs>
```

## Audit Framework

An audit answers one question: **would this system fail loudly or silently?** Score four dimensions, then rank findings by severity so the report is actionable rather than a list.

### Dimension 1 — Completeness

Does the design account for the whole lifecycle, or only the happy path?

- [ ] Every loop has a **stop condition** that is not model judgement (max turns, budget, deadline)
- [ ] Every failure has a defined **response**: retry, fallback, escalate, or fail closed
- [ ] **Absence, empty, and error** are three distinct modelled states at every boundary
- [ ] Every side-effecting action has an **idempotency key** and a **rollback or compensating action**
- [ ] Human gates exist at every **irreversible** action (payment, delete, external send, deploy)
- [ ] State that must survive a restart is **persisted**, and recovery is a tested path, not a hope
- [ ] The **maximum hop count** and **maximum cost** are stated and enforced
- [ ] Tool schemas validate outputs, not just inputs

### Dimension 2 — Security

- [ ] Tool surface is **least privilege**; no agent holds a credential broader than its job
- [ ] Untrusted input (web content, user files, tool results, other agents' output) is **never** treated as instruction
- [ ] The agent cannot **widen its own permissions** via a tool call
- [ ] Prompt-injection reachability is mapped: which tools can an injected instruction invoke?
- [ ] Exfiltration paths are enumerated: what can leave, to where, carrying what
- [ ] Secrets are not in the context window, prompts, logs, or traces
- [ ] Every tool call is **attributable to a principal** (user, service, agent) in the audit log
- [ ] Destructive tools are either absent, gated, or dry-run-first

### Dimension 3 — Observability

- [ ] One **trace per task**, one **span per step**, with model, token counts, cost, and latency on each
- [ ] Prompts, tool args, and tool results are captured (with redaction) and **retrievable by trace id**
- [ ] Errors are classified, not just logged — you can count `contract_violation` separately from `timeout`
- [ ] **Outcome** is recorded per task (success/failure/escalated), not just activity
- [ ] You can answer, from data: which step fails most, which tool is slowest, what a task costs at p95
- [ ] Alerts exist on **outcome drift** (success rate, escalation rate, cost per task) — not just on 5xx
- [ ] Replay is possible from a stored trace without re-running side effects

### Dimension 4 — Cost

- [ ] Per-task cost is **measured**, not estimated, and has a stated ceiling
- [ ] Budgets are **enforced** (hard stop), not merely monitored
- [ ] Token growth is bounded: history trimming, summarization, or retrieval — not unbounded accumulation
- [ ] Model tier matches task difficulty; no frontier model on classification
- [ ] Loops have a cost-per-iteration ceiling and a total ceiling
- [ ] Cacheable work is cached (retrieval, classification, deterministic sub-calls)
- [ ] Cost is attributable per user/task/agent so an outlier is visible

### Severity ranking

| Severity | Definition | Response |
|---|---|---|
| **S1 — Critical** | Silent data loss, unbounded spend, or an ungated irreversible action; will cause an incident | Block release |
| **S2 — High** | Failure mode exists with no detection; you will learn from the customer | Fix before scale |
| **S3 — Medium** | Detectable but slow/expensive to diagnose; degrades MTTR | Schedule |
| **S4 — Low** | Naming, structure, documentation, minor inefficiency | Backlog |

Finding format — one block per finding, no prose paragraphs:

```markdown
### S2-03: Supervisor cannot distinguish worker timeout from empty result
- **Where:** `supervisor.py:112` → `worker_client.call()`
- **Evidence:** exception path returns `[]`; supervisor treats `[]` as "no findings"
- **Impact:** silent under-reporting; a failed research worker reports "nothing found"
- **Fix:** return typed envelope `{status: "timeout"}`; supervisor escalates on non-`ok`
- **Effort:** S
```

Audit report skeleton:

```markdown
# Architecture audit: <agent> — <date>
## Verdict: <ship | ship with fixes | do not ship> / risk: <low|med|high>
## Scorecard
| Dimension | Findings (S1/S2/S3/S4) | Assessment |
## Findings (severity ordered)
## What the architecture gets right
## Recommended migration path
```

Include what it gets right. An audit that is only a defect list gets argued with; an audit that shows the reviewer understood the design gets acted on.

## Architectural Decision Record (ADR)

ADRs are how architecture survives the people who chose it. One decision per file, immutable once accepted — supersede, never edit. Store in `docs/adr/NNNN-slug.md`.

```markdown
# ADR-0007: Supervisor topology over swarm for ticket routing

- **Status:** Accepted (2026-11-14)
- **Deciders:** <names/roles>
- **Supersedes:** —
- **Superseded by:** —

## Context
Routing has 4 known intents and a fixed escalation policy. Volume is 40k/day.
Handoff loops would be unbounded and cost is per-hop. Two engineers own the system.

## Decision
Supervisor with three specialist workers. Handoff is supervisor-only; workers
cannot call each other. Worker results return as typed envelopes.

## Consequences
- Positive: bounded hop count (max 3), attributable cost per worker, one policy point.
- Negative: supervisor is a single point of misinterpretation; adding an intent means touching the router.
- Neutral: worker prompts become stable, so per-worker eval is possible.

## Alternatives considered
- **Swarm:** rejected — unbounded handoff, no per-hop cost ceiling, needs eval we don't have.
- **Pipeline:** rejected — intents are not ordered; classification is genuinely conditional.

## Signals that would reopen this
> 10k/day and >10 intents, or supervisor misroutes exceeding 5% of traffic.
```

Rules: an ADR states the **pressure**, not just the choice; it records **rejected alternatives with reasons**; it names **signals that would reopen it** — a decision with no reopening condition becomes dogma.

## Anti-Patterns

| Anti-pattern | Symptom | Why it fails | Instead |
|---|---|---|---|
| **Swarm by default** | No one can explain a run's path | Emergent control flow with no attribution | Justify topology with a named pressure; start single-agent |
| **Prose handoffs** | Parent "interprets" child output | Intent parsed out of text is invented | Typed envelopes with status/error class |
| **Unbounded loop** | Costs spike; runs never end | Stop condition is model judgement | Max turns + budget + deadline, all enforced |
| **Agent as router for deterministic work** | Slow, expensive, flaky classification | Model used where a rule or query suffices | Deterministic code for deterministic steps |
| **God tool** | One tool with a `mode` parameter | Model must guess the mode; failures are ambiguous | Separate tools with tight schemas |
| **Context as memory** | Quality decays on long tasks | Window is finite and attention degrades | Durable store + retrieval; summarize deliberately |
| **Silent fallback** | Wrong answers, no errors | Degradation hidden behind a default | Fail loudly or return a typed degraded status |
| **Eval by demo** | "It worked when we tried it" | 5 examples prove nothing about the tail | Golden set + adversarial set + thresholds |
| **Prompt-only guardrails** | Policy bypasses found in prod | Instructions are suggestions to a model | Tool-level and code-level enforcement |
| **Agent owning its own permissions** | Privilege creep | Self-modifying authority | Permissions fixed outside the loop |
| **No persistence at step boundaries** | Long tasks restart from zero | State lives in one context | Durable checkpoints after each stage |
| **Retry without idempotency** | Duplicate side effects | Agents retry on ambiguity | Idempotency keys on every mutation |

## Evaluation Design

The question an eval answers is not "does it work" but "**which failure classes does it still have, at what rate, and is that acceptable?**"

### Layers

| Layer | What it measures | Size | Cadence |
|---|---|---|---|
| **Unit** | One tool, one parser, one classifier | 50–200 cases | Every commit |
| **Step** | One agent node's decision quality given inputs | 20–50 per node | Every change to that node |
| **Trajectory** | The sequence of steps, not just the final answer | 20–50 tasks | Every architecture change |
| **End-to-end** | Task outcome vs. expected outcome | 50–200 tasks | Pre-release + nightly |
| **Online** | Real traffic outcomes, escalations, cost | continuous | Always |

Trajectory evaluation is the one teams skip and the one that catches architecture bugs: an agent can reach the right answer through a path that cost 40x and would break on any perturbation. Score both **outcome** and **path** (hop count, tool errors, recoveries).

### Golden set construction

- **Sampled from real traffic**, not invented. Synthetic tasks share the designer's blind spots.
- **Stratified** across intents, difficulty, and input length.
- **Adversarial slice**, minimum 20%: prompt injection, missing fields, contradictory instructions, tool failures, empty results, out-of-scope requests.
- **Expected outcome is checkable** — exact match, schema validity, or a rubric a second model can apply reliably. "Looks good" is not an expectation.
- **Frozen and versioned.** Silent edits to the golden set make every historical comparison a lie.

### Metrics that matter

| Metric | Definition | Why |
|---|---|---|
| Task success rate | Outcome matches expectation | The headline, and the least informative alone |
| Trajectory efficiency | Steps used / steps needed | Catches success-by-brute-force |
| Tool error rate | Failed calls / total calls | Separates tooling bugs from reasoning bugs |
| Recovery rate | Errors followed by a successful retry | Measures the failure model, not the model |
| Escalation rate | Tasks handed to a human | The honest cost signal; rising means the agent is failing politely |
| Harmful action rate | Ungated irreversible actions / tasks | Should be structurally zero |
| Cost per successful task | Total cost / successes | The number that decides viability |
| p95 latency | End-to-end | UX and timeout design |

### Pass criteria and the rules of eval

- **Threshold per layer, agreed before the run.** Choosing a threshold after seeing results is how evals become theatre.
- **Report confidence.** 50 tasks with 90% success has a wide interval; do not present it as 90%.
- **Track per-failure-class rates, not just aggregate.** An aggregate that holds while escalations triple is a regression.
- **Every production incident grows the golden set.** This is the only mechanism that makes the suite get better over time.
- **Pin the model version.** An eval that changes when the provider ships is not a regression test.
- **Compare against a baseline**, ideally the previous version and, for routing/classification work, a deterministic baseline.

### Execution continuity

The eval and the audit share one question: can a run survive the middle?

- **Checkpoint after every stage** that has a side effect or costs more than a few seconds.
- **A resumed run must not repeat completed side effects** — checkpoint + idempotency key together.
- **Recovery is a tested path.** Deliberately kill the process mid-run in staging and confirm the task completes correctly. An untested resume path is a myth.
- **Partial results are first-class.** A run that fails at stage 4 of 5 must leave stages 1–3 usable, with a status that says so.
- **Timeout budgets compound.** If each step has a 30s timeout and the task has 10 steps, the caller's timeout must account for the sum, not the max.
- **Long runs need a heartbeat and an owner.** A task with no progress marker is indistinguishable from a hung one.

## Red Flags

- No stop condition other than "the model decides it's done"
- Any irreversible tool without a human gate
- Retries on a mutating tool with no idempotency key
- A subagent whose failure is indistinguishable from an empty result
- Cost measured monthly rather than per task
- Traces that record prompts but not outcomes
- Golden set written by the same person who wrote the prompts, from imagination
- Topology chosen before the pressure that justifies it
- An architecture with no ADR — or an ADR with no rejected alternatives
- Numbers in the design doc with no measurement behind them

## Verification

Before calling a design complete:

- [ ] One-sentence job statement, typed inputs/outputs, and explicit non-goals
- [ ] Topology chosen with the pressure written down, and an ADR recording rejected alternatives
- [ ] Every node boundary has input schema, output schema, error classes, timeout, retry policy, budget, version
- [ ] Maximum hop count and maximum cost per task stated and enforced
- [ ] Every irreversible action gated or absent; blast radius named
- [ ] Trace per task, span per step, outcome recorded, alerts on outcome drift
- [ ] Golden set ≥20 tasks including adversarial cases; thresholds agreed before the run
- [ ] Resume path exists, checkpointed, and tested by killing a run mid-flight
- [ ] Rollout phased with a kill switch, and "off" defined

Before calling an audit complete:

- [ ] All four dimensions scored with evidence, not impressions
- [ ] Every finding has location, evidence, impact, fix, and severity
- [ ] Findings severity-ordered; S1s block the verdict explicitly
- [ ] Report states what the architecture gets right
- [ ] Migration path given for S1/S2 findings, not just a defect list
