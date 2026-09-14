---
name: "nodejs-development"
description: "Use when building, debugging, or optimizing Node.js applications — Fastify servers, TypeScript with type stripping, Node.js core internals, OAuth 2.0/2.1 auth flows, advanced TypeScript types, or diagnosing performance/crash issues. Covers the full Node.js stack from framework patterns (Fastify plugins, routes, schemas, hooks) through internals (V8, libuv, N-API, C++ addons) to production concerns (graceful shutdown, caching, streams, testing, error handling)."
version: "1.0.0"
author: "JPeetz (adapted from Matteo Collina's skills: mcollina/skills)"
license: "MIT"
metadata:
  hermes:
    tags:
      - nodejs
      - fastify
      - typescript
      - backend
      - api
      - server
      - type-stripping
      - streams
      - caching
      - v8
      - libuv
      - n-api
      - oauth
      - testing
      - performance
      - async
    related_skills:
      - api-design-first
      - graphql-api-development
      - github-code-review
      - test-driven-development
      - codebase-inspection
      - systematic-debugging
---

# Node.js Development — Meta-Skill

A comprehensive collection of Node.js development patterns distilled from Matteo Collina's (Fastify creator, Node.js core contributor) personal skills. Covers **Fastify** application architecture, **Node.js** best practices (type stripping, streams, caching, error handling, testing), **Node.js core internals** (V8, libuv, N-API, C++ addons), **OAuth 2.0/2.1** authorization flows, and **advanced TypeScript** type patterns.

