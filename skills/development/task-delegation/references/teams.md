# Teams and shared state

Use peer communication when it materially helps workers resolve shared contracts or competing evidence. Prefer ordinary subagents when focused assignments and parent integration suffice. Inspect actual team, messaging, task, and wait capabilities before relying on them.

## Coordinate writes

- Assign disjoint write scopes. Order shared-file edits or use isolated worktrees, following the installed worktree procedure. Share interface decisions before dependent edits.
- Re-read shared content immediately before editing. Reconcile intervening changes rather than overwriting another worker's work.
- Coordinate formatters, generators, and shell rewrites over shared paths; they can bypass editor conflict checks.
- Respect the repository's active-operation and delivery ownership. A separate checkout does not authorize a competing push or deployment.

## Coordinate work

- Use supported task claims when available; otherwise assign one explicit owner in the parent's record.
- Distinguish created, running, idle, waiting, failed, and completed. An idle agent is not necessarily done. A sent message is not acknowledgment or execution; use the host's start/resume primitive when needed.
- Keep amendments and sibling-impacting findings visible to the parent. Confirm receipt before depending on a changed contract.
- Observe completion through the mechanism established in the main workflow. A wait observes work; it does not necessarily start or resume a worker. Recheck relevant state after wakeup or timeout.
- Collect required results before final integration. Stop unused task-owned workers safely, preserving useful edits and evidence. Keep user decisions and the combined report in the parent session.
