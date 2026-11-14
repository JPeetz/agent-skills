/**
 * Support-tickets MCP server — TypeScript scaffold for MCP spec 2026-07-28.
 *
 * Verified against @modelcontextprotocol/server 2.4.0 (SDK v2).
 *
 * Install:
 *   npm pkg set type=module
 *   npm install @modelcontextprotocol/server @modelcontextprotocol/node zod
 *   npm install -D typescript tsx @types/node
 *
 * Run:
 *   npx tsx src/index.ts                        # stdio (a host launches it)
 *   MCP_TRANSPORT=http npx tsx src/index.ts     # http://127.0.0.1:8000/mcp
 *   npx @modelcontextprotocol/inspector npx tsx src/index.ts
 *
 * Three rules this file exists to demonstrate:
 *   1. One factory, `createServer()`. The HTTP handler calls it per request,
 *      so no state survives on the instance and any worker can serve any call.
 *   2. Cross-call state is an explicit handle the model passes back
 *      (`pageToken`), never hidden server-side session state.
 *   3. A destructive tool asks for confirmation by RETURNING `inputRequired`,
 *      not by calling back into the client.
 */

import { McpServer, ResourceTemplate, createMcpHandler, inputRequired, acceptedContent } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { createServer as createHttpServer } from 'node:http';
import { randomUUID } from 'node:crypto';
import * as z from 'zod/v4';

// ---------------------------------------------------------------------------
// Domain layer — replace with your database client. Module scope, so it is
// created once per process, not once per request.
// ---------------------------------------------------------------------------

type Ticket = {
  id: string;
  subject: string;
  body: string;
  status: 'open' | 'pending' | 'closed';
  priority: 'low' | 'normal' | 'high';
};

const tickets = new Map<string, Ticket>();
const idempotency = new Map<string, string>();

for (const t of [
  { id: 'T-1001', subject: 'Export fails on CSV', body: 'HTTP 500 for accounts with >10k rows.', status: 'open', priority: 'high' },
  { id: 'T-1002', subject: 'Add SSO for Okta', body: 'Customer asks for Okta SAML support.', status: 'pending', priority: 'normal' },
  { id: 'T-1003', subject: 'Typo in invoice email', body: "'Reciept' should be 'Receipt'.", status: 'closed', priority: 'low' }
] as Ticket[]) {
  tickets.set(t.id, { ...t });
}

// ---------------------------------------------------------------------------
// The factory. Register EVERYTHING in here.
// ---------------------------------------------------------------------------