> **Source:** Adapted from [mcollina/skills](https://github.com/mcollina/skills) — 11 skills by Matteo Collina.

---

## Table of Contents

1. [When to Use](#when-to-use)
2. [Section A: Node.js Best Practices](#section-a-nodejs-best-practices)
3. [Section B: Fastify Application Architecture](#section-b-fastify-application-architecture)
4. [Section C: Node.js Core Internals](#section-c-nodejs-core-internals)
5. [Section D: OAuth 2.0/2.1 with Fastify](#section-d-oauth-2021-with-fastify)
6. [Section E: Advanced TypeScript Types](#section-e-advanced-typescript-types)
7. [Pitfalls](#pitfalls)
8. [Verification](#verification)

---

## When to Use

Trigger this skill when any of these appear in the prompt:

| Signal | Relevant Section |
|--------|-----------------|
| "Fastify", "Fastify plugin", "Fastify routes", "Fastify hooks" | B |
| "Node 22", "type stripping", "strip types", "native TypeScript", ".ts without build" | A |
| "streams", "pipeline", "CSV/ETL", "backpressure", "large file processing" | A |
| "graceful shutdown", "close-with-grace", "SIGTERM", "SIGINT" | A |
| "flaky tests", "node --test", "test timeout", "process did not exit" | A |
| "V8", "libuv", "event loop", "node-gyp", "N-API", "NAN", "C++ addon", "segfault" | C |
| "OAuth", "authorization code", "PKCE", "refresh token rotation", "JWT validation" | D |
| "conditional types", "infer", "mapped types", "branded types", "opaque types" | E |
| "any type", "remove any", "strict TypeScript" | E |
| "tsc --noEmit", "type error", "compiler error" | E |

**General Node.js development** (error handling, logging, performance, profiling, environment config) uses Section A.

---

## Section A: Node.js Best Practices

### A1. TypeScript with Type Stripping (Node 22.6+)

Use **type stripping** instead of build tools (ts-node, tsx). Node runs `.ts` files directly by removing type annotations without transpilation.

**Requirements:**
- Use `import type` for type-only imports
- Use const objects instead of `enum`
- Avoid `namespace` and parameter properties
- Use `.ts` extensions in import paths

```ts
// greet.ts — valid type-stripped file
import type { IncomingMessage } from 'node:http';

const greet = (name: string): string => `Hello, ${name}!`;
console.log(greet('world'));
```

```bash
node greet.ts   # runs directly, no build step
```

**tsconfig.json for type stripping:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noEmit": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true
  }
}
```

### A2. Error Handling

Use `@fastify/create-error` for typed, code-bearing errors:

```ts
import createError from '@fastify/create-error';

const NotFoundError = createError('NOT_FOUND', '%s not found', 404);
const ValidationError = createError('VALIDATION_ERROR', '%s', 400);

throw new NotFoundError('User');          // → 404, code: NOT_FOUND
throw new ValidationError('Email required');  // → 400, code: VALIDATION_ERROR
```

**Minimal zero-dependency pattern:**
```ts
interface AppErrorOptions { code: string; statusCode?: number; cause?: Error; }

function createAppError(message: string, opts: AppErrorOptions): Error {
  const err = new Error(message, { cause: opts.cause });
  (err as any).code = opts.code;
  (err as any).statusCode = opts.statusCode ?? 500;
  Error.captureStackTrace(err, createAppError);
  return err;
}

function notFound(resource: string) {
  return createAppError(`${resource} not found`, { code: 'NOT_FOUND', statusCode: 404 });
}
```

**Operational vs programmer errors:** Classify errors at the boundary. Operational errors (failed network call, file not found) should be handled gracefully. Programmer errors (TypeError, ReferenceError) should crash or restart.

**Global async error handlers:**
```ts
process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Rejection:', reason);
  // Log and crash hard — these are programmer errors
  process.exitCode = 1;
});

process.on('uncaughtException', (err, origin) => {
  console.error('Uncaught Exception:', err, origin);
  // Perform emergency cleanup, then exit
  process.exit(1);
});
```

### A3. Streams

**Always use `pipeline()` from `node:stream/promises`** — never bare `.pipe()`:

```ts
import { pipeline } from 'node:stream/promises';
import { createReadStream, createWriteStream } from 'node:fs';
import { createGzip } from 'node:zlib';

await pipeline(
  createReadStream('input.csv'),
  createGzip(),
  createWriteStream('output.csv.gz')
);
```

**Async generator transforms** (preferred over `Transform` class):

```ts
async function* toUpperCase(source: AsyncIterable<Buffer>): AsyncGenerator<string> {
  for await (const chunk of source) {
    yield chunk.toString().toUpperCase();
  }
}

await pipeline(createReadStream(input), toUpperCase, createWriteStream(output));
```

**CSV/ETL pattern** — pipeline + async transform + deduplicated enrichment:
```ts
import { pipeline } from 'node:stream/promises';
import { createReadStream, createWriteStream } from 'node:fs';
import { createCache } from 'async-cache-dedupe';

const cache = createCache({ ttl: 60, stale: 5, storage: { type: 'memory' } });
cache.define('lookupUser', async (id: string) => {
  const res = await fetch(`https://api.internal/users/${id}`);
  return res.json();
});

async function* enrichRows(source: AsyncIterable<Buffer>): AsyncGenerator<string> {
  for await (const chunk of source) {
    const row = JSON.parse(chunk.toString());
    const user = await cache.lookupUser(row.userId); // deduped
    yield JSON.stringify({ ...row, user });
  }
}

await pipeline(createReadStream('data.ndjson'), enrichRows, createWriteStream('enriched.ndjson'));
```

**Pitfall:** Pipelines are lazy — without a consumer they never run. Always `await pipeline(...)` and never omit the destination stream.

### A4. Caching

| Library | Use Case | Key Feature |
|---------|----------|-------------|
| `lru-cache` | Bounded in-memory cache (max N entries) | Fast, predictable eviction |
| `async-cache-dedupe` | Deduplicate concurrent async calls | Stale-while-revalidate, dedup |

```ts
// lru-cache: bounded, in-memory
import { LRUCache } from 'lru-cache';
const cache = new LRUCache<string, any>({ max: 500, ttl: 1000 * 60 * 5 });
cache.set('key', value);
const val = cache.get('key');

// async-cache-dedupe: deduplicates concurrent requests
import { createCache } from 'async-cache-dedupe';
const dedupe = createCache({ ttl: 60, stale: 10 });
dedupe.define('fetchPlan', async (id: string) => api.getPlan(id));
// 100 concurrent calls → 1 actual request
const results = await Promise.all(ids.map(id => dedupe.fetchPlan(id)));
```

### A5. Graceful Shutdown

Use `close-with-grace` (from the Fastify team):

```ts
import closeWithGrace from 'close-with-grace';
import { createServer } from 'node:http';

const server = createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'ok' }));
});

server.listen(3000);

