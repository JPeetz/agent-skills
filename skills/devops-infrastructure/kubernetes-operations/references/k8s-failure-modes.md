# Kubernetes Failure Modes — Detection & Remediation

Comprehensive reference for the 8 failure modes identified by the kubernetes-operations skill. Each mode includes symptoms, detection commands, prevention patterns, and remediation steps.

---

## FM-1: Insecure Workloads

### Description
Container workloads running with excessive privileges: root user, privileged mode, hostPath mounts, missing or weak securityContext, capabilities not dropped.

### Severity: CRITICAL

### Symptoms
- `kubectl describe pod` shows no `securityContext` or `privileged: true`
- Pod can access host filesystem
- Container UID is 0 (root)
- Capabilities like `SYS_ADMIN`, `NET_ADMIN` present

### Detection

```bash
# Find privileged containers
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[].securityContext.privileged == true) | .metadata.name'

# Find containers running as root
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[].securityContext.runAsUser == 0 or .spec.containers[].securityContext.runAsNonRoot == false) | .metadata.name'

# Find hostPath mounts
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.volumes[]?.hostPath) | {name: .metadata.name, paths: [.spec.volumes[].hostPath.path]}'

# Find pods missing securityContext entirely
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[] | has("securityContext") | not) | .metadata.name'
```

### Prevention — Full Security Context

```yaml
spec:
  containers:
  - name: app
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 1000
      fsGroup: 1000
      seccompProfile:
        type: RuntimeDefault
      capabilities:
        drop: ["ALL"]
        # add only if truly required:
        # add: ["NET_BIND_SERVICE"]
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
```

### Remediation
1. Add the full `securityContext` block above to every container
2. Label the namespace with `pod-security.kubernetes.io/enforce: restricted`
3. Deploy Kyverno/OPA policy to block non-compliant pods at admission
4. Rebuild images that require root — most frameworks support non-root (e.g., Node.js `USER node`, Python non-root, Go distroless)

---

## FM-2: Resource Starvation

### Description
Pods without resource requests/limits causing unpredictable scheduling, CPU throttling, OOMKilled evictions, and noisy-neighbor problems.

### Severity: HIGH

### Symptoms
- Pods stuck in `CrashLoopBackOff` with reason `OOMKilled`
- `kubectl top pods` shows CPU throttling (high throttle %)
- Nodes showing memory pressure
- QoS class is `BestEffort`

### Detection

```bash
# Find pods without resource limits
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[] | (.resources.limits // {}) == {}) | .metadata.name'

# Find pods without resource requests
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[] | (.resources.requests // {}) == {}) | .metadata.name'

# Check QoS class
kubectl get pods -A -o json | \
  jq '.items[] | {name: .metadata.name, qos: .status.qosClass}'

# Monitor OOM events
kubectl get events -A --field-selector reason=OOMKilling

# Check actual vs requested
kubectl top pods -A
```

### Prevention — Guaranteed QoS for Critical Workloads

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "2Gi"
  limits:
    cpu: "500m"     # Equal to request = Guaranteed QoS
    memory: "2Gi"
```

### Namespace-Level LimitRange

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
```

### Remediation
1. Add `resources.requests` and `resources.limits` to every container
2. Use Guaranteed QoS (requests == limits) for databases and critical services
3. Deploy `LimitRange` to enforce defaults per namespace
4. Use VPA in recommendation mode to profile and right-size
5. Set HPA with CPU/memory targets for scaling before starvation

---

## FM-3: Network Exposure

### Description
Missing NetworkPolicies, services exposed as LoadBalancer/NodePort unnecessarily, no TLS termination, flat network allowing unrestricted pod-to-pod communication.

### Severity: HIGH

### Symptoms
- `kubectl get netpol -A` returns few or no policies
- LoadBalancer services without TLS
- Any pod can reach any other pod in the cluster
- Egress to the internet unrestricted

### Detection

```bash
# Check NetworkPolicy coverage
kubectl get netpol -A

# Find exposed services
kubectl get svc -A | grep LoadBalancer

# Find services without TLS annotation
kubectl get ingress -A -o json | \
  jq '.items[] | select(.spec.tls == null) | .metadata.name'

# Test pod-to-pod reachability
kubectl run tmp --rm -it --image=nicolaka/netshoot -- /bin/bash
# curl http://<any-service>.<any-namespace>:<port>
```

### Prevention — Defense in Depth

**Layer 1: Default deny in every namespace**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

**Layer 2: Explicit allow-lists**
```yaml
# Only the ingress controller can talk to my app
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - port: 8080
```

