# MCP spec context — revision `2026-07-28`

Everything a server author needs to know about the current revision, and what it
replaced. Verified against the MCP specification `2026-07-28`, the official
Python SDK `mcp` 2.3.0, and `@modelcontextprotocol/server` 2.4.x.

Source of truth:
- <https://modelcontextprotocol.io/specification/2026-07-28>
- <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
- <https://modelcontextprotocol.io/specification/2026-07-28/server/discover>

---

## 1. The headline: MCP is stateless

The protocol is no longer a bidirectional stateful connection. It is
request/response, and every request is self-describing.

| Removed | Replaced by |
|---|---|
| `initialize` / `notifications/initialized` handshake | Per-request `_meta` on every call |
| `Mcp-Session-Id` header, protocol-level sessions | Nothing — no session exists |
| Capabilities learned at handshake time | `server/discover` (servers **MUST** implement it) |
| Server-initiated `elicitation/create`, `sampling/createMessage`, `roots/list` | Multi Round-Trip Requests (MRTR) |
| HTTP `GET` notification stream; `resources/subscribe` / `unsubscribe` | `subscriptions/listen` (single opted-in stream) |
| `ping`, `logging/setLevel`, `notifications/roots/list_changed` | Log level per request via `_meta`; log to stderr |
| SSE resumability (`Last-Event-ID`, event ids) | A dropped stream means the client re-issues the request |

Consequence for deployment: **any request may land on any instance behind a
plain round-robin load balancer.** No sticky sessions, no shared session store.

State that must survive across calls is *application* state, and it travels as
an explicit handle the model passes back as an ordinary tool argument (a
`pageToken`, a `jobId`, a `draftId`). This is better than hidden transport
state: the model can see the handle and thread it between tools.

---

## 2. The request envelope

Every request carries required `_meta`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_tickets",
    "arguments": { "query": "export" },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": { "name": "my-app", "version": "1.0" },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

| `_meta` key | Direction | Required | Purpose |
|---|---|---|---|
| `io.modelcontextprotocol/protocolVersion` | request | **yes** | Version this request speaks |
| `io.modelcontextprotocol/clientCapabilities` | request | **yes** | What the client can answer (elicitation, sampling, roots, extensions) |
| `io.modelcontextprotocol/clientInfo` | request | SHOULD | Client identity for logs |
| `io.modelcontextprotocol/serverInfo` | every result | SHOULD | Server identity (moved out of the discover body) |
| `io.modelcontextprotocol/logLevel` | request | optional | Per-request log level; without it, servers **MUST NOT** emit `notifications/message` |
| `traceparent` / `tracestate` / `baggage` | request | optional | OpenTelemetry trace propagation |

The rule for `_meta` keys: reverse-DNS prefix. Any vendor extension must use
your own namespace and must not collide with `io.modelcontextprotocol/*`.

---

## 3. `server/discover` — mandatory

Servers **MUST** implement `server/discover`. It is how a client learns the
supported versions, capabilities, and identity before doing anything else, and
it is the stdio backward-compatibility probe.

Request: no body params beyond `_meta`.

```json
{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "method": "server/discover",
  "params": { "_meta": { "io.modelcontextprotocol/protocolVersion": "2026-07-28" } }
}
```

Result:

```json
{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "result": {
    "resultType": "complete",
    "supportedVersions": ["2026-07-28"],
    "capabilities": { "tools": {}, "resources": {}, "prompts": {} },
    "instructions": "Search and triage support tickets.",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": { "name": "support-tickets", "version": "1.0.0" }
    },
    "ttlMs": 300000,
    "cacheScope": "public"
  }
}
```

`serverInfo` is self-reported and unverified: for display, logging and
debugging only. Clients **SHOULD NOT** base security decisions on it.

Calling `server/discover` is *optional for clients*. A client may invoke any RPC
inline and handle `UnsupportedProtocolVersionError` instead. Both SDKs answer
`server/discover` for you from your registered primitives — you write nothing.

---

## 4. `resultType` and MRTR (`InputRequiredResult`)

Every result now carries a required `resultType`:

- `"complete"` — an ordinary result. Clients **MUST** treat results from
  earlier-revision servers that omit the field as `"complete"`.
- `"input_required"` — an interim result asking the client for more input.

An `InputRequiredResult` is how a tool asks the user something mid-call without
any back-channel:

```json
{
  "resultType": "input_required",
  "inputRequests": {
    "confirm": {
      "method": "elicitation/create",
      "params": {
        "message": "Closing T-1002 is not reversible. Confirm?",
        "requestedSchema": {
          "type": "object",
          "properties": { "ok": { "type": "boolean" } },
          "required": ["ok"]
        }
      }
    }
  },
  "requestState": "close:T-1002"
}
```

