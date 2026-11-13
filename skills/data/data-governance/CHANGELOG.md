# Changelog

All notable changes to the `data-governance` agent skill.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-13

### Initial Release

A single, progressively-disclosed skill for standing up or auditing a data governance program, independent of vendor stack.

### What's Included

- **Framework setup** — phased rollout (baseline → decisions → instrumentation → operate), minimum-viable policy outline, cadence table (daily/weekly/monthly/quarterly/annual)
- **Data cataloging** — four metadata layers, DataHub ingestion recipes (dbt/Snowflake/Looker), Atlan and Amundsen patterns, glossary-as-code with approval fields, discovery KPIs
- **Data lineage** — table/column/job/dashboard levels, column-level impact-analysis workflow with notification and deprecation shims, seven-step root-cause procedure, lineage quality metrics
- **Data quality** — seven dimensions, tier-based SLOs, Great Expectations 1.x and Soda check examples, dbt `data_tests` with severity discipline, four-chart quality dashboard
- **Data classification** — four-tier model, PII modeled as a property (not a tier), detect→review→enforce pipeline, Snowflake masking policy example, non-production hygiene rules
- **Ownership** — nine roles, 12-row RACI matrix (one accountable per row), machine-readable owners registry with CI validation rules
- **Retention** — five-stage lifecycle, ten-domain retention schedule template, partition-drop purge mechanics, append-only deletion log as audit evidence
- **Compliance mapping** — GDPR Art. 5–35 and 44+, CCPA/CPRA obligations, SOC 2 CC6/CC7/P-series criteria, each mapped to an artifact and the evidence to produce
- **Automation** — `scripts/scan_governance.py` (CI-ready metadata coverage scanner with PyYAML-optional parsing), useful shell one-liners, five CI gates with ratchet guidance
- **Anti-patterns** — eight failure modes with symptoms and fixes
- **Quick reference** — 8-week from-zero rollout plan

### Evaluation Coverage

- 3 scenarios in `evals/evals.json`: framework/ownership design, column-level lineage impact analysis, and GDPR/SOC 2 control mapping
