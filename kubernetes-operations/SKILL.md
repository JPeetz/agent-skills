---
name: kubernetes-operations
description: Production-grade Kubernetes operations for AI agents: manifest generation, security hardening, Helm charts, GitOps workflows, and multi-cloud deployment patterns. Prevents K8s hallucinations with failure-mode diagnosis, compliance validation, and structured output contracts.
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
domain: DevOps/Kubernetes
version: 1.0.0
triggers:
  - "create deployment"
  - "kubernetes manifest"
  - "Helm chart"
  - "K8s security"
  - "review my deployment"
  - "fix pod"
  - "scale cluster"
  - "deploy to"
  - "network policy"
  - "RBAC"
  - "service mesh"
  - "GitOps"
  - "ArgoCD"
  - "Flux CD"
  - "resource limits"
  - "HPA"
  - "pod disruption budget"
  - "PodSecurityPolicy"
  - "pod security"
  - "scan manifest"
  - "validate k8s"
  - "cluster autoscaler"
  - "spot instances"
  - "External Secrets"
  - "Sealed Secrets"
  - "kubectl"
  - "kustomize"
  - "ingress"
  - "cert-manager"
  - "OpenTelemetry"
near_miss_negatives:
  - "Docker only questions (use Docker-specific skill)"
  - "Terraform/IaC infrastructure (use infrastructure-as-code skill)"
  - "non-K8s container orchestration (Docker Swarm, Nomad, etc.)"
  - "CI/CD pipeline without K8s deployment context"
keywords:
  primary: "kubernetes agent skill"
  semantic_cluster:
    - "k8s-ai-operations"
    - "helm-charts-agent"
    - "gitops-automation"
    - "kubernetes-security-hardening"
    - "kubernetes-cost-optimization"
    - "multi-cloud-kubernetes"
    - "k8s-observability"
    - "kubernetes-compliance"
---

# Kubernetes Operations — Agent Skill

Production-grade Kubernetes operations for AI agents. Generates secure, scalable, multi-cloud K8s manifests and Helm charts with built-in failure-mode prevention, compliance validation, and structured output contracts.

---

## Core Workflow — 7-Step Failure-Mode Prevention

Every K8s response MUST follow this sequence. Skip a step → risk a failure mode.

```
Context → Diagnose → Reference → Design → Validate → Output → Rollback
```

| Step | Action | Deliverable |
|------|--------|-------------|
| **1. Context** | Identify target platform (EKS/GKE/AKS/OpenShift/k3s), cluster version, namespace, existing workloads, constraints | Context summary |
| **2. Diagnose** | Check for failure-mode exposures in the ask (see §Failure Modes) | Risk assessment |
| **3. Reference** | Pull current API versions, platform-specific defaults, security standards (PSS, CIS, NSA/CISA) | Reference baseline |
| **4. Design** | Build manifest/chart/policy with least-privilege, resource bounds, network isolation | Artifact draft |
| **5. Validate** | Run mental validation against all 8 failure modes, check API deprecations, verify security context | Validation pass/fail |
| **6. Output** | Emit structured output with assumptions, tradeoffs, and rollback instructions per §Output Contract | Final artifact + contract |
| **7. Rollback** | Provide `kubectl delete` / `helm uninstall` / `kubectl rollout undo` instructions | Rollback plan |

---

## Failure Modes — The 8 Ways K8s Goes Wrong

These are the failure modes this skill prevents. Every manifest review and generation MUST check all eight.

