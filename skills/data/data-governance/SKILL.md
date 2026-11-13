---
name: data-governance
description: "Use this skill when establishing or auditing data governance practices — data cataloging and discovery, data lineage tracking, data quality frameworks, metadata management, data classification and tagging, ownership and stewardship models, data retention policies, and compliance mapping (GDPR, CCPA, SOC 2 data controls). Covers tools like Atlan, DataHub, Amundsen, dbt, Great Expectations, and Soda."
license: MIT
domain: Data/Governance
version: 1.0.0
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
---

# Data Governance — Agent Skill

Operating manual for making data **findable, trustworthy, owned, and lawfully retained**. Three legs: people (ownership), process (review, retention, incident), technology (catalog, lineage, quality tests). Output is artifacts you can ship — dbt `meta` blocks, DataHub recipes, Great Expectations suites, Soda checks, RACI matrices, control crosswalks.

## When to Use This Skill

### ✅ DO trigger when

- **Stand up governance** — "We have 400 tables and no governance; where do we start?"
- **Catalog rollout** — "Deploy DataHub and ingest dbt + Snowflake metadata"
- **Business glossary** — "Define canonical terms for 'active customer' and 'MRR'"
- **Lineage / impact analysis** — "What breaks if I rename `dim_customers.email`?"
- **Root-cause a bad dashboard** — "Revenue is wrong in the exec dashboard; trace it upstream"
- **Data quality framework** — "Add completeness/freshness/uniqueness tests to our marts"
- **Classification** — "Tag every PII column and enforce masking on it"
- **Ownership model** — "Build a RACI for our domain data products"
- **Retention** — "How long can we keep raw clickstream events?"
- **Compliance mapping** — "Which controls satisfy GDPR Art. 30 and SOC 2 CC6?"
- **Governance audit** — "Score our catalog coverage and stale-owner risk"

### ❌ DO NOT trigger for

- Transformation logic with no governance angle → `dbt-data-transformation`
- Dashboards / ad-hoc analysis → `data-analysis`
- Physical schema design → `database-schema-designer`
- Application authn/authz → security skills

---

## 1. Framework Setup: People → Process → Technology

Governance fails when it starts with a tool. Start with **decisions that need an owner**, then codify them.

**Phase 0 — Baseline (1–2 weeks).** Inventory before prescribing: which systems hold regulated data (warehouse, SaaS, buckets, spreadsheets, vendor exports); who already answers "what is this number?" (they become stewards); what is already broken; what is legally required (DPAs, SOC 2 scope, controller vs processor). Deliverable: one-page current-state memo + top-10 risk list.

**Phase 1 — Decisions (3–4 weeks).** Minimum viable policy, ~6 pages: (1) scope — name the systems, "all data" is unenforceable; (2) roles per §6; (3) 4-tier classification per §5; (4) quality SLOs per tier; (5) retention schedule per domain; (6) exception process with **mandatory expiry** on every deviation.

**Phase 2 — Instrumentation (6–10 weeks).** Wire metadata into tools people already use, in this order: dbt `meta` (owner, domain, tier, classification, retention) → catalog ingestion from warehouse/BI/dbt → automated checks on tier-1 only → lineage capture (automatic, manual edges as exception) → dashboards for coverage, test pass rate, stale owners, open exceptions.

**Phase 3 — Operate.** Governance is a cadence, not a project:

| Cadence | Ritual | Owner | Output |
|---|---|---|---|
| Daily | Triaging quality failures | On-call data engineer | Incident ticket |
| Weekly | New datasets reviewed & classified | Data steward | Approved catalog entries |
| Monthly | Ownership + coverage review | Governance lead | Coverage report |
| Quarterly | Retention purge + access recertification | Platform + Legal | Deletion log, signed review |
| Annual | Policy, DPIA refresh, SOC 2 evidence | Sponsor + Legal | Signed policy vN+1 |

> **Rule:** a control with no owner and no cadence does not exist. Log it as a gap, not as policy.

---

## 2. Data Cataloging

A catalog has three jobs: **find** the data, **understand** it, **know if you may use it**.

### 2.1 Metadata layers

