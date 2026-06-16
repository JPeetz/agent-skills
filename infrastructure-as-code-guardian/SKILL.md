---
name: infrastructure-as-code-guardian
description: >
  Universal Infrastructure as Code (IaC) agent skill for authoring, securing,
  and managing cloud infrastructure across Terraform, Pulumi, CloudFormation,
  Ansible, and Bicep. Provides cross-tool security hardening, state management
  best practices, cost optimization, drift detection, and CI/CD integration.
  Covers AWS, Azure, GCP, and hybrid-cloud environments with a unified workflow
  that spans the full IaC lifecycle—from greenfield module authoring through
  production hardening audits to multi-tool migration planning. Designed for
  DevOps engineers who switch between IaC tools daily: includes a decision
  tree for tool selection, per-tool authoring guidelines (HCL patterns, Pulumi
  TypeScript/Python idioms, CloudFormation YAML conventions, Ansible playbook
  structure, Bicep DSL tips), security checklist aligned to CIS benchmarks and
  SOC 2, drift detection workflows that catch configuration skew before it
  causes outages, and cost-optimization guardrails built into the authoring
  phase. The skill bridges the gap left by single-tool IaC skills—HashiCorp's
  focus is Terraform-only, Pulumi's official guidance stays within its own
  ecosystem—by providing a tool-agnostic framework that treats IaC as a
  discipline, not a product silo.
version: 1.0.0
author: Skill Foundry
platforms:
  - terraform
  - pulumi
  - cloudformation
  - ansible
  - bicep
  - aws
  - azure
  - gcp
  - kubernetes
  - crossplane
  - opentofu
tags:
  - infrastructure-as-code
  - iac
  - terraform
  - pulumi
  - cloudformation
  - ansible
  - bicep
  - security-hardening
  - drift-detection
  - state-management
  - cost-optimization
  - migration
  - cicd
  - aws
  - azure
  - gcp
  - devops
  - sre
  - platform-engineering
  - cis-benchmark
  - compliance
  - opentofu
---

# Infrastructure as Code Guardian

Universal IaC agent skill—author, secure, manage, and migrate infrastructure across Terraform, Pulumi, CloudFormation, Ansible, and Bicep.

---

## Activation Triggers

### Positive Triggers (activate on these)

1. "Write a Terraform module for…"
2. "Secure this IaC codebase" / "Harden my infra config"
3. "Check for drift in staging" / "Run a drift detection workflow"
4. "Migrate from CloudFormation to Terraform" (or any cross-tool migration)
5. "Add cost optimization tags to my IaC" / "Reduce cloud costs via IaC"
6. "Set up remote state for this project" / "Fix state locking"
7. "Generate a least-privilege IAM policy from this Terraform"
8. "Review this Pulumi stack for security issues" / "IaC security audit"
9. "Create an Ansible playbook from this existing infra"
10. "Write a Bicep module and convert to ARM" / "Author Bicep for Azure"
11. "Set up GitOps pipeline for infrastructure" / "CI/CD for IaC"
12. "This Terraform plan shows drift—help me reconcile" / "Infra state is out of sync"
13. "What IaC tool should I use for…" / "Pulumi vs Terraform for this project"
14. "Convert Kubernetes YAML manifests to Crossplane compositions"
15. "Generate compliance report for my infrastructure" / "CIS benchmark for IaC"

### Near-Miss Negatives (do NOT activate)

1. "Deploy this Docker container to production" — operational deploy, not IaC authoring
2. "Write a Python script to list S3 buckets" — script authoring, not infrastructure definition
3. "How do I SSH into this EC2 instance?" — operational troubleshooting, not IaC

### Ambiguous Cases (ask clarifying question)

- "Fix my cloud" → ask: "Are you looking to fix IaC definitions, or troubleshoot a running deployment?"
- "Setup AWS" → ask: "Do you want to author infrastructure code, or configure an AWS account manually?"

---

## Tool Selection Decision Tree

When choosing an IaC tool, evaluate the following in order. Present your reasoning explicitly.

