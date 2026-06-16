# IaC Security Hardening — Comprehensive Checklist & Patterns

> Part of the Infrastructure as Code Guardian skill. Covers security hardening for infrastructure defined as code, aligned to CIS benchmarks, SOC 2, and industry best practices.

---

## Table of Contents

1. [IAM Least Privilege](#iam-least-privilege)
2. [Secret Management](#secret-management)
3. [Encryption Standards](#encryption-standards)
4. [Network Security](#network-security)
5. [Logging & Audit Trail](#logging--audit-trail)
6. [Compliance Frameworks Mapping](#compliance-frameworks-mapping)
7. [Automated Enforcement](#automated-enforcement)
8. [Secret Rotation Strategy](#secret-rotation-strategy)
9. [Incident Response Readiness](#incident-response-readiness)

---

## IAM Least Privilege

### The Principle

Every IAM policy must grant the **minimum permissions required** for a specific task. No wildcard actions. No wildcard resources. Explicit conditions whenever possible.

### Terraform — Least Privilege IAM

```hcl
# PREFERRED: Policy generated from actual usage via IAM Access Analyzer
data "aws_iam_policy_document" "app_role" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.app_uploads.arn,
      "${aws_s3_bucket.app_uploads.arn}/*",
    ]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
    ]
    resources = [aws_dynamodb_table.app.arn]
    condition {
      test     = "ForAllValues:StringEquals"
      variable = "dynamodb:LeadingKeys"
      values   = ["${var.environment}-*"]
    }
  }
}

# ANTI-PATTERN — Never do this:
# data "aws_iam_policy_document" "bad" {
#   statement {
#     effect    = "Allow"
#     actions   = ["*"]
#     resources = ["*"]
#   }
# }
```

### IAM Boundaries (Permission Boundaries + SCPs)

```hcl
# Permission boundary — caps what a role can ever do
resource "aws_iam_role" "developer" {
  name               = "developer-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  permissions_boundary = aws_iam_policy.dev_boundary.arn
}

# Developer boundary: limit to non-prod, deny IAM changes
data "aws_iam_policy_document" "dev_boundary" {
  statement {
    effect    = "Deny"
    actions   = ["iam:*", "organizations:*", "billing:*"]
    resources = ["*"]
  }
  statement {
    effect    = "Deny"
    actions   = ["*"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Environment"
      values   = ["prod"]
    }
  }
}
```

### Service Control Policies (SCP)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyLeavingOrg",
      "Effect": "Deny",
      "Action": ["organizations:LeaveOrganization"],
      "Resource": ["*"]
    },
    {
      "Sid": "DenyRootActivity",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        }
      }
    }
  ]
}
```

### Pulumi — IAM Patterns

```typescript
import * as aws from "@pulumi/aws";

// Attach boundary to role at creation time
const appRole = new aws.iam.Role("app", {
  assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({
    Service: "ecs-tasks.amazonaws.com",
  }),
  permissionsBoundary: boundaryPolicy.arn,
  tags: { Environment: environment, ManagedBy: "pulumi" },
});

// Use policy generator for least privilege
const appPolicy = new aws.iam.Policy("app-policy", {
  policy: aws.iam.getPolicyDocument({
    statements: [{
      effect: "Allow",
      actions: ["s3:GetObject", "s3:PutObject"],
      resources: [`${bucket.arn}/*`],
      conditions: [{
        test: "Bool",
        variable: "aws:SecureTransport",
        values: ["true"],
      }],
    }],
  }).then(doc => doc.json),
});
```

---

## Secret Management

### Secret Storage Hierarchy

```
Tier 0: Environment variables (⚠️ NEVER for secrets)
Tier 1: Encrypted .tfvars / pulumi config --secret (ok for dev, NOT prod)
Tier 2: Ansible Vault / SOPS (ok for config secrets)
Tier 3: Cloud Secret Manager (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
Tier 4: HashiCorp Vault (dynamic secrets, short-lived leases — GOLD STANDARD)
```

### Terraform — Secrets Manager Integration

```hcl
# NEVER:
# variable "db_password" { default = "SuperSecret123!" }  ← NO

# ALWAYS:
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "${var.environment}/database/master-password"
}

locals {
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)
}

resource "aws_db_instance" "main" {
  username = local.db_credentials.username
  password = local.db_credentials.password
  # ...
}

# Mark outputs as sensitive
output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}
```

### Pulumi — Pulumi ESC (Environments, Secrets, and Configuration)

```typescript
// Pulumi ESC: central secret store that integrates natively
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
// Marked as secret in Pulumi Cloud → encrypted at rest + in transit
const dbPassword = config.requireSecret("dbPassword");

const db = new aws.rds.Instance("main", {
  password: dbPassword,  // Pulumi tracks this as a secret automatically
});
```

### gitleaks Configuration

```toml
# .gitleaks.toml — committed to repository
[allowlist]
  description = "Global allowlist"
  paths = [
    '''go\.sum$''',
    '''package-lock\.json$''',
  ]

[[rules]]
  id = "aws-access-key"
  description = "AWS Access Key"
  regex = '''(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'''
  tags = ["key", "aws"]

[[rules]]
  id = "generic-api-key"
  description = "Generic API Key"
  regex = '''(?i)(?:key|api|token|secret|password|passwd|auth)[\s:=]+['\"][0-9a-zA-Z\-_=]{20,}['\"]'''
  entropy = 3.5
```

### Ansible Vault Usage

```bash
# Encrypt secrets file
ansible-vault encrypt vars/production/secrets.yml

# Run playbook with vault password prompt
ansible-playbook site.yml --ask-vault-pass

# CI/CD: pass vault password via file (mounted from Secret Manager)
ansible-playbook site.yml --vault-password-file /run/secrets/vault-password
```

```yaml
# vars/production/secrets.yml (encrypted at rest)
# $ANSIBLE_VAULT;1.1;AES256
# 66386439653236336...encrypted content...

# Referenced naturally in playbooks
- name: Configure database
  postgresql_db:
    login_password: "{{ db_master_password }}"
```

---

## Encryption Standards

### Encryption at Rest — Per-Service Requirements

| Service          | Requirement                      | Terraform Directive                         |
|------------------|----------------------------------|---------------------------------------------|
| S3               | SSE-KMS (customer-managed key)   | `sse_algorithm = "aws:kms"`                |
| RDS              | Storage encryption enabled       | `storage_encrypted = true`                  |
| DynamoDB         | Default (always encrypted)       | No action needed                            |
| EBS              | Encrypted by default             | `encrypted = true` (or account-wide)        |
| EFS              | Encryption at rest               | `encrypted = true`                          |
| ECR              | Image scanning + immutable tags  | `image_scanning_configuration`              |
| CloudWatch Logs  | KMS encryption                   | `kms_key_id = aws_kms_key.logs.arn`         |
| SQS              | SSE enabled                      | `sqs_managed_sse_enabled = true`            |
| SNS              | KMS encryption                   | `kms_master_key_id`                         |
| ElastiCache      | Encryption at rest + in transit  | `at_rest_encryption_enabled = true`         |
| Redshift         | Encryption enabled               | `encrypted = true`                          |

### KMS Key Policy — Least Privilege

```hcl
data "aws_iam_policy_document" "kms_key" {
  # Allow key admin (can manage key, not use it)
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [var.admin_role_arn]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  # Allow specific services to encrypt/decrypt
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com", "s3.amazonaws.com"]
    }
    actions   = ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "kms:CallerAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  # Enable automatic key rotation
  enable_key_rotation = true
}
```

### Encryption in Transit

```hcl
# ALB: HTTPS-only with HTTP redirect
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# CloudFront: HTTPS-only
resource "aws_cloudfront_distribution" "cdn" {
  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = aws_acm_certificate.cdn.arn
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method            = "sni-only"
  }
}
```

---

## Network Security

### Defense-in-Depth Layering

```
Internet
  │
  ▼
