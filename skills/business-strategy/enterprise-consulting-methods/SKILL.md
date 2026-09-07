---
name: "enterprise-consulting-methods"
description: "Use when you need McKinsey/BCG-grade strategy work — problem decomposition, hypothesis testing, storyline building, decision memos, stakeholder mapping, synthesis, meeting prep, workshop design, and native PowerPoint chart production. Covers 15 consulting methodology patterns from Situation-Complication-Problem-Recommendation (SCPR) through MECE issue trees, hypothesis trees, Minto Pyramid writing, and the 4-agent deck pipeline. All chart outputs are native python-pptx objects, editable inside PowerPoint."
version: "1.0.0"
author: "JPeetz (adapted from Sruthi Chintakunta — github.com/sruthir28/enterprise-ai-skills)"
license: "MIT"
metadata:
  hermes:
    tags:
      - consulting
      - strategy
      - mckinsey
      - powerpoint
      - python-pptx
      - deck-pipeline
      - issue-tree
      - hypothesis-tree
      - decision-memo
      - stakeholder-map
      - synthesis
      - meeting-prep
      - workshop-design
      - scpr-framework
      - minto-pyramid
      - prioritization
      - business-strategy
      - enterprise
      - presentation
    related_skills:
      - "mckinsey-charts"
      - "issue-tree-builder"
      - "storyline-builder"
      - "decision-memo-builder"
      - "meeting-prep-kit"
      - "stakeholder-map"
      - "top-down-memo"
      - "hypothesis-tree"
      - "mckinsey-critic"
      - "workshop-designer"
      - "prioritization"
      - "synthesis"
      - "scpr-framework"
      - "ai-use-case-scorer"
---

# Enterprise Consulting Methods

A comprehensive meta-skill package containing 15 battle-tested consulting methodology patterns from a former McKinsey consultant. Each encodes a specific consulting move so you don't reinvent the structure every time. All deck/chart outputs produce **native python-pptx objects** — editable inside PowerPoint, right-click → Edit Data.

---

## Overview