```
START
 │
 ├─ Is managed-by-CSP-only acceptable? (no external state)
 │   ├─ YES, AWS-only          → CloudFormation / AWS CDK
 │   ├─ YES, Azure-only         → Bicep / ARM
 │   └─ NO (multi-cloud needed) → Continue ▼
 │
 ├─ Is the team primarily developers comfortable with
 │  general-purpose languages?
 │   ├─ YES → Pulumi (TypeScript, Python, Go, C#)
 │   └─ NO  → Continue ▼
 │
 ├─ Is this a greenfield project with strong community
 │  / module ecosystem needs?
 │   ├─ YES → Terraform (HCL) or OpenTofu
 │   └─ NO  → Continue ▼
 │
 ├─ Is configuration management the primary goal
 │  (installing packages, managing config files on VMs)?
 │   ├─ YES                       → Ansible
 │   └─ NO (declarative infra)    → Continue ▼
 │
 ├─ Are you operating inside a Kubernetes-native
 │  platform team?
 │   ├─ YES → Crossplane
 │   └─ NO  → Terraform (default fallback with largest ecosystem)
 │
 └─ OUTCOME: Recommend tool with reasoning.
    Always note: Terraform (76% market share) is the safest default.
    Pulumi is the fastest-growing (45% YoY) and best for dev-centric teams.
```

### Quick Comparison Matrix

| Criterion              | Terraform   | Pulumi       | CFn         | Bicep       | Ansible     |
|------------------------|-------------|--------------|-------------|-------------|-------------|
| **Language**           | HCL         | TS/Py/Go/C#  | YAML/JSON   | Bicep DSL   | YAML        |
| **State Management**   | Explicit    | Explicit     | Implicit    | Implicit    | N/A         |
| **Multi-Cloud**        | Yes         | Yes          | AWS only    | Azure only  | Yes         |
| **Ecosystem Size**     | Largest     | Growing fast | Large (AWS) | Medium      | Large       |
| **Learning Curve**     | Moderate    | Low (for devs)| Steep       | Low         | Low         |
| **Drift Detection**    | plan        | refresh      | Drift Detect| what-if     | check mode  |
| **Secret Handling**    | Vault/sops  | ESC/Vault    | KMS/Secrets | Key Vault   | Vault/sops  |
| **CI/CD Integration**  | Excellent   | Excellent    | Good        | Good        | Good        |

---

## Authoring Guidelines per Tool

### Terraform (HCL)

**Structure:**
```hcl
# Standard module layout
modules/
  networking/
    main.tf        # Primary resources
    variables.tf   # Input variables with types + descriptions
    outputs.tf     # Exported values
    versions.tf    # Provider + Terraform version constraints
    README.md      # Usage, examples, API surface
```

**HCL Patterns to Enforce:**
- Always pin provider versions in `versions.tf` with `>=` lower bound and `~>` pessimistic constraint
- Use `for_each` over `count` for resource iteration (deterministic keys prevent destroy/recreate cascades)
- Prefix all outputs with the module name to avoid collisions: `output "vpc_id"` → `output "networking_vpc_id"`
- Use `dynamic` blocks sparingly—prefer explicit blocks for readability
- Every variable must have `type` and `description`; sensitive vars must have `sensitive = true`
- Use `terraform-docs` to generate README from variable/output metadata
- Apply `lifecycle { prevent_destroy = true }` on stateful resources (databases, storage buckets)
- Use `lifecycle { ignore_changes = [tags["LastModified"]] }` for externally-managed tag mutations

**State Management:**
```hcl
# Remote state with locking (S3 + DynamoDB example)
terraform {
  backend "s3" {
    bucket         = "myorg-terraform-state-${var.environment}"
    key            = "networking/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
```

**Anti-Patterns to Flag:**
- `terraform plan | sh` (blind apply) → recommend `terraform apply` with review
- Hardcoded ARNs → use `data` sources or `var.*` references
- Missing `required_providers` block → enforce in `versions.tf`
- Embedding secrets in `.tf` files → recommend Vault/sops/ESC

---

### Pulumi (TypeScript / Python)

**TypeScript Patterns:**
```typescript
// Component Resource pattern (Pulumi best practice)
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface VpcComponentArgs {
  cidrBlock: string;
  enableDnsHostnames?: boolean;
  tags?: pulumi.Input<{ [key: string]: pulumi.Input<string> }>;
}

export class VpcComponent extends pulumi.ComponentResource {
  public readonly vpc: aws.ec2.Vpc;
  public readonly publicSubnets: aws.ec2.Subnet[];
  public readonly privateSubnets: aws.ec2.Subnet[];

  constructor(name: string, args: VpcComponentArgs, opts?: pulumi.ComponentResourceOptions) {
    super("myorg:networking:Vpc", name, {}, opts);

    this.vpc = new aws.ec2.Vpc(`${name}-vpc`, {
      cidrBlock: args.cidrBlock,
      enableDnsHostnames: args.enableDnsHostnames ?? true,
      tags: { ...args.tags, Name: `${name}-vpc` },
    }, { parent: this });

    // Register outputs
    this.registerOutputs({
      vpc: this.vpc,
      publicSubnets: this.publicSubnets,
    });
  }
}
```

