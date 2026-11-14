# Transport guide — stdio vs Streamable HTTP, and getting it deployed

Pick the transport before you write the server: it decides who owns the process,
where auth lives, and how you scale. The protocol is identical either way.

---

## 1. Decision table

| | **stdio** | **Streamable HTTP** | SSE (legacy) |
|---|---|---|---|
| Who launches it | the host, as a child process | you deploy it, clients connect | — |
| Who can use it | one local user / one host | many clients, many tenants | — |
| Auth | process boundary only — no `Authorization` header | OAuth 2.1 bearer tokens, per request | — |
| Scaling | N/A (one process per session) | any instance, round-robin, no sticky sessions | — |
| Cold start / serverless | no | yes — stateless by construction | no |
| Debugging | Inspector spawns it for you | Inspector connects by URL | — |
| Status in `2026-07-28` | supported, recommended for local tools | supported, recommended for anything deployed | **deprecated** |

Rules of thumb:

- **Local developer tool, filesystem, git, shell, local DB** → stdio.
- **Anything a browser, another machine, or more than one user touches** →
  Streamable HTTP.
- **SSE** → only if a client you cannot change still speaks it. Never build new.

---

## 2. stdio

The host spawns `python server.py` / `node dist/index.js`, writes JSON-RPC to
stdin, reads responses from stdout.

Hard constraints:

- **stdout is the wire.** One `print()` / `console.log()` corrupts the stream.
  Log to stderr: Python `logging` (its handler flushes to stderr), TS
  `console.error`.
- The process must stay alive waiting on stdin; `run()` blocks.
- Keep `run()` under `if __name__ == "__main__":` (Python) — everything that
  loads your file (`mcp dev`, `mcp run`, tests) imports it.

Host config is the same command in every host's own file:

```jsonc
// Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json
// VS Code:        .vscode/mcp.json          Cursor: ~/.cursor/mcp.json
{
  "mcpServers": {
    "support-tickets": {
      "command": "uv",
      "args": ["run", "--directory", "/abs/path", "python", "server.py"],
      "env": { "TICKETS_API_KEY": "${env:TICKETS_API_KEY}" }
    }
  }
}
```

The host's environment is not your shell's. Anything the server needs must be in
that `env` block (Python: `mcp install server.py -v KEY=VALUE -f .env` writes it
for Claude Desktop).

---

## 3. Streamable HTTP

One endpoint, POST only, one JSON-RPC message per request.

```
POST /mcp
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: search_tickets
```

- Response is either `application/json` (one object) or
  `text/event-stream` (request-scoped notifications then the final result).
- Notifications get `202 Accepted` with no body.
- Closing the response stream **is** cancellation. There is no
  `notifications/cancelled` on HTTP and no `Last-Event-ID` resume.
- Change notifications: `subscriptions/listen`, one long-lived stream, opted in
  per notification type.

SDK entry points:

```python
# Python — options go on run(), never on MCPServer(...)
mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
app = mcp.streamable_http_app(transport_security=security)   # uvicorn target
```

```ts
// TypeScript — factory + web-standard handler
const handler = createMcpHandler(createServer, { legacy: 'stateless' });
// Workers/Deno/Bun: export default handler
// Node/Express: toNodeHandler(handler) behind createMcpExpressApp()
```

The TS handler runs the factory **once per request** — a fresh `McpServer` per
call. Keep the factory cheap and side-effect free; open pools and caches at
module scope and close over them.

---

## 4. Deployment checklist

### 4.1 The Host allowlist (`421` — the #1 deploy failure)

Both SDKs default to a localhost-only `Host`/`Origin` allowlist (DNS-rebinding
protection). Deployed behind a real hostname, **every** request is rejected:

```
HTTP/1.1 421 Misdirected Request
Invalid Host header — the host is not in the allowlist
```

It is a plain-text HTTP response, not JSON-RPC, so the client only reports a
generic transport error. If a freshly deployed server refuses everything, this is
why.

```python
from mcp.server.transport_security import TransportSecuritySettings
security = TransportSecuritySettings(
    allowed_hosts=["mcp.example.com", "mcp.example.com:*"],   # exact values
    allowed_origins=["https://app.example.com"],
)
app = mcp.streamable_http_app(transport_security=security)
```

```ts
const app = createMcpExpressApp({ host: '0.0.0.0', allowedHosts: ['api.example.com'] });
```

Behind a proxy that already controls `Host`, `enable_dns_rebinding_protection=False`
is the honest configuration. Passing a non-localhost `host=` does **not**
allowlist it.

### 4.2 TLS terminates at a proxy

Tell uvicorn to trust forwarded headers, or an `/mcp` → `/mcp/` redirect points
at `http://` and clients refuse the downgrade:

```bash
uvicorn server:app --proxy-headers --forwarded-allow-ips='*'
```

### 4.3 Multiple workers: `requestState` must be openable by any worker

Modern requests need no affinity — that is the point of the revision. But MRTR
round 1 and round 2 are two independent HTTP requests, and the retry may hit a
different worker. Each worker seals `requestState` with its own random key by
default, so the retry fails:

```json
{ "code": -32602, "message": "Invalid or expired requestState",
  "data": { "reason": "invalid_request_state" } }
```

