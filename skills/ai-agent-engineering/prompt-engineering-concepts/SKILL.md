---
name: prompt-engineering-concepts
description: Use this skill when choosing or fixing a prompt — the 20 core techniques (zero-shot, few-shot, chain-of-thought, role, instruction, output formatting, temperature, chaining, self-consistency, RAG, templates, guardrails, dynamic, ReAct, tree-of-thought, compression, multi-modal, JSON mode, evaluation, optimization) mapped to when each earns its tokens, with the exact prompt move, a selection path for time-pressured cases, and the eight pitfalls that make prompts fail.
version: 1.0.0
license: MIT
author: Joerg Peetz (JPeetz), Hermes Agent
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - prompt-engineering
      - prompting-techniques
      - chain-of-thought
      - few-shot
      - react
      - prompt-selection
    related_skills:
      - agentic-eval
      - prompt-injection-defense
---

# Prompt Engineering — The 20 Core Concepts

Which prompting technique to reach for, why, and the exact move — as a selection
table rather than an essay. This skill is the *choosing* layer; it does not cover
production hardening (5-layer prompt anatomy, quality scoring, A/B discipline,
injection defense, per-platform delimiter conventions) or judge calibration —
that is `agentic-eval`'s and `prompt-injection-defense`'s territory.

## When to Use

- Writing or rewriting a system prompt, skill body, or long task prompt
- A prompt produces vague, unreliable, or unusable output and you need a specific fix
- Choosing between zero-shot, few-shot, chain-of-thought, tree-of-thought, or ReAct
- Designing tool-use loops or multi-stage agent workflows
- Debugging inconsistent output, runaway token cost, or broken JSON output
- Don't use for: single-turn factual questions, injection/safety hardening
  (`prompt-injection-defense`), or judge design and eval harnesses (`agentic-eval`)
- Don't use as a substitute for running the prompt and inspecting the output

## The 20 Concepts (selection table)

| # | Technique | Reach for it when | The move |
|---|-----------|-------------------|----------|
| 1 | **Zero-shot** | Task is common, unambiguous, one-shot answer | State the task plainly: "Explain quantum computing simply." No examples. |
| 2 | **Few-shot** | Format or judgment is easier to show than describe | Give 1–5 input→output pairs, then the real input. Match their pattern exactly. |
| 3 | **Chain-of-Thought** | Math, logic, multi-step reasoning, planning | "Let's think step by step. Plan → Reason → Answer." |
| 4 | **Role prompting** | Output tone/register or domain expertise matters | "You are a senior data scientist…" then the constraints. |
| 5 | **Instruction prompting** | Output is vague because the ask is vague | Be explicit: length, format, audience, what to exclude. "Summarize in 3 bullets." |
| 6 | **Output formatting** | Output gets parsed, or must be consistent | Give a schema/shape, not a label: `{"summary": …, "key_points": [...]}` |
| 7 | **Temperature control** | Inconsistent vs. creative — you're tuning the wrong knob | Extraction/deterministic: low temp (≈0.0–0.3). Ideation: high (≈0.7–1.0). |
| 8 | **Prompt chaining** | Task has distinct phases with different goals | Split: Plan → Research → Write. Each stage's output feeds the next as input. |
| 9 | **Self-consistency** | One sample is unreliable on reasoning tasks | Sample N answers at higher temp, take the majority/consensus. Costs N×. |
| 10 | **RAG** | The answer must come from specific documents, not memory | Retrieve relevant chunks first, put them in context, instruct: answer only from these. |
| 11 | **Prompt templates** | The same shape is reused across inputs | Parameterize role + task + `{input}` + format. Keep tone stable across instances. |
| 12 | **Guardrails** | Anything user-facing, untrusted input, or with side effects | Explicit never-list (no harm, no PII, no secret leakage), placed before the instructions. |
| 13 | **Dynamic prompting** | One prompt must serve beginner/expert/pro users | Branch on user type: adjust vocabulary, depth and examples per segment. |
| 14 | **ReAct** | Real tasks needing tools, search, or environment feedback | Thought → Action (tool call) → Observation, repeat. |
| 15 | **Tree-of-Thought** | Many plausible paths, one-shot CoT gets stuck | Generate 2–3 candidate paths, evaluate each, commit to the best. |
| 16 | **Prompt compression** | Long context, repeated calls, token bills | Strip redundancy and hedges; keep constraints + the ask. Same behavior, fewer tokens. |
| 17 | **Multi-modal** | The answer depends on an image/diagram/screenshot | Attach the image AND say what to look at: "What is this? Focus on the wiring." |
| 18 | **JSON mode** | Output feeds code | Constrain to JSON, parse safely (schema validation / try-except, never blind `eval`). |
| 19 | **Prompt evaluation** | You can't tell if a change helped | Score quality/relevance, track success rate over N runs, iterate on data not vibes. |
| 20 | **Prompt optimization** | The prompt works but isn't good enough | Vary one element at a time, measure, keep the winner. Iterative, not one-pass. |

