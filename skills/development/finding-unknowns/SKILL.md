---
name: finding-unknowns
description: Use when entering unfamiliar code or domain territory.
version: 1.0.0
license: MIT
author: Neeeophytee (original author, based on Thariq Shihipar essays), Skill Foundry (packaged edition)
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - meta-cognitive
      - blindspot
      - unknown-unknowns
      - context-audit
      - agent-skills
    related_skills:
      - skill-miner
      - code-review
---

# Finding Unknowns — Meta-Cognitive Skill Suite

A collection of 11 meta-cognitive skills that make coding agents surface unknown unknowns before they get expensive. These skills teach agents to discover what they don't know, audit their own context, design better interfaces, and structure implementation for maximum reviewability.

Based on Thariq Shihipar's "finding your unknowns" techniques. Originally published by Neeeophytee at https://github.com/Neeeophytee/finding-unknowns-skills.

## Skills in This Suite

| Skill | Description |
|-------|-------------|
| **blindspot-pass** | Surface unknown unknowns before work starts — landmines, hidden context, quality calibration |
| **interview-me** | One-question-at-a-time targeted interview to resolve remaining ambiguity |
| **reference-hunt** | Extract semantics from existing code as specification, then reimplement |
| **implementation-plan** | Write plans ordered by likelihood of tweaking, not build order |
| **implementation-notes** | Log deviations from plan and discovered edge cases during a build |
| **pitch-packager** | Package work into a single review-ready document that gets fast approvals |
| **change-quiz** | Produce a diff report + 5-8 question quiz the user must pass before merge |
| **brainstorm-prototypes** | Generate wildly different throwaway variations for user reaction |
| **context-audit** | Audit CLAUDE.md, AGENTS.md, skills for contradictions, bloat, and overlap |
| **agent-interface-design** | Design MCP servers, tool definitions, and CLIs that teach their own use |
| **progressive-disclosure** | Split oversized skills/specs into entry + on-demand files |

## When to Use

- You're about to work in an unfamiliar codebase area or domain
- You're planning a complex multi-step implementation
- You've just finished a long session and need to verify what changed
- User asks to "audit context" or "find my blindspots"
- You're designing an MCP server or agent-facing tool

## Hermes Installation

This suite can be installed as external skills. Add to your `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /path/to/finding-unknowns/skills
```

Then run `hermes skills list` to verify all 11 skills are enabled.

See `INSTALL-HERMES.md` in the original repository at https://github.com/Neeeophytee/finding-unknowns-skills for alternative installation methods.

## Skill Index

Each sub-skill is in `skills/<name>/SKILL.md`. Refer to the individual skill file for full procedure.

1. [blindspot-pass](skills/blindspot-pass/SKILL.md) — Systematic unknown-unknowns discovery
2. [interview-me](skills/interview-me/SKILL.md) — One-question-at-a-time ambiguity resolution
3. [reference-hunt](skills/reference-hunt/SKILL.md) — Code-as-specification reimplementation
4. [implementation-plan](skills/implementation-plan/SKILL.md) — Decision-first plan authoring
5. [implementation-notes](skills/implementation-notes/SKILL.md) — Running deviation log
6. [pitch-packager](skills/pitch-packager/SKILL.md) — Review-ready work packaging
7. [change-quiz](skills/change-quiz/SKILL.md) — Pre-merge comprehension gate
8. [brainstorm-prototypes](skills/brainstorm-prototypes/SKILL.md) — Throwaway variation generation
9. [context-audit](skills/context-audit/SKILL.md) — Agent context rightsizing
10. [agent-interface-design](skills/agent-interface-design/SKILL.md) — Self-teaching tool interfaces
11. [progressive-disclosure](skills/progressive-disclosure/SKILL.md) — On-demand content structuring

## Pitfalls

- `progressive-disclosure` uses `disable-model-invocation: true` in original source (invoked only by user, not auto-activated). In Hermes, it behaves as model-invoked. Keep this in mind for context cost accounting.
- The suite is most effective when used as a cycle: Context Audit → Brainstorm → Interview → Plan → Implement (with Notes) → Quiz → Pitch. Not all steps are needed for every task.
- Individual skills work standalone — you can pick just the ones you need.

## Verification

1. Run `hermes skills list` and verify all 11 skill names appear as "enabled".
2. Give the agent a task in an unfamiliar domain and check if `blindspot-pass` triggers.
3. After a long session, ask "what did we change?" and verify `change-quiz` produces a comprehensive report.
4. Request a context audit on your active configuration and verify contradictions are surfaced.