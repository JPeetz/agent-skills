# OWASP Agentic Skills Top 10 (AST10:2026) — Supply Chain Context

> **Source:** OWASP Foundation, Agentic Skills Top 10:2026
> **Published:** June 2026
> **Relevance:** This summary focuses on how AST10 risks apply to supply chain
> security in agentic platforms and how the supply-chain-security-scanner skill
> addresses them.

## Overview

The OWASP Agentic Skills Top 10 (AST10) is a risk-awareness document for AI
agent platforms where user-installed skills (plugins, extensions, tools) can
execute arbitrary code with agent-level permissions. Published by OWASP in
2026, it mirrors the OWASP Top 10 for Web Applications but tailored for the
unique threat surface of agentic AI.

## Risk Categories Relevant to Supply Chain Security

### AST01:2026 — Prompt Injection via Malicious Dependencies

**Risk:** A dependency of an agent skill contains code that manipulates agent
prompts at runtime, redirecting agent behavior without the user's knowledge.
Compromised npm/pip packages are a primary delivery vector.

**Supply chain relevance:** Every dependency is a potential prompt injection
vector. The SBOM allows tracing which dependency introduced a poisoned package.

**Scanner mitigation:** The skill's Scan phase detects known-vulnerable
dependencies. SBOM anchoring enables precise attribution.

### AST03:2026 — Insecure Skill Design

**Risk:** Skills are distributed without security review, containing hardcoded
credentials, excessive permissions, or vulnerable dependency trees. Skills
inherit the same access as the agent platform.

**Supply chain relevance:** Skills that themselves import vulnerable dependencies
are a transitive risk. Self-auditing is critical.

**Scanner mitigation:** Running the scanner on the skill's own codebase catches
CVEs before the skill is deployed.

### AST06:2026 — Excessive Agency via Compromised Tools

**Risk:** Agent tools (scanners, CLIs, SDKs) with broad permissions can be
compromised to execute unauthorized operations on the host system. A tool
running as root has unlimited blast radius.

**Supply chain relevance:** Security tools like Syft, Grype, Trivy, and cosign
are themselves attack surfaces. Outdated or backdoored versions can produce
false clean reports.

**Scanner mitigation:** Verify the provenance of security tools themselves.
Check tool checksums against known-good releases. Update tools regularly.

### AST08:2026 — Supply Chain Poisoning

**Risk:** The primary supply chain risk category. Attackers compromise upstream
dependencies through:
- **Dependency confusion:** Publishing packages with names matching internal
  private packages to public registries.
- **Typosquatting:** Publishing packages with names similar to popular packages
  (e.g., `requets` instead of `requests`).
- **Account takeover:** Compromising maintainer accounts on npm, PyPI, etc.
- **Build pipeline injection:** Modifying CI/CD to inject malicious code during
  build.
- **Compromised registry:** Attacking the registry infrastructure itself.

**Supply chain relevance:** This is the direct focus of the scanner skill.

**Scanner mitigation:**
- SBOM generation creates an auditable dependency snapshot
- Provenance verification confirms artifacts came from expected sources
- Vulnerability scanning detects known compromises
- License checking catches unexpected packages (dependency confusion often
  uses permissive licenses on malicious packages)

### AST09:2026 — Inadequate Logging & Monitoring

**Risk:** Agent platforms lack audit trails for skill execution, making
post-incident investigation impossible.

**Supply chain relevance:** Without logged scans and stored SBOMs, you cannot
determine whether a vulnerability existed when an incident occurred.

**Scanner mitigation:** Always timestamp and store scan reports. Commit SBOMs
to version control. Use the SBOM lifecycle for audit trails.

## AST10 Full Listing (2026)

| # | Risk | Supply Chain Relevance |
|---|------|----------------------|
| AST01 | Prompt Injection via Malicious Dependencies | HIGH — Dependencies as injection vectors |
| AST02 | Insecure Output Handling | MEDIUM — Scan reports could be tampered |
| AST03 | Insecure Skill Design | HIGH — Skills with vulnerable trees |
| AST04 | Excessive Permissions | MEDIUM — Scanner tool permissions |
| AST05 | Data Leakage via Skills | LOW — Scan results contain dependency info |
| AST06 | Excessive Agency via Compromised Tools | HIGH — Scanners as attack surface |
| AST07 | Model Theft via Skills | LOW |
| AST08 | Supply Chain Poisoning | CRITICAL — Direct domain |
| AST09 | Inadequate Logging & Monitoring | MEDIUM — Missing audit trails |
| AST10 | Unverified Skill Sources | MEDIUM — Skills from untrusted origins |

## Research Findings

A 2026 academic study found that **26.1% of community-contributed agent skills**
contain at least one known vulnerability in their dependency trees.
Furthermore, **8.7% contain critical vulnerabilities** (CVSS ≥ 9.0) that
could lead to remote code execution on the agent host.

Key findings:
- **npm-based skills:** 31.2% vulnerable (largest ecosystem, most targets)
- **Python-based skills:** 24.5% vulnerable
- **Unpinned dependencies:** Present in 62% of skills (no lockfile, floating
  version ranges)
- **Average dependency depth:** 8.3 levels (transitive risk is significant)

## Recommendations from OWASP AST10

1. **Generate SBOMs** for every skill before deployment
2. **Verify provenance** of all skill dependencies
3. **Scan for known CVEs** on every dependency update
4. **Pin dependencies** with lockfiles and integrity hashes
5. **Use private registries** with vulnerability scanning for internal packages
6. **Implement dependency firewall** — block installations of packages with
   known-critical vulnerabilities
7. **Audit skill permissions** — limit what scanners can access
8. **Maintain audit logs** of all supply chain scans

## References

- OWASP Agentic Skills Top 10: https://owasp.org/www-project-agentic-skills-top-10/
- OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/
- OWASP CycloneDX: https://cyclonedx.org/
- SLSA Framework: https://slsa.dev/