| Layer | Examples | Source of truth |
|---|---|---|
| Technical | schemas, types, row counts, partitions | `information_schema`, dbt `catalog.json` |
| Operational | freshness, test results, query volume, cost | dbt artifacts, query logs, orchestrator |
| Business | glossary terms, owner, domain, SLA | governance repo (Git) |
| Governance | classification, retention, lawful basis, policy | governance repo + catalog tags |

**Keep business and governance metadata in Git**, push to the catalog. Catalogs are UIs; Git is the audit trail — a metadata change should be a pull request.

### 2.2 Ingestion — DataHub example

```yaml
# ingestion/dbt.yml
source:
  type: dbt
  config:
    manifest_path: target/manifest.json
    catalog_path: target/catalog.json
    target_platform: snowflake
    include_column_lineage: true
sink:
  type: datahub-rest
  config: {server: "http://datahub.internal:8080", token: "${DATAHUB_TOKEN}"}
```

```bash
datahub ingest -c ingestion/dbt.yml         # models, tests, column lineage
datahub ingest -c ingestion/snowflake.yml   # tables dbt doesn't build
datahub ingest -c ingestion/looker.yml      # dashboards -> usage lineage
```

**Atlan** pushes via REST (`POST /api/meta/entity/bulk`) or its dbt/warehouse connectors; **Amundsen** uses `databuilder` jobs writing to Neo4j + Elasticsearch. Same pattern everywhere: extract → normalize to a common entity model (dataset, column, dashboard, owner, term) → upsert.

### 2.3 Business glossary as code

- **One term = one definition + one formula + one owner.** A definition without a formula is an opinion.
- Definitions live in YAML, reviewed by PR:

```yaml
# glossary/metrics.yml
- term: active_customer
  definition: A customer with at least one order in the trailing 90 days.
  formula: count(distinct customer_id) where order_ts >= current_date - 90
  owner: finance-analytics
  domain: finance
  tier: 1
  approved_by: cfo-office
  approved_on: 2026-03-04
```

- Link terms to physical columns (`meta.glossary: [mrr]`) so the catalog can show term→column coverage.
- Report **term coverage**: % of tier-1 columns mapped to an approved term. Under 40% means the glossary is aspirational.

Track: % of tier-1 tables with a ≥40-char description, % with owner + domain, % with classification, and median "time to find" from a 3-question quarterly survey. A catalog with 100% ingestion and 20% ownership is a schema browser — **ship ownership first**.

---

## 3. Data Lineage

Lineage answers two questions: **"where did this number come from?"** (root cause) and **"what breaks if I change this?"** (impact).

| Level | Meaning | How to capture |
|---|---|---|
| Table | `fct_orders` reads `stg_orders` | dbt `ref()` graph, SQL parse, query logs |
| Column | `gross_revenue` ← `stg_payments.amount` | dbt column lineage, sqlglot, OpenLineage |
| Job | which run produced the table | orchestrator OpenLineage events |
| Dashboard | which tile uses the column | BI connector |

**Column-level is the only level that makes impact analysis safe.** Table-level lineage flags unaffected dashboards — noise that trains people to ignore lineage.

### 3.1 Impact analysis (before any breaking change)

1. **Locate** the asset; confirm env and schema (prod vs staging names collide).
2. **Expand downstream** 2–3 hops (more for tier-1 columns).
3. **Filter to material consumers** — tier-1 dashboards, ML features, reverse-ETL syncs, customer exports, contract-bound reports.
4. **Identify owners** of those assets; notify with deadline and proposed change.
5. **Prefer a shim**: keep the old column, add the new one, set `meta.deprecation_date`, publish a migration note.
6. **Record the decision in the PR**: "downstream consumers: 4 (2 tier-1); owners notified 2026-03-04; shim until 2026-06-01."
7. **Migrate the classification**: a PII column keeps its `pii`/`masking` metadata under the new name (§5).

```bash
# DataHub: downstream column-level impact
datahub graphql -q '
{ searchAcrossLineage(input:{urn:"urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.marts.fct_orders,PROD)",
   direction: DOWNSTREAM, query:"*", start:0, count:200}) {
   searchResults { entity { urn type } degree } } }'
```