### FM-1: Insecure Workloads
**Symptom:** Container running as root, privileged mode, hostPath mounts, no securityContext.
**Prevention:** `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, drop ALL capabilities, add only required ones.
**Detection:** `kubectl get pods -o json | jq '.items[].spec.containers[].securityContext'`

### FM-2: Resource Starvation
**Symptom:** No requests/limits, unbounded memory growth, CPU throttling, OOMKilled.
**Prevention:** Always set `requests` = `limits` for Guaranteed QoS on critical workloads. Use `LimitRange` at namespace level.
**Detection:** `kubectl top pods --namespace=<ns>` and check for OOMKilled in pod status.

### FM-3: Network Exposure
**Symptom:** Missing NetworkPolicies, services exposed as LoadBalancer unnecessarily, no TLS termination.
**Prevention:** Deny-all ingress by default, explicit NetworkPolicy allowlists, TLS via cert-manager.
**Detection:** `kubectl get netpol --all-namespaces` and `kubectl get svc --all-namespaces | grep LoadBalancer`

### FM-4: Privilege Sprawl
**Symptom:** ClusterRoleBindings to `cluster-admin`, overly broad RBAC, service accounts with secrets access.
**Prevention:** Least-privilege RBAC, per-namespace Roles, service account token audiences restricted.
**Detection:** `kubectl get clusterrolebindings -o json | jq '.items[] | select(.roleRef.name=="cluster-admin")'`

### FM-5: Fragile Rollouts
**Symptom:** No health probes, no PDB, rolling update with single replica, no revision history.
**Prevention:** Readiness + liveness probes, PodDisruptionBudget, `revisionHistoryLimit: 10`, `minReadySeconds`.
**Detection:** `kubectl get deployment -o json | jq '.items[] | select(.spec.replicas==1 and .spec.strategy.type=="RollingUpdate")'`

### FM-6: API Drift
**Symptom:** Deprecated `extensions/v1beta1`, `apps/v1beta2`, `policy/v1beta1` PDB.
**Prevention:** Always check `kubectl api-resources` for current API version. Use `apps/v1` for Deployments, `policy/v1` for PDB.
**Detection:** `kubectl get --raw /apis | jq -r '.groups[].preferredVersion.groupVersion'`

### FM-7: GitOps Divergence — NEW
**Symptom:** Manual `kubectl apply` bypasses GitOps pipeline, cluster state drifts from Git, unrecorded changes.
**Prevention:** All changes through Git → Flux/ArgoCD reconciliation. `kubectl` for read-only and emergencies only.
**Detection:** `flux get kustomizations -A` or `argocd app diff <app>` to detect drift.

### FM-8: Multi-Cloud Skew — NEW
**Symptom:** EKS-specific annotations on GKE, AKS ingress class mismatch, OpenShift SCC violations.
**Prevention:** Platform-conditional manifest generation. Check cloud provider before emitting manifests.
**Detection:** Validate against provider-specific `kubectl api-resources` and admission webhooks.

---

## Platform Guidance

### Amazon EKS
- **Ingress:** AWS Load Balancer Controller (`kubernetes.io/ingress.class: alb`)
- **Storage:** EBS CSI driver (`gp3` default)
- **Auth:** IAM Roles for Service Accounts (IRSA) — `eks.amazonaws.com/role-arn` annotation
- **Networking:** VPC CNI, security groups for pods
- **Patching:** Bottlerocket OS recommended

### Google GKE
- **Ingress:** GKE Ingress Controller / Gateway API (`networking.gke.io/managed-certificates`)
- **Storage:** Compute Engine persistent disk CSI (`pd-standard`, `pd-ssd`)
- **Auth:** Workload Identity Federation (`iam.gke.io/gcp-service-account` annotation)
- **Networking:** Dataplane V2, NetworkPolicy logging via Cloud Logging
- **Patching:** GKE Autopilot for managed nodes

### Azure AKS
- **Ingress:** Application Gateway Ingress Controller (AGIC) or NGINX
- **Storage:** Azure Disk CSI / Azure Files CSI
- **Auth:** Microsoft Entra Workload ID (`azure.workload.identity/use: "true"`)
- **Networking:** Azure CNI with NetworkPolicy via Calico
- **Patching:** AKS node image auto-upgrade

### Red Hat OpenShift
- **Ingress:** OpenShift Router (HAProxy-based, `route.openshift.io`)
- **Security:** Security Context Constraints (SCC) — `restricted-v2` as default, drop ALL caps mandatory
- **Storage:** OpenShift Data Foundation / any CSI
- **Auth:** OAuth integrated, no IRSA equivalent — use `serviceAccount` annotations
- **Patching:** Cluster Version Operator (CVO) managed

---

## Security

### Pod Security Standards (PSS)
```
restricted (default recommended)
  - runAsNonRoot: true
  - seccompProfile: RuntimeDefault
  - capabilities.drop: ["ALL"]
  - readOnlyRootFilesystem: true (where feasible)
  - allowPrivilegeEscalation: false
