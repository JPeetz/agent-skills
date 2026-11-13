---
name: agent-skills-creator
description: Use this skill when writing a new agent skill, auditing or rewriting an existing SKILL.md, trimming redundant instructions, choosing a skill's structural pattern, or fixing a skill that never triggers or triggers on the wrong prompts. Covers the full lifecycle — pattern selection, frontmatter and description design, body and reference files, validation, and the evidence-based keep, cut, merge, or retire decision.
version: 0.1.0
author: "Matthew Blode (mblode), Skill Foundry"
license: MIT
---

# Agent Skills Creator

## Overview

A skill is a routing decision plus an operating procedure. The routing decision is the description; the procedure is the body. Most broken skills fail at one of those two places, and the failure modes look nothing alike: a description without the words users actually type never loads, while a body that dumps a specification into the main file loads and buries the model in text it cannot act on.

This skill covers the whole lifecycle in the Agent Skills open format — creating a skill from nothing, auditing one that misbehaves, simplifying a collection that has grown redundant, and retiring what no longer earns its context cost.

**IS:** creating new agent skills, and auditing, scoring, simplifying, or rewriting existing ones — SKILL.md, references, rules folders, evals.
**IS NOT:** AGENTS.md/CLAUDE.md instruction files, general documentation or prose quality, or writing the domain content itself. This skill governs the container, not the expertise inside it.

## Choose a Mode

| Situation | Where to go |
|-----------|-------------|
| New skill | The Creation Workflow below, Steps 1–8 |
| Existing skill is bloated, vague, or contradictory | Audit first (below), then rewrite the body and rejoin at Step 5 |
| Skill never triggers, or triggers on the wrong prompts | Fix the description, not the body. Body edits cannot repair routing |
| Two skills cover the same job | Merge or retire. Pick one owner and make the other a reference file |
| Whole collection needs pruning | Audit each skill's keep decision, then the collection ledger |
| Choosing how to shape the skill | `references/skill-patterns.md` |

### Audit Before Rewrite

Never rewrite a skill you have not scored. Read the current SKILL.md end to end and answer, in writing:

1. Does the description name what users actually say, or a category name the model cannot route on?
2. Is each body section load-bearing, or is it general coaching the model already follows?
3. Does the body contradict itself anywhere — a rule, then an exception that dissolves it?
4. Does any step read as a stop condition ("present for review") that halts work the user asked for?
5. Are the reference files split by loading condition, or by line count?
6. Do the evals exist, and would the skill pass them without the skill?

Cut what fails 2 and 3, repair 1 and 4, restructure 5, and write 6 before you ship. A rewrite that cannot name what was wrong is a paraphrase.

## Reference Files

| File | Read when |
|------|-----------|
| `references/authoring-tips.md` | Default when writing or cutting body content: descriptions, frontmatter, body structure, degrees of freedom |
| `references/skill-patterns.md` | Choosing a structural pattern, or deciding that an existing skill is the wrong shape |

## Creation Workflow

Copy this checklist to track progress:

```text
Skill creation progress:
- [ ] Step 1: Choose a pattern
- [ ] Step 2: Create the directory and frontmatter
- [ ] Step 3: Write the SKILL.md body
- [ ] Step 4: Add reference or rule files
- [ ] Step 5: Validate
- [ ] Step 6: Register the skill in README.md
- [ ] Step 7: Smoke-test what a fresh session actually loads
- [ ] Step 8: Evaluate and iterate
```

### Step 1: Choose a pattern

Check whether an existing skill already owns this job. Two skills with the same trigger compete, and the model picks arbitrarily. If the job is close but not identical, extend the existing skill or add it as a reference file.

Then pick a shape: simple/hub, workflow, rules-based, or mixed. `references/skill-patterns.md` has the shapes, what each is for, and the problem-to-pattern table.

### Step 2: Create the directory and frontmatter

Create `skills/<category>/<skill-name>/SKILL.md` with `---` on line 1, then `name`, `description`, `version`, `author`, and `license`.

- **Name**: lowercase, hyphenated, matching the directory exactly. The validator enforces this. Use a name a model could route on — `postgres-migration-safety`, not `db-helper`.
- **Description**: a routing trigger, not a human summary. Start with "Use this skill when", then the phrases users actually type, most valuable case first because hosts trim from the tail. Keep it under 1024 characters and short enough to sit comfortably beside its siblings in a listing.
- **Version and author**: keep them truthful. Bump the minor version on a rewrite that changes behaviour.

Decide where the skill runs before adding fields. Use portable fields; put genuine runtime prerequisites in `compatibility`. Host-specific fields need current host documentation and a deliberately host-specific package.

