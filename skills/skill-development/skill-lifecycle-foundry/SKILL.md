---
name: skill-lifecycle-foundry
description: Use when mining, authoring, and generalizing agent skills.
version: 1.0.0
license: MIT
author: Skill Foundry
platforms:
  - linux
  - macos
metadata:
  tags:
    - agent-skills
    - skill-authoring
    - skill-mining
    - skill-personalizing
    - skill-generalizing
    - progressive-disclosure
    - lifecycle
  complexity_level: intermediate
  managed_workflows:
    - discovering_repeated_workflows
    - authoring_new_skill
    - personalizing_existing_skill
    - generalizing_for_release
---

# Skill Lifecycle Foundry

The agent-skill lifecycle is a loop: you mine real usage for repeated workflows,
author those into `SKILL.md` files, personalize them to the local user's tools and
phrasing, generalizing them for public release, and keep them honest through a
validation gate. This is the meta-skill that governs that whole loop. It governs
the *other* skills in your inventory, not a single task — it tells you how to
discover, write, tune, and ship them safely.

It ships one small, optional executable — `scripts/scan_sessions.py` — a deterministic
first-pass miner for the mining step. It is stdlib-only and safe to run on any
archive; the rest of the skill is procedure and templates, because session layouts
vary too much for a bigger script to be trustworthy.

## When to Use

Use this skill when you want to:

- Mine an agent session history, memory archive, or repo history for recurring
  workflows that deserve their own skill file.
- Draft a brand-new `SKILL.md` from a spec, meeting notes, or a task the developer
  already performs by hand.
- Personalize a downloaded, forked, or community skill to the local tools, paths,
  aliases, and phrasing of the current session.
- Generalize a private skill so it is safe to publish to a public repo, marketplace,
  or team without leaking secrets or internal facts.
- Audit an existing skill for under- and over-triggering and tighten its
  `description` and frontmatter.
- Run a release review against a checklist before a skill goes public.

**Don't use for:** one-off tasks that are unlikely to recur (those are comments,
not skills), writing a skill for a workflow you've never actually run, or any task
where a single snippet suffices. If you wouldn't do it twice the same way, it isn't
a skill.

## Prerequisites

- Read access to the session/archive sources you intend to mine (session logs,
  transcripts, memory summaries, repo history).
- Write access to the target skills root directory. This skill uses a
  repository-relative `skills/` convention; adapt to `~/.agents/skills/`,
  `~/.claude/skills/`, or `.codex/skills/` as appropriate.
- No API credentials are needed to operate this meta-skill. Any credential a
  target skill needs stays inside that skill's own `Prerequisites`, never here.

## How to Run

You run this skill by naming the lifecycle operation you want, for example:

```
Mine my session history for repeated workflows that should become skills.
```
```
Audit this skill; tell me why it doesn't trigger when I say things naturally.
```
```
Generalize this private skill so I can publish it.
```

Because there is no single executable, the procedure below is the run: use the
terminal tool to `find` the archive trees, `read_file` sessions, and run the
validation gate on any skill you author or change.

## Quick Reference

| Operation | Action |
|---|---|
| Mine | `python3 scripts/scan_sessions.py <archive>` — count workflow-intent repeats |
| Draft | `write_file <repo>/<slug>/SKILL.md` with frontmatter + canonical body |
| Personalize | Rewrite examples/phrasing to the local user + tools |
| Generalize | Redact secrets, paths, and facts; make examples portable |
| Validate | `scripts/validate_skill.py <skills-dir>` → `"valid": true` |
| Release | Walk `references/release-checklist.md` |

## Procedure

Each step ends with a checkable completion criterion.

1. **Scope the mine.** Enumerate the session/archive sources (logs, transcripts,
   memory, repo history) that record repeated work.
   *Completion: a named list of source paths to scan.*

2. **Run the repeat detector.** Run `python3 scripts/scan_sessions.py <archive_root>`
   in the terminal to count how often each intent keyword recurs across distinct
   files. Pair the mechanical count with a close read: a keyword may appear often
   yet be one trivial action.
   *Completion: a shortlist of candidate workflows, each with the session/offset
   evidence where it repeats.*

3. **Rate each candidate.** Mark each as *personal* (local-only), *publishable*
   (safe to generalize), or *skip* (too trivial or already covered).
   *Completion: every candidate has a decision.*

4. **Draft the `SKILL.md`.** Create `<repo>/<slug>/SKILL.md` (slug = lowercase-kebab
   folder name). Write frontmatter (`name` matching the folder, `description` ≤60
   chars ending in a period, `version`, `license`, `author`, `platforms`, a
   `metadata.tags` block) and the canonical body sections.
   *Completion: frontmatter matches the folder, and the body has all canonical
   sections.*

5. **Personalize where needed.** If this is an existing or community skill, rewrite
   its examples and phrasing to the local user's tools, aliases, and paths — but
   keep secrets out and keep paths portable.
   *Completion: the skill reads as the user, not a boilerplate.*
6. **Generalize for release.** If publishing, sweep the skill for private paths,
   hostnames, keys, names, quotes, and internal facts; neutralize or redact each.
   *Completion: a secret/pattern sweep of the file returns nothing outside
   `references/sources.md`.*
7. **Document references.** Add `references/sources.md` (one line per source +
   URL) and push any domain-heavy content into dedicated reference docs so the
   `SKILL.md` stays fair.
   *Completion: every reference is sourced and referenced from the body.*
8. **Package.** Add `LICENSE`, `CHANGELOG.md`, and `evals/evals.json` next to it.
   *Completion: SKILL.md, LICENSE, CHANGELOG.md, evals/, references/ exist.*
9. **Run the gate.** Execute `scripts/validate_skill.py <skills-dir>`; fix any
   frontmatter or structure issue and re-run until `"valid": true`.
   *Completion: the validator reports valid and an empty `issues` list.*
10. **Release review.** Walk the release checklist when the skill ships public.
    *Completion: every checklist line is satisfied before publication.*

## Pitfalls

- **Hardcoded absolute paths.** `SKILL.md` files that contain `/Users/<you>/...`
  break on other machines. Keep paths repo-relative or `~`-based.
- **Secret leaks.** A private key, hostname, or account name is ink that can't be
  unprinted. Sweep before release and never tell it later.
- **Runaway body length.** A >500-line body is a warning sign. Keep the frontmatter
  and quick-reference flat; move depth to references.
- **Trigger drift.** A skill whose `description` says nothing about when to use it
  is a skill that never learns. Keep the description crisp and pointing.
- **Silently rewording others' skills.** When personalizing a skill you did not
  write, keep the blame of changes visible/reviewable.

## Verification

- Frontmatter `name` equals the folder slug; `description` is ≤60 characters and
  ends in a period.
- Body sections appear in the canonical order: When to Use, Prerequisites, How to
  Run, Quick Reference, Procedure, Pitfalls, Verification.
- `LICENSE`, `CHANGELOG.md`, `evals/evals.json`, and `references/` sit beside
  `SKILL.md`.
- A scan for `sk-`+24-char tokens, `lin_api_`, and absolute path patterns across
  the released file returns nothing leaked.
- `scripts/validate_skill.py <skills-dir>` prints `"valid": true` with no issues.