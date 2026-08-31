# Changelog

All notable changes to the Infrastructure as Code Guardian skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-09

### Added

- **SKILL.md** — Complete universal IaC agent skill definition with:
  - YAML frontmatter with SEO-optimized description, platforms, and tags
  - 15 positive activation triggers and 3 near-miss negatives
  - Tool selection decision tree covering Terraform, Pulumi, CloudFormation, Ansible, Bicep, Crossplane, and OpenTofu
  - Quick comparison matrix across 6 dimensions
  - Per-tool authoring guidelines with code examples (Terraform HCL, Pulumi TypeScript/Python, CloudFormation YAML, Ansible YAML, Bicep)
  - Comprehensive security hardening checklist (6 categories, 40+ items)
  - State management best practices (10 rules for Terraform, 5 for Pulumi, 4 for CloudFormation)
  - Drift detection workflow with CI/CD integration and remediation patterns
  - Migration patterns (CloudFormation → Terraform, Terraform → Pulumi, ARM → Bicep)
  - Quick Reference with 30+ one-liner commands
  - 10 common pitfalls with detection and remediation
  - SEO metadata section with primary/secondary keywords and search intent alignment

- **scripts/validate-iac.sh** — Auto-detection IaC validation script:
  - Supports Terraform, Pulumi, CloudFormation, Ansible, Bicep
  - JSON output mode for CI/CD pipelines
  - Fail-fast option for quick feedback
  - Color-coded console output

- **scripts/security-scan-iac.sh** — Multi-tool security scanner:
  - Integrates tfsec, checkov, trivy, cfn-nag, ansible-lint
  - Universal secret scanning (gitleaks, trufflehog, grep fallback)
  - Compliance framework filtering (CIS, SOC2, PCI-DSS, HIPAA, ISO27001)
  - Severity-based failure thresholds (CRITICAL/HIGH/MEDIUM/LOW)
  - SARIF/JSON output

- **scripts/drift-check.sh** — Cross-tool drift detection:
  - Terraform plan with detailed exit code
  - Pulumi refresh with diff
  - CloudFormation stack drift detection + resource-level analysis
  - Bicep what-if deployment
  - Ansible --check --diff for configuration drift
  - Slack webhook alerting
  - Optional auto-remediation mode

- **references/iac-patterns.md** — Reusable IaC patterns:
  - Module composition (flat vs. layered vs. domain-oriented)
  - Environment stratification with ephemeral feature branch environments
  - Remote state architecture with access control
  - GitOps CI/CD pipeline with directory-based apply
  - Multi-cloud abstraction patterns
  - Cost optimization (tagging, auto-scaling, lifecycle policies)
  - Disaster recovery (multi-region active-passive)
  - Zero-downtime deployment (blue-green, rolling updates, DB migrations)

- **references/security-hardening.md** — Security checklist and patterns:
  - IAM least privilege with permission boundaries and SCPs
  - Secret management hierarchy (Tier 0–4) with vault integration
  - Encryption at rest per-service requirements table
  - Network defense-in-depth layering with security group templates
  - Logging and audit trail configuration
  - SOC 2 and CIS AWS Foundations benchmark mappings
  - Automated enforcement (pre-commit hooks, CI/CD gates, Pulumi policy packs)
  - Secret rotation schedule and strategy
  - Incident response readiness (infrastructure freeze via SCP, audit log correlation)

- **references/cloud-provider-matrix.md** — AWS/Azure/GCP feature parity:
  - Compute, containers, serverless, storage, databases, networking
  - Security & identity, monitoring & observability, CI/CD
  - Multi-cloud resource mapping table for common workloads
  - VPC architecture comparison (AWS, Azure, GCP)
  - Migration decision matrix
  - Cross-cloud resource patterns with Terraform code examples

- **evals/evals.json** — 7 evaluation cases:
  - 5 positive triggers covering Terraform authoring, Pulumi security audit, drift detection, CloudFormation migration, tool selection
  - 2 near-miss negatives (Docker deployment, SSH troubleshooting)

### Infrastructure

- MIT License
- Complete directory structure with scripts/, references/, evals/
- All shell scripts are executable and include comprehensive usage documentation
