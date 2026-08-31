# Changelog — GraphQL API Development Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-06-23

### Added
- Initial release by Skill Foundry
- Comprehensive schema design workflow: naming conventions, pagination
  patterns (Relay cursor + simplified offset), typed union error handling,
  schema documentation standards
- Resolver architecture patterns: parent-to-child delegation, field-level
  authorization, DataLoader setup for N+1 prevention with critical rules
- Mutation design patterns: single input types, idempotency key support,
  payload types, thin-resolver/thick-service architecture
- Real-time subscription patterns: event-driven PubSub, filtered
  subscriptions with `withFilter`, WebSocket authentication, async iterator
  teardown and cleanup
- Apollo Federation principles: entity definition with `@key`, reference
  resolvers, `@shareable`/`@requires`/`@tag` usage, contract-based API
  versioning, `_entities` query testing
- Security hardening: depth limiting (graphql-depth-limit), query cost
  analysis, per-operation rate limiting, schema-directive-based authz,
  introspection gating
- Performance optimization: Automatic Persisted Queries (APQ), field-level
  `@cacheControl` directives, CDN GET-based caching, response compression,
  `@defer`/`@stream` incremental delivery, Apollo inline tracing
- Quick Reference table: 8 dimensions with key indicators
- Common Pitfalls & Anti-Patterns: 10 GraphQL-specific anti-patterns with
  descriptions and correct approaches
- 10-item GraphQL Quality Checklist
- Safety Rules: 8 absolute rules for production GraphQL APIs
- Platform Compatibility Notes for all 8 agentic platforms
- 7 eval cases (5 positive, 2 near-miss negatives) with expected behaviors
- PEP 723 validation script for schema and resolver output validation
- Comprehensive `references/graphql-patterns.md` reference document
- SEO-optimized description with primary keyword clusters for AI engine
  discovery
## v1.0.1 — 2026-06-25

### Changed
- Published to GitHub repository (JPeetz/agent-skills)
- Part of Skill Foundry Run 004
