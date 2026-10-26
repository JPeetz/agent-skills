---
name: data-privacy-compliance
description: Use this skill when handling PII, personal data, privacy regulations, data subject requests, consent management, data breach response, or any GDPR/CCPA/HIPAA compliance task. Provides structured privacy compliance workflows based on regulatory frameworks.
---

# Data Privacy & Compliance

## Overview

Structured privacy compliance workflows for AI agents handling personal data. Covers GDPR (EU), CCPA/CPRA (California), HIPAA (US Healthcare), and general privacy engineering practices. Each workflow maps to specific regulatory requirements with verification gates.

**Important:** This skill provides educational reference workflows, not legal advice. Consult qualified legal counsel for compliance decisions in production.

## When to Use

- Processing data subject access requests (DSARs) across jurisdictions
- Conducting privacy impact assessments (PIAs/DPIAs)
- Evaluating cross-border data transfer mechanisms
- Handling consent management and cookie compliance
- Responding to data breaches with notification obligations
- Implementing privacy by design in new features
- Auditing data processing activities
- Classifying and inventorying personal data
- Establishing data retention schedules
- Reviewing vendor data processing agreements

## Core Privacy Principles

Regardless of jurisdiction, these principles apply universally:

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| Lawfulness | Process data on a valid legal basis | Identify and document the basis before collection |
| Purpose Limitation | Only use data for the purpose it was collected | Document purposes at collection point |
| Data Minimization | Collect only what's necessary | Audit collection fields regularly |
| Accuracy | Keep data accurate and up to date | Implement verification workflows |
| Storage Limitation | Delete when no longer needed | Enforce retention schedules |
| Integrity & Confidentiality | Secure data appropriately | Apply encryption, access controls |
| Accountability | Demonstrate compliance | Maintain records of processing |

## GDPR Compliance Workflow

### Determine Applicability

Check if GDPR applies:

1. Does the organization have an establishment in the EU/EEA?
2. Does the organization offer goods/services to data subjects in the EU/EEA?
3. Does the organization monitor behavior of data subjects in the EU/EEA?
4. Does the processing involve personal data of EU/EEA residents?

If YES to any → GDPR applies. Proceed with compliance assessment.

### Data Mapping & ROPA

Create or update the Record of Processing Activities (Article 30):

| Field | Description |
|-------|-------------|
| Processing purpose | Why is the data being processed? |
| Data categories | What types of personal data? |
| Data subjects | Whose data? (customers, employees, etc.) |
| Legal basis | Art. 6 basis (consent, contract, legal obligation, etc.) |
| Recipients | Who receives the data? |
| Transfers | Cross-border transfer mechanisms |
| Retention period | How long is data kept? |
| Technical safeguards | Encryption, access controls, etc. |

### Data Subject Rights Handling

When receiving a DSAR, follow this workflow:

1. **Verify identity** — Confirm the requestor is who they claim to be (without excessive data collection)
2. **Acknowledge receipt** — Within the regulatory timeline (GDPR: without undue delay, max 1 month)
3. **Scope the request** — Identify what personal data is held, where, and in what systems
4. **Retrieve data** — Search across all systems (production, backups, logs, analytics)
5. **Redact third-party data** — Remove or anonymize data of other individuals
6. **Format response** — Machine-readable format if requested; common formats include JSON, CSV, PDF
7. **Deliver securely** — Encrypted delivery, identity-verified channel
8. **Document** — Log the request, steps taken, and outcome for accountability

### Breach Notification

Timeline varies by jurisdiction:

| Jurisdiction | Notification Timeline | Regulator | Individuals |
|-------------|---------------------|-----------|-------------|
| GDPR (EU) | 72 hours | Lead Supervisory Authority | Without undue delay |
| CCPA (California) | No specific timeline | Attorney General | Promptly |
| HIPAA (US Healthcare) | 60 days | HHS | Within 60 days |
| LGPD (Brazil) | 72 hours | ANPD | Simultaneously |
| PIPEDA (Canada) | As soon as possible | OPC/OIPC | As soon as possible |

**Breach response workflow:**

1. **Contain** — Stop the breach from spreading (revoke credentials, isolate systems)
2. **Assess** — Determine scope: what data, how many records, who is affected
3. **Notify** — Inform regulator within required timeline
4. **Communicate** — Inform affected data subjects with clear remediation steps
5. **Document** — Record all actions taken, timelines, and decisions
6. **Remediate** — Fix the root cause, update security measures
7. **Review** — Post-incident review to prevent recurrence

