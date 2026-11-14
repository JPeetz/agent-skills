---
name: agentic-eval
description: >-
  Use this skill when setting up or improving evaluation for AI agents and LLM
  outputs. Activates on "agent eval", "LLM evaluation", "eval harness", "agent
  benchmark", "rubric judge", "evaluator-optimizer", "self-critique", "LLM as
  judge", "pairwise rank", "eval pipeline", "calibration test", "agentic eval",
  or "eval-driven development". Covers rubric design, evaluator-optimizer
  architecture, self-critique loops, pairwise ranking, calibration, eval
  harness setup, and continuous eval pipelines.
version: 1.0.0
author: Skill Foundry
license: MIT
category: ai-agent-engineering
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - evaluation
  - evals
  - benchmarks
  - LLM-as-judge
  - rubric
  - testing
  - agent-eval
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
    - evaluation
    - evals
    - LLM-as-judge
    - rubric
    - agent-benchmark
    - calibration
  related_skills:
    - ai-agent-architecture
    - prompt-engineering
    - qa-testing
---

# Agentic Eval

## Overview

An agent that "seems good" in a demo is an untested agent. Evaluation is how you replace that impression with a number you can act on: a fixed set of cases, a scoring procedure, and a baseline you compare against before every change. Without it you cannot tell a prompt rewrite that helped from one that merely felt better, and you ship regressions you never saw.

Three things make agent evals different from ordinary unit tests:

- **The output space is open.** There is rarely one correct string, so correctness has to be defined by criteria, not equality.
- **Trajectory matters.** An agent that reaches the right answer after seven wrong tool calls is a worse agent than one that reaches it in two. Score the path, not just the final text.
- **The judge is often a model.** That judge has biases — verbosity, position, self-preference — and it drifts. A judge you have not calibrated is a random number generator with good vocabulary.

This skill covers the loop that turns that mess into a usable signal: an eval pyramid that tells you which level to test, rubric design for open-ended outputs, the evaluator-optimizer architecture for improving outputs at runtime, self-critique loops that are honest about their limits, pairwise ranking that controls for position bias, calibration that proves the judge agrees with humans, and a harness you can run in CI.

The governing rule: **write the eval before you write the prompt.** An eval that is written after the output is a description of the output, not a test of it.

## When to Use

- Starting a new agent, prompt chain, or tool-using workflow and you need a way to know if it works
- A prompt change "feels better" and you need evidence it did not regress three other cases
- Choosing between two models, two prompts, or two agent architectures
- A stakeholder asks for a quality score, or you need a regression gate in CI
- Building a generate → evaluate → critique → refine loop and you need the evaluator to be trustworthy
- Your LLM-as-judge scores disagree with human review and you need to find out why
- Costs are climbing and you want to know which fraction of traffic actually needs the expensive path

**When not to use:** functional correctness that a normal test can assert (`assert total == 42`) belongs in your test suite, not an LLM judge — deterministic assertions are cheaper, faster, and never drift. Verifying that a specific claim is true belongs to a retrieval/citation workflow. This skill is for qualities that resist exact assertions: helpfulness, faithfulness, tone, plan quality, tool-use efficiency, and task completion.

## The Eval Pyramid

Test at the lowest level that can catch the failure. Higher levels are slower, noisier, and more expensive; if a unit-level check can catch a bug, a full agent run is waste.

```
                 ┌──────────────────────┐
    Level 5      │  Human review        │  slow, expensive, ground truth
                 ├──────────────────────┤
    Level 4      │  System / end-to-end │  full agent run, task success
                 ├──────────────────────┤
    Level 3      │  Integration         │  multi-step, tools, retrieval
                 ├──────────────────────┤
    Level 2      │  Component           │  one prompt / one node / one tool call
                 ├──────────────────────┤
    Level 1      │  Unit                │  deterministic asserts, schemas, parsers
                 └──────────────────────┘
```

**Level 1 — Unit.** Deterministic and free. Does the output parse as JSON? Does the tool call use a valid argument schema? Did the router pick an allowed route? Are required fields present? Run these on every commit. They catch the majority of production breakage and never need a judge.

**Level 2 — Component.** One prompt or one node in isolation, scored against a rubric. "Given this ticket, is the generated plan missing any acceptance criterion?" Cheap enough to run on every prompt edit. This is where most rubric work happens.