**Python Patterns:**
```python
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_aws import ec2

class VpcComponent(ComponentResource):
    def __init__(self, name: str, args: VpcComponentArgs, opts: ResourceOptions = None):
        super().__init__("myorg:networking:Vpc", name, {}, opts)

        self.vpc = ec2.Vpc(
            f"{name}-vpc",
            cidr_block=args.cidr_block,
            enable_dns_hostnames=True,
            tags={"Name": f"{name}-vpc"},
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({"vpc": self.vpc})
```

**Pulumi-Specific Guardrails:**
- Use `ComponentResource` for all reusable abstractions (never raw `new Resource()` in stacks)
- Stack references for cross-stack data: `new pulumi.StackReference("org/project/stack")`
- Use `pulumi.output` and `apply()` for computed values; avoid `Promise.all` anti-patterns
- Enable Pulumi ESC for secret management; never hardcode secrets in stack configs
- Use `pulumi policy pack` for organization-wide compliance (e.g., `--policy-pack awsguard`)
- Handle `ResourceOptions` propagation: `protect`, `deleteBeforeReplace`, `ignoreChanges`

---

### CloudFormation (YAML)

**Best-Practice Structure:**
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: >
  Production VPC stack with public/private subnets, NAT gateways,
  and VPC endpoints for S3 and DynamoDB. (SOC 2 compliant)

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Description: Deployment environment name

  VpcCidr:
    Type: String
    Default: "10.0.0.0/16"
    AllowedPattern: "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\\/([0-9]|[1-2][0-9]|3[0-2]))$"

Mappings:
  SubnetConfig:
    us-east-1:
      PublicA: "10.0.1.0/24"
      PrivateA: "10.0.10.0/24"

Conditions:
  IsProduction: !Equals [!Ref Environment, "prod"]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VpcId"
```

**CloudFormation Rules:**
- Always use `!Sub` over `Fn::Join` for readability
- Export stack outputs with unique names: `${AWS::StackName}-ResourceId`
- Use `Mappings` for region-specific values; `Conditions` for environment branching
- Enable `TerminationProtection` on production stacks
- Use `AWS::CloudFormation::StackSet` for multi-region/multi-account deployments
- Run `cfn-lint` and `cfn-nag` in pre-commit; integrate into CI pipeline
- Avoid embedding secrets in Parameters—use `AWS::SecretsManager::Secret` or `resolve:ssm-secure:/path`

---

### Ansible

**Playbook Structure:**
```yaml
---
# site.yml — Entry-point playbook
- name: Configure production web servers
  hosts: webservers
  become: true
  vars_files:
    - vars/production.yml
  roles:
    - common
    - nginx
    - node_exporter
  pre_tasks:
    - name: Verify minimum disk space
      ansible.builtin.assert:
        that: ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first > 1073741824
        fail_msg: "Insufficient disk space on / "
  post_tasks:
    - name: Send deployment notification
      ansible.builtin.uri:
        url: "{{ slack_webhook_url }}"
        method: POST
        body: '{"text": "Deployment complete on {{ inventory_hostname }}"}'
```

**Ansible IaC Patterns:**
- Use `ansible.builtin.*` FQCNs for all modules (future-proof against collections changes)
- Separate inventory by environment: `inventories/production/hosts.yml`
- Encrypt secrets with `ansible-vault`; never store plaintext in vars files
- Use `check_mode: true` for dry-run validation before production applies
- `--diff` flag for configuration change previews (acts as drift detection)
- Idempotency is mandatory—every task must produce the same result on repeat runs
- Use `ansible-lint` with production ruleset; integrate into pre-commit hooks

---

### Bicep

**Module Patterns:**
```bicep
// modules/network.bicep
param location string = resourceGroup().location
param vnetName string
param addressPrefix string = '10.0.0.0/16'
param subnetPrefixes array = ['10.0.1.0/24', '10.0.2.0/24']
param tags object = {}

