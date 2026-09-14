# Gate 5: Infra Hardening — CI/CD, Containers, and IaC

## Overview

This gate catches the systematic ways LLMs produce insecure infrastructure config. Where other gates stop (clean-code-pro excludes CI/tooling config, security reviews application code), agents write workflow YAML, Dockerfiles, and Terraform constantly — and the training data for these is dominated by tutorial-grade examples whose defaults are permissive on purpose (root containers, `write-all` tokens, `0.0.0.0/0` ingress, mutable `latest` tags). A single finding here — a poisoned pipeline, an exfiltrated `GITHUB_TOKEN` — compromises every artifact the pipeline ships.

## The 18 Imperatives

### CI/CD Workflows
1. **Untrusted context never reaches a shell inline.** Attacker-controlled workflow context — issue titles, PR titles/bodies, branch names — must not appear inside `run:` via `${{ }}` interpolation. Pass through an env var and quote it. (CICD-SEC-4)
2. **`pull_request_target` never executes fork code with secrets.** These triggers run with secret access; checking out and running the PR's head code under them hands secrets to any forker. Use `pull_request` or split privileged steps into a separate workflow. (CICD-SEC-4)
3. **Token permissions are minimal and explicit.** Every workflow declares `permissions:` with only what it needs — start from `contents: read`. Never `write-all`. (CICD-SEC-2)
4. **Third-party actions are pinned to a full commit SHA.** A moving tag (`@v4`, `@main`) is a supply-chain handle anyone who compromises the action repo can yank. Pin SHA, comment version. (CICD-SEC-3)
5. **Secrets stay out of logs, artifacts, and forks.** No `echo` of secrets, no secrets in artifact uploads or build args, no secrets available to fork-triggerable workflows. Prefer OIDC federation over long-lived keys. (CICD-SEC-6)
6. **Artifacts, caches, and outputs from untrusted runs are untrusted input.** A `workflow_run` that downloads an artifact from fork code and executes it re-opens imperative 2. Validate provenance. (CICD-SEC-9)
7. **Self-hosted runners never serve public-repo or fork workloads** without isolation — a fork PR on a self-hosted runner is remote code execution on your infrastructure. (CICD-SEC-5)

### Containers
8. **Containers run as non-root.** A `USER` directive with a non-zero UID in every final image. No `privileged: true`, no docker-socket mount, no `--cap-add` beyond need. (CIS Docker Benchmark)
9. **No secrets in images — ever.** Not in `ENV`, not in `ARG`, not in a `COPY`'d file deleted "later" — every layer is preserved. Use BuildKit secret mounts or runtime injection. (CWE-798 applied to layers)
10. **Base images are pinned and minimal.** Digest-pinned (`@sha256:...`) or exact-version base; never bare `latest`. Multi-stage builds keep compilers and source out of the runtime image. (CICD-SEC-3)
11. **Nothing is piped from the network into a shell during build.** `curl | sh` in a Dockerfile is third-party code execution baked into every build. Download, verify checksum, then run.

### IaC and Cloud
12. **No wildcard IAM.** `Action: "*"`, `Resource: "*"`, or both is a finding. Grant specific actions on specific resources. (CIS; least privilege)
13. **No open ingress to admin or data ports.** `0.0.0.0/0` (or `::/0`) to SSH/RDP/databases/k8s API is exposed-to-the-internet. Allow-list sources or use a bastion/VPN.
14. **Storage and state are private and encrypted.** Buckets block public access unless serving a public website. Terraform state lives in an encrypted, access-controlled backend; never committed.
15. **Modules and providers are pinned and verified.** Version-pinned module sources from verified namespaces. Kubernetes workloads declare `securityContext` (`runAsNonRoot`, no privilege escalation) and resource limits.

### AI-Specific Infra Guardrails
16. **Never weaken the pipeline to make it green.** No `continue-on-error: true` on a failing security step, no `|| true`, no deleting the scan job, no `--no-verify`. (The infra twin of security imperative 26)
17. **Demo config is not production config.** The model emits the tutorial default — root user, `write-all`, open ingress, `latest`. Re-derive each privilege from actual workload need.
18. **Verify every action, image, and module name against its registry** before use — existence, publisher, popularity. The package-hallucination mechanism applies identically to Actions marketplace, Docker Hub, and module registries.

## Self-Check (Gate 5)
1. Walk imperatives 1–18 against your diff. Fix or flag every violation.
2. Any `${{ }}` of attacker-controlled context inside `run:`? Any `pull_request_target` that touches fork code?
3. Does every workflow declare minimal `permissions:`? Is every third-party action SHA-pinned?
4. Any secret in a layer, build arg, env literal, or log path? Any `curl | sh` in a build?
5. Final image non-root and minimal? Base image pinned?
6. Any wildcard IAM, `0.0.0.0/0` to an admin port, public bucket, or committed state file?
7. Did you loosen any permission, disable any check, or add `continue-on-error` to make something pass? If yes, revert and solve properly.