Symptom: a confirm-before-acting tool works on one worker and fails *some of the
time* on four. Fix: configure a shared key.

```python
mcp = MCPServer("billing", request_state_security=RequestStateSecurity(key=SHARED_KEY))
```

Either way, keep `requestState` small and self-contained (an id plus what you
need), never a server-memory pointer.

### 4.4 Scaling shape per protocol era

| Client speaks | Session | Load balancer |
|---|---|---|
| `2026-07-28` | none, ever | nothing — any worker serves any request |
| `2025-11-25` or earlier | `Mcp-Session-Id` in one worker's memory | **sticky sessions** |
| legacy + `stateless_http=True` | none | nothing (loses back-channel + resumability) |

`stateless_http=True` only affects the legacy path; the modern path is
sessionless by construction.

### 4.5 Change-notification fan-out

`subscriptions/listen` streams live in one process. With more than one replica, a
list change on worker A never reaches a listener on worker B unless you put a bus
between them (Redis pub/sub, NATS). Streams are not resumable and events are not
replayed: losing a replica means clients re-listen and re-fetch. No notifications
to send? Turn the bus off — it is opt-in.

---

## 5. Auth at the edge, rate limits, and observability

- This revision exists partly so gateways can work **without parsing bodies**:
  route and meter on `Mcp-Method` / `Mcp-Name`. `Mcp-Param-{Name}` (from
  `x-mcp-header`) lets an edge proxy meter per tenant or per region.
- Rate limit per `(client_id, tool_name)`, not per connection. There are no
  connections to count.
- Answer 429 with `Retry-After`; the model retries, and a `ToolError` saying
  "rate limited, retry in 5s" is often better than a transport failure.
- Verify the bearer token in front of the handler (Express:
  `requireBearerAuth`; Python: `TokenVerifier` + `AuthSettings`), then read the
  result inside handlers (`ctx.http.authInfo`, `get_access_token()`).
- Trace: propagate `traceparent`/`tracestate`/`baggage` in `_meta`; emit spans
  per `tools/call` keyed by `Mcp-Name`. Server identity is stamped into every
  result's `_meta` for correlation.
- Log to stderr (stdio) or to your log pipeline (HTTP). Never `notifications/message`
  unless the request asked for a log level.

---

## 6. Testing before you deploy

```bash
# Local, both languages, launches the server over stdio
uv run mcp dev server.py
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

Inspector gives you a real tools/resources/prompts UI with forms built from your
schema. Use it to check the *schema*, not just the happy path: call with a
missing required argument and with an out-of-range value, and confirm the model
would see a readable error.

Then test in-process, no transport:

```python
# Python — same Client that talks to a URL, pointed at the object
async with Client(mcp, elicitation_callback=cb, raise_exceptions=True) as c:
    r = await c.call_tool("close_ticket", {"ticket_id": "T-1"})
```

```ts
// TypeScript — route a Request straight into the handler
const res = await handler.fetch(new Request('http://localhost/mcp', { method: 'POST', ... }));
```

Smoke-test the deployed endpoint by hand — headers included, because a missing
`Mcp-Method` is a protocol error, not a warning:

```bash
curl -s -X POST https://mcp.example.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":1,"method":"server/discover",
       "params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",
                          "io.modelcontextprotocol/clientCapabilities":{}}}}'
```

A healthy response contains `resultType`, `supportedVersions`, `capabilities`,
`ttlMs`, `cacheScope`, and `_meta["io.modelcontextprotocol/serverInfo"]`.

---

## 7. Packaging and the Registry

Ship a package, then publish metadata.

```bash
# Python
uv build && uv publish                  # PyPI: pipx run my-mcp

# TypeScript
npm publish --access public             # npx -y my-mcp
```

Container (both): expose the HTTP transport, listen on `0.0.0.0` inside the
container, terminate TLS in front, and pass `MCP_ALLOWED_HOSTS` through.

The official MCP Registry (<https://registry.modelcontextprotocol.io>, preview)
hosts **metadata only** — it points at npm/PyPI/OCI packages or at a public
remote URL. Private networks and private registries are out of scope; self-host
a private registry for those.

`server.json` essentials:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/draft/server.schema.json",
  "name": "io.github.<owner>/support-tickets",
  "description": "Search, create and triage support tickets.",
  "version": "1.0.0",
  "packages": [
    { "registryType": "pypi", "identifier": "support-tickets-mcp", "version": "1.0.0",
      "transport": { "type": "stdio" } }
  ]
}
```

Names are reverse-DNS and namespace-verified (GitHub account or domain
challenge), so `io.github.you/...` only works if you own that account. Bump the
version, republish, and keep `description` honest — aggregators surface it
verbatim.

---

## 8. Transport decision, in one line each

- Local, single user, filesystem or shell access → **stdio**.
- Multi-user, remote, serverless, or behind a gateway → **Streamable HTTP**.
- Need browser reachability from web apps → Streamable HTTP plus the `Origin`
  allowlist and CORS.
- Still serving pre-2026 hosts → dual-era from **one** factory; do not fork the
  server definition.
- SSE → only for a client you cannot replace.
