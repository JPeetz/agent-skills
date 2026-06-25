# API Documentation Completeness Checklist

Use this checklist to audit API documentation for completeness. Score each
endpoint against these criteria. Target: 100% coverage for public APIs, ≥80%
for internal APIs.

---

## Per-Endpoint Checklist

For every API endpoint, verify:

### Request Documentation

- [ ] HTTP method is documented (GET, POST, PUT, PATCH, DELETE)
- [ ] Full URL path is documented (including base URL)
- [ ] Path parameters are documented (name, type, required/optional, description,
      example)
- [ ] Query parameters are documented (name, type, required/optional, default,
      description, example)
- [ ] Request body schema is documented (JSON Schema or equivalent)
- [ ] Request body includes a complete example
- [ ] Content-Type header is documented (`application/json`, `multipart/form-data`, etc.)
- [ ] Authentication requirements are documented (method, scope, how to obtain)

### Response Documentation

- [ ] Success response (2xx) is documented
  - [ ] Status code
  - [ ] Response body schema
  - [ ] Complete response example
- [ ] Error responses are documented (at minimum 400, 401, 403, 404, 500)
  - [ ] Status code
  - [ ] Error body schema (RFC 7807 Problem Details recommended)
  - [ ] Error example for each documented error code
- [ ] Response headers are documented (RateLimit-*, ETag, Location, etc.)

### Behavioral Documentation

- [ ] Rate limits are documented (requests per window, window size)
- [ ] Pagination is documented (cursor-based or offset, page size limits)
- [ ] Sorting and filtering options are documented
- [ ] Idempotency behavior is documented (for POST/PUT/PATCH)
- [ ] Caching behavior is documented (Cache-Control headers, ETags)
- [ ] Webhook / callback behavior is documented (if applicable)
- [ ] Deprecation status is documented (if applicable: Sunset, Deprecation headers,
      migration path)

### Quality Checks

- [ ] All examples are valid (copy-paste into an API client and they work)
- [ ] No hardcoded credentials or API keys in examples
- [ ] Date/time formats are specified (ISO 8601 recommended)
- [ ] Field constraints are documented (min/max length, pattern, enum values)
- [ ] Nullable fields are documented
- [ ] Default values are documented for optional fields
- [ ] Backward-incompatible changes are documented with migration guidance
- [ ] The OpenAPI/Swagger spec is the canonical source (not hand-written prose)

---

## Cross-API Checklist

For the API as a whole:

- [ ] **Base URL** is documented (production, staging, sandbox)
- [ ] **Authentication overview** exists (all supported methods, how to get
      credentials, token refresh)
- [ ] **Versioning strategy** is documented (URL path, header, content negotiation)
- [ ] **Rate limiting overview** exists (global limits, per-endpoint limits,
      how to check remaining quota)
- [ ] **Error format** is documented (consistent across all endpoints)
- [ ] **Common patterns** are documented (pagination, filtering, sorting, search)
- [ ] **SDK / client library** documentation exists (if applicable)
- [ ] **Changelog / migration guide** is up to date
- [ ] **Quick start / getting started** guide exists
- [ ] **Glossary** of domain-specific terms exists (if applicable)

---

## Protocol-Specific Checklists

### REST / OpenAPI

- [ ] OpenAPI spec version is 3.0+ (3.1 preferred)
- [ ] `info` section is complete (title, version, description, contact)
- [ ] `servers` section includes all environments
- [ ] `security` / `securitySchemes` are defined
- [ ] All endpoints have `operationId`
- [ ] All endpoints have `tags` for grouping
- [ ] All schemas are defined under `components/schemas`
- [ ] All parameters use `schema` (not just `type`)
- [ ] `examples` are provided for complex request/response bodies

### GraphQL

- [ ] Schema introspection is enabled (or documented as disabled)
- [ ] Every type has a `description`
- [ ] Every field has a `description`
- [ ] Every query/mutation has a `description`
- [ ] Every enum value has a `description`
- [ ] Deprecated fields use the `@deprecated` directive with a `reason`
- [ ] Input types have validation constraints documented
- [ ] Pagination uses the Relay Connection spec (or an alternative is documented)
- [ ] Error extensions (code, path, etc.) are documented

### gRPC

- [ ] Every service has a comment describing its purpose
- [ ] Every RPC method has a comment
- [ ] Every message has a comment
- [ ] Every field has a comment
- [ ] Streaming behavior is documented (unary, server, client, bidi)
- [ ] Error codes are documented per RPC
- [ ] Deadline/timeout recommendations are documented
- [ ] Authentication metadata requirements are documented

---

## Automated Checks

Checks that can be automated in CI/CD:

- [ ] OpenAPI spec validates against the OpenAPI 3.x JSON Schema
- [ ] OpenAPI spec has no undefined `$ref` references
- [ ] All endpoints have at least one success response documented
- [ ] All endpoints have at least one error response documented
- [ ] All endpoints have `operationId`
- [ ] GraphQL schema parses without errors
- [ ] GraphQL schema has no types/fields without descriptions
- [ ] Protobuf files compile without errors
- [ ] API examples in docs are valid JSON (or valid per Content-Type)
- [ ] No hardcoded credentials, keys, or tokens in any doc

---

## Scoring

For each endpoint, calculate:

```
Endpoint Score = (checks passed / total applicable checks) × 100
```

For the API overall:

```
API Score = average of all endpoint scores
```

**Targets:**

| API Type | Minimum Score |
|----------|--------------|
| Public / External API | 100% |
| Internal / Partner API | ≥90% |
| Internal / Team API | ≥80% |
| Experimental / Alpha API | ≥60% |

---

*Version: 1.0.0 — Last updated: 2026-06-23*