@description('Tags to apply to all resources, merged with env tags')
param environmentTags object

var effectiveTags = union(tags, environmentTags)

resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: vnetName
  location: location
  tags: effectiveTags
  properties: {
    addressSpace: {
      addressPrefixes: [addressPrefix]
    }
    subnets: [for (prefix, i) in subnetPrefixes: {
      name: 'subnet-${i}'
      properties: {
        addressPrefix: prefix
      }
    }]
  }
}

output vnetId string = vnet.id
output vnetNameOut string = vnet.name
```

**Bicep Best Practices:**
- Use `@description()` decorator on all params and outputs
- Use Bicep parameter files (`.bicepparam`) for environment-specific values
- Run `bicep build` before deployment to catch compile-time errors
- Use `what-if` deployment for change preview (Azure's equivalent of `terraform plan`)
- Pin API versions explicitly; avoid `@latest`-style references in production
- Use modules with semantic version references via module registries (`br:*`)
- Use `existing` keyword for referencing externally-managed resources

---

## Security Hardening Checklist

Execute this checklist on every IaC codebase review. Flag violations with severity and fix suggestions.

### 1. Least Privilege IAM (CRITICAL)

- [ ] No `*` in Action arrays—use explicit action lists
- [ ] No `*` in Resource arrays (except where unavoidable like CloudWatch Logs)
- [ ] No `"Effect": "Allow"` combined with `"Resource": "*"` and `"Action": "*"` (triple-star anti-pattern)
- [ ] S3 bucket policies have explicit `Principal`; no `"Principal": {"AWS": "*"}` unless intentional public access
- [ ] IAM Roles use `AssumeRolePolicyDocument` with least-privilege trust relationships
- [ ] IAM Policies follow the "250 IAM best practices" checklist: condition keys, source IP restriction, MFA enforcement

**Terraform Fix Example:**
```hcl
# BAD — triple-star anti-pattern
data "aws_iam_policy_document" "bad" {
  statement {
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]
  }
}

# GOOD — least privilege with conditions
data "aws_iam_policy_document" "good" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = ["${aws_s3_bucket.app.arn}/uploads/*"]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}
```

### 2. Secret Management (CRITICAL)

- [ ] No secrets in `.tf`, `.ts`, `.yaml`, `.bicep` files (check with `gitleaks` or `trufflehog`)
- [ ] Database passwords, API keys, private keys stored in: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, Pulumi ESC
- [ ] State files encrypted at rest (S3 SSE, Azure storage encryption, GCS CMEK)
- [ ] State files encrypted in transit (TLS 1.2+)
- [ ] `sensitive = true` on all Terraform output values containing secrets
- [ ] Ansible vault encrypts all `vars/secrets.yml` files
- [ ] Pulumi stack config secrets marked with `--secret` flag

**Detection Script:**
```bash
# Quick secret-in-code scan
gitleaks detect --source . --no-git --verbose 2>/dev/null || \
  trufflehog filesystem . --no-update --fail 2>/dev/null