closeWithGrace({ delay: 10000 }, async ({ signal, err }) => {
  if (err) console.error('Shutdown error:', err);
  console.log(`${signal} received, closing server...`);

  // 1. Stop accepting new connections
  await new Promise<void>((resolve) => server.close(() => resolve()));
  // 2. Drain in-flight requests (the server.close callback handles this)
  // 3. Close external connections
  await db.end();
  console.log('Shutdown complete');
});
```

**Signal handling order:** SIGTERM/SIGINT → stop accepting new work → drain in-flight → close DB/cache → exit.

### A6. Testing with Node.js Built-in Test Runner (node:test)

```ts
import { describe, it, before, after, mock } from 'node:test';
import assert from 'node:assert';

describe('UserService', () => {
  let service: UserService;

  before(() => { service = new UserService(); });

  it('should create a user', async (t) => {
    const user = await service.create({ name: 'John' });
    assert.strictEqual(user.name, 'John');
    assert.ok(user.id);
  });

  it('should reject invalid input', async (t) => {
    await assert.rejects(
      () => service.create({ name: '' }),
      { message: 'Name is required' }
    );
  });
});
```

**Mocking with test context:**
```ts
it('should send email', async (t) => {
  const sendMock = t.mock.fn(async () => ({ success: true }));
  const service = new EmailService({ send: sendMock });

  await service.sendWelcome('user@example.com');
  assert.strictEqual(sendMock.mock.calls.length, 1);
});
```

**Fastify `inject()` for integration testing:**
```ts
import Fastify from 'fastify';
import { test } from 'node:test';
import assert from 'node:assert';
import myApp from '../app.js';

test('GET /health returns ok', async () => {
  const app = Fastify();
  await app.register(myApp);
  await app.ready();

  const response = await app.inject({ method: 'GET', url: '/health' });
  assert.strictEqual(response.statusCode, 200);
  assert.deepStrictEqual(response.json(), { status: 'ok' });
});
```

**Diagnosing flaky tests:**
1. Isolate the test with `--test-only` (`test.only()` in the file)
2. Run with `--test-timeout=5000` to surface hangs
3. Check for shared state, timer dependencies, or async teardown order
4. Use `--test-reporter=spec` for verbose output
5. Run individual files: `for f in src/**/*.test.ts; do echo "Running: $f"; timeout 30s node --test "$f" || echo "TIMEOUT: $f"; done`

**Diagnosing stuck processes** (tests that "do not exit"):
1. Isolate the file/test
2. Run with explicit timeout and reporter
3. Find open handles with `SIGUSR1` (requires `why-is-node-running`)
4. Patch deterministic teardown in every resource-creation scope

### A7. Async Patterns

- **Always** prefer `async/await` over raw `.then()` chains
- Use `Promise.allSettled()` when you need results from all promises even if some reject
- Use `AbortController` + `AbortSignal` for cancellable operations
- For concurrent bounded work: `p-limit` or `Promise.allSettled` with chunking

```ts
// Cancellable fetch with AbortController
async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  const ac = new AbortController();
  const timeout = setTimeout(() => ac.abort(), ms);
  try {
    return await fetch(url, { signal: ac.signal });
  } finally {
    clearTimeout(timeout);
  }
}
```

### A8. Profiling

```bash
# CPU profile
node --cpu-prof --cpu-prof-dir=./profiles app.js
node --prof-process isolate-*.log > processed.txt

# V8 optimization tracing
node --trace-opt --trace-deopt app.js
# Checkpoint: confirm no unexpected deoptimizations

# Event loop lag
node --trace-event-categories v8,node,node.async_hooks app.js

# Heap snapshot (open chrome://inspect)
node --inspect app.js
```

### A9. Environment Configuration

- Use `process.env` with validated defaults — never use `dotenv` in production
- Parse and validate at startup, not at point of use
- Use `@fastify/env` (see Section B) for Fastify apps

```ts
function env(key: string, fallback?: string): string {
  const val = process.env[key] ?? fallback;
  if (val === undefined) throw new Error(`Missing required env: ${key}`);
  return val;
}

const config = {
  port: parseInt(env('PORT', '3000'), 10),
  dbUrl: env('DATABASE_URL'),
  logLevel: env('LOG_LEVEL', 'info'),
};
Object.freeze(config);
```

---

## Section B: Fastify Application Architecture

### B1. Quick Start

```ts
import Fastify from 'fastify';