The client fulfils each entry in `inputRequests`, then **re-issues the same
request** with:

- `inputResponses` — keyed by the same names the server chose (`"confirm"`).
  Each value is an `ElicitResult`, `CreateMessageResult`, or `ListRootsResult`.
- `requestState` — the opaque token, echoed verbatim.

```
round 1: tools/call close_ticket  -> resultType: input_required + inputRequests + requestState
round 2: tools/call close_ticket (+ inputResponses + requestState) -> resultType: complete
```

Rules that bite:

- **`inputRequests` keys are server-chosen and must be echoed back.** Answers
  arrive under the same key; read them by key, not by position.
- **`requestState` is sealed with a per-process key by default.** Under
  `--workers 4` that is four keys, so a retry landing on a sibling worker fails
  with `-32602 Invalid or expired requestState` (see transport guide).
- **One channel per call.** A tool that uses a declared `Resolve(...)` /
  dependency parameter cannot also return `InputRequiredResult` from its body.
- Client capabilities are enforced: asking for elicitation from a client that
  did not declare it yields `-32021 MissingRequiredClientCapability`.
- `tools/call`, `prompts/get` and `resources/read` (template resources only) may
  all answer with `input_required`. Static resources take no context, so they
  cannot.

Client side, both SDKs drive the loop for you (up to a bounded number of
rounds); register the elicitation/sampling/roots callbacks and the retries are
invisible.

---

## 5. Cacheable results

`tools/list`, `prompts/list`, `resources/list`, `resources/templates/list`,
`resources/read` and `server/discover` are `CacheableResult`s and **MUST** carry:

| Field | Meaning |
|---|---|
| `ttlMs` | Freshness hint in milliseconds. `0` = do not cache. |
| `cacheScope` | `"public"` (shared intermediaries may cache) or `"private"` |

Defaults are `ttlMs: 0`, `cacheScope: "private"` — compliant and useless. Set
real hints. `"public"` is only correct when the payload is byte-identical for
every caller; a per-tenant tool list cached `public` leaks one tenant's catalog
to another.

Also: `tools/list` **SHOULD** be returned in a deterministic order. That is what
makes client-side caching and upstream prompt-cache hits work.

Python: `cache_hints={"tools/list": CacheHint(ttl_ms=60_000, scope="public")}`
(import `CacheHint` from `mcp.server.caching`).
TypeScript: `new McpServer({...}, { cacheHints: { 'tools/list': { ttlMs: 60_000, cacheScope: 'public' } } })`.

---

## 6. Streamable HTTP request headers

Every POST to the MCP endpoint carries:

| Header | Value | When |
|---|---|---|
| `Content-Type` | `application/json` | always |
| `Accept` | `application/json, text/event-stream` | always |
| `MCP-Protocol-Version` | e.g. `2026-07-28` | always |
| `Mcp-Method` | the JSON-RPC `method` | **all** requests |
| `Mcp-Name` | `params.name` or `params.uri` | `tools/call`, `resources/read`, `prompts/get` |
| `Mcp-Param-{name}` | value of an `x-mcp-header`-annotated tool parameter | optional, server-declared |

Headers exist so gateways, rate limiters and WAFs can route and authorize
without parsing bodies. A mismatch between `Mcp-Name` and the body is
`-32020 HeaderMismatch` — both SDKs enforce this for you.

`x-mcp-header` lets a server mirror a primitive tool parameter into a header so
an edge proxy can meter per-tenant: declare `"x-mcp-header": "Region"` on a
`string`/`integer`/`boolean` property reachable via `properties` only (no
arrays, `$ref`, or composition keywords).

---

## 7. Error codes

| Code | Name | Use |
|---|---|---|
| `-32700` | Parse error | Malformed JSON |
| `-32600` | Invalid request | Not a valid JSON-RPC request / missing `_meta` |
| `-32601` | Method not found | Unknown method |
| `-32602` | Invalid params | Bad arguments; **also the code for a missing resource** (was `-32002`) |
| `-32603` | Internal error | Unexpected server fault (sdk sanitises the message) |
| `-32020` | HeaderMismatch | `Mcp-Name`/`Mcp-Method` disagree with the body |
| `-32021` | MissingRequiredClientCapability | Server needs a capability the client did not declare |
| `-32022` | UnsupportedProtocolVersion | Include `data.supported` and `data.requested` |

Allocation policy: `-32000..-32019` implementation-defined, `-32020..-32099`
reserved for the specification. Never invent a code in the reserved range.

**Two error paths inside a tool, and they are not interchangeable:**

