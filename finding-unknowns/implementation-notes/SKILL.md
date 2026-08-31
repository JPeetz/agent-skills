---
name: finding-unknowns-implementation-notes
description: >-
  Use during a build to log every deviation from the plan and
  every discovered edge case for the next session.
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
    - implementation
    - session-logging
    - decision-tracking
  related_skills:
    - finding-unknowns-implementation-plan
    - finding-unknowns-change-quiz
    - note-taking
  complexity_level: intermediate
---

# Implementation Notes

No amount of planning removes every unknown; some only appear once the code is open. When the territory disagrees with the plan, don't stop and don't silently improvise — take the conservative option, write it down, and keep going. The notes file is how the next attempt learns from this one.

Original technique: *A Field Guide to Fable: Finding Your Unknowns* by Thariq Shihipar.

## Steps

1. At the start of the build, create `implementation-notes.md` with three headings: **Deviations**, **Discovered edge cases**, **Questions for review**.
2. Whenever reality forces a choice the plan didn't cover:
   - pick the conservative option (the one that's easiest to reverse),
   - log it under Deviations: what the plan said, what was done instead, why, and what it would take to revisit,
   - continue working. Do not block on the user for reversible decisions.
3. Log edge cases as they're found, even ones handled cleanly — they are exactly the unknowns the next plan should account for.
4. Anything irreversible or scope-changing goes under Questions for review AND stops the work at a safe checkpoint. Deviating conservatively is fine; deviating expensively needs a human.
5. At the end, append a five-line summary: deviations count, the one most likely to be revisited, edge cases found, and what the next session should read first. Reference the file in the handoff or PR.

## Pitfalls

- **Drift from reality**: an unlogged deviation is worse than no notes at all, because the file claims completeness. Log everything.
- **Verbosity**: the notes file is temporary working memory, not documentation. Keep entries to 2-3 lines each.
- **Wrong conservatism**: "conservative" means reversible, not necessarily simple. A reversible complex fix is better than an irreversible simple one.

## Verification

- [ ] Was `implementation-notes.md` created at the start of the build with the three headings?
- [ ] Are all deviations logged (plan → what was done → why → revisit cost)?
- [ ] Did you stop work for irreversible/scope-changing deviations?
- [ ] Does the file end with a five-line summary?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).