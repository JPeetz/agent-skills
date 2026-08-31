---
name: finding-unknowns-reference-hunt
description: >-
  Use when the user can't describe what they want in words and
  points to existing code as the spec ("like this").
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
    - reference
    - reverse-engineering
    - specification
  related_skills:
    - finding-unknowns-implementation-plan
    - finding-unknowns-brainstorm-prototypes
    - har-api-reverse-engineering
  complexity_level: advanced
---

# Reference Hunt

Some requirements are too intricate or too tacit to write down, but working code somewhere already embodies them. The best reference is not a screenshot or a description — it's source. Read it like a spec, then reimplement the semantics, not the syntax.

Original technique: *A Field Guide to Fable: Finding Your Unknowns* by Thariq Shihipar.

## Steps

1. Get the reference: a repo path, a vendored folder, a library name, or a site whose underlying code can be read. Ask what specifically to extract from it — behavior, structure, visual system, API shape — so you don't imitate the wrong dimension.
2. Read the reference (use `read_file`, `search_files`, `terminal` with `git`/`curl`) and produce a **semantics summary** before writing any code:
   - the behaviors and guarantees it implements (timing, ordering, error handling, edge cases),
   - the decisions that look deliberate versus incidental,
   - anything that won't translate to the target language or stack, with a proposed equivalent.
3. Have the user confirm the semantics summary. This is the moment misreadings get caught cheaply.
4. Reimplement in the target stack: same semantics, native idioms. Do not transliterate line by line, and do not copy code verbatim from references whose license doesn't allow it — note the license if it's unclear.
5. Close the loop: list each behavior from the summary and where the new implementation honors it, plus any place you consciously diverged and why.

## Pitfalls

- **Transliteration**: copying syntax rather than semantics. The reference defines *what*; the target codebase's conventions define *how*.
- **License violation**: extracting semantics is fine; copying incompatible code is not. Check the LICENSE file before any verbatim reproduction.
- **Blind reproduction**: if the reference itself is buggy or inconsistent, surface that instead of faithfully reproducing the bug.
- **Scope creep**: the reference may contain patterns your task doesn't need. Extract only the relevant semantics.

## Verification

- [ ] Did you produce a semantics summary before writing any code?
- [ ] Was the summary confirmed by the user before implementation?
- [ ] Does the final implementation honor each behavior from the summary?
- [ ] Did you check the reference's license before any verbatim copying?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).