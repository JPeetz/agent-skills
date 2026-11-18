# Codex Sessions

Codex has two useful surfaces:

- `$CODEX_HOME/state_*.sqlite` stores thread metadata.
- `$CODEX_HOME/sessions/**/rollout-*.jsonl` and archived rollout files store event transcripts.

Prefer the host's own Codex history tools when exposed (for example, the Codex
app's `list_threads` / `read_thread`). Otherwise list candidate rollout files
with `rg --files --hidden "$CODEX_HOME/sessions"` and search them with `rg -l -F`.

Useful search dimensions: time range, working directory, model, and whether
spawned (subagent) threads are in scope.

## Spawned (subagent) threads

Codex subagent threads are ordinary rows in `threads` with their own rollout files. Two linkage sources:

- `thread_spawn_edges(parent_thread_id, child_thread_id, status)` — authoritative parent→child table.
- `threads.source` — `cli` / `exec` / `vscode` for user-started threads, or JSON for spawned ones:
  - `{"subagent": "review"}`, `{"subagent": "memory_consolidation"}` — built-in side threads.
  - `{"subagent": {"thread_spawn": {"parent_thread_id": "...", "depth": 1, "agent_nickname": "Tesla", "agent_role": "explorer"}}}` — collab/multi-agent spawns (depth can exceed 1: children spawn grandchildren).

`threads` also carries `agent_nickname`, `agent_role`, `model`, `first_user_message`, `tokens_used`. Without the SQLite DB, the same linkage is in each rollout file's first line: `type: "session_meta"` whose `payload` has `id`, `cwd`, `model_provider`, `forked_from_id`, and the same `source.subagent.thread_spawn` object.

The finder maps these to `parent_id` and `agent = "nickname (role)"`; `get <parent-thread-id>` lists children under `subagents`, and `get <child-thread-id>` returns the child's rollout events.
