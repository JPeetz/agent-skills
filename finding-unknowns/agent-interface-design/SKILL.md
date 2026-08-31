---
name: finding-unknowns-agent-interface-design
description: >-
  Use when building an MCP server, tool definition, or script
  that an agent will call — make the interface teach its own use.
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
    - interface-design
    - mcp
    - tool-design
    - agent-tools
  related_skills:
    - finding-unknowns-context-audit
    - finding-unknowns-progressive-disclosure
    - composio
  complexity_level: advanced
---

# Agent Interface Design

Examples teach one path and quietly fence off the others: shown three ways to call a tool, a model tends to produce those three. A well-designed interface teaches the whole space at once. The parameters say what is possible, the description says what is expected, and there is very little left to write.

Derived from: *The new rules of context engineering for Claude 5 generation models* by Thariq Shihipar.

## Steps

1. Find out how the tool is actually being misused before redesigning it. Read transcripts, logs, or the user's complaint. Misuse is an interface symptom first and a documentation symptom second, and the fix is usually a rename or a type, not a paragraph.
2. Push meaning into the parameters:
   - Enumerate instead of accepting free text. A status of `pending | in_progress | completed` teaches the whole state machine without a sentence of prose.
   - Name for intent rather than implementation, so the right call is the one that reads correctly.
   - Make invalid states unrepresentable wherever the type system allows it.
3. Put behavioral instruction in the tool's own description, at the point of use, and only there. The same guidance restated in a global preamble is how a codebase grows contradictions.
4. Treat the urge to add a usage example as a diagnostic: it usually means a parameter is underspecified. Fix the interface first. Keep an example only for a format that genuinely cannot be guessed.
5. Decide what is resident and what is discoverable. Tools needed on most turns belong in context; tools needed rarely should be findable on demand.
6. Finish by naming the mistake the design still permits, and say whether it is cheap enough to live with or needs an explicit guardrail.

## Pitfalls

- **Descriptions vs. names**: a description that has to explain what a parameter means is a parameter that needs a better name.
- **Elegance vs. safety**: irreversible and high-stakes operations are the exception — there, explicit constraint and confirmation beat elegance.
- **Blind redesign**: never redesign a signature without first finding every existing caller (search_files for all usages).

## Verification

- [ ] Did you investigate current misuse patterns before redesigning?
- [ ] Are parameters enumerated instead of free-text where possible?
- [ ] Does each parameter name express intent, not implementation?
- [ ] Did you name the mistake the design still permits?

## Install

See the [finding-unknowns README](https://github.com/JPeetz/agent-skills/tree/main/finding-unknowns) for install instructions. Original source: [Neeeophytee/finding-unknowns-skills](https://github.com/Neeeophytee/finding-unknowns-skills).