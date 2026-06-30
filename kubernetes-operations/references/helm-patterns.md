# Helm Chart Patterns & Best Practices

Complete reference for Helm chart architecture, values.yaml patterns, dependency management, and multi-environment deployment strategies for the kubernetes-operations skill.

---

## 1. Chart Structure (Production Standard)

```
mychart/
├── .helmignore                    # Files to exclude from packaging
├── Chart.yaml                     # Chart metadata and dependencies
├── values.yaml                    # Default values with inline documentation
├── values.schema.json             # JSON schema for values validation
├── values/                        # Environment-specific overrides
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── templates/
│   ├── _helpers.tpl               # Named templates and shared functions
│   ├── NOTES.txt                  # Post-install instructions
│   ├── deployment.yaml            # Core workload
│   ├── service.yaml               # Service exposure
│   ├── ingress.yaml               # Ingress rules
│   ├── hpa.yaml                   # Horizontal Pod Autoscaler
│   ├── pdb.yaml                   # Pod Disruption Budget
│   ├── serviceaccount.yaml        # ServiceAccount with IAM annotations
│   ├── networkpolicy.yaml         # Network security
│   ├── configmap.yaml             # Non-sensitive configuration
│   ├── secret.yaml                # Only if NOT using ESO/Vault
│   ├── servicemonitor.yaml        # Prometheus Operator integration
│   └── externalsecret.yaml        # External Secrets Operator
├── templates/tests/               # Helm test pod definitions
│   └── test-connection.yaml
├── crds/                          # Custom Resource Definitions (if needed)
├── charts/                        # Vendored dependencies (helm dependency update)
└── README.md                      # Usage documentation
```

### .helmignore
```
.git/
.gitignore
.helmignore
Makefile
README.md
*.md
values/
ci/
```

---

## 2. Chart.yaml — Complete Example

```yaml
apiVersion: v2
name: myapp
description: Production microservice with autoscaling, TLS, and observability
type: application
version: 1.5.0
appVersion: "2.3.1"
kubeVersion: ">=1.27.0-0"

keywords:
  - api
  - microservice
  - nodejs
  - production

home: https://github.com/org/myapp
sources:
  - https://github.com/org/myapp
maintainers:
  - name: platform-team
    email: platform@example.com

dependencies:
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
    tags:
      - caching
  - name: postgresql
    version: "15.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
    tags:
      - database
  - name: opentelemetry-collector
    version: "0.90.x"
    repository: https://open-telemetry.github.io/opentelemetry-helm-charts
    condition: otel.enabled

annotations:
  category: Application
  licenses: MIT
```

---

## 3. _helpers.tpl — Essential Named Templates

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ .Chart.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Security Context — reusable across all containers
*/}}
{{- define "myapp.securityContext" -}}
securityContext:
  runAsNonRoot: true
  runAsUser: {{ .Values.securityContext.runAsUser }}
  runAsGroup: {{ .Values.securityContext.runAsGroup }}
  fsGroup: {{ .Values.securityContext.fsGroup }}
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop:
    - ALL
    {{- with .Values.securityContext.capabilities.add }}
    add:
    {{- toYaml . | nindent 4 }}
    {{- end }}
  readOnlyRootFilesystem: {{ .Values.securityContext.readOnlyRootFilesystem }}
  allowPrivilegeEscalation: false
{{- end }}

{{/*
Pod Annotations — metrics, tracing, config checksums
*/}}
{{- define "myapp.podAnnotations" -}}
prometheus.io/scrape: {{ .Values.metrics.enabled | quote }}
prometheus.io/port: {{ .Values.metrics.port | quote }}
prometheus.io/path: {{ .Values.metrics.path | quote }}
{{- if .Values.configChecksum }}
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
{{- end }}
{{- if .Values.secretChecksum }}
checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
{{- end }}
{{- end }}

