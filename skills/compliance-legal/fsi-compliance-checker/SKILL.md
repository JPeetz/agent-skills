---
name: fsi-compliance-checker
description: >-
  Maps code, architecture, and infrastructure changes to specific control IDs in financial services
  compliance frameworks — PCI-DSS v4.0 for payment card data and MAS TRM for Singapore-regulated
  institutions — producing an audit-traceable findings report with per-control remediation. Use this
  instead of a general security review whenever a compliance framework (PCI-DSS, MAS TRM), regulator,
  audit, or cardholder-data scope is mentioned, even if the request is phrased as a code review or a
  yes/no compliance question. Triggers on: "PCI-DSS check", "MAS TRM", "is this compliant",
  "compliance review", "audit this change for banking regulations", "does logging this violate PCI",
  "cardholder data handling review".
category: compliance-legal
---

# FSI Compliance Checker

Map a concrete change (code diff, architecture design, IaC, pipeline config) to the specific controls it touches in financial services compliance frameworks, and report gaps with actionable remediation. This is engineering-level compliance triage — it helps teams catch violations before audit, but it does not replace a qualified assessor (QSA) or the institution's compliance function. Say so in every report.

## Framework Selection

Load only the reference file(s) the engagement needs:

| Situation | Load |
|-----------|------|
| Payment card data is stored, processed, or transmitted (PAN, CVV, track data) | [references/pci-dss.md](references/pci-dss.md) |
| Singapore-regulated financial institution (bank, insurer, capital markets, major payment institution) | [references/mas-trm.md](references/mas-trm.md) |
| Both apply (e.g. Singapore bank handling cards) | Both files |
| Other jurisdictions/frameworks (SOX, GDPR, HKMA, APRA) | State that they are out of scope of this skill's bundled references; offer general secure-engineering review instead |

If the user hasn't said which applies, ask one question: what data does the change touch, and is the institution Singapore-regulated?

## Review Process

1. **Scope the change.** Identify what the diff/design actually touches: data elements (card data? customer PII? credentials?), trust boundaries, environments (production? DR?), and third parties.
2. **Select applicable controls** from the loaded reference file(s) — typically 5-15 controls, not the whole framework. List what you ruled out and why (one line each) so the scoping is auditable.
3. **Assess each applicable control** against the change: `Compliant` / `Gap` / `Needs evidence` (can't tell from the artifact — name the evidence required).
4. **Write findings** using the report format below. Every Gap gets: the control ID, what's wrong in this specific change, concrete remediation, and severity (Critical = violation involving live regulated data; High = control absent; Medium = control partial/undocumented).
5. **Recommend story conversion**: offer to turn findings into backlog items (via the security-story-writing skill if available) with the control ID in each story for traceability.

## Report Format

```markdown
# Compliance Review: [change title]
**Frameworks:** [PCI-DSS v4.0 / MAS TRM 2021] · **Date:** [YYYY-MM-DD]
**Scope:** [what was reviewed: files, design doc, pipeline]
> Engineering triage only — not a substitute for QSA assessment or the compliance function.

## Data & Boundary Analysis
- Data elements touched: [e.g. PAN (masked), customer NRIC, none]
- Environments/boundaries: [e.g. CDE-adjacent service, public API]

## Findings
| # | Control | Status | Severity | Finding | Remediation |
|---|---------|--------|----------|---------|-------------|
| 1 | [PCI 3.5.1] | Gap | Critical | [specific issue in this change] | [specific fix] |

## Ruled Out (not applicable)
- [Control area] — [one-line reason]

## Evidence Needed
- [Control]: [what artifact would demonstrate compliance]
```

## Common FSI Engineering Triggers

Changes that almost always have compliance impact — check these proactively when they appear in a diff:

- Logging statements near payment or authentication flows (PAN/CVV must never be logged; MAS TRM requires security event logging — both directions matter)
- New data stores or caches receiving customer or card data (encryption at rest, retention, residency)
- Authentication/session changes (MFA requirements, session timeout, credential storage)
- New third-party SDKs or API integrations (outsourcing/vendor controls, data flows leaving the boundary)
- Infrastructure changes touching network segmentation, security groups, or public exposure
- CI/CD changes that alter who/what can deploy to production (change management, segregation of duties)

## Guidelines

- Cite control IDs precisely (e.g. "PCI-DSS 8.3.6", "MAS TRM 9.1.1") so findings are traceable in audit tooling; the reference files carry the ID schemes.
- Severity discipline: don't inflate. A missing comment is not a Critical; unencrypted PAN at rest is.
- When the change is compliant, say so affirmatively per control — "no findings" plus the checked-control list is a useful audit artifact.
- Never output real card numbers, even as examples; use the standard test PANs (e.g. 4111 1111 1111 1111) when illustrating.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "It's just a dev environment, PCI doesn't apply there" | If the dev environment touches real card data or mirrors production CDE boundaries, it is in scope. Scope exclusions must be explicit in the compliance program. |
| "We're not storing PAN, so we're compliant" | Transmission of PAN (in memory, over the wire) is still regulated. Logging, caching, or error messages containing card data are all violations. |
| "We use a third-party payment processor, so card data never touches us" | Verify this at the architectural level. Many integrations receive raw PAN at some point (webhook payloads, redirect back URLs, iframe parent-communication). |
| "The compliance team will catch this later" | The compliance team reviews policy. Engineering changes are invisible to them unless surfaced. This review is the surface. |
| "It's just a small change, compliance review is overkill" | Compliance impact is about the data touched, not the diff size. A one-line logging change can be a Critical PCI violation. |
| "We handle PII, so PCI doesn't apply" | PII regulations (GDPR, PDPA) are separate from PCI-DSS. Card data has its own framework regardless of PII compliance. |
| "The other frameworks aren't in the reference files, so I can ignore compliance entirely" | State which frameworks are out of scope and why. Don't silently skip — silence looks like an oversight. |

## Verification

- [ ] Did you scope the data elements before selecting controls?
- [ ] Is every finding mapped to a specific control ID?
- [ ] Does each finding include a concrete remediation, not a general principle?
- [ ] Is the QSA disclaimer present in the report?
- [ ] Are ruled-out controls listed with reasons (not silently skipped)?
- [ ] Did you flag any evidence gaps separately from compliance findings?
- [ ] Did you offer to convert findings into backlog stories?