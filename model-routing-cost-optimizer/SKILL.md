---
name: model-routing-cost-optimizer
description: Use when routing tasks to the cheapest fitting model tier.
version: 1.0.0
license: MIT
author: Skill Foundry
platforms:
  - linux
  - macos
metadata:
  tags:
    - model-routing
    - cost-optimization
    - model-tiering
    - llm-cost
    - subagent-routing
    - provider-agnostic
  complexity_level: intermediate
  similar_skills:
    - model-hierarchy
  related_workflows:
    - classify_task_complexity
    - select_cost_appropriate_model
    - avoid_routing_anti_patterns
---

# Model Routing Cost Optimizer

Route every agent task to the cheapest model that can still do it well. This skill
establishes a three-tier model hierarchy (cheap / mid / premium), a task classifier
that buckets work into ROUTINE / MODERATE / COMPLEX, and the decision rules that
turn a description into a model pick. It does not enforce any one provider — the
tier prices live in `references/model-pricing.md` so the body stays provider-
neutral — and it does not cover local quantized inference.

The core belief is blunt: most agent work is routine, and routing routine work to a
premium model is pure waste. Down-tier by default; escalate on evidence, never on
habit.

## When to Use

Use this skill when you want to:

- Choose which model should handle a task, a sub-agent, or a cron job.
- Decide whether the current model is overkill for what you are about to run.
- Spawn sub-agents at a cost that matches the work.
- Keep heartbeat, monitoring, and scheduled-report traffic off premium models.
- Explain to a teammate why one model is running a task instead of another.
- Classify a batch of tasks into ROUTINE / MODERATE / COMPLEX for tiering.

**Don't use for**: fine-tuning a model, model evaluation or benchmarking, serving
infrastructure (vLLM / TGI), or any task where correctness risk is high and you
need the best possible reasoning regardless of price. If the work is irrecoverable
or safety-critical, stop tiering and use the premium model.

## Prerequisites

- Visibility into the models your agent or gateway exposes (OpenRouter catalog,
  a provider console, or the `model` config of OpenClaw / Claude Code / Codex).
- No secret is required to operate this skill; the pricing table in
  `references/model-pricing.md` is illustrative, so refresh it against provider
  docs before relying on a number.
- If you run the classifier, `scripts/classify_task.py` is stdlib-only.

## Decision Rules (read these before you pick a model)

- **Rule 1 — vision.** If the task needs images (screenshots, photos, charts,
  image generation), pick a *vision-capable* model. Never route vision work to a
  text-only model just because it is the cheap tier — the cheapest viable model is
  the cheapest one that can actually see.
- **Rule 2 — escalation.** If a cheaper model already failed the same task, move
  one tier up, not down; re-trying the same failed tier burns more than one upgrade.
- **Rule 3 — explicit signals.** Complex words like `debug`, `architect`,
  `design`, `security`, `adversarial`, `ambiguous` push to Tier 3. Routine words
  like `read`, `fetch`, `check`, `format`, `status`, `list` push to Tier 1.
- **Rule 4 — classify by default.** Otherwise classify the task with the procedure
  and pick the tier that matches.

## Task Classification

| Bucket | Heuristic | Typical Examples |
|---|---|---|
| ROUTINE → Tier 1 | Single-step, deterministic, no judgment | file I/O, heartbeat, status check, lookup, formatting, URL fetch |
| MODERATE → Tier 2 | Multi-step but well-scoped | code-gen on known patterns, summarization, draft writing, data transforms |
| COMPLEX → Tier 3 | Ambiguous, multi-approach, high-stakes | multi-step debugging, architecture, security review, long-context reasoning |

## Quick Reference

| Concern | Move |
|---|---|
| Task is routine | Tier 1 |
| Task is moderate | Tier 2 |
| Task needs image / vision | vision-capable model (never a text-only tier-1) |
| Task already failed on cheap | move up (escalation), never down |
| Heartbeat / cron / monitoring | always Tier 1 |
| Sub-agent spawn | default Tier 1 unless clearly moderate+ |

## Procedure

Each step ends with a checkable completion criterion.

1. **State the task.** Write the task in one line, including whether it needs
   images and whether a cheaper model already tried.
   *Completion: you have a task statement with its vision and prior-failure flags.*

2. **Classify.** Run `python3 scripts/classify_task.py "<task>"` in the terminal,
   or read the bucket heuristics above by hand.
   *Completion: you have a label of `ROUTINE`, `MODERATE`, or `COMPLEX`.*

3. **Apply the vision override.** If the task is vision-requiring, restrict the
   model choice to vision-capable options, ignoring any text-only option entirely —
   a text-only model cannot take image input at any price.
   *Completion: the chosen model can actually accept image input.*

4. **Apply escalation and signal overrides.** If a prior failure exists, go one
   tier *up* from the classifier result. If explicit complex signals appear, go to
   Tier 3.
   *Completion: the final tier is never lower than the classifier would have
   produced.*

5. **Name a concrete model.** From the provider's resolvable list, pick the
   cheapest model of the final tier that meets that tier's bar.
   *Completion: you can name a concrete model, or a route to find one.*

6. **Run the anti-pattern sweep.** If this is a sub-agent, heartbeat, cron, file
   I/O, or routine batch, drop it to Tier 1 unless the classifier returned
   MODERATE or above.
   *Completion: no heartbeat/cron work remains on a premium tier.*

## Anti-Patterns

- **Feeding heartbeats / cron to premium models.** A two-token status ping on a
  flagship model is pure waste.
- **Spawning sub-agents at the parent's tier.** Daemon children should be one tier
  down unless the work is provably complex.
- **Refusing to upgrade when stuck.** A cheap model that already failed costs more
  if you keep retrying it; one step up is the cheaper path.
- **Routing vision to a text-only model.** GLM-5 (and other cheap text-only tier-1/2
  models) must never see image input. Send vision to a vision-capable model.
- **Tiering on habit.** Do not stay on a new flagship model just because it is the
  default; escalate on evidence only.

## Verification

- The classifier `scripts/classify_task.py` returns Tier 1 for a routine phrase,
  Tier 2 for a moderate phrase, and Tier 3 for a complex phrase.
- A vision phrase (screenshot / photo / chart) routes to a vision-capable model,
  and a text-only model is never selected for it.
- A failed-task phrase routes one tier *up* from baseline, never down.
- The heartbeat / cron phrase never lands on a premium tier.
- `references/model-pricing.md` exists and contains the pricing table and the
  "prices change, check provider docs" caveat.