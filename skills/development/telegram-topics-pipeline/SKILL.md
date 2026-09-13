---
name: telegram-topics-pipeline
description: >
  Use this skill when setting up Telegram forum topics to run multiple
  independent bot sessions or automated pipelines in one group with
  isolated context, per-topic skills, cron delivery, and no cross-contamination
  between workflows.
version: 1.0.0
author: Joerg Peetz / Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [telegram, topics, forum, multi-session, pipeline, orchestration]
    related_skills: [hermes-agent, social-media, cronjob, hermes-multi-profile-ops, recurring-content-anti-repetition]
---

# Telegram Topics Pipeline

Wire Telegram's forum topics into your agent infrastructure so each topic is its own isolated agent session with dedicated context, skills, and cron pipeline. No context bleed. No accidental cross-posting. One group, N independent workflows.

This is the single highest-impact operational change you can make to how your agent runs. A flat DM or group chat forces every topic into the same context window. Topics fix that.

---

## How It Works

Telegram forum topics (supergroups with Topics mode) each carry a unique `message_thread_id`. Hermes (and OpenClaw) use the pair `(chat_id, thread_id)` as a session key:

```
agent:main:telegram:dm:{chat_id}:{thread_id}     # DM topics
agent:main:telegram:group:{chat_id}:{thread_id}   # Group forum topics
```

Messages in Topic A never appear in Topic B's session history. They are independent conversations with their own scrollback, memory, and active context.

---

## Step 0: Enable Topics

**You must enable Topics on the Telegram side.** The bot cannot do this.

1. Create a Telegram group (or use an existing one)
2. Add your bot to the group
3. Go to **Group Settings → Edit → Enable Topics (Forum mode)**
4. Create topics with descriptive names and emoji icons

**If the bot is in privacy mode**, either:
- Turn it off via BotFather (`/setprivacy` → `Disable`), **or**
- Make the bot a group admin (topics count as messages; privacy-mode bots only see messages that `@mention` them or slash commands)

---

## Step 1: DM Topics (Hermes)

Add `dm_topics` under `platforms.telegram.extra` in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
        - chat_id: 123456789          # Your Telegram user ID (integer)
          topics:
            - name: General
              icon_color: 7322096
            - name: Website
              icon_color: 9367192
            - name: Research
              icon_color: 16766590
              skill: arxiv             # Auto-loads arxiv skill in this topic
            - name: Engineering
              skill: software-development
            - name: Social Pipeline
              icon_color: 16752821
              skill: social-media       # Every session in this topic loads social-media
```

Field reference:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Topic display name |
| `icon_color` | No | Telegram icon color code (integer) |
| `icon_custom_emoji_id` | No | Custom emoji ID |
| `skill` | No | Skill to auto-load on every new session in this topic |
| `thread_id` | No | Auto-populated by Hermes after creation — don't set manually |

On first gateway restart, Hermes calls `createForumTopic` for each entry without a `thread_id` and saves the ID back to config.yaml automatically.

Set `ignore_root_dm: true` to turn the root DM into a silent lobby — normal messages are ignored while slash commands (/start, /help, /status) still work:

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: General
            - name: Research
              skill: arxiv
```

---

## Step 2: Group Forum Topic Skill Binding (Hermes)

For supergroups where topics are created manually in the Telegram UI, use `group_topics`:

```yaml
platforms:
  telegram:
    extra:
      group_topics:
        - chat_id: -1001234567890      # Group ID (prefixed with -100)
          topics:
            - thread_id: 5             # From URL: t.me/c/1234567890/5
              skill: marketing
            - thread_id: 8
              skill: software-development
            - thread_id: 12
              skill: research
```

To find a topic's `thread_id`: open the topic in Telegram Web or Desktop and look at the URL — `https://t.me/c/1234567890/5` — the last number (5) is the `thread_id`. The group's `chat_id` is the group ID prefixed with `-100`.

---

## Step 3: Cron Delivery to Topics

Route scheduled task output to a specific topic instead of the default chat:

```yaml
cron:
  social-pipeline:
    schedule: "30 8 * * *"
    goal: "Generate and post today's BetterLife social content"
    target: "telegram:-1001234567890:31"   # telegram:<chat_id>:<thread_id>
```

