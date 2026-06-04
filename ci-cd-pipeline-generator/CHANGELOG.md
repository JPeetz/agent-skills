# CHANGELOG — ci-cd-pipeline-generator

## v1.0.0 — 2026-06-04

### Added
- Initial release of CI/CD Pipeline Generator agent skill
- GitHub Actions pipeline generation with full DAG-aware parallel stages
- GitLab CI pipeline generation (`.gitlab-ci.yml`)
- CircleCI and Jenkins pipeline support
- Multi-environment deployment: staging → production with approval gates
- Canary deployment pattern for Kubernetes
- Rollback strategies for all deployment types (K8s, Docker, Serverless, Static)
- Security mandates: SHA-pinned actions, OIDC auth, token permission limits, artifact signing
- Container scanning integration (Trivy)
- Dependency audit steps (npm audit, pip-audit, govulncheck)
- Caching strategy documentation (package managers, Docker layer cache, build cache)
- Secrets management guidance with platform-native secrets
- Pipeline diagram generation (Mermaid)
- Monorepo path-filtering support
- Multi-language matrix build support
- Database migration stage with rollback patterns
- Ready-to-use templates: Node.js+K8s, Python+ECS, Go+Kube, Static Site
- 5 eval cases with near-miss negatives
- Reference documentation for provider-specific best practices

### Why
Fills a critical gap in the agent skills ecosystem: no existing skill provides
end-to-end CI/CD pipeline generation with security validation, environment
promotion, and rollback strategies. Existing alternatives (env-doctor, basic
CI config generators) only handle diagnostics or single-stage pipelines.