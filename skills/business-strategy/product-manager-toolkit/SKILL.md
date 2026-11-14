---
name: product-manager-toolkit
description: >-
  Use this skill when performing product management tasks like prioritizing
  features, synthesizing customer interviews, writing PRDs, setting OKRs, or
  managing stakeholder communication. Activates on "product management", "PM
  toolkit", "prioritization", "RICE", "PRD", "feature prioritization",
  "customer interview", "OKR planning", "stakeholder update", or "roadmap
  planning". Covers RICE prioritization, customer interview synthesis, PRD
  authoring, OKR setting with leading/lagging indicators, stakeholder
  communication templates, and decision frameworks.
version: 1.0.0
author: Skill Foundry
license: MIT
category: business-strategy
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - product-management
  - prioritization
  - RICE
  - PRD
  - OKR
  - strategy
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
    - product-management
    - prioritization
    - PRD
    - OKR
    - RICE
    - stakeholder
  related_skills:
    - go-to-market-launch
    - linear-project-management
    - pricing-strategist
---

# Product Manager Toolkit

Product management is a **decision discipline**, not a document factory. This skill produces the four artifacts a PM is actually judged on: a ranked backlog that survives an engineering argument, a synthesis of customer evidence that a designer and an exec both accept, a PRD that bounds scope, and OKRs that do not become a wishlist. Each artifact ends in a decision — what we do, what we refuse, and how we will know.

The rule throughout: **every claim is traceable to an input** (a quote, a metric, a stated strategy). Untraceable claims are opinions, and opinions are labeled as such.

## When to Use

- Ranking a backlog where everything is "P0" and the loudest stakeholder wins by default
- Turning 8–30 raw customer interviews into themes with evidence, not a summary of anecdotes
- Writing a PRD that engineering can estimate and QA can test without asking you what "fast" means
- Setting quarterly OKRs that are not a list of projects with percentages attached
- Preparing a stakeholder update where bad news needs to travel without panic
- Choosing between DACI, DARE, RICE and opportunity scoring for a specific stuck decision

## Do Not Use For

| Need | Use instead |
|------|-------------|
| Launch plan, channels, Product Hunt / HN runbook | `go-to-market-launch` |
| Setting the price or packaging tiers | `pricing-strategist` |
| Sprint mechanics, issue templates, cycle tracking | `linear-project-management` |
| Whether the idea is worth pursuing at all | `app-discovery-scrutiny` |
| Consulting engagement structure, workshop facilitation | `enterprise-consulting-methods` |

---

## 1. RICE Prioritization

**RICE = (Reach × Impact × Confidence) / Effort.** It exists to force four separate arguments onto four separate axes so a big number cannot hide a weak assumption.

| Factor | Unit | Question it answers | Typical scale |
|--------|------|---------------------|---------------|
| **Reach** | users / quarter | How many people does this touch in a fixed period? | Absolute count — never a 1–5 score |
| **Impact** | multiplier | How much does it move each of them? | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| **Confidence** | % | How sure are we about reach and impact? | 100% data, 80% strong signal, 50% anecdote, 20% hunch |
| **Effort** | person-weeks | Total cost to ship and support | Absolute estimate, one unit for the whole team |

### Rules that keep RICE honest

- **Reach is counted, not scored.** "5 out of 5" is meaningless; "1,400 accounts per quarter" is arguable.
- **Confidence is the honesty dial.** A 20%-confidence item with a huge score is a research task, not a build task. Cap unsupported items at 50% and say so.
- **Effort uses one consistent unit.** Mixing designer-days with engineer-weeks silently reorders the list.
- **Never compare scores across quarters** without re-basing reach and effort. The numbers are relative within one cycle.
- **RICE ranks; it does not decide.** Strategy, dependencies, and reversibility override the ranking — record why.
- **Show the inputs, not just the score.** A score with no visible inputs gets argued with; a table of inputs gets corrected, which is the point.

