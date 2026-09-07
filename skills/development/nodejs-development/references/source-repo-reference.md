# Source Repository Reference

This meta-skill was adapted from [mcollina/skills](https://github.com/mcollina/skills) by Matteo Collina (Node.js core contributor, Fastify creator).

## Repository Structure (Source)

```
skills/
├── documentation/        → Diátaxis framework (excluded — general-purpose)
├── fastify/              → Fastify best practices, 19 rule files (adapted → §B)
├── init/                 → AGENTS.md management (excluded — general-purpose)
├── linting-neostandard-eslint9/ → ESLint v9 flat config (excluded — general-purpose)
├── node/                 → Node.js best practices, 15 rule files (adapted → §A)
├── nodejs-core/          → Node core internals, 21+ rule files (adapted → §C)
├── oauth/                → OAuth 2.0/2.1 with Fastify (adapted → §D)
├── octocat/              → Git/GitHub via gh CLI (excluded — already in agent-skills)
├── skill-optimizer/      → Skill optimization methodology (excluded — general-purpose)
├── snipgrapher/          → Code snippet image rendering (excluded — general-purpose)
└── typescript-magician/  → Advanced TypeScript types, 14 rule files (adapted → §E)
```

## Why These 6 Skills Were Excluded

| Source Skill | Reason |
|-------------|--------|
| `documentation` | Diátaxis framework is a general documentation methodology, not Node.js-specific. Already covered by JPeetz/agent-skills `documentation-content/` category. |
| `init` | AGENTS.md creation/optimization is a general repo-onboarding concern. Already covered by JPeetz/agent-skills `skill-development/` category. |
| `linting-neostandard-eslint9` | ESLint v9 / neostandard is a general JS/TS linting tool, not Node.js-specific. Universal across stacks. |
| `octocat` | GitHub workflow via gh CLI is a general git operation skill. Already covered by JPeetz/agent-skills `git-release/` and `github-code-review` skills. |
| `skill-optimizer` | Skill activation benchmarking and optimization is a general meta-dev concern. Not Node.js-specific. |
| `snipgrapher` | Code snippet rendering to PNG/SVG is a documentation presentation tool, not Node.js-specific. |

## Verification of Content Fidelity

Each section of this meta-skill was condensed from the corresponding source skill's rule files:

- **§A (Node.js Best Practices)** — Drawn from all 15 rule files in `skills/node/rules/`
- **§B (Fastify)** — Drawn from all 19 rule files in `skills/fastify/rules/`
- **§C (Node.js Core Internals)** — Drawn from 21+ rule files in `skills/nodejs-core/rules/`
- **§D (OAuth 2.0/2.1)** — Drawn from `skills/oauth/SKILL.md` and its reference files
- **§E (Advanced TypeScript)** — Drawn from all 14 rule files in `skills/typescript-magician/rules/`

All code examples are original or adapted from the source material. No content was fabricated.