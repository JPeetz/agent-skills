---
name: gdpr-dsgvo-expert
description: "Use this skill when handling GDPR/DSGVO compliance: scanning codebases for privacy risks, generating DPIAs, or tracking data subject requests under Art. 12(3)."
author: Alireza Rezvani (alirezarezvani), Skill Foundry
version: 0.1.0
license: MIT
platforms:
  - linux
  - macos
  - windows
category: compliance-legal
---

# GDPR/DSGVO Expert

## Overview

Tools and guidance for EU General Data Protection Regulation (GDPR) and German Bundesdatenschutzgesetz (BDSG) compliance work.

The three scripts in `scripts/` do mechanical triage: they find personal data in a codebase, assemble the skeleton of a Data Protection Impact Assessment, and keep data subject requests from silently blowing the one-month deadline. They are deliberately deterministic and dependency-free, because the value of a compliance artifact is that it can be re-run and produce the same answer.

What the tools cannot do is make a legal call. Whether a processing operation has a valid legal basis, whether a DPIA's residual risk is acceptable, and whether a request can lawfully be refused are decisions for the Data Protection Officer or qualified counsel. Every report these scripts emit says so; keep that sentence in whatever you forward.

## When to Use

- Auditing a repository or service for personal data handling before a release
- Preparing or refreshing a DPIA for a new processing activity (Art. 35)
- Onboarding a processor or a new data source and needing a risk snapshot
- Tracking DSARs against the Art. 12(3) one-month clock
- Checking German-specific obligations: DPO threshold, § 26 employment data, § 4 video surveillance
- Reviewing whether retention, consent, or logging practice creates exposure

## Tools

All three scripts are Python 3.8+ standard library only. Run them with `python3 scripts/<name>.py --help`.

### GDPR Compliance Checker

`scripts/gdpr_compliance_checker.py` scans a directory tree for personal data patterns and risky code practices.

Detects:

- Personal data patterns — email addresses, phone numbers, IPv4 addresses, IBANs, card-number-shaped strings
- Special category data (Art. 9) — health, biometric, genetic, religious, trade-union, ethnicity, sexual-orientation indicators
- Financial data — IBAN, card numbers, account/sort-code pairs
- Risky code patterns — logging or printing personal data, hardcoded PII in fixtures, indefinite retention markers, collection without a consent reference

Output: a compliance score from 0 to 100, a risk band, per-finding locations with line numbers, and prioritized recommendations each carrying the GDPR article it addresses.

```bash
python3 scripts/gdpr_compliance_checker.py ./src
python3 scripts/gdpr_compliance_checker.py ./src --json > gdpr-report.json
python3 scripts/gdpr_compliance_checker.py ./src --fail-under 70   # CI gate, exits 1
python3 scripts/gdpr_compliance_checker.py ./src --include-tests
```

Default exclusions are `.git`, `node_modules`, `venv`, `.venv`, `dist`, `build`, `__pycache__`, and binary files. Findings are capped per rule (default 5, `--max-per-rule`) so one noisy regex cannot swamp the report — the count still reflects every hit.

### DPIA Generator

`scripts/dpia_generator.py` produces a DPIA document following Art. 35, and performs the threshold assessment that decides whether a DPIA is required at all.

- Automatic DPIA threshold assessment against the Art. 35(3) triggers and the WP248 nine-criteria test
- Risk identification driven by the processing characteristics you declare
- Legal basis and necessity/proportionality sections
- Mitigation recommendations with residual-risk fields left for the DPO to fill

```bash
python3 scripts/dpia_generator.py --template > dpia-spec.json   # starter spec
python3 scripts/dpia_generator.py --spec dpia-spec.json --output DPIA-crm.md
python3 scripts/dpia_generator.py --spec dpia-spec.json --format json
```

Give it a spec rather than flags when the assessment is real: the spec carries purposes, data categories, subject counts, retention, recipients, and transfers, and those fields are what make the risk section specific instead of boilerplate.

### Data Subject Rights Tracker

`scripts/data_subject_rights_tracker.py` manages requests under GDPR Articles 15–22.

- Supported rights: access (Art. 15), rectification (16), erasure (17), restriction (18), portability (20), objection (21), automated decisions (22)
- All carry the one-month deadline of Art. 12(3), with the two-month extension recorded explicitly when invoked
- Deadline tracking, identity-verification state, response template generation, compliance reporting

```bash
python3 scripts/data_subject_rights_tracker.py add --subject C-1042 --right access --received 2026-11-02
python3 scripts/data_subject_rights_tracker.py list --status open
python3 scripts/data_subject_rights_tracker.py due --within 7
python3 scripts/data_subject_rights_tracker.py status --id DSR-0001 --set completed
python3 scripts/data_subject_rights_tracker.py response --id DSR-0001 > reply.md
python3 scripts/data_subject_rights_tracker.py report
```