The calculator: `scripts/rice_scorer.py` reads a JSON file of items and emits a ranked table with each factor visible, plus flags for low confidence and outlier effort. See `--help`.

```bash
python3 scripts/rice_scorer.py features.json               # ranked markdown table
python3 scripts/rice_scorer.py features.json --output json # machine-readable
python3 scripts/rice_scorer.py --help                      # input schema
```

Use it whenever there are **more than five candidates** or when the ranking will be shown to someone who will challenge it. Below five, the table is faster than the script.

### Input shape

```json
{
  "cycle": "2026-Q1",
  "items": [
    {
      "name": "Bulk CSV import",
      "reach": 1400,
      "impact": 2,
      "confidence": 0.8,
      "effort": 6,
      "notes": "from 12 support tickets + 3 interviews"
    }
  ]
}
```

`impact` accepts `3 | 2 | 1 | 0.5 | 0.25`; `confidence` accepts `0–1` or `0–100`; `effort` must be `> 0`. The script rejects rather than silently coercing bad input.

---

## 2. Customer Interview Synthesis

Goal: convert raw transcripts into **defensible themes**, each with a count, a severity, and verbatim evidence. A synthesis that cannot be traced back to quotes is a summary, and summaries drift toward what the team already believed.

### Step 1 — Decompose before you theme

Read every transcript once and extract atomic observations into a flat list. One observation = one behavior, pain, workaround, or quote. Strip interviewer questions; keep only what the customer did or said.

Tag each observation with: `participant_id`, `segment`, `job_step` (what they were trying to do), and `type` (`pain | workaround | goal | trigger | objection`).

### Step 2 — Affinity mapping

Cluster observations bottom-up — by what people *did*, not by what topic they mentioned.

- Sort by `job_step` first, then cluster within each step. Mixing steps produces themes like "reporting" that mean nothing.
- Name each cluster with the **behavior**, not the noun: "rebuilds the same export in Excel weekly" beats "reporting pain".
- A cluster needs **≥3 distinct participants** to be a theme. Below that it is a signal, listed separately.
- Keep a "counter-evidence" cluster. If every theme confirms the roadmap, the interview guide was leading.

### Step 3 — Score each theme

| Field | Meaning |
|-------|---------|
| Participants | distinct people, not mentions |
| Segment skew | which segments dominate; a theme from 3 of 3 enterprise users is not a market theme |
| Severity | blocks work / costs time weekly / annoying / cosmetic |
| Current workaround | what they do today — the real competitor |
| Willingness signal | did they ask for it, build it, or pay for it? |

### Step 4 — Write the output

```
TL;DR — three sentences. What we heard, what surprised us, what we recommend.

THEMES (ranked by participants × severity)
1. <behavior-named theme> — 11/24 participants, 3 segments
   Evidence: "…" (P04, enterprise ops), "…" (P17, mid-market)
   Workaround today: …
   Implication: …
SIGNALS (below threshold) — 4 items, one line each.
COUNTER-EVIDENCE — what contradicted the top themes.
WHAT WE DID NOT LEARN — questions still open, who to interview next.
```

### Interview hygiene

- **Ask about past behavior, never hypotheticals.** "Walk me through the last time…" beats "would you use…".
- **Never pitch.** If you describe the solution, the rest of the interview is politeness.
- **Silence is a tool.** Count three seconds before filling a pause.
- **Recruit for variance**, not for confirmation: at least one churned user and one non-user per study.
- **Stop when themes saturate** — usually 8–12 interviews per segment; more only adds confidence, not new themes.

---

## 3. PRD Template

A PRD is a **scope contract**. It is done when engineering can estimate it, design can sketch it, QA can test it, and a new hire can explain why it exists without you in the room.

Length target: 2–4 pages. Longer PRDs are read by nobody and treated as cover for unclear thinking.

### 1. Problem & Vision

