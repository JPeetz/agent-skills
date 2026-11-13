---
name: data-pipeline-engineering
description: "Use this skill when designing, building, or debugging data pipelines — ETL/ELT workflows, data orchestration (Airflow/Dagster/Prefect), streaming (Kafka/Spark Streaming), schema drift handling, pipeline observability, backfill strategies, and data warehouse integration (BigQuery/Snowflake/Redshift). Covers batch and real-time patterns, idempotency, partitioning, incremental loads, and monitoring."
license: MIT
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
domain: Data/Data Engineering
version: 1.0.0
---

# Data Pipeline Engineering — Agent Skill

Design, build, operate, and debug production data pipelines. This skill covers the decisions that actually break pipelines in production: idempotency, late and duplicate data, schema drift, incremental state, backfills, and whether anyone notices when the numbers are wrong.

## When to Use This Skill

### ✅ DO trigger when:

- **Design a pipeline** — "Build an ELT pipeline from Postgres to BigQuery that runs hourly"
- **Choose an orchestrator** — "Should we use Airflow, Dagster, or Prefect for this?"
- **Incremental loads** — "Make this load incremental instead of a full refresh"
- **Idempotency** — "This job double-counts revenue when it reruns — fix it"
- **Schema drift** — "The upstream API added a field and our loader crashed"
- **Streaming** — "Set up Kafka → Spark Structured Streaming with exactly-once semantics"
- **Backfill** — "I need to reprocess 18 months of history without taking the pipeline down"
- **Pipeline observability** — "Alert me when the table stops updating"
- **Warehouse tuning** — "This BigQuery query scans 40 TB; how do we partition it?"
- **Debug a failed run** — "The DAG fails at 3am with a lock timeout on the merge"
- **Cost control** — "Our warehouse bill tripled after we added the hourly schedule"

### ❌ DO NOT trigger for:

- **Pure SQL analytics / ad-hoc queries** → use a data-analysis skill
- **dbt model authoring, tests, semantic layer** → use `dbt-data-transformation`
- **Table/index design on an OLTP database** → use `database-schema-designer`
- **Notebook-based EDA** → use `exploratory-data-analysis`
- **Application-side event tracking design** → use an analytics-instrumentation skill

## Core Mental Model

A pipeline is a **function of (source snapshot, partition, run timestamp) → target state**. Everything below follows from making that function:

1. **Idempotent** — same input, same run twice, same output.
2. **Partition-scoped** — a run touches exactly the window it owns, never "whatever is new".
3. **Observable** — freshness, volume, and schema are checked at every boundary.
4. **Reversible** — any partition can be replayed from source without manual surgery.

If a design cannot satisfy those four, it will page someone at 3am eventually.

## 1. Architecture: ETL vs ELT, Batch vs Streaming

### ETL vs ELT

| | ETL | ELT |
|---|---|---|
| Transform happens | Before load, in a separate engine | After load, inside the warehouse |
| Best for | Regulated PII scrubbing, legacy targets, non-SQL targets | Cloud warehouses, analytics engineering, fast iteration |
| Cost driver | Compute cluster | Warehouse storage + scan volume |
| Failure mode | Transform bug = reload everything | Transform bug = rerun one model |
| Default in 2026 | Only when compliance forces it | **Yes** — land raw, transform in-warehouse |

**Rule:** land raw data as immutable as possible (append-only, source-shaped, no type coercion beyond what the loader needs). All business logic belongs downstream where it can be re-run cheaply. The raw layer is your replay source of truth.

### Batch vs streaming decision table

| Requirement | Choose |
|---|---|
| Consumers tolerate 15 min – 24 h latency | Batch (hourly/daily). Cheapest, simplest, easiest to backfill. |
| 1–15 min latency, complex joins to warehouse tables | Micro-batch (Spark Structured Streaming `trigger(availableNow=True)`, or 5-min scheduled batch) |
| Sub-second, event-driven, many consumers | Streaming (Kafka + Flink/Spark). Expect 3–5× the operational cost. |
| Need to reprocess history often | Batch or micro-batch over a durable log. Streaming-only ("Kappa") makes replay a project. |
| Small tables (<10M rows), simple transforms | Just do a full refresh on a schedule. Incremental complexity is not free. |

