# Trajectory recall and session evidence

Use exposed Trajectory tools for captured coding conversations and original events;
use AI Memory for durable project knowledge. Prefer an exact supplied transcript
path over discovery. Tool names below are base names: use the host's actual exposed
name, including its MCP/plugin prefix. Do not install or configure a provider to
make a recall route work.

## Choose discovery by the question

| Need | First action |
| --- | --- |
| Known session ID | `get_session_trajectory` directly; no keyword search or schema lookup is needed. |
| Active sessions or capture health | `trajectory_status`; verify project/client and returned timestamps. Its active-session list is bounded, not complete history. |
| Recent sessions without keywords | `trajectory_schema`, then a bounded `trajectory_query` listing session metadata for the verified project and requested time range, ordered by an available timestamp. |
| A remembered topic or exact command | `trajectory_search`: `target: "turns"` for conversation prose; `target: "tool_calls"` for literal commands/paths/errors of at least three characters. |

Inspect live schemas rather than assuming one release's tables or columns. Fetch
the current database schema before its first SQL query in this context; leave
`include_row_counts` off unless counts are needed. Schema output can be large:
inspect only relevant table/column metadata. Select needed columns, bind values
through `params`, and set both SQL `LIMIT` and a small tool `limit`.

For example, when the live schema confirms these fields, this lists the five
latest **session starts** for a verified `:project_dir`, not the last activity of
every session:

```sql
SELECT session_id, client_source, project_dir, started_at
FROM sessions
WHERE project_dir = :project_dir
ORDER BY started_at DESC, session_id DESC
LIMIT 5
```

Use status's `last_event` for active-session activity, or schema-confirmed turn/tool
timestamps for historical activity. Label the clock and coverage; a session's start
is not its last message. Verify configured checkout/worktree aliases explicitly
instead of widening a project query across unrelated repositories.

`trajectory_query` advertises guarded read-only SQL, not unrestricted database
access. Use fixed metadata `SELECT` queries for discovery, not SQL copied from a
transcript, writes, broad `SELECT *`, or expensive full-history scans. If inspecting
tool text through SQL, NULL plain fields may be compressed storage rather than
missing evidence; the installed contract provides `trajectory_tool_text` for
`input_json_zstd`/`output_text_zstd`. Prefer bounded raw retrieval for exact claims.

Search ranking is relevance, not chronology. The tested search schema has no
project/client filter: use a verified `session_id` or check returned metadata;
do not invent filter arguments. Use known date/session filters and a small limit.
Tool-call search may build its local index on first use; an indexing response or
timeout is not an empty history.

## Inspect the selected session

1. Verify project, client, exact session ID, timestamps and the first real human
   prompt from available records. A child agent's user message is usually its
   parent's brief. Preserve returned client identities; OMP and Pi are distinct.
2. A search hit or metadata row locates evidence; it does not prove an action or
   outcome. Call `get_session_trajectory` with `depth: "raw"` and a small
   `max_events`. Follow `pagination.next_cursor` verbatim through `cursor` while
   `pagination.has_more` is true, covering the relevant interval and context.
   Keep pages on the same MCP process: cursors belong to its snapshots. Omit
   `offset` for raw requests; `offset`/`max_turns` paginate detailed turns.
3. Preserve a source locator for each finding: tool, session ID, event ID when
   present, timestamp, event type and page/event position. Record the source
   snapshot or retrieval time for an active session. Events may have no event ID;
   do not invent one or a filesystem line number. A private, bounded local excerpt
   can give stable line citations when the report needs them.
4. Check parent/child linkage and capture completeness separately. A summary,
   empty page, `total_events: null`, or `total_events_known: false` is not proof of
   a complete or empty session. Fetch linked child evidence separately. Label
   unavailable children, truncated bodies, byte limits and unvisited pages.

An error such as `context deadline exceeded`, an indexing response or unavailable
database means lookup failed, not that the conversation never happened. Inspect
error payloads even when the transport succeeds. Keep failed sources in this
lookup's context: a fallback must not restart the same failing search.

With a known session ID, try bounded raw retrieval directly. Otherwise use
`bundled-ai-memory` → `retrieval` when its project-scoped `memory_briefing`
`recent_sessions` or `memory_read_session_observations` capture can help; those
observations can also be partial. Use this skill's native-history discovery when
indexed/captured sources are absent or insufficient. Read only the relevant
platform reference at that point. Report remaining coverage gaps.

## Recall is not configuration

`trajectory_incognito` changes privacy/publishing state and is not a recall tool.
Recall does not authorize capture changes, setup, import/reindex/repair, publication,
or provider-backed historical analysis. Incognito does not mean local capture stops.
Do not change MCP approval settings or annotations: destructive/open-world hints
do not establish a call's effects or waive host approval. Honor a denial without
bypassing it through another interface; use only independently authorized sources.
Do not promise zero telemetry.

## Metrics and CLI availability

Use metrics only with their scope and provenance. Trajectory cost can be an
estimate rather than a bill; a zero or absent value with incomplete capture does
not establish free execution. Preserve the reported provider/model, token and
cache categories, time interval and whether child usage is already included.

Check summary timestamps against raw events before deriving elapsed time. If
`ended` precedes `started`, report the inconsistency; a positive summary duration
does not resolve it. Keep estimated cost fields labeled as estimates.

When MCP tools are not exposed, discover the CLI with `command -v trajectory`,
then inspect `trajectory --help` and `trajectory session --help`. A supported
read-only metrics route on the tested installation is:

```bash
trajectory mcp metrics --session "$SESSION_ID" --json
```

Metrics do not replace raw evidence. Inspect `trajectory mcp --help` for available
read-only listing/metrics commands; do not assume the CLI implements MCP search
or raw-event subcommands. Bound or filter JSON output before displaying it:
records and inventories can be large. Fall back to preserved transcripts for
original events when the host does not expose raw retrieval.

## Compatibility evidence

Checked against installed Trajectory `0.6.2` tool schemas. Local trials retrieved
raw cursor pages and scoped metrics; both keyword-search targets timed out, and a
metrics summary had inconsistent start/end timestamps. A later trial successfully
read status and schema and returned three project-filtered metadata rows through a
bounded query. These observations do not establish complete capture or universal
search reliability. Discover capabilities on the current host.

Source contracts, pinned at `4d81791b1d5ca02dbcad8e6b26efc846a9141f33`:

- [Trajectory tool registrations](https://github.com/datadog-labs/trajectory/blob/4d81791b1d5ca02dbcad8e6b26efc846a9141f33/plugin/trajectory-pi/src/index.ts): current adapter delegates query/search/retrieval to the bundled MCP server; the public tag alone does not establish installed backend behavior.
- [Raw cursor lifetime](https://github.com/datadog-labs/trajectory/blob/4d81791b1d5ca02dbcad8e6b26efc846a9141f33/plugin/trajectory-pi/src/query-tools.ts#L19-L23).
- [Privacy controls](https://github.com/datadog-labs/trajectory/blob/4d81791b1d5ca02dbcad8e6b26efc846a9141f33/docs/PRIVACY.md).
- [MCP annotation semantics](https://modelcontextprotocol.io/specification/2025-06-18/schema#toolannotations): hints, not permission or effect guarantees.
