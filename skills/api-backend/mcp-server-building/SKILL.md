---
name: mcp-server-building
description: >
  Use this skill when building, scaffolding or shipping an MCP server: deciding
  tools vs resources vs prompts, choosing Python (mcp 2.x) or TypeScript
  (@modelcontextprotocol/server 2.x), implementing primitives on the 2026-07-28
  stateless spec (server/discover, _meta, resultType, InputRequiredResult/MRTR),
  wiring stdio or Streamable HTTP, adding OAuth, error handling and rate limits,
  testing with MCP Inspector, and deploying or publishing to the MCP Registry.
  Triggers on "build an MCP server", "expose my API to Claude/Cursor", "add a
  tool to my MCP server", "mcp server template", "my MCP server returns 421",
  "sampling is deprecated, now what".
version: 1.0.0
author: Skill Foundry
license: MIT
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - copilot
  - windsurf
  - opencode
  - openclaw
tags:
  - mcp
  - model-context-protocol
  - server
  - python
  - typescript
  - tools
  - resources
  - prompts
  - streamable-http
  - stdio
  - oauth
  - agent-integration
geo:
  primary_workflows:
    - contract_design
    - server_scaffolding
    - primitive_implementation
    - transport_selection
    - auth_and_hardening
    - testing_and_inspection
    - deployment_and_publishing
  target_roles:
    - backend_developer
    - platform_engineer
    - ai_engineer
    - integration_developer
  complexity_level: intermediate
  prerequisite_knowledge:
    - json_rpc
    - python_or_typescript
    - http_basics
    - oauth_basics
---

# MCP Server Building

Build MCP servers a real host can load. Revision `2026-07-28` is **stateless**:
no `initialize` handshake, no `Mcp-Session-Id`, per-request metadata, mandatory
`server/discover`, and multi-round-trip requests instead of a back-channel.
Pre-2026 tutorials teach a protocol that no longer exists. Verify every API
against the installed SDK (`mcp` 2.x, `@modelcontextprotocol/server` 2.x).

## Quick Reference

| Dimension | Check | Failure symptom if wrong |
|---|---|---|
| 🔵 Contract | Each capability is a tool, resource, or prompt on purpose | Model calls a resource; app "calls" a prompt |
| 🔵 Naming | `verb_noun` tools, `scheme://` URIs, kebab prompts | Collisions, unusable menus |
| 🟢 Schema | Types/constraints in the schema, description per field | Model guesses, retries blindly |
| 🟢 Errors | `ToolError` for fixable, `MCPError` for not | Silent failures or opaque 500s |
| 🟡 Transport | stdio local, Streamable HTTP deployed | Works locally, dead in prod |
| 🟡 Statelessness | No session state; handles passed as arguments | Breaks on worker 2 |
| 🟠 Deploy | Host allowlist set, MRTR key shared | `421`, intermittent `-32602` |
| 🔴 Cache | `ttlMs`/`cacheScope` set and honest | Stale catalogs or tenant leakage |

## 1. The protocol you are targeting

- **Every request is self-describing** in `_meta`:
  `io.modelcontextprotocol/protocolVersion` + `.../clientCapabilities` (required),
  `.../clientInfo` (SHOULD). Servers stamp `.../serverInfo` into results.
- **`server/discover` is a MUST**: returns `supportedVersions`, `capabilities`,
  `instructions`, `ttlMs`, `cacheScope`. Both SDKs answer it from your
  registered primitives.
- **Every result carries `resultType`**: `"complete"` or `"input_required"`.
- **Elicitation/sampling/roots are now MRTR**: return an `InputRequiredResult`
  with `inputRequests` + `requestState`; the client retries with
  `inputResponses`. No server→client request exists.
- **List/read results are cacheable**: `ttlMs` + `cacheScope` required;
  deterministic tool order SHOULD.
- **HTTP requests carry `Mcp-Method`, `Mcp-Name`, `MCP-Protocol-Version`**, so
  gateways route without parsing bodies.
- **Removed**: `ping`, `logging/setLevel`, roots list-changed, the GET stream,
  `resources/subscribe`, SSE resumability. **Deprecated**: Roots, Sampling,
  Logging, HTTP+SSE.

