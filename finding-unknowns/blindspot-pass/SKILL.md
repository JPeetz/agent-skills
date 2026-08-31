---
name: finding-unknowns-blindspot-pass
description: >-
  Use when entering an unfamiliar codebase area or domain and
  you need to surface unknown unknowns before starting work.
version: 1.0.0
author: Skill Foundry
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  tags:
    - finding-unknowns
    - blind-spot
    - discovery
    - planning
  related_skills:
    - finding-unknowns-interview-me
    - finding-unknowns-reference-hunt
    - technique-spike
  complexity_level: intermediate
---

# Blindspot Pass

The user is about to work in territory they don't know well. Your job is not to do the task yet. Your job is to show them what they don't know they don't know, so their next prompt is better.

Original technique: *A Field Guide to Fable: Finding Your Unknowns* by Thariq Shihipar.

## Steps

1. Ask (or infer from context) two things: what they're trying to do, and what their experience level is with this specific area. Their starting point changes everything.
2. Explore the relevant territory yourself: the module, its history, its conventions, prior art in the repo, and (if the domain is external) what practitioners consider table stakes. Use `terminal` and `search_files` to inspect the codebase.
3. Report back in four sections:
   - **Landmines** — the mistakes someone new here typically makes, and any repo-specific potholes (deprecated paths, misleading names, half-migrated patterns).
   - **Hidden context** — decisions already made that constrain the work (why the code is shaped this way, invariants that must hold).
   - **What good looks like** — 2-3 examples of the pattern done well, from this repo or elsewhere, so they can calibrate quality.
   - **Questions you should be asking** — the 3-5 questions an expert would ask before starting, with your best guess at each answer.
4. End with a rewritten version of their original request that incorporates what you found, so they can see the difference between their map and the territory.

## Pitfalls

- **Implementation creep**: the urge to start coding is strong. Remind yourself this skill ends at understanding.
- **Overwhelming the user**: report 3-5 landmines, not 30. Prioritize what would change the architecture.
- **False simplicity**: if the area is simpler than feared, say so clearly. "You have no significant blindspots" is a valid deliverable.

## Verification

- [ ] Did you explore the codebase (search_files, read_file, terminal) to find landmines?
- [ ] Does the report include all four sections (landmines, hidden context, what good looks like, questions)?
- [ ] Did you end with a rewritten version of the user's request?
- [ ] Did you avoid implementing anything?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions via `hermes skills` or `gh skill install`.

See the [original Hermes install guide](https://github.com/Neeeophytee/finding-unknowns-skills/blob/main/INSTALL-HERMES.md) for `skills.external_dirs` setup.