### 3.2 Root cause (a number is reported wrong)

Work downstream from the symptom and upstream from the source; meet in the middle.

1. Confirm on the physical table, not the dashboard.
2. **Check freshness first** — late, partial, or double-loaded partitions cause most "wrong numbers".
3. Compare row counts against the trailing 7-day baseline, per stage.
4. Walk upstream one hop at a time; the first stage where counts diverge is the culprit.
5. Counts match but values differ → diff compiled SQL against the last known-good commit.
6. Look for **silent schema drift**: new enum value, timezone shift, currency change, NULL→0.
7. End with a **test**, not just a fix. Every incident produces a check.

Lineage health: orphan rate (tier-1 tables with no upstream and no `source()`), manual-edge count and age, % of tier-1 columns with resolved column lineage.

---

## 4. Data Quality

Quality without a definition of "good enough" is infinite work: **dimensions → checks → SLOs → response**.

| Dimension | Question | Typical check |
|---|---|---|
| Completeness | Are required values present? | `null_count(col) = 0`, row count vs baseline |
| Uniqueness | Is the grain actually the grain? | `duplicate_count(pk) = 0` |
| Validity | Do values conform? | accepted values, regex, range, referential integrity |
| Accuracy | Does it match reality? | reconciliation vs source system / ledger |
| Timeliness | Is it fresh enough? | `freshness(ts) < 6h`, SLA breach hours |
| Consistency | Do two systems agree? | value diff across source and warehouse |
| Volume | Is the shape plausible? | `row_count` within 0.8–1.2× the 7-day median |

**SLOs by tier** — do not test everything:

| Tier | Freshness | Coverage | On failure |
|---|---|---|---|
| 1 (revenue, regulatory, customer-facing) | < 2h after source | all critical columns | page on-call, block downstream publish |
| 2 (internal decisions) | < 24h | key columns | ticket, next business day |
| 3 (exploratory) | best effort | smoke checks | log only |

### 4.1 dbt-native tests (cheapest layer)

```yaml
models:
  - name: fct_orders
    config:
      meta:
        owner: finance-analytics
        domain: finance
        tier: 1
        classification: confidential
        retention: "7y"
    columns:
      - name: order_id
        data_tests: [unique, not_null]
      - name: customer_email
        meta: {classification: pii, pii_type: email, masking: hash}
        data_tests: [not_null]
      - name: status
        data_tests:
          - accepted_values: {values: [placed, shipped, delivered, cancelled, refunded], config: {severity: warn}}
      - name: customer_id
        data_tests: [{relationships: {to: ref('dim_customers'), field: customer_id, config: {severity: error}}}]
```

Severity discipline: `error` blocks the pipeline, `warn` records and continues. Use `warn` for any **new** expectation for two weeks — otherwise you break production on day one.

### 4.2 Great Expectations (GX 1.x)

```python
import great_expectations as gx
context = gx.get_context()
source = context.data_sources.add_postgres("warehouse", connection_string="${WAREHOUSE_URL}")
batch = source.add_table_asset("fct_orders", "marts").add_batch_definition_whole_table("full").get_batch()
results = batch.validate(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"),
    gx.expectations.ExpectColumnValuesToBeBetween(column="gross_revenue", min_value=0),
)
assert results.success, results.describe()
```

### 4.3 Soda

```yaml
checks for fct_orders:
  - row_count > 0
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - freshness(order_ts) < 6h
  - invalid_percent(status) < 1%:
      valid_values: [placed, shipped, delivered, cancelled, refunded]
```

```bash
soda scan -d warehouse -c configuration.yml checks/fct_orders.yml
```

**Dashboard:** only four charts matter — pass rate by tier (30d), tier-1 freshness breach hours, incidents opened vs closed with time-to-detect/resolve, and tier-1 test coverage %. The rest is vanity.

---

## 5. Data Classification

Four tiers, one exception path. Classification drives masking, access, retention, and incident severity.

