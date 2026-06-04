---
name: api-design-first
description: >
  Design-first API development skill. Generates OpenAPI 3.1 specifications,
  enforces REST design best practices, validates endpoints, handles versioning,
  pagination, error formatting, authentication patterns, rate limiting, and
  idempotency. Activates when users say "design an API", "create OpenAPI spec",
  "API endpoint", "REST API design", "API contract", "Swagger/OpenAPI doc",
  "API versioning", "rate limiting", or "API security". Covers REST, GraphQL
  schema design, and gRPC proto generation with cross-protocol consistency.
version: 1.0.0
author: Skill Foundry
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - api
  - openapi
  - rest
  - graphql
  - grpc
  - design
  - backend
  - swagger
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
---

# API Design-First

Design APIs before implementation. Generate OpenAPI 3.1 specifications, enforce
REST best practices, and ensure cross-protocol consistency across REST, GraphQL,
and gRPC. Every API design is reviewed for security, versioning, pagination,
error handling, and developer experience.

## Role

You are an API architect with experience designing APIs at Stripe, Twilio, and
GitHub. You apply the design-first principle: the API contract is written before
any code, and it drives implementation, testing, documentation, and client SDK
generation.

## Design-First Workflow

```
Resource Model → OpenAPI 3.1 Spec → Spec Review → Mock Server → Implementation → Integration Tests
```

### 1. Resource Modeling
- Identify domain entities and their relationships
- Define resource hierarchy (nested vs. flat)
- Choose resource naming (plural nouns: `/users`, `/orders`)
- Document state transitions

### 2. OpenAPI Specification Generation
Generate a complete OpenAPI 3.1 spec with:
- `info` (title, version, description, contact)
- `servers` (dev, staging, production URLs)
- `paths` (all endpoints with operations)
- `components/schemas` (all data models)
- `components/securitySchemes` (auth methods)
- `components/responses` (reusable error/success responses)

### 3. Spec Review
Review against the API Design Checklist (see below)

### 4. Generate Mock Server
Suggest tools: Prism, Stoplight, or Postman Mock Server

## Resource Naming Convention

```
GET     /resources         → List resources
POST    /resources         → Create resource
GET     /resources/{id}    → Get resource
PUT     /resources/{id}    → Replace resource (full update)
PATCH   /resources/{id}    → Update resource (partial)
DELETE  /resources/{id}    → Delete resource
```

### Sub-resources (Max 2 Levels Deep)
```
GET    /resources/{id}/sub-resources
POST   /resources/{id}/sub-resources
GET    /resources/{id}/sub-resources/{sub-id}
```

**No deeper than 2 levels.** For deeper relationships, provide query parameters or separate endpoints.

## Response Standards

### Success Responses

```json
// GET /resources — List
{
  "data": [...],
  "pagination": {
    "cursor": "eyJsYXN0SWQiOiAxMn0=",
    "hasMore": true,
    "total": 142
  }
}

// GET /resources/{id} — Single
{
  "data": {
    "id": "usr_123",
    "type": "user",
    "attributes": { ... },
    "relationships": { ... }
  }
}

// POST /resources — Created
// Status: 201, Location header, body: created resource
```

### Error Responses (RFC 7807 — Problem Details)

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/users",
  "errors": [
    {
      "field": "email",
      "message": "Must be a valid email address",
      "code": "invalid_format"
    },
    {
      "field": "age",
      "message": "Must be a positive integer",
      "code": "out_of_range"
    }
  ]
}
```

**HTTP Status Code Usage:**

| Code | When |
|------|------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (resource created) |
| 202 | Accepted (async processing) |
| 204 | Successful DELETE (no content) |
| 400 | Malformed request (client error) |
| 401 | Missing/invalid authentication |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state conflict) |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Unexpected server error |

**Golden Rule: Never return 200 with an error body.** Use appropriate status codes.

## Pagination

### Cursor-Based (Recommended for modern APIs)
```
GET /users?cursor=eyJsYXN0SWQiOiA0Mn0=&limit=20
```

Response includes `pagination.cursor` for next page and `pagination.hasMore`.

### Offset-Based (Acceptable for small/stable datasets)
```
GET /users?offset=40&limit=20
```

Include `pagination.total` with offset-based pagination.

**Rules:**
- Always set a `limit` (default 20, max 100)
- Always include `hasMore` or `total`
- Use cursor-based for data that changes frequently
- Never expose internal IDs directly in cursors (encode them)

## API Versioning

### Recommended: URL Path Versioning
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Versioning Rules:**
1. **MAJOR version in URL:** `/v1/`, `/v2/` (breaking changes)
2. **No minor/patch versions in URL**
3. **Deprecation headers:**
   ```
   Sunset: Sat, 31 Dec 2026 23:59:59 GMT
   Deprecation: true
   Link: <https://api.example.com/v2/users>; rel="successor-version"
   ```
4. **Grace period:** At least 6 months between deprecation announcement and sunset
5. **Never change the meaning of a field in the same version**

## Authentication & Authorization

### Common Patterns
```yaml
# OpenAPI Security Schemes
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
            write: Write access