{{/*
Service Account Annotations — cloud IAM
*/}}
{{- define "myapp.serviceAccountAnnotations" -}}
{{- if eq .Values.cloudProvider "aws" }}
eks.amazonaws.com/role-arn: {{ .Values.iam.roleArn }}
{{- else if eq .Values.cloudProvider "gcp" }}
iam.gke.io/gcp-service-account: {{ .Values.iam.serviceAccount }}
{{- else if eq .Values.cloudProvider "azure" }}
azure.workload.identity/client-id: {{ .Values.iam.clientId }}
{{- end }}
{{- end }}

{{/*
Resource block — QoS-aware
*/}}
{{- define "myapp.resources" -}}
resources:
  requests:
    cpu: {{ .Values.resources.requests.cpu }}
    memory: {{ .Values.resources.requests.memory }}
  limits:
    {{- if eq .Values.resources.qosClass "Guaranteed" }}
    cpu: {{ .Values.resources.requests.cpu }}
    memory: {{ .Values.resources.requests.memory }}
    {{- else }}
    cpu: {{ .Values.resources.limits.cpu }}
    memory: {{ .Values.resources.limits.memory }}
    {{- end }}
{{- end }}
```

---

## 4. values.yaml — Complete Defaults

```yaml
# =============================================================================
# DEFAULT VALUES — Override per environment: values/<env>.yaml
# =============================================================================

# -- Chart metadata overrides
nameOverride: ""
fullnameOverride: ""

# -- Target cloud provider: aws | gcp | azure | openshift | generic
cloudProvider: generic

# -- Number of replicas (overridden by HPA if enabled)
replicaCount: 3

# -- Container image
image:
  repository: org/myapp
  tag: "2.3.1"
  pullPolicy: IfNotPresent
  pullSecrets: []

# -- Security context — PSS restricted compliant
securityContext:
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  readOnlyRootFilesystem: true
  capabilities:
    add: []
    # add: ["NET_BIND_SERVICE"]  # Only if binding to port < 1024

# -- Service configuration
service:
  type: ClusterIP
  port: 8080
  targetPort: 8080
  protocol: TCP
  annotations: {}

# -- Ingress configuration
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

# -- Resource allocation
resources:
  qosClass: Burstable  # Burstable | Guaranteed
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

# -- Autoscaling (HPA v2)
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
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

# -- Health probes
probes:
  liveness:
    enabled: true
    httpGet:
      path: /healthz
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readiness:
    enabled: true
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3
  startup:
    enabled: false
    httpGet:
      path: /healthz
      port: 8080
    initialDelaySeconds: 0
    periodSeconds: 5
    failureThreshold: 30

# -- Pod Disruption Budget
pdb:
  enabled: true
  minAvailable: 1
  # maxUnavailable: 1

# -- Service Account
serviceAccount:
  create: true
  name: ""
  annotations: {}
  automountServiceAccountToken: true

# -- Cloud IAM configuration (provider-specific)
iam:
  # EKS IRSA
  roleArn: ""
  # GKE Workload Identity
  serviceAccount: ""
  # AKS Workload ID
  clientId: ""

# -- Network Policy
networkPolicy:
  enabled: true
  # Namespace labels that can send ingress traffic
  ingressNamespaces:
    - kubernetes.io/metadata.name: ingress-nginx
  # External CIDRs allowed for egress
  egressCIDRs: []
  # - 10.0.0.0/8
  # Egress to specific services
  egressServices:
    # External APIs
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - port: 443
          protocol: TCP
        - port: 53
          protocol: UDP

# -- Metrics (Prometheus)
metrics:
  enabled: true
  port: 8080
  path: /metrics
  serviceMonitor:
    enabled: false
    interval: 30s

# -- OpenTelemetry
otel:
  enabled: false
  endpoint: http://otel-collector.observability:4317

# -- Environment variables (non-sensitive)
env:
  NODE_ENV: production
  LOG_FORMAT: json

# -- Environment variables from ConfigMaps/Secrets
envFrom: []
# - configMapRef:
#     name: myapp-config
# - secretRef:
#     name: myapp-secrets

# -- ConfigMap data (non-sensitive config)
config:
  enabled: true
  data:
    app.yaml: |
      server:
        port: 8080
        readTimeout: 30s
      logging:
        level: info
        format: json