| Tier | Label | Examples | Handling |
|---|---|---|---|
| 4 | `restricted` | credentials, full PAN, gov IDs, health records, precise geolocation | encrypted + column-level ACL, no export, no non-prod copies, DLP alerts |
| 3 | `confidential` | PII (email, phone, address), financials, contracts, strategy | masked in non-prod, role-gated, exports logged |
| 2 | `internal` | aggregates, operational metrics, config | default employee access, no external sharing |
| 1 | `public` | marketing metrics, open datasets | unrestricted |

**PII is a property, not a tier** — a column can be `confidential` *and* `pii`:

```yaml
meta:
  classification: confidential
  pii: true
  pii_type: email          # email|phone|name|address|dob|ssn|ip|device_id|financial|health
  lawful_basis: contract   # consent|contract|legal_obligation|vital_interest|public_task|legitimate_interest
  retention: "24m"
  masking: hash            # none|hash|redact|tokenize|null
```

### 5.1 Detect → review → enforce

1. **Detect** — Presidio, GX regex expectations, warehouse tag propagation, or catalog auto-classification. Detection produces a *proposal*.
2. **Review** — a steward confirms; false positives are the norm (a product-catalog `name` is not PII).
3. **Enforce** — the tag must change behaviour: Snowflake masking policy bound to the tag, BigQuery policy tags + column ACL, Databricks Unity Catalog column masks, dbt-generated masking in staging, catalog access-request workflow.

```sql
CREATE MASKING POLICY mask_email AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ANALYST_MASKED','DBT_PROD') THEN SHA2(val, 256)
       ELSE val END;

ALTER TABLE marts.dim_customers MODIFY COLUMN email
  SET TAG governance.pii = 'email', governance.classification = 'confidential';
ALTER TABLE marts.dim_customers MODIFY COLUMN email SET MASKING POLICY mask_email;
```

> A tag that doesn't change behaviour is documentation, not governance. Track **enforcement coverage**: % of `pii` columns with an active masking policy.

**Non-prod hygiene** — the most common breach vector is a full prod copy in a dev schema. Require: sampling (1%), masking of tier ≥3, zero tier-4 in non-prod, and a check that fails the copy job if unmasked PII is detected.

---

## 6. Ownership and Stewardship (RACI)

| Role | Accountability | Commitment |
|---|---|---|
| Executive sponsor | Funds program, resolves cross-domain disputes, signs policy | 2h/month |
| Governance lead | Runs cadence, owns policy + catalog roadmap | 0.5–1 FTE |
| Domain owner (A) | Definitions, SLOs, access decisions for a domain | 2–4h/month |
| Data steward (R) | Classifies, documents, triages quality issues | 4–8h/week |
| Data engineer (R) | Tests, lineage hooks, masking | part of normal work |
| Platform team | Catalog, quality tooling, access platform | capacity plan |
| Legal / privacy (C) | DPIA, retention schedule, DSR, breach notification | as needed |
| Security (C) | Access recertification, DLP, incident response | quarterly |

R = responsible, A = accountable (exactly one per row), C = consulted, I = informed.

| Activity | Sponsor | Gov lead | Domain owner | Steward | Eng | Legal | Security |
|---|---|---|---|---|---|---|---|
| Approve policy | A | R | C | I | I | C | C |
| Define business term | I | C | A | R | C | I | I |
| Classify a dataset | I | C | A | R | C | C | I |
| Approve access to tier 3/4 | I | I | A | R | I | C | C |
| Set quality SLO | I | C | A | R | R | I | I |
| Fix a quality incident | I | I | A | C | R | I | I |
| Retention schedule | I | R | C | C | I | A | C |
| Execute deletion | I | C | C | I | R | A | I |
| DSR fulfilment | I | C | C | R | R | A | C |
| Access recertification | I | R | A | C | I | C | C |
| Catalog coverage | I | A | R | R | C | I | I |
| Breach notification | A | C | C | I | C | R | R |

**One `A` per row. If two people are accountable, nobody is.** Keep the registry machine-readable and validate it in CI:

```yaml
# governance/owners.yml
domains:
  finance:
    owner: finance-analytics      # team handle, not a person
    accountable: cfo-office
    steward: maria.k
    tier1_datasets: [fct_orders, fct_subscriptions, dim_customers]
    sla_response_hours: 4
```

