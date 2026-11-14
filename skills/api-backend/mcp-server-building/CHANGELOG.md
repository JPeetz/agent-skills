# Changelog — MCP Server Building Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-11-14

### Added
- Initial release by Skill Foundry, targeting MCP specification revision
  `2026-07-28` (stateless core) with the current SDK lines: Python `mcp` 2.3.0
  and TypeScript `@modelcontextprotocol/server` 2.4.x.
- Stateless-protocol primer: per-request `_meta`
  (`protocolVersion`/`clientCapabilities`/`clientInfo`/`serverInfo`), mandatory
  `server/discover`, required `resultType`, removed `ping`/`logging/setLevel`/
  root list-changed, removed GET stream and `resources/subscribe`, no SSE
  resumability, and the deprecated Roots/Sampling/Logging surface with migration
  targets.
- Contract-first planning workflow: a tools/resources/prompts decision table,
  naming conventions (`verb_noun`, `scheme://`, kebab prompts),
  description-as-prompt guidance, schema-constraint rules, paging and
  idempotency requirements.
- Stack-selection matrix (Python vs TypeScript) keyed on runtime, deployment
  target, schema source (type hints/Pydantic vs Zod v4) and distribution.
- Primitive implementation patterns for both SDKs: `@mcp.tool()/resource()/
  prompt()` and `registerTool/Resource/Prompt`, structured output, resource
  templates with placeholder/parameter agreement, prompt message lists, and
  MRTR confirmation flows (`InputRequiredResult` / `inputRequired`,
  `request_state` sealing, `inputResponses`).
- Transport guidance: stdio (stdout-is-the-wire rule, host config JSON),
  Streamable HTTP (`Mcp-Method`/`Mcp-Name`/`MCP-Protocol-Version` headers,
  request-scoped SSE, `subscriptions/listen`), and SSE as deprecated.
- Error-handling model: `ToolError` vs `MCPError` vs unplanned crash vs
  `ResourceNotFoundError`, with the `-32602` resource-not-found change and the
  `-32020`/`-32021`/`-32022` allocation policy.
- Authorization (OAuth 2.1 resource server, `TokenVerifier` + `AuthSettings`,
  RFC 9728 metadata, 401 challenge), plus rate-limit guidance at the edge and
  in-handler.
- Testing workflow: MCP Inspector for schema/error paths, in-memory `Client`
  with `raise_exceptions=True`, `server/discover` curl verification, and a
  two-worker MRTR replay to catch per-process state keys.
- Deployment and publishing: Host allowlist (`421` diagnosis), `--proxy-headers`,
  multi-worker `requestState` sharing, scaling shape per protocol era, change
  notification fan-out, packaging (PyPI/npm/OCI) and `server.json` registry
  publication with namespace verification.
- Three worked examples: Python stdio bookshop, TypeScript notes server on HTTP
  with per-caller auth, and Python HTTP billing server with MRTR confirmation,
  OAuth and four workers.
- Anti-pattern table (14 entries), 14-item quality checklist, 8 safety rules,
  and platform compatibility notes.
- `templates/server-py-template.py` — support-tickets scaffold, executed against
  `mcp` 2.3.0 (in-memory client, stdio, and HTTP `server/discover` /
  `tools/list` / `tools/call` verified).
- `templates/server-ts-template.ts` — same surface in TypeScript, typechecked
  under `strict` against `@modelcontextprotocol/server` 2.4.0 and verified over
  Streamable HTTP including the `input_required` round trip.
- `references/mcp-spec-context.md` and `references/transport-guide.md`.
- 7 eval cases covering trigger and near-miss behaviour.