Do not choose streaming because it sounds modern. Choose it when a downstream product is genuinely worse at 10-minute latency, and budget for consumer-lag monitoring, partition rebalancing, and dead-letter queues.

### Layering (medallion, or whatever you call it)

```
raw/landing   → append-only, source-shaped, partitioned by ingest date, never edited
staging       → typed, deduplicated, one row per source record, PII-scrubbed if needed
marts         → business entities, joins, aggregates; consumed by BI and ML
monitoring    → run metadata, quality results, freshness per table (a normal table, queryable)
```

Keep raw partitioned by `ingest_date` **and** carry the source's own event timestamp. Ingest-time partitioning makes backfills trivial; event-time partitioning makes queries cheap. You usually need both columns, partitioning on one.

## 2. Orchestration: Airflow vs Dagster vs Prefect

| | Airflow | Dagster | Prefect |
|---|---|---|---|
| Primitive | DAG of tasks | Asset (data), op inside asset | Flow of tasks, dynamic by default |
| Mental model | "Run these steps at 2am" | "This table should exist and be fresh" | "Run this Python orchestration" |
| Strength | Ecosystem, managed options everywhere, ops familiarity | Lineage, asset-centric backfills, typed I/O, local dev | Lowest ceremony, dynamic/parameterized flows, great DX |
| Weakness | Task-centric lineage, DAG-file churn, scheduler scaling | Smaller hiring pool, opinionated | Weaker first-class asset lineage; state model simpler |
| Backfill UX | `airflow dags backfill` / clear task instances | Partition-based, one click, lineage-aware | `flow.serve` / deployment-based reruns |
| Choose when | Team already runs it, or you need max managed-host options | Many interdependent tables and lineage/questions like "why is this stale" | Python-heavy team, few tables, dynamic fan-out, fast setup |

**Airflow — asset-aware batch DAG (Airflow 2.7+ / 3.x):**

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.datasets import Dataset

ORDERS_RAW = Dataset("warehouse://raw/orders")

@dag(
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,          # explicit backfills only
    max_active_runs=1,      # serialize writers to the same target
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5),
                  "retry_exponential_backoff": True, "max_retry_delay": timedelta(minutes=30)},
    tags=["orders", "tier1"],
)
def orders_elt():
    @task(outlets=[ORDERS_RAW])
    def extract(ds: str | None = None):
        # ds is the logical date — derive the partition from it, never from now()
        return run_extract(partition_date=ds)

    @task
    def load(payload):
        return run_merge(payload, partition_date=payload["partition_date"])

    @task
    def check(ds: str | None = None):
        assert_freshness("warehouse.orders", partition_date=ds)

    check(load(extract()))

orders_elt()
```

Key points: `catchup=False` so a typo in `start_date` doesn't enqueue three years of runs; `max_active_runs=1` to prevent two writers merging into the same partition; partition derived from the **logical date**, not `datetime.now()` — otherwise reruns write to the wrong window.

**Dagster — partitioned asset (backfill comes free):**

```python
from dagster import asset, AssetExecutionContext, DailyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2026-01-01")

@asset(partitions_def=daily, deps=["raw_orders"], group_name="warehouse")
def orders(context: AssetExecutionContext) -> None:
    day = context.partition_key           # "2026-11-13"
    merge_partition("orders", day)        # idempotent MERGE on order_id
    context.log.info(f"merged orders for {day}")
```

Because the asset declares `partitions_def`, Dagster records materialization per partition and can backfill any range with correct lineage — the reason to prefer it when the org has many interdependent tables.

**Prefect — dynamic fan-out:**

```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def sync_table(table: str, day: str) -> int:
    return merge_partition(table, day)

@flow(log_prints=True)
def sync_all(day: str, tables: list[str]):
    for table in tables:              # native dynamic mapping
        sync_table.submit(table, day)
