#!/usr/bin/env python3
"""Support-tickets MCP server — Python 3.11+ / MCP spec 2026-07-28 scaffold.

Copy this file, rename the domain objects, and replace the in-memory STORE with
your real backend. Everything here is verified against `mcp` 2.3.0 (SDK v2).

Install:
    uv add "mcp[cli]"            # or: pip install "mcp[cli]"

Run:
    mcp dev server.py                          # Inspector over stdio
    python server.py                           # stdio (a host launches it)
    MCP_TRANSPORT=streamable-http python server.py   # http://127.0.0.1:8000/mcp
    uvicorn server:app --workers 4             # production, behind a proxy

Design notes that matter more than the code:
  * The protocol is stateless. There is no session object, no initialize
    handshake, no Mcp-Session-Id. Any request may land on any worker.
  * Cross-call state is an explicit handle the model passes back as an
    argument (see `list_tickets_page`), never hidden transport state.
  * A destructive tool asks for confirmation by RETURNING an
    InputRequiredResult (MRTR), not by calling back into the client.
"""

import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from starlette.applications import Starlette

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.server.caching import CacheHint
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitResult,
    InputRequiredResult,
    ToolAnnotations,
)

SERVER_NAME = "support-tickets"
SERVER_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Domain layer — replace with your database client.
# --------------------------------------------------------------------------


class Ticket(BaseModel):
    """A support ticket as the model sees it."""

    id: str
    subject: str
    status: Literal["open", "pending", "closed"] = "open"
    priority: Literal["low", "normal", "high"] = "normal"
    body: str = ""


@dataclass
class Store:
    tickets: dict[str, Ticket] = field(default_factory=dict)
    idempotency: dict[str, str] = field(default_factory=dict)

    def seed(self) -> None:
        self.tickets["T-1001"] = Ticket(
            id="T-1001", subject="Export fails on CSV", priority="high",
            body="Export button returns HTTP 500 for accounts with >10k rows.",
        )
        self.tickets["T-1002"] = Ticket(
            id="T-1002", subject="Add SSO for Okta", status="pending",
            body="Customer asks for Okta SAML support on the business plan.",
        )
        self.tickets["T-1003"] = Ticket(
            id="T-1003", subject="Typo in invoice email", status="closed",
            body="'Reciept' should be 'Receipt'.",
        )


STORE = Store()
STORE.seed()


# --------------------------------------------------------------------------
# Server
# --------------------------------------------------------------------------

_AUTH_KWARGS: dict = {}
if os.environ.get("MCP_AUTH_ISSUER"):  # pragma: no cover - deployment path
    from pydantic import AnyHttpUrl

    from mcp.server.auth.provider import AccessToken, TokenVerifier
    from mcp.server.auth.settings import AuthSettings

    class EnvTokenVerifier(TokenVerifier):
        """Swap for JWT signature verification or RFC 7662 introspection."""

        async def verify_token(self, token: str) -> AccessToken | None:
            import json

            table = json.loads(os.environ.get("MCP_TOKENS_JSON", "{}"))
            entry = table.get(token)
            if entry is None:
                return None
            return AccessToken(
                token=token,
                client_id=entry["client_id"],
                scopes=entry.get("scopes", []),
                resource=os.environ["MCP_RESOURCE_URL"],
            )

    # token_verifier and auth always travel together; one without the other
    # raises ValueError before the server ever serves a request.
    _AUTH_KWARGS = {
        "token_verifier": EnvTokenVerifier(),
        "auth": AuthSettings(
            issuer_url=AnyHttpUrl(os.environ["MCP_AUTH_ISSUER"]),
            resource_server_url=AnyHttpUrl(os.environ["MCP_RESOURCE_URL"]),
            required_scopes=["tickets:read"],
            validate_token_resource=True,
        ),
    }

# Auth is wired into the SAME server object: building a second MCPServer later
# would silently drop every tool registered before it.
mcp = MCPServer(
    SERVER_NAME,
    title="Support Tickets",
    version=SERVER_VERSION,
    instructions=(
        "Search and triage support tickets. Read `config://limits` before "
        "bulk operations. Closing a ticket asks for confirmation first."
    ),
    # ttlMs / cacheScope are REQUIRED on list, read and discover results. The
    # default is ttl_ms=0, scope="private" — compliant but useless. Use
    # "public" only when the response is byte-identical for every caller;
    # a per-tenant tool list cached public leaks one tenant's list to another.
    cache_hints={
        "tools/list": CacheHint(ttl_ms=60_000, scope="public"),
        "server/discover": CacheHint(ttl_ms=300_000, scope="public"),
        "resources/list": CacheHint(ttl_ms=30_000, scope="private"),
    },
    **_AUTH_KWARGS,
)


# --- Tools: the model decides to call these -------------------------------


@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
def search_tickets(
    query: Annotated[str, Field(description="Words to match in subject or body.")],
    status: Literal["open", "pending", "closed"] | None = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Max results.")] = 10,
) -> list[Ticket]:
    """Search support tickets by keyword, optionally filtered by status."""
    q = query.lower()
    hits = [
        t
        for t in STORE.tickets.values()
        if (q in t.subject.lower() or q in t.body.lower())
        and (status is None or t.status == status)
    ]
    return hits[:limit]


