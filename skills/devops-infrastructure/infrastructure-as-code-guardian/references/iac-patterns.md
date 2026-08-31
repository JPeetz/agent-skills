# IaC Patterns — Reusable Infrastructure Patterns

> Part of the Infrastructure as Code Guardian skill. Covers battle-tested patterns for module composition, environment stratification, remote state, GitOps, and cost-effective infrastructure design across Terraform, Pulumi, CloudFormation, and Bicep.

---

## Table of Contents

1. [Module Composition](#module-composition)
2. [Environment Stratification](#environment-stratification)
3. [Remote State Architecture](#remote-state-architecture)
4. [GitOps Workflow](#gitops-workflow)
5. [Multi-Cloud Patterns](#multi-cloud-patterns)
6. [Cost Optimization Patterns](#cost-optimization-patterns)
7. [Disaster Recovery Patterns](#disaster-recovery-patterns)
8. [Zero-Downtime Deployment Patterns](#zero-downtime-deployment-patterns)

---

## Module Composition

### Flat vs. Layered vs. Domain Modules

```
FLAT (Anti-pattern for large infra):
  ├── main.tf (3000 lines — everything in one file)
  └── variables.tf

LAYERED (Good for medium infra):
  ├── 01-networking/
  │   └── main.tf
  ├── 02-compute/
  │   └── main.tf
  └── 03-data/
      └── main.tf

DOMAIN-ORIENTED (Best for large/team infra):
  ├── modules/
  │   ├── networking/      (VPC, subnets, gateways)
  │   │   ├── main.tf
  │   │   ├── variables.tf
  │   │   ├── outputs.tf
  │   │   └── README.md
  │   ├── compute/         (ASG, ECS, Lambda)
  │   ├── data/            (RDS, DynamoDB, ElastiCache)
  │   ├── security/        (IAM, KMS, WAF)
  │   └── monitoring/      (CloudWatch, alarms, dashboards)
  ├── environments/
  │   ├── dev/
  │   │   ├── main.tf      (module "networking" { source = "../../modules/networking" })
  │   │   └── terraform.tfvars
  │   ├── staging/
  │   └── prod/
  └── global/
      └── main.tf            (Route53, CloudFront, IAM — once per org)
```

### Module Versioning Strategy

```hcl
# Pinned: deterministic, safe
module "vpc" {
  source  = "app.terraform.io/myorg/vpc/aws"
  version = "~> 3.1.0"
}

# Git reference: flexible, use for pre-release
module "vpc" {
  source = "git::https://github.com/myorg/terraform-aws-vpc.git?ref=v3.1.0"
}

# Never use: master branch references in production
# module "vpc" { source = "git::https://github.com/...?ref=main" }  ← NO
```

### Module Interface Design

Good modules have:
1. **Narrow interface** — few required variables, reasonable defaults for the rest
2. **Rich outputs** — expose all resources that downstream consumers need
3. **No provider blocks in modules** — provider configuration belongs in the root module
4. **No backends in modules** — only root modules configure backends
5. **Versioned examples** — every major version ships with a working example

### Pulumi Component Resources

```typescript
// Reusable encapsulation that feels native to the language
class DatabaseCluster extends pulumi.ComponentResource {
  public readonly endpoint: pulumi.Output<string>;
  public readonly securityGroupId: pulumi.Output<string>;

  constructor(name: string, args: DatabaseArgs, opts?: pulumi.ComponentResourceOptions) {
    super("myorg:data:DatabaseCluster", name, {}, opts);

    const sg = new aws.ec2.SecurityGroup(`${name}-sg`, {
      vpcId: args.vpcId,
      ingress: [{ protocol: "tcp", fromPort: 5432, toPort: 5432, cidrBlocks: [args.cidr] }],
    }, { parent: this });

    const cluster = new aws.rds.Cluster(`${name}-cluster`, {
      engine: "aurora-postgresql",
      databaseName: args.databaseName,
      masterUsername: args.username,
      masterPassword: args.password, // pulled from Secrets Manager in production
      vpcSecurityGroupIds: [sg.id],
      skipFinalSnapshot: args.environment !== "prod",
    }, { parent: this, protect: args.environment === "prod" });

    this.endpoint = cluster.endpoint;
    this.securityGroupId = sg.id;

    this.registerOutputs({ endpoint: this.endpoint, securityGroupId: this.securityGroupId });
  }
}
```

---

## Environment Stratification

### Isolation Patterns

| Pattern               | Isolation Level | Complexity | Best For                          |
|-----------------------|-----------------|------------|-----------------------------------|
| Single state + workspace | Low          | Low        | Solo dev, small projects          |
| Directory-per-env     | Medium          | Medium     | Most teams                        |
| Account-per-env (AWS) | Maximum         | High       | Regulated industries, SOC2/HIPAA   |
| Subscription-per-env (Azure) | Maximum   | High       | Enterprise                        |

### Directory-per-Environment (Recommended Default)

```
environments/
├── dev/
│   ├── main.tf
│   ├── terraform.tfvars    # cidr = "10.1.0.0/16", instance_type = "t3.small"
│   └── backend.tf
├── staging/
│   ├── main.tf              # Same modules, different tfvars
│   └── terraform.tfvars     # cidr = "10.2.0.0/16", instance_type = "t3.medium"
└── prod/
    ├── main.tf
    └── terraform.tfvars     # cidr = "10.3.0.0/16", instance_type = "m6i.large"
```

### Feature Branch Environments (Ephemeral)

```yaml
# CI/CD pattern: spin up isolated env per PR, tear down on merge
name: Feature Env
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  deploy-feature:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Terraform Apply
        run: |
          cd environments/feature
          terraform init
          terraform workspace new "pr-${{ github.event.number }}" || terraform workspace select "pr-${{ github.event.number }}"
          terraform apply -auto-approve -var="pr_number=${{ github.event.number }}"
      - name: Comment PR with URL
        run: |
          URL=$(terraform output -raw app_url)
          gh pr comment ${{ github.event.number }} --body "🚀 Feature env ready: $URL"
  teardown-feature:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - name: Terraform Destroy
        run: |
          cd environments/feature
          terraform init
          terraform workspace select "pr-${{ github.event.number }}"
          terraform destroy -auto-approve
```

---

## Remote State Architecture

### State File Layout

```
S3 Bucket: myorg-terraform-state  (account: management)
├── global/
│   └── route53/terraform.tfstate      (org-wide DNS)
├── networking/
│   └── terraform.tfstate               (transit gateway, VPC peering)
├── dev/
│   ├── compute/terraform.tfstate
│   ├── data/terraform.tfstate
│   └── networking/terraform.tfstate
├── staging/  (same layout)
└── prod/     (same layout)
```

### State Access Control

```hcl
# IAM policy for CI/CD service role — least privilege
data "aws_iam_policy_document" "terraform_state" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::myorg-terraform-state/env:/${terraform.workspace}/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"]
    resources = ["arn:aws:dynamodb:*:*:table/terraform-state-locks"]
  }
}
```

### Anti-Patterns

- ❌ Sharing state between environments (`workspace` for long-lived envs)
- ❌ Local state in CI/CD (no `.gitignore` for `*.tfstate`)
- ❌ State bucket without versioning
- ❌ State bucket without encryption
- ❌ Developers with direct S3 access to state files

---

## GitOps Workflow

### Pull-Request Pipeline

```
Developer opens PR
  → terraform fmt -check
  → terraform validate
  → tflint / checkov / tfsec
  → terraform plan (post to PR comment)
  → CODEOWNERS required review
  → terraform apply (on merge to main)
```

### Directory-Based Apply Strategy

```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD
on:
  pull_request:
    paths:
      - 'environments/**'
  push:
    branches: [main]
    paths:
      - 'environments/**'
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      dirs: ${{ steps.changes.outputs.dirs }}
    steps:
      - uses: actions/checkout@v4
      - id: changes
        run: |
          DIRS=$(git diff --name-only origin/main...HEAD | grep '^environments/' | cut -d'/' -f1-2 | sort -u | jq -R -s -c 'split("\n")[:-1]')
          echo "dirs=$DIRS" >> "$GITHUB_OUTPUT"
  plan:
    needs: detect-changes
    if: needs.detect-changes.outputs.dirs != '[]'
    strategy:
      matrix:
        dir: ${{ fromJSON(needs.detect-changes.outputs.dirs) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: |
          cd ${{ matrix.dir }}
          terraform init
          terraform plan -out=tfplan
  apply:
    if: github.ref == 'refs/heads/main'
    needs: [plan, detect-changes]
    strategy:
      matrix:
        dir: ${{ fromJSON(needs.detect-changes.outputs.dirs) }}
    runs-on: ubuntu-latest
    environment:
      name: ${{ matrix.dir }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: |
          cd ${{ matrix.dir }}
          terraform init
          terraform apply -auto-approve tfplan
```

---

## Multi-Cloud Patterns

### Abstraction Layer with Pulumi

```typescript
// Define a cloud-agnostic interface
interface ManagedDatabase {
  endpoint: pulumi.Output<string>;
  port: number;
  engine: string;
  connectionString: pulumi.Output<string>;
}

class AwsRdsDatabase extends pulumi.ComponentResource implements ManagedDatabase {
  public readonly endpoint: pulumi.Output<string>;
  public readonly port: number = 5432;
  public readonly engine: string = "aurora-postgresql";
  public readonly connectionString: pulumi.Output<string>;

  constructor(name: string, args: DbArgs, opts?: pulumi.ComponentResourceOptions) {
    super("myorg:multicloud:AwsDatabase", name, {}, opts);
    const cluster = new aws.rds.Cluster(`${name}-pg`, { ... });
    this.endpoint = cluster.endpoint;
    this.connectionString = pulumi.interpolate`postgres://${args.username}:${args.password}@${cluster.endpoint}:5432/${args.dbName}`;
  }
}

class AzurePostgresDatabase extends pulumi.ComponentResource implements ManagedDatabase {
  public readonly endpoint: pulumi.Output<string>;
  public readonly port: number = 5432;
  public readonly engine: string = "postgresql-flexible";
  public readonly connectionString: pulumi.Output<string>;

  constructor(name: string, args: DbArgs, opts?: pulumi.ComponentResourceOptions) {
    super("myorg:multicloud:AzureDatabase", name, {}, opts);
    const server = new azure.dbforpostgresql.FlexibleServer(`${name}-pg`, { ... });
    this.endpoint = server.fqdn;
    this.connectionString = pulumi.interpolate`postgres://${args.username}:${args.password}@${server.fqdn}:5432/${args.dbName}`;
  }
}
```

### Terraform Multi-Cloud Considerations

- Use separate provider blocks per cloud — no shared state across clouds in single root module
- Cross-cloud references via data sources (e.g., `data "aws_route53_zone"` referenced from Azure DNS)
- Service mesh (Consul, Istio) for cross-cloud service discovery — avoid hardcoding cloud endpoints
- Multi-cloud CI: validate all providers in PR, apply serially (cloud A → cloud B)

---

## Cost Optimization Patterns

### Tagging Strategy

All IaC-managed resources must carry these tags (enforce via policy):

| Tag          | Purpose                        | Example         |
|-------------|--------------------------------|-----------------|
| Environment | Tier identification            | prod, staging   |
| Owner       | Team or individual             | platform-team   |
| CostCenter  | Finance tracking               | eng-1234        |
| Project     | Application/business context   | checkout-api    |
| ManagedBy   | IaC tool identification        | terraform       |
| AutoShutdown| Eligible for off-hours stop    | true/false      |

### Auto-Scaling Guardrails

```hcl
# Terraform — enforce min/max bounds
resource "aws_autoscaling_group" "app" {
  min_size         = var.environment == "prod" ? 3 : 1
  max_size         = var.environment == "prod" ? 12 : 2
  desired_capacity = var.environment == "prod" ? 3 : 1

  # Scaling policies: scale up fast, scale down slow
  # (avoids thrash, saves money on gradual scale-in)
}

# Always pair ASG with target tracking scaling
resource "aws_autoscaling_policy" "cpu" {
  autoscaling_group_name = aws_autoscaling_group.app.name
  adjustment_type        = "ChangeInCapacity"
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### Storage Lifecycle

```hcl
# S3 lifecycle — auto-transition to cheaper tiers
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "log-lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    expiration {
      days = 365
    }
    # Clean up incomplete multipart uploads (often forgotten)
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
```

### Dev/Staging Cost Reduction

```hcl
# Lambda — start-stop scheduling for non-prod
resource "aws_autoscaling_schedule" "stop_night" {
  count                  = var.environment != "prod" ? 1 : 0
  scheduled_action_name  = "stop-nightly"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 0
  max_size               = 0
  desired_capacity       = 0
  recurrence             = "0 20 * * *"  # 8 PM
}

resource "aws_autoscaling_schedule" "start_morning" {
  count                  = var.environment != "prod" ? 1 : 0
  scheduled_action_name  = "start-morning"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 1
  max_size               = var.environment == "staging" ? 2 : 1
  desired_capacity       = 1
  recurrence             = "0 7 * * *"  # 7 AM
}
```

---

## Disaster Recovery Patterns

### Multi-Region Active-Passive

```hcl
# Primary region (active)
provider "aws" {
  region = var.primary_region  # us-east-1
}

module "app_primary" {
  source = "./modules/app"
  providers = { aws = aws }
  environment = var.environment
}

# DR region (passive — data replicated, compute scaled to zero)
provider "aws" {
  alias  = "dr"
  region = var.dr_region  # us-west-2
}

module "app_dr" {
  source = "./modules/app"
  providers = { aws = aws.dr }
  environment     = var.environment
  is_dr           = true
  min_capacity    = 0            # No compute until failover
  enable_compute  = false
}
```

### Backup Strategy Checklist

- [ ] RDS: automated backups enabled, retention >= 30 days for prod
- [ ] S3: versioning + cross-region replication for critical buckets
- [ ] DynamoDB: point-in-time recovery + on-demand backup schedule
- [ ] EBS: automated snapshots with Data Lifecycle Manager (DLM) policies
- [ ] State files: cross-region/cross-account replication of state buckets
- [ ] Configuration: all IaC source in git; git is its own DR

---

## Zero-Downtime Deployment Patterns

### Blue-Green with Terraform

```hcl
# Create new resources before destroying old ones
resource "aws_launch_template" "app" {
  name_prefix   = "app-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true  # Create new LT, then roll ASG
  }
}

resource "aws_autoscaling_group" "app" {
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  # Instance refresh for zero-downtime rolling updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 66     # Keep 2/3 healthy during refresh
      instance_warmup        = 300    # Wait 5 min for new instances
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

### Database Migrations During Deploy

```hcl
# 1. Apply backward-compatible schema changes first
# 2. Deploy new app code (works with both old and new schema)
# 3. Clean up old columns/tables in a follow-up deploy
resource "null_resource" "db_migrate" {
  triggers = {
    schema_version = filemd5("${path.module}/migrations/V${var.schema_version}.sql")
  }

  provisioner "local-exec" {
    command = "psql $DATABASE_URL -f migrations/V${var.schema_version}.sql"
  }
}
```
