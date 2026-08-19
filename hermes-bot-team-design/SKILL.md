---
name: hermes-bot-team-design
description: >
  Use this skill when an agent needs to design a team of specialist Hermes bots
  from a project specification. Covers role assignment, SOUL.md authoring, MCP
  wiring, and group chat setup.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [bot-mode, team, design, profiles, soul, mcp, orchestration]
    related_skills: [hermes-multi-profile-ops, openclaw-to-hermes-adoption, hermes-agent]
---

# Hermes Bot Team Design

Design a team of specialized Hermes bots from a project specification. Each bot gets a SOUL.md with identity, behavior rules, handoff protocols, shared Memory section, and group chat integration. MCP servers (MeMex Zero RAG, HermesVault) are wired by default.

## When to use
- A new project needs a team of specialist bots
- You are expanding an existing fleet
- You are migrating an OpenClaw workflow to Hermes Bot Mode

## The team design workflow

### 1. Read the project spec
Understand the full pipeline before deciding roles. Identify: pipeline phases, which need deep reasoning (expensive model) vs high-volume/mechanical (cheap model), outputs, and handoffs.

### 2. Decide team size and roles
Map each phase to a bot role:
- **Discovery / Research** — high-volume, cheap model (DeepSeek V4 Flash)
- **Improvement / Creation** — deep reasoning, expensive model (DeepSeek V4 Pro)
- **Validation / Publishing** — mechanical, cheap model (DeepSeek V4 Flash)
- **Strategy / Direction** — deep reasoning, expensive model (DeepSeek V4 Pro)
- **Content / Copy** — creative, expensive model (DeepSeek V4 Pro)
- **UX / Design** — creative, expensive model (DeepSeek V4 Pro)
- **Frontend / Backend** — implementation, cheap model (DeepSeek V4 Flash)
- **Commerce / Marketplace** — mechanical, cheap model (DeepSeek V4 Flash)

### 3. Create a group chat directory
```bash
mkdir -p ~/workspace/MeMex-Zero-RAG/wiki/agentforge/group-chat/<project-name>/
```
Write a README.md with: protocol (file-based messaging), team roster (bot name, role, phase, model), pipeline flow, and communication rules.

### 4. For each bot, create the profile
```
~/.hermes/profiles/<name>/
├── SOUL.md      # Identity, Memory, behavior, handoffs
├── config.yaml  # model, provider, inherit_mcp_toolsets: true
```

**SOUL.md sections**: Frontmatter (name, description, role, teammates) → Identity → Memory (shared across all profiles — MeMex + HermesVault) → Group Chat → Browser verification → Behavior → Handoffs → Agent Inbox Protocol.

**config.yaml**:
```yaml
model:
  default: <provider>/<model>
  provider: <provider>
platforms:
  telegram:
    enabled: false  # Team bots don't need Telegram
```

### 5. Wire MCP servers (mandatory)
Set `inherit_mcp_toolsets: true` to inherit MeMex Zero RAG (wiki_search, wiki_read, wiki_query, wiki_ingest, wiki_lint) and HermesVault (read_file, search_files, list_directory, read_file_header) from global config.

### 6. Write roster + drop initial message
Add the roster to the group chat README. Write a message from the director introducing the team, pipeline, and first task.

### 7. Verify
- `ls ~/.hermes/profiles/<name>/` — SOUL.md + config.yaml exist
- `hermes gateway list` — gateway loads the new profile
- Group chat has README.md + first message

## Pitfalls
- Do NOT create a bot without a SOUL.md
- Do NOT skip the Memory section (shared brain between all bots)
- Do NOT use expensive models for mechanical work — Scout (discovery) and Overseer (publishing) are cheap
- Do NOT wire Telegram to team bots — they communicate via the group chat
- Do NOT suggest UI buttons that don't exist — if the user says "there's no such button," find an alternative
- Verify catalog files after rebase — conflict resolution can silently drop sibling rows

## References
- `references/skill-foundry-example.md` — full team design example (11 bots, Skill Foundry pipeline)