State authorization boundaries in the body when a workflow deploys, sends, or spends — and grant the safe loops just as explicitly. The body carries both sides of that envelope.

### Step 3: Write the SKILL.md body

Read `references/authoring-tips.md` first. It carries the judgement on what to include, how hard to say it, degrees of freedom, and progressive disclosure.

Order that survives review: a short overview that says why the skill exists, the IS/IS NOT contract, the procedure as numbered steps, **Gotchas**, then **Anti-patterns**. Build Gotchas from failures you have actually observed — a wrong turn the model took, a tool call that silently did nothing. It is the highest-signal section in any skill, and it cannot be invented from imagination.

Say where the work ends in terms of scope, not as a review checkpoint nobody asked for. A step reading "stop here and present for review" ends the task on current models even when the user wanted the whole job.

### Step 4: Add reference or rule files

- **Workflow/mixed**: a `references/` folder, each file linked from SKILL.md with an explicit "read when" condition. Unlinked references are dead weight.
- **Rules-based**: a `rules/` folder of individually addressable checks, one concern per file.
- **Simple/hub**: track files alongside SKILL.md, linked from a tracks table.

Split by loading condition, not line count: two topics read at different moments are two files. Prefer a reference that is code — an existing implementation or test suite pins a contract better than prose describing it.

### Step 5: Validate

Run the repository validator — `validate_skill.py`, inside the repository's `scripts` folder — against the completed skill directory, from the repository root.

The validator returns JSON and exits non-zero on any issue. It checks mechanical gates only: frontmatter parses, `name` is present and matches the folder, `description` exists and starts with "Use this skill when", the body stays under 500 lines, and any folder the body references with a trailing slash actually exists. Fix every issue. A clean run establishes format compliance and nothing about behavioural quality — no validator can tell you whether the skill helps.

### Step 6: Register the skill in README.md

Add the skill's row under the matching category heading, and bump the stated skill count. A skill that exists but is unlisted is invisible to anyone browsing the repo, and the count drifts silently.

### Step 7: Smoke-test

Verify what a fresh session actually loads, not what is on disk in your editor. Install the edited local source into a disposable target, then read back the loaded SKILL.md and one bundled reference. Never overwrite a global installation to smoke-test an edit, and never treat the remote default branch as evidence for unpushed changes.

### Step 8: Evaluate and iterate

Write 2–3 scenarios in `evals/evals.json`. Then measure with-skill against without-skill in fresh sessions. That comparison is the keep test: the skill must improve the job enough to justify its cost in every session's context.

Test routing separately with should-trigger and near-miss prompts — a routing failure is invisible to body evals. Ablate any rule you suspect is dead weight: delete it, rerun, keep it only if something regresses. If nothing regresses, the rule was coaching, and coaching is what makes a skill long enough to be ignored.

## Gotchas

- **The installed copy is a copy, not a link.** Editing the repo changes nothing in a running session, and the stale copy loads silently. A skill can be several commits behind while appearing correct. Always confirm an evaluation loaded the edited local source.
- **A description can pass every check and still never route.** The validator sees "Use this skill when" and stops. It cannot see that the trigger words are ones nobody types. Only a routing eval finds this.
- **Descriptions pass individually and fail together.** Each under 1024 characters can still overrun the host's listing budget as a set, at which point the host shortens all of them and drops the "Use when" clauses first. Judge a description next to its siblings.
- **A reference chain is a load condition, not a file path.** If the model never opens the reference, move the load condition into SKILL.md rather than rewording the same dependency.
- **A body over 500 lines usually means the specification belongs in a reference.** Trimming prose to fit the limit preserves the mistake.
- **Rules that restate good practice dilute the rules that matter.** The model already knows to be careful and to test its work. A skill full of universal advice teaches it that this file is skimmable.

## Anti-patterns

- Dumping the full specification into the SKILL.md body instead of a reference file
- Time-sensitive content ("before August 2026, use..."), including model names as the reason a rule exists
- Vague names (`helper`, `utils`, `tools`, `documents`, `data`) that give the model nothing to route on
- A step that ends the turn for review when the user asked for the complete job
- Skills that duplicate an owner already in the collection, leaving routing to chance
- Shipping without an eval, then treating "it looks good" as the keep decision

## Related Skills

- `skill-miner` for finding repeated workflows in session history worth turning into a skill
- `skill-lifecycle-foundry` for mining, personalizing, and generalizing skills across a fleet
- `interview-me` when the requested skill's scope is genuinely underspecified