WAF (AWS WAF / Cloudflare)           ← Layer 7 protection
  │
  ▼
DDoS Protection (Shield / CDN)       ← Volumetric attack protection
  │
  ▼
Load Balancer (ALB/NLB)              ← TLS termination
  │
  ▼
Network ACLs (stateless)             ← Subnet-level filtering
  │
  ▼
Security Groups (stateful)           ← Instance-level firewall
  │
  ▼
Application Firewall                 ← mod_security / WAF at app level
  │
  ▼
Workload (EC2/ECS/Lambda)            ← Your application
```

### Security Group Templates

```hcl
# Public ALB — minimal exposure
resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Public ALB — HTTPS only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description      = "HTTPS from internet"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]  # Intentional — public ALB
  }

  ingress {
    description = "HTTP from internet (redirects to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # ALBs need to reach targets and AWS APIs
  }

  tags = { Name = "${var.environment}-alb-sg" }
}

# Application — locked down
resource "aws_security_group" "app" {
  name        = "${var.environment}-app-sg"
  description = "Application tier"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "From ALB only"
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "To VPC endpoints only (S3, DynamoDB, KMS, ECR)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    # RESTRICTED — use prefix lists or VPC endpoint security groups
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.s3.id]
  }
}

# Database — most restrictive
resource "aws_security_group" "db" {
  name        = "${var.environment}-db-sg"
  description = "Database tier — app access only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from application tier only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # NO egress to internet — use VPC endpoints for AWS services
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.s3.id]
  }
}
```

### Network ACLs — Defense-in-Depth

```hcl
# NACL on private subnet — restrictive stateless rules
resource "aws_network_acl" "private" {
  vpc_id = module.vpc.vpc_id

  # Ephemeral ports for return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = module.vpc.vpc_cidr
    from_port  = 1024
    to_port    = 65535
  }

  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"  # VPC endpoints route
    from_port  = 443
    to_port    = 443
  }

  # Deny all by default (NACL default rule)
}

