# SBOM Formats: SPDX vs CycloneDX

## Overview

Two dominant SBOM standards exist: **SPDX** (Software Package Data Exchange)
from the Linux Foundation and **CycloneDX** from OWASP. Both satisfy U.S.
Executive Order 14028 requirements and the NTIA minimum elements. They serve
different primary use cases but overlap significantly.

## Quick Comparison

| Aspect | SPDX 2.3 | CycloneDX 1.5 |
|--------|----------|---------------|
| **Originating body** | Linux Foundation | OWASP |
| **First release** | 2011 | 2017 |
| **Primary use case** | License compliance | Security/vulnerability |
| **Secondary use** | Security (via external refs) | License compliance, inventory |
| **ISO standard** | ISO/IEC 5962:2021 | (In progress) |
| **Mandatory fields** | 12 (SPDX 2.3) | 5 (CycloneDX 1.5) |
| **JSON schema** | ✅ | ✅ |
| **XML schema** | ✅ (RDF/XML) | ✅ |
| **Tag-value format** | ✅ (unique to SPDX) | ❌ |
| **PURL support** | ✅ (SPDX 2.3+) | ✅ (native) |
| **CPE support** | ✅ | ✅ |
| **SWID support** | ✅ | ✅ |
| **VEX integration** | Via external document ref | ✅ Native VEX |
| **Native vulnerability** | ❌ | ✅ |
| **Pedigree/supply chain** | ✅ | ✅ |
| **Cryptographic hashes** | ✅ (SHA1, SHA256, SHA512, MD5) | ✅ (SHA1, SHA256, SHA384, SHA512, MD5) |
| **NTIA compliant** | ✅ | ✅ |
| **Package URL (PURL)** | ✅ 2.3+ | ✅ Native |
| **File-level detail** | ✅ | Limited |
| **Snippet-level detail** | ✅ | ❌ |

## NTIA Minimum Elements

Per the U.S. National Telecommunications and Information Administration (NTIA),
every SBOM must include these minimum elements. Both SPDX and CycloneDX satisfy
all requirements.

| Element | SPDX Field | CycloneDX Field |
|---------|-----------|-----------------|
| **Supplier name** | `PackageSupplier` | `component.supplier.name` |
| **Component name** | `PackageName` | `component.name` |
| **Version** | `PackageVersion` | `component.version` |
| **Unique identifier** | `SPDXID`, `PackageChecksum` | `bom-ref`, PURL, CPE |
| **Dependency relationships** | `Relationship` (DEPENDS_ON) | `dependencies` array |
| **Author** | `Creator` | `metadata.authors` |
| **Timestamp** | `Created` | `metadata.timestamp` |

## When to Use Which

### Use CycloneDX When:

- **Primary goal is vulnerability management**
- Integrating with Grype, Trivy, or OWASP Dependency-Track
- You need VEX (Vulnerability Exploitability eXchange) data inline
- You're in a DevSecOps pipeline focused on CVEs
- Simpler schema is preferred (fewer required fields)
- Your ecosystem tools default to CycloneDX (Syft, Trivy, Grype)

### Use SPDX When:

- **Primary goal is license compliance**
- Enterprise legal review is required (SPDX is an ISO standard)
- You need file-level or snippet-level detail
- Integrating with FOSSology, ORT, or SW360
- You're in a heavily regulated industry requiring ISO compliance
- You need the tag-value human-readable format

### Generate Both When:

- You have both security and compliance requirements
- You're in an enterprise with separate security and legal teams
- You're publishing open-source releases (SPDX for community, CycloneDX for consumers)
- Regulations require both perspectives

## Structural Differences

### CycloneDX (Simplified Example)

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "metadata": {
    "timestamp": "2026-06-09T02:07:00Z",
    "component": {
      "name": "my-app",
      "version": "2.1.0",
      "type": "application",
      "bom-ref": "pkg:npm/my-app@2.1.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "lodash",
      "version": "4.17.21",
      "purl": "pkg:npm/lodash@4.17.21",
      "licenses": [{"license": {"id": "MIT"}}]
    }
  ],
  "dependencies": [
    {"ref": "pkg:npm/my-app@2.1.0", "dependsOn": ["pkg:npm/lodash@4.17.21"]}
  ]
}
```

### SPDX (Simplified Example)

```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "my-app",
  "creationInfo": {
    "created": "2026-06-09T02:07:00Z",
    "creators": ["Tool: Syft"]
  },
  "packages": [
    {
      "SPDXID": "SPDXRef-my-app",
      "name": "my-app",
      "versionInfo": "2.1.0",
      "downloadLocation": "NOASSERTION",
      "licenseConcluded": "NOASSERTION",
      "copyrightText": "NOASSERTION"
    },
    {
      "SPDXID": "SPDXRef-lodash",
      "name": "lodash",
      "versionInfo": "4.17.21",
      "licenseConcluded": "MIT",
      "externalRefs": [
        {"referenceCategory": "PACKAGE-MANAGER", "referenceType": "purl", "referenceLocator": "pkg:npm/lodash@4.17.21"}
      ]
    }
  ],
  "relationships": [
    {"spdxElementId": "SPDXRef-my-app", "relationshipType": "DEPENDS_ON", "relatedSpdxElementId": "SPDXRef-lodash"}
  ]
}
```

## VEX (Vulnerability Exploitability eXchange)

VEX is a companion format that tells consumers whether a product is affected by
a specific vulnerability. It's critical for reducing false-positive fatigue.

### CycloneDX VEX

CycloneDX 1.4+ supports VEX natively through the `vulnerabilities` array:

```json
{
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "affects": [{"ref": "pkg:npm/protobufjs@7.2.4"}],
      "analysis": {
        "state": "not_affected",
        "detail": "The vulnerable function is not called in our codebase",
        "justification": "code_not_reachable"
      }
    }
  ]
}
```

### SPDX VEX

SPDX handles VEX through external document references linking to a separate
VEX document:

```
ExternalRef: SECURITY vex-location https://example.com/vex.json
```

## Tool Support Matrix

| Tool | CycloneDX Output | SPDX Output | VEX Support |
|------|:---:|:---:|:---:|
| **Syft** | ✅ | ✅ | ✅ (via Grype) |
| **Trivy** | ✅ | ✅ | Partial |
| **Grype** | Input only | Input only | N/A |
| **Dependency-Track** | ✅ | ✅ | ✅ |
| **FOSSology** | ❌ | ✅ | ❌ |
| **ORT** | ✅ | ✅ | ❌ |
| **SPDX tools** | ❌ | ✅ | ✅ |

## Generating SBOMs with the Scanner

```bash
# CycloneDX JSON (recommended for security)
bash scripts/generate-sbom.sh --format cyclonedx-json

# SPDX JSON (for license compliance)
bash scripts/generate-sbom.sh --format spdx-json

# Both formats
bash scripts/generate-sbom.sh --format cyclonedx-json
bash scripts/generate-sbom.sh --format spdx-json
```

## References

- SPDX Specification: https://spdx.dev/specifications/
- CycloneDX Specification: https://cyclonedx.org/specification/overview/
- NTIA SBOM Minimum Elements: https://www.ntia.gov/page/software-bill-materials
- Executive Order 14028: https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/