```

### 3. Encryption (HIGH)

- [ ] S3 buckets: SSE-S3 minimum, SSE-KMS recommended; `block_public_access` enabled
- [ ] RDS/Database: storage_encrypted = true; encryption at rest enabled
- [ ] EBS volumes: `encrypted = true` by default (enforce via SCP or AWS Config rule)
- [ ] EKS/Container: secrets encryption with KMS; envelope encryption on etcd
- [ ] ELB/ALB: HTTPS listeners only; HTTP → HTTPS redirect; minimum TLS 1.2
- [ ] CloudFront: `viewer_protocol_policy = "redirect-http-to-https"`
- [ ] KMS key rotation enabled (automatic annual rotation or custom schedule)

### 4. Network Isolation (HIGH)

- [ ] Security groups: no `0.0.0.0/0` ingress unless intentional (e.g., public ALB)
- [ ] Security groups: restricted egress to necessary CIDRs/prefix-lists only
- [ ] NACLs: stateless rules as defense-in-depth layer
- [ ] Private subnets: no direct internet route; NAT Gateway for outbound-only
- [ ] VPC endpoints for AWS services (S3, DynamoDB) to avoid internet traversal
- [ ] WAF attached to all public-facing ALBs and CloudFront distributions
- [ ] Network firewall or equivalent for egress filtering in production

### 5. Logging & Monitoring (MEDIUM)

- [ ] CloudTrail enabled in all regions with log file validation
- [ ] VPC Flow Logs enabled on all VPCs
- [ ] S3 access logs enabled on sensitive buckets
- [ ] Load balancer access logs enabled
- [ ] GuardDuty enabled in all regions
- [ ] Security Hub enabled with CIS benchmark standard
- [ ] Config rules for continuous compliance monitoring

### 6. Cost Optimization Guardrails (MEDIUM)

- [ ] Resource tagging strategy enforced: `Environment`, `Owner`, `CostCenter`, `Project`
- [ ] Auto-scaling configured with min/max bounds (not static instance counts)
- [ ] Reserved Instances / Savings Plans for predictable workloads
- [ ] S3 lifecycle policies: transition to IA/Glacier, expire old versions
- [ ] NAT Gateway count minimized (use single-AZ for dev, multi-AZ for prod)
- [ ] RDS: stop-dev-instances automation for non-production after hours
- [ ] Lambda: memory and timeout tuned (not default 128MB/3s for everything)

---

## State Management Best Practices

### Terraform / OpenTofu

1. **Remote State is Mandatory.** No local state files in production repos. Use S3 + DynamoDB (AWS), Azure Storage (Azure), GCS (GCP).
2. **State File Isolation.** One state file per environment (dev/staging/prod), per region, and per logical boundary (networking, compute, data).
3. **State Locking.** Always enable DynamoDB locks (AWS) or equivalent. Prevents concurrent applies that corrupt state.
4. **State Encryption.** Enable server-side encryption on state storage. `encrypt = true` in backend config.
5. **Workspace Strategy.** Use separate backends or directory separation. Avoid `terraform workspace` for long-lived environments—they share the same backend and credentials.
6. **State Access Control.** Restrict state bucket access to CI/CD service roles and senior engineers. No developer IAM users with direct state read/write.
7. **State Versioning.** Enable bucket versioning on state storage for rollback capability.
8. **State Import Hygiene.** `terraform import` should be followed immediately by cleanup of manual resource configs. Document every import in a migration log.
9. **State Refresh.** Run `terraform apply -refresh-only` before plan to reconcile external changes.
10. **Never Edit State Files.** Use `terraform state mv`, `terraform state rm`, `terraform state pull`—never edit JSON state manually.

### Pulumi

1. **Pulumi Cloud or Self-Managed Backend.** Pulumi Cloud (SaaS) is the default and recommended. For self-managed, use S3/Azure/GCS with the Pulumi service managing locking.
2. **Stack Configuration.** Separate stacks per environment. Use `pulumi config set --secret` for sensitive values.
3. **State Export.** `pulumi stack export` for backup; `pulumi stack import` for recovery.
4. **Resource Protection.** `protect: true` on stateful resources (RDS, DynamoDB) to prevent accidental deletion.
5. **State History.** Pulumi Cloud retains deployment history; self-managed backends use object versioning.

### CloudFormation

1. **Change Sets.** Always create a Change Set and review before executing. Never direct-update production stacks.
2. **Stack Policies.** Define stack policies that prevent updates/replacements of stateful resources during routine changes.
3. **Nested Stacks.** Use nested stacks for large deployments to stay within resource limits (500 resources per stack). Export shared outputs via `Fn::ImportValue`.
4. **StackSets.** For multi-account/multi-region: use StackSets with service-managed permissions.

### Cross-Cutting Rules

- **Never share state between tools.** A resource created by Terraform should not be managed by Pulumi in the same state.
- **State backup is non-negotiable.** Automate daily state file backups to a separate, immutable bucket.
- **State access audit.** Log all state file reads/writes. Alert on unexpected access patterns.

---

## Drift Detection Workflow

Drift = configuration in code ≠ actual infrastructure state. Drift causes outages, security gaps, and compliance failures.

### Standard Workflow

```
1. IDENTIFY
   ├─ Terraform:  terraform plan -detailed-exitcode
   ├─ Pulumi:     pulumi refresh --diff
   ├─ CFn:        aws cloudformation detect-stack-drift
   ├─ Bicep:      az deployment group what-if
   └─ Ansible:    ansible-playbook --check --diff site.yml