# -- External Secrets (ESO integration)
externalSecrets:
  enabled: false
  refreshInterval: 1h
  storeRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  data: []
  # - secretKey: DATABASE_URL
  #   remoteRef:
  #     key: /prod/myapp/DATABASE_URL

# -- Pod scheduling
podAnnotations: {}
podLabels: {}

# Check podAntiAffinity defaults below for HA scheduling
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: myapp
          topologyKey: kubernetes.io/hostname

# Topology spread across zones
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: myapp

# Node selector — platform-specific, override in values/<env>.yaml
nodeSelector: {}
# EKS spot: { "eks.amazonaws.com/capacityType": "SPOT" }
# GKE spot: { "cloud.google.com/gke-spot": "true" }

# Tolerations — override per environment
tolerations: []

# Priority class
priorityClassName: ""

# -- Pod lifecycle hooks
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]  # Graceful drain

# -- Termination grace period
terminationGracePeriodSeconds: 60

# -- Update strategy
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0

# -- Revision history for rollback
revisionHistoryLimit: 10

# -- Config checksums (roll pods on config change)
configChecksum: false
secretChecksum: false

# -- Extra volumes and volume mounts
extraVolumes: []
extraVolumeMounts: []

# -- Init containers
initContainers: []

# -- Dependency flags
redis:
  enabled: false
postgresql:
  enabled: false
otel:
  enabled: false
```

---

## 5. Environment Override Files

### values/dev.yaml — Development
```yaml
replicaCount: 1
cloudProvider: generic

image:
  tag: latest
  pullPolicy: Always

resources:
  qosClass: Burstable
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi

autoscaling:
  enabled: false

ingress:
  enabled: false
  # Use port-forward for dev

probes:
  liveness:
    initialDelaySeconds: 60
  readiness:
    initialDelaySeconds: 15

externalSecrets:
  enabled: false  # Use local secrets in dev

config:
  data:
    app.yaml: |
      server:
        port: 8080
        readTimeout: 10s
      logging:
        level: debug
        format: text

metrics:
  serviceMonitor:
    enabled: false

networkPolicy:
  enabled: false  # Open networking in dev

pdb:
  enabled: false

# Dev uses local postgres
postgresql:
  enabled: true
  auth:
    username: app
    password: devpassword
    database: app_dev
```

### values/staging.yaml — Staging
```yaml
replicaCount: 2
cloudProvider: aws

image:
  tag: staging
  pullPolicy: IfNotPresent

resources:
  qosClass: Burstable
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5

ingress:
  enabled: true
  hosts:
    - host: app.staging.example.com
  tls:
    - secretName: app-staging-tls
      hosts:
        - app.staging.example.com

iam:
  roleArn: "arn:aws:iam::111111111111:role/app-staging"

externalSecrets:
  enabled: true
  refreshInterval: 30m
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: /staging/myapp/DATABASE_URL
    - secretKey: API_KEY
      remoteRef:
        key: /staging/myapp/API_KEY

config:
  data:
    app.yaml: |
      server:
        port: 8080
      logging:
        level: info
        format: json

networkPolicy:
  enabled: true

pdb:
  enabled: true
  minAvailable: 1

nodeSelector:
  eks.amazonaws.com/capacityType: SPOT

otel:
  enabled: true
  endpoint: http://otel-collector.observability:4317
```

### values/prod.yaml — Production
```yaml
replicaCount: 3
cloudProvider: aws

image:
  tag: "2.3.1"  # Explicit version, never :latest
  pullPolicy: IfNotPresent

resources:
  qosClass: Guaranteed
  requests:
    cpu: 500m
    memory: 2Gi
  limits:
    cpu: 500m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/limit-rps: "100"
  hosts:
    - host: app.example.com
  tls:
    - secretName: app-prod-tls
      hosts:
        - app.example.com

iam:
  roleArn: "arn:aws:iam::222222222222:role/app-prod"

externalSecrets:
  enabled: true
  refreshInterval: 15m
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: /prod/myapp/DATABASE_URL
    - secretKey: API_KEY
      remoteRef:
        key: /prod/myapp/API_KEY