Full detail (error codes, `_meta` table, version negotiation):
`references/mcp-spec-context.md`.

**Design consequence:** no sessions means any request may hit any instance.
State that must survive a call is an explicit handle the model passes back
(`jobId`, `pageToken`, `draftId`) — never hidden transport state.

## 2. Contract first, before code

| Name | Primitive | Trigger | Input | Output | Side effects |
|---|---|---|---|---|---|
| `search_tickets` | tool | model | `query`, `status?`, `limit=10` | `Ticket[]` | none |
| `create_ticket` | tool | model | `subject`, `body`, `priority`, `idempotency_key?` | `Ticket` | writes |
| `close_ticket` | tool | model | `ticket_id` (+ confirm) | text | destructive |
| `config://limits` | resource | app | — | JSON | none |
| `tickets://{ticket_id}` | resource template | app | `ticket_id` | JSON | none |
| `triage` | prompt | human | `ticket_id` | message | none |

**Primitive choice.** Tool = action the *model* chooses (anything with side
effects or arguments). Resource = read-only data the *application* attaches as
context (config, docs, records). Prompt = template a *person* picks from a menu,
with flat string arguments. A "get_ticket" tool that only reads is a resource —
it burns model attention and a round trip.

**Naming.** Tools `verb_noun` snake_case; prompts kebab-case; resources
`scheme://path`. The description is the prompt — one clause of *when*, one of
*what it returns*. Put every constraint in the schema (`min`/`max`/`enum`/
`default`, per-property `description`): `Field(ge=1, le=50)` gives
self-correcting retries; prose in a docstring does not.

**What the model needs that your API does not have:** search-before-write,
ids-before-actions, small paged reads. Add `search_*`/`list_*` tools so ids get
discovered, not invented. Cap page sizes — an unbounded list is a context bomb.
Writes take an `idempotency_key`; the model *will* retry. Scope destructive
tools narrowly: `close_ticket(id)`, not `update_ticket(**fields)`.

## 3. Stack selection

| | **Python (`mcp` 2.x)** | **TypeScript (`@modelcontextprotocol/server` 2.x)** |
|---|---|---|
| Install | `uv add "mcp[cli]"` | `npm i @modelcontextprotocol/server zod` |
| Runtime | Python 3.11+ | Node 20+, Bun, Deno, Workers |
| Server object | `from mcp.server import MCPServer` | `new McpServer({name, version})` |
| API style | decorators `@mcp.tool()/resource()/prompt()` | `registerTool/Resource/Prompt(...)` |
| Schema source | type hints + Pydantic `Field` | Zod **v4** `z.object(...)` |
| Transport | `mcp.run(transport=...)` | `serveStdio(factory)` / `createMcpHandler(factory)` |
| Edge/serverless | ASGI (FastAPI, Lambda container) | first-class (Workers, Vercel, Deno, Bun) |
| Choose when | data/ML libs, internal Python services, a box | edge deploy, shared types with a TS frontend, npm distribution |

Pick by where it runs and who maintains it, not by taste. Both SDKs answer
`server/discover`, stamp `_meta`/`resultType`, enforce `Mcp-*` headers and drive
MRTR — the protocol work is not yours to write.

## 4. Scaffold

Start from the verified scaffolds, delete what you do not need:
`templates/server-py-template.py` (tools + resource template + prompt,
`ToolError`/`ResourceNotFoundError`, MRTR confirm, optional OAuth, transport
switch) and `templates/server-ts-template.ts` (same surface, Zod,
`createMcpHandler`, `serveStdio`, Node mount).

```bash
# Python
uv init support-tickets && cd support-tickets && uv add "mcp[cli]"
cp <skill>/templates/server-py-template.py server.py
uv run mcp dev server.py                      # Inspector over stdio

# TypeScript
npm init -y && npm pkg set type=module
npm i @modelcontextprotocol/server zod && npm i -D typescript tsx @types/node
cp <skill>/templates/server-ts-template.ts src/index.ts
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

Keep one server definition even if you only need stdio today: the HTTP handler
calls that factory per request, and a second definition drifts from the first.

## 5. Implement the primitives

**Tools (Python).** Name from the function, description from the docstring,
schema from the type hints — do not hand-write JSON Schema unless you drop to
the low-level `Server`.

```python
@mcp.tool(annotations={"read_only_hint": True})
def search_tickets(
    query: Annotated[str, Field(description="Words to match in subject or body.")],
    status: Literal["open", "pending", "closed"] | None = None,
    limit: Annotated[int, Field(ge=1, le=50)] = 10,
) -> list[Ticket]:
    """Search support tickets by keyword, optionally filtered by status."""
    hits = search(query, status)[:limit]
    if not hits:
        raise ToolError("No tickets matched; try a broader query.")
    return hits
