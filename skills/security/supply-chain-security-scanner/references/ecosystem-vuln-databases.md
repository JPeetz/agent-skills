# Ecosystem Vulnerability Databases

## Overview

Supply chain security scanning depends on authoritative vulnerability data. Three
primary databases power the ecosystem, plus several specialized sources. This
document covers how to query each and when to use them.

## Primary Databases

### 1. NVD — National Vulnerability Database

**URL:** https://nvd.nist.gov/
**Operator:** NIST (U.S. National Institute of Standards and Technology)
**Scope:** All published CVEs across all software
**API:** REST API v2.0 (requires API key for production use)
**Update frequency:** Continuous (multiple times daily)

The NVD is the canonical source for CVE data. It assigns CVSS scores, CWE
mappings, and CPE identifiers. It is the most authoritative source but also the
slowest to query and update.

#### API Usage

```bash
# Single CVE lookup (no API key — rate limited to 5 req/30s)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2024-12345" | jq .

# With API key (50 req/30s)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2024-12345" \
  -H "apiKey: YOUR_NVD_API_KEY" | jq .

# Search by keyword (requires API key for production)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=protobuf&resultsPerPage=20" \
  -H "apiKey: YOUR_NVD_API_KEY" | jq '.vulnerabilities | length'

# Filter by CVSS severity range
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cvssV3Severity=CRITICAL&pubStartDate=2026-01-01T00:00:00.000&pubEndDate=2026-06-09T23:59:59.999" \
  -H "apiKey: YOUR_NVD_API_KEY" | jq '.totalResults'
```

#### Rate Limits