const app = Fastify({ logger: true });

app.get('/health', async (request, reply) => {
  return { status: 'ok' };
});

const start = async () => {
  await app.listen({ port: 3000, host: '0.0.0.0' });
};
start();
```

### B2. Plugin System

Fastify provides **automatic encapsulation** — each `app.register()` creates an isolated context.

```ts
// Encapsulated plugin — decorators NOT exposed to parent
app.register(async function childPlugin(fastify) {
  fastify.decorate('privateUtil', () => 'only available here');
  fastify.get('/child', async function (req, reply) {
    return this.privateUtil();
  });
});
```

**`fastify-plugin` to break encapsulation** (share decorators with parent context):

```ts
import fp from 'fastify-plugin';

export default fp(async function dbPlugin(fastify, opts) {
  const db = await connect(opts.connectionString);
  fastify.decorate('db', db);
  fastify.addHook('onClose', async () => { await db.close(); });
}, { name: 'database-plugin', dependencies: [] });
```

### B3. JSON Schema Validation with TypeBox

**Always use TypeBox** for type-safe schemas:

```ts
import { Type, type Static } from '@sinclair/typebox';

const CreateUserBody = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: 'email' }),
  age: Type.Optional(Type.Integer({ minimum: 0 })),
});

type CreateUserBodyType = Static<typeof CreateUserBody>;

app.post<{ Body: CreateUserBodyType }>('/users', {
  schema: { body: CreateUserBody },
}, async (req, reply) => {
  // req.body is fully typed
  const user = await createUser(req.body);
  return user;
});
```

**Request validates:** `body`, `querystring`, `params`, `headers`. **Response serializes** via `response` schema.

### B4. Request Lifecycle (Hooks)

Order of execution: `onRequest` → `preParsing` → `preValidation` → `preHandler` → handler → `preSerialization` → `onSend` → `onResponse`

```ts
// Global hook — applies to all routes
app.addHook('onRequest', async (request, reply) => {
  // Common: rate limiting, request logging, CORS pre-flight
});

// Scoped hook — applies only to routes in this plugin
app.register(async function scopedRoutes(fastify) {
  fastify.addHook('onRequest', async (req, reply) => {
    // Only affects routes registered inside this plugin
  });
});
```

### B5. Authentication

```ts
import jwt from '@fastify/jwt';

app.register(jwt, { secret: process.env.JWT_SECRET! });

app.addHook('onRequest', async (request, reply) => {
  try {
    await request.jwtVerify();
  } catch (err) {
    reply.send(err);
  }
});

app.get('/me', async (request) => {
  return request.user; // decoded JWT payload
});
```

### B6. Testing with inject()

```ts
import Fastify from 'fastify';
import myApp from '../app.js';

const app = Fastify();
await app.register(myApp);
await app.ready();

const res = await app.inject({
  method: 'POST',
  url: '/users',
  payload: { name: 'John', email: 'john@test.com' },
});

assert.strictEqual(res.statusCode, 201);
assert.deepStrictEqual(res.json().name, 'John');
```

### B7. Logging with Pino

Fastify uses Pino by default. Control via `logger` option:

```ts
const app = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: process.env.NODE_ENV !== 'production'
      ? { target: 'pino-pretty' }
      : undefined,
  },
});
```

**Per-request logs:** `request.log.info('processing order')` — automatically includes `reqId`.

### B8. CORS and Security Headers

```ts
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';

await app.register(cors, {
  origin: ['https://app.example.com'],
  credentials: true,
});

