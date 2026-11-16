#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""memory_architect.py -- recommend an AI agent memory architecture.

Reads a JSON description of an agent's memory requirements and emits a
markdown recommendation: architecture tier, retrieval strategy, persistence
layout, summarization approach, context budget, consolidation policy, and the
tradeoffs being accepted.

Stdlib only. Read-only: performs no network calls and writes nothing unless
--out is given.

Usage:
  python3 memory_architect.py --config requirements.json
  python3 memory_architect.py --config requirements.json --out rec.md
  python3 memory_architect.py --print-schema
  python3 memory_architect.py --self-test
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------

SCHEMA: Dict[str, Any] = {
    "conversation_length": {
        "type": "enum",
        "values": ["short", "medium", "long", "unbounded"],
        "default": "medium",
        "help": "Typical session length. short=<10 turns, medium=10-50, "
                "long=50-500, unbounded=never ends / months of history.",
    },
    "concurrent_users": {
        "type": "int",
        "default": 1,
        "help": "Peak number of simultaneous active sessions.",
    },
    "data_types": {
        "type": "list",
        "values": ["chat", "documents", "structured_records", "code"],
        "default": ["chat"],
        "help": "Kinds of content the agent must remember or retrieve.",
    },
    "corpus_size": {
        "type": "enum",
        "values": ["none", "small", "medium", "large"],
        "default": "none",
        "help": "Retrievable knowledge base size. none, small=<10k chunks, "
                "medium=10k-1M, large=>1M.",
    },
    "persistence_required": {
        "type": "bool",
        "default": True,
        "help": "Must memory survive process restart?",
    },
    "workflow_resumption": {
        "type": "bool",
        "default": False,
        "help": "Must multi-step work resume after a crash without repeating "
                "side effects?",
    },
    "multi_tenant": {
        "type": "bool",
        "default": False,
        "help": "Do different customers share one deployment (hard isolation)?",
    },
    "multi_agent": {
        "type": "bool",
        "default": False,
        "help": "Do multiple agents share memory or coordinate through it?",
    },
    "compliance_audit": {
        "type": "bool",
        "default": False,
        "help": "Is an immutable, replayable audit trail of what the agent "
                "knew and did required?",
    },
    "budget": {
        "type": "enum",
        "values": ["low", "medium", "high"],
        "default": "medium",
        "help": "Monthly infrastructure tolerance for the memory layer.",
    },
    "latency_target_ms": {
        "type": "int",
        "default": 800,
        "help": "p95 budget for a memory retrieval round trip, in ms.",
    },
    "context_window_tokens": {
        "type": "int",
        "default": 128000,
        "help": "Model context window in tokens.",
    },
}

CONFIG_KEYS = set(SCHEMA.keys())


class ConfigError(ValueError):
    """Raised when an input config is structurally invalid."""


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ConfigError(msg)


def validate_config(cfg: Any) -> Dict[str, Any]:
    """Validate and normalize a config dict. Raises ConfigError on bad input."""
    _require(isinstance(cfg, dict), "config must be a JSON object")

    unknown = set(cfg.keys()) - CONFIG_KEYS
    if unknown:
        raise ConfigError(
            "unknown key(s): %s. Valid keys: %s"
            % (", ".join(sorted(unknown)), ", ".join(sorted(CONFIG_KEYS)))
        )

    out: Dict[str, Any] = {}
    for key, spec in SCHEMA.items():
        if key not in cfg:
            out[key] = spec["default"]
            continue
        val = cfg[key]
        kind = spec["type"]

        if kind == "enum":
            _require(
                isinstance(val, str) and val in spec["values"],
                "'%s' must be one of %s (got %r)"
                % (key, spec["values"], val),
            )
            out[key] = val
        elif kind == "bool":
            _require(isinstance(val, bool), "'%s' must be true or false" % key)
            out[key] = val
        elif kind == "int":
            _require(
                isinstance(val, int) and not isinstance(val, bool),
                "'%s' must be an integer" % key,
            )
            _require(val >= 0, "'%s' must be >= 0" % key)
            out[key] = val
        elif kind == "list":
            _require(
                isinstance(val, list) and all(isinstance(v, str) for v in val),
                "'%s' must be a list of strings" % key,
            )
            bad = [v for v in val if v not in spec["values"]]
            _require(
                not bad,
                "'%s' has invalid value(s) %s; allowed: %s"
                % (key, bad, spec["values"]),
            )
            _require(len(val) > 0, "'%s' must not be empty" % key)
            out[key] = list(dict.fromkeys(val))  # dedupe, keep order
        else:  # pragma: no cover - schema is internal
            raise ConfigError("internal schema error for '%s'" % key)

    # Cross-field sanity checks
    _require(
        out["concurrent_users"] >= 1,
        "'concurrent_users' must be at least 1",
    )
    _require(
        out["context_window_tokens"] >= 4000,
        "'context_window_tokens' must be >= 4000",
    )
    _require(
        out["latency_target_ms"] >= 50,
        "'latency_target_ms' must be >= 50",
    )
    if out["corpus_size"] == "none":
        _require(
            "documents" not in out["data_types"],
            "'data_types' includes 'documents' but 'corpus_size' is 'none'; "
            "set corpus_size to small/medium/large",
        )
    if out["multi_agent"] and out["budget"] == "low":
        _require(
            False,
            "multi_agent memory on a 'low' budget is not realistic "
            "(shared store + coordination is at least 2 services); "
            "raise budget to medium or high",
        )
    if out["latency_target_ms"] < 150 and out["corpus_size"] == "large":
        _require(
            False,
            "a <150ms retrieval target over a large corpus requires a "
            "dedicated ANN index and hot cache; this tool will not pretend "
            "an in-process store meets it",
        )
    return out


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

