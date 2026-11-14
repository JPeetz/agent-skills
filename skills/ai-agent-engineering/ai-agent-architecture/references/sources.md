# Sources

Reference material behind this skill. Primary sources (vendor engineering write-ups, specs, standards) take precedence over secondary summaries; every claim about a topology's trade-offs is grounded in at least one of the entries below or in observed production behaviour.

## Upstream collections and the source family

- **github/awesome-copilot** — https://github.com/github/awesome-copilot (MIT)
  Community-contributed instructions, agents, and skills for GitHub Copilot. Source of the agent/instruction packaging conventions this skill follows (frontmatter shape, `description` as the trigger contract, platform list), plus several agent definitions whose structure informed the topology section. MIT-licensed; no text is copied verbatim — the patterns were re-derived and generalised.
- **o11y / agent-architecture source family** — the agent-architecture and agent-observability material curated alongside the `o11y` skill collection (agent span modelling, task/step hierarchy, cost attribution). Source for the observability dimension of the audit framework — one trace per task, one span per step, outcome recorded alongside activity — and for treating cost as an architectural property rather than a billing afterthought.
- **Observability Engineering** (Majors, Fong-Jones, Miranda), O'Reilly — https://www.oreilly.com/library/view/observability-engineering/9781492076438/
  The argument that you cannot debug what you instrumented as an afterthought; basis for making traces a design-step deliverable rather than a post-launch task.

## Agent design patterns

- Anthropic, "Building effective agents" — https://www.anthropic.com/engineering/building-effective-agents
  The workflow-vs-agent distinction, the prompt-chaining / routing / orchestrator-workers / evaluator-optimizer patterns, and the standing advice to prefer the simplest structure that works. Basis for "most systems that need multi-agent are one agent with a bad tool contract".
- OpenAI, "A practical guide to building agents" — https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
  Guardrails layering (relevant vs. LLM vs. rule-based), single-agent-first guidance, and human-in-the-loop escalation design. Basis for the human-gate and blast-radius checks.
- Google, "Agent2Agent (A2A) Protocol" — https://a2a-protocol.org/
  Agent-to-agent interoperability: capability discovery, task lifecycle states, and message/artifact separation. Basis for the typed-envelope rule and for treating cross-agent calls as a versioned contract.
- Model Context Protocol specification — https://modelcontextprotocol.io/specification
  Tool definition and invocation semantics, including the separation of tool schema from description. Basis for "tool descriptions are contracts" and "separate tools over a god tool with a mode parameter".
- Microsoft Azure Architecture Center, "AI agent orchestration patterns" — https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
  Independent side-by-side catalogue of sequential, concurrent, group-chat, handoff, and magnetic orchestration patterns. Used as a cross-check that the five topologies here map onto an independently maintained taxonomy.

## Distributed-systems foundations applied to agents

- Martin Kleppmann, *Designing Data-Intensive Applications*, O'Reilly — https://dataintensive.net/
  Partial failure, idempotency, retries, and exactly-once illusion. Basis for the idempotency-key requirement on every side-effecting tool and for "retry without idempotency" as an anti-pattern.
- Google SRE Book, "Addressing Cascading Failures" and "Handling Overload" — https://sre.google/sre-book/table-of-contents/
  Timeout budgets, retry amplification, and load shedding. Basis for the compounding-timeout rule and for enforced rather than monitored budgets.
- Pat Helland, "Idempotence Is Not a Medical Condition" — https://dl.acm.org/doi/10.1145/2180927.2180932
  Why "exactly once" is achieved by making effects idempotent, not by retrying cleverly.
- Michael Nygard, "Documenting Architecture Decisions" — https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
  The original ADR format: context, decision, consequences, status. This skill adds rejected alternatives and reopening signals as required fields.

## Evaluation and measurement

- OpenTelemetry, GenAI semantic conventions — agent spans — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
  Attribute names for agent, tool, and model spans (`gen_ai.agent.name`, `gen_ai.tool.name`, token usage). Basis for making spans portable across vendors rather than bespoke logs.
- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023) — https://arxiv.org/abs/2306.05685
  Where model-based grading is reliable and where position/verbosity bias bites; basis for requiring checkable expectations and warning against rubric grading without calibration.
- Liu et al., "AgentBench: Evaluating LLMs as Agents" (2023) — https://arxiv.org/abs/2308.03688
  Multi-environment agent evaluation and the observation that trajectory quality diverges from final-answer quality.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022) — https://arxiv.org/abs/2210.03629
  The observe → reason → act loop that the single-agent pattern formalises.
- "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., 2023) — https://arxiv.org/abs/2307.03172
  Evidence behind "context as memory" as an anti-pattern: quality degrades with position and length, so durable state plus retrieval beats unbounded accumulation.

## Security

- OWASP, "Top 10 for Large Language Model Applications" — https://owasp.org/www-project-top-10-for-large-language-model-applications/
  LLM01 prompt injection, LLM06 excessive agency, LLM08 vector weaknesses. Basis for the security dimension's least-privilege, untrusted-input, and privilege-escalation checks.
- NIST AI Risk Management Framework (AI RMF 1.0) — https://www.nist.gov/itl/ai-risk-management-framework
  Govern / map / measure / manage structure; basis for requiring a named owner and a measurable success criterion per agent.
- Simon Willison, "The Dual LLM pattern" — https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
  Why untrusted content must not share an instruction channel with privileged capability. Basis for the "untrusted input is never an instruction" audit item.

## Adjacent skills in this repo

- `skills/ai-agent-engineering/*` — the category this skill opens. Sibling skills own prompt authoring, evaluation harness implementation, and threat modelling in depth.
- `skills/devops-infrastructure/observability-engineering` — instrumentation depth: metrics, logs, traces, SLOs. Boundary: that skill builds the telemetry pipeline; this one decides what an agent must emit.
- `skills/security/threat-modeling` — structured attack-surface analysis. Boundary: that skill enumerates threats; this one checks whether the architecture can be attacked structurally at all.
- `skills/business-strategy/app-discovery-scrutiny` — questioning whether a product should exist. Boundary: this skill assumes the agent is wanted and asks whether it is built correctly.
