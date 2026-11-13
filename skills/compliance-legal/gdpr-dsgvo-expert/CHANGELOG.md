# Changelog

## [0.1.0] - 2026-11-13

### Added
- Initial release: gdpr-dsgvo-expert skill for GDPR (EU) and BDSG (Germany) compliance work
- `scripts/gdpr_compliance_checker.py` — stdlib scanner for personal data patterns (email, phone, IP, IBAN, card numbers), Art. 9 special category indicators, and risky code practices (PII logging, hardcoded fixtures, indefinite retention), with a 0–100 score, risk banding, line-level findings, and article-referenced recommendations
- `scripts/dpia_generator.py` — Art. 35 threshold assessment against the Art. 35(3) triggers and the WP248 nine-criteria test, plus DPIA document generation in markdown or JSON
- `scripts/data_subject_rights_tracker.py` — DSAR tracking for Art. 15–22 with Art. 12(3) one-month deadlines, two-month extension handling, identity-verification state, response template generation, and compliance reporting
- Three workflows: new processing activity assessment, data subject request handling, German BDSG compliance check
- `references/gdpr_compliance_guide.md` — article-by-article reference covering principles, legal bases, special category data, data subject rights, DPIA, breach notification, international transfers, BDSG additions, and penalties
- `## Pitfalls` section covering consent misuse, Art. 6/9 conflation, deadline miscalculation, retention-vs-erasure conflicts, and scanner-score overconfidence
- `evals/evals.json` with evaluation scenarios for each tool and the DPO escalation boundary