# VPC Endpoints — keep traffic within AWS network
resource "aws_vpc_endpoint" "s3" {
  vpc_id          = module.vpc.vpc_id
  service_name    = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = module.vpc.private_route_table_ids
  tags            = { Name = "${var.environment}-s3-endpoint" }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id          = module.vpc.vpc_id
  service_name    = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids = module.vpc.private_route_table_ids
}
```

---

## Logging & Audit Trail

### Minimum Logging Requirements

```hcl
# CloudTrail — organization trail, all regions
resource "aws_cloudtrail" "org" {
  name                          = "org-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  is_organization_trail         = true
  kms_key_id                    = aws_kms_key.cloudtrail.arn

  # Prevent deletion
  lifecycle {
    prevent_destroy = true
  }
}

# S3 bucket for logs — locked down
resource "aws_s3_bucket" "cloudtrail" {
  bucket = "myorg-cloudtrail-logs-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  policy = data.aws_iam_policy_document.cloudtrail_bucket.json
}

# VPC Flow Logs — capture ALL traffic metadata
resource "aws_flow_log" "vpc" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"  # Not just REJECT — capture all
  vpc_id          = module.vpc.vpc_id
}
```

---

## Compliance Frameworks Mapping

### SOC 2 — Key IaC Controls

| SOC 2 Trust Criteria | IaC Control                                      |
|---------------------|--------------------------------------------------|
| CC6.1 (Logical Access) | IAM least privilege in IaC policies            |
| CC6.3 (Security Incidents) | GuardDuty + CloudTrail via IaC             |
| CC6.6 (External Threats) | WAF rules, SG restrictions in IaC             |
| CC7.1 (Change Management) | Git PR → plan → apply pipeline              |
| CC7.2 (Risk Mitigation) | Drift detection scheduled hourly              |
| CC8.1 (Monitoring) | All logging configured via IaC                   |

### CIS AWS Foundations Benchmark — Top IaC Checks

| CIS Rule | Description                     | checkov ID         |
|----------|---------------------------------|-------------------|
| 1.2      | No root access keys             | CKV_AWS_42        |
| 1.4      | Access keys rotated < 90 days   | CKV_AWS_45        |
| 1.16     | IAM policy without full "*:*"   | CKV_AWS_62        |
| 2.1      | CloudTrail enabled              | CKV_AWS_35        |
| 2.2      | CloudTrail log validation       | CKV_AWS_36        |
| 3.1      | CloudTrail in CloudWatch        | CKV_AWS_90        |
| 4.1-4.10 | VPC security controls           | CKV_AWS_23-27     |

---

## Automated Enforcement

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.88.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_tfsec
      - id: terraform_checkov

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/ansible/ansible-lint
    rev: v24.2.0
    hooks:
      - id: ansible-lint
```

### CI/CD Policy Gates

