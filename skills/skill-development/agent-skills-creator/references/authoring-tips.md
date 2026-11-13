# Authoring Tips

Judgement for writing or cutting the contents of a skill. Read this before drafting a body.

## The description is the whole product

A skill only exists when it loads. The description is the only thing the host sees before deciding, so write it as a trigger rather than a summary of the file.

- **Start with "Use this skill when"** — repositories here enforce it, and hosts weight it.
- **Use the user's words, not the domain's.** People say "my skill never triggers", not "description-routing mismatch".
- **Lead with the highest-value case.** Hosts trim descriptions from the tail when a listing runs over budget. The last clause you wrote is the first one to disappear.
- **Name the near-misses.** "NOT for interactive sessions" or "not for general docs" stops the skill loading where it cannot help. Every false load costs context and dilutes the trigger.
- **Stay under 1024 characters, and shorter than that in practice.** Judge length next to sibling descriptions, not alone — a collection of individually-legal descriptions can overflow the shared listing budget, and the host shortens all of them.
- **No category names.** `development` and `tooling` give a model nothing to route on. The concrete task does.

Test: if a user's phrasing would not appear anywhere in your description, the skill will not fire for them.

## Frontmatter

```yaml
---
name: kebab-case-matching-the-folder
description: Use this skill when <trigger phrases>. <what it does>.
version: 0.1.0
author: "Name (handle)"
license: MIT
---
```

- `---` on line 1, closed properly. A leading blank line breaks parsing in most hosts.
- `name` must equal the directory name. The validator fails the skill otherwise.
- Add `compatibility` only for real runtime prerequisites (a CLI, a language, credentials). Do not list "an LLM".
- Host-specific fields (`allowed-tools`, `context`, `hooks`) require current documentation for that host and a deliberately host-specific skill. Portable skills should not assume them.
- Bump `version` when behaviour changes; leave it alone for typos.

## Body structure

Order that survives review, roughly top to bottom:

1. **Overview** — why this skill exists. Two to four paragraphs. The mechanism, not the marketing.
2. **IS / IS NOT** — one line each. This is the boundary that keeps the skill from absorbing neighbouring jobs.
3. **When to use / when not to** — optional if the description already carries it; keep at most a short list.
4. **Procedure** — numbered steps, each one action with a success condition. If a step needs a judgement call, say what the call is.
5. **Gotchas** — failures you have actually seen. Highest-signal section in any skill.
6. **Anti-patterns** — the wrong shapes, listed flat.
7. **Related skills** — where to go instead. Prevents overlap at the source.

## What to include

Include what the model gets wrong without the skill. Exclude everything else.

**Belongs:** a specific order of operations that matters; a non-obvious tool quirk; a constraint the model would not infer (rate limits, an approval gate, a naming rule); a definition of done the user cares about; a reference implementation that pins a contract.

**Does not belong:** "be thorough", "consider edge cases", "write clean code", "communicate clearly". The model already does these. A body padded with universal advice teaches the reader that the file is skimmable, which is how the load-bearing lines get ignored.

If you cannot name the wrong turn a line prevents, delete the line.

## Degrees of freedom

Match prescription to risk:

- **Fragile, ordered, or irreversible** (deploy, migration, send, spend): exact commands, exact order, explicit confirmation gates, and an explicit statement of what the agent may do without asking.
- **Judgement-heavy** (review, design, diagnosis): principles plus a worked example, and let the model choose the route.
- **Mixed**: hard-gate the irreversible steps, leave the analysis free.

Over-prescription on a judgement task produces mechanical, low-quality output. Under-prescription on an irreversible task produces incidents.

## Cutting

- One rule per idea; no rule restated in three places.
- If a section is a specification longer than ~50 lines, it is a reference file with a load condition.
- Contradictions are worse than gaps: a rule followed by an exception that dissolves it means the model picks whichever it read last.
- Delete any "stop here and present for review" step that halts work the user asked for. Put a scope-of-done line in the overview instead.
- Ablate rather than argue: remove a suspect rule, rerun the evals, restore it only if something regresses.

## Time

Skills outlive the moment they were written. Avoid dated instructions, model names as justification, and tool versions in the imperative. If a rule only makes sense for one release, write the condition, not the release.
