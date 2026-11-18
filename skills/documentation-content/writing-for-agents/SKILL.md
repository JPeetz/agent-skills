---
name: writing-for-agents
description: Writing documents for agents. Use when creating or editing a skill, subagent, prompt, AGENTS.md / CLAUDE.md, or a doc behind a pointer.
---

Reference for writing any document an agent consumes: a skill, an `AGENTS.md` / `CLAUDE.md`, a doc reached by a pointer. The packaging differs; the writing does not: the same levers make each one predictable, since the agent takes the same _process_ every run rather than producing the same output.

When the document you're writing is a skill, read [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md) for frontmatter, invocation choice, and router skills. When it is an instruction file — `AGENTS.md`, `CLAUDE.md`, README, runbook — read [`references/default-to-permission.md`](references/default-to-permission.md) for the standing stance: gates only on the irreversible, restrictions dated and reasoned.

## Context pointers

A **context pointer** is a reference held in the agent's context that names some out-of-context material and encodes the condition for reaching it. A skill's description is one; a line in `AGENTS.md` naming a doc is the same object. The pointer's _wording_, not its target, decides when — and how reliably — the agent reaches the material. A must-have target behind a weakly worded pointer is a variance bug: sharpen the wording first, and inline the material only if sharpening fails.

A pointer does two jobs: state what the material is, and list the **branches** that should trigger reaching it (a branch is a distinct case the document handles, so different runs take different paths through it). Every word of an always-loaded pointer costs on every turn, so it earns even harder pruning than the body:

- **Front-load the leading word**: the pointer's head does the triggering.
- **One trigger per branch.** Synonyms that rename a single branch are one branch written twice; collapse them and keep only genuinely distinct branches.
- **Cut identity the body already carries.**
- **Write for truncation**: skill lists are capped (Codex shortens or drops descriptions under pressure). The trigger words and the negative boundary ("not for X") belong at the head, never the tail — whatever survives truncation is what routes.
- **"Always" is not a branch.** A pointer that fires unconditionally ("read X before every task") is context load pretending to be a pointer. Keep short rules needed throughout the work inline; leave detailed reference behind a pointer naming when to consult it, even if it applies to every task.

## The two loads

Every document and pointer you add spends one of two budgets:

- **Context load** is the cost of always-loaded material on the agent's window: an `AGENTS.md` line, a skill description, anything sitting in context every turn, paid whether it fires or not.
- **Cognitive load** is the cost on the human: which documents exist and when to reach for each. The human is the index. Not a cost to minimise: it is the price of human agency; spend it where human judgement matters, remove it where it does not.

Material reached only through a pointer escapes context load at the price of the pointer's own line; material with no pointer at all rides entirely on cognitive load.

## Information hierarchy

