---
name: skill-miner
description: Use when mining agent history for repeated skill-worthy workflows.
version: 1.0.0
license: MIT
author: hqhq1025 (original source), Skill Foundry (packaged edition)
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - skill-mining
      - workflow-discovery
      - skill-authoring
      - session-analysis
    related_skills:
      - skill-lifecycle-foundry
---

# Skill Miner

## Overview

Mine real agent usage for new skill opportunities. The goal is to find repeated workflows, extract the reusable technique, and turn strong candidates into draft skills with evidence.

## When To Use

- A user wants to scan past coding-agent sessions for repeated workflows.
- The user suspects they keep asking agents to do similar tasks manually.
- A team wants a backlog of candidate skills based on actual work rather than brainstorming.
- Existing memories, session logs, or project notes contain recurring procedures that have not been packaged.

Do not use to tune an existing skill; use `skill-personalizer`. Do not use to publish a private skill publicly; use `skill-generalizer`.

## Workflow

1. Locate real evidence: session JSONL, memory summaries, repo notes, repeated scripts, and recent project folders. Use Hermes tools like `search_files` to find session logs and `session_search` to query past conversation context for recurring patterns.
2. Run `scripts/scan_sessions.py` for a first-pass sanitized cluster report when local session files or exported transcripts are available.
3. Cluster repeated work by intent, trigger phrasing, tools used, files touched, and verification pattern.
4. Filter out one-off tasks, ordinary coding knowledge, and project-specific instructions better suited for `AGENTS.md`.
5. Score candidates by recurrence, friction, risk, portability, and future value.
6. For each strong candidate, draft a concise skill name, trigger description, workflow outline, bundled-resource needs, and validation prompts.
7. Recommend whether each candidate should stay personal, become a public skill (see `skill-lifecycle-foundry` for generalization), or be skipped.
8. If the user asks to proceed, create the selected skill folders and verify frontmatter/layout.

## Evidence Rules

- Quote or summarize enough source evidence to justify each candidate.
- Do not expose sensitive transcript content unless the user explicitly asks for raw evidence.
- Avoid turning every repeated task into a skill; prefer workflows where guidance changes future behavior.
- Treat broad intent clusters as navigation hints, not skill drafts.
- Check sampled positives and near misses before trusting a regex-based workflow candidate.
- If session access is incomplete, label findings as partial and list what was scanned.

## Prerequisites

- Access to agent session history or archives
- For automated scanning: a recent Hermes, Claude Code, or Codex session archive
- Familiarity with the skill-lifecycle-foundry skill for generalization and publication workflows

## Pitfalls

- Session logs can contain sensitive data. Always sanitize before sharing mining results.
- One repeated task does not make a skill — look for 3+ occurrences before drafting.
- Mining without domain context can produce overly generic skill candidates.
- The automated scanner (`scan_sessions.py`) is a first-pass tool. Always review its output manually before creating skills.

## Verification

1. Run `search_files` on session archives with recurring action patterns.
2. Verify that extracted candidates show 3+ repeat instances.
3. Cross-check candidate against the existing `skill-lifecycle-foundry` to confirm it's a genuine gap.
4. Draft a test workload and verify the agent follows the new skill correctly.

## References

See `skill-lifecycle-foundry` for the full skill lifecycle: personalize, generalize, and publish skills from this miner's output.