**Layer 3: Service mesh mTLS (Istio/Linkerd)**
```yaml
# Istio PeerAuthentication — require mTLS mesh-wide
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

### Remediation
1. Apply default-deny NetworkPolicy to every namespace
2. Create explicit allowlist policies for required communication paths
3. Replace LoadBalancer services with Ingress + cert-manager for TLS
4. Deploy service mesh for mTLS between services
5. Restrict egress to known external endpoints only

---

## FM-4: Privilege Sprawl

### Description
Overly broad RBAC permissions: `cluster-admin` bindings, wildcard resources/verbs, service accounts with unrestricted access, default service account used instead of dedicated SAs.

### Severity: CRITICAL

### Symptoms
- Multiple `cluster-admin` ClusterRoleBindings
- Roles with `resources: ["*"]` and `verbs: ["*"]`
- Pods using `default` service account
- Service accounts with secrets access

### Detection

```bash
# Find all cluster-admin bindings
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name=="cluster-admin") | {name: .metadata.name, subjects: .subjects}'

# Find roles with wildcard permissions
kubectl get roles,clusterroles -A -o json | \
  jq '.items[] | select(.rules[]?.resources[]? == "*" and .rules[]?.verbs[]? == "*") | {kind: .kind, name: .metadata.name, namespace: .metadata.namespace}'

# Find pods using default service account
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.serviceAccountName == "default" or .spec.serviceAccountName == null) | {name: .metadata.name, namespace: .metadata.namespace}'

# Check what a service account can actually do
kubectl auth can-i --list --as=system:serviceaccount:production:myapp-sa -n production
```

### Prevention — Least-Privilege Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-operator
  namespace: production
rules:
# ONLY the resources and verbs needed
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "update", "patch"]  # No create, no delete
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
# Explicit NO access to: secrets, configmaps (unless needed), delete

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-operator-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: cicd-sa
  namespace: production
roleRef:
  kind: Role
  name: app-operator
  apiGroup: rbac.authorization.k8s.io
```

### Remediation
1. Audit all ClusterRoleBindings — remove or downscope `cluster-admin`
2. Replace wildcard `resources:["*"]` with explicit resource lists
3. Create dedicated ServiceAccounts per workload, never use `default`
4. Set `automountServiceAccountToken: false` on ServiceAccounts by default
5. Use `kubectl auth can-i` to verify effective permissions

---

## FM-5: Fragile Rollouts

### Description
Deployments without health probes, PodDisruptionBudgets, or proper update strategies. Single-replica deployments with RollingUpdate causing downtime during upgrades. No revision history for rollback.

### Severity: MEDIUM

### Symptoms
- Pods restarting without traffic being drained
- Downtime during deployments
- Pods evicted during node maintenance with no PDB
- `kubectl rollout undo` fails due to insufficient revision history

### Detection

```bash
# Find deployments without health probes
kubectl get deployment -A -o json | \
  jq '.items[] | select(.spec.template.spec.containers[] | (has("livenessProbe") | not) or (has("readinessProbe") | not)) | .metadata.name'

# Find single-replica deployments
kubectl get deployment -A -o json | \
  jq '.items[] | select(.spec.replicas == 1) | {name: .metadata.name, namespace: .metadata.namespace}'

# Find deployments without PDB
kubectl get pdb -A  # Check which deployments have no corresponding PDB
```

### Prevention — Production-Grade Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  revisionHistoryLimit: 10
  minReadySeconds: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0   # Zero-downtime: never go below desired replicas
  selector:
    matchLabels:
      app: myapp
  template:
    spec:
      containers:
      - name: app
        # Readiness: is the pod ready to serve traffic?
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 3
        # Liveness: should the pod be restarted?
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        # Startup: give slow-starting apps time
        startupProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 0
          periodSeconds: 5
          failureThreshold: 30  # 150s startup window

---
# Always pair with a PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 1   # At least 1 pod must always be available
  # OR maxUnavailable: 1 — at most 1 pod can be unavailable
  selector:
    matchLabels:
      app: myapp
