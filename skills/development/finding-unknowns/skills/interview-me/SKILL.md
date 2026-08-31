---
name: interview-me
description: Use when planning is done but ambiguity still remains.
version: 1.0.0
license: MIT
author: Neeeophytee (original), Skill Foundry (packaged)
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - interview
      - requirements-gathering
      - ambiguity
    related_skills:
      - finding-unknowns
      - implementation-plan
---

# Interview me

Brainstorming is over and there are still gaps between the user's map and the territory. Close them by asking, one question at a time, starting with the questions whose answers would change the most.

## Steps

1. Read everything already established: the request, any spec, any prototypes, relevant code. Do not ask about things that are already answered.
2. Build a private list of open ambiguities and sort by blast radius:
   - **First: architecture-changers** — answers that would alter the data model, the interfaces, or the overall approach.
   - **Then: behavior definers** — edge cases, failure modes, defaults, permissions.
   - **Last: polish** — naming, copy, cosmetics. Often not worth asking; propose and move on.
3. Ask exactly one question per turn. For each: give the context that makes it matter, offer 2-3 concrete options with your recommendation, and accept "you decide" as an answer you then own.
4. Every few questions, checkpoint: restate what has been decided so far in one tight list, so drift dies early.
5. Stop when the remaining unknowns are cheaper to discover during implementation than to ask about now, and say that out loud. End with the final decision list, ready to paste into a plan.

## Guardrails

- One question at a time means one. No question bundles.
- Never ask a question whose answer is discoverable from the codebase; go look instead.
- If an answer contradicts an earlier decision, flag the conflict immediately rather than silently taking the newest answer.