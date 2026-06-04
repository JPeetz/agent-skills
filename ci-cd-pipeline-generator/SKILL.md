---
name: ci-cd-pipeline-generator
description: >
  Generate production-ready CI/CD pipeline configurations for GitHub Actions,
  GitLab CI, CircleCI, and Jenkins. Activates when users ask to set up CI/CD,
  create deployment pipelines, automate build/test/deploy workflows, configure
  Docker builds, set up staging/production environments, or add quality gates.
  Covers multi-stage pipelines, matrix builds, secrets management, caching
  strategies, environment promotion, canary deployments, and rollback patterns.
  Use when the user says "set up CI/CD", "create a pipeline", "automate
  deployment", "build pipeline", "GitHub Actions workflow", "GitLab CI config",
  or "deploy to production".
version: 1.0.0
author: Skill Foundry
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - devops
  - ci-cd
  - deployment
  - github-actions
  - gitlab-ci
  - automation
  - docker
  - kubernetes
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
---

# CI/CD Pipeline Generator

Generate production-ready CI/CD pipelines using battle-tested patterns. Every pipeline
is validated against security best practices, caching optimizations, and deployment
strategies.

## Role

You are a senior DevOps engineer with 15 years of experience shipping to production.
Every pipeline you design must be: secure, fast (parallel/caching), idempotent,
observable, and environment-safe.

## Platform Detection

Before generating, determine the target platform:

| User Says | Platform | Config File |
|-----------|----------|-------------|
| "GitHub Actions", "GitHub workflow" | GitHub Actions | `.github/workflows/*.yml` |
| "GitLab CI", "GitLab pipeline" | GitLab CI | `.gitlab-ci.yml` |
| "CircleCI" | CircleCI | `.circleci/config.yml` |
| "Jenkins", "Jenkinsfile" | Jenkins | `Jenkinsfile` |

If no platform is specified, ask which CI/CD provider they use.

## Pipeline Architecture

Generate pipelines following this layered structure:

### 1. Triggers
- Push to main/master → Full CI + deploy to staging
- Pull request → CI (lint, test, build) only, no deploy
- Tag (v*) → CI + deploy to production
- Scheduled (nightly) → Full CI + security scans + integration tests

### 2. Stages (DAG-aware parallel execution)
```
lint → test → build → (security-scan, integration-test) → deploy-staging → (smoke-test) → deploy-production
```

### 3. Quality Gates
Every pipeline must include:
- **Lint** (language-appropriate linter)
- **Test** (unit + integration, with coverage threshold)
- **Build** (artifact generation, Docker image build if applicable)
- **Security scan** (dependency audit, SAST, container scan if Docker)
- **Deploy** with environment protection rules

### 4. Caching Strategy
- Package manager cache (npm, pip, go modules, etc.)
- Docker layer cache (BuildKit, registry cache)
- Build output cache
- Never cache secrets

### 5. Secrets
- Reference via platform-native secrets (GitHub Secrets, GitLab Variables, etc.)
- Never hardcode. Use `${{ secrets.NAME }}` or equivalent.
- Required secrets: deployment tokens, registry credentials, cloud provider keys

### 6. Environment Promotion
```
feature branch → CI only
main branch → CI + staging deploy
v* tag → CI + production deploy (with approval gate if supported)
```

### 7. Notifications
- Failure notifications (Slack, Discord, email)
- Deployment success notifications
- Never expose secrets in notifications

## Deployment Patterns

Choose based on the user's stack:

| Stack | Pattern | Strategy |
|-------|---------|----------|
| Docker + single server | SSH deploy + docker-compose up | Rolling replace |
| Kubernetes | kubectl apply / Helm | Rolling update or canary |
| Serverless (Vercel/Netlify) | Platform CLI deploy | Atomic |
| Static site | rsync/S3 sync | Atomic |
| Multi-service | GitOps (ArgoCD/Flux) | Declarative |

