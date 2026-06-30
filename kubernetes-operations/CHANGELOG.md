# Changelog

All notable changes to the kubernetes-operations skill.

## [1.0.0] — 2026-06-18

### Initial Release

Materially improved from [KubeShark](https://github.com/LukasNiessen/kubernetes-skill) (LukasNiessen/kubernetes-skill), the #1 Kubernetes skill in the ecosystem.

#### Expansions Over KubeShark

| Dimension | KubeShark | kubernetes-operations |
|-----------|-----------|----------------------|
| Failure Modes | 6 | **8** (added FM-7 GitOps Divergence, FM-8 Multi-Cloud Skew) |
| Helm Support | Basic | **Full** — chart structure, values patterns, dependency management, multi-environment deployment |
| GitOps | Mentioned | **Deep** — Flux CD, ArgoCD, drift detection patterns |
| Cost Optimization | None | **Full** — right-sizing, spot instances, cluster autoscaler |
| Secret Management | Basic | **Full** — ESO, Sealed Secrets, Vault decision tree |
| Multi-Cloud | EKS-focused | **EKS + GKE + AKS + OpenShift** — provider-specific patterns, taints/tolerations |
| Observability | None | **Full** — Prometheus, structured logging, OpenTelemetry, golden signals |
| Output Contract | None | **Mandatory** — assumptions, tradeoffs, rollback for every response |
| Platform Support | Claude Code | **8 platforms**: claude-code, codex, cursor, gemini-cli, openclaw, copilot, windsurf, opencode |
| Eval Cases | 0 | **7** (5 triggers + 2 near-miss negatives) |
| Reference Docs | 0 | **3** detailed references (security, failure modes, Helm patterns) |
| Validation Scripts | 0 | **2** scripts (manifest validation, security scanning) |

#### Feature Inventory

- **7-Step Failure-Mode Prevention Workflow:** Context → Diagnose → Reference → Design → Validate → Output → Rollback
- **8 Failure Modes with Detection & Remediation:** Insecure Workloads, Resource Starvation, Network Exposure, Privilege Sprawl, Fragile Rollouts, API Drift, GitOps Divergence, Multi-Cloud Skew
- **Security Compliance:** PSS (restricted), OWASP K8s Top 10, NSA/CISA, CIS benchmarks, RBAC least-privilege
- **DO/DON'T Examples:** Rich code snippets showing correct and incorrect patterns
- **Production Checklist:** Minimal production-ready deployment checklist
- **Troubleshooting Quick Commands:** Common diagnostic commands for pod, resource, RBAC, network, and drift issues
- **Trigger Matching:** 30+ kata phrases for reliable agent routing
- **Near-Miss Negatives:** 4 exclusion patterns to prevent misrouting