# Kubernetes Security Hardening Reference

Comprehensive security reference for the kubernetes-operations skill. Covers Pod Security Standards, RBAC patterns, NetworkPolicies, secret management, and the OWASP Kubernetes Top 10.

---

## 1. Pod Security Standards (PSS)

Kubernetes 1.25+ replaced PodSecurityPolicy with built-in Pod Security Standards, enforced via namespace labels.

### Policy Levels

| Level | Description | Key Constraints |
|-------|-------------|-----------------|
| **Privileged** | Unrestricted | No restrictions — use only for system workloads (kube-system) |
| **Baseline** | Minimal hardening | Prevents known privilege escalations, hostPath of special dirs |
| **Restricted** | Full hardening | All baseline + non-root, seccomp, capabilities dropped, no privilege escalation |

### Restricted Profile — Full Specification

The **restricted** profile is the recommended default for all application namespaces:

```yaml
spec:
  containers:
  - name: app
    securityContext:
      # Must be set
      runAsNonRoot: true               # Cannot run as UID 0
      runAsUser: 1000                  # Specific non-zero UID
      seccompProfile:
        type: RuntimeDefault           # Kernel attack surface reduction
      capabilities:
        drop: ["ALL"]                  # No Linux capabilities
      allowPrivilegeEscalation: false  # No setuid binaries, no child privilege gain

      # Recommended but not required by restricted
      readOnlyRootFilesystem: true     # Immutable container filesystem
      runAsGroup: 1000
      fsGroup: 1000
```

### Namespace Enforcement

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Enforce at admission
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest

    # Audit violations without blocking
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest

    # Warn on violation
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

### Per-Namespace Exemptions

Use `pod-security.kubernetes.io/exempt: "true"` sparingly and only for system namespaces:
- `kube-system`
- `cert-manager`
- `istio-system`
- `flux-system`

---

## 2. RBAC Patterns

### Principle of Least Privilege

Grant only the verbs, resources, and namespaces a workload needs. Never grant cluster-wide access to application workloads.

### Role vs ClusterRole

| Scope | Use Case |
|-------|----------|
| **Role** (namespaced) | Application deployer, log reader, config updater |
| **ClusterRole** (cluster-wide) | Node reader, PV provisioner, ingress controller |

### Application Deployer Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-deployer
  namespace: app-production
rules:
# Deploy and manage application workloads
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
# Read and restart pods
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
# Manage services and configs
- apiGroups: [""]
  resources: ["services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
# No delete — prevents accidental destruction
# No secrets access — use External Secrets Operator
# No cluster-wide resources
```

### Service Account Token Restrictions

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: app-production
automountServiceAccountToken: false  # Explicit opt-in per pod

---
# Pod spec
spec:
  serviceAccountName: app-sa
  automountServiceAccountToken: true  # Only this pod mounts the token
```

### Token Audience Binding

```yaml
# For cloud IAM integration, project token to specific audience
spec:
  serviceAccountName: app-sa
  containers:
  - name: app
    volumeMounts:
    - name: sa-token
      mountPath: /var/run/secrets/tokens
      readOnly: true
  volumes:
  - name: sa-token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          audience: "sts.amazonaws.com"  # EKS IRSA
          expirationSeconds: 3600
```

### RBAC Audit Query

```bash
# Find all cluster-admin bindings
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name=="cluster-admin") | {name: .metadata.name, subjects: .subjects}'

# Check what a service account can do
kubectl auth can-i --list \
  --as=system:serviceaccount:production:app-sa \
  -n production

# Find overly broad roles
kubectl get roles,clusterroles -A -o json | \
  jq '.items[] | select(.rules[]?.resources[]? == "*" and .rules[]?.verbs[]? == "*") | .metadata.name'
```

---

## 3. NetworkPolicy Templates

### Default Deny All

Every namespace SHOULD start with:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}          # All pods in namespace
  policyTypes:
  - Ingress
  - Egress
