# Cross-Platform Session Search

## Default locations

Search these first, then add user-supplied roots with `--root`:

Registered platform keys: `codex`, `claude`, `senpi`, `oh-my-pi`, `gajae-code`, `opencode`, `openclaw`, `droid`, `amp`, `gemini`, `kimi`, `qwen`, `codebuff`, `roo-code`, `kilo-code`, `cline`, `kodu`, `cursor-cli`, `aider`, `kilo-cli`, `hermes`, `goose`, `crush`, `zed`, `kiro`, `aside`.

| Platform | Unix/macOS | Windows |
|---|---|---|
| Codex | `$CODEX_HOME`, `~/.codex` | `%CODEX_HOME%`, `%USERPROFILE%\.codex` |
| Claude | `~/.claude` | `%USERPROFILE%\.claude`, `%APPDATA%\Claude` |
| OMO / Senpi / pi | `~/.omo/agent`, `~/.senpi/agent`, `~/.pi/agent` | `%USERPROFILE%\.omo\agent`, `%USERPROFILE%\.senpi\agent`, `%USERPROFILE%\.pi\agent` |
| oh-my-pi (`omp`) | `~/.omp/agent`, `~/.omp/profiles/*/agent`, `$XDG_DATA_HOME/omp` | `%USERPROFILE%\.omp\agent` |
| gajae-code (`gjc`) | `~/.gjc/agent`, `~/.gjc/profiles/*/agent`, `$XDG_DATA_HOME/gjc` | `%USERPROFILE%\.gjc\agent` |
| OpenCode | `$OPENCODE_HOME`, `~/.opencode`, `~/.local/share/opencode` | `%OPENCODE_HOME%`, `%APPDATA%\opencode`, `%USERPROFILE%\.opencode` |
| OpenClaw | `~/.openclaw/agents/*/sessions`, `~/.openclaw/session-backups` | pass `--root` |
| Factory Droid | `~/.factory/sessions/*/*.jsonl` | pass `--root` |
| Amp | `~/.local/share/amp/threads/T-*.json` | pass `--root` |
| Gemini / Kimi / Qwen | `~/.gemini/tmp/*/chats`, `~/.kimi/sessions/*/*/wire.jsonl`, `~/.qwen/projects/*/chats` | pass `--root` |
| Codebuff | `~/.config/manicode*/projects/*/chats/*/chat-messages.json` | pass `--root` |
| Roo Code (`roo-code`) / Kilo Code (`kilo-code`) / Cline | VS Code `globalStorage/<extension>/tasks/*` | VS Code `globalStorage\<extension>\tasks\*` |
| Kodu | VS Code `globalStorage/kodu-ai.claude-dev-experimental/db/Azad.db` | VS Code `globalStorage\kodu-ai.claude-dev-experimental\db\Azad.db` |
| Cursor CLI | `~/.cursor/chats/*/*/store.db`, `~/.cursor/prompt_history.json` | `%USERPROFILE%\.cursor\chats` |
| Aider | bounded project roots containing `.aider.chat.history.md`; use `--root` for other repos | pass `--root` |
| Kilo CLI (`kilo-cli`) / Hermes / Goose / Crush / Zed | Known SQLite roots are probed cheaply; unsupported schemas return empty | pass `--root` |
| Kiro | `~/.kiro/sessions/cli/*.json` plus paired `*.jsonl` prompt events | pass `--root` |
| Aside (browser agent) | `~/.aside/u/*/sessions/<date>_<id>/messages.jsonl`, joined with the per-user `state.db` `sessions` table (title, parent_id, cwd, model, timestamps). `~/.aside/u/*/agents/*/sessions/` is a hardlink mirror of `sessions/` and is intentionally not scanned | pass `--root` |

## Excluded usage-only sources

Do not add these as default transcript platforms without a separate prompt-reconstruction source:

| Source | Why excluded |
|---|---|
| Copilot OTEL | Token/telemetry rows, not prompts |
| Mux | `session-usage.json` usage buckets only |
| Antigravity | tokscale cache/RPC data, not raw chat transcripts |
| Synthetic | Provider retagging over another platform, not an independent session store |
| Cursor IDE usage CSV | Usage accounting; use `cursor-cli` for local CLI chat stores |

## Workflow

1. Probe the table's exact store roots for the platforms likely to hold the
   session before globbing anything — never sweep the whole home directory.
2. List candidate transcripts with `rg --files --hidden` inside the confirmed
   roots, then narrow with `rg -l -F` for each query lane. When the work may
   have run inside a delegated agent, include child transcript locations —
   several stores exclude them from top-level listings.
3. If results are noisy, filter by working directory, model, and time range.
4. Follow the subagent linkage below for child sessions, then open the raw
   files for exact quotes, tool calls, and evidence.

## Subagent linkage cheat sheet

| Platform | Child identity | Parent linkage | Agent label |
|---|---|---|---|
| Claude | `projects/<proj>/<sid>/subagents/**/agent-<agentId>.jsonl` | directory `<sid>` | `agent-*.meta.json` `agentType` |
| Codex | thread row + own rollout JSONL | `thread_spawn_edges` / `source.subagent.thread_spawn.parent_thread_id` | `agent_nickname (agent_role)` |
| OpenCode | `session` table row / `storage/session/**.json` | `parent_id` column / `parentID` field | `agent` column |
| Aside | own `sessions/<date>_<id>/messages.jsonl` transcript | `parent_id` column in `state.db` `sessions` | child session's `title` column (task description) |

## Scan discipline

Search every plausible platform's root, not only the one the user named first —
the session may live in a different agent than remembered. Keep the scan
probe-first: check exact store roots before globbing or opening files, so newly
installed local agents become visible without home-wide searches.

OpenCode is optimized differently from raw JSONL stores: it calls `opencode db path`, reads the SQLite session table directly, falls back to `opencode session list --format json`, and only scans `messages/` / `parts/` when the DB/CLI is unavailable or explicit `--root` values force a file-store lookup.

## Evidence rule

Never answer "what happened in a session" from the normalized preview alone. Use the preview to locate candidates, then inspect the raw transcript or `get` output.