```

### Remediation
1. Add `readinessProbe` AND `livenessProbe` to every container
2. Set `replicas >= 2` with `maxUnavailable: 0` for zero-downtime
3. Create a PodDisruptionBudget for every Deployment
4. Set `revisionHistoryLimit: 10` for safe rollbacks
5. Add `minReadySeconds` to prevent traffic hitting unready pods

---

## FM-6: API Drift

### Description
Using deprecated or removed API versions. `extensions/v1beta1` and `apps/v1beta2` removed in 1.16+, `policy/v1beta1` PodDisruptionBudget deprecated in 1.21. Manifests that fail on newer cluster versions.

### Severity: MEDIUM

### Symptoms
- `error: unable to recognize "manifest.yaml": no matches for kind "Deployment" in version "extensions/v1beta1"`
- Warnings during `kubectl apply` about deprecated APIs
- Manifests working on old cluster but failing on new cluster

### Detection

```bash
# Check current API versions
kubectl api-resources

# Check for deprecated APIs in manifests
grep -r "extensions/v1beta1" ./deploy/
grep -r "apps/v1beta" ./deploy/
grep -r "policy/v1beta1" ./deploy/
grep -r "autoscaling/v2beta" ./deploy/
grep -r "networking.k8s.io/v1beta1" ./deploy/

# Use kubectl to check if a manifest can be applied
kubectl apply --dry-run=server -f manifest.yaml

# Use pluto to detect deprecated APIs
pluto detect-files -d ./deploy/
```

### API Version Mapping

| Resource | Deprecated | Current | Removed |
|----------|-----------|---------|---------|
| Deployment | `extensions/v1beta1`, `apps/v1beta1/2` | `apps/v1` | `extensions/v1beta1` in 1.16 |
| PodDisruptionBudget | `policy/v1beta1` | `policy/v1` | `policy/v1beta1` in 1.25 |
| Ingress | `extensions/v1beta1`, `networking.k8s.io/v1beta1` | `networking.k8s.io/v1` | `extensions/v1beta1` in 1.22 |
| CronJob | `batch/v1beta1` | `batch/v1` | `batch/v1beta1` in 1.25 |
| HPA | `autoscaling/v2beta1/2` | `autoscaling/v2` | `autoscaling/v2beta2` in 1.26 |
| PodSecurityPolicy | `policy/v1beta1` | REMOVED | Removed in 1.25 (use PSS) |

### Remediation
1. Always use `apps/v1` for Deployments, StatefulSets, DaemonSets
2. Always use `policy/v1` for PodDisruptionBudgets
3. Always use `networking.k8s.io/v1` for Ingresses and NetworkPolicies
4. Always use `autoscaling/v2` for HPAs
5. Run `kubectl apply --dry-run=server` before applying to production
6. Use `pluto` in CI/CD to catch deprecated APIs early

---

## FM-7: GitOps Divergence

### Description
Manual `kubectl apply` or `helm install` bypasses the GitOps pipeline, causing cluster state to diverge from the Git source of truth. Unrecorded emergency changes accumulate as technical debt.

### Severity: HIGH

### Symptoms
- `flux get kustomizations -A` shows `Ready=False` or drift
- `argocd app diff <app>` shows differences
- Cluster state doesn't match repository state
- "Emergency fixes" applied directly to cluster, never committed back

### Detection

```bash
# Flux: detect drift
flux get kustomizations -A --status-selector ready=false
flux reconcile source git flux-system  # force reconciliation

# ArgoCD: detect drift
argocd app list
argocd app diff myapp
argocd app sync myapp --dry-run  # preview what would change

# General: compare live vs committed
kubectl get deployment myapp -n production -o yaml > live.yaml
git show HEAD:overlays/production/deployment.yaml > committed.yaml
diff live.yaml committed.yaml
```

### Prevention — GitOps by Default

```yaml
# Flux: auto-reconciliation with drift detection
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  prune: true        # Remove resources not in Git
  force: false       # Don't force-replace on conflict
  sourceRef:
    kind: GitRepository
    name: myapp
  path: ./overlays/production
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production

---
# ArgoCD: automated sync with self-heal
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  syncPolicy:
    automated:
      prune: true     # Remove resources not in Git
      selfHeal: true  # Auto-correct manual changes
    syncOptions:
      - CreateNamespace=true
```

### Remediation
1. Commit all manual changes back to Git immediately
2. Configure Flux/ArgoCD with `selfHeal: true` and `prune: true`
3. Implement RBAC that prevents direct `kubectl apply` for most users
4. Set up alerts for drift detection (Flux notification controller, ArgoCD notifications)
5. Use `kubectl` as read-only for all non-emergency operations

---

## FM-8: Multi-Cloud Skew

### Description
Cloud-provider-specific configurations (annotations, ingress classes, storage classes, IAM) hardcoded for one provider, causing failures when deploying to different environments or during cloud migrations.

### Severity: MEDIUM

### Symptoms
- EKS-specific ALB annotations applied to GKE cluster → ingress non-functional
- AKS workload identity labels on EKS → IAM not working
- GCP-specific storage classes on AKS → PVC stuck in Pending
- OpenShift SCC violations on standard K8s → pods fail admission

### Detection

```bash
# Check for provider-specific annotations
grep -r "eks.amazonaws.com" ./deploy/
grep -r "iam.gke.io" ./deploy/
grep -r "azure.workload.identity" ./deploy/
grep -r "openshift.io" ./deploy/