```

**Namespace labeling:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### RBAC Least-Privilege Patterns

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: app-ns
  name: app-deployer
rules:
- apiGroups: ["apps", ""]
  resources: ["deployments", "pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
# NO delete, NO secrets access, NO cluster-wide verbs
```

### NetworkPolicy — Deny-All + Allowlist

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### OWASP Kubernetes Top 10 (Rapid Reference)
1. Insecure workload configurations → FM-1
2. Supply chain vulnerabilities → Image scanning (Trivy/Grype)
3. Overly permissive RBAC → FM-4
4. Lack of centralized policy enforcement → OPA/Gatekeeper, Kyverno
5. Inadequate logging & monitoring → FM-8 Observability
6. Broken authentication → Service account token hygiene
7. Missing network segmentation → FM-3
8. Secrets management failures → §Secret Management
9. Misconfigured cluster components → CIS benchmarks
10. Outdated/vulnerable K8s components → FM-6

### NSA/CISA Kubernetes Hardening Guidance
- Scan container images for vulnerabilities
- Run containers as non-root
- Use network segmentation (NetworkPolicies)
- Encrypt secrets at rest (etcd encryption)
- Enable audit logging
- Use service mesh for mTLS (Istio/Linkerd)
- Regularly update cluster components

### CIS Kubernetes Benchmarks
- 1.1: API server — AlwaysPullImages admission plugin
- 1.2: Scheduler — profiling disabled
- 4.1: Worker node — kubelet `--protect-kernel-defaults=true`
- 5.1: RBAC — minimize `cluster-admin` bindings
- 5.2: Pod Security Standards — restricted enforcement
- 5.3: Network Policies — namespaced default deny

---

## Helm Chart Generation & Review

### Chart Structure
```
mychart/
├── Chart.yaml          # name, version, appVersion, dependencies
├── values.yaml         # Default values with documentation
├── values/             # Multi-environment overrides (values-prod.yaml, values-staging.yaml)
├── templates/
│   ├── _helpers.tpl    # Reusable template functions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── serviceaccount.yaml
│   ├── networkpolicy.yaml
│   └── NOTES.txt       # Post-install instructions
├── templates/tests/    # Helm test pod definitions
├── crds/               # Custom Resource Definitions
└── README.md
```

### values.yaml Patterns
```yaml
# ALWAYS document every value
replicaCount: 3

image:
  repository: nginx
  tag: "1.25"
  pullPolicy: IfNotPresent
  # pullSecrets for private registries
  pullSecrets: []

# Security context as a named block — reusable
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop: ["ALL"]

# Resource defaults — MUST be set
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

# Autoscaling
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# Probes with sensible defaults
probes:
  liveness:
    httpGet:
      path: /healthz
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
  readiness:
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 5

# Pod disruption budget
pdb:
  enabled: true
  minAvailable: 1

# Ingress with TLS
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.example.com

# Network policy
networkPolicy:
  enabled: true
  ingressAllow:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ingress-nginx
  egressAllow:
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              app: database
      ports:
        - port: 5432
          protocol: TCP

# Service account with annotations for cloud IAM
serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/app-role"  # EKS IRSA
    # iam.gke.io/gcp-service-account: "app@project.iam.gserviceaccount.com"  # GKE WI
    # azure.workload.identity/use: "true"  # AKS WI

# Tolerations & node affinity
tolerations: []
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values: ["myapp"]
          topologyKey: kubernetes.io/hostname

# Topology spread constraints — zone-level HA
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: myapp

nodeSelector: {}
# platform-specific:
# EKS: nodeSelector: { "eks.amazonaws.com/capacityType": "ON_DEMAND" }
# GKE: nodeSelector: { "cloud.google.com/gke-nodepool": "default-pool" }
```

### Dependency Management
```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: "18.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
  - name: postgresql
    version: "15.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
```

**Multi-environment deployment:**
```bash
# Staging
helm upgrade --install myapp ./mychart -f values.yaml -f values/staging.yaml -n staging

# Production
helm upgrade --install myapp ./mychart -f values.yaml -f values/prod.yaml -n production
```

---

## GitOps Integration

### Flux CD Pattern
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/myapp-deploy
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  path: ./overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production
  postBuild:
    substitute:
      ENV: production