The `target` format is: `telegram:<chat_id>:<thread_id>`

On Hermes, you can also use `target: origin` to send back to wherever the cron was registered from.

---

## Step 4: User-Driven Multi-Session Mode (`/topic`)

For end-users who want to create topics on the fly without touching config:

1. The user sends `/topic` in the bot DM
2. Hermes verifies the bot has `can_create_topics` and `threads_enabled` flags (you must toggle these in BotFather first)
3. User creates topics from the Telegram UI (`+` button in the topic bar)
4. Each topic gets its own isolated session
5. The user can rename topics — Hermes auto-renames to match the session title

Commands:

| Command | Context | Effect |
|---------|---------|--------|
| `/topic` | Root DM | Enable multi-session mode |
| `/topic off` | Root DM | Disable and clear all topic bindings |
| `/topic help` | Any | Show usage |
| `/topic <session-id>` | Inside a topic | Restore a previous session |
| `/new` | Inside a topic | Reset that topic's session |

---

## Pipeline Architecture Patterns

### Pattern A: Separate Pipeline Per Topic

One group, three topics, three independent automated pipelines:

```
Group: "Agent HQ"
├── 📰 Social (topic 31)
│   └── Cron: 08:30 daily → generate + review + post social content
│       Skill: social-media, recurring-content-anti-repetition
├── 🔬 Research (topic 32)
│   └── Cron: 06:00 daily → web research digest → deliver to topic
│       Skill: arxiv, web-search
└── 🛠️ Engineering (topic 33)
    └── Cron: hourly → check PRs, run tests, report status
        Skill: software-development, github
```

Each pipeline runs autonomously. Results land in their own topic. You browse them when convenient.

### Pattern B: Topic as Session Boundaries

```
DM
├── General (casual chat, quick questions)
├── Project Alpha (deep context, long research threads)
├── Client Reports (weekly deliverable production)
└── Agent Maintenance (skill updates, config changes)
```

Switch between topics freely. Each one picks up exactly where you left off.

### Pattern C: Multi-Profile Routing

Each Hermes profile can connect its own bot. Map one bot per function:

| Bot | Topics | Purpose |
|-----|--------|---------|
| `@fluffy_bot` | General, Social, Engineering | Daily ops |
| `@research_bot` | Research, Deep-Dives | Heavy research, no distractions |
| `@monitor_bot` | System Health, Alerts | Silent monitoring, cron deliveries only |

Configure under `telegram.accounts` or run separate gateway instances per profile.

---

## Common Pitfalls

**Bots don't see topic messages.** — Privacy mode blocks them. Fix: disable privacy in BotFather OR make the bot a group admin.

**Telegram "409 Conflict" errors.** — Stale polling session from another process. Find and kill the duplicate: `grep -rl <bot_token> ~/.hermes ~/.openclaw ~/.config`.

**Topic not appearing after config change.** — Hermes only calls `createForumTopic` for entries without a saved `thread_id`. Delete the thread_id from config.yaml for that topic to force recreation.

**Session bleeding between topics.** — Verify each topic has a unique `thread_id`. Duplicate thread_ids share the same session key.

**Cron output goes to the wrong topic.** — Double-check the `target` format: `telegram:<chat_id>:<thread_id>` with no extra spaces.

---

## Verification

After setup, verify isolation:

1. Send a message in Topic A → reply
2. Switch to Topic B → send unrelated message → reply (should show no knowledge of Topic A)
3. Send `/new` in Topic A → verify Topic B's session is unaffected
4. Check cron deliveries arrive in the correct topic
5. For skill binding: send a message in a topic with `skill: arxiv` → the agent should have `arxiv` pre-loaded

---

## References

- [Hermes Agent Telegram Docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)
- [Bot API — Forum Topics](https://core.telegram.org/bots/api#forum-topic-availability)
- [OpenClaw Telegram Topics Guide](https://wayintoai.com/ref/telegram-topics-openclaw)
- [Multi-Topic AI Workspace with OpenClaw](https://maniak.io/articles/2026-03-29-openclaw-telegram-topics-ai-workspace/)