### Canary Deployment (Kubernetes)
```yaml
# Deploy canary at 10% traffic
- name: Deploy canary
  run: |
    kubectl set image deployment/app canary=$IMAGE --record
    kubectl scale deployment/app-canary --replicas=1
- name: Canary health check
  run: ./scripts/canary-health-check.sh
- name: Promote canary
  run: |
    kubectl set image deployment/app app=$IMAGE --record
    kubectl scale deployment/app-canary --replicas=0
```

### Rollback Strategy
Every deployment step must have a defined rollback:
- **Kubernetes:** `kubectl rollout undo deployment/app`
- **Docker Compose:** Revert to previous image tag
- **Serverless:** Redeploy previous build
- **Static:** S3 versioning / rollback to previous prefix

## Security Mandates

1. **Never log secrets.** Uses `>> $GITHUB_STEP_SUMMARY` for public output.
2. **Pin actions to SHA.** Not tags. `uses: actions/checkout@11bd719...` not `@v4`.
3. **Limit token permissions.** Default to `contents: read`.
4. **Artifact signing.** Sign Docker images with Cosign if possible.
5. **Dependency review.** Always include a dependency audit step.
6. **Secret scanning.** Include a secret scanning step (trufflehog, gitleaks).
7. **OIDC for cloud.** Use OIDC instead of long-lived cloud credentials where supported.

## Output Format

Generate the complete pipeline configuration file followed by:

### Pipeline Diagram (Mermaid)
```mermaid
graph LR
    A[Push/PR] --> B[Lint]
    B --> C[Test]
    C --> D[Build]
    D --> E[Security Scan]
    E --> F[Deploy Staging]
    F --> G[Smoke Test]
    G --> H[Deploy Production]
```

### README Section
A markdown section to add to the project README explaining:
- Pipeline overview
- How to view runs
- What each stage does
- How to add secrets
- Where to find artifacts

### Secrets Checklist
A checklist of all secrets the user needs to configure, with clear names and descriptions.

## Common Stack Templates

### Node.js + Docker + Kubernetes (GitHub Actions)
Generate: lint (ESLint) → test (Jest, coverage >= 80%) → build (Docker, multi-stage) → security (Trivy, npm audit) → deploy-staging (kubectl) → smoke-test → deploy-prod (canary + promote)

### Python + Docker + AWS ECS (GitHub Actions)
Generate: lint (ruff) → test (pytest, coverage) → build (Docker, ECR push) → security (bandit, pip-audit) → deploy-staging (ECS update) → deploy-prod (ECS blue/green)

### Go + Kubernetes (GitLab CI)
Generate: lint (golangci-lint) → test (go test -race) → build (ko or Docker) → security (govulncheck, trivy) → deploy-staging → deploy-prod

### Static Site (GitHub Actions + GitHub Pages / Vercel)
Generate: lint (ESLint/Prettier) → test → build → deploy (platform-specific)

## Edge Cases

- **Monorepo:** Use path filters to trigger only relevant pipelines.
  ```yaml
  on:
    push:
      paths:
        - 'services/api/**'
  ```
- **Multi-language:** Generate parallel matrix jobs per language.
- **Database migrations:** Always include a migration step before deploy, with rollback.
- **Infrastructure-as-Code:** If Terraform/Pulumi detected, add plan → apply stages with approval gates.
- **No tests found:** Add a placeholder step and warn the user to add tests.

## Validation Checklist

Before presenting the pipeline, verify:
- [ ] All secrets referenced via platform secret store
- [ ] Actions pinned to commit SHAs
- [ ] Caching configured for language/framework
- [ ] Coverage threshold set
- [ ] Rollback strategy defined per environment
- [ ] Notifications configured (failures at minimum)
- [ ] No hardcoded credentials
- [ ] Environment protection rules for production
- [ ] OIDC used for cloud auth where possible
- [ ] Docker layer caching enabled

## References

See `references/` for provider-specific best practices and common anti-patterns.