2. CLASSIFY
   ├─ EXPECTED DRIFT   (auto-scaling events, tag auto-updates)
   │   └─ Update code to match reality (terraform import / pulumi import)
   └─ UNEXPECTED DRIFT (manual console changes, security group widens)
       └─ Investigate audit logs → Reconcile or revert

3. RECONCILE
   ├─ Prefer code-as-truth:  update infrastructure to match code
   ├─ Import manual changes: terraform import / pulumi import / CFn resource import
   └─ Document exceptions:   lifecycle { ignore_changes = [...] }

4. PREVENT
   ├─ Restrict console access (break-glass only, with auto-revert)
   ├─ Run drift detection on schedule (hourly for prod, daily for staging)
   ├─ Alert on drift via CloudWatch/PagerDuty/Slack
   └─ Auto-remediate with AWS Config rules or OPA policies
```

### CI/CD Integration

```yaml
# GitHub Actions — Drift Check Job
drift-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: hashicorp/setup-terraform@v3
    - name: Terraform Plan (Drift Check)
      id: plan
      run: |
        terraform init -backend-config="key=${{ env.TF_STATE_KEY }}"
        terraform plan -detailed-exitcode -out=tfplan
      continue-on-error: true
    - name: Alert on Drift
      if: steps.plan.outcome == 'failure'
      uses: slackapi/slack-github-action@v2
      with:
        payload: '{"text": "🚨 Drift detected in ${{ github.repository }} — ${{ env.ENVIRONMENT }}"}'
