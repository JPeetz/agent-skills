---
name: supply-chain-security-scanner
description: >
  AI-powered software supply chain security auditing skill for agentic platforms. Performs
  comprehensive dependency vulnerability scanning across npm, PyPI, Maven, Go modules, Cargo,
  and container images. Generates SBOMs (Software Bill of Materials) in SPDX and CycloneDX
  formats using Syft and Grype. Validates license compliance against organizational policies
  and detects copyleft risks. Verifies cryptographic provenance and SLSA framework attestations
  using cosign and slsa-verifier. Executes a structured audit methodology—Scan → Analyze →
  Report → Remediate—producing machine-readable vulnerability reports with CVSS scores,
  exploitability assessments, and actionable fix recommendations aligned with OWASP Agentic
  Skills Top 10 guidance. Integrates with ecosystem vulnerability databases including NVD
  (National Vulnerability Database), GitHub Advisory Database (GHSA), and Open Source
  Vulnerabilities (OSV). Covers software composition analysis (SCA) workflows, dependency
  confusion detection, typosquatting checks, and end-to-end software supply chain integrity
  verification. Designed for CI/CD pipeline integration, pre-commit hooks, and ad-hoc
  security audits. Suitable for DevSecOps teams, open-source maintainers, and enterprise
  compliance programs adopting SLSA Level 1–3 supply chain security requirements. Works
  with existing toolchains: npm audit, pip-audit, OWASP Dependency-Check, Syft, Grype,
  cosign, slsa-verifier, and trivy. All findings include remediation paths and SBOM
  lifecycle management guidance.
version: 1.0.0
author: Skill Foundry
platforms:
  - linux
  - macos
  - ci
tags:
  - supply-chain-security
  - sbom
  - dependency-scanning
  - vulnerability-audit
  - license-compliance
  - provenance-verification
  - software-composition-analysis
  - owasp
  - slsa
  - devsecops
  - sca
  - cve
  - cyclonedx
  - spdx
  - npm-audit
  - pip-audit
  - syft
  - grype
  - cosign
  - supply-chain
  - security-scanner
  - agent-skill
---

# Supply Chain Security Scanner

AI-powered software supply chain security auditing for agentic platforms. Covers dependency
vulnerability scanning, SBOM generation, license compliance, and provenance verification
across npm, PyPI, Maven, Go modules, Cargo, and container images.

## Table of Contents