# Verify storage classes exist
kubectl get storageclass

# Verify ingress classes exist
kubectl get ingressclass
```

### Prevention — Cloud-Agnostic Abstractions

```yaml
# Use Helm values for provider-specific configs
# values.yaml
cloudProvider: aws  # aws | gcp | azure | openshift

# templates/_helpers.tpl
{{- define "app.ingressAnnotations" -}}
{{- if eq .Values.cloudProvider "aws" }}
alb.ingress.kubernetes.io/scheme: internet-facing
{{- else if eq .Values.cloudProvider "gcp" }}
kubernetes.io/ingress.class: gce
networking.gke.io/managed-certificates: {{ .Release.Name }}-cert
{{- else if eq .Values.cloudProvider "azure" }}
kubernetes.io/ingress.class: azure/application-gateway
{{- else }}
kubernetes.io/ingress.class: nginx
{{- end }}
{{- end }}
```

### Provider-Specific Patterns Table

| Feature | EKS | GKE | AKS | OpenShift |
|---------|-----|-----|-----|-----------|
| **Ingress** | AWS LB Controller (`alb`) | GCE Ingress (`gce`) | AGIC (`azure/application-gateway`) | Router (`route.openshift.io`) |
| **IAM** | IRSA (`eks.amazonaws.com/role-arn`) | Workload Identity (`iam.gke.io/gcp-service-account`) | Workload ID (`azure.workload.identity/use`) | OAuth + SCC |
| **Storage** | EBS CSI (`gp3`) | PD CSI (`pd-ssd`) | Azure Disk CSI (`managed-csi`) | ODF / any CSI |
| **Registry** | ECR | Artifact Registry | ACR | Quay / any |
| **Spot** | `eks.amazonaws.com/capacityType: SPOT` | `cloud.google.com/gke-spot: "true"` | `kubernetes.azure.com/scalesetpriority: spot` | N/A |
| **Certificates** | cert-manager (standard) | ManagedCertificate CRD + cert-manager | cert-manager (standard) | cert-manager (standard) |

### Remediation
1. Externalize provider-specific config into Helm values or Kustomize overlays
2. Use `overlays/eks/`, `overlays/gke/`, `overlays/aks/` directory structure in GitOps
3. Never hardcode `LoadBalancer` service type without Ingress abstraction
4. Use CSI drivers and `StorageClass` names that exist across providers
5. Test manifests against each target platform in CI

---

## Failure Mode Severity Matrix

| Mode | Severity | Exploitability | Impact | Detection Difficulty |
|------|----------|---------------|--------|---------------------|
| FM-1: Insecure Workloads | CRITICAL | Low | Critical | Easy |
| FM-2: Resource Starvation | HIGH | N/A | High | Easy |
| FM-3: Network Exposure | HIGH | Medium | High | Medium |
| FM-4: Privilege Sprawl | CRITICAL | Low | Critical | Medium |
| FM-5: Fragile Rollouts | MEDIUM | N/A | Medium | Easy |
| FM-6: API Drift | MEDIUM | N/A | Low | Easy |
| FM-7: GitOps Divergence | HIGH | Medium | High | Hard |
| FM-8: Multi-Cloud Skew | MEDIUM | N/A | Medium | Medium |

---

## Quick Reference: Prevention Checklist

```
[ ] FM-1: securityContext on every container, runAsNonRoot: true, drop ALL caps
[ ] FM-2: resources.requests AND .limits set, Guaranteed QoS for critical workloads
[ ] FM-3: default-deny NetworkPolicy in every namespace, explicit allowlists
[ ] FM-4: least-privilege RBAC, dedicated ServiceAccounts, no cluster-admin
[ ] FM-5: readinessProbe + livenessProbe, PDB, replicas >= 2, revisionHistoryLimit >= 10
[ ] FM-6: apps/v1, networking.k8s.io/v1, policy/v1 — no deprecated APIs
[ ] FM-7: all changes through GitOps, self-heal enabled, drift alerts configured
[ ] FM-8: cloud-agnostic base + provider-specific overlays, no hardcoded annotations
```