```

**Tools (TypeScript).**

```ts
server.registerTool('search_tickets', {
  description: 'Search support tickets by keyword, optionally filtered by status.',
  annotations: { readOnlyHint: true },
  inputSchema: z.object({
    query: z.string().min(1).describe('Words to match in subject or body'),
    status: z.enum(['open', 'pending', 'closed']).optional(),
    limit: z.number().int().min(1).max(50).default(10)
  })
}, async ({ query, status, limit }) => ({
  content: [{ type: 'text', text: JSON.stringify(hits) }],
  structuredContent: { result: hits }
}));
```

Return typed data: `content` is what the model reads, `structuredContent` /
`structured_content` is what the application gets. JSON Schema 2020-12 is fully
supported now — use `oneOf`/`$ref` instead of flattening real inputs.

**Resources.** Addressed by URI, not name; read on demand, listed cheaply.

```python
@mcp.resource("config://limits", mime_type="application/json")
def limits() -> dict[str, int]:
    """Operational limits for this server."""
    return {"max_page_size": 50}

@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> Ticket:
    """One ticket by id."""
    t = STORE.get(ticket_id)
    if t is None:
        raise ResourceNotFoundError(f"No ticket {ticket_id!r}.")   # -> -32602
    return t
```

Placeholder names must equal parameter names (Python fails at import time if not).
`str` → text, `bytes` → base64 blob, anything else → JSON text; declare
`mime_type`.

**Prompts.** Return a `str` for one user message, or `UserMessage`/
`AssistantMessage` list to seed a conversation. Embed resources with
`EmbeddedResource` rather than pasting text, so clients can render attachments.

**Asking the user mid-call (MRTR).** Round 1 returns the question; round 2 reads
the answer under the same key:

```python
@mcp.tool(annotations={"destructive_hint": True})
async def close_ticket(ticket_id: str, ctx: Context) -> str | InputRequiredResult:
    """Close a ticket. Asks the human for confirmation before acting."""
    if ctx.input_responses is None:
        return InputRequiredResult(
            input_requests={"confirm": CONFIRM_CLOSE},     # ElicitRequest
            request_state=f"close:{ticket_id}")            # sealed, echoed back
    answer = ctx.input_responses.get("confirm")
    if not isinstance(answer, ElicitResult) or not (answer.content or {}).get("ok"):
        return f"Ticket {ticket_id} left open."
    ...
```

TypeScript: `return inputRequired({ inputRequests, requestState })`, read with
`acceptedContent(ctx.mcpReq.inputResponses, 'confirm')`.

## 6. Transport, errors, auth, limits

**Transport.** stdio = local, host-launched, one user; stdout is the wire, so log
to stderr and never `print`/`console.log` in a handler. Streamable HTTP = anything
deployed: one POST endpoint, per-request JSON or SSE, `subscriptions/listen` for
change notifications. SSE = deprecated. Traps, scaling, packaging:
`references/transport-guide.md`.

**Errors.** One question decides the path: *could a smarter model have avoided
this?*

| Situation | Do | Model sees |
|---|---|---|
| Bad arguments | let the SDK validate | readable `isError`, retryable |
| Execution/business failure | raise `ToolError` / `isError: true` | your message in `content` |
| Request itself invalid | raise `MCPError(code, message)` | JSON-RPC error, nothing |
| Unplanned exception | let it raise | sanitised `-32603`, traceback in your log |
| Missing resource | `ResourceNotFoundError` | `-32602` with the URI |
| Unknown version | SDK handles | `-32022` + supported list |

Never return a string that says "error": `isError: false` makes the model treat
it as the answer and move on.

**Auth (HTTP only).** Your server is an OAuth 2.1 resource server — it verifies
tokens, never issues them.

```python
mcp = MCPServer("notes", token_verifier=JwtVerifier(), auth=AuthSettings(
    issuer_url=AnyHttpUrl("https://auth.example.com"),
    resource_server_url=AnyHttpUrl("https://mcp.example.com/mcp"),
    required_scopes=["notes:read"], validate_token_resource=True))