State lives in a JSON file (`--store`, default `dsr_requests.json` in the working directory). Commit it or store it wherever your records of processing live — it is the accountability evidence for Art. 5(2).

## Workflows

### 1. New Processing Activity Assessment

1. Describe the processing: purpose, data categories, subjects, volume, recipients, retention, transfers.
2. Run the DPIA threshold assessment (`dpia_generator.py --spec ... --format json`) before writing anything. If no trigger fires, record the negative assessment and stop — a documented "no DPIA required" is itself the artifact.
3. If a trigger fires, scan the implementing code with `gdpr_compliance_checker.py` to find where personal data actually lands: logs, fixtures, caches, analytics calls.
4. Identify the legal basis per purpose (Art. 6, plus Art. 9 for special category data). One basis per purpose — "consent or contract or legitimate interests" is not a basis.
5. Run the necessity and proportionality test: is each field needed for the stated purpose, and is retention the shortest defensible period?
6. Draft mitigations for each identified risk, then have the DPO assign residual risk and sign off.
7. File the DPIA with the ROPA entry (Art. 30) so the two records reference each other.

### 2. Data Subject Request Handling

1. Log the request the day it arrives: `add --received <date>`. The clock starts on receipt, not on identification of the right.
2. Verify identity proportionately — enough to be confident, not a dossier. Record the verification method on the request.
3. Scope the search: production stores, backups, logs, analytics, support tickets, processor-held data.
4. Retrieve and assemble; redact third-party data and any data subject to legal privilege or a statutory retention obligation.
5. Decide on any refusal ground (Art. 12(5), Art. 17(3)) and record the reasoning — refusals are reviewable.
6. Deliver in a commonly used machine-readable format for portability (Art. 20), through a verified channel.
7. Close the request with `status --set completed` and keep the record; `report` is the evidence pack for a supervisory authority.

If the deadline is at risk, extend before it expires, not after: `status --id ... --extend --reason "complex request"`. The extension is two further months and must be notified to the subject within the original month.

### 3. German BDSG Compliance Check

On top of GDPR, verify the German additions:

- **DPO threshold (§ 38 BDSG)** — generally required when at least 20 persons are constantly engaged in automated processing of personal data. Count processors, not just employees. The threshold is not a safe harbour: a DPO may still be required under Art. 37(1) for core activities.
- **Employment data (§ 26 BDSG)** — processing for the employment relationship needs necessity for hiring, performance, or termination, or a works-council agreement. Monitor proportionality, not just consent (employee consent is rarely freely given).
- **Video surveillance (§ 4 BDSG)** — public-space surveillance needs necessity for public or private-space protection, and must be signposted. Covert surveillance requires a documented criminal-offence suspicion.
- **Scoring and credit data (§§ 28a, 31 BDSG)** — probability-value scoring has specific disclosure duties.
- **Supervisory authority** — identify the competent Land authority (Bavaria: BayLDA, Berlin: BlnBDI, and so on); a breach notification goes to the lead authority, not "the EU".

## Key GDPR Concepts

### Legal Bases (Art. 6)

| Basis | When it applies | Notes |
|-------|-----------------|-------|
| Consent (6(1)(a)) | Freely given, specific, informed, unambiguous | Withdrawable at any time; must be as easy to withdraw as to give |
| Contract (6(1)(b)) | Necessary to perform a contract with the subject | Does not cover profiling for marketing |
| Legal obligation (6(1)(c)) | Required by EU or member-state law | Cite the specific statute |
| Vital interests (6(1)(d)) | Life-or-death situations | Narrow; not for routine processing |
| Public task (6(1)(e)) | Public authority exercise of official authority | Public bodies only |
| Legitimate interests (6(1)(f)) | Balanced against the subject's rights | Requires a documented LIA; not available to public authorities |

### Special Category Data (Art. 9)

Racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, biometric data for unique identification, health data, sex life or sexual orientation.

Processing requires an explicit Art. 9(2) exception — explicit consent, employment/social-security law, vital interests, a foundation's legitimate activities, data made public by the subject, legal claims, substantial public interest, public health, archiving/research, or a member-state law with safeguards. Art. 6 alone is never sufficient.

### Data Subject Rights

| Right | Article | Deadline |
|-------|---------|----------|
| Information | 13–14 | At collection |
| Access | 15 | One month |
| Rectification | 16 | One month |
| Erasure | 17 | One month |
| Restriction | 18 | One month |
| Notification of recipients | 19 | Part of the above |
| Portability | 20 | One month |
| Objection | 21 | One month; absolute for direct marketing |
| Automated decisions | 22 | One month |