```

### Allow DNS Egress

Required for pod functionality — allow CoreDNS:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

### Allow Ingress from Ingress Controller

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
```

### Allow Egress to Specific Database

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-to-database
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Allow Egress to External APIs (by IP/CIDR)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/8       # Internal VPC
        except:
        - 10.0.0.0/16          # Except management subnet
    ports:
    - protocol: TCP
      port: 443
```

### NetworkPolicy Testing

```bash
# List all NetworkPolicies in namespace
kubectl get netpol -n production

# Test connectivity from a debug pod
kubectl run tmp --rm -it --image=nicolaka/netshoot -n production -- /bin/bash
# Inside: curl -v http://myapp:8080/healthz
# Inside: nc -zv postgres 5432
```

---

## 4. Secret Management

### Kubernetes Native Secrets

**Minimum:** Enable etcd encryption at rest.

```yaml
# etcd encryption configuration (set at cluster bootstrap)
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-32-byte-key>
    - identity: {}  # fallback for reading unencrypted secrets
```

### External Secrets Operator (Recommended)

**Use case:** Cloud-native, existing secrets manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).

```yaml
# ClusterSecretStore — available to all namespaces
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secretsmanager
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-west-1
      auth:
        jwt:
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets

---
# ExternalSecret — maps cloud secrets to K8s Secret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  target:
    name: myapp-secrets
    creationPolicy: Owner
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: /prod/myapp/DATABASE_URL
  - secretKey: API_KEY
    remoteRef:
      key: /prod/myapp/API_KEY
```

### Sealed Secrets (GitOps-Friendly)

**Use case:** GitOps, no external dependency, secrets committed to Git.

```bash
# Install controller
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

# Encrypt a secret
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=s3cret \
  --dry-run=client -o yaml | \
  kubeseal --controller-namespace kube-system --format yaml > sealed-db-creds.yaml

# The sealed secret is safe to commit to Git
# Only the controller in the target cluster can decrypt it
```

### HashiCorp Vault

**Use case:** Dynamic secrets, PKI, multi-cluster, audit trail.

```yaml
# Vault CSI Provider — mounts secrets as volumes
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-db-creds
spec:
  provider: vault
  parameters:
    vaultAddress: "https://vault.internal:8200"
    roleName: "myapp"
    objects: |
      - objectName: "db-creds"
        secretPath: "database/creds/myapp"
        secretKey: "username"
      - objectName: "db-creds"
        secretPath: "database/creds/myapp"
        secretKey: "password"
```

### Decision Matrix

| Requirement | Solution | Complexity |
|-------------|----------|------------|
| Cloud-native, existing secrets manager | External Secrets Operator | Low |
| GitOps, secrets in Git | Sealed Secrets | Low |
| Dynamic secrets, PKI | Vault | High |
| Simple, single cluster | K8s Secrets + etcd encryption | Low |
| Audit trail, compliance | Vault | High |

---

## 5. OWASP Kubernetes Top 10 — Full Summary

### K01 — Insecure Workload Configurations
- **Risk:** Privileged containers, root users, hostPath mounts, no securityContext
- **Mitigation:** PSS restricted, `securityContext` on every container, admission webhooks (OPA/Kyverno)
- **FM Alignment:** FM-1

### K02 — Supply Chain Vulnerabilities
- **Risk:** Vulnerable base images, unverified third-party charts, poisoned dependencies
- **Mitigation:** Image scanning (Trivy, Grype, Snyk), image signing (cosign/sigstore), private registry
- **Command:** `trivy image myapp:latest`

### K03 — Overly Permissive RBAC
- **Risk:** `cluster-admin` bindings, wildcard verbs/resources, default service account used
- **Mitigation:** Least-privilege Roles, per-namespace ServiceAccounts, no automount by default
- **FM Alignment:** FM-4

### K04 — Lack of Centralized Policy Enforcement
- **Risk:** Inconsistent security across namespaces, manual enforcement gaps
- **Mitigation:** OPA/Gatekeeper, Kyverno, PSS namespace labels
- **Example Kyverno policy:**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-non-root
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Running as root is not allowed"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
```