Validate: every tier-1 dataset has a registered owner, every owner a steward, and no owner holds more than ~15 tier-1 datasets (beyond that, ownership is fiction). **Stale owner** is the top cause of decayed catalogs — reassign on team changes.

---

## 7. Retention and Lifecycle

Retention is a legal obligation *and* a cost lever. Minimum retention matters as much as maximum: deleting early destroys evidence you must keep.

Lifecycle: `create → active → warm → archive (cold, still queryable) → purge (irreversible)`. Every stage needs storage tier, access path, cost, and an owner. Automate transitions — manual archival never happens.

| Domain | Examples | Retention | Basis | On expiry |
|---|---|---|---|---|
| Transactions | orders, invoices, payments | 7y | tax/accounting law | purge + log |
| Customer PII | profile, contact | account life + 24m | contract / legitimate interest | delete or anonymize |
| Consent records | opt-ins, timestamps | consent life + 5y | proof of consent | purge |
| Web analytics | clickstream | 14m raw, 26m agg | legitimate interest | aggregate, purge raw |
| Application logs | access logs w/ IP | 90d | security | purge |
| Backups | snapshots | 35d rolling | operational | auto-expire |
| ML features | derived | 12m | model risk | purge + retrain |
| Legal hold | litigation data | until release | legal hold | documented release |

**Erasure vs retention conflict:** honour erasure unless a legal obligation requires retention. Resolve per domain *in advance* (pseudonymize PII, keep the financial transaction) — don't litigate it in production at 2am.

Mechanics:

- Partition by date (`ds`) so purges are `DROP PARTITION`, not `DELETE` — cheap and auditable.
- Record each purge in an append-only **deletion log**: dataset, partition range, rows, policy id, approver, timestamp, job id. This is your SOC 2 evidence.
- Test the purge path quarterly on a non-prod copy.
- Document lag: `retention_effective_after = purge + backup_window` — a snapshot still holds purged data.

```sql
-- BigQuery partition purge
DECLARE cutoff DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 14 MONTH);
DELETE FROM `proj.raw.events` WHERE _PARTITIONDATE < cutoff;
```

---

## 8. Compliance Mapping

Map each control to **one artifact** that proves it. Auditors ask for evidence, not intentions.

### GDPR

| Requirement | Artifact | Evidence |
|---|---|---|
| Art. 5 — principles, minimisation | classification + glossary + retention schedule | catalog export of tier-1 fields |
| Art. 6 — lawful basis | `lawful_basis` tag per PII column | tag coverage report |
| Art. 15–17 — access, rectification, erasure | DSR runbook + subject index (subject → tables) | DSR tickets with timestamps |
| Art. 28 — processors | vendor register with DPAs, sub-processors | DPA register |
| Art. 30 — records of processing | processing register generated from catalog | dated register export |
| Art. 32 — security | masking, access control, encryption | enforcement coverage % |
| Art. 33/34 — breach (72h) | incident runbook + lineage to scope records | tabletop record |
| Art. 35 — DPIA | template + trigger list | DPIAs for high-risk processing |
| Art. 44+ — transfers | per-dataset residency tag | residency report |

### CCPA / CPRA

| Requirement | Artifact |
|---|---|
| Notice at collection | classification on collection-point schemas |
| Know / delete / correct / opt-out | DSR runbook; "do not sell/share" flag propagated via lineage |
| Sensitive PI limits | `pii_type` ssn/financial/health/geolocation → `restricted` |
| Service provider contracts | vendor register |
| 12-month lookback | retention schedule retains ≥12m of relevant data |
| Reasonable security | masking + recertification evidence |

### SOC 2 (data-relevant criteria)

