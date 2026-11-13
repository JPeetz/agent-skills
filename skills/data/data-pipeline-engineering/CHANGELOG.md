# Changelog

All notable changes to the data-pipeline-engineering agent skill.

## [1.0.0] — 2026-11-13

### Initial Release

Skill for designing, building, and debugging batch and streaming data
pipelines, with emphasis on the failure modes that actually cause production incidents
rather than tool syntax.

### What's Included

- **Core mental model** — a pipeline as a function of (source snapshot, partition, run
  timestamp), and the four properties that follow from it: idempotent, partition-scoped,
  observable, reversible.
- **Architecture guidance** — ETL vs ELT decision table, batch vs micro-batch vs streaming
  decision table with the operational-cost caveat, and raw/staging/mart/monitoring layering.
- **Orchestration comparison** — Airflow vs Dagster vs Prefect on primitive, strengths,
  weaknesses, and backfill UX, with working example DAG/asset/flow snippets and the
  serialization and logical-date pitfalls called out.
- **Idempotency** — three strategies (partition overwrite, MERGE on business key, append +
  dedupe view), half-open watermark windows, late/duplicate handling, full MERGE SQL, and
  delete-handling options.
- **Schema drift** — fingerprinting, a drift classification table with severity and
  required action, catalog-based detection per warehouse, and the
  "tolerant on read, strict on write" rule.
- **Data quality** — boundary-based checks (extract / transform / publish), minimum viable
  check set with blocking-vs-warning guidance, and a combined SQL check query.
- **Observability** — the four per-run signals (freshness, volume, latency, status +
  schema), cost tracking, and an alert-design section (symptom-based, deduplicated,
  numbered, tiered) including scheduler watchdogs.
- **Backfill and replay** — six-step procedure, idempotency proof before backfill,
  throttling, atomic swap isolation, downstream cascade, and run-type tagging.
- **Warehouse-specific patterns** — BigQuery partitioning/clustering/partition-filter
  enforcement, Snowflake clustering keys and warehouse separation, Redshift dist/sort keys
  and VACUUM, plus cross-warehouse rules for semi-structured data, timezones, and units.
- **Anti-pattern table** — ten common mistakes mapped to symptom and fix.
- **Build checklist** and a **failing-run debugging order of operations**.

### Artifacts

- `SKILL.md` — Cross-platform skill definition
- `LICENSE` — MIT
- `CHANGELOG.md` — This file
- `evals/evals.json` — 3 evaluation scenarios (design, debug, operations)
- `references/sources.md` — Authoritative upstream documentation
- `scripts/pipeline_lint.py` — Static lint for a pipeline spec: idempotency declaration,
  partition scoping, non-deterministic partition bounds, watermark/lookback, cost
  guardrails, quality-check completeness, backfill bounds. Stdlib only, JSON output,
  exit 1 on errors.
- `scripts/data_freshness_check.py` — Freshness lag vs SLA, missing-partition gaps (only
  for windows already closed, so the in-progress period is never a false positive), and
  row-count anomalies vs trailing median. Stdlib only, exit 2 on failure.

### Design Notes

- Scope deliberately excludes dbt model authoring and OLTP schema design; those route to
  `dbt-data-transformation` and `database-schema-designer` respectively.
- Scripts avoid `yaml` and every third-party dependency so they can run in a bare CI
  container or an agent sandbox without an install step.