```yaml
# .github/workflows/security-gate.yml
name: Security Gate
on: [pull_request]
jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@v12
        with:
          directory: .
          framework: terraform,cloudformation,ansible,bicep
          soft_fail: false  # Hard block on ANY checkov failure
          output_format: sarif
          output_file_path: checkov-results.sarif

  tfsec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/tfsec-pr-commenter-action@v1.3.1
        with:
          tfsec_args: --minimum-severity HIGH
          github_token: ${{ secrets.GITHUB_TOKEN }}

  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@v3.67.0
        with:
          path: ./
          base: ${{ github.event.pull_request.base.sha }}
          head: ${{ github.event.pull_request.head.sha }}
          extra_args: --only-verified
```

### Pulumi Policy Pack

```typescript
// policy/iamPolicyPack.ts
import * as pulumi from "@pulumi/pulumi";
import { PolicyPack, ReportViolation, ResourceValidationPolicy } from "@pulumi/policy";

new PolicyPack("iam-security", {
  policies: [
    // No S3 buckets with public ACL
    new ResourceValidationPolicy("s3-bucket-no-public-acl", {
      validateResource: (args, report) => {
        if (args.type === "aws:s3/bucket:Bucket" && args.props.acl === "public-read") {
          report("S3 bucket must not use public-read ACL. Use CloudFront or signed URLs.");
        }
      },
    }),

    // EC2 instances must use approved AMIs
    new ResourceValidationPolicy("ec2-approved-ami", {
      validateResource: (args, report) => {
        if (args.type === "aws:ec2/instance:Instance") {
          const ami = args.props.ami as string;
          if (!ami.startsWith("ami-") || !APPROVED_AMIS.has(ami)) {
            report(`EC2 instance AMI '${ami}' is not in the approved AMI list.`);
          }
        }
      },
    }),

    // RDS must be encrypted
    new ResourceValidationPolicy("rds-storage-encrypted", {
      validateResource: (args, report) => {
        if (args.type === "aws:rds/instance:Instance" && !args.props.storageEncrypted) {
          report("RDS instances must have storage encryption enabled.");
        }
      },
    }),
  ],
});
```

---

## Secret Rotation Strategy

### Rotation Schedule

| Secret Type           | Rotation Frequency | Method                              |
|-----------------------|--------------------|-------------------------------------|
| Database passwords    | 30 days            | AWS Secrets Manager auto-rotation   |
| API keys              | 90 days            | Manual rotation with overlap window  |
| IAM Access Keys       | 90 days            | AWS IAM credential report + rotation |
| TLS Certificates      | ~365 days (or ACM) | ACM auto-renewal (preferred)         |
| Encryption Keys       | 365 days           | KMS automatic rotation              |

### Terraform DB Password Rotation

```hcl
# Secrets Manager with automatic rotation
resource "aws_secretsmanager_secret" "db" {
  name                    = "${var.environment}/database/master-password"
  recovery_window_in_days = 0  # Immediate delete for non-prod (careful in prod!)

  rotation_rules {
    automatically_after_days = 30
  }

  # Lambda rotation function
  rotation_lambda_arn = aws_lambda_function.rotate_db_secret.arn
}

# Terraform handles the password change gracefully:
# 1. AWS Secrets Manager rotates the secret
# 2. RDS gets new password
# 3. Application gets new secret via SDK cache refresh
# 4. Terraform state remains unchanged (password is `sensitive`, not in state)
```

---

## Incident Response Readiness

### Infrastructure Freeze via IaC

```hcl
# Break-glass SCP or IAM boundary to freeze all IaC changes
# Applied at organization level during incidents

# Emergency: deny all Terraform apply operations
data "aws_iam_policy_document" "freeze" {
  statement {
    effect = "Deny"
    actions = [
      "ec2:*",
      "rds:*",
      "s3:Delete*",
      "dynamodb:Delete*",
      "iam:*",
      "lambda:*",
      "ecs:*",
      "eks:*",
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:CalledVia"
      values   = ["cloudformation.amazonaws.com"]  # Deny CFn but allow console
    }
  }
}
```

### Audit Log Correlation

IaC changes are tracked across three layers:

1. **Git history** — who changed what code, when, in which PR
2. **CI/CD logs** — which pipeline applied the change, with full plan output
3. **CloudTrail** — actual API calls with timestamps, source IP, and principal

Cross-reference these three for any security investigation:

```bash
# Find who applied a specific Terraform change
git log --all --follow -- environments/prod/main.tf

# Find CloudTrail events from that time window
aws cloudtrail lookup-events \
  --start-time "$(date -v-1H -u +%s)" \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances

# Check CI/CD for the deployment
gh run list --workflow terraform.yml --limit 20
```