**Level 3 — Integration.** Multi-step behavior with tools and retrieval: does the retriever surface the right document, does the agent recover from a failed API call, does the summarizer stay faithful to the fetched sources? Score both the final answer and the trajectory (tool calls, retries, dead ends).

**Level 4 — System / end-to-end.** A whole task from a realistic starting state, judged on completion: "the issue is fixed and the tests pass", "the booking exists in the calendar". Use executable checks wherever possible — running tests, diffing state, querying the environment — because an executable check cannot be talked into agreeing with a bad agent.

**Level 5 — Human review.** Slow, expensive, and the only source of truth for subjective quality. Do not run it on every change. Run it on a stratified sample (a few dozen cases, weighted toward high-traffic and high-risk paths) to calibrate levels 2–4, and whenever the judge's scores move without a corresponding human review.

Practical allocation: many level-1 cases, a few dozen level-2, a handful of level-3/4 scenarios, and a small rotating human sample. A suite of 40 well-chosen cases beats 4,000 scraped ones, because you can read every failure.

## Eval-Driven Development

The loop mirrors TDD, with a judge where the assert would be:

1. **Collect real cases.** Pull from production traces, bug reports, support tickets, and the failures you already know about. Invented cases test your imagination; real cases test your product.
2. **Write the expected behavior in words.** Not the expected string — the criteria a good answer satisfies, plus at least one specific thing a bad answer would get wrong. If you cannot articulate the failure mode, you cannot score it.
3. **Run the baseline and record it.** Current prompt, current model, current settings. Save outputs verbatim. A baseline you did not save is a baseline you will reconstruct wrongly.
4. **Change one thing.** Prompt, model, retrieval, tool description — one variable at a time, or you learn nothing about which one moved the score.
5. **Compare, don't just re-score.** Diff outputs case by case. Aggregate scores hide the trade: +4% average with three cases newly broken is a regression, not a win.
6. **Read the failures.** Every failing case gets a human read before you decide the judge is right. The judge is a hypothesis; the human read is the test of the test.
7. **Freeze the case.** Once a case has caught a real regression, it stays in the suite permanently. That is how the suite earns its keep.

Keep the suite versioned next to the code. An eval suite that lives in a spreadsheet dies in a quarter.

## Rubric Design

A rubric converts "is this good?" into a small number of independently checkable criteria. Bad rubrics are the most common cause of unusable eval numbers — a judge asked "rate 1–10" will produce a confident, meaningless 7.

### Dimensions

Choose 3–7 dimensions, each answering a different question, each scorable without reference to the others:

| Dimension | Question it answers | Example failure it catches |
|---|---|---|
| Correctness | Are the claims true and the computation right? | Confident wrong answer |
| Faithfulness | Is every claim supported by the provided context? | Hallucinated citation |
| Completeness | Are all parts of the request addressed? | Answers the easy half |
| Instruction adherence | Did it follow format, length, and constraints? | Ignores "no bullet points" |
| Tool efficiency | Did it reach the result without wasted calls? | 12 tool calls for a 2-call task |
| Safety / policy | Does it avoid prohibited content and actions? | Acts outside its authority |
| Tone / style | Does it match the audience and house voice? | Internal jargon to a customer |

Two rules that prevent most rubric rot:

- **Separate correctness from style.** If one dimension mixes "accurate" with "well written", a beautifully written wrong answer scores mid, and you cannot tell whether a change improved truth or prose.
- **One dimension per failure mode.** If "completeness" and "correctness" both punish a missing section, that failure is double-counted and dominates the average.

### Anchors beat scales

Anchors are concrete descriptions of what each score level looks like. Without them, "4 out of 5" means whatever the judge felt that morning.

```
Faithfulness (0–3)
3 — Every factual claim is traceable to the provided context; no outside facts introduced.
2 — All central claims are supported; one minor unsupported detail (an adjective, a date, a name).
1 — At least one central claim is unsupported or contradicted by the context.
0 — The answer contradicts the context, or invents sources/facts wholesale.
```

Notes on anchors that make them work:

- Anchor on **observable properties**, not vibes. "Cites a source for each numeric claim" beats "feels rigorous".
- Make the **lowest anchor explicit and concrete**. Judges are reluctant to give zeros unless told exactly what a zero is.
- Keep the scale small (0–3 or 0–4). Wide scales (0–100) imply precision the judge does not have.
- Write the anchors **before** looking at model outputs. Anchors written afterwards get reverse-engineered to fit the outputs you already have.

