# API Documentation Completeness Checklist

Use this checklist when auditing or writing API documentation. Every check
should be verified — not assumed.

## Every Endpoint

- [ ] HTTP method and path are documented
- [ ] Path parameters documented with types, descriptions, and examples
- [ ] Query parameters documented with types, descriptions, defaults, and whether required
- [ ] Request body schema documented (if applicable) with all field types and descriptions
- [ ] Authentication requirements documented (API key? OAuth? JWT?)
- [ ] Success response shape documented with example
- [ ] Error codes documented — both HTTP status codes and error response body shapes
- [ ] Rate limits documented (requests per window, headers returned)
- [ ] Deprecation status documented if applicable (`Sunset` and `Deprecation` headers)

## Collections (List Endpoints)

- [ ] Pagination method documented (cursor-based vs offset-based)
- [ ] Page size default and maximum documented
- [ ] Sort/filter parameters documented
- [ ] Response includes pagination metadata documented

## Schema / Type Documentation

- [ ] Every field has a description, type, and example
- [ ] Enumerated values are listed with descriptions
- [ ] Required vs optional fields are clearly marked
- [ ] Default values are documented
- [ ] Format constraints documented (ISO 8601 for dates, UUID for IDs, etc.)

## General

- [ ] Base URL is documented
- [ ] API versioning strategy is documented (URL path prefix vs header)
- [ ] Authentication/authorization flow is documented end to end
- [ ] Error response shape is consistent across all endpoints (RFC 7807 recommended)
- [ ] Example requests and responses exist for all major use cases
- [ ] Rate limit headers and retry-after behavior documented
- [ ] Changelog or version history for the API exists
- [ ] Contact/support information for API consumers
- [ ] SDK or client library links (if available)
- [ ] OpenAPI spec is the canonical source — human docs are generated from it, not maintained separately