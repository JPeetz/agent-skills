---
name: skill-miner
description: >-
  Use when mining agent session history, archived transcripts,
  or memories to discover recurring workflow patterns.
version: 1.0.0
author: Skill Foundry
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  tags:
    - skill-mining
    - workflow-discovery
    - session-analysis
    - pattern-detection
  related_skills:
    - skill-lifecycle-foundry
    - finding-unknowns-context-audit
    - session-librarian
  complexity_level: advanced
---

# Skill Miner

Mine real agent usage for new skill opportunities. The goal is to find repeated workflows, extract the reusable technique, and turn strong candidates into draft skills with evidence.

This skill is the discovery side of the [skill-lifecycle-foundry](https://github.com/JPeetz/agent-skills/tree/main/skill-lifecycle-foundry) meta-skill. Use it to produce candidate evidence; then use skill-lifecycle-foundry to author, personalize, and release.

Source: [hqhq1025/skill-optimizer](https://github.com/hqhq1025/skill-optimizer). MIT license.

## When To Use

- Scan past agent sessions for repeated workflows.
- The user suspects they keep asking agents to do similar tasks manually.
- A team wants a backlog of candidate skills based on actual work rather than brainstorming.
- Existing memories, session logs, or project notes contain recurring procedures that have not been packaged.

**Do not use** to tune an existing skill — use `skill-personalizer`. **Do not use** to publish a private skill publicly — use `skill-generalizer`.

## Hermes Tool Integration

This skill integrates with Hermes Agent's native tools for session mining:

| Tool | Usage |
|---|---|
| `session_search(query=..., limit=N)` | Query past sessions for workflow patterns by intent/trigger phrasing |
| `search_files(pattern, path=...)` | Find session logs, memories, and transcripts in the filesystem |
| `terminal("find ...", "ls ...")` | Locate history files, repeat-count repeated scripts |
| `read_file(path)` | Inspect session transcript excerpts for evidence |
| `web_search` | Find public examples of similar workflows for comparison |

## Workflow

### 1. Locate Evidence

Find real evidence of repeated work:

- **Agent session history**: use `session_search` to query past sessions for repeated patterns (e.g., "session_search(query='deploy OR publish', limit=10)")
- **Memory/transcript files**: use `search_files` to locate session JSONL, memory summaries, or notes in standard paths (`~/.codex/sessions`, `~/.claude/sessions`, `~/.agents/memories`)
- **Repeated scripts**: use `terminal` with `find` and `wc` to locate scripts run more than once
- **Project notes**: read `AGENTS.md`, `CLAUDE.md`, docs, and runbooks for workflows already documented locally

### 2. Cluster by Intent

Group repeated work by:
- **Intent**: review, debug, publish, deploy, summarize, install, sync, research
- **Trigger phrasing**: the user's actual short phrases and shorthand
- **Tools used**: shell, browser, git, SSH, GitHub, APIs
- **Files touched**: patterns in paths and file types
- **Verification pattern**: what "done" looked like in successful sessions
- **Failure pattern**: where agents usually got stuck or drifted

### 3. Filter Candidates

Filter out:
- One-off tasks (done only once)
- Ordinary coding knowledge (well-handled by the base model)
- Project-specific instructions better suited for `AGENTS.md`
- Secrets or workflows that should not be automated

Strong candidates usually have:
- The user asked for the same kind of work at least 3 times
- The workflow requires non-obvious sequencing or local judgment
- Agents often miss a step, ask unnecessary questions, or stop before verification
- The task crosses tools, repos, remote hosts, browsers, or document formats
- The user corrected an agent in a way future agents should remember

### 4. Score Candidates

Use a 1-5 scoring rubric:

| Score | Meaning |
|---|---|
| 5 | Repeated, high-value, non-obvious, mishandled without a skill |
| 4 | Repeated and useful, clear triggers and validation steps |
| 3 | Plausible, needs more evidence or narrower scope |
| 2 | Mostly project-specific or better as documentation |
| 1 | Do not create; generic, risky, or one-off |

Recommend creating skills for scores 4-5. Put score-3 items in a backlog. Skip scores 1-2.

### 5. Draft Skills

For each strong candidate, draft:
- Proposed skill name
- Personal or public direction
- Evidence count and representative sanitized examples
- Trigger description draft (≤60 chars, "Use when...")
- Core workflow bullets
- Bundled resources needed, if any
- Validation prompts (direct trigger, natural shorthand, and neighbor task)
- Risks or privacy notes

### 6. Handoff to Lifecycle

For each candidate the user asks to proceed:
1. Author the skill folder and SKILL.md
2. Reference [skill-lifecycle-foundry](https://github.com/JPeetz/agent-skills/tree/main/skill-lifecycle-foundry) for personalization and release steps
3. Verify frontmatter and layout against existing repo standards

## Pitfalls

- **Noisy clusters**: command-only turns, automations, passed logs, and multi-topic sessions create false positives. Always manually inspect 5 positive + 3 near-miss examples before accepting a candidate.
- **Broad triggers**: patterns catching generic words like `build`, `host`, `design`, or `service` need tightening before drafting.
- **Incomplete access**: if session access is incomplete, label findings as partial and list what was scanned.
- **Over-mining**: not every repeated task needs a skill. Prefer workflows where guidance changes future behavior.
- **Privacy**: quote or summarize evidence — do not expose sensitive transcript content unless the user explicitly asks for raw evidence.
- **Script-first**: if the candidate needs deterministic counting, parsing, or redaction, create a script instead of relying on prose alone.

## Verification

- [ ] Did you query at least 3 different evidence sources?
- [ ] Are candidates supported by at least 3 occurrences of the same intent?
- [ ] Did you manually inspect 5 positive examples and 3 near-misses per candidate?
- [ ] Is each candidate scored 1-5 with a clear disposition (create/backlog/skip)?
- [ ] Does each draft include a trigger description, core workflow, and evidence summary?
- [ ] Are privacy notes included for any candidate touching sensitive data?

## References

- [discovery-rubric.md](references/discovery-rubric.md) — full evidence source list, candidate signals, scoring criteria, and creation rules.
- [skill-lifecycle-foundry](https://github.com/JPeetz/agent-skills/tree/main/skill-lifecycle-foundry) — the meta-skill for authoring, personalizing, and releasing mined skills.
- [hqhq1025/skill-optimizer](https://github.com/hqhq1025/skill-optimizer) — original source repository (MIT license).

## Install

Install via `gh skill install JPeetz/agent-skills skill-miner` or `hermes skills install JPeetz/agent-skills/skill-miner`.