```

### ArgoCD Pattern
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/myapp-deploy
    targetRevision: main
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 30s
        factor: 2
        maxDuration: 5m
```

---

## Resource Management

### Requests & Limits
| Workload Type | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------------|-------------|-----------|----------------|--------------|
| Burstable API | 100m | 500m | 128Mi | 256Mi |
| Guaranteed DB | 500m | 500m | 2Gi | 2Gi |
| Background Job | 50m | 200m | 64Mi | 128Mi |

```yaml
# Pod with Guaranteed QoS (requests == limits)
resources:
  requests:
    cpu: "500m"
    memory: "2Gi"
  limits:
    cpu: "500m"
    memory: "2Gi"
```

### HPA (Horizontal Pod Autoscaler)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### VPA vs HPA Decision Matrix
- **HPA:** Stateless workloads, request-driven scaling, predictable patterns
- **VPA:** Stateful workloads, right-sizing after profiling, JVM heap tuning
- **Both:** Use VPA in recommendation mode (`updateMode: "Off"`) with HPA for execution

### Priority Classes
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "Critical production workloads"
---
# System-critical (never evicted): 2000000000
# Production high: 1000000
# Production default: 100000
# Batch / non-critical: -1
```

---

## Cost Optimization

### Right-Sizing
- Use `kubectl top pods` + VPA recommender to profile actual usage
- Set requests at P95 of observed usage, not guesstimates
- Run `kubecost` or `opencost` for namespace-level cost allocation

### Spot Instances
```yaml
# EKS
spec:
  nodeSelector:
    eks.amazonaws.com/capacityType: SPOT
  tolerations:
  - key: "eks.amazonaws.com/capacityType"
    operator: "Equal"
    value: "SPOT"
    effect: "NoSchedule"

# GKE
spec:
  nodeSelector:
    cloud.google.com/gke-spot: "true"
  tolerations:
  - key: "cloud.google.com/gke-spot"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"

# AKS
spec:
  nodeSelector:
    kubernetes.azure.com/scalesetpriority: spot
  tolerations:
  - key: "kubernetes.azure.com/scalesetpriority"
    operator: "Equal"
    value: "spot"
    effect: "NoSchedule"
```

### Cluster Autoscaler
- Set min/max on node groups, not on individual deployments
- Use `cluster-autoscaler.kubernetes.io/safe-to-evict: "true"` on pods that can move
- Apply PDBs so autoscaler respects availability during scale-down

### Workload Rightsizing Rules
1. **Never run without limits.** Use LimitRange to enforce defaults
2. **Burstable for dev/staging.** Guaranteed for production databases and stateful sets
3. **Preemptible nodes for batch.** Tolerations + nodeSelectors
4. **HPA over static replicas.** Let metrics drive scaling decisions

---

## Observability

### Prometheus Metrics
```yaml
# Pod annotations for Prometheus scraping
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"

# ServiceMonitor (Prometheus Operator)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Structured Logging
```yaml
# Sidecar or daemonset pattern — emit JSON to stdout
# Containers should log to stdout/stderr in JSON format:
# {"level":"info","ts":"2026-06-18T02:06:00Z","msg":"request","method":"GET","path":"/api","duration_ms":42,"status":200}

# Use Fluent Bit or Vector as DaemonSet for log collection:
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      serviceAccountName: fluent-bit
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:3.1
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
```

### OpenTelemetry
```yaml
# Instrument with OTel SDK, configure via OTEL_EXPORTER_OTLP_ENDPOINT
env:
- name: OTEL_EXPORTER_OTLP_ENDPOINT
  value: "http://otel-collector.observability:4317"
- name: OTEL_SERVICE_NAME
  value: "myapp"
- name: OTEL_RESOURCE_ATTRIBUTES
  value: "deployment.environment=production,cloud.provider=aws"

# OpenTelemetry Collector — sidecar pattern
# OR use the OpenTelemetry Operator for auto-instrumentation
```

### Golden Signals Dashboard (Grafana / Datadog / New Relic)
- **Latency:** P50, P95, P99 of request duration
- **Traffic:** Requests per second
- **Errors:** 5xx rate + error budget burn rate
- **Saturation:** CPU throttle %, memory pressure, goroutine count