- **Problem statement** — one paragraph: who, in what situation, what breaks, what it costs them. Cite evidence (interview IDs, ticket counts, metric).
- **Vision** — one sentence describing the world after this ships. No features in it.
- **Why now** — the forcing function. If there isn't one, say "no forcing function" and let priority be argued on RICE.

### 2. Personas & Jobs

| Persona | Job to be done | Today's workaround | Success looks like |
|---------|----------------|--------------------|--------------------|
| | | | |

Limit to two personas. A PRD with five personas has no primary user, which means design will optimize for the loudest internal advocate.

### 3. Requirements

Split explicitly — the split *is* the scope decision.

- **Must have (v1):** without these the problem is not solved. Each one testable.
- **Should have (v1.x):** the obvious next increment; designed for, not built.
- **Won't have (this time):** named and dated. This section prevents 80% of scope-creep arguments.
- **Open questions:** with an owner and a decide-by date.

Each requirement: `R1 — As a <persona>, I can <action> so that <outcome>. Acceptance: <observable check>.`

### 4. Success Criteria

- **Primary metric:** one, with baseline, target, and measurement window.
- **Guardrail metrics:** what must not get worse (latency, support volume, churn).
- **Kill criteria:** the result that means we stop investing. Written before launch.

### 5. Scope & Non-Goals

Explicitly list adjacent problems this will *not* solve, especially the ones stakeholders assume are included. Then: dependencies, rollout plan (flag? cohort? GA?), and the owner of each external dependency.

### 6. Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|

Include the risk nobody writes down: *the PRD solves a problem the team has stopped caring about.*

---

## 4. OKR Design

An OKR set is a **falsifiable bet**, not a project list. If every KR is "ship X by date Y," you have written a roadmap with percentages.

### Objectives

- 1–3 per team per quarter. Qualitative, inspirational, and *directional* — no numbers.
- Must be uncomfortable. An objective you are certain to hit is a status update.
- Test: could a reasonable person disagree that this is the most important thing? If not, it is too safe.

### Key Results

Each objective gets 2–4 KRs. Each KR must have a **baseline, a target, and a date**, and must measure an *outcome*, not an output.

| Type | Definition | Role | Example |
|------|------------|------|---------|
| **Lagging** | The result you ultimately want; moves slowly, confirms after the fact | At least one per objective — it is the truth test | "Weekly active teams: 1,800 → 2,600 by Mar 31" |
| **Leading** | An early input you can influence this week; predicts the lagging KR | 1–3 per objective — these are what the team works on | "New teams completing setup in <24h: 41% → 65%" |

Rules:

- **Output KRs are banned.** "Ship the new onboarding" is a task. "Activation rate 34% → 50%" is a KR that the task might achieve.
- **Baseline is mandatory.** A KR without a starting number cannot be scored.
- **Confidence rating per KR:** `high / medium / low` *at the start of the quarter*, plus the assumption that would break it. A set where every KR is "high" was written backwards from a plan.
- **Score 0–1 at quarter end**, and grade honestly: 0.7 is a good quarter for a stretch set. Hitting 1.0 everywhere means the targets were sandbagged.
- **KRs are not shared across teams as commitments.** A KR owned by two teams is owned by neither.

### Writing a KR — the checklist

1. Does it have a number and a baseline?
2. Would it move if the team did nothing but also shipped nothing? (If it moves on its own, it is a market metric — fine as context, weak as a KR.)
3. Is it influenceable by this team this quarter?
4. Is the data available at the cadence you will check it?
5. Would scoring it honestly require a difficult conversation? If not, it is not a stretch.

### Cadence

Weekly: leading indicators only. Mid-quarter: one written re-forecast — expected score per KR and what changed. End of quarter: score, retro on the *bet* (was the theory right?), not just the execution.

---

## 5. Decision Frameworks

Pick the framework from the shape of the decision, not from habit.

