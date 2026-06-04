# CHANGELOG — api-design-first

## v1.0.0 — 2026-06-04

### Added
- Initial release of API Design-First agent skill
- Design-first workflow: Resource Model → OpenAPI 3.1 Spec → Review → Mock → Implementation → Tests
- Complete OpenAPI 3.1 specification generation with all required sections
- Resource naming conventions (plural nouns, max 2 levels deep)
- REST endpoint patterns: CRUD operations with correct HTTP methods
- RFC 7807 Problem Details error response format
- Complete HTTP status code usage table (200-500)
- Cursor-based pagination (preferred) and offset-based pagination (acceptable)
- URL path API versioning with deprecation headers (Sunset, Deprecation, Link)
- Authentication patterns: Bearer JWT, API Key, OAuth2 (with OpenAPI securitySchemes)
- Tiered rate limiting with standard response headers (RateLimit-*, Retry-After)
- Idempotency key pattern (Idempotency-Key header) for safe retries
- Filtering, sorting, searching, sparse fieldsets, and include patterns
- GraphQL schema design with Relay Cursor Connections
- gRPC proto design with service definitions
- Cross-protocol consistency rules (camelCase, ISO 8601 dates, cursor pagination everywhere)
- Security hardening: input validation, TLS, CORS, CSP, security headers, rate limiting
- API Design Checklist (15 items) for spec review
- 6 eval cases with near-miss negatives
- Helper scripts: validate-spec.sh, generate-mock.sh, generate-sdk.sh
- Reference docs: OpenAPI Best Practices, REST Checklist, RFC Standards

### Why
The ecosystem has API documentation skills and database schema skills, but no
API design-first skill that enforces contract-first development across REST,
GraphQL, and gRPC. This skill fills the gap between "generate API docs from code"
and "design database schema" by providing a complete API architecture workflow
that drives code generation, not documentation retrofitting.