### Chain-of-thought before the label

Ask for reasoning first, then the score. A judge that emits a label and then justifies it is rationalizing; a judge that reasons and then labels is measuring.

```
Evaluate the answer against the rubric.

Step 1: For each dimension, quote the specific evidence from the answer that bears on it.
Step 2: Note any evidence that is missing.
Step 3: Assign the score per dimension using the anchors, citing the anchor level you matched.
Step 4: Give one sentence on what would raise the score by one level.

Return JSON only:
{"evidence": {...}, "scores": {"faithfulness": 3, "completeness": 2},
 "anchor_matched": {"faithfulness": "3", "completeness": "2"},
 "one_level_up": "..."}
```

Requiring the judge to quote evidence does three useful things: it makes hallucinated justifications visible, it gives you something to audit without re-running the judge, and it forces the score to depend on the text rather than on length or confidence.

### What a good rubric does not contain

- **Vague intensifiers** ("high quality", "professional", "robust") — unfalsifiable, so the judge fills them with its own taste.
- **More than one instruction per dimension** — a judge that must satisfy two goals in one score picks one and ignores the other.
- **Weights without a story** — if you cannot say why correctness is 3× tone, do not weight; report dimensions separately and let the reader weigh them.
- **Criteria the task cannot satisfy** — a rubric that requires citations from a task with no retrieval guarantees every case fails and teaches you nothing.

## Evaluator-Optimizer

Evaluator-optimizer is a two-role loop: a **generator** produces an artifact, an **evaluator** scores it against explicit criteria and returns actionable critique, and the generator revises. It is the right architecture when (a) quality is judgeable more reliably than it is producible in one shot, and (b) iteration measurably improves the artifact.

It is the wrong architecture when the evaluator cannot articulate *what* to change ("this is not good enough" is not feedback), or when a single pass already saturates the task — you pay double for a loop that converges on iteration one.

```
             ┌──────────────┐
  task ─────▶│  Generator   │──── artifact ────┐
             └──────────────┘                  │
                    ▲                          ▼
                    │                  ┌──────────────┐
                    │   critique +     │  Evaluator   │
                    └──── score ◀──────│  (rubric)    │
                                       └──────────────┘
                                              │
                                     pass / max iters
                                              ▼
                                         ship or fail
```

Design rules:

- **Give the evaluator the rubric, not the artifact's expected answer.** If the evaluator knows the reference answer, it scores similarity, not quality, and the loop learns to imitate.
- **Critique must be actionable and specific.** Require "name the sentence and the dimension it fails, and state the fix". Generic critique produces generic revision.
- **Re-score with fresh eyes.** Do not let the evaluator see its previous score in the same context; it will anchor and approve the revision. Run it in a new call.
- **Bound the loop.** `max_iterations` of 2–3. Track score per iteration; if iteration 2 does not beat iteration 1, stop and return the better artifact. Loops that run to the limit are usually oscillating, not improving.
- **Keep the best artifact, not the last.** Revision can regress. Return the highest-scoring version and log all of them.
- **Watch the cost ratio.** Two model calls per iteration is the floor; a tool-using generator multiplies it. If a single stronger model pass costs less than three weak passes, do that instead.

```python
def evaluator_optimizer(task, generate, evaluate, max_iters=3):
    best = None
    critique = None
    for i in range(max_iters):
        artifact = generate(task, critique=critique)
        result = evaluate(task, artifact)          # fresh call, rubric only
        if best is None or result.score > best.score:
            best = Scored(artifact, result.score, i)
        if result.passed:
            break
        critique = result.critique                 # specific, per-dimension
    return best
```

Use it for: drafting with a style rubric, code generation with a test-and-lint evaluator, report writing with a faithfulness evaluator, plan generation with a completeness evaluator. For code, the evaluator should be *executable* (run the tests) wherever possible — a test suite is a better judge than a model and costs nothing per run.

## Self-Critique Loops

Self-critique asks one model to review its own output. It is cheap and it catches a real class of errors — omissions, unstated assumptions, format violations, arithmetic slips. It also has hard limits you should design around rather than hope past.

What self-critique reliably catches:

- **Requirement amnesia** — the output ignored a constraint from the prompt. Re-reading the prompt against the output is a genuine check.
- **Internal inconsistency** — a number that contradicts another number in the same answer.
- **Format and schema violations** — missing sections, wrong field names.
- **Obvious omissions** — an edge case the model knows about but did not mention.