config:
  data:
    app.yaml: |
      server:
        port: 8080
        readTimeout: 30s
      logging:
        level: info
        format: json

metrics:
  serviceMonitor:
    enabled: true
    interval: 30s

networkPolicy:
  enabled: true

pdb:
  enabled: true
  minAvailable: 2

affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app.kubernetes.io/name: myapp
        topologyKey: kubernetes.io/hostname

nodeSelector:
  eks.amazonaws.com/capacityType: ON_DEMAND

otel:
  enabled: true
  endpoint: http://otel-collector.observability:4317

priorityClassName: production-critical

# Unique checksums trigger pod restart on config changes
configChecksum: true
```

---

## 6. Deployment Commands

### Local Development
```bash
# Template rendering (dry-run)
helm template myapp ./mychart -f values.yaml -f values/dev.yaml

# Lint
helm lint ./mychart -f values.yaml -f values/dev.yaml

# Install to dev cluster
helm upgrade --install myapp ./mychart \
  -f values.yaml \
  -f values/dev.yaml \
  -n dev \
  --create-namespace \
  --wait \
  --timeout 5m
```

### CI/CD Pipeline
```bash
# Template + validate
helm template myapp ./mychart -f values.yaml -f values/staging.yaml | \
  kubeconform -kubernetes-version 1.30 -strict -summary

# Security scan
helm template myapp ./mychart -f values.yaml -f values/prod.yaml | \
  kubesec scan -

# Install to staging
helm upgrade --install myapp ./mychart \
  -f values.yaml \
  -f values/staging.yaml \
  -n staging \
  --atomic \
  --timeout 10m

# Install to production (after approval)
helm upgrade --install myapp ./mychart \
  -f values.yaml \
  -f values/prod.yaml \
  -n production \
  --atomic \
  --timeout 15m \
  --set image.tag="${GIT_SHA}"
```

### Rollback
```bash
# List history
helm history myapp -n production

# Rollback to previous
helm rollback myapp -n production

# Rollback to specific revision
helm rollback myapp 5 -n production

# Full uninstall
helm uninstall myapp -n production
```

---

## 7. Dependency Management

### Updating Dependencies
```bash
# Update Chart.lock with latest compatible versions
helm dependency update ./mychart

# Build dependencies (vendors charts/ directory)
helm dependency build ./mychart

# List dependencies
helm dependency list ./mychart
```

### Conditional Dependencies
```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled         # Controlled by values.yaml
    tags:
      - caching
```

```yaml
# values/prod.yaml
redis:
  enabled: false  # Uses AWS ElastiCache instead

# values/dev.yaml
redis:
  enabled: true   # Bundled Redis for local dev
```

### Subchart Value Overrides

```yaml
# Override subchart values through the dependency key
# values.yaml
redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: false
  master:
    persistence:
      enabled: false

postgresql:
  enabled: true
  auth:
    username: app
    database: myapp
    existingSecret: postgres-creds
  primary:
    persistence:
      size: 10Gi
```

---

## 8. NOTES.txt — Post-Install Instructions

```txt
{{- if .Values.ingress.enabled }}
🌐 Application URL:
  https://{{ (index .Values.ingress.hosts 0).host }}

{{- end }}
📊 Monitoring:
{{- if .Values.metrics.serviceMonitor.enabled }}
  ServiceMonitor created. Check Prometheus targets.
{{- else if .Values.metrics.enabled }}
  Metrics available at port {{ .Values.metrics.port }}{{ .Values.metrics.path }}
{{- end }}

🔍 Check deployment status:
  kubectl get pods -n {{ .Release.Namespace }} -l app.kubernetes.io/name={{ include "myapp.name" . }}

📋 View logs:
  kubectl logs -n {{ .Release.Namespace }} -l app.kubernetes.io/name={{ include "myapp.name" . }} -f

{{- if .Values.autoscaling.enabled }}
📈 HPA status:
  kubectl get hpa -n {{ .Release.Namespace }}
{{- end }}

{{- if .Values.pdb.enabled }}
🛡 Pod Disruption Budget:
  kubectl get pdb -n {{ .Release.Namespace }}
{{- end }}

