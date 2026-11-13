# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-13

### Added

- Initial release: `open-source-license-compliance` skill for inventorying,
  evaluating, and enforcing open source license obligations.
- License taxonomy across four classes — permissive, weak copyleft, strong
  copyleft, and proprietary/source-available — with the specific obligations
  each imposes (attribution, `NOTICE` propagation, file-level source release,
  relinking rights, network-use source offer).
- SPDX identifier guidance: canonical identifiers over deprecated bare forms,
  `OR` / `AND` / `WITH` expression semantics, `LicenseRef-*` for non-standard
  terms, and `UNKNOWN` vs `NOASSERTION` as distinct classifications.
- Inbound compatibility matrix covering MIT, BSD, Apache-2.0, MPL-2.0, LGPL,
  GPL-2.0-only, GPL-3.0-only, AGPL-3.0, and proprietary code across common
  outbound licenses — including the Apache-2.0 → GPL-2.0-only patent-clause
  incompatibility and the MPL-2.0 §3.3 secondary-license route into the GPL
  family.
- Linking-boundary section: dynamic, static, subprocess/IPC, header-only, and
  runtime plugin cases, with the instruction to record the boundary decision
  in writing at the time it is made.
- Transitive scan recipe in four stages: manifest-level fast pass per ecosystem,
  file-level ScanCode Toolkit pass, licensee identification for ambiguous or
  modified license texts, and ORT orchestration with curations, policy rules,
  and NOTICE/SBOM reporters.
- Unknown and missing license handling: default to all rights reserved under
  default copyright, exhaustive search procedure, written maintainer escalation,
  and documented accepted-risk path with an owner.
- Attribution output: `NOTICE` aggregation for Apache-2.0 §4(d), generated
  third-party notices with full license texts, deduplication rules, shipping
  locations per artifact form, and SPDX/CycloneDX SBOM output.
- Redistribution rules: distribution triggers, valid source offers, scope of
  corresponding source, prohibition on added restrictions, change marking, and
  versioning of notice obligations — explicitly framed as engineering guidance.
- CI policy gate: allow/review/deny policy file, enforcement command, lockfile
  evaluation, fail-closed handling of unknown licenses, base-branch baselining,
  and waivers that require an owner and an expiry date.
- AI-generated and agent-vendored code provenance: per-block JSON provenance
  record, generated-code license scanning, prompt hashing, mandatory human
  review, and the warning against asserting a license over material that may
  not be copyrightable.
- `references/sources.md` — primary sources: SPDX license list, REUSE
  specification, licensee, ScanCode Toolkit, OSS Review Toolkit,
  choosealicense.com.
- `Pitfalls` table covering 13 recurring failure modes, and a 14-item
  verification checklist.
- `evals/evals.json` with three scenarios: dependency audit, NOTICE
  generation, and CI policy violation.