## CCPA/CPRA Compliance

### Key Rights Under CCPA/CPRA

| Right | Description | Timeline |
|-------|-------------|----------|
| Right to Know | What personal data is collected, used, shared | 10 business days |
| Right to Delete | Request deletion of personal data | 45 calendar days |
| Right to Opt-Out | Opt out of sale/sharing of personal data | 15 business days |
| Right to Correct | Correct inaccurate personal data | Reasonable timeframe |
| Right to Limit Use | Limit use of sensitive personal data | Reasonable timeframe |
| Right to Non-Discrimination | No price/service discrimination for exercising rights | Ongoing |

### CCPA Assessment Checklist

- [ ] Determine if business is subject to CCPA (revenue >$25M, 100K+ records, or 50%+ revenue from data)
- [ ] Update privacy notice with CCPA-required disclosures
- [ ] Implement opt-out mechanism (Do Not Sell/Share link)
- [ ] Establish DSAR handling procedures
- [ ] Audit data sharing with third parties
- [ ] Review and update data processing agreements
- [ ] Train staff on CCPA requirements
- [ ] Document consumer request metrics

## HIPAA Compliance (US Healthcare)

### Key Rules

| Rule | Focus | Key Requirements |
|------|-------|------------------|
| Privacy Rule | Protected Health Information (PHI) use and disclosure | Patient rights, minimum necessary standard |
| Security Rule | Administrative, physical, technical safeguards | Risk analysis, access controls, audit controls |
| Breach Notification Rule | Notification following breach | Timelines vary by scale |
| Enforcement Rule | Penalties and procedures | Tiered civil money penalties |

### HIPAA Safeguards

**Administrative:**
- Designate a Security/Privacy Officer
- Conduct risk analysis
- Implement workforce training
- Establish contingency plans
- Regularly review and update policies

**Physical:**
- Facility access controls
- Workstation and device security
- Media controls (reuse, disposal)

**Technical:**
- Access controls (unique user IDs, emergency access, automatic logoff)
- Audit controls (track PHI access)
- Integrity controls (ensure PHI not improperly altered)
- Transmission security (encryption)

## Privacy by Design

Embed privacy into the development lifecycle:

1. **Proactive not reactive** — Anticipate privacy risks before they materialize
2. **Privacy as default** — Collect minimum data; don't rely on opt-out
3. **Embedded into design** — Privacy is core functionality, not a bolt-on
4. **Full functionality** — Privacy doesn't mean diminished features
5. **End-to-end security** — Protect data throughout its lifecycle
6. **Visibility and transparency** — Data subjects should know what's collected
7. **Respect for user privacy** — User-centric design, give meaningful choices

**Implementation checklist for new features:**
- [ ] Data flow mapping completed
- [ ] Legal basis identified and documented
- [ ] Data minimization applied (collect only what's needed)
- [ ] Privacy notice drafted at point of collection
- [ ] Access controls designed in
- [ ] Retention schedule determined
- [ ] Third-party data sharing identified
- [ ] Cross-border transfer mechanism assessed
- [ ] Encryption standards applied
- [ ] Incident response plan updated

## Common Compliance Pitfalls

| Pitfall | Risk | Prevention |
|---------|------|------------|
| Assuming one regulation covers everything | Missing jurisdiction-specific requirements | Map all applicable regulations per data flow |
| Storing data indefinitely | Violates storage limitation | Implement and enforce retention schedules |
| Relying solely on consent | Consent can be withdrawn; other bases may be more appropriate | Identify primary legal basis; document alternatives |
| Ignoring cross-border transfers | Major fines under GDPR Schrems II framework | Map data flows; implement SCCs or BCRs where needed |
| Treating anonymization as silver bullet | Re-identification risks remain | Use formal anonymization standards and verify |
| Not documenting compliance | Cannot prove accountability without records | Maintain ROPA, PIAs, and processing logs |
| Forgetting employees' privacy rights | Employee data is still personal data | Apply same rigor to internal processing |
| Overlooking data processor obligations | Liability flows both ways | Review DPAs; ensure processors have equivalent safeguards |

## Red Flags

- Collecting data without a documented legal basis
- Data retention periods described as "indefinite" or "as needed"
- No process for handling DSARs
- Personal data stored in unencrypted form
- Cross-border transfers without documented safeguards
- No incident response plan for data breaches
- Cookie consent that doesn't offer equal accept/reject options
- Dark patterns that nudge users toward sharing more data
- Third-party data sharing without adequate DPAs
- Logging or analytics that capture PII unnecessarily