- *Execution failed, a smarter model could have avoided it* → a **tool error**:
  the call succeeds with `isError: true` and the message in `content`. The model
  reads it and retries. Python: `raise ToolError(...)`. TypeScript: return
  `{ isError: true, content: [...] }`.
- *The request itself should be rejected* (no retry helps) → a **protocol
  error**: `raise MCPError(code=..., message=...)` / throw. The model sees
  nothing; the host gets a JSON-RPC error.

Never `return` a string like `"Error: not found"` — the model reads it as a
successful result and moves on.

---

## 8. Primitives, and who triggers them

| Primitive | Triggered by | Addressed by | Typical use |
|---|---|---|---|
| Tool | the **model** | name | actions, lookups, writes |
| Resource | the **application** | URI (static or `{template}`) | context: files, records, docs |
| Prompt | a **human** | name + string args | slash commands, menu entries |

- Tool input schemas are full **JSON Schema 2020-12**: `oneOf`, `anyOf`, `$ref`,
  composition and resource bounds are all legal now. Stop flattening complex
  input into a bag of optional strings.
- `outputSchema` / `structuredContent` are supported (`structured_content` in
  Python, `structuredContent` in TS). Return typed objects; the SDK derives the
  schema.
- Prompt arguments are a **flat list of named strings** — a form a person fills
  in, not a model-built payload. `required` is enforced before your function
  runs, as `-32602`.
- Resource templates: `{placeholder}` names must equal the function/param names
  (Python raises at import time on a mismatch). A template function runs on
  *read*, not on list.
- Server-to-client change notifications go through `subscriptions/listen`, one
  long-lived POST stream, opted in per type (`toolsListChanged`,
  `promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`).
  Request-scoped notifications (`notifications/progress`,
  `notifications/message`) travel on the response stream of the request they
  relate to — never on the listen stream.

---

## 9. Version negotiation and dual-era servers

- Modern = `2026-07-28` and later (per-request metadata).
- Legacy = `2025-11-25` and earlier (`initialize` handshake).
- Dual-era = supports both. One factory, one endpoint, two protocol paths.

Unknown/unsupported version → `-32022 UnsupportedProtocolVersionError` with the
supported list. Clients pick from it and retry.

Stdio probe: a modern client sends `server/discover`; a recognized modern error
means "modern server, retry with a supported version"; any other error/timeout
means "legacy server, fall back to `initialize`".

Streamable HTTP probe: attempt a modern request and inspect a `400` body before
falling back. Both official SDKs implement the classification; both expose a
`legacy: 'stateless' | 'reject'` (TS) / dual-era automatic behaviour (Python)
switch. Serving 2025-era clients statelessly costs the back-channel and SSE
resumability; legacy clients that need those require sticky sessions.

---

## 10. Authorization posture

Your server is an OAuth 2.1 **resource server**: it verifies tokens, it never
issues them.

- Publish RFC 9728 Protected Resource Metadata at
  `/.well-known/oauth-protected-resource/<path>` (the SDK does this from your
  `AuthSettings`).
- Unauthenticated request → `401` with `WWW-Authenticate: Bearer
  error="invalid_token", ..., resource_metadata="<metadata url>"`. That pointer
  is what makes discovery automatic.
- Validate `iss` (RFC 9207) if present; keep credentials bound to their issuer.
- Client ID Metadata Documents (CIMD) are the forward path; Dynamic Client
  Registration is deprecated.
- Stdio has no `Authorization` header: the security boundary is the process that
  launched the server.

---

## 11. Deprecated — do not adopt

| Feature | Migrate to |
|---|---|
| Roots | tool parameters, resource URIs, server config |
| Sampling | call your LLM provider directly |
| Logging (`logging/setLevel`, `notifications/message` broadcast) | stderr (stdio), OpenTelemetry |
| HTTP+SSE transport (`2025-03-26`) | Streamable HTTP |
| Dynamic Client Registration | CIMD |
| `includeContext: "thisServer" / "allServers"` | omit or `"none"` |

Deprecated features keep working for at least twelve months under the formal
lifecycle policy. New implementations should not add them.

---

## 12. Extensions

Optional capabilities are advertised in `capabilities.extensions`, a map from
extension id (reverse-DNS, mandatory prefix) to a settings object:

```json
{ "capabilities": { "tools": {}, "extensions": { "io.modelcontextprotocol/tasks": {} } } }
```

Known extensions: `io.modelcontextprotocol/tasks` (poll-based `tasks/get` +
`tasks/update`, long-running work), `io.modelcontextprotocol/ui` (MCP Apps,
inline UI in the host), Enterprise Managed Authorization. If one side supports
an extension and the other does not, the supporting side **MUST** revert to core
behaviour or reject with a clear error.