# inside a handler: get_access_token() -> client_id, scopes
```

The SDK publishes RFC 9728 metadata and answers 401 with a `WWW-Authenticate`
pointer to it. `token_verifier` and `auth` always travel together. Stdio has no
auth — the process boundary is the boundary.

**Rate limits.** Limit per `(client_id, tool_name)`; there is no connection to
count. Reject at the edge on `Mcp-Method`/`Mcp-Name` (and `Mcp-Param-*` for
per-tenant metering) with 429 + `Retry-After`. Inside a handler,
`ToolError("rate limited, retry in 5s")` beats a transport failure.

## 7. Test before claiming it works

1. **Inspector** (real host behaviour, stdio): `uv run mcp dev server.py` /
   `npx @modelcontextprotocol/inspector npx tsx src/index.ts`. Call every tool
   with happy path, missing required arg, out-of-range value, and the error
   path. If the rendered form is confusing, the model is confused too.
2. **In-process**, no transport:
   `async with Client(mcp, elicitation_callback=cb, raise_exceptions=True) as c:`
   — then assert on `is_error`, `content`, `structured_content`.
3. **Endpoint**: `curl -X POST … -H 'Mcp-Method: server/discover'` and check
   `resultType`, `supportedVersions`, `ttlMs`, `cacheScope`, `serverInfo`.
4. **Scale shape**: two workers, an MRTR round trip through both. Intermittent
   failure = per-process `requestState` key.

## 8. Deploy and publish

- [ ] `transport_security` / `allowedHosts` names the real hostname, or every
      request is `421 Invalid Host header`.
- [ ] TLS termination passes `--proxy-headers` (or framework equivalent).
- [ ] MRTR `requestState` sealed with a shared key across workers; token small
      and self-contained.
- [ ] No session state, no per-request behavioural caches.
- [ ] Auth verifier + `AuthSettings`; scopes checked per tool.
- [ ] Logs to stderr/pipeline; traces via `traceparent` in `_meta`.
- [ ] `ttlMs`/`cacheScope` set; `"public"` only for caller-independent payloads.
- [ ] Package published (PyPI/npm/OCI) and `server.json` pushed to the registry
      under a namespace you own.

## Worked example 1 — Python stdio bookshop

**Contract:** `search_books(query, limit=10)` tool, `books://{title}` resource,
`review-book` prompt. Local, read-only, no auth.

```python
from typing import Annotated
from pydantic import Field
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError

CATALOG = {"Dune": "Frank Herbert", "Neuromancer": "William Gibson"}
mcp = MCPServer("bookshop", title="Bookshop", version="1.0.0",
                instructions="Look up books by title; read books://<title> for detail.")

@mcp.tool(annotations={"read_only_hint": True})
def search_books(
    query: Annotated[str, Field(description="Title or author to search for.")],
    limit: Annotated[int, Field(ge=1, le=20)] = 10,
) -> list[str]:
    """Search the catalog by title or author."""
    q = query.lower()
    return [t for t, a in CATALOG.items() if q in t.lower() or q in a.lower()][:limit]

@mcp.resource("books://{title}", mime_type="text/plain")
def book(title: str) -> str:
    """One catalog entry."""
    if title not in CATALOG:
        raise ResourceNotFoundError(f"No book titled {title!r}.")
    return f"{title} by {CATALOG[title]}"

@mcp.prompt(title="Review a book")
def review_book(title: str) -> str:
    """Ask for a short review of one book."""
    return f"Write a 150-word review of {title}."

if __name__ == "__main__":
    mcp.run()          # stdio
```

Verify: `mcp dev server.py`; call `search_books` with `limit=999` and watch the
schema reject it before your function runs; read `books://Dune`;
`mcp install server.py --name Bookshop`. Ship as `pipx run bookshop-mcp` with
`server.json` → `transport: {"type":"stdio"}`.