### Alert Rules (Prometheus)
```yaml
groups:
- name: app
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Error rate > 1% for {{ $labels.app }}"
  - alert: PodRestarting
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: warning
```

---

## Secret Management

### External Secrets Operator (ESO)
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager  # or gcp-secretmanager, azure-keyvault
    kind: ClusterSecretStore
  target:
    name: myapp-secrets
    creationPolicy: Owner
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: prod/myapp/database-url
  - secretKey: API_KEY
    remoteRef:
      key: prod/myapp/api-key
```

### Sealed Secrets
```bash
# Encrypt a secret for GitOps
kubectl create secret generic mysecret --from-literal=password=s3cret --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system --format yaml > sealed-secret.yaml
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysecret
  namespace: production
spec:
  encryptedData:
    password: AgBy8hCKF...encrypted_base64...
```

### Secret Management Decision Tree
| Scenario | Solution |
|----------|----------|
| Cloud-native, existing secrets manager | External Secrets Operator |
| GitOps, no external dependency | Sealed Secrets |
| Dynamic secrets (DB creds, PKI) | Vault + Vault CSI Provider |
| Simple, single-cluster | Kubernetes Secrets + etcd encryption |
| Multi-cluster, audit trail | Vault with Kubernetes auth method |

---

## Multi-Cloud Deployment Patterns

### Conditional Manifests (Helm)
```yaml
# templates/ingress.yaml
{{- if eq .Values.cloudProvider "aws" }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  # ...
{{- else if eq .Values.cloudProvider "gcp" }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: gce
    networking.gke.io/managed-certificates: myapp-cert
  # ...
{{- end }}
```

### Node Selectors & Taints/Tolerations
```yaml
# EKS — Spot node pool
nodeSelector:
  eks.amazonaws.com/capacityType: SPOT
tolerations:
- key: "eks.amazonaws.com/capacityType"
  operator: "Equal"
  value: "SPOT"
  effect: "NoSchedule"

# GKE — GPU node pool
nodeSelector:
  cloud.google.com/gke-accelerator: nvidia-l4
tolerations:
- key: "nvidia.com/gpu"
  operator: "Exists"
  effect: "NoSchedule"

# AKS — Memory-optimized node pool
nodeSelector:
  agentpool: memoryoptimized
```

### Cloud-Agnostic Abstraction
```yaml
# Use Kubernetes-native primitives, not cloud-specific ones
# Good: Ingress + cert-manager (works everywhere with proper controller)
# Bad: Cloud-specific LoadBalancer annotations hardcoded

# For cloud-specific features, use Helm template functions:
{{- define "app.cloudConfig" -}}
{{- if eq .Values.cloudProvider "aws" }}
serviceAccountAnnotations:
  eks.amazonaws.com/role-arn: {{ .Values.aws.roleArn }}
{{- else if eq .Values.cloudProvider "gcp" }}
serviceAccountAnnotations:
  iam.gke.io/gcp-service-account: {{ .Values.gcp.serviceAccount }}
{{- else if eq .Values.cloudProvider "azure" }}
podLabels:
  azure.workload.identity/use: "true"
{{- end }}
{{- end }}
```

---

## Output Contract

Every response that produces K8s artifacts MUST include:

### Required Sections
1. **Assumptions:** What you assumed about the environment
2. **Tradeoffs:** What you chose and why (e.g., Guaranteed vs Burstable QoS)
3. **Rollback Instructions:** Exact `kubectl delete` / `helm uninstall` / `kubectl rollout undo` commands

```markdown
### Assumptions
- Target cluster: EKS 1.30, namespace: `production`
- You have cert-manager and AWS Load Balancer Controller installed
- IRSA is configured for service account IAM roles

### Tradeoffs
- Chose Guaranteed QoS for the database pod (slight over-provision, but predictable performance)
- Used Burstable QoS for the API (cost-effective, acceptable for stateless workloads)
- Disabled privilege escalation even though it breaks some debugging tools — security over convenience

### Rollback
\`\`\`bash
kubectl delete -f manifest.yaml
# OR for Helm:
helm uninstall myapp -n production
# OR to undo last rollout:
kubectl rollout undo deployment/myapp -n production
\`\`\`
```

---

## DO / DON'T

### ✅ DO
```yaml
# DO: Complete security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

# DO: Both probes
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
readinessProbe:
  httpGet:
    path: /ready
    port: 8080

# DO: Resource requests AND limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

# DO: Namespace labels for PSS
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted

# DO: Use current API versions
apiVersion: apps/v1
apiVersion: networking.k8s.io/v1
apiVersion: policy/v1

# DO: Pod anti-affinity for HA
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: myapp
      topologyKey: kubernetes.io/hostname

# DO: Topology spread for zone HA
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway

# DO: Provide PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 1
```

### ❌ DON'T
```yaml
# DON'T: No security context
spec:
  containers:
  - name: app
    image: myapp:latest
    # securityContext is MISSING — FM-1

# DON'T: Running as root
securityContext:
  runAsUser: 0  # NO — FM-1

# DON'T: Privileged container
securityContext:
  privileged: true  # NO — FM-1, NEVER in production

# DON'T: hostPath mounts without extreme caution
volumes:
- name: dangerous
  hostPath:
    path: /var/run/docker.sock  # NO — FM-1, container escape risk

# DON'T: No resource limits
resources: {}  # NO — FM-2

# DON'T: No health probes — FM-5
# No livenessProbe or readinessProbe defined

# DON'T: Deprecated API versions — FM-6
apiVersion: extensions/v1beta1  # DEPRECATED since 1.16

# DON'T: Single replica without PDB — FM-5
spec:
  replicas: 1
  # No PodDisruptionBudget defined

# DON'T: Overly broad RBAC — FM-4
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]  # NO — just use cluster-admin if you need this

# DON'T: No NetworkPolicy — FM-3
# Default deny NetworkPolicy must exist in every namespace

# DON'T: Hardcoded cloud provider specifics — FM-8
annotations:
  eks.amazonaws.com/role-arn: "..."  # OK if target is known EKS, NOT OK as generic manifest

# DON'T: kubectl apply for GitOps-managed resources — FM-7
# Use Git → Flux/ArgoCD path instead
```

---

## Quick Reference Cards

### Minimal Production-Ready Deployment Checklist
- [ ] `securityContext` with `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, capabilities drop ALL
- [ ] `readinessProbe` AND `livenessProbe` defined
- [ ] `resources.requests` AND `resources.limits` set for all containers
- [ ] HPA with `minReplicas >= 2` for stateless workloads
- [ ] PodAntiAffinity or TopologySpreadConstraints for HA
- [ ] PodDisruptionBudget with `minAvailable: 1` or `maxUnavailable: 1`
- [ ] ServiceAccount with cloud IAM annotations (if cloud managed)
- [ ] NetworkPolicy — deny-all + explicit allowlist
- [ ] PSS namespace labels (`enforce: restricted`)
- [ ] No deprecated API versions (`kubectl api-resources` verified)
- [ ] Secrets externalized (ESO/SealedSecrets/Vault), NOT in plain ConfigMap
- [ ] Prometheus scrape annotations or ServiceMonitor

### Troubleshooting Quick Commands
```bash
# Pod won't start
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --previous

# Resource issues
kubectl top pods -n <ns>
kubectl get events -n <ns> --sort-by='.lastTimestamp'

# RBAC issues
kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa> -n <ns>

# Network issues
kubectl run tmp --rm -it --image=nicolaka/netshoot -n <ns> -- /bin/bash
# Then: curl, nc, dig, tcpdump from inside cluster

# Drift detection (Flux)
flux get kustomizations -A --status-selector ready=false

# Drift detection (ArgoCD)
argocd app diff <app>

# API version check
kubectl api-resources --verbs=list -o wide
kubectl explain deployment --api-version=apps/v1
```

---

## Evaluation

See `evals/eval_cases.json` for trigger match test cases and near-miss negatives.

## References

- `references/k8s-security-hardening.md` — Full security reference: PSS, RBAC, NetworkPolicies, OWASP Top 10
- `references/k8s-failure-modes.md` — All 8 failure modes with detection and remediation
- `references/helm-patterns.md` — Helm chart architecture, multi-env patterns, dependency management

## Scripts

- `scripts/validate-k8s-manifest.sh` — Validate K8s YAML against schemas (kubeval/kubeconform)
- `scripts/security-scan-k8s.sh` — Security scan for K8s manifests (kubesec, privileged checks)