### K05 — Inadequate Logging & Monitoring
- **Risk:** No audit logs, missing workload metrics, blind to intrusions
- **Mitigation:** Kubernetes audit logging, Prometheus metrics, structured logging (JSON), OpenTelemetry
- **FM Alignment:** §Observability in SKILL.md

### K06 — Broken Authentication Mechanisms
- **Risk:** Overly permissive service account tokens, static credentials, no token expiry
- **Mitigation:** Bound service account tokens, token audience restriction, OIDC for user auth

### K07 — Missing Network Segmentation
- **Risk:** Flat network, pod-to-pod communication unrestricted, no egress controls
- **Mitigation:** Deny-all NetworkPolicy, explicit allowlists, service mesh mTLS (Istio/Linkerd)
- **FM Alignment:** FM-3

### K08 — Secrets Management Failures
- **Risk:** Secrets in plaintext in ConfigMaps, committed to Git, no rotation
- **Mitigation:** External Secrets Operator, Sealed Secrets, Vault, etcd encryption at rest
- **FM Alignment:** §Secret Management

### K09 — Misconfigured Cluster Components
- **Risk:** API server exposed, kubelet anonymous auth, etcd unauthenticated
- **Mitigation:** CIS benchmarks audit, kube-bench scanning, managed K8s where possible
- **Command:** `kube-bench run --targets master,node`

### K10 — Outdated & Vulnerable Kubernetes Components
- **Risk:** Unpatched CVEs, end-of-life K8s versions, deprecated APIs
- **Mitigation:** Regular upgrades, managed K8s auto-upgrades, API deprecation checks
- **FM Alignment:** FM-6

---

## 6. NSA/CISA Kubernetes Hardening Checklist

- [ ] Scan container images for vulnerabilities (Trivy/Grype)
- [ ] Run containers as non-root (`runAsNonRoot: true`)
- [ ] Use immutable container filesystems (`readOnlyRootFilesystem: true`)
- [ ] Drop all Linux capabilities, add only required ones
- [ ] Enable seccomp (`RuntimeDefault`) and AppArmor/SELinux
- [ ] Use NetworkPolicies to segment pod traffic
- [ ] Encrypt secrets at rest in etcd
- [ ] Enable Kubernetes audit logging
- [ ] Use service mesh for mTLS between services
- [ ] Regularly update cluster components and node OS
- [ ] Use separate service accounts per workload
- [ ] Restrict cloud metadata access (`metadata.google.internal`, `169.254.169.254`)

---

## 7. CIS Kubernetes Benchmark — Key Controls

| # | Control | Severity | Implementation |
|---|---------|----------|----------------|
| 1.1.1 | API server — anonymous auth disabled | CRITICAL | `--anonymous-auth=false` |
| 1.2.1 | API server — AlwaysPullImages admission plugin | MEDIUM | `--enable-admission-plugins=...,AlwaysPullImages` |
| 1.2.19 | API server — audit log max age ≥30 days | MEDIUM | `--audit-log-maxage=30` |
| 4.1.1 | Kubelet — anonymous auth disabled | CRITICAL | `--anonymous-auth=false` |
| 4.2.6 | Kubelet — protect kernel defaults | MEDIUM | `--protect-kernel-defaults=true` |
| 5.1.5 | RBAC — minimize cluster-admin bindings | HIGH | `kubectl get clusterrolebindings -o json \| jq ...` |
| 5.2.1 | PSS — restricted enforcement | HIGH | Namespace labels as above |
| 5.3.2 | NetworkPolicies — default deny per namespace | MEDIUM | `kubectl get netpol -A` |
| 5.4.1 | Secrets — prefer external provider | MEDIUM | ESO / Sealed Secrets / Vault |

---

## References

- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/)
- [NSA/CISA Kubernetes Hardening Guidance](https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [External Secrets Operator](https://external-secrets.io/)
- [Kyverno Policies](https://kyverno.io/policies/)