🔄 Rollback:
  helm rollback {{ .Release.Name }} -n {{ .Release.Namespace }}
```

---

## 9. Multi-Environment GitOps Layout

```
deploy/
├── base/                         # Kustomize base (cloud-agnostic)
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── networkpolicy.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   ├── kustomization.yaml   # patches + images + configMapGenerator
│   │   └── patches/
│   ├── production/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── production-eks/
│   │   ├── kustomization.yaml   # Cloud-specific overlay
│   │   └── patches/
│   └── production-gke/
│       ├── kustomization.yaml
│       └── patches/
└── flux/
    ├── sources/
    │   └── myapp-gitrepository.yaml
    └── kustomizations/
        ├── myapp-staging.yaml
        └── myapp-production.yaml
```

### Helm + Kustomize Hybrid Approach

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# Use Helm chart as base
helmCharts:
- name: myapp
  repo: oci://ghcr.io/org/charts
  version: 1.5.0
  releaseName: myapp
  namespace: production
  valuesFile: ../../helm/values/prod.yaml
  includeCRDs: true

# Kustomize patches on top of Helm output
patchesStrategicMerge:
  - patches/node-selector.yaml
  - patches/extra-labels.yaml

# Override image tag
images:
- name: org/myapp
  newTag: 2.3.1

configMapGenerator:
- name: app-overrides
  behavior: merge
  literals:
    - LOG_LEVEL=warn
    - FEATURE_FLAG_NEW_UI=true
```

---

## 10. Helm Best Practices Checklist

### Chart Design
- [ ] `Chart.yaml` has `apiVersion: v2`, `type: application`
- [ ] `appVersion` is set to the container image tag
- [ ] `kubeVersion` constraint specified (`>=1.27.0-0`)
- [ ] Dependencies use `condition` for conditional install
- [ ] `.helmignore` excludes dev files

### Templates
- [ ] `_helpers.tpl` defines `name`, `fullname`, `labels`, `selectorLabels`
- [ ] All templates use `{{ include "myapp.labels" . | nindent 4 }}`
- [ ] Resource names use `{{ include "myapp.fullname" . }}`
- [ ] No hardcoded `namespace:` — let `helm install -n` handle it
- [ ] NOTES.txt provides actionable post-install instructions

### Values
- [ ] Every value has a comment explaining its purpose
- [ ] `values.yaml` is the DEFAULT (dev-friendly), not production-tuned
- [ ] Sensible defaults: `replicaCount: 1`, probes enabled, PDB disabled by default
- [ ] Production overrides in `values/prod.yaml`, not in `values.yaml`
- [ ] `resources.requests` and `resources.limits` are ALWAYS set

### Security
- [ ] `securityContext` enforced via template helper, not copy-pasted
- [ ] `runAsNonRoot: true` in all security contexts
- [ ] `readOnlyRootFilesystem: true` unless writable filesystem is required
- [ ] `capabilities.drop: [ALL]` with explicit adds for required caps only
- [ ] Secrets use ESO/SealedSecrets, never plaintext in values

### Operations
- [ ] README.md explains setup, dependencies, and configuration
- [ ] `helm lint` passes with no errors
- [ ] `helm template` output passes `kubeconform` validation
- [ ] `helm test` pods defined for smoke testing
- [ ] Rollback instructions in NOTES.txt

### Multi-Environment
- [ ] Dev uses `replicaCount: 1`, no HPA, no PDB
- [ ] Staging mirrors production config but at reduced scale
- [ ] Production uses Guaranteed QoS, PDB `minAvailable >= 2`, explicit image tags
- [ ] Cloud-specific config is in values overlays, NOT hardcoded
- [ ] CI/CD validates against all target environments before deploy

---

## References

- [Helm Chart Best Practices Guide](https://helm.sh/docs/chart_best_practices/)
- [Helm Template Function List](https://helm.sh/docs/chart_template_guide/function_list/)
- [Bitnami Helm Charts](https://github.com/bitnami/charts)
- [Artifact Hub](https://artifacthub.io/)