| Framework | Use it when | Output |
|-----------|-------------|--------|
| **RICE** | Many comparable candidates competing for one capacity pool | Ranked list with visible inputs |
| **DACI** | The decision needs one accountable human and cross-functional buy-in | Driver, Approver (one), Contributors, Informed |
| **DARE** | The choice is between 2–4 options with real trade-offs and disagreement | Decision, Alternatives, Reasoning, Evidence |
| **Opportunity Scoring** | You have importance/satisfaction survey data and need to find underserved needs | (Importance + max(Importance − Satisfaction, 0)) ranking |

### DACI — one approver, always

- **Driver** — runs the process, owns the doc. Not the approver.
- **Approver** — exactly one person. If two, the decision will stall or be re-litigated.
- **Contributors** — consulted before the decision, not after.
- **Informed** — told after, in writing.

Anti-pattern: "we're all approvers." That is consensus, and consensus on a reversible decision is expensive theater.

### DARE — record the reasoning, not just the answer

```
Decision:  <what we will do>
Alternatives considered:  <2–3, with the reason each lost>
Reasoning:  <the criteria that decided it>
Evidence:  <data, quotes, prior attempts — linkable>
Revisit if:  <the condition that would reopen this>
```

`Revisit if` is the most valuable line in the document. Without it, the decision gets reopened every time a stakeholder is unhappy.

### Opportunity Scoring (Ulwick)

Score each need on importance and current satisfaction (1–10, from survey or interviews asked quantitatively). Opportunity = `importance + max(importance − satisfaction, 0)`. A need that is important *and* poorly satisfied scores highest — that gap is where product work pays. A high-importance need that is already well served is not an opportunity, it is table stakes.

---

## Anti-Patterns

- **RICE theater.** Scores appear after the roadmap is decided; inputs get tuned until the preferred item ranks first. Fix: collect inputs before the meeting, and record overrides *with reasons*.
- **Confidence inflation.** Everything at 90% so nothing looks like a guess. Fix: cap unsupported items at 50%.
- **Synthesis by anecdote.** The one quotable customer becomes the strategy. Fix: participant counts per theme, visible.
- **The interview that validates.** Leading questions plus a recruited-for-confirmation sample. Fix: one churned and one non-user per study, past-behavior questions only.
- **PRD as spec.** Function-by-function description with no problem statement or kill criteria. Fix: if the "why now" is missing, the doc is a ticket with a cover page.
- **Scope creep through silence.** Unlisted non-goals get assumed. Fix: name what you will not do, in writing, in the doc.
- **OKRs as a project list.** Every KR is a deliverable with a date. Fix: outcome language, baseline before target.
- **Sandbagged OKRs.** 1.0 across the board. Fix: grade the bet, not just the number.
- **Stakeholder updates that only carry good news.** Trust dies on the surprise, not the miss. Fix: bad news first, with a plan and a date.
- **Framework shopping.** DACI for a two-person call, RICE for a single obvious feature. Fix: match the framework to the shape of the decision; skip it when the call is reversible and cheap.

---

## Verification

Before handing any artifact over, confirm:

1. **Traceability** — every claim in the PRD or synthesis cites evidence (quote, ticket count, metric, interview ID).
2. **RICE** — reach is an absolute count, effort is one consistent unit, confidence is defensible, and overrides are recorded with reasons.
3. **Synthesis** — each theme names ≥3 participants, a behavior, a severity, the current workaround, and a counter-evidence section exists.
4. **PRD** — problem, vision, one primary persona, must/should/won't split, one primary metric with baseline + target + window, and kill criteria.
5. **OKRs** — 1–3 objectives, 2–4 KRs each, every KR has a baseline and a date, at least one lagging KR per objective, confidence rated at the start.
6. **Decision record** — one named approver, alternatives with reasons, and a "revisit if" condition.
7. **No output-only KRs and no unlabeled opinions** presented as findings.

## References

- `references/sources.md` — frameworks, original sources, and reading list
- `scripts/rice_scorer.py` — RICE calculator (stdlib only)

## License

MIT — see `LICENSE`.