| Tier | Requests/30s | API Key Required |
|------|:---:|:---:|
| Anonymous | 5 | No |
| With API key | 50 | Yes (free, request at https://nvd.nist.gov/developers/request-an-api-key) |

#### Key Fields in Response

```
.vulnerabilities[].cve.id                    # CVE ID
.vulnerabilities[].cve.metrics.cvssMetricV31[].cvssData.baseScore  # CVSS 3.1 score
.vulnerabilities[].cve.metrics.cvssMetricV31[].cvssData.vectorString  # CVSS vector
.vulnerabilities[].cve.descriptions[]        # Human-readable descriptions
.vulnerabilities[].cve.references[]          # Advisory links
.vulnerabilities[].cve.configurations[]      # Affected CPE configurations
.vulnerabilities[].cve.published             # Publication date
```

#### Strengths
- Most authoritative CVE data
- CVSS scores from NIST analysts
- CWE weakness mappings
- CPE identifiers for precise product matching

#### Limitations
- Slow API (high latency, rate-limited)
- No ecosystem-native identifiers (no PURL, no npm package names)
- Data enrichment lags behind GHSA and OSV
- No fix version information directly in CVE data

### 2. GHSA — GitHub Advisory Database

**URL:** https://github.com/advisories
**Operator:** GitHub
**Scope:** npm, PyPI, RubyGems, Maven, Go, NuGet, Rust (crates.io), PHP (Packagist), Swift
**API:** GraphQL (GitHub API)
**Update frequency:** Real-time (advisories published as soon as reviewed)

GHSA is the fastest-moving advisory database for developer ecosystems. GitHub's
security team reviews advisories and maps them to exact package names and
version ranges, including the first patched version.

#### API Usage

```bash
# Via GitHub CLI (recommended)
gh api graphql -f query='
  query($ecosystem: SecurityAdvisoryEcosystem!, $package: String!) {
    securityVulnerabilities(ecosystem: $ecosystem, package: $package, first: 10) {
      nodes {
        severity
        advisory {
          ghsaId summary description
          identifiers { type value }
          references { url }
        }
        vulnerableVersionRange
        firstPatchedVersion { identifier }
      }
    }
  }
' -f ecosystem=NPM -f package=lodash

# Direct curl to GitHub API
curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST https://api.github.com/graphql \
  -d '{"query":"{ securityAdvisory(ghsaId: \"GHSA-xxxx-xxxx-xxxx\") { summary severity identifiers { value } } }"}' | jq .
```

#### Key Fields

```
.securityVulnerabilities.nodes[].advisory.ghsaId     # GHSA ID
.securityVulnerabilities.nodes[].advisory.summary      # Short description
.securityVulnerabilities.nodes[].severity              # CRITICAL/HIGH/MODERATE/LOW
.securityVulnerabilities.nodes[].vulnerableVersionRange # e.g., "< 4.17.21"
.securityVulnerabilities.nodes[].firstPatchedVersion.identifier  # e.g., "4.17.21"
.securityVulnerabilities.nodes[].advisory.identifiers[]  # CVE and GHSA mappings
```

#### Strengths
- Fastest advisory publication pipeline
- Exact ecosystem-native identifiers (npm package names, PyPI names, etc.)
- First-patched-version data (actionable fix information)
- GraphQL API enables precise queries
- Curated by GitHub security team with high signal-to-noise ratio

#### Limitations
- GitHub API rate limits apply (5000 req/hour for authenticated users)
- GitHub-centric (requires GitHub account for API access)
- GraphQL learning curve
- Does not cover non-GitHub-ecosystem software (no proprietary, no embedded)

### 3. OSV — Open Source Vulnerabilities

**URL:** https://osv.dev/
**Operator:** Google / OpenSSF
**Scope:** All open-source ecosystems (aggregates 20+ databases)
**API:** REST API (no authentication required)
**Update frequency:** Continuous aggregation from source databases

OSV is a distributed vulnerability database that aggregates advisories from
ecosystem-specific databases into a unified schema. It powers pip-audit and
other automated tooling. The OSV schema is designed for machine consumption.

#### API Usage

```bash
# Query by package and version
curl -s -X POST https://api.osv.dev/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "package": {"name": "lodash", "ecosystem": "npm"},
    "version": "4.17.20"
  }' | jq '.vulns[] | {id: .id, summary: .summary, severity: .severity}'

# Query by commit hash (identifies vulnerabilities introduced/fixed by specific commits)
curl -s -X POST https://api.osv.dev/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "commit": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }' | jq .

# Batch query
curl -s -X POST https://api.osv.dev/v1/querybatch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"package": {"name": "lodash", "ecosystem": "npm"}, "version": "4.17.20"},
      {"package": {"name": "requests", "ecosystem": "PyPI"}, "version": "2.28.0"}
    ]
  }' | jq '.results[] | {id: .vulns[].id}'

# Get specific vulnerability by ID
curl -s https://api.osv.dev/v1/vulns/GHSA-xxxx-xxxx-xxxx | jq .
```

#### Strengths
- No authentication required
- Aggregates 20+ databases into unified schema
- Batch query support
- Commit-level vulnerability tracking
- Designed for automated tooling (pip-audit, osv-scanner)
- OpenSSF-backed, community-governed

#### Limitations
- Aggregation latency (depends on source databases updating)
- Less curated than NVD or GHSA
- No CVSS enrichment (relies on source databases)
- API stability varies across aggregator instances

## Ecosystem-Specific Databases

### npm Advisory Database
- **URL:** https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm
- **Used by:** `npm audit`
- **Access:** Built into npm CLI, also available via GHSA

### PyPI Advisory Database
- **URL:** https://github.com/pypa/advisory-database
- **Used by:** `pip-audit`
- **Access:** Git repository, also available via OSV

### RustSec Advisory Database
- **URL:** https://rustsec.org/advisories/
- **Used by:** `cargo audit`
- **Access:** Git repository, also available via OSV

### Go Vulnerability Database
- **URL:** https://vuln.go.dev/
- **Used by:** `govulncheck`
- **Access:** REST API, also available via OSV

### Maven Central / Sonatype OSS Index
- **URL:** https://ossindex.sonatype.org/
- **Used by:** OWASP Dependency-Check
- **Access:** REST API (free tier available)

## Database Aggregation in Scanners

### How Grype Uses Databases

Grype maintains a local vulnerability database (`~/.grype/db/`) that aggregates:
- NVD (CVSS scores, CPE mappings)
- GHSA (package-level fix versions)
- OSV (cross-ecosystem coverage)
- Red Hat Security Data
- Alpine SecDB
- Debian Security Tracker
- Ubuntu Security Notices
- Amazon Linux Security Center

```bash
# Update Grype's local database
grype db update

# Check database status
grype db status
# Output: Location, Built, Schema version, Checkpoint
```

### How Trivy Uses Databases

Trivy similarly aggregates multiple sources. It downloads vulnerability data
on first run and caches it:

```bash
# Force database refresh
trivy image --refresh nginx:latest

# Check database info
trivy --cache-dir /tmp/trivy-cache image nginx:latest
```

## Query Strategy for the Scanner Skill

When the scanner skill needs to look up specific vulnerability details beyond
what the CLI tools provide:

1. **First: Check Grype/Trivy output** — These already aggregate all databases
   and provide fix version information. Most queries are satisfied here.

2. **Second: Query GHSA** — For developer-friendly advisories with actionable
   fix information. Use `gh api graphql` if GitHub CLI is available.

3. **Third: Query OSV** — For cross-ecosystem queries or when a CVE maps to
   multiple packages across ecosystems. No authentication needed.

4. **Fourth: Query NVD** — For authoritative CVSS scores, CWE mappings, and
   compliance reporting. Use only when official NVD data is required.

## EPSS and KEV

### EPSS — Exploit Prediction Scoring System

**URL:** https://www.first.org/epss
**Operator:** FIRST.org
**Purpose:** Predicts the probability (0-1) that a vulnerability will be
exploited in the next 30 days.

```bash
# EPSS API (no auth required)
curl -s "https://api.first.org/data/v1/epss?cve=CVE-2024-12345" | jq '.data[] | {cve: .cve, epss: .epss, percentile: .percentile}'
```

**Interpretation:**
- EPSS > 0.1 (10%+ probability) → Prioritize above CVSS-only scoring
- EPSS > 0.4 (40%+ probability) → Immediate action regardless of CVSS base score

### KEV — Known Exploited Vulnerabilities Catalog

**URL:** https://www.cisa.gov/known-exploited-vulnerabilities-catalog
**Operator:** CISA (U.S. Cybersecurity and Infrastructure Security Agency)
**Purpose:** Lists vulnerabilities known to be actively exploited in the wild.

```bash
# CISA KEV catalog (JSON, always current)
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
  jq '.vulnerabilities[] | select(.cveID == "CVE-2024-12345")'
```

**Verdict:** Any vulnerability on the KEV catalog is **immediate-priority**
regardless of CVSS score.

## Remediation Priority Matrix

This is the priority matrix the scanner uses to assign remediation urgency:

| CVSS | EPSS > 0.1 | KEV Listed | Priority | Action Timeline |
|------|:---:|:---:|----------|-----------------|
| Any | Any | ✅ | **IMMEDIATE** | Hours |
| Critical (9.0+) | ✅ | ❌ | **URGENT** | 24 hours |
| High (7.0-8.9) | ✅ | ❌ | **URGENT** | 48 hours |
| Critical (9.0+) | ❌ | ❌ | **HIGH** | 72 hours |
| High (7.0-8.9) | ❌ | ❌ | **SCHEDULED** | Next sprint |
| Medium (4.0-6.9) | ✅ | ❌ | **SCHEDULED** | Next sprint |
| Medium (4.0-6.9) | ❌ | ❌ | **BACKLOG** | Within month |
| Low (0.1-3.9) | Any | ❌ | **MONITOR** | Opportunistic |

## References

- NVD API: https://nvd.nist.gov/developers
- GHSA GraphQL API: https://docs.github.com/en/graphql/reference/objects#securityadvisory
- OSV API: https://osv.dev/docs/
- EPSS: https://www.first.org/epss
- CISA KEV: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- Grype DB sources: https://github.com/anchore/grype#grype
- Trivy DB sources: https://aquasecurity.github.io/trivy/latest/docs/scanner/vulnerability/