1. [Activation Triggers](#activation-triggers)
2. [Prerequisites](#prerequisites)
3. [Audit Methodology](#audit-methodology)
4. [Workflow: Step-by-Step](#workflow-step-by-step)
5. [Tool Coverage](#tool-coverage)
6. [SBOM Generation & Management](#sbom-generation--management)
7. [Provenance Verification](#provenance-verification)
8. [License Compliance](#license-compliance)
9. [Remediation & Reporting](#remediation--reporting)
10. [Quick Reference](#quick-reference)
11. [Common Pitfalls & Anti-Patterns](#common-pitfalls--anti-patterns)
12. [CI/CD Integration Patterns](#cicd-integration-patterns)
13. [Ecosystem Vulnerability Databases](#ecosystem-vulnerability-databases)
14. [OWASP Agentic Skills Top 10 Context](#owasp-agentic-skills-top-10-context)
15. [SEO Metadata](#seo-metadata)

---

## Activation Triggers

This skill activates when a user requests a supply chain security action.

### Primary Triggers (activate)

- "scan my project for vulnerable dependencies"
- "generate an SBOM for this repository"
- "check if our npm packages have known CVEs"
- "audit our software supply chain"
- "verify the provenance of this container image"
- "run a dependency vulnerability scan"
- "check license compliance of our dependencies"
- "generate a CycloneDX SBOM"
- "verify SLSA provenance for this build artifact"
- "scan this Docker image for vulnerabilities"
- "run software composition analysis on this codebase"
- "check for dependency confusion attacks"
- "audit pip packages for security issues"
- "generate SPDX bill of materials"

### Near-Miss Negatives (do NOT activate)

- "explain what SBOM means" — informational request, no action needed
- "how do I secure my npm packages?" — general security advice, not a scan
- "what is SLSA provenance?" — definition/education request, not verification

If a user asks an educational question, answer it directly without launching a scan.
If a user asks for general security advice, provide guidance without running tooling.

---

## Prerequisites

The following CLIs must be available. The scripts in `scripts/` perform capability
detection automatically and report which tools are missing before any scan runs.

| Tool | Purpose | Installation |
|------|---------|-------------|
| `syft` | SBOM generation (SPDX, CycloneDX) | `brew install syft` / `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \| sh -s -- -b /usr/local/bin` |
| `grype` | Vulnerability scanning against SBOM | `brew install grype` / `curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh \| sh -s -- -b /usr/local/bin` |
| `cosign` | Container image signing & verification | `brew install cosign` |
| `slsa-verifier` | SLSA provenance verification | `go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest` |
| `trivy` | Comprehensive scanner (images, fs, repos) | `brew install trivy` |
| `npm` | npm audit (bundled with Node.js) | `brew install node` |
| `pip-audit` | PyPI vulnerability audit | `pip install pip-audit` |
| `owasp-dependency-check` | OWASP Dependency-Check CLI | `brew install dependency-check` |
| `jq` | JSON report processing | `brew install jq` |
| `curl` | API calls to vulnerability databases | Pre-installed on macOS/Linux |

The skill checks for each tool at runtime. Missing tools are reported with
copy-paste installation commands. Scans proceed with available tools only.

---

## Audit Methodology

Every supply chain audit follows a four-phase methodology:

```
SCAN → ANALYZE → REPORT → REMEDIATE
```

### Phase 1: SCAN

**Goal:** Collect raw data from all available sources.

1. **Ecosystem detection** — Auto-detect project type(s) from lockfiles and build files:
   - `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` → npm/JavaScript
   - `requirements.txt`, `Pipfile.lock`, `pyproject.toml` → Python/PyPI
   - `pom.xml`, `build.gradle`, `build.gradle.kts` → Java/Maven/Gradle
   - `go.sum` → Go modules
   - `Cargo.lock` → Rust/Cargo
   - `Dockerfile`, `Containerfile` → Container images
   - `.csproj`, `packages.config` → .NET/NuGet

2. **Parallel scanning** — Run all applicable scanners concurrently:
   - `npm audit --json` for Node.js projects
   - `pip-audit --format=json` for Python projects
   - `owasp-dependency-check --format JSON` for JVM projects
   - `grype dir:. --output json` for general-purpose scanning
   - `trivy fs . --format json` for comprehensive filesystem scan
   - `trivy image <image>` for container images

3. **SBOM generation** — Produce an SBOM before scanning so results are anchored to
   a specific dependency graph snapshot. Default: CycloneDX JSON. Option: SPDX tag-value.

4. **Provenance check** — For container images and build artifacts with attached
   attestations, verify SLSA provenance and signature chains.

### Phase 2: ANALYZE

**Goal:** Correlate findings, de-duplicate, and prioritize.

1. **De-duplication** — Merge findings from multiple scanners by CVE ID. Keep the
   highest CVSS score and most detailed advisory for each unique vulnerability.

2. **CVSS triage** — Sort by severity:
   - **Critical** (CVSS 9.0–10.0): Immediate action required. Exploitable remotely.
   - **High** (CVSS 7.0–8.9): Patch within 48 hours.
   - **Medium** (CVSS 4.0–6.9): Schedule in next sprint.
   - **Low** (CVSS 0.1–3.9): Monitor; patch opportunistically.
   - **None** (CVSS 0.0): Informational only.

3. **Exploitability assessment** — Cross-reference with:
   - EPSS (Exploit Prediction Scoring System) scores > 0.1
   - KEV (Known Exploited Vulnerabilities) catalog membership
   - Public exploit availability (Exploit-DB, Metasploit)
   - Attack vector: Network (AV:N) vs Local (AV:L)
   - Attack complexity and privileges required

4. **License risk analysis** — Flag:
   - Copyleft licenses (GPL, AGPL, EUPL) in proprietary codebases
   - Unlicensed or unknown-license packages
   - License incompatibilities between direct dependencies

5. **Provenance findings** — Report:
   - Unsigned or unattested artifacts
   - SLSA level gaps (no provenance → SLSA 0, signed → SLSA 1+, attested → SLSA 2+)
   - Expired or untrusted signing keys

### Phase 3: REPORT

**Goal:** Output structured, actionable findings.

Output formats (select based on user request or default to Markdown + JSON):

| Format | Use Case |
|--------|----------|
| **Markdown table** | Human-readable summaries, PR comments |
| **JSON** | Machine consumption, CI/CD integration |
| **SARIF** | GitHub Code Scanning, IDE integration |
| **CSV** | Spreadsheet import for compliance tracking |
| **HTML** | Self-contained report for stakeholders |

Every finding includes:
- **CVE ID** — Canonical identifier
- **Package** — Name and affected version(s)
- **Severity** — CVSS score and vector string
- **Description** — Plain-language impact summary
- **Fix** — Minimum patched version or workaround
- **References** — Links to NVD, GHSA, and vendor advisories

### Phase 4: REMEDIATE

**Goal:** Provide actionable fix paths.

1. **Automatic fixes** (offer to run, never auto-apply):
   - `npm audit fix` — Auto-update compatible patches
   - `npm audit fix --force` — Breaking updates (warn user)
   - `pip install --upgrade <package>` — Pin to patched version
   - Maven `<dependency>` version bumps with `versions:use-latest-releases`

2. **Manual fixes** — For vulnerabilities with no direct patch:
   - Recommend alternative packages
   - Suggest vendor mitigations or configuration changes
   - Flag for architecture review if package is critical

3. **SBOM updates** — After remediation, regenerate SBOM to reflect the patched
   dependency graph. Recommend committing SBOM to repository at `sbom/` or `.sbom/`.

4. **Verification** — Re-scan to confirm fixes resolved vulnerabilities and no
   regressions were introduced.

---

## Workflow: Step-by-Step

### Standard Dependency Scan

```
1. cd <project-root>
2. Run: scripts/scan-dependencies.sh
   → Auto-detects ecosystem, runs appropriate scanners
   → Outputs: scan-report-<timestamp>.json, scan-report-<timestamp>.md
3. Review findings
4. Apply fixes per report recommendations
5. Re-run scan to verify
```

### SBOM Generation Workflow

```
1. cd <project-root>
2. Run: scripts/generate-sbom.sh --format cyclonedx
   → Generates: sbom-<project>-<version>-<timestamp>.cdx.json
3. Optionally sign: cosign sign-blob --key cosign.key sbom-*.cdx.json
4. Commit SBOM to repository
5. (Optional) Upload to dependency-track or OWASP Dependency-Track instance
```

### Provenance Verification Workflow

```
1. Identify the artifact (image digest, binary hash, or build ID)
2. Run: scripts/verify-provenance.sh --image <image>@<digest>
   OR:  scripts/verify-provenance.sh --artifact <path> --provenance <attestation-url>
3. Review SLSA level, builder identity, and source repository
4. Validate against expected values (builder, repo, branch, workflow)
5. Block deployment if verification fails
```

### CI/CD Integration

```yaml
# Example GitHub Actions snippet
- name: Supply Chain Scan
  run: |
    bash scripts/scan-dependencies.sh --ci
- name: Upload SBOM
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom-*.cdx.json
```

---

## Tool Coverage

### npm audit (Node.js / JavaScript)

```bash
# Standard audit
npm audit --json

# Fix compatible vulnerabilities
npm audit fix

# Fix all (including breaking changes — review first!)
npm audit fix --force

# Audit specific package
npm audit --json --package-lock-only
```

**Strengths:** Fast, built-in, understands npm dependency resolution quirks.
**Limitations:** Only covers the npm registry advisory database. Does not cover
transitive dependencies outside the lockfile. No license or provenance checking.

### pip-audit (Python / PyPI)

```bash
# Audit from requirements.txt
pip-audit --requirement requirements.txt --format json

# Audit from pyproject.toml
pip-audit --format json

# Audit ignoring specific CVEs (with documented reason)
pip-audit --ignore-vuln PYSEC-2023-123 --desc "False positive: internal-only service"

# Fix: pip-audit outputs fix versions; apply manually
pip install --upgrade <package>==<fixed-version>
```

**Strengths:** Uses the PyPI Advisory Database (via OSV). Fast, minimal dependencies.
**Limitations:** Python-only. Does not scan compiled extensions or vendored libraries.

### OWASP Dependency-Check (Java / JVM / Multi-language)

```bash
# Basic scan of current directory
dependency-check --project "MyProject" --scan . --format JSON --out ./reports/

# With NVD API key (required for production use; increases rate limits)
dependency-check --nvdApiKey $NVD_API_KEY --project "MyProject" --scan .

# HTML report for stakeholders
dependency-check --project "MyProject" --scan . --format HTML --out ./reports/
```

**Strengths:** Broad language support (Java, .NET, Ruby, Python, Node.js via OSS Index),
NVD integration, CPE matching. Mature and OWASP-backed.
**Limitations:** Slow on first run (downloads NVD data feed). Java-centric. Large memory
footprint (allocate `-Xmx4g` for large projects).

### Syft + Grype (SBOM-based Scanning)

**Syft** generates an SBOM. **Grype** scans the SBOM for vulnerabilities.
This separation is powerful: generate once, scan many times with updated vulnerability data.

```bash
# Generate CycloneDX SBOM
syft dir:. --output cyclonedx-json > sbom.cdx.json

# Generate SPDX SBOM
syft dir:. --output spdx-json > sbom.spdx.json

# Scan SBOM with Grype
grype sbom:sbom.cdx.json --output json > vulnerabilities.json

# Fail on critical/high (exit code 1)
grype sbom:sbom.cdx.json --fail-on high

# Only show fixable vulnerabilities
grype sbom:sbom.cdx.json --only-fixed
```

**Strengths:** Works across all ecosystems. SBOM is reusable across tools. Fast.
**Limitations:** Requires both syft and grype. SBOM must be regenerated when dependencies
change.

### Trivy (Comprehensive Scanner)

```bash
# Filesystem scan
trivy fs . --format json --output trivy-fs.json

# Container image scan
trivy image nginx:1.25 --format json --output trivy-image.json

# Repository scan (remote)
trivy repo https://github.com/owner/repo --format json

# Scan with SBOM output
trivy fs . --format cyclonedx --output sbom.cdx.json

# Filter by severity
trivy fs . --severity CRITICAL,HIGH
```

**Strengths:** Single binary, covers filesystem + images + repos + K8s, built-in SBOM
generation, fast, actively maintained by Aqua Security.
**Limitations:** Less granular license detection than dedicated tools. Some false positives
in go.sum scanning.

### cosign + slsa-verifier (Provenance)

```bash
# Verify container image signature
cosign verify --key cosign.pub <image>@sha256:<digest>

# Verify SLSA provenance attestation
slsa-verifier verify-image <image>@sha256:<digest> \
  --source-uri github.com/owner/repo \
  --source-branch main

# Verify artifact with provenance file
slsa-verifier verify-artifact <binary> \
  --provenance-path <attestation.intoto.jsonl> \
  --source-uri github.com/owner/repo
```

**Strengths:** Cryptographic proof of build integrity. SLSA framework compliance.
**Limitations:** Only works when build system produces attestations (GitHub Actions with
SLSA generator, Google Cloud Build, etc.). Most open-source projects lack attestations today.

---

## SBOM Generation & Management

### SBOM Formats

| Aspect | SPDX | CycloneDX |
|--------|------|-----------|
| **Originating body** | Linux Foundation | OWASP |
| **Primary use case** | License compliance | Security/vulnerability |
| **Mandatory fields** | 12 fields (SPDX 2.3) | 5 fields (CycloneDX 1.5) |
| **JSON schema** | Yes | Yes |
| **Tag-value format** | Yes (unique to SPDX) | No |
| **NTIA minimum elements** | ✅ | ✅ |
| **Vulnerability data** | Via external ref | Native VEX support |
| **Tool ecosystem** | FOSSology, ORT | Syft, Trivy, Grype, Dependency-Track |

**Recommendation:** Generate both. CycloneDX for security tooling (Grype, Dependency-Track);
SPDX for license compliance (FOSSology, ORT). Use Syft with `--output` to produce either format.

### NTIA Minimum Elements for SBOM

Per U.S. Executive Order 14028 and NTIA guidance, every SBOM must include:

1. **Supplier name** — Entity creating the component
2. **Component name** — Human-readable identifier
3. **Version** — Version string of the component
4. **Unique identifier** — PURL, CPE, or SWID tag
5. **Dependency relationships** — Which components depend on which
6. **Author** — SBOM creator
7. **Timestamp** — When SBOM was generated

### SBOM Lifecycle

```
Build → Generate SBOM → Sign → Attest → Store → Monitor → Update on change
```

- **Generate:** At every build, tag, or release
- **Sign:** `cosign sign-blob` or in-toto attestation
- **Store:** Commit to repo, upload to Dependency-Track, or push to OCI registry
- **Monitor:** Regularly re-scan stored SBOMs against updated vulnerability databases
- **Update:** Regenerate whenever `package.json`, `Cargo.lock`, or equivalent changes

---

## Provenance Verification

### SLSA Framework Levels

| Level | Name | Requirements |
|-------|------|-------------|
| **0** | None | No guarantees. Ad-hoc builds. |
| **1** | Build is scripted | Build process documented, build-as-code. |
| **2** | Build service + provenance | Hosted build platform (GitHub Actions, Cloud Build), signed provenance attestation. |
| **3** | Hardened build | Isolated, ephemeral, hermetic builds. Two-person review. Reproducible. |
| **4** | Maximum | All SLSA 3 + non-falsifiable provenance. Current state-of-the-art (rare). |

### What to Verify

1. **Builder identity** — Is the provenance from the expected CI system?
2. **Source repository** — Does the source URI match the expected repo?
3. **Build invocation** — Was the build triggered by the expected workflow/event?
4. **Material digests** — Do the source code digests in the attestation match?
5. **Signature validity** — Is the attestation signed by a trusted key?
6. **Key trust chain** — Does the signing key chain to a trusted root?

### Provenance Red Flags

- Missing attestation entirely (SLSA 0)
- Attestation from an unexpected builder
- Source URI mismatch (built from a fork or different repo)
- Expired or self-signed certificates
- Attestation predates or postdates the artifact
- Mismatched subject digest in attestation

---

## License Compliance

### License Categories

| Category | Licenses | Policy |
|----------|----------|--------|
| **Permissive** | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Unlicense | ✅ Safe for all use |
| **Weak copyleft** | MPL-2.0, LGPL-2.1, LGPL-3.0, EPL-2.0 | ⚠️ File-level reciprocity; usually acceptable |
| **Strong copyleft** | GPL-2.0, GPL-3.0, AGPL-3.0, EUPL-1.2 | 🔴 Viral; requires entire project to be open-sourced under same license |
| **Unknown** | No license detected | 🔴 Default copyright — all rights reserved; cannot legally use |
| **Non-standard** | WTFPL, Beerware, custom | ⚠️ Review manually with legal counsel |

### Detection Tools

- **Syft:** `syft dir:. --output json | jq '.artifacts[].licenses'`
- **Trivy:** License scanning built into `trivy fs`
- **FOSSology:** Full-featured OSS license compliance toolkit (for deep audits)
- **ORT (OSS Review Toolkit):** Automated compliance for large projects

### Policy Enforcement

Define a license policy file (e.g., `.license-policy.json`):

```json
{
  "allowed": ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"],
  "review_required": ["MPL-2.0", "LGPL-2.1", "LGPL-3.0"],
  "denied": ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "UNKNOWN"]
}
```

---

## Remediation & Reporting

### Report Template

Every scan produces a structured report. Example Markdown output:

```markdown
# Supply Chain Security Scan Report

**Project:** my-project
**Scan date:** 2026-06-09T02:07:00+01:00
**Scanners:** npm audit, grype, trivy
**SBOM:** sbom-my-project-2.1.0-20260609.cdx.json

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2     |
| High     | 5     |
| Medium   | 12    |
| Low      | 3     |

## Critical Findings

### CVE-2024-12345 — protobufjs 7.2.4

- **CVSS:** 9.8 (AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
- **EPSS:** 0.45 (45% probability of exploitation in next 30 days)
- **KEV:** ✅ Listed (CISA Known Exploited Vulnerability)
- **Description:** Remote code execution via malicious protobuf message
- **Fix:** Upgrade to protobufjs >= 7.2.5
- **References:** https://nvd.nist.gov/vuln/detail/CVE-2024-12345
```

### Remediation Priority Matrix

| EPSS > 0.1 | KEV Listed | CVSS | Priority |
|------------|------------|------|----------|
| ✅ | ✅ | Any | **Immediate** (hours) |
| ✅ | ❌ | Critical/High | **Urgent** (24h) |
| ❌ | ✅ | Any | **Urgent** (24h) |
| ✅ | ❌ | Medium | **Soon** (sprint) |
| ❌ | ❌ | High | **Scheduled** (week) |
| ❌ | ❌ | Medium/Low | **Backlog** (month) |

---

## Quick Reference

```bash
# Fast dependency scan (auto-detect ecosystem)
bash scripts/scan-dependencies.sh

# Full scan with SBOM generation
bash scripts/scan-dependencies.sh --full --sbom

# Container image scan
bash scripts/scan-dependencies.sh --image nginx:1.25

# Generate CycloneDX SBOM
bash scripts/generate-sbom.sh --format cyclonedx

# Generate SPDX SBOM with signing
bash scripts/generate-sbom.sh --format spdx --sign --key cosign.key

# Verify container provenance
bash scripts/verify-provenance.sh --image ghcr.io/owner/app@sha256:abc123

# Verify artifact provenance
bash scripts/verify-provenance.sh --artifact ./binary --provenance attestation.intoto.jsonl

# CI mode (JSON output, non-zero exit on failure)
bash scripts/scan-dependencies.sh --ci --fail-on high

# License-only scan
bash scripts/scan-dependencies.sh --licenses-only
```

---

## Common Pitfalls & Anti-Patterns

### ❌ Scanning Without Lockfiles

Running `npm audit` or `pip-audit` against `package.json` or `requirements.txt` without
lockfiles only scans direct dependencies. Transitive dependencies (which account for
~80% of vulnerabilities) are missed.

**✅ Fix:** Always use lockfiles. Commit them. Scan the lockfile, not the manifest.

### ❌ Trusting CVSS Scores Blindly

A CVSS 7.5 vulnerability in a development-only tool (e.g., a test runner) that never
touches production data is less urgent than a CVSS 5.0 vulnerability in a
network-facing production dependency.

**✅ Fix:** Contextualize CVSS with asset criticality, attack surface, and actual usage.

### ❌ Ignoring License Compliance

Teams often focus exclusively on CVEs and overlook license violations. Using a
GPL-licensed library in proprietary software can be as damaging as a vulnerability.

**✅ Fix:** Always run license detection alongside vulnerability scanning.

### ❌ One-Time Scans

A scan at release time finds vulnerabilities that may have been present (and exploitable)
for weeks. The mean time to detect (MTTD) for supply chain attacks is measured in months.

**✅ Fix:** Scan on every push, every PR, and nightly on a schedule. Integrate into CI/CD.

### ❌ Blocking Deployments on Every Finding

Failing CI on every medium-severity finding leads to alert fatigue and teams disabling
the check entirely.

**✅ Fix:** Fail on Critical/High with known exploits only. Track Medium findings as
tickets. Use grace periods for newly published CVEs without fixes.

### ❌ Using Outdated Vulnerability Databases

Running `grype` without updating its database scans against stale data. New CVEs are
published daily. Supply chain attacks appear suddenly.

**✅ Fix:** Always update databases before scanning (`grype db update`, `trivy image --refresh`).

### ❌ Generating SBOMs Without Storing Them

An SBOM generated and discarded is useless. SBOMs are only valuable when preserved
alongside the artifact they describe.

**✅ Fix:** Commit SBOMs to the repository, attach to releases, or push to a dedicated
SBOM registry. Treat them as build artifacts with the same retention as binaries.

### ❌ Assuming Provenance Exists

Currently, the vast majority of open-source projects and container images lack
SLSA provenance attestations. Assuming provenance exists leads to false confidence.

**✅ Fix:** Distinguish between "provenance verified" and "no provenance available".
Flag the latter as a risk, not a pass. Prefer artifacts with provenance when choosing
between alternatives.

---

## CI/CD Integration Patterns

### GitHub Actions

```yaml
name: Supply Chain Security
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily at 06:00 UTC

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install syft & grype
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
          curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
      - name: Run Supply Chain Scan
        run: bash scripts/scan-dependencies.sh --ci --fail-on high
      - name: Generate SBOM
        run: bash scripts/generate-sbom.sh --format cyclonedx
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom-*.cdx.json
      - name: Upload Scan Report
        uses: actions/upload-artifact@v4
        with:
          name: scan-report
          path: scan-report-*.json
```

### GitLab CI

```yaml
supply-chain-scan:
  stage: test
  image: alpine:latest
  before_script:
    - apk add --no-cache curl bash jq
    - curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
    - curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
  script:
    - bash scripts/scan-dependencies.sh --ci --fail-on high
    - bash scripts/generate-sbom.sh --format cyclonedx
  artifacts:
    paths:
      - sbom-*.cdx.json
      - scan-report-*.json
    expire_in: 30 days
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit — Block commits with critical vulnerabilities
bash scripts/scan-dependencies.sh --ci --fail-on critical
if [ $? -ne 0 ]; then
  echo "❌ Commit blocked: critical vulnerabilities found."
  echo "   Review the scan report and fix before committing."
  exit 1
fi
```

---

## Ecosystem Vulnerability Databases

### Primary Databases

| Database | Scope | API | Best For |
|----------|-------|-----|----------|
| **NVD** (National Vulnerability Database) | All software (CVE) | REST API (rate-limited) | Authoritative CVE data, CVSS scores |
| **GHSA** (GitHub Advisory Database) | npm, PyPI, RubyGems, Maven, Go, NuGet, Rust, Composer | GraphQL API | Developer-friendly advisories, fix versions |
| **OSV** (Open Source Vulnerabilities) | All ecosystems, unified schema | REST API | Cross-ecosystem queries, automated tooling |

### Querying the Databases

```bash
# NVD API (requires API key for production)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2024-12345" \
  -H "apiKey: $NVD_API_KEY" | jq '.vulnerabilities[0].cve'

# GHSA via GitHub CLI
gh api graphql -f query='
  query($cve: String!) {
    securityAdvisory(ghsaId: $cve) {
      summary severity identifiers { value }
      vulnerabilities(first: 5) {
        nodes { package { ecosystem name } vulnerableVersionRange firstPatchedVersion { identifier } }
      }
    }
  }
' -f cve="GHSA-xxxx-xxxx-xxxx"

# OSV API (no auth required)
curl -s "https://api.osv.dev/v1/query" -d '{
  "package": {"name": "lodash", "ecosystem": "npm"},
  "version": "4.17.20"
}' | jq '.vulns[] | {id: .id, summary: .summary, severity: .severity}'
```

### When to Use Each

- **NVD:** Legal/compliance reports requiring authoritative CVE data. Slow, rate-limited.
- **GHSA:** Developer workflows, quick fix-version lookups. Fast. GitHub-native.
- **OSV:** Cross-ecosystem tooling, automated pipelines. Machine-readable schema.

Production scans should use Grype or Trivy, which aggregate all three databases internally.

---

## OWASP Agentic Skills Top 10 Context

The OWASP Agentic Skills Top 10 (AST10:2026) highlights supply chain security as a
critical concern for agentic AI platforms. Key risks relevant to this skill:

- **AST01:2026 — Prompt Injection via Malicious Dependencies**: A compromised
  dependency can inject malicious prompts into agent workflows. SBOM verification
  and provenance checks are defensive controls.
- **AST03:2026 — Insecure Skill Design**: Skills without supply chain scanning
  may themselves contain vulnerable dependencies. Self-audit with this skill.
- **AST06:2026 — Excessive Agency via Compromised Tools**: Vulnerable CLI tools
  (scanners themselves) can be attack vectors. Keep scanners updated.
- **AST08:2026 — Supply Chain Poisoning**: Directly the domain of this skill.
  Dependency confusion, typosquatting, and compromised registries.

See `references/owasp-ast10-summary.md` for the full summary.

---

## SEO Metadata

<!-- SEO_META
keywords: supply chain security, SBOM, software bill of materials, dependency scanning,
  vulnerability audit, license compliance, provenance verification, software composition analysis,
  OWASP, SLSA framework, supply chain scanner, npm audit, pip audit, OWASP Dependency-Check,
  Syft, Grype, cosign, slsa-verifier, trivy, CVE scanning, CycloneDX, SPDX, DevSecOps,
  agent skill, agentic security, container image scanning, dependency confusion,
  typosquatting, open source security, NVD, GHSA, OSV
category: security
subcategory: supply-chain
difficulty: intermediate
requires_network: true
estimated_duration: 2-15 minutes (depends on project size and network speed)
compatible_agents: any-agent-platform
target_audience: DevSecOps, security engineers, open-source maintainers, compliance teams
last_validated: 2026-06-09
-->
