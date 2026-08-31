---
name: finding-unknowns-interview-me
description: >-
  Use when brainstorming is done but ambiguity remains and you
  need to resolve assumptions one question at a time.
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
    - interview
    - ambiguity
    - requirements
  related_skills:
    - finding-unknowns-blindspot-pass
    - finding-unknowns-implementation-plan
    - technique-spike
  complexity_level: intermediate
---

# Interview Me

Brainstorming is over and there are still gaps between the user's map and the territory. Close them by asking, one question at a time, starting with the questions whose answers would change the most.

Original technique: *A Field Guide to Fable: Finding Your Unknowns* by Thariq Shihipar.

## Steps

1. Read everything already established: the request, any spec, any prototypes, relevant code. Do not ask about things that are already answered.
2. Build a private list of open ambiguities and sort by blast radius:
   - **First: architecture-changers** — answers that would alter the data model, the interfaces, or the overall approach.
   - **Then: behavior definers** — edge cases, failure modes, defaults, permissions.
   - **Last: polish** — naming, copy, cosmetics. Often not worth asking; propose and move on.
3. Ask exactly one question per turn. For each: give the context that makes it matter, offer 2-3 concrete options with your recommendation, and accept "you decide" as an answer you then own.
4. Every few questions, checkpoint: restate what has been decided so far in one tight list, so drift dies early.
5. Stop when the remaining unknowns are cheaper to discover during implementation than to ask about now, and say that out loud. End with the final decision list, ready to paste into a plan.

## Pitfalls

- **Question bundling**: one question at a time means one. Resist the urge to ask 2-3 related items together.
- **Re-asking answered questions**: use `read_file` or `search_files` to check if the codebase already answers a question. Never ask what the code can tell you.
- **Silently accepting contradictions**: if a new answer contradicts an earlier decision, flag the conflict immediately rather than taking the newest answer silently.

## Verification

- [ ] Did you read all existing context (spec, code, prototypes) before asking?
- [ ] Are architecture-changing questions asked first?
- [ ] Is each question offered with 2-3 options and a recommendation?
- [ ] Does the final output include a consolidated decision list?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).