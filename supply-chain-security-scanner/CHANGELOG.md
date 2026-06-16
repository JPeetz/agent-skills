# Changelog

All notable changes to the supply-chain-security-scanner skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-09

### Added
- Initial release of the supply-chain-security-scanner skill.
- **SKILL.md** — Comprehensive skill definition with YAML frontmatter, 400+ lines of methodology, tool coverage, and remediation guidance.
- **scan-dependencies.sh** — Multi-ecosystem dependency vulnerability scanner with auto-detection of npm, PyPI, Maven, Go, Cargo, and container projects. Supports CI mode, fail-on thresholds, full scans, and license-only mode.
- **generate-sbom.sh** — SBOM generator producing CycloneDX JSON, CycloneDX XML, SPDX JSON, and SPDX tag-value formats via Syft. Includes validation, optional cosign signing, and OWASP Dependency-Track upload.
- **verify-provenance.sh** — Provenance verification script supporting container image signature verification (cosign), SLSA attestation checks (slsa-verifier), and artifact provenance validation.
- **owasp-ast10-summary.md** — Reference document summarizing the OWASP Agentic Skills Top 10 (2026) with supply chain relevance mapping, risk categorization, and research findings.
- **sbom-formats.md** — Reference document comparing SPDX 2.3 and CycloneDX 1.5 formats, NTIA minimum elements mapping, tool support matrix, and VEX handling.
- **ecosystem-vuln-databases.md** — Reference document covering NVD, GHSA, and OSV APIs with query examples, rate limits, EPSS/KEV priority matrix, and scanner database aggregation details.
- **evals.json** — 10 test cases (8 primary triggers + 2 near-miss negatives) with expected activation behavior, activation patterns, and keyword analysis.
- **LICENSE** — MIT License.
- **CHANGELOG.md** — This file.

### Coverage
- **Ecosystems:** npm/Node.js, PyPI/Python, Maven/Gradle/Java, Go modules, Cargo/Rust, Ruby/Bundler, PHP/Composer, .NET/NuGet, container images
- **Scanners:** npm audit, pip-audit, OWASP Dependency-Check, Syft, Grype, Trivy
- **Provenance:** cosign (image signing), slsa-verifier (SLSA attestations)
- **SBOM formats:** CycloneDX (JSON, XML), SPDX (JSON, tag-value)
- **Databases:** NVD, GHSA, OSV, EPSS, CISA KEV
- **Compliance:** NTIA minimum elements, SLSA levels 0–4, license policy enforcement
- **Integration:** GitHub Actions, GitLab CI, pre-commit hooks
