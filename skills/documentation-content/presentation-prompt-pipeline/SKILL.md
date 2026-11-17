---
name: presentation-prompt-pipeline
description: Use this skill when building or repairing a presentation with an AI model — the six staged prompts (blueprint → structure → story frame → visual direction → content → build) that turn an idea into a deck with one message, each stage producing an artifact and a checkable gate, with prompt templates, eight named failure modes, and a deck_lint.py script that mechanically enforces short titles, tight bullets, speaker notes, a two-font and three-colour ceiling.
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
      - presentations
      - slides
      - storytelling
      - prompting
      - deck-review
      - pptx
    related_skills:
      - spec-writer
---

# Presentation Prompt Pipeline

Six staged prompts that take a deck from idea to presentable, in the order the
work actually has to happen: message → outline → story → visual direction → copy
→ file. Each stage produces an artifact the next stage consumes, and each has a
gate you can check before spending the next prompt. This skill is the planning
and review layer; the mechanical creation of the `.pptx` is plain `python-pptx`.

## When to Use

- Building a deck with a model from a brief, a document, or a pile of notes
- A deck exists but reads as a wall of bullets, or says nothing memorable
- Pitching, teaching, or reporting where the *ask* on the last slide matters
- Reviewing someone else's deck against a repeatable standard
- Don't use for: decks whose content is fixed by a template or mandate (drive
  `python-pptx` directly), format conversion, or as a substitute for rendering
  the slides and looking at them

## The Six Stages

| # | Stage | Produces | Gate before moving on |
|---|-------|----------|------------------------|
| 1 | **Blueprint** | One message, audience, 3 emotional angles, slide flow, target slide count | The deck's single message fits one falsifiable sentence, and you can name who it changes |
| 2 | **Structure** | Slide-by-slide outline: one-line purpose and intended feeling per slide | Every slide has a purpose line; no slide exists "for context" |
| 3 | **Story frame** | Hook → Problem → Insight → Solution → Proof → Takeaway beat sheet mapped onto slides | All six beats present; the last slide carries exactly one action |
| 4 | **Visual direction** | Emotional visual intent, chart-for-data choice, icon/grid for lists, 3-colour palette, font pairing | Palette and fonts are named with hex/font values and cover every slide |
| 5 | **Content** | Titles ≤6 words, 3–5 bullets ≤10 words, one speaker note per slide, audience-matched tone | `deck_lint.py` passes on the draft text |
| 6 | **Build** | The `.pptx`: bold titles, tight bullets, notes on every slide, clean flow | `deck_lint.py` passes on the real file; rendered slides reviewed by eye |

## Prompt Templates

Each prompt names its input and the shape of its output — that is what makes the
output checkable rather than merely plausible.

**1 — Blueprint**

> You are a presentation strategist. From the material below, give me: (a) the ONE
> message in a single sentence, phrased as a claim, not a topic; (b) the audience
> and the three things they care about most; (c) three emotional angles I could
> take and the risk of each; (d) a slide-by-slide flow in ≤12 steps; (e) the ideal
> slide count and why that number. Be specific — no generic advice.
> Material: {brief}

**2 — Structure**

> Using this blueprint, write a slide-by-slide outline. For each slide: a one-line
> purpose ("this slide makes the audience ___"), what they should feel, and the
> single idea it carries. Flag any slide that repeats another's job. {blueprint}

**3 — Story frame**

> Rewrite the outline into this six-beat story frame: Hook (grab attention),
> Problem (the pain), Insight (the surprise), Solution (what to do), Proof (one
> statistic or example), Takeaway (one action). Map each beat onto slide numbers,
> and say in one line what the audience should feel at each beat. {outline}

**4 — Visual direction**

> For each slide, specify: the emotion the visual must carry, whether the data is
> better shown as a bar, line, pie, or a single big number and why, whether lists
> become icons or a grid, one 3-colour palette with hex codes (background, ink,
> accent), and one heading/body font pairing available in standard Office or
> Google fonts. No stock-photo descriptions; describe the composition.

**5 — Content**

> Write the final copy per slide: a title of ≤6 words, 3–5 bullets of ≤10 words
> each (no sentences), and one speaker note of 2–3 sentences that says what to
> say out loud — not a restatement of the bullets. Match this tone: {tone}.
> Audience: {audience}. Keep the Takeaway slide to a single action.

**6 — Build**

> Produce a python-pptx JSON spec for this content: 16:9, title+content layouts,
> the palette and fonts above, speaker notes included per slide. Then the deck is
> built and linted — not hand-assembled.

## How to Run

Stages 1–5 are prompts: run each in a **fresh** context with the previous stage's
artifact pasted in, not as one mega-prompt. Stage 6 builds the file and then
lints it:

```bash
uv run --with python-pptx scripts/deck_lint.py deck.pptx
```

The linter is the only script here. It reads a `.pptx`, prints JSON or a human
line per finding, and exits `0` clean, `1` with findings, `2` unreadable file.
Tune the ceilings per deck:

```bash
uv run --with python-pptx scripts/deck_lint.py deck.pptx \
  --max-title-words 8 --max-bullets 6 --max-bullet-words 12
```

Rules it enforces by default: title ≤6 words, ≤5 bullets per slide, ≤10 words per
bullet, speaker notes on every slide, ≤2 font families, ≤3 explicit text colours.

## Quick Reference

| Symptom | Where the process broke |
|---|---|
| Message is fuzzy | Stage 1 accepted a topic ("Q3 review") instead of a claim |
| 30 slides of bullets | Stage 2 outline has no purpose lines, so nothing could be cut |
| Every slide feels the same | Stage 4's emotional intent was never specified |
| Titles are sentences | Stage 5's ≤6-word rule, enforced by the linter |
| Data slide is unreadable | Stage 4: one chart type per idea, one number per chart |
| Deck "done" but not delivered | Notes missing, or the last slide has no single ask |

## Pitfalls

1. **One mega-prompt.** Asking for message + outline + copy + design at once
   produces a generic deck, because the model optimises every constraint at once.
   The stages exist so each constraint gets attention.
2. **A blueprint that names a topic, not a claim.** "Q3 review" is not a message;
   "Churn doubled and ownership fixes it" is. Stage 1's output must be falsifiable.
3. **Bullet walls dressed as structure.** 5 bullets × 12 words reads as prose. The
   ≤10-word rule forces one idea per bullet.
4. **Decoration before storyline.** Picking a theme or template first locks you
   into layouts that fight the story; stage 4 comes after stage 3 for that reason.
5. **Speaker notes that repeat the bullets.** Notes are the spoken track; if they
   duplicate the slide, the deck is a document, not a presentation.
6. **Palette creep.** Every extra accent colour dilutes the one that matters; the
   linter caps explicit text colours at three by default.
7. **Trusting the outline instead of the rendered slide.** Overflow, overlap and
   contrast problems exist only in the render — always look at the slides.
8. **A Takeaway slide with three asks.** One action. Three asks means the deck has
   three messages and none of them lands.

## Verification

- `deck_lint.py` exits 0 on the final file
- Slides rendered to images and reviewed — no overflow, no contrast failure, no
  orphaned bullet
- Stage 1's one-sentence message appears near the front, and the Takeaway slide
  repeats the action rather than the message
- Every slide traces to a stage-2 purpose line; none is "context"

## Reference

- `references/six-prompts-cheatsheet.md` — transcription of the source infographic
  (Cyberman AI, "How to build a presentation using AI: 6 powerful prompts"),
  including each stage's checklist items.