## Worked example 2 — TypeScript notes server on HTTP, per-caller

**Contract:** `add_note(text)`, `whoami()`, `notes://{id}` resource. Multi-user,
Node behind TLS.

```ts
import { McpServer, createMcpHandler } from '@modelcontextprotocol/server';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { createMcpExpressApp, requireBearerAuth } from '@modelcontextprotocol/express';
import * as z from 'zod/v4';

const notes = new Map<string, string>();            // module scope, created once

export function createServer() {                    // called once per request
  const server = new McpServer({ name: 'notes', version: '1.0.0' }, {
    cacheHints: { 'tools/list': { ttlMs: 60_000, cacheScope: 'private' } }
  });
  server.registerTool('add_note',
    { description: 'Append a note', inputSchema: z.object({ text: z.string().min(1) }) },
    async ({ text }) => {
      const id = crypto.randomUUID().slice(0, 8);
      notes.set(id, text);
      return { content: [{ type: 'text', text: `Saved as notes://${id}` }] };
    });
  server.registerTool('whoami', { description: 'Name the authenticated caller' },
    async (_a, ctx) => ({ content: [{ type: 'text',
      text: ctx.http?.authInfo?.clientId ?? 'anonymous' }] }));
  return server;
}

const handler = createMcpHandler(createServer, { legacy: 'stateless' });
const app = createMcpExpressApp({ host: '0.0.0.0', allowedHosts: ['mcp.example.com'] });
const node = toNodeHandler(handler);
app.all('/mcp', requireBearerAuth({ verifier }), (req, res) => void node(req, res, req.body));
app.listen(8080);
```

Why each choice: per-request factory means no state survives (any replica serves
any call); `allowedHosts` avoids the `421` wall; `private` cache scope because
the tool list varies by caller; `authInfo` comes from the verifier in front, never
from the body. Verify with a `server/discover` curl, then two replicas.

## Worked example 3 — Python HTTP with confirmation, OAuth, four workers

**Contract:** `refund(amount)`, destructive, needs human confirmation, scope
`billing:write`, `uvicorn --workers 4` behind a proxy.

```python
mcp = MCPServer(
    "billing", version="1.0.0",
    token_verifier=JwtVerifier(),
    auth=AuthSettings(issuer_url=AnyHttpUrl("https://auth.example.com"),
                      resource_server_url=AnyHttpUrl("https://mcp.example.com/mcp"),
                      required_scopes=["billing:write"], validate_token_resource=True),
    # four worker processes → four keys unless you share one, and the retry
    # of an MRTR round can land on a sibling worker
    request_state_security=RequestStateSecurity(key=os.environ["REQUEST_STATE_KEY"].encode()),
)

@mcp.tool(annotations={"destructive_hint": True})
async def refund(amount: int, ctx: Context) -> str | InputRequiredResult:
    """Refund an amount, once a human has confirmed it."""
    if ctx.input_responses is None:
        return InputRequiredResult(input_requests={"ok": CONFIRM},
                                   request_state=f"refund:{amount}")
    answer = ctx.input_responses.get("ok")
    if not isinstance(answer, ElicitResult) or not (answer.content or {}).get("ok"):
        return "refund cancelled"
    return f"refunded ${amount}"

app = mcp.streamable_http_app(transport_security=TransportSecuritySettings(
    allowed_hosts=["mcp.example.com", "mcp.example.com:*"],
    allowed_origins=["https://app.example.com"]))