LENGTH_RANK = {"short": 1, "medium": 2, "long": 3, "unbounded": 4}
CORPUS_RANK = {"none": 0, "small": 1, "medium": 2, "large": 3}


def choose_architecture(cfg: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Return (architecture tier, list of reasons)."""
    reasons: List[str] = []
    c_len = LENGTH_RANK[cfg["conversation_length"]]
    c_corpus = CORPUS_RANK[cfg["corpus_size"]]

    if cfg["multi_agent"]:
        reasons.append(
            "multiple agents share memory, so coordination and ownership "
            "rules dominate the design"
        )
        return "distributed", reasons

    hierarchical = (
        c_corpus >= 3
        or c_len >= 4
        or cfg["concurrent_users"] >= 2000
        or (c_corpus >= 2 and c_len >= 4)
    )
    if hierarchical:
        if c_corpus >= 3:
            reasons.append("corpus >1M chunks needs a real ANN index plus tiers")
        if c_len >= 4:
            reasons.append("unbounded history cannot live in one store")
        if cfg["concurrent_users"] >= 2000:
            reasons.append(
                "%d concurrent users demands caching and load isolation"
                % cfg["concurrent_users"]
            )
        return "hierarchical", reasons

    needs_durable_longterm = (
        c_len >= 2
        or c_corpus >= 1
        or cfg["persistence_required"]
        or cfg["workflow_resumption"]
        or cfg["compliance_audit"]
    )
    if needs_durable_longterm:
        if cfg["persistence_required"]:
            reasons.append("memory must survive process restart")
        if c_corpus >= 1:
            reasons.append("a retrievable corpus requires an external index")
        if c_len >= 2:
            reasons.append("sessions run long enough that history must be "
                           "compacted and stored")
        if cfg["workflow_resumption"]:
            reasons.append("resumable workflows need durable state")
        if cfg["compliance_audit"]:
            reasons.append("audit requires an append-only record")
        return "dual-store", reasons

    reasons.append(
        "short sessions, no external corpus, and no restart requirement fit "
        "in one store"
    )
    return "single-store", reasons


def choose_retrieval(cfg: Dict[str, Any]) -> Tuple[str, str]:
    """Return (retrieval strategy, justification)."""
    has_text = any(
        t in cfg["data_types"] for t in ("documents", "code")
    )
    corpus = cfg["corpus_size"]

    if has_text and corpus in ("medium", "large"):
        return (
            "hybrid + cross-encoder rerank",
            "a text corpus this size contains exact identifiers (IDs, error "
            "codes, symbol names) that dense vectors miss; fuse BM25 with dense "
            "via RRF, then rerank the top 50 to 5",
        )
    if has_text and corpus == "small":
        return (
            "hybrid (dense + BM25) without rerank",
            "small corpora make reranking a latency cost with little gain; "
            "fusion alone handles both paraphrase and exact terms",
        )
    if corpus == "none" and LENGTH_RANK[cfg["conversation_length"]] >= 3:
        return (
            "recency-weighted semantic over stored turns",
            "there is no corpus, so the only thing to retrieve is past "
            "conversation; blend similarity with exponential recency decay",
        )
    if corpus == "none":
        return (
            "last-N turns (no retrieval)",
            "history is short enough to keep verbatim; a retrieval layer "
            "would add failure modes without adding recall",
        )
    return (
        "semantic with metadata filters",
        "moderate corpus with structure; filter by source and date before "
        "the vector search rather than after",
    )


def choose_persistence(cfg: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return list of (component, purpose)."""
    comps: List[Tuple[str, str]] = []

    if cfg["workflow_resumption"] or cfg["compliance_audit"]:
        comps.append(
            ("Relational DB (Postgres/SQLite)",
             "system of record for workflow state, checkpoints, and the "
             "idempotency/effect log — transactional and queryable"),
        )
    elif cfg["persistence_required"]:
        comps.append(
            ("Relational DB or JSONL file",
             "durable session + facts ledger; JSONL is acceptable only for a "
             "single-process agent"),
        )
    else:
        comps.append(("In-process dict", "working memory only; state dies with "
                                         "the process by design"))

    if CORPUS_RANK[cfg["corpus_size"]] >= 1:
        comps.append(
            ("Vector store",
             "semantic/episodic index over %s corpus; store tenant_id, source, "
             "effective_date, and embedding_model as filterable metadata"
             % cfg["corpus_size"]),
        )

    if cfg["concurrent_users"] >= 500 or cfg["multi_agent"]:
        comps.append(
            ("Distributed cache (Redis-class)",
             "session cache, run leases, and rate state — never the source of "
             "truth, because eviction is silent"),
        )

    if cfg["compliance_audit"]:
        comps.append(
            ("Append-only object store",
             "immutable transcripts and raw artifacts with content hashes, for "
             "replay and audit"),
        )
    return comps


def choose_summarization(cfg: Dict[str, Any]) -> Tuple[str, str]:
    c_len = LENGTH_RANK[cfg["conversation_length"]]
    if c_len >= 4:
        return (
            "recursive + facts ledger",
            "unbounded history summarized in levels capped at 2-3 deep, with "
            "an append-only ledger of decisions, identifiers, and constraints "
            "that is never compressed",
        )
    if c_len == 3:
        return (
            "rolling abstractive summary + facts ledger",
            "50-500 turn sessions need a compacted narrative plus an "
            "uncompressed ledger; numbers and names are copied verbatim",
        )
    if c_len == 2:
        return (
            "extractive tail-trimming",
            "10-50 turns rarely need synthesis; trim old chatter and keep "
            "decisions verbatim",
        )
    return (
        "none",
        "short sessions fit in the window; summarizing would only lose detail",
    )


def context_budget(cfg: Dict[str, Any]) -> List[Tuple[str, int]]:
    """Return [(segment, percent)] summing to 100."""
    if CORPUS_RANK[cfg["corpus_size"]] >= 2:
        retrieval = 35
        convo = 20
    elif CORPUS_RANK[cfg["corpus_size"]] == 1:
        retrieval = 25
        convo = 28
    else:
        retrieval = 0
        convo = 45

    system = 12
    output = 20 if cfg["workflow_resumption"] else 18
    pinned = 4
    total = system + retrieval + convo + output + pinned
    margin = 100 - total
    if margin < 3:
        convo -= (3 - margin)
        margin = 3
    return [
        ("System prompt + tool schemas", system),
        ("Retrieved memory / documents", retrieval),
        ("Conversation + working state", convo),
        ("Pinned constraints (never evicted)", pinned),
        ("Output reserve", output),
        ("Safety margin", margin),
    ]


def consolidation_plan(cfg: Dict[str, Any]) -> List[str]:
    steps = [
        "Cluster near-duplicate memories by embedding similarity + entity overlap.",
        "Merge each cluster: keep earliest `first_seen`, latest `last_confirmed`, "
        "and the occurrence count as a confidence signal.",
    ]
    if cfg["compliance_audit"]:
        steps.append(
            "Supersede conflicting records with `superseded_by`; never delete — "
            "audit requires the prior state to remain readable."
        )
    else:
        steps.append(
            "Supersede conflicting records and soft-delete losers with a "
            "30-day grace window."
        )
    steps.append(
        "Promote recurring episodic patterns into semantic facts and repeated "
        "procedures into declarative playbooks."
    )
    if LENGTH_RANK[cfg["conversation_length"]] >= 3:
        steps.append(
            "Roll episodes older than 30 days into coarser summaries that keep "
            "pointers to the raw records."
        )
    steps.append(
        "Prune by documented rule: importance below threshold and older than "
        "90 days; never-retrieved and older than 180 days; tool chatter "
        "immediately. Pinned records are exempt."
    )
    steps.append(
        "Run idempotently (content-hash + scope key) and off the request path — "
        "nightly or at session end."
    )
    return steps


def cost_model(cfg: Dict[str, Any]) -> List[str]:
    """Rough order-of-magnitude monthly figures with stated assumptions."""
    users = cfg["concurrent_users"]
    sessions_per_user_month = {
        "short": 40, "medium": 20, "long": 8, "unbounded": 30,
    }[cfg["conversation_length"]]
    sessions = max(1, users * sessions_per_user_month)

    retrieval_tokens = {
        "none": 0, "small": 900, "medium": 2200, "large": 3200,
    }[cfg["corpus_size"]]
    turns = {"short": 6, "medium": 25, "long": 120, "unbounded": 200}[
        cfg["conversation_length"]
    ]
    tokens_per_month = sessions * turns * (retrieval_tokens + 700)

    lines = [
        "Assumptions: %d users x %d sessions/month x %d turns x ~%d injected "
        "tokens/turn. Order-of-magnitude only — replace with your own traffic "
        "numbers before budgeting."
        % (users, sessions_per_user_month, turns, retrieval_tokens + 700),
        "Injected memory tokens/month: ~%.1fM" % (tokens_per_month / 1e6),
    ]
    if CORPUS_RANK[cfg["corpus_size"]] >= 1:
        embed_chunks = {"small": 10_000, "medium": 250_000, "large": 2_000_000}[
            cfg["corpus_size"]
        ]
        lines.append(
            "One-time embedding of ~%s chunks (~%.1fM tokens); re-run on every "
            "embedding-model change, so budget for at least one migration."
            % (f"{embed_chunks:,}", embed_chunks * 250 / 1e6)
        )
    lines.append(
        "Vector store: %s. %s"
        % (
            {"none": "none needed", "small": "single node or embedded",
             "medium": "managed mid-tier", "large": "sharded managed cluster"}[
                cfg["corpus_size"]],
            "Reranking adds a per-query model call on the top-50 only."
            if CORPUS_RANK[cfg["corpus_size"]] >= 2 else
            "No rerank call at this corpus size.",
        )
    )
    if cfg["concurrent_users"] >= 500:
        lines.append("Cache and lease layer is required at this concurrency; "
                     "treat it as fixed cost, not optional.")
    return lines


def risks(cfg: Dict[str, Any]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    if cfg["multi_tenant"]:
        out.append((
            "Tenant leakage",
            "Enforce tenant_id inside the query builder and assert a non-empty "
            "result count; a model-side instruction is not an isolation boundary.",
        ))
    if cfg["workflow_resumption"]:
        out.append((
            "Duplicate side effects on resume",
            "Derive idempotency keys from run_id+step+target, record the effect "
            "before returning, and fence concurrent runs with a TTL lease.",
        ))
    if LENGTH_RANK[cfg["conversation_length"]] >= 3:
        out.append((
            "Constraint loss during compaction",
            "Pin user-stated constraints and the original task outside the "
            "summarization path; verify they survive a forced-compaction test.",
        ))
    if cfg["corpus_size"] in ("medium", "large"):
        out.append((
            "Silent recall regression",
            "Build 50-200 labeled queries and track recall@k against exact "
            "search before and after any index or embedding change.",
        ))
    if cfg["concurrent_users"] >= 500:
        out.append((
            "Cache eviction treated as truth",
            "Session state in the cache must be rebuilt from the store on miss; "
            "never let the cache be the only copy of a decision.",
        ))
    if cfg["compliance_audit"]:
        out.append((
            "Unauditable rewrite",
            "Append corrections with timestamps; forbid UPDATE/DELETE at the "
            "database permission level so the rule is enforced, not documented.",
        ))
    if cfg["budget"] == "low":
        out.append((
            "Cost creep from retrieval",
            "Cap retrieved tokens per turn, cache query embeddings, and skip "
            "reranking for low-stakes routes.",
        ))
    if not out:
        out.append((
            "Over-engineering",
            "This profile is simple; adding a vector store or multi-tier cache "
            "now buys failure modes you do not need. Revisit only when a "
            "measured limit is hit.",
        ))
    return out


def analyse(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Full analysis. cfg must already be validated."""
    arch, arch_reasons = choose_architecture(cfg)
    retrieval, retrieval_why = choose_retrieval(cfg)
    summarizer, summarizer_why = choose_summarization(cfg)
    return {
        "architecture": arch,
        "architecture_reasons": arch_reasons,
        "retrieval": retrieval,
        "retrieval_why": retrieval_why,
        "persistence": choose_persistence(cfg),
        "summarization": summarizer,
        "summarization_why": summarizer_why,
        "budget": context_budget(cfg),
        "consolidation": consolidation_plan(cfg),
        "cost": cost_model(cfg),
        "risks": risks(cfg),
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

ARCH_TITLE = {
    "single-store": "Single-store",
    "dual-store": "Dual-store (working + long-term)",
    "hierarchical": "Hierarchical (tiered, promoted/demoted)",
    "distributed": "Distributed / shared blackboard",
}


def render(cfg: Dict[str, Any], res: Dict[str, Any]) -> str:
    L: List[str] = []
    a = L.append

    a("# Memory architecture recommendation")
    a("")
    a("## Requirement profile")
    a("")
    a("| Setting | Value |")
    a("|---|---|")
    a("| Conversation length | %s |" % cfg["conversation_length"])
    a("| Concurrent users | %s |" % f"{cfg['concurrent_users']:,}")
    a("| Data types | %s |" % ", ".join(cfg["data_types"]))
    a("| Corpus size | %s |" % cfg["corpus_size"])
    a("| Persistence across restart | %s |" % _yn(cfg["persistence_required"]))
    a("| Workflow resumption | %s |" % _yn(cfg["workflow_resumption"]))
    a("| Multi-tenant | %s |" % _yn(cfg["multi_tenant"]))
    a("| Multi-agent | %s |" % _yn(cfg["multi_agent"]))
    a("| Audit trail required | %s |" % _yn(cfg["compliance_audit"]))
    a("| Budget | %s |" % cfg["budget"])
    a("| p95 retrieval target | %d ms |" % cfg["latency_target_ms"])
    a("| Context window | %s tokens |" % f"{cfg['context_window_tokens']:,}")
    a("")

    a("## Recommended architecture: %s" % ARCH_TITLE[res["architecture"]])
    a("")
    a("Driven by:")
    a("")
    for r in res["architecture_reasons"]:
        a("- %s" % r)
    a("")
    a("```")
    a(_ascii_arch(res["architecture"], cfg))
    a("```")
    a("")

    a("## Components")
    a("")
    a("| Component | Purpose |")
    a("|---|---|")
    for name, purpose in res["persistence"]:
        a("| %s | %s |" % (name, purpose))
    a("")

    a("## Retrieval strategy")
    a("")
    a("**%s**" % res["retrieval"])
    a("")
    a(res["retrieval_why"])
    a("")
    a("Ranking blend to start from (tune against a labeled set, not by feel):")
    a("")
    a("```python")
    a("score = 0.55 * relevance + 0.25 * recency + 0.15 * importance")
    a("        + 1.00 * pinned          # pin is an escape hatch, not a score")
    a("```")
    a("")
    a("Always inject, outside the ranking: the pinned constraint set and the "
      "last 2-4 turns, so continuity survives a bad similarity result.")
    a("")

    a("## Summarization")
    a("")
    a("**%s**" % res["summarization"])
    a("")
    a(res["summarization_why"])
    a("")

    a("## Context budget")
    a("")
    a("| Segment | Share of window |")
    a("|---|---|")
    for seg, pct in res["budget"]:
        a("| %s | %d%% |" % (seg, pct))
    a("")
    a("At %s tokens that is roughly %s tokens for retrieved memory."
      % (f"{cfg['context_window_tokens']:,}",
         f"{cfg['context_window_tokens'] * res['budget'][1][1] // 100:,}"))
    a("")

    a("## Consolidation policy")
    a("")
    for i, step in enumerate(res["consolidation"], 1):
        a("%d. %s" % (i, step))
    a("")

    a("## State management")
    a("")
    if cfg["workflow_resumption"]:
        a("Persist workflow state at every step boundary and **before** any "
          "irreversible action, as a self-sufficient checkpoint: plan, cursor, "
          "accumulated results, and the list of completed effects.")
        a("")
        a("```json")
        a(json.dumps({
            "run_id": "run_xxxx",
            "step": "current_step",
            "attempts": {"current_step": 1},
            "completed_effects": ["effect_type:external_id"],
            "cursor": {"record_id": "..."},
        }, indent=2))
        a("```")
        a("")
        a("Resume by skipping completed effects, not by replaying from step 1.")
    elif cfg["persistence_required"]:
        a("Durable session row keyed by `session_id`: compacted history, the "
          "append-only facts ledger, and the current plan. Write on every turn "
          "that changes a decision; batch pure chatter.")
    else:
        a("Working memory only. Keep a structured scratchpad (goal, plan, facts, "
          "open questions) instead of an ever-growing message list.")
    a("")

    a("## Cost expectations")
    a("")
    for line in res["cost"]:
        a("- %s" % line)
    a("")

    a("## Tradeoffs accepted")
    a("")
    for name, text in ARCH_TRADEOFFS[res["architecture"]]:
        a("- **%s** — %s" % (name, text))
    a("")

    a("## Risks and mitigations")
    a("")
    a("| Risk | Mitigation |")
    a("|---|---|")
    for risk, fix in res["risks"]:
        a("| %s | %s |" % (risk, fix))
    a("")

    a("## First three things to build")
    a("")
    for i, item in enumerate(_first_steps(cfg, res), 1):
        a("%d. %s" % (i, item))
    a("")
    a("---")
    a("Generated by memory_architect.py v%s. Heuristic guidance, not a "
      "substitute for load testing your own traffic." % VERSION)
    return "\n".join(L) + "\n"


def _yn(v: bool) -> str:
    return "yes" if v else "no"


ARCH_TRADEOFFS: Dict[str, List[Tuple[str, str]]] = {
    "single-store": [
        ("Simplicity", "one service, one schema, one thing to debug."),
        ("Ceiling", "cannot express priority across memory classes; a stale "
                    "document scores the same as a fresh user correction."),
        ("Migration cost", "adding a second store later means backfilling and "
                           "reconciling — cheap now, expensive at 10x data."),
    ],
    "dual-store": [
        ("Clarity", "the working/long-term boundary forces an explicit "
                    "promotion policy, which is where most memory bugs hide."),
        ("Cost", "one summarization pass and one retrieval pass per turn."),
        ("Two consistency surfaces", "the summary can drift from the store; a "
                                     "facts ledger plus source pointers keeps "
                                     "them reconcilable."),
    ],
    "hierarchical": [
        ("Scalability", "each tier is sized and paid for independently; hot "
                        "data stays fast, cold data stays cheap."),
        ("Tuning burden", "promotion/demotion thresholds are a second system to "
                          "tune, and a bad threshold silently degrades recall."),
        ("Operational surface", "more services means more failure modes; each "
                                "tier needs its own health check and fallback."),
    ],
    "distributed": [
        ("Concurrency", "agents can work in parallel and share findings."),
        ("Conflict risk", "without per-key ownership two agents write "
                          "contradictory state; ownership rules are mandatory."),
        ("Debugging", "causality spans processes; you need a correlation id on "
                      "every read and write or you cannot explain an outcome."),
    ],
}


def _ascii_arch(arch: str, cfg: Dict[str, Any]) -> str:
    if arch == "single-store":
        return (
            "  turns/tools ──▶ [ single store ] ──▶ top-k ──▶ context\n"
            "                   (vector or table)"
        )
    if arch == "dual-store":
        return (
            "  turns ──▶ ┌──────────────────┐ ◀── retrieve ──┐\n"
            "            │ working memory   │                │\n"
            "            │ (context window) │                │\n"
            "            └────────┬─────────┘                │\n"
            "                     │ compact / promote        │\n"
            "                     ▼                          │\n"
            "            ┌──────────────────┐        ┌────────┴────────┐\n"
            "            │ summarizer       │───────▶│ long-term store │\n"
            "            └──────────────────┘  write │ + facts ledger  │\n"
            "                                           └─────────────────┘"
        )
    if arch == "hierarchical":
        return (
            "  L0 context window   ~%dk tok   ns      (free-ish)\n"
            "  L1 session cache    ~1M tok    ms      (cheap)\n"
            "  L2 vector store     ~%s chunks ~50ms   (per-query)\n"
            "  L3 archive          unbounded  seconds (cheapest)\n"
            "\n"
            "  promotion: importance + access count, demotion: age + never-read"
            % (max(4, cfg["context_window_tokens"] // 1000),
               {"none": "0", "small": "10k", "medium": "500k",
                "large": "2M"}[cfg["corpus_size"]])
        )
    return (
        "  agent A ──┐                    ┌──▶ agent C\n"
        "            ├──▶ [ event bus ] ──┤\n"
        "  agent B ──┘         │          └──▶ agent D\n"
        "                      ▼\n"
        "            [ shared state view ]  (single reducer, per-key owner)"
    )


def _first_steps(cfg: Dict[str, Any], res: Dict[str, Any]) -> List[str]:
    steps: List[str] = []
    if cfg["workflow_resumption"]:
        steps.append(
            "Write the workflow-state table and effect log first — resumption "
            "correctness is the hardest thing to retrofit."
        )
    if CORPUS_RANK[cfg["corpus_size"]] >= 1:
        steps.append(
            "Build a 50-query labeled retrieval set before writing the index; "
            "you cannot tune chunking or embeddings without it."
        )
        steps.append(
            "Implement retrieval with tenant/date filters enforced in code, then "
            "measure recall@10 against exact search."
        )
    else:
        steps.append(
            "Define the structured working-memory schema (goal, plan, facts, "
            "open questions, pinned constraints) before writing retrieval."
        )
    steps.append(
        "Add the facts ledger and pin handling, then run a forced-compaction "
        "test asserting that constraints and identifiers survive."
    )
    steps.append(
        "Instrument cost per session and p95 retrieval latency; set the budget "
        "guardrails before traffic, not after the bill."
    )
    return steps[:3]


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

SELF_TEST_CASES: List[Tuple[str, Dict[str, Any], str, str]] = [
    (
        "Stateless classifier: short, no corpus, no persistence",
        {
            "conversation_length": "short",
            "concurrent_users": 5,
            "data_types": ["chat"],
            "corpus_size": "none",
            "persistence_required": False,
            "budget": "low",
        },
        "single-store",
        "last-N turns (no retrieval)",
    ),
    (
        "Support assistant over a medium policy corpus",
        {
            "conversation_length": "medium",
            "concurrent_users": 400,
            "data_types": ["chat", "documents"],
            "corpus_size": "medium",
            "persistence_required": True,
            "multi_tenant": True,
            "budget": "medium",
        },
        "dual-store",
        "hybrid + cross-encoder rerank",
    ),
    (
        "Long-lived personal assistant with unbounded history",
        {
            "conversation_length": "unbounded",
            "concurrent_users": 1200,
            "data_types": ["chat", "documents"],
            "corpus_size": "large",
            "persistence_required": True,
            "budget": "high",
        },
        "hierarchical",
        "hybrid + cross-encoder rerank",
    ),
    (
        "Multi-agent research pipeline with resumable workflows",
        {
            "conversation_length": "long",
            "concurrent_users": 40,
            "data_types": ["chat", "documents", "structured_records"],
            "corpus_size": "small",
            "persistence_required": True,
            "workflow_resumption": True,
            "multi_agent": True,
            "compliance_audit": True,
            "budget": "high",
        },
        "distributed",
        "hybrid (dense + BM25) without rerank",
    ),
    (
        "Coding agent over a repo",
        {
            "conversation_length": "long",
            "concurrent_users": 50,
            "data_types": ["code", "chat"],
            "corpus_size": "medium",
            "persistence_required": True,
            "budget": "medium",
        },
        "dual-store",
        "hybrid + cross-encoder rerank",
    ),
]

BAD_CONFIGS: List[Tuple[str, Dict[str, Any], str]] = [
    ("unknown key", {"conversation_length": "short", "wibble": 1}, "unknown key"),
    ("bad enum", {"conversation_length": "forever"}, "must be one of"),
    ("bool as int", {"concurrent_users": True}, "must be an integer"),
    ("empty data_types", {"data_types": []}, "must not be empty"),
    (
        "documents without corpus",
        {"data_types": ["documents"], "corpus_size": "none"},
        "corpus_size",
    ),
    (
        "multi-agent on low budget",
        {"multi_agent": True, "budget": "low"},
        "not realistic",
    ),
    (
        "impossible latency on large corpus",
        {"corpus_size": "large", "latency_target_ms": 100},
        "150ms",
    ),
    ("context too small", {"context_window_tokens": 1000}, ">= 4000"),
]


def self_test() -> int:
    """Run built-in cases. Returns process exit code."""
    failures: List[str] = []
    failed_cases: set = set()
    checks = 0

    def fail(case: str, msg: str) -> None:
        failures.append("%s: %s" % (case, msg))
        failed_cases.add(case)

    for name, raw, want_arch, want_retrieval in SELF_TEST_CASES:
        try:
            cfg = validate_config(raw)
            res = analyse(cfg)
        except ConfigError as e:  # pragma: no cover
            fail(name, "unexpected ConfigError: %s" % e)
            continue
        checks += 1
        if res["architecture"] != want_arch:
            fail(name, "architecture %r != expected %r"
                 % (res["architecture"], want_arch))
        checks += 1
        if res["retrieval"] != want_retrieval:
            fail(name, "retrieval %r != expected %r"
                 % (res["retrieval"], want_retrieval))

        # Invariants that must hold for every valid profile
        checks += 1
        if sum(p for _, p in res["budget"]) != 100:
            fail(name, "context budget does not sum to 100")
        checks += 1
        if not res["persistence"]:
            fail(name, "empty persistence plan")
        checks += 1
        if not res["risks"]:
            fail(name, "empty risk list")

        # Renderer must produce non-trivial markdown without raising
        checks += 1
        md = render(cfg, res)
        if len(md) < 800 or "## Recommended architecture" not in md:
            fail(name, "rendered output too small or malformed")
        checks += 1
        if "\t" in md:
            fail(name, "output contains a tab character")

    for name, raw, needle in BAD_CONFIGS:
        checks += 1
        try:
            validate_config(raw)
        except ConfigError as e:
            if needle.lower() not in str(e).lower():
                fail(name, "error %r does not mention %r" % (str(e), needle))
        else:
            fail(name, "invalid config was accepted")

    # --print-schema output must round-trip back through the parser
    checks += 1
    buf = io.StringIO()
    _stdout, sys.stdout = sys.stdout, buf
    try:
        print_schema()
    finally:
        sys.stdout = _stdout
    try:
        validate_config(parse_config_text(buf.getvalue()))
    except (ConfigError, json.JSONDecodeError) as e:
        fail("print-schema round-trip", str(e))

    # Defaults must be usable
    checks += 1
    try:
        cfg = validate_config({})
        analyse(cfg)
    except ConfigError as e:  # pragma: no cover
        fail("defaults", str(e))

    total = len(SELF_TEST_CASES) + len(BAD_CONFIGS) + 2  # + defaults, print-schema round-trip
    print("memory_architect.py v%s self-test" % VERSION)
    print("-" * 52)
    print("profiles checked : %d" % len(SELF_TEST_CASES))
    print("invalid configs  : %d" % len(BAD_CONFIGS))
    print("assertions       : %d" % checks)
    print("cases passed     : %d/%d" % (total - len(failed_cases), total))
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("\nOK - all cases passed")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="memory_architect.py",
        description=(
            "Recommend an AI agent memory architecture from a JSON requirement "
            "profile. Emits markdown covering architecture tier, retrieval, "
            "persistence, context budget, consolidation, cost, and risks."
        ),
        epilog=(
            "examples:\n"
            "  python3 memory_architect.py --config req.json\n"
            "  python3 memory_architect.py --config req.json --out rec.md\n"
            "  python3 memory_architect.py --print-schema > req.json\n"
            "  python3 memory_architect.py --self-test\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--config", metavar="PATH",
                   help="path to a JSON requirement profile ('-' for stdin)")
    p.add_argument("--out", metavar="PATH",
                   help="write markdown here instead of stdout")
    p.add_argument("--print-schema", action="store_true",
                   help="print the config schema and an example profile, then exit")
    p.add_argument("--self-test", action="store_true",
                   help="run built-in demo cases and validation checks")
    p.add_argument("--json", action="store_true",
                   help="emit the structured analysis as JSON instead of markdown")
    p.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    return p


def print_schema() -> None:
    example = {k: v["default"] for k, v in SCHEMA.items()}
    print("# memory_architect.py config schema (v%s)" % VERSION)
    print("#")
    for key, spec in SCHEMA.items():
        print("# %-22s %s" % (key, spec["help"]))
        if spec["type"] == "enum":
            print("# %-22s one of: %s" % ("", " | ".join(spec["values"])))
        print("# %-22s type: %s, default: %s"
              % ("", spec["type"], json.dumps(spec["default"])))
    print()
    print(json.dumps(example, indent=2))


def parse_config_text(raw: str) -> Any:
    """Parse JSON, tolerating full-line '#' comments (JSONC-lite).

    Raises json.JSONDecodeError if the text is not recoverable.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        stripped = "\n".join(
            ln for ln in raw.splitlines() if not ln.lstrip().startswith("#")
        )
        return json.loads(stripped)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.self_test:
        return self_test()
    if args.print_schema:
        print_schema()
        return 0
    if not args.config:
        build_parser().print_help(sys.stderr)
        print("\nerror: --config, --print-schema, or --self-test is required",
              file=sys.stderr)
        return 2

    try:
        if args.config == "-":
            raw = sys.stdin.read()
        else:
            if not os.path.exists(args.config):
                print("error: config file not found: %s" % args.config,
                      file=sys.stderr)
                return 2
            with open(args.config, "r", encoding="utf-8") as f:
                raw = f.read()
    except OSError as e:
        print("error: cannot read config: %s" % e, file=sys.stderr)
        return 2

    try:
        data = parse_config_text(raw)
    except json.JSONDecodeError as e:
        print("error: invalid JSON in %s: %s (line %d, column %d)"
              % (args.config, e.msg, e.lineno, e.colno), file=sys.stderr)
        return 2

    try:
        cfg = validate_config(data)
    except ConfigError as e:
        print("error: invalid config: %s" % e, file=sys.stderr)
        print("hint: run --print-schema to see valid keys and values",
              file=sys.stderr)
        return 2

    res = analyse(cfg)
    output = json.dumps({"config": cfg, "analysis": res}, indent=2) \
        if args.json else render(cfg, res)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(output)
        except OSError as e:
            print("error: cannot write %s: %s" % (args.out, e), file=sys.stderr)
            return 2
        print("wrote %s (%d bytes)" % (args.out, len(output)))
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