await app.register(helmet);
```

### B9. Error Handling in Fastify

```ts
// Global error handler
app.setErrorHandler(async (error, request, reply) => {
  const statusCode = error.statusCode ?? error.status ?? 500;

  request.log.error({ err: error }, 'Request error');

  return reply.status(statusCode).send({
    error: {
      code: error.code ?? 'INTERNAL_ERROR',
      message: statusCode >= 500 ? 'Internal server error' : error.message,
    },
  });
});
```

### B10. Full Lifecycle Recommendations

| Scenario | Reading Order |
|----------|--------------|
| New to Fastify | Plugins → Routes → Schemas |
| Adding auth | Plugins → Hooks → Authentication |
| Performance | Schemas → Serialization → Performance |
| Testing | Routes → Testing |
| Production | Logging → Configuration → Deployment |

---

## Section C: Node.js Core Internals

### C1. V8 Engine

**Garbage Collection:**
- **Scavenger** (young generation): fast, frequent. Objects that survive 2+ collections move to old generation.
- **Mark-Sweep** (old generation): marks live objects, sweeps dead ones. Triggers when old gen runs out of space.
- **Mark-Compact** (old gen): like Mark-Sweep but also compacts memory to reduce fragmentation.

**Hidden Classes and Inline Caching:**
- Adding properties to an object out of order creates different hidden classes → deoptimization
- Always initialize object properties in consistent order

**TurboFan JIT:**
- Functions become "hot" after ~1000 calls → TurboFan optimizes them
- Deoptimization happens when assumptions change (e.g., monomorphic call becomes polymorphic)

```bash
# Trace V8 optimization
node --trace-opt --trace-deopt app.js

# CPU profiling
node --prof app.js
node --prof-process isolate-*.log > processed.txt
```

### C2. libuv Event Loop

**Phases** (in order each tick):
1. **Timers** — `setTimeout`, `setInterval` callbacks
2. **Pending callbacks** — I/O callbacks deferred from previous cycle
3. **Idle, prepare** — internal use
4. **I/O poll** — waits for I/O events (blocking most of the time)
5. **Check** — `setImmediate` callbacks
6. **Close callbacks** — `close` events (e.g., socket.on('close'))

```bash
# Detect event loop lag
node --trace-event-categories v8,node,node.async_hooks app.js

# Thread pool (default 4 threads)
UV_THREADPOOL_SIZE=8 node app.js
```

**Key rules:**
- `setTimeout(cb, 0)` runs in **timers phase** (after I/O poll)
- `setImmediate(cb)` runs in **check phase** (after I/O poll, before next timers)
- In I/O callbacks, `setImmediate` always fires before `setTimeout(cb, 0)`
- Never block the event loop with synchronous CPU work — use worker threads

### C3. N-API and C++ Addons

```cpp
// Basic N-API addon: addon.cpp
#include <node_api.h>

napi_value Add(napi_env env, napi_callback_info info) {
  size_t argc = 2;
  napi_value args[2];
  napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);

  double a, b;
  napi_get_value_double(env, args[0], &a);
  napi_get_value_double(env, args[1], &b);

  napi_value result;
  napi_create_double(env, a + b, &result);
  return result;
}