@mcp.tool()
def create_ticket(
    subject: Annotated[str, Field(min_length=3, max_length=200)],
    body: str,
    priority: Literal["low", "normal", "high"] = "normal",
    idempotency_key: Annotated[
        str | None,
        Field(description="Reuse the same key to make retries safe."),
    ] = None,
) -> Ticket:
    """Create a support ticket. Retries with the same idempotency_key are safe."""
    if idempotency_key and idempotency_key in STORE.idempotency:
        return STORE.tickets[STORE.idempotency[idempotency_key]]
    if "spam" in subject.lower():
        # A ToolError is a turn in the conversation: the model reads it and
        # can fix its own call. Raise it; never return an error string.
        raise ToolError("Refusing to create a ticket whose subject contains 'spam'.")
    ticket = Ticket(
        id=f"T-{uuid.uuid4().hex[:6].upper()}", subject=subject, body=body,
        priority=priority,
    )
    STORE.tickets[ticket.id] = ticket
    if idempotency_key:
        STORE.idempotency[idempotency_key] = ticket.id
    return ticket


CONFIRM_CLOSE = ElicitRequest(
    params=ElicitRequestFormParams(
        message="Closing a ticket is not reversible. Confirm?",
        requested_schema={
            "type": "object",
            "properties": {"ok": {"type": "boolean", "description": "true closes it"}},
            "required": ["ok"],
        },
    )
)


@mcp.tool(annotations=ToolAnnotations(destructive_hint=True, idempotent_hint=True))
async def close_ticket(
    ticket_id: str,
    ctx: Context,
) -> str | InputRequiredResult:
    """Close a ticket. Asks the human for confirmation before acting."""
    ticket = STORE.tickets.get(ticket_id)
    if ticket is None:
        raise ToolError(f"No ticket {ticket_id!r}. Search first to get a valid id.")

    if ctx.input_responses is None:
        # Round 1: return the question instead of calling back into the client.
        # `request_state` is sealed by the SDK and echoed on the retry.
        return InputRequiredResult(
            input_requests={"confirm": CONFIRM_CLOSE},
            request_state=f"close:{ticket_id}",
        )

    answer = ctx.input_responses.get("confirm")
    if not isinstance(answer, ElicitResult) or answer.action != "accept":
        return f"Ticket {ticket_id} left open (confirmation declined)."
    if not (answer.content or {}).get("ok"):
        return f"Ticket {ticket_id} left open (confirmation declined)."

    ticket.status = "closed"
    return f"Ticket {ticket_id} closed."


# --- Resources: the application decides to read these ---------------------


@mcp.resource("config://limits", mime_type="application/json")
def limits() -> dict[str, int]:
    """Operational limits for this server."""
    return {"max_page_size": 50, "max_bulk_close": 20}


@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> Ticket:
    """One ticket by id. Template: the function runs on read, not on list."""
    ticket = STORE.tickets.get(ticket_id)
    if ticket is None:
        # Missing resource is -32602 in this revision (was -32002).
        raise ResourceNotFoundError(f"No ticket {ticket_id!r}.")
    return ticket


# --- Prompts: a human picks these from a menu -----------------------------


@mcp.prompt(title="Triage a ticket")
def triage(ticket_id: str) -> str:
    """Draft a triage note for one ticket."""
    ticket = STORE.tickets.get(ticket_id)
    if ticket is None:
        raise ValueError(f"No ticket {ticket_id!r}.")
    return (
        f"Triage support ticket {ticket.id}: {ticket.subject!r} "
        f"(priority={ticket.priority}, status={ticket.status}).\n\n"
        f"{ticket.body}\n\n"
        "Give: severity, likely owner, next action, and a customer-facing reply."
    )


# --------------------------------------------------------------------------
# Authorization helper — Streamable HTTP only (stdio has no Authorization
# header, so a stdio server's boundary is the process that launched it).
# --------------------------------------------------------------------------

if os.environ.get("MCP_AUTH_ISSUER"):  # pragma: no cover - deployment path
    from mcp.server.auth.middleware.auth_context import get_access_token

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
    def whoami() -> str:
        """Report the calling client and its scopes."""
        token = get_access_token()
        return "anonymous" if token is None else f"{token.client_id} {token.scopes}"


# --------------------------------------------------------------------------
# Transport / entrypoint
# --------------------------------------------------------------------------


def build_http_app() -> Starlette:
    """ASGI app for deployment. `transport_security` is not optional in prod:
    the default allowlist is localhost only and answers 421 to everything else."""
    from mcp.server.transport_security import TransportSecuritySettings

    hosts = [h for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h]
    origins = [o for o in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",") if o]
    security = (
        TransportSecuritySettings(
            allowed_hosts=[f"{h}:*" for h in hosts] + hosts,
            allowed_origins=origins,
        )
        if hosts
        else None
    )
    return mcp.streamable_http_app(transport_security=security)


app = build_http_app()


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        # Transport options belong on run(), never on MCPServer(...).
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "8000")),
        )
    else:
        mcp.run()  # stdio: stdout is the wire, so log to stderr only


if __name__ == "__main__":
    main()
