# Changelog

All notable changes to this skill package are documented here.

## [1.0.0] — 2025-09-07

### Added

- **Initial release** — Comprehensive Node.js Development meta-skill packaging 5 core skillsets from [mcollina/skills](https://github.com/mcollina/skills) by Matteo Collina.

### Sections included

- **Section A: Node.js Best Practices** — Type stripping (Node 22.6+), error handling (`@fastify/create-error`, operational vs programmer), streams (`pipeline()` + async generators), caching (`lru-cache`, `async-cache-dedupe`), graceful shutdown (`close-with-grace`), testing (`node:test` + `inject()`), flaky test diagnosis, stuck process diagnosis, async patterns (`AbortController`, `Promise.allSettled`), profiling (`--cpu-prof`, `--trace-opt`), environment configuration.
- **Section B: Fastify Application Architecture** — Plugin system & encapsulation, TypeBox schema validation, request lifecycle (hooks), authentication (`@fastify/jwt`), testing (`inject()`), logging (Pino), CORS/security, error handling, full lifecycle reading recommendations.
- **Section C: Node.js Core Internals** — V8 GC (Scavenger, Mark-Sweep, Mark-Compact), hidden classes & inline caching, TurboFan JIT & deoptimization, libuv event loop phases & thread pool, N-API & node-addon-api C++ addons, segfault decision tree, Node.js core contribution rules.
- **Section D: OAuth 2.0/2.1 with Fastify** — Authorization Code + PKCE, JWT validation middleware, refresh token rotation, security checklist, anti-patterns.
- **Section E: Advanced TypeScript Types** — Eliminating `any`, conditional types & `infer`, template literal types, mapped types, branded/opaque types, type workflow.

### Source skills adapted

| Source Skill | Source Author | Coverage |
|-------------|--------------|----------|
| node | Matteo Collina | §A except node-modules-exploration, modules (covered by TypeScript section) |
| fastify | Matteo Collina | §B (all 19 rule files condensed) |
| nodejs-core | Matteo Collina | §C (all domains, condensed) |
| oauth | Matteo Collina | §D (all flows condensed with security checklist) |
| typescript-magician | Matteo Collina | §E (core patterns condensed) |

### Not included (already covered in JPeetz/agent-skills or universal)

| Source Skill | Reason for Exclusion |
|--------------|---------------------|
| documentation | Already handled by JPeetz/agent-skills documentation-content category |
| init (AGENTS.md) | Already handled by JPeetz/agent-skills skill-development category |
| linting-neostandard-eslint9 | General tooling, not Node.js-specific |
| octocat | Already handled by JPeetz/agent-skills git-release category |
| skill-optimizer | General skill optimization, not Node.js-specific |
| snipgrapher | Code snippet rendering, not Node.js-specific |