export function createServer(): McpServer {
  const server = new McpServer(
    { name: 'support-tickets', version: '1.0.0', title: 'Support Tickets' },
    {
      instructions:
        'Search and triage support tickets. Read the config://limits resource before bulk ' +
        'operations. Closing a ticket asks for human confirmation first.',
      // ttlMs / cacheScope are required on list, read and discover results.
      // Default is ttlMs 0 / 'private' — compliant but useless. Use 'public'
      // ONLY when the payload is identical for every caller: a per-tenant tool
      // list cached 'public' leaks one tenant's tools to another.
      cacheHints: {
        'tools/list': { ttlMs: 60_000, cacheScope: 'public' },
        'server/discover': { ttlMs: 300_000, cacheScope: 'public' },
        'resources/list': { ttlMs: 30_000, cacheScope: 'private' }
      }
    }
  );

  // --- Tools: the model decides to call these ------------------------------

  server.registerTool(
    'search_tickets',
    {
      title: 'Search tickets',
      description: 'Search support tickets by keyword, optionally filtered by status.',
      annotations: { readOnlyHint: true },
      inputSchema: z.object({
        query: z.string().min(1).describe('Words to match in the subject or body'),
        status: z.enum(['open', 'pending', 'closed']).optional().describe('Only this status'),
        limit: z.number().int().min(1).max(50).default(10).describe('Maximum results')
      })
    },
    async ({ query, status, limit }) => {
      const q = query.toLowerCase();
      const hits = [...tickets.values()]
        .filter(t => (t.subject.toLowerCase().includes(q) || t.body.toLowerCase().includes(q)) && (!status || t.status === status))
        .slice(0, limit);
      return {
        content: [{ type: 'text', text: JSON.stringify(hits, null, 2) }],
        structuredContent: { result: hits }
      };
    }
  );

  server.registerTool(
    'create_ticket',
    {
      title: 'Create ticket',
      description: 'Create a support ticket. Retries with the same idempotencyKey are safe.',
      inputSchema: z.object({
        subject: z.string().min(3).max(200),
        body: z.string().describe('What the customer reported'),
        priority: z.enum(['low', 'normal', 'high']).default('normal'),
        idempotencyKey: z.string().optional().describe('Reuse the same key to make retries safe')
      })
    },
    async ({ subject, body, priority, idempotencyKey }) => {
      if (idempotencyKey) {
        const existing = idempotency.get(idempotencyKey);
        if (existing) {
          return { content: [{ type: 'text', text: JSON.stringify(tickets.get(existing)) }] };
        }
      }
      if (subject.toLowerCase().includes('spam')) {
        // isError: true is a turn in the conversation — the model reads it and
        // can fix its own call. Do not return a string that looks like success.
        return { content: [{ type: 'text', text: 'Refusing to create a ticket whose subject contains "spam".' }], isError: true };
      }
      const ticket: Ticket = { id: `T-${randomUUID().slice(0, 6).toUpperCase()}`, subject, body, status: 'open', priority };
      tickets.set(ticket.id, ticket);
      if (idempotencyKey) idempotency.set(idempotencyKey, ticket.id);
      return { content: [{ type: 'text', text: JSON.stringify(ticket) }] };
    }
  );

  server.registerTool(
    'close_ticket',
    {
      title: 'Close ticket',
      description: 'Close a ticket. Asks the human for confirmation before acting.',
      annotations: { destructiveHint: true, idempotentHint: true },
      inputSchema: z.object({ ticketId: z.string().describe('Ticket id, e.g. T-1001') })
    },
    async ({ ticketId }, ctx) => {
      const ticket = tickets.get(ticketId);
      if (!ticket) {
        return { content: [{ type: 'text', text: `No ticket ${ticketId}. Search first to get a valid id.` }], isError: true };
      }

      // Multi Round-Trip Requests: return the question, let the client retry
      // the same call with the answers attached. The server never calls back.
      const confirmed = acceptedContent(ctx.mcpReq.inputResponses, 'confirm');
      if (confirmed === undefined) {
        return inputRequired({
          inputRequests: {
            confirm: {
              method: 'elicitation/create',
              params: {
                message: `Closing ${ticketId} is not reversible. Confirm?`,
                requestedSchema: {
                  type: 'object',
                  properties: { ok: { type: 'boolean', description: 'true closes it' } },
                  required: ['ok']
                }
              }
            }
          },
          // Opaque to the client, echoed verbatim on the retry. Keep it small
          // and self-contained: another worker must be able to open it.
          requestState: `close:${ticketId}`
        });
      }
      if (!(confirmed as { ok?: boolean }).ok) {
        return { content: [{ type: 'text', text: `Ticket ${ticketId} left open (confirmation declined).` }] };
      }
      ticket.status = 'closed';
      return { content: [{ type: 'text', text: `Ticket ${ticketId} closed.` }] };
    }
  );

  // --- Resources: the application decides to read these --------------------

  server.registerResource(
    'limits',
    'config://limits',
    { title: 'Operational limits', description: 'Page sizes and bulk-operation caps', mimeType: 'application/json' },
    async uri => ({
      contents: [{ uri: uri.href, mimeType: 'application/json', text: JSON.stringify({ maxPageSize: 50, maxBulkClose: 20 }) }]
    })
  );

  server.registerResource(
    'ticket',
    new ResourceTemplate('tickets://{ticketId}', { list: undefined }),
    { title: 'Ticket', description: 'One ticket by id', mimeType: 'application/json' },
    async (uri, { ticketId }) => {
      const ticket = tickets.get(String(ticketId));
      // A missing resource is -32602 in this revision (it was -32002 before).
      if (!ticket) throw new Error(`No ticket ${String(ticketId)}`);
      return { contents: [{ uri: uri.href, mimeType: 'application/json', text: JSON.stringify(ticket) }] };
    }
  );

  // --- Prompts: a human picks these from a menu ----------------------------

  server.registerPrompt(
    'triage',
    { title: 'Triage a ticket', argsSchema: z.object({ ticketId: z.string().describe('Ticket id') }) },
    ({ ticketId }) => {
      const ticket = tickets.get(ticketId);
      if (!ticket) throw new Error(`No ticket ${ticketId}`);
      return {
        messages: [
          {
            role: 'user',
            content: {
              type: 'text',
              text:
                `Triage support ticket ${ticket.id}: ${ticket.subject} ` +
                `(priority=${ticket.priority}, status=${ticket.status}).\n\n${ticket.body}\n\n` +
                'Give: severity, likely owner, next action, and a customer-facing reply.'
            }
          }
        ]
      };
    }
  );

  return server;
}

// ---------------------------------------------------------------------------
// Transports
// ---------------------------------------------------------------------------

/** Web-standard handler: `export default handler` on Workers/Deno/Bun. */
export const handler = createMcpHandler(createServer, {
  // Serve 2025-era clients statelessly too, so old hosts keep working from the
  // same factory. Use 'reject' in CI to prove you are 2026-only.
  legacy: 'stateless',
  onerror: error => console.error('[mcp] handler error:', error)
});

if (process.env.MCP_TRANSPORT === 'http') {
  // toNodeHandler adapts the web handler once; `handler.fetch` stays the same.
  const node = toNodeHandler(handler);
  createHttpServer((req, res) => void node(req, res))
    // Bind loopback by default. Deploying behind a hostname? Name the hosts
    // explicitly and enforce them in front of the handler (createMcpExpressApp
    // does this for you; on plain node:http compose the *_Validation guards).
    .listen(Number(process.env.MCP_PORT ?? 8000), process.env.MCP_HOST ?? '127.0.0.1');
  console.error(`support-tickets MCP server on http://${process.env.MCP_HOST ?? '127.0.0.1'}:${process.env.MCP_PORT ?? 8000}/mcp`);
} else {
  // stdio: stdout is the wire. Every log line must go to stderr.
  void serveStdio(createServer);
  console.error('support-tickets MCP server running on stdio');
}