```

**Anti-pattern in all three:** one giant DAG with 200 tasks where task 87 fails and nobody knows which tables are stale. Split by domain, tag by criticality, and let the monitoring table drive alerting, not the DAG graph.

## 3. Idempotency and Incremental Loads

### The three idempotency strategies

1. **Partition overwrite (best).** `DELETE WHERE partition_date = :p` then insert, or `CREATE OR REPLACE TABLE ... PARTITION`. Simple, obviously correct, cheap when partitions are bounded.
2. **MERGE / upsert on a business key.** Correct when records mutate after creation and you cannot rewrite the whole partition.
3. **Append with a dedupe view.** Land everything, then `QUALIFY ROW_NUMBER() OVER (PARTITION BY key ORDER BY ingested_at DESC) = 1` downstream. Use when the source has no update semantics and the raw layer must stay append-only.

Never: `INSERT INTO target SELECT * FROM staging` on rerun. That is the bug behind "revenue doubled in the dashboard".

### High-watermark incremental load

```sql
-- 1. read the watermark from the target, not from a config file
SELECT COALESCE(MAX(updated_at), TIMESTAMP '1970-01-01 00:00:00') AS wm
FROM warehouse.orders;

-- 2. extract a HALF-OPEN window, bounded on both sides
SELECT * FROM source.orders
WHERE updated_at >  @watermark
  AND updated_at <= @run_logical_ts      -- never now(): reruns must reproduce the run
```

Half-open `(low, high]` prevents both gaps and double-processing. Store the high bound you actually used in the run metadata table so a failure mid-batch is resumable.

### Handling late and duplicate data

- Carry a **`_ingested_at`** and the source **`updated_at`**; the merge compares `updated_at` so an older duplicate cannot overwrite a newer row.
- Late data older than the watermark is the classic silent-loss bug. Options: (a) widen the lookback window (`wm - 3 days`) and rely on MERGE to dedupe, (b) accept lateness explicitly and document the cutoff, (c) keep append-only raw and reprocess the partition.
- Deduplicate **before** the merge on the business key, ordered by `updated_at DESC, ingested_at DESC`, or MERGE will fail with "unstable source" on multi-match.

```sql
MERGE `proj.warehouse.orders` T
USING (
  SELECT * EXCEPT (rn) FROM (
    SELECT *, ROW_NUMBER() OVER (
      PARTITION BY order_id ORDER BY updated_at DESC, _ingested_at DESC) AS rn
    FROM `proj.staging.orders`
    WHERE _partition_date = @p
  ) WHERE rn = 1
) S
ON T.order_id = S.order_id
WHEN MATCHED AND S.updated_at > T.updated_at THEN UPDATE SET
  status = S.status, amount = S.amount, updated_at = S.updated_at
WHEN NOT MATCHED THEN INSERT (order_id, status, amount, updated_at, _ingested_at)
VALUES (S.order_id, S.status, S.amount, S.updated_at, S._ingested_at);
```

### Deletes

Full-refresh hides deletes; incremental loads lose them. Pick one and write it down: soft-delete flag from the source, CDC (`op` field / Debezium `__deleted`), or a periodic anti-join reconciliation against the full source key set.

## 4. Schema Drift

Drift is the most common cause of "it worked for six months and then broke". Upstream teams add columns, rename them, widen types, or start sending `null`.

### Detect

Store a canonical schema snapshot and diff it on every run:

```python
import hashlib, json

def schema_fingerprint(columns: list[dict]) -> str:
    """columns: [{"name": ..., "type": ...}] — order-independent, case-normalized."""
    canon = sorted((c["name"].lower(), c["type"].lower()) for c in columns)
    return hashlib.sha256(json.dumps(canon).encode()).hexdigest()[:16]
