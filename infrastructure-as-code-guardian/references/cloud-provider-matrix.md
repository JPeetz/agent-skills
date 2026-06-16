# Cloud Provider Matrix — IaC Feature Parity

> Part of the Infrastructure as Code Guardian skill. Maps infrastructure resource types across AWS, Azure, and GCP with their Terraform, Pulumi, and native IaC tool support.

---

## Table of Contents

1. [Compute](#compute)
2. [Containers & Orchestration](#containers--orchestration)
3. [Serverless](#serverless)
4. [Storage](#storage)
5. [Databases](#databases)
6. [Networking](#networking)
7. [Security & Identity](#security--identity)
8. [Monitoring & Observability](#monitoring--observability)
9. [CI/CD & DevOps](#cicd--devops)
10. [Multi-Cloud Resource Mappings](#multi-cloud-resource-mappings)

---

## Compute

| Capability            | AWS                        | Azure                      | GCP                        |
|-----------------------|----------------------------|----------------------------|----------------------------|
| **Virtual Machines**  | EC2                        | Virtual Machines           | Compute Engine             |
| Terraform Resource    | `aws_instance`             | `azurerm_virtual_machine`  | `google_compute_instance`  |
| Pulumi Resource       | `aws.ec2.Instance`         | `azure.compute.VirtualMachine` | `gcp.compute.Instance` |
| CFn / Bicep / DM      | `AWS::EC2::Instance`       | `Microsoft.Compute/virtualMachines` | `gcloud compute instances create` |
| **Auto-Scaling**      | Auto Scaling Group         | VM Scale Sets              | Managed Instance Groups    |
| **GPU Instances**     | P3/P4/P5/G5 instances      | NCas_T4_v3 / ND A100 v4    | A2 / G2 machine types      |
| **Spot/Preemptible**  | Spot Instances             | Spot VMs                   | Preemptible VMs            |
| **Dedicated Hosts**   | Dedicated Hosts            | Dedicated Hosts            | Sole-tenant Nodes          |
| **Capacity Reservations** | On-Demand Capacity Reservations | Capacity Reservations | Reservation-based MIGs |

### Cross-Cloud VM Pattern

```hcl
# Terraform multi-cloud compute module
variable "cloud" {
  type    = string
  validation {
    condition     = contains(["aws", "azure", "gcp"], var.cloud)
    error_message = "Cloud must be: aws, azure, or gcp."
  }
}

resource "aws_instance" "vm" {
  count         = var.cloud == "aws" ? var.instance_count : 0
  ami           = var.aws_ami
  instance_type = var.instance_type_map[var.cloud]
}

resource "azurerm_linux_virtual_machine" "vm" {
  count           = var.cloud == "azure" ? var.instance_count : 0
  size            = var.instance_type_map[var.cloud]
  admin_username  = var.admin_username
  # ...
}

resource "google_compute_instance" "vm" {
  count        = var.cloud == "gcp" ? var.instance_count : 0
  machine_type = var.instance_type_map[var.cloud]
  # ...
}
```

---

## Containers & Orchestration

| Capability            | AWS                        | Azure                      | GCP                        |
|-----------------------|----------------------------|----------------------------|----------------------------|
| **Managed K8s**       | EKS                        | AKS                        | GKE                        |
| Terraform Resource    | `aws_eks_cluster`          | `azurerm_kubernetes_cluster` | `google_container_cluster` |
| Serverless Containers | ECS Fargate / App Runner   | Container Instances / Container Apps | Cloud Run          |
| Container Registry    | ECR                        | ACR                        | Artifact Registry / GCR    |
| Service Mesh          | App Mesh                   | Open Service Mesh (depr.)  | Anthos Service Mesh (Istio) |
| K8s Add-on Mgmt       | EKS Add-ons                | AKS Add-ons                | GKE Add-ons                |
| K8s Autoscaling       | Cluster Autoscaler / Karpenter | Cluster Autoscaler     | Cluster Autoscaler / NAP   |

### GKE Autopilot vs. Standard

```hcl
# GKE Autopilot — minimal ops overhead
resource "google_container_cluster" "autopilot" {
  name     = "autopilot-cluster"
  location = "us-central1"

  enable_autopilot = true  # No node pool management needed

  # Autopilot defaults are production-ready:
  # - Auto node upgrade
  # - Auto repair
  # - Workload Identity enabled
  # - Shielded Nodes enabled
}
```

### EKS Best-Practice Module

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.environment}-eks"
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Security
  cluster_endpoint_public_access = false  # Private only
  enable_irsa                    = true    # IAM Roles for Service Accounts

  # Encryption
  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.eks.arn
  }

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 10
      desired_size   = 3

      # Security
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            encrypted  = true
            kms_key_id = aws_kms_key.ebs.arn
          }
        }
      }
    }
  }
}
```

---

## Serverless

| Capability            | AWS                        | Azure                      | GCP                        |
|-----------------------|----------------------------|----------------------------|----------------------------|
| **Functions**         | Lambda                     | Functions                  | Cloud Functions            |
| **HTTP Endpoints**    | API Gateway / Lambda URL   | API Management             | Cloud Endpoints / API Gateway |
| **Workflows**         | Step Functions             | Logic Apps                 | Workflows                  |
| **Event Bus**         | EventBridge                | Event Grid                 | Eventarc                   |
| **Queue**             | SQS                        | Queue Storage / Service Bus | Pub/Sub                   |
| **Notification**      | SNS                        | Notification Hubs          | Pub/Sub (push)             |
| **Edge Functions**    | Lambda@Edge / CloudFront Functions | Azure Front Door Rules Engine | N/A (use Cloud CDN) |

### Serverless Cross-Cloud Pattern

```hcl
# Use .zip packaging for Lambda, container for GCP/Azure

# AWS Lambda
resource "aws_lambda_function" "api" {
  count            = var.cloud == "aws" ? 1 : 0
  function_name    = "${var.service}-api"
  runtime          = "nodejs20.x"
  handler          = "index.handler"
  role             = aws_iam_role.lambda[0].arn
  source_code_hash = data.archive_file.lambda.output_base64sha256

  environment {
    variables = {
      SECRET_ARN = aws_secretsmanager_secret.api.arn
    }
  }
}

# GCP Cloud Run (serverless containers, not functions)
resource "google_cloud_run_v2_service" "api" {
  count    = var.cloud == "gcp" ? 1 : 0
  name     = "${var.service}-api"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    containers {
      image = "${var.container_registry}/${var.service}:${var.image_tag}"
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    }
    scaling {
      min_instance_count = var.environment == "prod" ? 1 : 0
      max_instance_count = 10
    }
  }
}
```

---

## Storage

| Capability            | AWS                        | Azure                      | GCP                        |
|-----------------------|----------------------------|----------------------------|----------------------------|
| **Object Storage**    | S3                         | Blob Storage               | Cloud Storage              |
| **Block Storage**     | EBS                        | Managed Disks              | Persistent Disk            |
| **File Storage**      | EFS / FSx                  | Azure Files / NetApp Files | Filestore                  |
| **Archive**           | S3 Glacier / Deep Archive  | Archive Tier               | Archive / Coldline         |
| **Hybrid/Edge**       | Storage Gateway / Snowball | StorSimple / Data Box      | Transfer Appliance         |
| **Data Transfer**     | DataSync / S3 Transfer     | AzCopy / Data Box          | Storage Transfer Service   |

### S3 Security Baseline

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "${var.environment}-${var.app_name}-${data.aws_caller_identity.current.account_id}"
}

# Public Access Block — ALWAYS enable
resource "aws_s3_bucket_public_access_block" "app" {
  bucket = aws_s3_bucket.app.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "app" {
  bucket = aws_s3_bucket.app.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# Versioning
resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id
  versioning_configuration {
    status = var.environment == "prod" ? "Enabled" : "Suspended"
  }
}

# Logging (to separate bucket)
resource "aws_s3_bucket_logging" "app" {
  bucket        = aws_s3_bucket.app.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access/${var.app_name}/"
}
```

---

## Databases

| Capability            | AWS                          | Azure                          | GCP                          |
|-----------------------|------------------------------|--------------------------------|------------------------------|
| **Relational (managed)** | RDS (MySQL, PG, MariaDB, Oracle, SQL Server) | SQL Database / Managed Instance / MySQL/PostgreSQL Flexible Server | Cloud SQL (MySQL, PG, SQL Server) |
| **Distributed SQL**   | Aurora (MySQL/PG compatible)  | Cosmos DB (multi-model)       | Cloud Spanner / AlloyDB      |
| **NoSQL — Key/Value**| DynamoDB                      | Cosmos DB / Table Storage     | Bigtable / Firestore         |
| **NoSQL — Document**  | DocumentDB (Mongo compat)     | Cosmos DB (Mongo API)         | Firestore                    |
| **In-Memory Cache**   | ElastiCache (Redis/Memcached) | Redis Cache                   | Memorystore (Redis/Memcached)|
| **Graph**             | Neptune                       | Cosmos DB (Gremlin API)       | N/A (JanusGraph on GKE)      |
| **Time Series**       | Timestream                    | Data Explorer / Time Series Insights | Bigtable (wide-column) |
| **Ledger**            | QLDB                          | Confidential Ledger           | N/A                          |
| **Search**            | OpenSearch                    | Cognitive Search              | Vertex AI Search / Elastic   |

### Database Connection Pattern (all clouds)

```hcl
# Use Secrets Manager / Key Vault / Secret Manager for credentials
# Never store passwords in Terraform state files

# AWS
data "aws_secretsmanager_secret_version" "db" {
  count     = var.cloud == "aws" ? 1 : 0
  secret_id = "${var.environment}/${var.service}/database"
}

# Azure
data "azurerm_key_vault_secret" "db" {
  count        = var.cloud == "azure" ? 1 : 0
  name         = "${var.service}-db-password"
  key_vault_id = data.azurerm_key_vault.shared.id
}

# GCP
data "google_secret_manager_secret_version" "db" {
  count   = var.cloud == "gcp" ? 1 : 0
  secret  = "${var.service}-db-password"
}
```

---

## Networking

| Capability              | AWS                    | Azure                    | GCP                        |
|-------------------------|------------------------|--------------------------|----------------------------|
| **VPC / VNet**          | VPC                    | Virtual Network (VNet)   | VPC                        |
| **Subnets**             | Subnets (AZ-scoped)    | Subnets (no AZ binding)  | Subnets (regional)         |
| **NAT**                 | NAT Gateway            | NAT Gateway              | Cloud NAT                  |
| **Load Balancer (L7)**  | ALB                    | Application Gateway      | HTTP(S) Load Balancer      |
| **Load Balancer (L4)**  | NLB                    | Load Balancer            | TCP/UDP Load Balancer      |
| **Global LB**           | Global Accelerator     | Front Door / Traffic Manager | Global Load Balancer   |
| **DNS**                 | Route 53               | Azure DNS                | Cloud DNS                  |
| **CDN**                 | CloudFront             | Azure CDN / Front Door   | Cloud CDN                  |
| **DDoS Protection**     | Shield / Shield Advanced | DDoS Protection Standard | Cloud Armor (L7)           |
| **WAF**                 | AWS WAF                | Azure WAF / Front Door WAF | Cloud Armor              |
| **VPN**                 | Site-to-Site VPN       | VPN Gateway              | Cloud VPN                  |
| **Direct Connect**      | Direct Connect         | ExpressRoute             | Cloud Interconnect         |
| **Transit / Hub**       | Transit Gateway        | Virtual WAN Hub          | Network Connectivity Center|
| **Private Link**        | PrivateLink            | Private Link             | Private Service Connect    |
| **Service Mesh**        | App Mesh / VPC Lattice | Open Service Mesh        | Anthos / Traffic Director  |

### VPC Architecture Comparison

```
AWS VPC (AZ-scoped subnets):
  Region: us-east-1
  ├── VPC: 10.0.0.0/16
  │   ├── AZ: us-east-1a
  │   │   ├── Public:  10.0.1.0/24
  │   │   └── Private: 10.0.10.0/24
  │   └── AZ: us-east-1b
  │       ├── Public:  10.0.2.0/24
  │       └── Private: 10.0.20.0/24

Azure VNet (regional subnets, no AZ binding):
  Region: eastus
  └── VNet: 10.0.0.0/16
      ├── Public:   10.0.1.0/24
      ├── Private:  10.0.2.0/24
      └── Gateway:  10.0.3.0/27

GCP VPC (global, regional subnets):
  Global VPC
  ├── Region: us-central1
  │   ├── Subnet-Private:  10.1.0.0/20
  │   └── Subnet-Public:   10.1.16.0/20
  └── Region: europe-west1
      ├── Subnet-Private:  10.2.0.0/20
      └── Subnet-Public:   10.2.16.0/20
```

---

## Security & Identity

| Capability              | AWS                    | Azure                    | GCP                        |
|-------------------------|------------------------|--------------------------|----------------------------|
| **IAM**                 | IAM (Users/Roles/Policies) | Entra ID (Azure AD) | IAM (Service Accounts)     |
| **Federation**          | IAM Identity Center / SAML | Entra ID Enterprise Apps | Workforce Identity Federation |
| **MFA**                 | Virtual MFA / U2F      | Microsoft Authenticator  | Security Keys / Titan      |
| **Secrets Manager**     | Secrets Manager        | Key Vault                | Secret Manager             |
| **KMS / HSM**           | KMS / CloudHSM         | Key Vault / Dedicated HSM | Cloud KMS / Cloud HSM    |
| **Certificate Manager** | ACM                    | App Service Certificates | Certificate Manager        |
| **WAF**                 | AWS WAF                | Azure WAF                | Cloud Armor                |
| **DDoS Protection**     | Shield / Shield Advanced | DDoS Protection         | Cloud Armor (adaptive)     |
| **Vulnerability Mgmt**  | Inspector / Security Hub | Defender for Cloud      | Security Command Center    |
| **Compliance**          | Audit Manager / Artifact | Compliance Manager      | Compliance Reports Center  |
| **Network Firewall**    | Network Firewall       | Azure Firewall           | Cloud NGFW (Palo Alto)     |

---

## Monitoring & Observability

| Capability              | AWS                    | Azure                    | GCP                        |
|-------------------------|------------------------|--------------------------|----------------------------|
| **Metrics**             | CloudWatch             | Azure Monitor            | Cloud Monitoring           |
| **Logs**                | CloudWatch Logs        | Log Analytics            | Cloud Logging              |
| **Traces**              | X-Ray                  | Application Insights     | Cloud Trace                |
| **Dashboards**          | CloudWatch Dashboards  | Azure Dashboards         | Cloud Monitoring Dashboards|
| **Alerts**              | CloudWatch Alarms      | Azure Monitor Alerts     | Cloud Monitoring Alerting  |
| **SIEM**                | Security Lake / OpenSearch | Sentinel              | Chronicle                  |
| **Network Monitoring**  | VPC Flow Logs / Reachability Analyzer | Network Watcher | VPC Flow Logs / Network Intelligence |

### Terraform Monitoring Stack

```hcl
# Multi-cloud monitoring baseline
module "monitoring" {
  source   = "./modules/monitoring"
  for_each = toset(var.enabled_clouds)

  cloud        = each.key
  environment  = var.environment

  # Common metrics to collect across all clouds
  metrics = [
    "cpu_utilization",
    "memory_utilization",
    "disk_utilization",
    "request_count",
    "error_rate",
    "latency_p95",
  ]

  alert_channels = {
    slack  = var.slack_webhook_url
    pagerduty = var.pagerduty_integration_key
  }
}
```

---

## CI/CD & DevOps

| Capability              | AWS                      | Azure                      | GCP                        |
|-------------------------|--------------------------|----------------------------|----------------------------|
| **CI/CD**               | CodePipeline / CodeBuild | Azure DevOps / GitHub Actions | Cloud Build / Cloud Deploy |
| **Source Control**      | CodeCommit               | Azure Repos / GitHub        | Cloud Source Repositories  |
| **Artifact Store**      | CodeArtifact / S3        | Azure Artifacts             | Artifact Registry          |
| **Infra as Code**       | CloudFormation / CDK     | Bicep / ARM                 | Deployment Manager / Config Connector |
| **Policy as Code**      | AWS Config / SCPs        | Azure Policy                | Organization Policy        |
| **Cost Management**     | Cost Explorer / Budgets  | Cost Management             | Billing / Cost Management  |
| **Landing Zone**        | Control Tower            | Azure Landing Zones         | Setup / Foundations        |

---

## Multi-Cloud Resource Mappings

### Common Workload: Web App + Database

| Layer               | AWS Resource                    | Azure Resource                          | GCP Resource                      |
|---------------------|---------------------------------|-----------------------------------------|-----------------------------------|
| DNS                 | Route53 Record                  | DNS Zone Record                         | Cloud DNS Record                  |
| CDN                 | CloudFront Distribution         | Azure Front Door / CDN Endpoint         | Cloud CDN Backend                 |
| WAF                 | WAF WebACL                      | WAF Policy                              | Cloud Armor Policy                |
| Load Balancer       | ALB                             | Application Gateway                     | HTTP(S) Load Balancer             |
| Compute             | ECS Fargate Service             | Container App                           | Cloud Run Service                 |
| Database            | RDS Aurora PostgreSQL           | PostgreSQL Flexible Server              | Cloud SQL PostgreSQL              |
| Cache               | ElastiCache Redis               | Azure Cache for Redis                   | Memorystore Redis                 |
| Object Storage      | S3 Bucket                       | Blob Storage Container                  | Cloud Storage Bucket              |
| Secrets             | Secrets Manager                 | Key Vault                               | Secret Manager                    |
| Monitoring          | CloudWatch + X-Ray              | Azure Monitor + App Insights            | Cloud Monitoring + Cloud Trace    |
| CI/CD               | CodePipeline + CodeBuild        | Azure DevOps Pipeline / GitHub Actions  | Cloud Build + Cloud Deploy        |

### Migration Decision Matrix

| From → To           | AWS → Azure          | AWS → GCP             | Azure → GCP           |
|---------------------|----------------------|----------------------|-----------------------|
| **VMs**             | Azure Migrate        | Migrate for Compute Engine | Migrate for Compute Engine |
| **Databases**       | DMS                  | DMS                  | DMS / Cloud SQL Migration |
| **Storage**         | AzCopy / Data Box    | Storage Transfer Service | Storage Transfer Service |
| **Containers**      | AKS + containerize   | GKE + containerize   | GKE + Migrate for Anthos |
| **IaC Migration**   | tf2pulumi export     | terraformer → adapt  | Azure2GCP scripts     |
| **Difficulty**       | Medium              | Medium               | Medium                |

> **Rule of thumb:** Always lift-and-shift first, then optimize for cloud-native services. IaC migration should follow infrastructure migration, not precede it. Generate IaC from existing infrastructure using `terraformer` or `former2`, then refactor into modules.