A document is built from two content types: **steps** (the ordered actions the agent performs) and **reference** (definitions, rules, facts consulted on demand). The two mix freely: all steps (a recipe), all reference (a review's rules, this skill), or both. The core decision is where each piece sits on the **information hierarchy**, a ladder ranked by how immediately the agent needs the material:

1. **In-file step** is the primary tier: what the agent does, in order.
2. **In-file reference** is consulted on demand. Often a legitimately flat peer-set (every rule of a review on one rung), which is a fine arrangement, not a smell.
3. **Disclosed reference** lives in a separate file behind a context pointer, loaded only when the pointer fires — anything from a sibling file to external material any document can point at.

Push too little down and the top bloats; push too much and you hide material the agent actually needs. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder — out of the main file, behind a pointer — so the top stays legible. Less a token optimisation than the hierarchy's protection. Branching is the cleanest test: inline what every branch needs, disclose what only some reach. Undisclosed reference in a steps document buries the steps; attending to them becomes a coin-flip — a variance lever, not just legibility.

**Co-location** is the within-file companion: where the ladder decides _how far down_ a piece sits, co-location decides _what sits beside it_ once there. Keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours with it. The test: does it read like documentation written for the agent? Grouped material does; scattered doesn't. (Distinct from duplication, which repeats one meaning in two places; scattering fragments one meaning across many.)

**Sprawl** is the failure mode here: a document simply too long, even when every line is live and unique. Attention thins across the excess, and every extra line is one more to keep relevant. The cure is the ladder: disclose reference behind pointers, and split by branch or sequence so each path carries only what it needs.

## Steps and completion criteria

Every step ends on a **completion criterion**, the condition that tells the agent the work is done. Two properties make it a lever:

- **Clarity**: can the agent tell done from not-done? A vague bound ("understanding reached") invites **premature completion**: ending the step before it is genuinely done, attention slipping to _being done_. The visible steps still ahead (the **post-completion steps**) supply the pull; the criterion's clarity is the resistance. Defend in order: **sharpen the bound first** (local and cheap); only if it is irreducibly fuzzy _and_ you observe the rush, hide the later steps by splitting the sequence. Hiding only works across a real context boundary (a hand-off or a subagent dispatch; an inline call leaves the later steps in context and clears nothing).
- **Demand**: how much it requires. "Every modified model accounted for" forces thorough work where "produce a change list" does not. Demand drives **legwork** (the digging the agent does within the work, latent in the wording rather than written as its own step), and it is not step-bound: "every rule applied" binds a body of flat reference just as "every step done" binds a sequence, which is how an all-reference document still carries an exhaustiveness bar.

The strongest criteria are both checkable and exhaustive.

**Done means done.** Capable models can stop at first implementation and report back while work remains. If done includes running it, inspecting the result, and fixing what fails, say so — the whole criterion, not the first leg. The mirror failure is the **premature gate**: an unconditional "ask before X" on a safe, reversible step the document itself was invoked to perform. Invocation is authority for the document's core safe operations; reserve confirmation for what is irreversible, shared, or outside the requested scope, and state a gate once rather than per phase — a repeated gate reads as accumulating exceptions, not as emphasis.

## When to split

Splitting one document into two adds a document to the human's index and usually a pointer line to context — split only when the cut earns it:

- **By sequence**: split a run of steps where the post-completion steps tempt the agent to rush the one in front of it. Keeping them out of view drives more legwork on the current task. Beware the reverse: a merged sequence exposes each step to what follows it, inviting premature completion.
- **By invocation**, skill-specific: see [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md).

## Leading words

A **leading word** is a compact concept already living in the model's pretraining that the agent thinks with while running the document (_lesson_, _fog of war_, _tracer bullets_). Repeated as a token, never as a sentence, it accumulates a distributed definition and anchors a whole region of behaviour in the fewest tokens, by recruiting priors the model already holds. Coining your own works if you define it clearly, but a made-up word recruits no priors: you pay in definition tokens what a pretrained word gives free; reach for an existing word first.

It anchors twice. In the body, _execution_: the agent reaches for the same behaviour every time the word appears, and inside flat reference it focuses attention on a class of thing to look for. In a pointer, _invocation_: when the same word lives in your prompts, your docs, and your codebase, the agent links that shared language to the material and reaches it more reliably.

Refactor restatements into leading words: a triad spelled out at three sites, a pointer spending a sentence on one idea — each a passage begging to collapse into a single token:

- "fast, deterministic, low-overhead" → _tight_ (a _tight_ loop).
- "a loop you believe in" → _red_, turning a fuzzy gate into a binary observable state (the loop goes _red_ on the bug, or it doesn't).

You win twice: fewer tokens, and a sharper hook for the agent to hang its thinking on. Assume every document is carrying restatements that leading words retire. Go find them.

**Negation** is the failure mode beside this lever: a prohibition makes the forbidden behaviour _more_ available, not less — _don't think of an elephant_ — since the negation is a weak modifier the strongly-activated concept overruns, and the ban half-reads as an instruction. Prompt the **positive**: state the target behaviour ("write one-line comments") so the banned one is never spoken. A prohibition earns its place only as a hard guardrail you cannot phrase positively; even then, pair it with the positive target so attention lands on what to do.

## Self-sufficiency and checkable rules

- **Write for a reader with no chat history.** Nothing leans on "as discussed", a prior session, or knowledge that lives in someone's head; the agent that opens the document cold has only the document. Test: a fresh session can act on it by reading alone.
- **State each rule as an observable condition, with its why beside it.** "Keep it clean" cannot be decided; "no function over 40 lines, because the reviewer reads one screen at a time" can, and the why lets the agent handle the case the rule did not foresee. Test: pass or fail follows from the text alone.
- **A deferral names its when.** "Later" or "in a follow-up" reads as unstarted or refused; state the step, session, or release that picks it up. Test: every deferral carries its trigger or time.
- **Close a handoff, report, or ticket on a next action** the reader can start now (the command, the pointer, the question), because a summary-only close makes the reader re-derive what to do first. Test: the last line answers "what do I do next?".
- **Number any procedure of three or more steps** so a reader can name step 3 and resume without re-reading; this is a reference handle, not a licence for an itinerary (see Pruning). Test: each such procedure carries stable numbers.

## Prose an agent speaks to a person

Replies and reports are not documents, but the same economy applies, with three additions:

- **Quote the core verbatim**: code, commands, paths, exact error text, numbers, units. A paraphrased error is a wrong error. Test: each quoted artifact matches tool output byte for byte, and no negator (not, never, only, except) was dropped.
- **Narrate only what the reader cannot see.** Tool calls are visible; announce the finding, the decision, or the next action. Test: no line describes a step the reader watched happen.
- **Write full sentences for warnings, irreversible confirmations, and ordered steps**, because a fragment can reorder steps or blur a risk. Terse is the default register, not the safety register.

## Pruning

- Keep each meaning in a **single source of truth**: one authoritative place, so changing the behaviour is a one-place edit. **Duplication** (the same meaning in more than one place) costs maintenance and tokens, and inflates a meaning's prominence on the ladder past its real rank. (The accidental inverse of a leading word, which repeats a token on purpose, never the meaning.)
- The **environment** is a source of truth too (`package.json` scripts, config files, the directory layout, `--help` output), and a document that restates it is a **cache**: a copy of a lookup, earning its load only when the lookup is expensive. Cache what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config confesses. Leave the one-file, one-command lookups to the environment, where they cannot go stale.
- Reference external documentation by **name**, wrapped in backticks and resolved through the fetching skill (`$docs`, `$find-docs`): "read `Claude Code hooks` before changing an event". Spell out a full URL only in an index or table of contents (`GLOSSARY.md`). A pasted URL goes stale, spends tokens, and bypasses the skill that knows where current docs live.
- Check every line for **relevance**: does it still bear on what the document does? A line loses relevance by never bearing on the task (mere exposition, or a branch that should be disclosed) or by going stale as the behaviour or world it describes changes. Without a pruning discipline the default fate is **sediment**: stale layers that settle because adding feels safe and removing feels risky, until you must core down through them to find what is still live.
- Hunt **no-ops** sentence by sentence: an instruction the model already obeys by default pays load to say nothing. The test (does it change behaviour versus the default?) is model-relative, not reader-relative: two people disagreeing about a no-op disagree about the default, and settle it by running the document, not by debate. When a sentence fails, delete the whole sentence rather than trim words from it. The test also grades leading words: a word too weak to beat the default (_be thorough_ when the agent is already thorough-ish) is a no-op, and the fix is a stronger word (_relentless_), not a different technique.
- Prefer **intent plus constraints** over exhaustive itineraries. Models keep getting better at nuance; step-numbered recipes that once scaffolded weaker models now constrain stronger ones and fossilize against the next. Keep the ordering only where the order itself is load-bearing — pinned artifact formats, compatibility strings, sequences where a later step's existence would pull the current one short.