```

Compare against `monitoring.schema_snapshots` keyed by (table, fingerprint). A changed fingerprint is a drift event even if nothing failed — that is the point.

Also read the live catalog rather than trusting your DDL: BigQuery `INFORMATION_SCHEMA.COLUMNS`, Snowflake `INFORMATION_SCHEMA.COLUMNS`, Redshift `SVV_COLUMNS` / `pg_table_def`.

### Classify and handle

| Drift | Risk | Action |
|---|---|---|
| **New nullable column** | Low | Auto-accept: add to target, backfill `NULL`, log event, notify owner. |
| **New NOT NULL column** | Medium | Add with a default or quarantine the batch; never let the loader crash silently. |
| **Type widening** (`int` → `bigint`, `int` → `float`) | Low-medium | Accept if lossless; coerce explicitly and record the cast. |
| **Type narrowing** / incompatible change | High | **Quarantine** the batch to a dead-letter table, alert, do not write to the target. |
| **Column renamed** | High (silent NULLs) | Detect via fingerprint + null-rate spike; require an explicit mapping in config. |
| **Column dropped** | High (silent NULLs) | Keep the target column, stop populating, alert. Never auto-drop from a warehouse table. |
| **Enum/new category values** | Medium | Land as-is; enforce the vocabulary in the quality layer, not the loader. |

Two rules that prevent most incidents:

1. **Loaders must be tolerant on read and strict on write.** Unknown fields go to a `_extra` JSON column or are dropped with a metric — they must not raise. Known fields are validated.
2. **Never auto-alter a warehouse table destructively.** Adding columns is safe; dropping, renaming, or retyping needs a human and a migration.

For streaming, register schemas in a registry (Confluent Schema Registry / Glue) with `BACKWARD` compatibility, and route unparseable messages to a DLQ topic rather than killing the consumer group.

## 5. Data Quality at Pipeline Boundaries

Check at three boundaries: **after extract** (is the source sane?), **after transform** (is the logic sane?), **before publish** (is the target sane?).

Minimum viable check set per table:

| Check | Fails when | Blocks publish? |
|---|---|---|
| **Freshness** | `now - max(event_ts) > SLA` | Yes (tier 1) |
| **Volume** | row count deviates > N% from trailing median | Yes — usually the cheapest real bug catcher |
| **Uniqueness** | duplicate business keys in a partition | Yes |
| **Not-null** | null rate on required columns exceeds threshold | Yes |
| **Referential** | orphan FKs vs dimension | Warn (or block on facts) |
| **Distribution** | a category's share shifts absurdly (e.g. 90% `unknown`) | Warn |
| **Range/enum** | negative amounts, future dates, invalid status | Warn |

```sql
-- volume + freshness + uniqueness in one pass, run per partition
SELECT
  COUNT(*)                                        AS rows,
  COUNT(DISTINCT order_id)                        AS distinct_keys,
  SUM(IF(order_id IS NULL, 1, 0))                 AS null_keys,
  MAX(updated_at)                                 AS max_event_ts,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(updated_at), MINUTE) AS lag_minutes
FROM `proj.warehouse.orders`
WHERE _partition_date = @p;
```

Thresholds belong in config next to the pipeline, versioned, with an owner. `rows < 0.5 * trailing_7d_median` catches "the upstream job didn't run" better than any schema check. Emit every result as a row in a monitoring table — dashboards and alerts read the table, not logs.

Blocking vs warning: block when bad data would corrupt a metric someone makes decisions on; warn when it would only annoy. A pipeline that blocks on everything gets disabled within a month.

## 6. Monitoring and Observability

Four signals per pipeline, emitted on every run:

1. **Freshness** — `now - max(event_ts)` vs SLA, per table and per partition.
2. **Volume** — rows written/read, delta vs trailing baseline.
3. **Latency / duration** — run wall time vs trailing p50/p95; also per-stage so you know *where* it slowed.
4. **Run status + schema fingerprint** — success/fail, retries, drift events.

Also track **cost** (bytes scanned, credits, slots) — a schedule change from daily to hourly is a 24× scan multiplier and nobody notices until the invoice.

### Alert design

- Alert on **symptoms users feel**: table stale past SLA, row count collapse, partition missing. Not "task X retried".
- One alert per incident: alert on the *first failing partition*, suppress duplicates for the same root cause (grouping/dedup key = pipeline + failure class).
- Always include in the payload: table, partition, expected vs actual, the run URL, and the last good timestamp. An alert without numbers gets ignored.
- Page only for tier-1 (revenue/customer-facing dashboards). Everything else → ticket.
- **Watchdog the scheduler itself**: an "if no successful run in 2× interval, alert" check outside the orchestrator. A dead scheduler emits no failures.

```python
# stdlib-only freshness/volume check — see scripts/data_freshness_check.py
from scripts.data_freshness_check import analyze_table, parse_ts

report = analyze_table(
    table_state,                              # {"table": ..., "partitions": [...]}
    parse_ts("2026-11-13T09:00:00Z"),         # evaluate as of a fixed instant
    {"cadence": 60, "sla_multiple": 2.0},     # defaults when the table doesn't declare them
)
if report["status"] == "fail":
    alert(report["table"], report["failures"])   # include the numbers in the payload
