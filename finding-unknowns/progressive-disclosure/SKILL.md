---
name: finding-unknowns-progressive-disclosure
description: >-
  Use when a skill or spec has grown too long — split it into an
  entry file plus files loaded only when needed.
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
    - progressive-disclosure
    - context-management
    - skill-architecture
  related_skills:
    - finding-unknowns-context-audit
    - finding-unknowns-agent-interface-design
    - skill-lifecycle-foundry
  complexity_level: advanced
---

# Progressive Disclosure

A long instruction file is paid for on every single turn, including the turns that need none of it. The fix is not deletion — the material is real — but placement: keep what every run needs in the entry file, and move what only some runs need behind a pointer that fires when it's relevant. This skill restructures one artifact. To find out which artifacts need it, audit first.

Derived from: *The new rules of context engineering for Claude 5 generation models* by Thariq Shihipar.

## Steps

1. Read the whole artifact and identify its **branches** — the genuinely different ways a run can go through it. A verification section reached only when the user asks to verify is a branch; a rule that applies every time is not.
2. Sort every section into two piles: needed on every branch, and needed on one. The split is the entire decision, and it is usually less even than it looks — most files are a short universal core wrapped in branch-specific detail.
3. Keep the universal core in the entry file, ordered so the file still reads coherently on its own. An entry file that no longer makes sense without its children has been cut in the wrong place.
4. Move each branch into a sibling file named for what it holds, not for where it came from — `verification.md`, `glossary.md` — so the name alone tells the reader when to open it.
5. Write the pointer with care, because the pointer's wording is what decides whether the material is ever reached. Name the condition and the file together: "when the change touches migrations, read `migrations.md` before planning." A bare link at the bottom of a file is not a pointer.
6. Walk each branch end to end and confirm it still has everything it needs. Then report what moved, what stayed, and the new size of the entry file.

## Pitfalls

- **Splitting without deleting**: if a section is genuinely dead, remove it outright rather than hiding it in a file nobody opens.
- **False splits**: never split material that every branch needs. Two files always read together are one file with extra steps.
- **Silent pointers**: a pointer that never fires has made the material invisible, which is worse than leaving it inline. When the triggering condition can't be stated crisply, that section stays put.
- **Platform compatibility**: verify the target harness ships sibling files alongside `SKILL.md` before relying on them. Installers differ.

## Verification

- [ ] Did you identify the artifact's branches (different ways a run can go through it)?
- [ ] Is the universal core kept in the entry file, reading coherently on its own?
- [ ] Are branch files named for what they hold (not where they came from)?
- [ ] Are pointers worded to fire when relevant (condition + filename)?
- [ ] Did you report what moved, what stayed, and the new entry file size?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).