What it reliably misses:

- **Confident factual errors.** The same weights that produced the error produce the justification for it. Asking "are you sure?" mostly produces a more confident restatement.
- **Shared blind spots.** If the model did not know a constraint, it will not notice the constraint was violated.
- **Sycophantic revision.** Models tend to agree that their own work is good, and to "fix" critique by adding hedges and length rather than substance.

Design that mitigates this:

1. **Separate the roles.** Use a different prompt with a different system message, ideally a different model or at least a fresh context. Same-context self-review is the weakest form.
2. **Critique against explicit criteria, not "review this".** "Check whether every acceptance criterion in the ticket appears in the plan; list any that are missing" is checkable. "Is this good?" is not.
3. **Require evidence per finding.** A critique entry must quote the offending text. Findings without quotes are usually invented.
4. **Ask for a severity, and act only on blocking findings.** Otherwise the loop churns on nitpicks and dilutes the good output.
5. **Never let the critic rewrite directly.** Critic produces findings; generator applies them. If the critic rewrites, you lose the audit trail and the ability to reject bad fixes.
6. **Verify the revision.** Re-run your deterministic checks (level 1) after every revision. Self-critique loops routinely break JSON validity while improving prose.

```python
def self_critique_draft(task, draft, critique, revise, checks):
    findings = critique(task, draft)          # fresh context, rubric-based
    blocking = [f for f in findings if f.severity == "blocking"]
    if not blocking:
        return draft
    revised = revise(task, draft, blocking)   # applies findings only
    if not checks(revised):                   # level-1 gate
        return draft                          # regressed: keep original
    return revised
```

The single most valuable use of self-critique is not improving a single answer — it is generating **eval cases**. Run self-critique over 100 production outputs, collect the findings, and promote the recurring ones into rubric dimensions and test cases. That converts a runtime trick into a durable asset.

## Pairwise Ranking

Absolute scores drift: the same judge gives the same answer a 7 on Monday and a 5 on Wednesday. Comparisons are more stable, because "which of these two is better" is an easier judgment than "how good is this on an absolute scale", and it is far more robust across models and prompt versions.

Use pairwise when: comparing two prompts, two models, or two agent versions; collecting human preference data; or building a preference set for fine-tuning. Use absolute rubric scores when you need a per-dimension profile of one output, or when you need to compare against a fixed historical threshold.

### Position bias, and how to control it

Judges systematically prefer the first (or, in some models, the last) option. This is not noise; it is a bias with a direction, and it will fabricate a win for whichever variant you happen to list first.

Controls, in order of strength:

1. **Run both orders and require agreement.** Score (A,B) and (B,A). Count a win only when the judge prefers the same artifact in both orders. Disagreements are ties. This is the default; it roughly doubles judge cost and removes most of the bias.
2. **Randomize order** per case with a recorded seed. Cheaper, but only averages the bias out across many cases — it does not remove it per case.
3. **Blind the labels.** Never send "baseline" and "candidate"; send "Response 1" and "Response 2". Judges leak label information into their reasoning.
4. **Add a tie option and make it legitimate.** Forcing a choice produces coin flips on equal outputs. Explicitly permit "A is better / B is better / tie", and report tie rate — a high tie rate means your change is not doing much, which is itself the finding.

```
Which response better satisfies the rubric? Judge each dimension
independently, then give an overall preference.

Response 1: ...
Response 2: ...

Reason per dimension first, then:
{"faithfulness": "1|2|tie", "completeness": "1|2|tie", "overall": "1|2|tie"}
```

### Turning comparisons into a ranking

- **Win rate** is the simplest and the most honest: wins / (wins + losses), ties excluded and reported separately. Use it for two variants.
- **Bradley–Terry** fits a strength parameter per variant from pairwise outcomes; use it when you have many variants and incomplete comparisons (not every pair was judged). It gives a ranking plus confidence intervals, and the intervals are the point — overlapping intervals mean "no detectable difference".
- **Elo** is an online approximation of Bradley–Terry. Fine for a live leaderboard, worse for a one-off experiment because the result depends on presentation order.
- **Report agreement between orderings.** If (A,B) and (B,A) agree on only 60% of cases, your judge is mostly measuring position, and no aggregate ranking from it is trustworthy.

Sample size: with a 55/45 true difference you need hundreds of comparisons to detect it. If your suite has 30 cases, it can only reliably detect large differences — say so instead of reporting a two-point win as a result.

