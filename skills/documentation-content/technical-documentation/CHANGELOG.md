# CHANGELOG — technical-documentation

## v1.0.0 — 2026-06-23

### Added
- Initial release of Technical Documentation agent skill
- Documentation type coverage: README, ADR, API docs (REST/GraphQL/gRPC),
  runbooks, onboarding guides, changelogs, knowledge base, AI agent context
- Architecture Decision Records (ADR) workflow with full template in
  `references/adr-template.md`
- API documentation patterns for OpenAPI 3.1 / Swagger, GraphQL introspection,
  and gRPC protobuf comments
- README quality standards with RED FLAG and YELLOW FLAG severity system
- Markdown best practices covering structure, code blocks, tables, links,
  images, and Mermaid diagrams
- Documentation-Driven Development (DDD) workflow with PR template
- Three-dimensional documentation auditing system (completeness, accuracy,
  freshness) with audit report format
- Knowledge base maintenance strategy with freshness review schedule
- AI agent-facing documentation patterns (AGENTS.md, CLAUDE.md, CURSOR.md,
  copilot-instructions.md, windsurfrules)
- Cross-platform agent context file compatibility table
- When to Use / Near-Miss Negatives with 8 negative patterns
- 10 Common Pitfalls & Anti-Patterns with corresponding Quality Checklist
- 7 Safety Rules including credential exposure prevention, destructive command
  warnings, and agent safety
- Platform compatibility notes for all 8 major agentic platforms
- Severity scale for documentation audits (CRITICAL / MAJOR / MINOR / NIT)
- Validation script (`scripts/validate_skill.py`) for SKILL.md compliance
- 8 eval cases (5 positive + 3 near-miss negative) in `evals/test_cases.json`
- Complete ADR template in `references/adr-template.md`

### Why
The ecosystem has code-review agents, API design agents, and test generation
agents, but no comprehensive technical documentation skill that covers the full
documentation lifecycle — from README composition through ADRs, API docs,
runbooks, onboarding guides, changelogs, knowledge base maintenance, and
AI-agent-facing documentation. This skill fills that gap by providing a single
source of truth for all technical documentation patterns, workflows, and
quality standards, including the emerging domain of AGENTS.md / CLAUDE.md
context files that AI coding assistants depend on.
## v1.0.1 — 2026-06-25

### Changed
- Published to GitHub repository (JPeetz/agent-skills)
- Part of Skill Foundry Run 004
