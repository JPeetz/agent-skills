# CHANGELOG — n8n-api-shape

## v1.0.0 — 2026-10-28

### Added
- Initial release of the instance-agnostic n8n REST API shape reference
- GET /api/v1/workflows/{id} read recipe
- PUT update recipe stripping extra fields down to the minimal 4-key payload
- Banned top-level fields list and the credentials-pop pitfall for nodes
- Health check (/api/v1/health) before any workflow edit
- Vault-based API key guardrails (never hardcode, never echo)
- evals/evals.json with 6 cases (5 positive, 1 near-miss negative)