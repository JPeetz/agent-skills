---
name: find-docs
description: >-
  Use when fetching current docs, API references, and code examples for a
  named library, framework, SDK, CLI, or cloud service via Context7 — API
  syntax, configuration, migration, setup, and library-specific debugging,
  even for well-known libraries: training data lags releases. Not for general
  web search or non-library topics.
---

# Documentation lookup

Retrieve current documentation and code examples for any library with the
Context7 CLI. Run it through `npx ctx7@latest` — no global install needed:

```bash
npx ctx7@latest library <name> "<query>"   # 1. resolve name to a library ID
npx ctx7@latest docs <libraryId> "<query>" # 2. query docs with that ID
```

Run `library` first unless the user supplies an ID in `/org/project` or
`/org/project/version` form. Cap the pair at 3 invocations per question; past
that, answer from the best result you have.

Keep secrets, credentials, personal data, and proprietary code out of every
query.

## Choosing a library

`library` results carry name, description, snippet count, source reputation
(High/Medium/Low/Unknown), benchmark score (max 100), and known versions.
Prefer the official spelling ("Next.js" not "nextjs"; try alternate spellings
before rewriting the query), then pick the best match on name similarity,
snippet count, reputation, and score. When several match, note the pick and
proceed; when none do, say so and suggest a refined query; when the library
itself is ambiguous, ask before guessing. When the user names a version,
append the closest listed one: `/org/project/version`.

## Querying docs

Library IDs keep their leading `/` (`/facebook/react`, not `facebook/react`).
The `query` argument is required and drives ranking: describe what to look up
in the docs, not the task to complete. One topic per query — split
multi-concept questions into separate `docs` calls unless the question is how
the concepts interact.

| Quality | Example |
|---------|---------|
| Good | `"How to set up authentication with JWT in Express.js"` |
| Good | `"React useEffect cleanup function with async operations"` |
| Bad (too vague) | `"auth"` |
| Bad (too broad) | `"routing and auth and caching in Next.js"` |

Output mixes titled **code snippets** (language-tagged blocks) and **info
snippets** (prose with breadcrumb context).

## Authentication

Works unauthenticated. For higher rate limits, `export
CONTEXT7_API_KEY=<key>` or `npx ctx7@latest login`.

## Failure

On a quota error ("Monthly quota reached" or "quota exceeded"), tell the user
the quota is exhausted, suggest `npx ctx7@latest login`, and only then answer
from training knowledge flagged as possibly outdated. Never fall back
silently.