```

Lineage matters for debugging: when a mart is wrong you need "which upstream partitions fed this row". Airflow assets/`outlets`, Dagster's asset graph, and dbt's manifest all give this; a spreadsheet does not.

## 7. Backfill and Replay

Backfill is a **product feature of the design**, not an emergency procedure. If a partition cannot be recomputed in isolation, the pipeline is not done.

Procedure:

1. **Scope by partition, never by row count.** Enumerate the exact partitions to recompute; write them to a file and iterate — resumable after failure.
2. **Prove idempotency first.** Rerun one already-good partition and assert the output is byte-identical (or row-count + checksum identical). If not, stop and fix the merge.
3. **Throttle.** `max_active_runs` / concurrency limits; a 400-partition backfill can saturate the warehouse and starve production. Backfill outside business hours or against a lower-priority queue/compute pool.
4. **Isolate when the target is live.** Write to `table_backfill`, verify, then `ALTER TABLE ... SWAP WITH` / atomic replace. Never let a half-finished backfill serve traffic.
5. **Cascade downstream explicitly.** Recomputing a source partition invalidates downstream aggregates; either the orchestrator tracks it (Dagster partitions, dbt `--select state:modified+`) or you list dependents by hand.
6. **Record it.** Backfill runs go in the same monitoring table with `run_type=backfill`, so freshness alerts don't misfire and audits can explain a spike.

Replay from the raw layer, not from the source API, whenever the API has retention limits or rate limits. That is the strongest argument for keeping raw immutable and complete.

Never: `UPDATE` a production table in place to "fix" history, or backfill into an append-only table without dedupe.

## 8. Warehouse-Specific Patterns

### BigQuery

- **Partition** on the column people filter by (`DATE(created_at)` or `_PARTITIONDATE` for ingest-time). Daily partitions, not hourly, unless volume demands it; >4,000 partitions degrades metadata performance.
- **Cluster** on high-cardinality filter/join columns, max 4, order by filter frequency. Clustering is free-ish; partitioning is what saves money.
- **Enforce partition filters** on big tables (`require_partition_filter = TRUE`) so a stray `SELECT *` fails instead of scanning 40 TB.
- Prefer `MERGE` on the partition, `INSERT` with `WRITE_APPEND` for pure appends, and `WRITE_TRUNCATE` per partition for rebuilds.
- Cost control: `maximum_bytes_billed` on every job; dry-run in CI; `INFORMATION_SCHEMA.JOBS` for per-query attribution.

### Snowflake

- Micro-partitions are automatic; **clustering keys** are only worth it on very large tables (>~1 TB) with a clear, stable filter column (`CLUSTER BY (event_date, customer_id)`). Over-clustering burns credits for nothing — watch `SYSTEM$CLUSTERING_INFORMATION` and clustering depth.
- Use `MERGE` (or `COPY INTO` + `MERGE`) for incremental; `SWAP WITH` for atomic rebuilds.
- Separate warehouses per workload class (loading / transforming / BI) so a backfill cannot starve dashboards. Set `STATEMENT_TIMEOUT_IN_SECONDS` and resource monitors.
- `COPY INTO` with `ON_ERROR = 'SKIP_FILE'` + a `VALIDATION_MODE` dry run before promoting a load.

### Redshift

- **DISTKEY** on the column used in the biggest join (usually the fact's FK to the largest dimension); `DISTSTYLE ALL` for small dimensions.
- **SORTKEY**: compound `(event_date, id)` when queries filter on a leading date range; interleaved only for genuinely multi-dimensional ad-hoc access (it costs more VACUUM).
- Load with `COPY` from S3 (parallel), never row-by-row `INSERT`. Run `VACUUM`/`ANALYZE` (or `VACUUM SORT ONLY`) after large loads; check `SVV_TABLE_INFO` for unsorted percentage.
- Watch `STL_ALERT_EVENT_LOG` for nested-loop and missing-statistics events.

### Cross-warehouse rules

- Semi-structured payloads (JSON) go into a native JSON/VARIANT/SUPER column plus extracted typed columns for the hot fields — do not explode everything into columns on day one.
- Timezone: store UTC `TIMESTAMP`, convert at presentation. A pipeline that mixes local time will produce a 23- or 25-hour day twice a year.
- Currency/units: normalize at ingest, record the rate/source used.

## 9. Anti-Patterns (and the fix)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| `SELECT *` into a typed target | Breaks on new upstream column | Explicit column list + drift-tolerant reader |
| `now()` as the partition bound | Reruns write different windows | Pass the logical run timestamp |
| Append-only without dedupe | Duplicated revenue | MERGE, or partition overwrite, or dedupe view |
| One monolithic DAG | Slow, unclear blast radius | Domain DAGs, tags, `max_active_runs` |
| Silent `try/except: pass` in loader | Missing data, green pipeline | Fail loud or write to DLQ + alert |
| Alert on task retries | Noise, then ignored | Alert on staleness/volume at the table |
| Backfill by editing `start_date` | Uncontrolled 3-year run, duplicate writes | Partition-scoped backfill command |
| Schema auto-migrate in production | Dropped columns, broken dashboards | Additive only; destructive changes need review |
| Full refresh of a 2 TB table hourly | Warehouse bill shock | Incremental + partition filter |
| Tests only on the transform | Bad source data lands anyway | Check at extract, transform, and publish |

## 10. Build Checklist

Before calling a pipeline done:

- [ ] Partition column chosen; every write is scoped to a partition.
- [ ] Rerunning the same partition twice produces identical results (**test this**).
- [ ] Incremental bound comes from the target watermark + logical run time, half-open interval.
- [ ] Late-arrival policy written down (lookback window or documented cutoff).
- [ ] Deletes handled (soft delete, CDC, or reconciliation job).
- [ ] Schema fingerprint recorded per run; drift classified; unknown fields tolerated.
- [ ] Freshness, volume, uniqueness, and null checks emit rows to a monitoring table.
- [ ] Alerts fire on staleness/volume, include numbers and a run link, and page only tier-1.
- [ ] Backfill path exists, is throttled, and is isolated from the live table.
- [ ] Warehouse physical design set: partitioning, clustering/sort/dist keys, partition filter enforcement.
- [ ] Cost guardrails: `maximum_bytes_billed` / resource monitor / query timeout.
- [ ] Owner, SLA, and tier recorded in the pipeline config.
- [ ] Scheduler watchdog exists outside the orchestrator.
- [ ] Run `python3 scripts/pipeline_lint.py <spec.json>` and resolve all errors.

## 11. Bundled Scripts

Both are stdlib-only, no pip installs, safe for CI.

```bash
# Static validation of a pipeline spec (JSON, or Python dict via --json-stdin)
python3 scripts/pipeline_lint.py spec.json

