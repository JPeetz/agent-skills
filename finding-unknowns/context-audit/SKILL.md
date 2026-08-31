---
name: finding-unknowns-context-audit
description: >-
  Use when an agent ignores its instructions or a CLAUDE.md has
  grown bloated — audit for contradictions, duplications, and dead rules.
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
    - context
    - audit
    - pruning
    - instructions
  related_skills:
    - finding-unknowns-progressive-disclosure
    - finding-unknowns-agent-interface-design
    - skill-lifecycle-foundry
  complexity_level: advanced
---

# Context Audit

A prompt is written for one task; context is reused across every task, so it can never be as specific. That gap is where instructions rot: rules written for a worst case that no longer happens, guidance duplicated across three layers, two layers quietly telling the model opposite things. The model can resolve all of it — by spending thinking budget on it before it starts your actual work. This skill finds what to delete.

Derived from: *The new rules of context engineering for Claude 5 generation models* by Thariq Shihipar.

## Steps

1. Inventory every layer that reaches the model: root and nested `CLAUDE.md`/`AGENTS.md`, each skill's description and body, hooks, tool and MCP server descriptions, and any harness prompt the user controls. Report each layer's size. The layer the user forgot they wrote is usually the loudest one.
2. Read them together, the way the model receives them — not one file at a time. Contradictions only exist between layers.
3. Classify every instruction as one of five things:
   - **Conflict** — two layers pulling opposite ways ("document as appropriate" against "never add comments"). Quote both sides verbatim.
   - **Duplicate** — the same instruction in two places. Keep the copy nearest the point of use.
   - **Obvious** — restates what the file tree, the language, or the surrounding code already shows.
   - **Judgement-now** — a blanket rule written to prevent a worst case, wrong for some real subset of requests.
   - **Gotcha** — non-obvious, specific to this repo, load-bearing. This is what should survive.
4. Propose the cut as a diff: conflicts resolved first, then duplicates, then the rest. For anything worth keeping but only sometimes needed, propose relocating into a skill or a linked file.
5. Close with before/after line counts and the single deletion you are least confident about, named explicitly so a human decides that one.

## Pitfalls

- **Assuming intent**: a rule that reads as over-constraint is sometimes scar tissue from a real incident. Anything naming a specific failure gets asked about, not cut.
- **Deleting invariants**: an audit that deletes a real invariant costs far more than the tokens it saved. When a line's purpose is unclear, that ambiguity is the finding.
- **Propose, don't apply**: the user approves every deletion. Never make cuts without confirmation.

## Verification

- [ ] Did you inventory every instruction layer and report each layer's size?
- [ ] Did you read layers together (not one file at a time)?
- [ ] Are contradictions quoted verbatim from both sides?
- [ ] Is the report closed with a before/after line count and the riskiest deletion?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).