| Criterion | Control | Evidence |
|---|---|---|
| CC6.1 — logical access | RBAC, least privilege | access matrix + quarterly review |
| CC6.3 — provisioning | request + approval workflow | ticket samples |
| CC6.6 — boundary protection | no tier-4 in non-prod, egress controls | scan results |
| CC6.7 — transmission / disposal | retention + purge automation | deletion log |
| CC7.2 — monitoring | quality/anomaly alerting | alert config + incident log |
| CC7.3 — incident evaluation | severity matrix tied to classification | 3 closed incidents |
| CC7.4 — incident response | runbook, post-mortems | post-mortem docs |
| P3.1–P3.2 — notice, choice, consent | notice mapped to collection points; consent records | notice + consent sample |
| P4.1–P4.3 — collection, use, retention, disposal | retention schedule + purge evidence | schedule + purge log |
| P8.1 — privacy incidents | breach runbook with notification steps | tabletop record |

**Crosswalk tip:** one matrix of `control_id → clause → artifact path → owner → last verified`. Most controls satisfy several frameworks — write once, reuse. Keep it in the governance repo so audit prep is a `git log`, not a scavenger hunt.

**Evidence hygiene:** dated automated exports beat screenshots; one artifact, one path; retain for the audit window (12 months for SOC 2 Type II).

---

## 9. Automation

`scripts/scan_governance.py` scores dbt governance metadata without touching the warehouse:

```bash
python3 scripts/scan_governance.py target/manifest.json \
  --owners governance/owners.yml --min-score 80
```

Per model it reports missing description, missing/unknown owner, missing or invalid classification, missing retention, PII column without masking, and tier-1 without tests, plus a weighted coverage score. Exits 1 below `--min-score`, so it drops into CI as a ratchet — **never lower the threshold**.

```bash
# dbt: which models changed classification since main?
git diff main -- 'models/**/*.yml' | grep -E '^\+.*classification'

# Snowflake: PII-looking columns needing a masking policy check
SELECT table_catalog, table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE ANY ('%email%','%ssn%','%phone%','%dob%')
  AND table_schema NOT IN ('INFORMATION_SCHEMA');
```

CI gates that hold:

| Gate | Fails when | Blast radius |
|---|---|---|
| Metadata | new model lacks owner/domain/classification | blocks merge |
| Classification | `pii: true` without `masking` | blocks merge |
| Quality | tier-1 pass rate < 99% | blocks deploy |
| Retention | schema has no `retention` | warn 2 sprints, then block |
| Terminology | new column duplicates a glossary term | warn + suggest mapping |

Start as warnings, convert to blocks after two sprints, and ratchet on **changed files only** — gates that fail on legacy debt get disabled within a week.

---

## 10. Anti-Patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Tool-first governance | catalog bought, unused in 6 months | owners + 10 tier-1 datasets first |
| Boil-the-ocean classification | 12 tiers nobody applies | 4 tiers, enforced by tag automation |
| Ownership by committee | team aliases, no individual | one accountable human per domain |
| Testing everything | 4000 failing warn tests, ignored | tier-1 only at `error` |
| Lineage as decoration | column lineage exists, never consulted | impact analysis as a required PR step |
| Retention written, never run | policy PDF, no deletion log | quarterly purge + evidence |
| Policy without exceptions | shadow copies, undocumented extracts | time-boxed exception register |
| Coverage as the only KPI | 100% cataloged, 0% trusted | pair coverage with pass rate |

---

## 11. Starting From Zero — 8 Weeks

**W1** inventory systems; name sponsor + governance lead; pick **10 tier-1 datasets** (revenue, customer, regulatory).
**W2** add `owner`, `domain`, `tier`, `classification`, `retention` to those 10 in dbt `meta`; add `unique`/`not_null`/freshness tests.
**W3** stand up the catalog (single-node DataHub suffices), ingest dbt + warehouse, verify all 10 show owners.
**W4** publish the 6-page policy: scope, roles, 4 tiers, SLO table, retention schedule, exception process.
**W5–6** add the metadata CI gate for changed files; route failure alerts to a channel with a named owner.
**W7–8** first quarterly ritual: coverage review, access recertification, purge rehearsal, control matrix v1.

Then expand **by domain**, never by "all tables".

---

## References

- `references/sources.md` — DAMA-DMBOK, DataHub/Atlan/Amundsen, GX, Soda, GDPR/CCPA/SOC 2 primary texts
- `scripts/scan_governance.py` — CI-ready metadata coverage scanner
- `evals/evals.json` — trigger and behaviour evaluation cases