napi_value Init(napi_env env, napi_value exports) {
  napi_value fn;
  napi_create_function(env, nullptr, 0, Add, nullptr, &fn);
  napi_set_named_property(env, exports, "add", fn);
  return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

**binding.gyp:**
```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**node-addon-api** (C++ wrapper, preferred for new code):
```cpp
#include <napi.h>

Napi::Number Add(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  double a = info[0].As<Napi::Number>().DoubleValue();
  double b = info[1].As<Napi::Number>().DoubleValue();
  return Napi::Number::New(env, a + b);
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports.Set("add", Napi::Function::New(env, Add));
  return exports;
}

NODE_API_MODULE(addon, Init)
```

**Segfault in native addon — decision tree:**
1. Reproduce with `node --napi-modules` → run `gdb`, capture `bt`
2. Does `bt` point to a V8 handle scope issue? → Check `HandleScope` usage
3. Points to a libuv callback? → Inspect async handle lifetime and `uv_close()` sequencing
4. No clear C++ frame? → Check JS-side type mismatches passed into the native binding

### C4. Node.js Core Contribution Rules

**Rebuild before testing:** Node.js embeds `lib/` JS into the binary via `js2c`. After any change to `src/` or `lib/`:

```bash
make -j$(nproc)    # rebuild
make lint          # JS, C++, MD, docs, YAML
make -j$(nproc) test   # or test specific area
```

**Lint before every commit:**
```bash
make -j$(nproc)
make lint
# C++ changes only:
CLANG_FORMAT_START="$(git merge-base HEAD upstream/main)" make format-cpp
git --no-pager diff --exit-code
git add -A && git commit -s   # -s is mandatory (DCO sign-off)
npx core-validate-commit --no-validate-metadata HEAD
```

**Commit message format:**
```
{area}: imperative description of change

Body explaining why and what, not how. Use terse subsystem-prefixed titles.
```

**NEVER** add `PR-URL:` or `Reviewed-By:` — those are added when the change lands. Every commit needs `git commit -s` (Signed-off-by).

---

## Section D: OAuth 2.0/2.1 with Fastify

### D1. Authorization Code + PKCE

```ts
// plugins/oauth.ts
import fp from 'fastify-plugin';
import oauth2 from '@fastify/oauth2';

export default fp(async function (fastify) {
  fastify.register(oauth2, {
    name: 'oauth2',
    scope: ['openid', 'profile', 'email'],
    credentials: {
      client: {
        id: process.env.CLIENT_ID!,
        secret: process.env.CLIENT_SECRET!,
      },
      auth: {
        authorizeHost: process.env.AUTH_SERVER!,
        authorizePath: '/authorize',
        tokenHost: process.env.AUTH_SERVER!,
        tokenPath: '/token',
      },
    },
    startRedirectPath: '/login',
    callbackUri: process.env.CALLBACK_URI!,
    pkce: 'S256',               // RFC 7636 — always for public clients
    generateStateFunction: (req) => req.session.state = crypto.randomUUID(),
    checkStateFunction: (req, callback) =>
      req.query.state === req.session.state
        ? callback()
        : callback(new Error('State mismatch')),
  });
});
```

**Validation checkpoint:** Confirm `callbackUri` matches a registered redirect URI at the auth server (RFC 6749 §3.1.2).

### D2. JWT Validation Middleware

```ts
import { FastifyRequest, FastifyReply } from 'fastify';
import jwt from '@fastify/jwt';

export async function verifyToken(request: FastifyRequest, reply: FastifyReply) {
  try {
    await request.jwtVerify();
    const payload = request.user as Record<string, unknown>;
    const now = Math.floor(Date.now() / 1000);

    if (typeof payload.exp === 'number' && payload.exp < now)
      return reply.code(401).send({ error: 'token_expired' });
    if (payload.iss !== process.env.EXPECTED_ISSUER)
      return reply.code(401).send({ error: 'invalid_issuer' });
    if (payload.aud !== process.env.EXPECTED_AUDIENCE)
      return reply.code(401).send({ error: 'invalid_audience' });
  } catch (err) {
    return reply.code(401).send({ error: 'invalid_token' });
  }
}
```

Validate `exp`, `iss`, `aud`, and `sub` on every request (RFC 7519 §4). Use asymmetric signing (RS256/ES256 via JWKS) for third-party tokens.

### D3. Refresh Token Rotation

```ts
async function refreshAccessToken(fastify, refreshToken: string) {
  const newToken = await fastify.oauth2.getNewAccessTokenUsingRefreshTokenFlow({
    refresh_token: refreshToken,
  });
  // Replace stored refresh token on every use (RFC 6749 §10.4)
  return {
    accessToken: newToken.token.access_token,
    refreshToken: newToken.token.refresh_token ?? refreshToken,
  };
}
```

### D4. Security Checklist

- Validate redirect URI against allowlist (RFC 6749 §3.1.2)
- PKCE S256 for all public clients (RFC 7636 §4.2)
- Validate `state` to prevent CSRF (RFC 6749 §10.12)
- Validate `iss`, `aud`, `exp` on every JWT (RFC 7519 §4)
- Rotate refresh tokens on every use (RFC 6749 §10.4)
- HTTPS everywhere; reject HTTP redirect URIs (RFC 6749 §3.1.2.1)
- Rate-limit token endpoints (OAuth 2.1 §7)

### D5. Anti-Patterns to Avoid

- **Storing tokens in localStorage** — use HttpOnly, Secure, SameSite=Strict cookies
- **Skipping audience validation** — allows token reuse across services
- **Using implicit flow** — deprecated in OAuth 2.1; use authorization code + PKCE
- **Symmetric signing (HS256) for third-party tokens** — use RS256/ES256 with JWKS

---

## Section E: Advanced TypeScript Types

### E1. Eliminating `any`

**Before** — raw `any`:
```ts
function getProperty(obj: any, key: string): any { return obj[key]; }
```

**After** — generic constraint:
```ts
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
// getProperty({ name: "Alice" }, "name") → inferred as string ✓
```

**Narrowing an unknown API response:**
```ts
interface User { id: number; name: string; }

function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value && 'name' in value;
}