## Choosing under time pressure

- **Simple, common task** → 1 (zero-shot) + 5 (instruction) + 6 (format).
- **Output must match a shape (code, parser, table)** → 2 (few-shot) + 6 (format) + 18 (JSON mode).
- **Reasoning / math / planning** → 3 (CoT); if still unreliable, 9 (self-consistency) or 15 (ToT).
- **Needs tools or live data** → 14 (ReAct); if the data is documents, 10 (RAG).
- **Multi-stage work** → 8 (chaining), not one giant prompt.
- **Production / user-facing** → 12 (guardrails) + 19 (evaluation), always.
- **Several user levels in one product** → 13 (dynamic) or separate 11 (templates) per level.
- **Cost or latency pain** → 16 (compression) + 7 (temperature) before adding more prompt.

## Procedure

1. **Name the failure mode** — vague output, wrong format, unreliable reasoning,
   wrong tone, token bloat, or unparsed JSON. Each maps to a different row above.
2. **Pick the smallest technique set** from the selection path. One or two concepts,
   not six; each added technique costs tokens and hides the cause of a regression.
3. **Write the prompt** with the task stated before the constraints where the
   technique allows it, and all never-rules grouped together.
4. **Run it on ≥3 real inputs** — not a hypothetical one — and read the outputs.
5. **Change one variable**, re-run, keep the better version (concept 20). Record
   what changed and why.
6. **Lock the shape** for anything machine-read: validate the JSON/schema in code,
   not by eye (concept 18).

## Pitfalls

1. **Few-shot examples that disagree with the instructions** — the examples win.
   Audit them (wrong label, wrong format) before blaming the model.
2. **CoT on tasks that don't need it** — costs latency and tokens on lookups and
   translation, and flattens creative voice. Apply the table, not CoT-by-default.
3. **Guardrails buried at the bottom** — constraints must precede the task
   instructions, or later content overrides them.
4. **"Output JSON" with no schema** — models invent keys. Ship the exact shape plus
   one example.
5. **Self-consistency on a non-reasoning task** — N× the cost for noise. It only
   pays where independent samples can genuinely disagree.
6. **Chaining without a contract between stages** — each stage needs a defined
   output shape, or errors compound silently.
7. **Changing several prompt elements at once** — no attribution, no learning.
8. **Trusting a "better" prompt without running it** — a prompt is a hypothesis
   until outputs are scored on real inputs.

## Verification

A prompt change is done when:

- [ ] It ran on ≥3 real inputs
- [ ] Parsed output validated programmatically (JSON parses, schema matches)
- [ ] Format compliance checked against the requested spec
- [ ] Token cost compared to the previous version if you compressed (16) or chained (8)
- [ ] Where reliability matters: N runs, success rate recorded (19), one variable
      changed per pass (20)

## References

- `references/20-concepts-cheatsheet.md` — verbatim transcription of the source
  poster (Akhil Meesala, "20 Prompt Engineering Concepts: A Compact Cheatsheet with
  Ideas, Use Cases and Visualizations"), including every use case and diagram note.