| Category | Skill | What It Does |
|----------|-------|-------------|
| **Framing** | [SCPR Framework](#1-scpr-framework-situation-complication-problem-recommendation) | Structure arguments using Situation-Complication-Problem-Recommendation |
| | [Issue Tree Builder](#2-issue-tree-builder-mece-decomposition) | Break down problems into MECE components |
| | [Hypothesis Tree](#3-hypothesis-tree-day-1-hypothesis) | Commit to a Day-1 answer and design tests that could kill it |
| **Analysis** | [Synthesis](#4-synthesis-insight-extraction) | Turn raw inputs into 3 insights with evidence + so-what |
| | [Prioritization](#5-prioritization-frameworks) | Score features using RICE, Impact/Effort, Value/Complexity |
| | [AI Use-Case Scorer](#6-ai-use-case-scorer) | Score AI use cases on Value × Feasibility × Safety |
| | [Data Insights](#7-data-insights) | Analyze datasets and answer key questions in plain English |
| **Writing** | [Decision Memo Builder](#8-decision-memo-builder) | 1-page memo forcing a yes/no decision |
| | [Top-Down Memo](#9-top-down-memo-minto-pyramid) | Answer-first writing using the Minto Pyramid Principle |
| | [Storyline Builder](#10-storyline-builder) | Build slide narratives where each line = a slide title |
| **Meetings & People** | [Meeting Prep Kit](#11-meeting-prep-kit) | Pre-read + agenda + talking points + objections |
| | [Stakeholder Map](#12-stakeholder-map) | Map the room onto Power/Interest |
| | [Workshop Designer](#13-workshop-designer) | Design sessions that end with committed artifacts |
| **Decks** | [McKinsey Charts](#14-mckinsey-charts-native-powerpoint) | Three workhorse charts as native python-pptx objects |
| **Quality** | [McKinsey Critic](#15-mckinsey-critic-em-review) | Review decks/docs like a McKinsey engagement manager |

---

## When to Use

Use this meta-skill whenever you need to apply structured consulting thinking to a business problem. Common triggers:

- **Strategic question → recommendation**: Issue Tree → Hypothesis Tree → run tests → Decision Memo
- **Customer research → memo**: Synthesis → Top-Down Memo (or Decision Memo) → McKinsey Critic
- **Board deck**: Issue Tree → Storyline Builder → Charts → Deck Pipeline → McKinsey Critic
- **Big decision with politics**: Stakeholder Map → Decision Memo → Meeting Prep Kit (for each 1:1)
- **Offsite or alignment workshop**: Workshop Designer → Meeting Prep Kit (pre-1:1s) → Top-Down Memo (post-send)
- **Any high-stakes presentation**: Use the 4-agent Deck Pipeline (Strategist → Builder → Critic → Fixer)
- **Analysis paralysis**: Hypothesis Tree to commit to a Day-1 answer before boiling the ocean
- **Exec communication**: Top-Down Memo for emails/briefs, Decision Memo for yes/no asks

---

## How to Use

### Quick Start — Full Deck Pipeline

```text
Build me a McKinsey-style deck on [topic] for [audience]. Run the full top-down workflow:
1. Use issue-tree-builder to decompose into MECE branches
2. Use storyline-builder to turn it into 8 claim-shaped slide titles
3. Use mckinsey-charts for the data slides (bar+callout, waterfall)
4. Use deck-pipeline (strategist → builder → critic → fixer) to produce the final .pptx
```

### Individual Method Calls

Each of the 15 methods below can be invoked individually. Pick the pattern that matches your current stage of work:

- **Framing the problem**: SCPR Framework → Issue Tree → Hypothesis Tree
- **Understanding the data**: Synthesis → Data Insights
- **Deciding what to do**: Prioritization → Decision Memo
- **Communicating the answer**: Top-Down Memo → Storyline Builder → Charts → Pipeline
- **Getting buy-in**: Stakeholder Map → Meeting Prep Kit → Workshop Designer
- **Quality gate**: McKinsey Critic on any draft before it ships

---

## Workflow: Full Strategic Engagement

This is the canonical top-down workflow for turning a fuzzy strategic question into an actionable recommendation:

```
Phase 1: FRAME
  SCPR Framework → Issues Tree → Hypothesis Tree
  (Structure the problem, commit to a Day-1 answer)

Phase 2: ANALYZE
  Synthesis / Data Insights → Prioritization
  (Process raw data, rank what matters)

Phase 3: RECOMMEND
  Decision Memo Builder → Top-Down Memo
  (Force a yes/no, communicate answer-first)

Phase 4: COMMUNICATE
  Storyline Builder → McKinsey Charts → Deck Pipeline
  (Build narrative, create charts, produce deck)

Phase 5: STRESS-TEST
  Stakeholder Map → Meeting Prep Kit → McKinsey Critic
  (Map politics, prep meetings, get EM-level review)

Phase 6: EXECUTE
  Workshop Designer
  (Align the team, leave with committed artifacts)
```

---

## Methodology Reference

### 1. SCPR Framework (Situation-Complication-Problem-Recommendation)

**Purpose**: Structure arguments for executive summaries, memos, and strategic recommendations.

**Structure**:
- **Situation**: Current state of the market/business (baseline context)
- **Complication**: Recent shift or change creating urgency (new dynamics, competitive threats)
- **Problem**: Crisp answerable question to solve
- **Recommendation**: Proposed actions that are MECE, specific, and time-bound

**Core Principles**: MECE at recommendation level, clarity, actionability. The Complication must be distinct from the Problem — Complication is "what changed," Problem is "what question to solve."

### 2. Issue Tree Builder (MECE Decomposition)

**Purpose**: Break down complex problems into MECE components for structured analysis.

**Structure**: Top-down, 2 levels max (Governing Question → 3 Branches → 2-3 Sub-Branches each).
- Level 0: Governing Question (specific, answerable)
- Level 1: Major branches — decompose to fundamentals (not actions)
- Level 2: Testable hypotheses

**Common Decompositions**:
- Revenue = Price × Quantity × Pipeline
- Profit = Revenue - Cost
- Growth = New customers + Expansion + New products
- Market entry = Attractiveness + Competitive position + Capability

**Prioritization**: After building the tree, rank branches by Impact × Effort. Start with High Impact + Low Effort.

### 3. Hypothesis Tree (Day-1 Hypothesis)

**Purpose**: Commit to a best-guess answer before analysis, so the work targets what would change your mind.

**Structure**: Top = Day-1 answer → 3 sub-claims (if all true, top is proven) → Tests that could kill each sub-claim.

**Key Rules**:
- You MUST commit to a Day-1 answer (even a weak guess beats no guess)
- 3 sub-hypotheses max
- Every leaf is a test that could kill the branch
- State conviction (High/Med/Low) — test low-conviction first
- Disconfirmation > confirmation: design tests to kill the hypothesis

**Issue Tree vs. Hypothesis Tree**:
| | Issue Tree | Hypothesis Tree |
|---|-----------|----------------|
| Top | The question | The answer (your guess) |
| Branches | Sub-questions (MECE) | Sub-claims proving the top |
| Bottom | Areas to investigate | Tests that would kill the claim |
| Use when | You don't know what matters | You have a strong prior |

### 4. Synthesis (Insight Extraction)

**Purpose**: Turn raw inputs (interviews, surveys, research) into 3 actionable insights with evidence and implication.

**Process**:
1. Cluster — let themes emerge from data (induction, not deduction)
2. Force-rank to 3 by frequency, severity, surprise
3. Name each insight as a claim (falsifiable, specific)
4. Stack evidence (2-3 bullets with direct quotes, exact numbers, named sources)
5. Write the so-what (one-line implication: "Because this is true, the reader should ___")
6. Anti-summary check: would the reader know what to do next?

**The test**: "Did the output change how the reader will act?" If no, you summarized — rewrite.

### 5. Prioritization Frameworks

**Purpose**: Score and rank features, initiatives, and tasks using proven frameworks.

| Framework | When to Use | Formula |
|-----------|-------------|---------|
| RICE | Quantitative data available | (Reach × Impact × Confidence) / Effort |
| Impact/Effort Matrix | Quick decisions, limited data | 2×2 grid |
| Value vs. Complexity | Engineering-heavy decisions | 2×2 grid |
| Weighted Scoring | Custom business criteria | Σ (Score × Weight) |

**When data is missing**: Provide baseline estimates based on industry patterns, mark clearly as estimates, use ranges (not false precision), and flag high-uncertainty items for validation.

### 6. AI Use-Case Scorer

**Purpose**: Score personal AI use cases on Value × Feasibility × Safety to tier them: Do Now / Do This Quarter / Park / Avoid.

**Scoring** (1–5 each axis, final = V × F × S):
- **Value**: Time saved + Quality lift + Strategic fit
- **Feasibility**: Tool maturity + Your skill/time
- **Safety**: Quality risk + Data risk + Trust risk (inverted: higher = safer)

**Tiers**: ≥60 Do Now, 30–59 This Quarter, 10–29 Park, <10 Avoid.

### 7. Data Insights

**Purpose**: Analyze any dataset and answer key questions in plain English. Best for quick analysis without being a data scientist. Ask for CSV/JSON data, specify the questions, and get structured analysis back.

### 8. Decision Memo Builder

**Purpose**: 1-page memo forcing a yes/no decision with specific owner and date.

**Memo DNA** — four non-negotiables:
1. Brutal brevity (~400 words max)
2. Storyline clarity (Situation → Complication → Resolution)
3. Decision-forcing (last line = yes/no ask with owner and date)
4. Evidence density (every claim backed by number, quote, or source)

**Structure**: Title (≤10 words) → Context (3-4 sentences) → Complication (2-3 sentences) → Options (2-3, 1-2 lines each) → Recommendation (1 paragraph) → Risks & Mitigations (≤3 bullets) → The Ask (1 line).

### 9. Top-Down Memo (Minto Pyramid)

**Purpose**: Answer-first writing — lead with the conclusion, then MECE arguments, then evidence.

**Structure**: LEAD (one sentence answer) → ARG 1 (claim + evidence) → ARG 2 → ARG 3 → (optional) Risks/Open Questions.

**The test**: Can the reader stop after the first paragraph and know what you think? If they need to read to the end, you wrote a story, not a memo.

### 10. Storyline Builder

**Purpose**: Build presentation storylines where each line = one slide title, creating logical narrative flow.

**Key characteristics**:
- Each line = action-oriented message (not topic label)
- Logical flow: Problem → Context → Analysis → Solution → Roadmap
- Reader must understand the full story from titles alone

**Templates by situation**:
- Market Strategy/Pitch Deck: Market opportunity → Competitive position → Product strategy → Roadmap
- Internal Problem-Solving: Problem framing → Root cause → Solution options → Prioritization → Next steps
- Project Roadmap: Approach → Phases → Activities → Timeline → Success criteria

### 11. Meeting Prep Kit

**Purpose**: Personal prep tool for meetings where YOU are driving an outcome.

**Output sections**:
- Pre-read (3 bullets, ≤30 words each) — minimum context needed
- Time-boxed agenda (adds up to meeting length, decision time reserved at end)
- Talking points (top 3, in spoken language) — lead with strongest, address elephant, make ask
- Anticipated objections (top 3 with rebuttals per person)

**Design rules**: Outcome-first, top 3 not all 12, speakable not slidable.

### 12. Stakeholder Map

**Purpose**: Map people onto Power/Interest grid with stance (Champion / Supporter / Neutral / Skeptic / Blocker / Unknown) and one influence move per person.

**Quadrants**:
- **Manage Closely** (High Power, High Interest) — deciders, most time goes here
- **Keep Satisfied** (High Power, Low Interest) — pre-brief so they're never surprised
- **Keep Informed** (Low Power, High Interest) — give them a role
- **Monitor** (Low Power, Low Interest) — quarterly update enough

**Key Rules**: Real names not roles. Honest stances. Coalition sequence (who to align first).

### 13. Workshop Designer

**Purpose**: Design half-day or full-day workshops that end with committed artifacts and named owners.

**Design rules**:
- One outcome (not three)
- Diverge then converge (never both at once)
- Breakouts < 4 people
- Energy curve: heavy thinking morning, decisions afternoon (never right after lunch)
- Pre-build the artifact template
- Facilitator plays referee, not participant

**Output**: Workshop charter → Hour-by-hour agenda → Breakout playbook → Facilitator "what if" notes → Artifact template → Post-workshop send (24-hour SLA).

### 14. McKinsey Charts (Native PowerPoint)

**Purpose**: Generate McKinsey-style charts as native python-pptx objects (editable in PowerPoint).

**Three chart types**:

1. **bar_callout**: Single-series column with one highlighted bar + callout textbox. Use for TAM/single-number stories.
2. **stacked_bar_over_time**: Stacked column over time with one series highlighted. Use for composition/mix stories.
3. **waterfall**: Start → adds → subtracts → total bridge. Use for revenue/cost bridge analysis.

**Design choices (intentional, not configurable)**:
- Title is a claim, not a label
- One highlight color (everything else grey)
- No gridlines, no chart border
- Source line bottom-left in grey italic
- Single font (Inter), consistent sizes

**Dependencies**: Python 3.9+, python-pptx. See `references/charts.py` for the full implementation.

### 15. McKinsey Critic (EM Review)

**Purpose**: Review decks, docs, and strategies like a McKinsey engagement manager at 2am before a client presentation.

**Grading**: Green (ready) / Yellow (fixable overnight) / Red (needs rework).

**What it checks**:
- Narrative flow (Problem → Context → Analysis → Solution)
- Data rigor (specific numbers, sources, fair comparisons)
- So-what on every slide
- Claim-based titles vs topic titles
- Frameworks vs bullet lists
- Financial frames where needed

**Output format**: Grade → Section-by-section table → Top 3 fixes (ranked by impact) → One thing that works.

---

## Common Pitfalls

### General Consulting Mistakes
- **Skipping the hypothesis tree**: The #1 reason strategy work takes 3x longer than it should. Commit to an answer before you start.
- **Boiling the ocean**: Don't investigate every branch of an issue tree. Prioritize by Impact × Effort and start with the highest-impact, lowest-effort branches.
- **Chronological narratives**: The way you thought about something is the opposite of how the reader needs to hear it. Lead with the answer.
- **Synthesis by list**: "Here are 7 themes" is clustering, not synthesis. Cut to 3 with implication.
- **Missing the so-what**: Every insight/argument needs an explicit implication. If the reader doesn't know what to do next, you haven't finished.

### SCPR Mistakes
- **Situation too detailed**: Keep to essential context only.
- **Complication = Problem**: They're different. Complication is "what changed," Problem is "what question to solve."
- **Overlapping recommendations**: Ensure MECE structure.
- **No timelines**: Always include "by when" in recommendations.

### Issue Tree Mistakes
- **Actions instead of fundamentals**: Level 1 decomposes the problem (Price × Quantity), not solutions.
- **Not MECE**: Overlapping branches or missing key dimensions.
- **Too deep**: 2 levels from governing question max.
- **Not testable**: Terminal branches must be provable/disprovable with data.

### Decision Memo Mistakes
- **Bullet-point soup with no storyline**: Must flow as Situation → Complication → Resolution.
- **Decision-averse hedging**: "We should consider..." — recommend or don't write the memo.
- **Missing numbers**: "Significant impact" without specificity.
- **Recommendation leaked into options**: Options are neutral; recommendation is separate.
- **Ask = "discuss next steps"**: The ask must be a specific yes/no with owner and date.

### Top-Down Memo Mistakes
- **Burying the lead**: Don't start with "Over the last 6 weeks, the team explored..." Lead with the answer.
- **Topic-shaped arguments**: "Pricing" is a topic. "Pricing is 2.4x the standalone value" is an argument.
- **More than 4 arguments**: You haven't synthesized.
- **Evidence that doesn't defend its argument**: Each bullet should clearly serve the headline.

### Stakeholder Map Mistakes
- **Mapping by title, not by power**: The CTO might not care; the staff eng who's been there 8 years might be the blocker.
- **Skipping the "unknown" stance**: Unknown is honest. "I think they're supportive" without evidence is wishful.
- **Over-engaging Monitor quadrant**: Don't burn cycles converting people who don't care.
- **No coalition sequence**: Knowing who matters isn't enough. You need the order of alignment.

### Workshop Design Mistakes
- **Multi-outcome workshops**: "Alignment + brainstorm + decisions" = none of the three. Pick one.
- **No artifact template**: "We'll write it up" = it doesn't get written up. Pre-build.
- **Mixing divergent and convergent**: "Let's brainstorm options and pick the best one in 45 min" produces neither good options nor a defensible pick.
- **Decision moment right after lunch**: Energy nadir. Schedule application work there, not commitment.
- **The sponsor facilitates**: They have a stake. Pick a neutral facilitator.

### McKinsey Charts Mistakes
- **No python-pptx installed**: The chart code requires `pip install python-pptx`. Run this before calling chart functions.
- **Using images instead of native charts**: The whole point is editable charts. Never paste screenshots of charts — use the python-pptx functions.
- **More than 5 series stacked**: Split into small multiples instead.
- **Rainbow charts**: One highlight color, everything else grey. No rainbow.

### Deck Pipeline Mistakes
- **Running the pipeline without a clear audience**: The Strategist needs to know who the deck is for.
- **Skipping stages**: Each agent in the pipeline serves a distinct purpose. Skipping the Critic means shipping an un-reviewed deck.
- **Missing the critic's top 3 fixes**: The Critic identifies the highest-impact problems. Fix those and only those before polish.

---

## Verification

### For Any Consulting Output

1. **Memo/Top-Down Memo**: Can the reader stop after the first paragraph and know the answer? Is every claim backed by a number, quote, or source?
2. **Issue Tree**: Is the governing question specific and answerable? Are branches MECE? Are terminal branches testable with data?
3. **Hypothesis Tree**: Is there a clear Day-1 answer? Can each test kill its branch? Is there an overall kill-criterion?
4. **Storyline**: Can you understand the full argument from slide titles alone? Are titles claims, not topics?
5. **Synthesis**: Did the output change how the reader will act? Are insights claims (not topics) with evidence and so-what?
6. **Decision Memo**: ~400 words max? Last line is a yes/no ask with owner and date?
7. **Stakeholder Map**: Are stances honest? Is there a coalition sequence? Is each stakeholder mapped by power (not title)?
8. **Meeting Prep**: Do talking points ladder to the outcome? Are objections specific per person?
9. **Workshop**: Is there one outcome? Pre-built artifact template? Facilitator "what if" playbook?
10. **McKinsey Charts**: Are charts native pptx objects (right-click → Edit Data)? Is there a source line? One highlight color?
11. **Deck Pipeline**: Check the Critic's grade. If Yellow/Red, apply all top 3 fixes before shipping.
12. **McKinsey Critic**: Run the output through the critic before it reaches stakeholders. Fix structure before polish.

### Python Charts Verification

```bash
pip install python-pptx
python references/charts.py  # Generates test_output.pptx with all 3 chart types
```

Open `test_output.pptx` in PowerPoint and right-click any chart → Edit Data to confirm it's a native chart object.

---

## Composition Patterns

Most real work uses 2–3 of these together:

| Need | Stack |
|------|-------|
| Customer research → memo | Synthesis → Top-Down Memo → McKinsey Critic |
| Strategic question → recommendation | Issue Tree → Hypothesis Tree → run tests → Decision Memo |
| Big decision with politics | Stakeholder Map → Decision Memo → Meeting Prep Kit |
| Board deck (production) | Issue Tree → Storyline Builder → Charts → Deck Pipeline → Critic |
| Offsite / alignment workshop | Workshop Designer → Meeting Prep Kit → Top-Down Memo |
| Pricing or feature analysis | Issue Tree → Prioritization → Decision Memo |
| Weekly exec update | Synthesis (of week's data) → Top-Down Memo (the ask) |
| Product launch proposal | SCPR Framework → Storyline Builder → Charts → Deck Pipeline |
| Quarterly planning | Workshop Designer → Prioritization → Top-Down Memo (post-send) |