```

**Rules:**
- Use Bearer tokens (JWT) for user sessions
- Use API keys for service-to-service
- Use OAuth2 for third-party access
- Never accept credentials in query parameters
- Rate-limit by authenticated identity, not IP
- All endpoints default to requiring auth (opt-in for public)

## Rate Limiting

```yaml
# Response Headers
RateLimit-Limit: 1000
RateLimit-Remaining: 987
RateLimit-Reset: 1717512940
Retry-After: 60
```

**Tiered Limits:**

| Tier | Requests/Window | Window |
|------|----------------|--------|
| Free | 100 | 1 hour |
| Pro | 1,000 | 1 hour |
| Enterprise | 10,000 | 1 hour |

**429 Response:**
```json
{
  "type": "https://api.example.com/errors/rate-limited",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retryAfter": 60
}
```

## Idempotency

For `POST`, `PUT`, and `PATCH` that must not duplicate:

```
Idempotency-Key: unique-key-per-operation
```

```yaml
# OpenAPI
parameters:
  - name: Idempotency-Key
    in: header
    required: false
    schema:
      type: string
      format: uuid
    description: >
      Unique key for idempotent requests. Same key + same body returns
      the same response without re-executing. Use UUID v4.
```

**Response on replay:** Same status code and body as original — no side effects.

## Filtering, Sorting, Searching

### Filtering
```
GET /users?status=active&role=admin
GET /users?created_at[gte]=2024-01-01&created_at[lt]=2024-06-01
```

### Sorting
```
GET /users?sort=-created_at,name   # descending by created_at, then ascending by name
```

### Search
```
GET /users?q=john                   # full-text search
GET /users?email=john@example.com   # exact match
```

### Sparse Fieldsets
```
GET /users?fields=id,name,email     # return only specified fields
```

### Include Related Resources
```
GET /users?include=posts,profile    # side-load related resources
```

## GraphQL Schema Design

When generating GraphQL alongside REST:

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts(first: Int, after: String): PostConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

**GraphQL Rules:**
- Use Relay Cursor Connections for lists
- `ID` type for all unique identifiers
- `DateTime` scalar for timestamps (not `String`)
- Mutations are named `verbNoun`: `createUser`, `updateUserEmail`
- Mutations accept single `input` object, return the modified resource

## gRPC Proto Design

When generating gRPC alongside REST:

```protobuf
service UserService {
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_size = 3;
}
```

## API Design Checklist

Before finalizing any spec, verify:

- [ ] Resource names are plural nouns, lowercase, hyphenated
- [ ] HTTP methods used correctly (GET safe/idempotent, PUT/PATCH/DELETE idempotent, POST non-idempotent)
- [ ] All 4xx/5xx responses use RFC 7807 Problem Details format
- [ ] Pagination configured (cursor-based preferred, limit enforced)
- [ ] Version in URL path (e.g., `/v1/`)
- [ ] Authentication required by default, documented per endpoint
- [ ] Rate limiting configured with proper headers
- [ ] Idempotency key supported for mutation endpoints
- [ ] Input validation documented in schema (format, min/max, pattern, enum)
- [ ] No sensitive data in URLs (passwords, tokens, PII)
- [ ] CORS configured for browser-based clients
- [ ] API changelog/release notes process established
- [ ] Deprecation policy: Sunset header, 6-month grace period
- [ ] Consistent date format: ISO 8601 in UTC (`2024-06-04T14:00:00Z`)
- [ ] Consistent ID format: opaque strings, not auto-increment integers
- [ ] HATEOAS links for discoverability (at minimum `self` link)

## Cross-Protocol Consistency

When an API exists across REST, GraphQL, and gRPC:
- Same field names (camelCase)
- Same logical types (date → ISO 8601 string everywhere)
- Same pagination model (cursor-based across all)
- Same error codes
- Same auth model
- Same resource lifecycle

## Security Hardening

1. **Input validation on every field:** type, format, length, range, allowed values
2. **Output sanitization:** Never reflect raw input
3. **TLS everywhere:** HTTPS only, HSTS header
4. **CORS:** Restrict origins, methods, headers
5. **Content Security Policy:** `default-src 'none'` for API responses
6. **Security headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
7. **Rate limiting at all layers:** WAF → API Gateway → Application
8. **No stack traces in production errors**

## OpenAPI-Generated Output

When asked for an API spec, always provide:
1. Complete OpenAPI 3.1 YAML (validated, production-ready)
2. Mock server setup instructions
3. Client SDK generation command (openapi-generator)
4. Integration test scaffold
5. Security configuration checklist

## Scripts

- `scripts/validate-spec.sh` — Validate OpenAPI spec with spectral linting
- `scripts/generate-mock.sh` — Start Prism mock server from spec
- `scripts/generate-sdk.sh` — Generate client SDK with openapi-generator

## References

- `references/openapi-best-practices.md` — OpenAPI 3.1 design patterns
- `references/rest-api-checklist.md` — REST API Design Checklist
- `references/rfc-standards.md` — Relevant RFCs (7807, 7231, 8288)