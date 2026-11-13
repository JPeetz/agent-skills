# GDPR / DSGVO Compliance Guide

Article-by-article reference for engineers and DPOs working through GDPR and BDSG obligations. Everything here is a summary of the regulation, not a substitute for the text of Regulation (EU) 2016/679 or the BDSG itself, and not legal advice.

- [1. Scope and Applicability](#1-scope-and-applicability)
- [2. Principles (Art. 5)](#2-principles-art-5)
- [3. Legal Bases (Art. 6)](#3-legal-bases-art-6)
- [4. Special Category Data (Art. 9)](#4-special-category-data-art-9)
- [5. Transparency and Consent (Art. 7, 12-14)](#5-transparency-and-consent-art-7-12-14)
- [6. Data Subject Rights (Art. 15-22)](#6-data-subject-rights-art-15-22)
- [7. Controller and Processor (Art. 24-28)](#7-controller-and-processor-art-24-28)
- [8. Records of Processing (Art. 30)](#8-records-of-processing-art-30)
- [9. Security of Processing (Art. 32)](#9-security-of-processing-art-32)
- [10. Data Protection Impact Assessment (Art. 35)](#10-data-protection-impact-assessment-art-35)
- [11. Breach Notification (Art. 33-34)](#11-breach-notification-art-33-34)
- [12. International Transfers (Art. 44-49)](#12-international-transfers-art-44-49)
- [13. German BDSG Additions](#13-german-bdsg-additions)
- [14. Penalties](#14-penalties)
- [15. Engineering Checklist](#15-engineering-checklist)

## 1. Scope and Applicability

GDPR applies when a controller or processor processes personal data and any of these hold:

1. The processing happens in the context of the activities of an establishment in the EU, regardless of where the processing itself takes place (Art. 3(1)).
2. The controller or processor is not established in the EU but offers goods or services to data subjects in the EU (Art. 3(2)(a)).
3. The controller or processor is not established in the EU but monitors the behaviour of data subjects in the EU (Art. 3(2)(b)).

Personal data is any information relating to an identified or identifiable natural person (Art. 4(1)). Identifiability is relative to means reasonably likely to be used — pseudonymised data remains personal data. Online identifiers (IP address, cookie ID, device fingerprint) are explicitly personal data (recital 30).

Territorial scope is not a get-out: a US company with EU users and EU-facing analytics is in scope.

## 2. Principles (Art. 5)

| Principle | Article | Engineering implication |
|---|---|---|
| Lawfulness, fairness, transparency | 5(1)(a) | Every field has a documented basis and a notice at collection |
| Purpose limitation | 5(1)(b) | Purposes declared at collection; new purposes need a compatibility assessment (Art. 6(4)) |
| Data minimisation | 5(1)(c) | Remove fields that have no owner and no purpose |
| Accuracy | 5(1)(d) | Provide correction paths; avoid derived fields that drift |
| Storage limitation | 5(1)(e) | Retention per category, enforced by a tested deletion job |
| Integrity and confidentiality | 5(1)(f) | Encryption, access control, audit logging |
| Accountability | 5(2) | ROPA, DPIAs, DPAs, and request logs exist and are current |

Accountability reverses the burden: not "prove we broke it" but "demonstrate we comply". A policy nobody can produce on request is not evidence.

## 3. Legal Bases (Art. 6)

| Basis | Article | Scope | Traps |
|---|---|---|---|
| Consent | 6(1)(a) | Optional processing where the subject genuinely chooses | Withdrawable at will (Art. 7(3)); not freely given in employment or public-service contexts |
| Contract | 6(1)(b) | Processing necessary to perform a contract with the subject, or pre-contract steps at their request | Does not extend to analytics or marketing bolted onto the product |
| Legal obligation | 6(1)(c) | Union or member-state law requires it | Cite the specific provision; "we must keep records" is not a citation |
| Vital interests | 6(1)(d) | Life or death of the subject or another person | Narrow; not a routine healthcare basis |
| Public task | 6(1)(e) | Public authority exercising official authority | Not available to private controllers |
| Legitimate interests | 6(1)(f) | Any lawful interest not overridden by the subject's rights | Requires a documented three-part LIA: interest, necessity, balancing; subject has an absolute right to object to direct marketing |

Rules that follow from practice:

- One basis per purpose. "Consent or legitimate interests" is an admission that neither was analysed.
- A basis cannot be swapped retroactively without a compatibility assessment.
- Public authorities cannot rely on 6(1)(f) for their public tasks.

## 4. Special Category Data (Art. 9)

Special categories: racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, biometric data processed to uniquely identify a person, health data, sex life or sexual orientation.

Processing is prohibited unless one of the Art. 9(2) conditions applies:

| Condition | Article | Note |
|---|---|---|
| Explicit consent | 9(2)(a) | Higher bar than Art. 6 consent: specific, unambiguous, explicit |
| Employment and social security law | 9(2)(b) | Requires a legal basis in Union or member-state law with safeguards |
| Vital interests | 9(2)(c) | Where the subject cannot consent |
| Legitimate activities of a foundation, association, or non-profit | 9(2)(d) | Members or former members only; no disclosure outside |
| Data manifestly made public by the subject | 9(2)(e) | Narrow; a social-media post is not blanket publication |
| Legal claims | 9(2)(f) | Establishing, exercising, or defending claims |
| Substantial public interest | 9(2)(g) | Needs a member-state legal basis |
| Public health | 9(2)(i) | Professional secrecy safeguards |
| Archiving, research, statistics | 9(2)(j) | Requires Art. 89(1) safeguards |

Art. 9 does not replace Art. 6 — a valid basis for both layers is needed. Also watch Art. 10 (criminal convictions) which needs an official-authority basis or member-state law.

## 5. Transparency and Consent (Art. 7, 12-14)

Notice must be concise, transparent, intelligible, and easily accessible, in clear language. Layered notice works: a short just-in-time statement plus a full notice.

Required content (Art. 13 for data collected from the subject, Art. 14 for data from elsewhere):

- Identity and contact details of the controller and DPO
- Purposes and legal basis
- Legitimate interests where that is the basis
- Recipients or categories of recipient
- Transfers and the safeguard relied on
- Retention period or the criteria used to determine it
- The data subject rights
- The right to withdraw consent and to lodge a complaint
- Whether provision is statutory/contractual and the consequences of not providing it
- Existence of automated decision-making, with meaningful information about the logic (Art. 13(2)(f))

Consent (Art. 7) is valid only when freely given, specific, informed, and unambiguous, expressed by a clear affirmative action. Pre-ticked boxes, silence, and inactivity are not consent. Withdrawal must be as easy as giving. Where processing has multiple purposes, each needs separate consent. Consent records must show who, when, for what wording, and for which version.

Cookie and tracker consent follows the ePrivacy regime in addition to GDPR: prior consent, equal prominence for reject, no non-essential cookies before consent, no consent walls for non-essential purposes.

## 6. Data Subject Rights (Art. 15-22)

| Right | Article | What it covers | Practical notes |
|---|---|---|---|
| Information | 13-14 | Notice at or before collection | Must be given at the point of collection for direct collection |
| Access | 15 | Confirmation, copy, purposes, categories, recipients, retention, rights, source, automated decisions | Provide a copy of the data, not a summary of it |
| Rectification | 16 | Correction of inaccurate or incomplete data | Incomplete data includes missing context that makes it misleading |
| Erasure | 17 | Deletion when data is no longer necessary, consent withdrawn, unlawful processing, or legal obligation | Overridden by Art. 17(3): legal obligation, legal claims, public interest, archiving |
| Restriction | 18 | Mark and store only | Used while accuracy is contested, or instead of erasure where retention is required |
| Notification | 19 | Inform recipients of rectification, erasure, restriction | Must name recipients if asked |
| Portability | 20 | Data provided by the subject plus observed data, in a structured machine-readable format | Does not include inferred or derived data; applies only to consent/contract bases and automated processing |
| Objection | 21 | Object to processing under 6(1)(e) or (f) | Absolute for direct marketing; otherwise controller must show compelling grounds |
| Automated decisions | 22 | Not be subject to solely automated decisions with legal or significant effect | Exceptions: contract necessity, legal authorisation, explicit consent; safeguards include human intervention, explanation, contest |

Procedural rules (Art. 12):

- Respond without undue delay and in any event within one month of receipt.
- Extend by two months for complex or numerous requests; notify the subject of the extension and the reasons within the first month.
- No fee for the first copy; a reasonable fee or refusal is available for manifestly unfounded or excessive requests (Art. 12(5)), with reasons.
- Identity may be verified, but not by demanding more data than necessary.
- If the controller does not act, it must inform the subject within one month of the reasons and their right to complain (Art. 12(4)).

The clock runs from receipt. A request that arrives on a Friday and is triaged on Monday has already consumed three days.

## 7. Controller and Processor (Art. 24-28)

The controller determines purposes and means; the processor acts on the controller's documented instructions. A processor that goes beyond instructions becomes a controller for that processing.

Art. 28 requires a written contract with every processor covering: subject matter and duration, nature and purpose, type of personal data and categories of subjects, the controller's obligations and rights, and specifically that the processor:

- processes only on documented instructions, including for transfers
- ensures personnel confidentiality
- implements Art. 32 security
- engages sub-processors only with authorisation and under equivalent terms
- assists with data subject rights and with Art. 32-36 obligations
- deletes or returns data at the end of the service
- provides audit information and allows inspections

Joint controllers (Art. 26) must arrange their responsibilities transparently, and the essence of the arrangement must be available to data subjects.

Practical checks: sub-processor lists, breach notification timelines in the DPA (must let the controller meet 72 hours), data location, deletion certification, and audit rights that are not theoretical.

## 8. Records of Processing (Art. 30)

Controllers must keep a record of processing activities containing:

- name and contact details of the controller, joint controllers, representative, and DPO
- purposes of the processing
- categories of data subjects and of personal data
- categories of recipients, including third countries and the safeguards
- transfers to third countries and the documentation of suitable safeguards
- envisaged retention periods
- a general description of the technical and organisational security measures

The record must be in writing, including electronic form, and made available to the supervisory authority on request. The Art. 30(5) exemption for fewer than 250 employees is narrow: it does not apply where processing is not occasional, is likely to result in risk, or involves special category data.

## 9. Security of Processing (Art. 32)

Appropriate technical and organisational measures, taking into account the state of the art, costs, and the nature, scope, context, and purposes of processing, plus the risks to rights and freedoms. Explicitly named:

- pseudonymisation and encryption
- ongoing confidentiality, integrity, availability, and resilience of systems
- the ability to restore availability and access after an incident
- a process for regularly testing and assessing effectiveness

Accountability here means documenting why the chosen measures are appropriate, not just listing them. A risk assessment that predates the architecture is not a control.

## 10. Data Protection Impact Assessment (Art. 35)

A DPIA is required where a type of processing is likely to result in a high risk to rights and freedoms, in particular when using new technologies and considering the nature, scope, context, and purposes.

Art. 35(3) mandatory cases:

- (a) systematic and extensive evaluation of personal aspects based on automated processing, including profiling, on which decisions producing legal effects or similarly significantly affecting the subject are based
- (b) large-scale processing of Art. 9 special category data or Art. 10 criminal-conviction data
- (c) systematic monitoring of a publicly accessible area on a large scale

The supervisory authorities' criteria list (WP248rev.01, endorsed by the EDPB) names nine factors; two or more generally indicate a DPIA is required: evaluation/scoring, automated decision-making with significant effect, systematic monitoring, sensitive or highly personal data, large-scale processing, matching or combining datasets, vulnerable data subjects, innovative technology, and processing that prevents subjects exercising a right or using a service.

Required content (Art. 35(7)):

1. A systematic description of the processing and purposes, including the legitimate interest where relevant
2. An assessment of necessity and proportionality
3. An assessment of the risks to rights and freedoms
4. The measures envisaged to address the risks, including safeguards and security measures

Additional obligations: seek the DPO's advice (Art. 35(2)), seek the views of data subjects or their representatives where appropriate (Art. 35(9)), and consult the supervisory authority before processing if residual risk remains high (Art. 36). Review when risk changes (Art. 35(11)).

A documented negative assessment — "no trigger fired, here is why" — is a legitimate outcome and should be kept. What is not legitimate is no assessment at all.

## 11. Breach Notification (Art. 33-34)

A personal data breach is a breach of security leading to accidental or unlawful destruction, loss, alteration, unauthorised disclosure of, or access to personal data.

Controller to supervisory authority (Art. 33):

- Notify within 72 hours of becoming aware, unless unlikely to result in a risk.
- Where notification is not within 72 hours, it must be accompanied by reasons for the delay.
- Content: nature of the breach including categories and approximate numbers of subjects and records, DPO contact, likely consequences, and measures taken or proposed.
- Processors must notify the controller without undue delay (Art. 33(2)).
- Document all breaches, including those not notified, with the facts, effects, and remedial action (Art. 33(5)).

Controller to data subjects (Art. 34): without undue delay where the breach is likely to result in a high risk. Communication must be in clear language describing the nature of the breach, the DPO contact, likely consequences, and measures taken. Exceptions: encryption made the data unintelligible, subsequent measures removed the high risk, or individual communication would involve disproportionate effort (then public communication).

The 72-hour clock starts on awareness, not on confirmation of scope. Detect early, notify with what you know, and supplement.

## 12. International Transfers (Art. 44-49)

Transfer mechanisms, in order of preference:

1. **Adequacy decision** (Art. 45) — the Commission has found the third country adequate. Adequacy decisions are periodically reviewed and can be invalidated (Schrems II struck down Privacy Shield).
2. **Appropriate safeguards** (Art. 46) — standard contractual clauses (SCCs), binding corporate rules (BCRs), approved codes of conduct, certification. SCCs require a transfer impact assessment in light of the destination country's law and, where needed, supplementary measures.
3. **Derogations** (Art. 49) — explicit consent, contract necessity, important public interest, legal claims. Occasional and non-repetitive by nature; not a basis for systematic transfers.

Practical requirements: know where data physically and logically resides (including sub-processors and support access from third countries), document the mechanism per transfer, and re-verify after legal changes. Remote access from a third country counts as a transfer.

## 13. German BDSG Additions

The BDSG fills the opening clauses the GDPR leaves to member states.

**Data Protection Officer (§ 38 BDSG).** A DPO is required where at least 20 persons are constantly engaged in automated processing of personal data, or where processing for commercial purposes involves automated processing likely to result in high risk. The count covers everyone who regularly touches automated processing, including contractors performing processing on the controller's behalf. The threshold is not a safe harbour: Art. 37(1) GDPR requires a DPO for core activities involving large-scale regular and systematic monitoring or large-scale special category data, regardless of headcount.

**Employment data (§ 26 BDSG).** Personal data of employees may be processed for the purposes of the employment relationship where necessary for hiring decisions, carrying out or terminating the relationship, or exercising or fulfilling rights and obligations arising from law, a collective agreement, or a works agreement. Employee consent is available in principle but rarely freely given — rely on necessity or a works agreement instead. § 26(2) covers special category data; § 26(3) covers sensitive data for the purposes of § 26(1). Co-determination rights of the works council apply to monitoring technology.

**Video surveillance (§ 4 BDSG).** Processing of video surveillance data of publicly accessible spaces is lawful only where necessary for public safety, for the protection of life, health, or property, or for the protection of a legitimate interest where no overriding interest of the data subject prevails. The processing must be signposted (Art. 13 GDPR notice plus visible signage). Covert surveillance and covert observation of non-public spaces require a documented suspicion of a criminal offence and are otherwise prohibited.

**Scoring and credit data (§§ 28a, 31 BDSG).** Probability-value scoring is permitted only under specified conditions, with disclosure duties toward the data subject, and consumer-credit scoring is limited to defined data categories.

**Supervisory authorities.** Germany has a Land authority per state rather than a single national DPA: BayLDA (Bavaria), BlnBDI (Berlin), LfDI Baden-Württemberg, HBDI (Hesse), and so on. The lead authority under the one-stop-shop is determined by the main establishment; a company without an EU establishment deals with the authority where its EU representative sits.

**Other BDSG specifics worth knowing:** § 22 restricts processing for purposes unrelated to the original one; § 35 restricts processing for non-public bodies; § 32 covers restrictions on the rights of data subjects (for example in archiving contexts); § 40 covers processing for employment-related research.

## 14. Penalties

Administrative fines (Art. 83):

| Tier | Article | Maximum |
|---|---|---|
| Basic obligations (controller/processor duties, certification, monitoring bodies) | 83(4) | €10 million or 2% of total worldwide annual turnover, whichever is higher |
| Principles, legal bases, data subject rights, transfers | 83(5) | €20 million or 4% of total worldwide annual turnover, whichever is higher |
| Failure to comply with a supervisory authority order | 83(6) | Same as the relevant tier |

Other consequences: processing bans, ordered deletion, compensation claims under Art. 82 (material and non-material damage), and reputational cost. Fines are assessed against factors including the nature, gravity, and duration of the infringement, intentional or negligent character, mitigation actions, and prior infringements.

## 15. Engineering Checklist

Design time:

- [ ] Data inventory: every field, every store, every owner
- [ ] Purpose and legal basis per purpose, written down before coding
- [ ] Data minimisation review: can any field be removed or coarsened?
- [ ] Retention period per category, with the deletion job designed alongside the schema
- [ ] DPIA threshold assessment run; DPIA or documented negative result filed
- [ ] Processor DPAs in place, including sub-processor chain
- [ ] Transfer mechanism verified for each location, including support access
- [ ] Notice drafted at the collection point, not only in a legal page

Operational:

- [ ] Access reviews on a schedule, with evidence
- [ ] PII redacted in logs and traces by default; verify with a log sample
- [ ] Deletion job tested end to end, including backups
- [ ] DSAR process documented, with the tracker populated and deadlines visible
- [ ] Breach playbook naming the actual lead or Land authority, with a 72-hour timeline rehearsal
- [ ] Vendor reviews on renewal, not only at onboarding

Evidence:

- [ ] ROPA current and matching the systems actually running
- [ ] DPIA versioned, reviewed on change
- [ ] DSAR records showing deadlines met
- [ ] Consent records with wording, timestamp, and version
- [ ] Security measure rationale, not just a control list

Run `scripts/gdpr_compliance_checker.py` for the code-level view, `scripts/dpia_generator.py` for the assessment artifact, and `scripts/data_subject_rights_tracker.py` for the request clock. None of them decides legal questions — that is the DPO's call, and the artifacts exist so that call is informed.