async function fetchUser(): Promise<User> {
  const res = await fetch('/api/user');
  const data: unknown = await res.json();
  if (!isUser(data)) throw new Error('Invalid user shape');
  return data;
}
```

### E2. Conditional Types & infer

```ts
// Extract the resolved type from a Promise
type Unwrap<T> = T extends Promise<infer U> ? U : T;
type Result = Unwrap<Promise<string>>; // string

// Extract array element type
type Element<T> = T extends (infer U)[] ? U : never;
type Elem = Element<string[]>; // string

// Function return type (like ReturnType)
type MyReturn<T> = T extends (...args: any[]) => infer R ? R : never;
```

### E3. Template Literal Types

```ts
type EventName<T extends string> = `${T}Changed`;
type UserEvent = EventName<'user'>; // "userChanged"

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiPath = `/api/${string}`;
type Route = `[${HttpMethod}] ${ApiPath}`;
// "[GET] /api/users"
```

### E4. Mapped Types

```ts
type Readonly<T> = { readonly [K in keyof T]: T[K]; };
type Optional<T> = { [K in keyof T]?: T[K]; };
type Nullable<T> = { [K in keyof T]: T[K] | null; };

// Deep partial
type DeepPartial<T> = T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;
```

### E5. Branded/Opaque Types

```ts
// Type-safe identifiers — prevents mixing up UserId and OrderId
type Brand<T, B> = T & { __brand: B };
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function getUser(id: UserId): User { /* ... */ }

const userId = 'abc123' as UserId;
const orderId = 'xyz789' as OrderId;

getUser(userId);  // ✓ OK
getUser(orderId); // ✗ Type error — can't pass OrderId where UserId is expected
```

### E6. Type Workflow

When facing TypeScript errors:
1. Run `tsc --noEmit` to capture full error output
2. Identify root cause (unsound inference, missing constraints, implicit `any`)
3. Craft precise, type-safe solutions
4. Eliminate all `any` types — validate each replacement satisfies call sites
5. Confirm with a second `tsc --noEmit` pass

---

## Pitfalls

1. **Type stripping only works with Node 22.6+.** Check the Node.js version before using `--experimental-strip-types`. On older versions, fall back to `tsx` or `ts-node`.
2. **`import type` is mandatory for type stripping.** Using `import` for type-only imports will try to resolve the module at runtime and fail.
3. **`enum` and `namespace` don't work with type stripping.** Use `const` objects and plain modules instead.
4. **Streams: pipelines are lazy.** Without `await pipeline(...)` the stream never runs. Always await or return the promise.
5. **Fastify encapsulation hides decorators from sibling plugins.** Use `fastify-plugin` to share functionality across plugins.
6. **Never skip the rebuild step when contributing to Node.js core.** After editing `src/` or `lib/`, changes don't take effect until `make -j$(nproc)` runs.
7. **Never commit without `-s` in Node.js core.** Every commit must be `Signed-off-by` (DCO).
8. **OAuth state parameter must be cryptographically random and session-bound.** Using a fixed string or time-based seed breaks CSRF protection.
9. **`any` types propagate silently.** One `any` in a chain disables type checking for everything it touches. Always remove `any` from the source, not just the call site.
10. **Symmetric signing (HS256) with third-party OAuth providers is a security risk.** Only use asymmetric (RS256/ES256) and validate against a JWKS endpoint.

---

## Verification

Before shipping code produced with this skill:

| Check | Section | How |
|-------|---------|-----|
| `tsc --noEmit` passes | A1, E | Run TypeScript compiler |
| `node --test` passes | A6 | Run test suite |
| JWT validation covers exp/iss/aud | D2 | Verify hook/middleware claims check |
| Graceful shutdown handles SIGTERM | A5 | Send SIGTERM and confirm cleanup |
| Stream pipeline is awaited | A3 | Check for `await pipeline(...)` |
| All `any` types removed | E1, E6 | `tsc --noEmit --strict` shows 0 errors |
| Fastify plugins use `fastify-plugin` | B2 | Inspect shared decorators |
| No OAuth implicit flow | D4 | Confirm PKCE+authorization code |
| npm audit clean | A0 | `npm audit` |