# Freshness / volume / gap analysis over partition run records
python3 scripts/data_freshness_check.py state.json --cadence-minutes 60 --sla-multiple 2
```

`pipeline_lint.py` catches the errors that cause incidents rather than style nits: missing idempotency declaration, non-partition-scoped writes, absent quality checks, missing owner/SLA, `now()`-style non-determinism flags, unsafe full-refresh on large tables, and unbounded backfill config.

`data_freshness_check.py` reads run records (`{"table": ..., "partitions": [{"date": ..., "rows": ..., "max_event_ts": ...}]}`), reports lag against SLA, row-count anomalies versus the trailing median, and missing partitions in the expected sequence.

See `references/sources.md` for authoritative upstream documentation.

## 12. Debugging a Failing Run — Order of Operations

1. **Read the run metadata**, not just the traceback: which partition, how many rows were written before the failure, was the target partially committed?
2. **Classify**: source unavailable / schema drift / data quality / resource contention (lock, slot, memory) / code bug / config.
3. **Check the blast radius**: does the target hold partial data? If yes, fix the partition before re-enabling the schedule — a partial commit plus a retry is exactly how duplicates appear.
4. **Rerun one partition** with logs at debug level. Never "rerun everything" as the first move.
5. **If it passed on retry, find out why** — lock timeouts and contention are real bugs, not noise. Add serialization or stagger the schedule.
6. **Close the loop**: add the check that would have caught it earlier, and record the failure class in the monitoring table so trends are visible.

For a hung or slow pipeline, look at the warehouse side first (queue time, `INFORMATION_SCHEMA.JOBS`, `STL_WLM_QUERY`, `QUERY_HISTORY`), not the orchestrator. The orchestrator usually reports the symptom.