```

### Drift Remediation Patterns

| Drift Type                  | Action                                            |
|----------------------------|---------------------------------------------------|
| Manual SG rule addition    | Revert manually; audit CloudTrail; enforce SCP    |
| Auto-scaling group change  | Update `desired_count` in IaC to match            |
| Tag mutation by external tool | Add `lifecycle { ignore_changes = [tags] }`    |
| IAM policy widened         | Immediate revert; security incident response       |
| RDS instance type changed  | Update IaC to match; verify change window approval |
| S3 bucket policy changed   | Revert; enable `block_public_access`; alert        |

---

## Migration Patterns (Cross-Tool)

### CloudFormation → Terraform

1. Use `terraform import` with resource mapping:
   ```bash
   terraform import aws_vpc.main vpc-0a1b2c3d4e5f67890
   ```
2. Alternatively: `former2` (ex-cloudformer) → generates Terraform/AWS CDK from existing infra
3. Post-import: `terraform plan` to verify no diffs; then remove CloudFormation stack after confirming resources are imported (use `DeletionPolicy: Retain` during transition)

### Terraform → Pulumi

1. Use `pulumi import` with Terraform state:
   ```bash
   pulumi import --from terraform terraform.tfstate
   ```
2. Use `tf2pulumi` to convert HCL to TypeScript/Python: `tf2pulumi ./modules/*.tf`
3. Validate with `pulumi preview` before going live

### ARM → Bicep

1. `bicep decompile` for automated conversion: `az bicep decompile --file template.json`
2. Manual review required—Bicep decompilation is not lossless for complex templates

---

## Quick Reference

### Terraform One-Liners

```bash
terraform fmt -recursive -diff              # Format all .tf files, show diffs
terraform validate                           # Syntax check
terraform plan -out=tfplan                   # Generate plan file
terraform apply tfplan                       # Apply from plan (safe)
terraform plan -detailed-exitcode            # Returns 2 if drift exists
terraform state list                         # List all managed resources
terraform state rm resource.addr             # Stop managing (don't destroy)
terraform import resource.addr resource-id   # Adopt existing resource
terraform output -json                       # Machine-readable outputs
terraform console                            # Interactive REPL
terraform graph | dot -Tpng > graph.png      # Dependency visualization
```

### Pulumi One-Liners

```bash
pulumi preview --json                         # Machine-readable plan
pulumi up --yes --skip-preview                # Quick apply (with caution)
pulumi refresh --diff                         # Detect drift
pulumi stack export --file state.json         # Backup state
pulumi config set aws:region us-east-1        # Set config
pulumi config set --secret dbPassword         # Set secret
pulumi import --from terraform state.tfstate  # Migrate from Terraform
pulumi policy pack                            # Generate policy pack skeleton
```

### CloudFormation One-Liners

```bash
aws cloudformation validate-template --template-body file://template.yaml
aws cloudformation create-change-set --stack-name prod --change-set-name review-me
aws cloudformation detect-stack-drift --stack-name prod
aws cloudformation describe-stack-resource-drifts --stack-name prod
cfn-lint template.yaml                        # Third-party linter
cfn_nag_scan --input-path template.yaml       # Security scan
```

### Security Scanning One-Liners

```bash
# Terraform
tfsec .                                       # Terraform security scanner
checkov -d .                                  # Policy-as-code (any IaC tool)
trivy config .                                # Misconfiguration scanner

# CloudFormation
cfn_nag_scan --input-path template.yaml

# Ansible
ansible-lint site.yml

# Bicep
az bicep lint --file main.bicep

# Universal secret scanning
gitleaks detect --source . --no-git
trufflehog filesystem . --no-update
```

---

## Common Pitfalls

### 1. Hardcoded Secrets (CRITICAL — #1 cause of security incidents)

**Symptoms:** passwords, API keys, private keys in `.tf`, `.ts`, `.yaml` files.
**Fix:** Use Vault dynamic secrets, AWS Secrets Manager, Pulumi ESC, or Azure Key Vault with data-source lookups.
**Detection:** `gitleaks detect --source . --verbose`

### 2. Overly Permissive IAM (CRITICAL)

**Symptoms:** `"Action": "*"`, `"Resource": "*"` in IAM policy documents.
**Fix:** Explicit action lists; resource ARN constraints; IAM Access Analyzer validation.
**Tool:** `checkov -d . --check CKV_AWS_*` for Terraform; `cfn_nag_scan` for CloudFormation.

### 3. Missing Lifecycle Rules (HIGH)

**Symptoms:** Database destroyed during routine update because `prevent_destroy` was absent.
**Fix:** Every stateful resource needs:
```hcl
lifecycle {
  prevent_destroy = true
}
```

### 4. No Remote State (HIGH)

**Symptoms:** `terraform.tfstate` in git repository; state file conflicts between teammates.
**Fix:** Configure remote backend with locking before the first `terraform apply`.

### 5. State-Only Changes Without Infrastructure Updates (MEDIUM)

**Symptoms:** `terraform state rm` used to "fix" issues instead of updating code.
**Fix:** Always update `.tf` files first; only use state manipulation as an emergency bridge.

### 6. Unpinned Provider Versions (MEDIUM)

**Symptoms:** CI pipeline breaks because provider released a breaking change.
**Fix:** Pin both Terraform core and provider versions with `required_providers` blocks.

### 7. Monolithic State Files (MEDIUM)

**Symptoms:** Plan times >10 minutes; blast radius covers entire infrastructure.
**Fix:** Split state by environment, region, and logical domain. Use `terraform output` and data sources for cross-state references.

### 8. Ignoring Drift (MEDIUM)

**Symptoms:** `terraform plan` shows unexpected changes long after initial apply.
**Fix:** Schedule drift checks; restrict console access; use SCPs to prevent manual modifications.

### 9. Missing Resource Tagging (LOW — Cost Impact: HIGH)

**Symptoms:** Untaggable resources lead to untracked cloud spend.
**Fix:** Enforce tags with Terraform `default_tags` on provider block or Pulumi `transformations`. Cost allocation tags in AWS Billing.

### 10. Inappropriate `count` Usage (LOW)

**Symptoms:** Changing a list element reorders resources and triggers destroy/recreate.
**Fix:** Use `for_each` with a map or `toset()`—deterministic keys prevent cascading changes.

---

## SEO Metadata

### Primary Keywords
- infrastructure as code
- IaC security hardening
- Terraform best practices
- Pulumi patterns
- drift detection IaC
- IaC state management
- CloudFormation to Terraform migration
- IaC CI/CD pipeline

### Secondary Keywords
- Bicep module patterns
- Ansible playbook structure
- IaC cost optimization
- IaC compliance checklist
- CIS benchmark IaC
- least privilege IAM IaC
- OpenTofu migration
- Crossplane compositions

### Search Intent Alignment
- **Informational:** "What is the best IaC tool for multi-cloud?" → Decision Tree section
- **Tutorial:** "How to secure Terraform code" → Security Hardening Checklist
- **Comparative:** "Terraform vs Pulumi vs CloudFormation" → Comparison Matrix
- **Troubleshooting:** "How to fix Terraform drift" → Drift Detection Workflow
- **Migration:** "How to migrate CloudFormation to Terraform" → Migration Patterns