## Calibration and Overfitting

A judge is a measuring instrument. Calibration is proving it measures what you think it measures. Without it, every number downstream is decoration.

### Agreement with humans

Build a small human-labeled set — 30–50 cases is enough to start, stratified across the dimensions and difficulty. Have at least two humans label a subset so you can measure human–human agreement first: **the judge cannot be more reliable than the humans it is imitating**, and if humans disagree 30% of the time, a judge at 70% agreement is already near the ceiling.

Measure with the metric that matches the label type:

| Label type | Metric | Read it as |
|---|---|---|
| Binary pass/fail | Cohen's κ | >0.6 substantial, >0.8 strong; <0.4 the judge is guessing |
| Ordinal 0–3 | Weighted κ or Spearman ρ | Weighted κ penalizes off-by-two errors |
| Pairwise preference | Agreement rate + tie rate | Track agreement on both orderings separately |

Then inspect the disagreements, not just the number. Sort by |judge − human| and read the top 20. The pattern is usually one of: a dimension the rubric under-specifies, a systematic bias (length, format, confidence), or a genuinely ambiguous case that belongs out of the suite.

Recalibrate whenever you change the judge model, the rubric, or the anchors. A judge swap silently invalidates every historical comparison; re-run the baseline on the new judge before trusting a delta.

### Known judge biases to measure explicitly

- **Verbosity bias** — longer answers score higher. Test: pad a good answer with filler and check whether the score rises. Mitigation: cap length in the rubric, or add an anchor that penalizes unrequested length.
- **Self-preference** — a model favors its own outputs. Test: judge a set containing its own generations. Mitigation: use a different model as judge than the one under test, or calibrate the offset.
- **Position bias** — covered above; measure with both orderings.
- **Format bias** — markdown, bullets, and headings read as "organized". Test with the same content in plain prose.
- **Authority/confidence bias** — hedged correct answers lose to confident wrong ones. Test with a confident wrong answer; if it wins, the rubric needs a correctness anchor that ignores tone.

### Overfitting the eval

Once a suite is public inside a team, prompts get tuned against it and the score stops predicting production quality. Symptoms: eval score climbs while user complaints do not fall; a case passes only with a suspiciously specific prompt phrasing; a change improves the suite and breaks an unlisted adjacent case.

Defenses:

- **Hold out a set.** Keep 20–30% of cases out of the tuning loop and run them only at release. A gap between tuning and holdout scores is the size of your overfit.
- **Refresh from production.** Add new real cases every cycle; retire cases that no longer reflect traffic.
- **Score the path, not just the answer.** Trajectory metrics (tool calls, retries, tokens) are harder to overfit than final text.
- **Rotate cases.** A case that has been in the suite for a year and is passed by every model is measuring nothing. Retire or harden it.
- **Never tune on the test set you report.** If you must, report it as a tuning score and label the holdout as the real number.

## Eval Harness Setup

A harness is three things: a dataset, a runner, and a scorer — plus the discipline to run it on every change.

### Dataset

One JSONL record per case, with everything needed to reproduce the run:

```json
{"id": "refund-014", "level": 2, "split": "tune",
 "input": {"ticket": "...", "policy": "..."},
 "criteria": ["cites the 30-day window", "does not promise a refund the policy excludes"],
 "reference": "optional gold answer",
 "tags": ["billing", "policy-edge"],
 "added": "2026-11-01", "source": "prod-trace-8812"}
```

Rules that keep a dataset usable: stable IDs (never renumber), a `split` field so holdout is mechanical, `tags` so you can run a slice, and `source` so every case traces back to a real failure. Version the file in git with the code.

### Runner

Boring and parallel. It should:

- **Pin everything** — model version, temperature, seed, prompt hash, tool versions. A score without these is not reproducible.
- **Cache by hash of (input, config)** so re-scoring does not re-pay for generation.
- **Isolate failures** — one crashing case must not abort the run; record the error as the result.
- **Run cases concurrently** with a bounded pool, and respect rate limits with backoff.
- **Write raw outputs verbatim** to a run directory, alongside the config. Scoring is downstream and re-runnable; raw outputs are the artifact you cannot recreate.
- **Be deterministic where it can be** — `temperature=0` for judged tasks, fixed seeds, fixed tool stubs.

### Scorer

Two-stage, always:

1. **Deterministic gate (free).** Schema validity, required sections, forbidden strings, length bounds, executable checks. Anything failing here never reaches the judge. This alone typically catches a third of regressions and costs nothing.
2. **Judge (expensive).** Rubric scoring or pairwise comparison, on what survived the gate.

```python
def score(case, output):
    gate = deterministic_checks(case, output)      # level 1
    if not gate.ok:
        return Result(case.id, 0.0, failed=gate.reason, judged=False)
    verdict = judge(case.criteria, output)          # fresh call, CoT first
    return Result(case.id, verdict.overall, dims=verdict.scores, judged=True)
```

### Reporting

A single average hides everything that matters. Report:

- **Per-dimension means** and the **per-case diff against baseline**, sorted by delta. The sorted diff is what you actually read.
- **Pass rate at a threshold**, not just the mean — a mean of 2.6 can hide 20% of cases at zero.
- **Cost and latency** per case and per run, with p50/p95. A quality win that triples p95 is a product decision, not a free improvement.
- **Tie and error rates.** Silent judge failures read as low scores; surface them separately.
- **N and confidence.** With 30 cases, differences under ~10 points are noise. Say so.

### CI integration

- **Level 1 on every commit** — fast, deterministic, blocking.
- **Level 2–3 on PRs touching prompts, tools, or routing** — path-filtered so unrelated PRs do not pay for it.
- **Level 4 nightly** — full scenarios, cost-capped, results posted to the PR or dashboard.
- **Human sample weekly** — a rotating batch, used to recalibrate the judge, not to gate merges.

Gate on **regressions, not absolutes**: "no case may drop more than one anchor level versus baseline, and pass rate may not fall" is enforceable. "Overall score must exceed 0.8" invites tuning to the number and blocks legitimate trade-offs.

## Anti-Patterns

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| Vibe-checking ("this looks better") | Unfalsifiable, and biased toward the most recent output | Fix a case set and a rubric before changing the prompt |
| One giant 1–10 score | The judge collapses every dimension into "feels good" | 3–7 anchored dimensions, reported separately |
| Judge that labels before reasoning | Justification is post-hoc rationalization | Require quoted evidence, then the score |
| Same-context self-review | The model defends its own error | Fresh context, different prompt, ideally different model |
| Unbounded refine loop | Oscillates, burns tokens, returns the worst iteration | Max 2–3 iterations, keep the best, stop on no improvement |
| Single-order pairwise | Position bias decides the winner | Both orders, agreement required, ties reported |
| Judge = model under test | Self-preference inflates the score | Different judge model, or measured and corrected offset |
| Tuning on the holdout | Score stops predicting production | Mechanical `split` field, holdout run at release only |
| 4,000 scraped cases nobody reads | Unread failures are unactionable | 40 cases you have read, expanded by real regressions |
| Average-only reporting | Hides the three newly broken cases | Per-case diff sorted by delta, plus pass rate |
| Judging what a test could assert | Slower, costlier, drifts | Deterministic check first; judge only what resists assertion |
| Changing prompt, model, and retriever at once | You learn nothing about the cause | One variable per run |

## Red Flags

- An eval suite with no baseline recorded, or a baseline from a different judge version
- Rubric dimensions you cannot score from the output alone
- Judge invoked once, uncalibrated, with no human-labeled set behind it
- A score that improved while user-reported quality did not
- Pairwise results reported without the order-swapped agreement rate
- A refine loop whose iteration count equals `max_iterations` on most cases
- Cases with no source, no owner, and no date added
- Holdout set that anyone on the team has tuned against
- Latency and cost absent from the eval report, so a "win" ships as a regression

## Verification

Before trusting an eval number:

- [ ] Every case names the behavior it checks and the failure it would catch
- [ ] Rubric dimensions are independent, anchored, and scored after quoted evidence
- [ ] Deterministic checks run before the judge and reject invalid output for free
- [ ] Judge agreement with humans measured (κ / weighted κ / pairwise agreement), on a labeled sample
- [ ] Verbosity, position, and self-preference bias each probed at least once
- [ ] Baseline saved verbatim with model, prompt hash, seed, and temperature
- [ ] Pairwise comparisons run in both orders with disagreement counted as a tie
- [ ] Holdout split is mechanical and has not been tuned against
- [ ] Refine loops bounded, best-iteration retained, regression-checked after each revision
- [ ] Report shows per-case diffs, pass rate, cost, latency, and n