```

Run `uvicorn server:app --proxy-headers --forwarded-allow-ips='*' --workers 4`.
Test the two rounds against *different* workers on purpose; `-32602 Invalid or
expired requestState` means the shared key is not deployed.

## Anti-patterns

| Anti-pattern | Why it breaks | Instead |
|---|---|---|
| Building on the `initialize` handshake | Removed; new hosts never call it | Per-request `_meta`, let the SDK handle it |
| Conversation state in a session/transport | No sessions exist; breaks on replica 2 | Return a handle; model passes it back |
| Server "calls back" to elicit input | Back-channel is gone | Return `InputRequiredResult` |
| `print()` / `console.log()` in stdio server | Corrupts the JSON-RPC stream | `logging` / `console.error` |
| Returning `"Error: not found"` as output | `isError: false` → treated as the answer | raise `ToolError` / `isError: true` |
| One mega-tool `do_everything(action=…)` | Model cannot pick arguments reliably | Small single-purpose tools |
| Unbounded list results | Context blow-up, timeouts | `limit` + max, paging handles |
| Description-less tools/fields | Model guesses, retries blindly | *when* clause + per-field `.describe()` |
| Auth checked inside one tool only | Every other tool is open | Verify at the edge, scopes per tool |
| `cacheScope: "public"` on per-tenant tools | Cross-tenant leakage via shared cache | `"private"` unless byte-identical |
| Deploying without a Host allowlist | Every request is `421` | `TransportSecuritySettings` / `allowedHosts` |
| Per-process `requestState` key, N workers | Intermittent `-32602` on MRTR retry | Shared key, small token |
| Two server definitions (stdio + HTTP) | They drift; tests stop proving prod | One factory, two mounts |
| Adopting Sampling / Roots / Logging | Deprecated, 12-month window | Tool params, direct LLM calls, stderr/OTel |

## Quality checklist

- [ ] Every capability is deliberately a tool, a resource, or a prompt.
- [ ] Names: `verb_noun` tools, `scheme://` resources, kebab prompts.
- [ ] Descriptions say *when* to use it, not just what it does.
- [ ] Constraints live in the schema (min/max/enum/default), not prose.
- [ ] Writes take an idempotency key; destructive tools confirm via MRTR.
- [ ] `ToolError` where the model can recover, `MCPError` where it cannot.
- [ ] Missing resources raise not-found, not a generic crash.
- [ ] No session state; cross-call state is an argument handle.
- [ ] Transport matches reality; stdout never carries logs.
- [ ] `ttlMs` + `cacheScope` set, with honest scope.
- [ ] Inspector forms are sane; every error path is readable.
- [ ] `server/discover` returns the right versions and capabilities.
- [ ] Deploy: Host allowlist, proxy headers, shared MRTR key, auth verifier.
- [ ] Package + `server.json` published under a namespace you own.

## Safety rules

1. **Least privilege:** if a tool can do it, the model can do it. No `run_sql`
   with a superuser credential — scope the credential to the operation.
2. **Confirm before irreversible actions** — deletes, refunds, deploys, sends.
   MRTR, not a warning in the description.
3. **Never trust client-supplied paths or URLs.** Resolve template variables
   against a fixed root (`realpath` + prefix check) before reading.
4. **Validate at the schema, authorize at the tool.** A valid argument is not an
   authorized action; check scopes for the specific operation.
5. **Sanitise what leaves.** Never leak stack traces, SQL, or internal hosts; the
   SDK's sanitiser only covers unplanned exceptions.
6. **Bound everything:** page sizes, timeouts, retries, payload size
   (`max_request_body_size`), tokens returned to the model.
7. **Treat `requestState` as untrusted input**: small, self-contained, no
   pointers into server memory.
8. **No secrets in tool output** — results land in context windows, logs, traces.

## Platform notes

| Platform | Notes |
|---|---|
| Claude Code / Desktop | stdio; `mcp install` targets Desktop, config JSON for the rest |
| Cursor / VS Code / Windsurf | stdio in their own MCP config files; Inspector for a quick check |
| Codex / Gemini CLI / OpenCode | pass the launch command in their MCP config; stdio first |
| Cloud / Workers | TS `createMcpHandler` + `export default handler`; nothing to store |

## References

- `references/mcp-spec-context.md` — `_meta`, `server/discover`, MRTR, caching,
  headers, error codes, deprecations, version negotiation, auth posture.
- `references/transport-guide.md` — stdio vs Streamable HTTP, deployment traps
  (`421`, proxy headers, workers, `requestState`), testing, packaging, Registry.
- `templates/server-py-template.py` — verified Python scaffold (mcp 2.3.0).
- `templates/server-ts-template.ts` — verified TypeScript scaffold
  (`@modelcontextprotocol/server` 2.4.x), typechecks under `strict`.