One month under Art. 12(3), extendable by two months for complex or numerous requests with notice inside the first month. Extensions do not stack.

### German BDSG Additions

| Topic | Provision | Point |
|-------|-----------|-------|
| DPO threshold | § 38 | 20+ persons constantly engaged in automated processing |
| Employment data | § 26 | Necessity for the employment relationship or works-council agreement |
| Video surveillance | § 4 | Necessity plus signposting; covert only on documented suspicion |
| Scoring | § 28a | Disclosure duties for probability values |
| Consumer credit | § 31 | Credit-scoring data restrictions |
| Supervisory authority | — | Competent Land authority, not a single EU body |

## Compliance Score Interpretation

The checker's 0–100 score is a triage signal, not a compliance certificate.

| Band | Score | Meaning |
|------|-------|---------|
| Low risk | 85–100 | No structural issues found; still verify legal bases by hand |
| Moderate | 65–84 | Real findings, mostly fixable: logging of PII, missing retention markers |
| High | 40–64 | Systemic problems: special category data without safeguards, hardcoded PII |
| Critical | 0–39 | Likely unlawful processing; escalate before shipping |

A high score on a codebase that collects nothing sensitive only means the scanner had little to find. Absence of evidence is not evidence of absence — the scanner sees code, not your contracts, your processors, or your actual data flows.

## Pitfalls

| Pitfall | Why it bites | What to do instead |
|---------|--------------|--------------------|
| Treating consent as a catch-all basis | Consent is fragile: withdrawable, and invalid where there is a power imbalance (employment, public services) | Pick the basis that fits the processing; keep consent for genuinely optional things |
| Mixing Art. 6 and Art. 9 analyses | Special category data needs its own Art. 9(2) condition — a valid Art. 6 basis is not enough | Document both layers, separately, per purpose |
| One basis for many purposes | Bundling purposes into one consent or one contract defeats purpose limitation | One basis per purpose; split consent requests |
| Running the clock from the wrong date | Art. 12(3) starts on receipt, including weekends and holidays — not when the request is triaged | Log `--received` on day zero; the tracker computes from there |
| "Extending" after the deadline | An extension notified late is not an extension | Extend inside the first month, in writing |
| Assuming erasure beats retention duties | Art. 17(3) obligations (tax, employment, statutory retention) survive the request | Check retention obligations; document the refusal ground |
| Scanning only application code | PII hides in fixtures, test data, seed files, notebooks, and CI configs | Scan the repo, then the infrastructure and the analytics calls |
| Treating the DPIA as a one-off | Art. 35(11) requires review when risk changes | Re-run the assessment on material changes; version the document |
| Believing anonymisation is a checkbox | Pseudonymised data is still personal data; naive anonymisation re-identifies | Keep pseudonymised data in scope; verify anonymisation claims |
| Ignoring processors | Controller liability survives outsourcing | DPAs (Art. 28) for every processor; check sub-processor chains |
| Notifying the wrong authority | There is no single "EU DPA" | Notify the lead supervisory authority under the one-stop-shop, or the competent Land authority |
| Shipping the scanner's score as proof | A green score means "nothing matched the rules" | Pair the score with a human review of legal basis and retention |

Additional traps worth naming: logging full request bodies (they contain everything), retaining "just in case" indefinitely with no schedule, cookie banners with unequal accept/reject prominence, and transferring data to a third country on the strength of an adequacy decision that has since been invalidated.

## References

- `references/gdpr_compliance_guide.md` — article-by-article reference: principles, bases, rights, DPIA, breach notification, transfers, BDSG, penalties
- `scripts/gdpr_compliance_checker.py` — codebase scanner
- `scripts/dpia_generator.py` — DPIA threshold assessment and document generation
- `scripts/data_subject_rights_tracker.py` — DSAR deadline tracking
- `evals/evals.json` — evaluation scenarios

## Verification Checklist

Before calling GDPR work done:

- [ ] Every purpose has exactly one documented legal basis
- [ ] Special category data has an Art. 9(2) condition, not just Art. 6
- [ ] Retention period is stated in days/months/years, never "indefinite" or "as needed"
- [ ] Codebase scan run, findings triaged, and false positives recorded as such
- [ ] DPIA completed or a documented negative threshold assessment filed
- [ ] Every open DSAR has a computed deadline inside the tracker
- [ ] Processor agreements exist for every third party that touches the data
- [ ] Cross-border transfers have a current mechanism (adequacy decision, SCCs, BCRs)
- [ ] Breach notification path names the actual lead or Land authority
- [ ] DPO has reviewed and signed the residual risk assessment

This skill provides engineering triage and reference material, not legal advice. Final compliance determinations belong to the Data Protection Officer or qualified counsel.
