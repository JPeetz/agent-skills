---
name: threat-modeling
description: Use this skill when performing security reviews of features, APIs, or architecture changes. Produces a STRIDE threat model document with risk-rated threats, mitigations, and backlog-ready security stories. Use during sprint planning or design review.
---

# Threat Modeling (STRIDE)

## Overview

Produce a lightweight, sprint-compatible threat model: 15-30 minutes of structured analysis, not a multi-week security assessment. The output is a threat model document plus security stories the team can schedule.

## When to Use

- Designing a new feature or API endpoint
- Reviewing architecture changes
- Integrating with third-party services
- Processing personal data, payment data, or regulated data
- Sprint planning or design review sessions
- Any change that crosses a trust boundary

## Process

### 1. Establish the Data Flow

Ask for (or derive from the code/design) the feature's data flow: actors, entry points, services, data stores, and trust boundaries. Summarize it as:

```
Actor → Component || API Gateway → Service → Database
```

Mark each trust boundary crossing with `||`. If the user has architecture docs or code, read them instead of asking.

### 2. Walk the STRIDE Categories

Run each STRIDE category against every trust boundary crossing:

| # | Category | Question to Ask | Typical Mitigations |
|---|---|---|---|
| 1 | **S**poofing | Can someone pretend to be a user, service, or device? | Strong authentication, mTLS, signed tokens |
| 2 | **T**ampering | Can data be modified in transit or at rest? | TLS, integrity checks, signed payloads, immutable logs |
| 3 | **R**epudiation | Can an actor deny performing an action? | Audit logging with identity + timestamp, log integrity |
| 4 | **I**nformation disclosure | Can data leak to the wrong party? | Encryption, least-privilege access, output filtering, masking |
| 5 | **D**enial of service | Can the component be made unavailable? | Rate limiting, quotas, timeouts, autoscaling, circuit breakers |
| 6 | **E**levation of privilege | Can a user gain rights they shouldn't? | AuthZ checks at every boundary, input validation, sandboxing |

For each plausible threat, capture: description, category, likelihood (H/M/L), impact (H/M/L), and a concrete mitigation. Skip categories that genuinely don't apply — do not pad the table.

### 3. Rate Risk

- **High**: likelihood OR impact is High AND the other is at least Medium
- **Low**: only if BOTH likelihood and impact are Low
- **Medium**: everything else

### 4. Generate Security Stories

For every High and Medium threat, write security stories using the format below. Low threats go to the residual risk list with a one-line acceptance rationale.

### 5. Deliver the Document

Use the template below. Tell the user which stories should enter the next sprint.

## Threat Model Template

```markdown
# Threat Model: [Feature Name]

**Date:** [YYYY-MM-DD] · **Sprint/Milestone:** [if applicable] · **Participants:** [names/roles]

## Feature Description

[2-3 sentences: what it does and what data it touches]

## Data Flow

[Actor → Component || API Gateway → Service → Database]
(|| marks trust boundary crossings)

## STRIDE Analysis

| # | Threat | Category | Likelihood | Impact | Risk | Mitigation |
|---|--------|----------|-----------|--------|------|------------|
| 1 | [description] | [S/T/R/I/D/E] | H/M/L | H/M/L | H/M/L | [concrete control] |

## Security Stories Generated

- [ ] [Story title] — [priority] — [estimate if known]

## Residual Risks (accepted)

- [Low-risk threat] — [one-line justification for accepting]
```

## Security Story Format

```markdown
**As** [the system/security role], **I want** [security control], **so that** [risk is mitigated].
**Threat:** [STRIDE category + threat #] · **Source:** threat model [feature name]
**Acceptance:** Given [precondition], when [attack vector attempted], then [system prevents/detects/alerts].
```

## Guidelines

- Anchor every threat to a specific element of the data flow — "hackers could attack the API" is not a threat; "an unauthenticated caller can enumerate user IDs via GET /users/{id} (Information disclosure)" is.
- Prefer mitigations that already exist in the team's stack (their gateway, their IdP) over introducing new components.
- If the feature touches payment card data, personal data, or regulated industries, recommend a compliance pass (e.g., PCI-DSS, GDPR) in addition to the threat model.
- For a brand-new system rather than a feature, model the 2-3 most critical flows first rather than attempting full coverage in one session.
- The threat model is a living document — revisit it when the architecture changes.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Threat modeling takes too long" | A 15-minute STRIDE walkthrough for a feature catches design flaws that take days to fix in code. |
| "We use cloud infrastructure, they handle security" | Cloud providers secure the infrastructure, not your application logic. Trust boundaries still apply. |
| "Our API is internal, no one can reach it" | Internal APIs are reachable from compromised clients, insider threats, and supply chain attacks. |
| "We'll threat-model when it's built" | Threat modeling finds design flaws. By the time it's built, fixing them requires rewriting, not patching. |
| "We already have a firewall" | A firewall is a network boundary, not an application security boundary. STRIDE covers different threats. |
| "This is just CRUD, nothing novel to model" | CRUD touches data stores and authentication — both have STRIDE threats worth surfacing. |

## Red Flags

- No identified trust boundaries in the architecture
- Authentication or authorization handled client-side
- User-supplied URLs fetched server-side without validation (SSRF)
- No audit logging on sensitive operations (data deletion, privilege changes)
- Data flows to or from unencrypted endpoints
- External API keys or secrets hardcoded in code or config
- "We'll fix it later" attitude toward identified threats

## Verification

- [ ] Data flow diagram drawn with trust boundaries marked (||)
- [ ] STRIDE walked over each trust boundary crossing
- [ ] High and Medium risks have concrete mitigations
- [ ] Security stories written for all High and Medium risks
- [ ] Low risks documented as accepted residual risks with rationale
- [ ] Mitigations prefer existing stack components over new introductions
- [ ] Threat model shared with the team for review
- [ ] Threat model saved and dated for future reference