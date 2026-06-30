# dbt Model Patterns Reference

Comprehensive reference for dbt model design patterns: staging, intermediate, and marts layers; materialization strategies; incremental model patterns; snapshots; and seeds.

---

## The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│                    SOURCES                          │
│         (raw data in warehouse — read only)          │
└──────────────────────┬──────────────────────────────┘
                       │  source() references
                       ▼
┌─────────────────────────────────────────────────────┐
│  STAGING (stg_)                                     │
│  • 1:1 with source tables                           │
│  • Rename, recast, light transforms                  │
│  • Materialized as VIEWS                            │
│  • Zero business logic                              │
│  • Naming: stg_<source>__<table>                    │
└──────────────────────┬──────────────────────────────┘
                       │  ref() references
                       ▼
┌─────────────────────────────────────────────────────┐
│  INTERMEDIATE (int_)                                │
│  • Join staging models together                     │
│  • Business logic aggregation                       │
│  • Materialized as EPHEMERAL or VIEWS               │
│  • Not exposed to BI tools                          │
│  • Naming: int_<purpose>                            │
└──────────────────────┬──────────────────────────────┘
                       │  ref() references
                       ▼
┌─────────────────────────────────────────────────────┐
│  MARTS (fct_, dim_)                                 │
│  • Business-defined entities and processes           │
│  • Materialized as TABLES or INCREMENTAL            │
│  • Exposed to BI, ML, reverse ETL                   │
│  • Naming: fct_<process>, dim_<entity>              │
└─────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Patterns

### Staging Layer

**Purpose:** Create a clean, renamed copy of each source table. No joins, no aggregations, no business logic.

**Rules:**
1. One staging model per source table (1:1 mapping)
2. Use `source()` macro — never hardcode table references
3. Column renaming: use a `renamed` CTE — snake_case, descriptive, consistent
4. Light type casting (cents → dollars, string → date, etc.)
5. Materialized as `view` — no storage cost, always fresh
6. Never join two sources in staging

```sql
-- models/staging/shopify/stg_shopify__orders.sql
WITH source AS (
    SELECT * FROM {{ source('shopify', 'orders') }}
),

renamed AS (
    SELECT
        id                  AS order_id,
        customer            AS customer_id,
        total_price         / 100.0 AS total_amount_dollars,
        financial_status,
        fulfillment_status,
        created_at,
        updated_at,
        _synced_at          AS _synced_at
    FROM source
)

SELECT * FROM renamed
```

**Column naming conventions for staging:**
- Use `_` prefix for metadata columns: `_synced_at`, `_batched_at`, `_line`
- Always add descriptions in YAML
- Add basic tests (unique, not_null) on keys
- Add freshness checks on source tables

### Intermediate Layer

**Purpose:** Combine staging models into reusable building blocks for marts. Performance-critical: only materialize when needed by 3+ downstream models.

**Rules:**
1. Name describes the transformation purpose: `int_customer_orders`, `int_daily_sessions`
2. Materialized as `ephemeral` when referenced by 1-2 downstream models
3. Materialized as `view` when referenced by 3+ models or when debugging
4. May join multiple staging models
5. May apply business logic (currency conversion, deduplication, etc.)
6. Should NOT be the final answer for a business question

```sql
-- models/intermediate/int_customer_orders.sql
{{
    config(
        materialized = 'ephemeral'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_shopify__orders') }}
    WHERE financial_status != 'voided'
),

order_items AS (
    SELECT * FROM {{ ref('stg_shopify__order_items') }}
),

aggregated AS (
    SELECT
        orders.order_id,
        orders.customer_id,
        orders.order_date,
        orders.financial_status,
        COUNT(DISTINCT order_items.item_id) AS line_item_count,
        SUM(order_items.quantity)           AS total_quantity,
        SUM(order_items.price)              AS total_items_amount,
        MAX(orders.updated_at)              AS last_updated
    FROM orders
    LEFT JOIN order_items USING (order_id)
    GROUP BY 1, 2, 3, 4
)

SELECT * FROM aggregated
```

### Marts Layer

**Purpose:** Business-defined entities (dimensions) and processes (facts). This is what BI tools query.

#### Fact Tables

- **Prefix:** `fct_`
- **Content:** Business events/transactions, numeric measures, foreign keys to dimensions
- **Grain:** One row per business event (order, payment, session, ticket, etc.)
- **Materialization:** `table` for small (<1M rows), `incremental` with merge for large

```sql
-- models/marts/finance/fct_orders.sql
{{
    config(
        materialized = 'incremental',
        unique_key = 'order_id',
        incremental_strategy = 'merge',
        on_schema_change = 'sync_all_columns',
        partition_by = {'field': 'order_date', 'data_type': 'date'},
        cluster_by = ['customer_id']
    )
}}

WITH customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
    {% if is_incremental() %}
        WHERE last_updated > (SELECT MAX(last_updated) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

final AS (
    SELECT
        co.order_id,
        co.customer_id,
        c.customer_name,
        c.customer_segment,
        co.order_date,
        co.financial_status,
        co.line_item_count,
        co.total_quantity,
        co.total_items_amount,
        co.last_updated
    FROM customer_orders co
    LEFT JOIN customers c USING (customer_id)
)

SELECT * FROM final
```

#### Dimension Tables

- **Prefix:** `dim_`
- **Content:** Descriptive attributes, slowly changing, wide tables
- **Grain:** One row per entity instance (customer, product, location)
- **Materialization:** `table` (rebuilt) or `snapshot` (for SCD Type 2)

```sql
-- models/marts/marketing/dim_customers.sql
{{
    config(
        materialized = 'table'
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_shopify__customers') }}
),

orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(*)        AS lifetime_orders,
        SUM(total_amount) AS lifetime_value
    FROM {{ ref('fct_orders') }}
    GROUP BY 1
),

final AS (
    SELECT
        c.customer_id,
        c.email,
        c.first_name,
        c.last_name,
        c.country,
        c.state               AS customer_state,
        c.created_at          AS customer_created_at,
        o.first_order_date,
        o.last_order_date,
        o.lifetime_orders,
        o.lifetime_value,
        CASE
            WHEN o.lifetime_value >= 500 THEN 'VIP'
            WHEN o.lifetime_value >= 100 THEN 'Regular'
            WHEN o.lifetime_orders > 0   THEN 'New'
            ELSE 'Prospect'
        END AS customer_segment
    FROM customers c
    LEFT JOIN orders o USING (customer_id)
)

SELECT * FROM final
```

---

## Materialization Decision Matrix

```
Materialization    │ Compute Cost │ Storage Cost │ Freshness  │ Use When
───────────────────┼──────────────┼──────────────┼────────────┼──────────────────────────
View               │   Low (query)│   Zero       │   Always   │ Staging, light transforms
Ephemeral          │   Low (CTE)  │   Zero       │   Always   │ Intermediate, 1-2 dependents
Table              │   High (full)│   High       │   At build │ Marts, small dimensions
Incremental        │   Medium     │   Medium     │   At build │ Large fact tables (>1M rows)
  — append         │   Low        │   Medium     │   At build │ Immutable event streams
  — merge          │   Medium     │   Medium     │   At build │ Mutable records, deduplication
  — delete+insert  │   Medium     │   Medium     │   At build │ Full row replacement
  — insert_overwrite│  Medium     │   Medium     │   At build │ Partition-based (Spark, BQ)
Snapshot           │   High (SCD) │   High       │   At build │ Slowly changing dimensions
```

### View vs Ephemeral vs Table Decision Flow

```
Model is staging?                    → View (always)
Model is intermediate?
  ├─ Referenced by 1 downstream?     → Ephemeral
  ├─ Referenced by 2-3 downstream?   → Ephemeral (default) or View (if debugging)
  └─ Referenced by 4+ downstream?    → View
Model is mart (dimension)?
  ├─ < 100K rows?                    → Table
  └─ SCD Type 2 required?            → Snapshot
Model is mart (fact)?
  ├─ < 1M rows?                      → Table
  └─ > 1M rows?                      → Incremental
```

---

## Incremental Model Strategies

### Strategy: merge (Snowflake, BigQuery, Databricks)

Best for: Mutable source data where records can be updated after creation.

```sql
{{
    config(
        materialized = 'incremental',
        unique_key = 'order_id',
        incremental_strategy = 'merge',
        merge_update_columns = ['status', 'total_amount', 'updated_at']
    )
}}

-- On the first run, process all rows
-- On subsequent runs, only process rows newer than the max updated_at in the table
{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### Strategy: delete+insert (Postgres, Redshift, default)

Best for: Replace entire rows when source data changes. Simpler than merge, but replaces all columns.

```sql
{{
    config(
        materialized = 'incremental',
        unique_key = 'session_id',
        incremental_strategy = 'delete+insert'
    )
}}

{% if is_incremental() %}
    WHERE session_date >= (SELECT MAX(session_date) FROM {{ this }}) - INTERVAL '3 days'
{% endif %}
```

**Overlap window:** Always add a lookback window (like `- INTERVAL '3 days'`) to catch late-arriving data.

### Strategy: append

Best for: Immutable event streams, audit logs, clickstream data.

```sql
{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

{% if is_incremental() %}
    WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

### Strategy: insert_overwrite (Spark, BigQuery)

Best for: Partitioned tables where you rebuild entire partitions.

```sql
{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'insert_overwrite',
        partition_by = {'field': 'event_date', 'data_type': 'date'}
    )
}}
```

### Incremental Best Practices

| Practice | Why |
|---|---|
| **Always add a lookback window** | Prevents data gaps from late-arriving records |
| **Use `merge_update_columns`** | Only update columns that actually change |
| **Add `updated_at` to all models** | Enables efficient incremental filtering |
| **Set `on_schema_change: sync_all_columns`** | Avoids full refresh on column additions |
| **Set `full_refresh: false` in project config** | Prevents accidental costly full refreshes |
| **Use `unique_key` with composite keys** | `unique_key = ['order_id', 'line_item_id']` |
| **Test incremental logic with unit tests** | Validate merge/upsert behavior offline |
| **Monitor incremental model runtime** | Alert if incremental build starts taking as long as full refresh |

---

## Snapshots (Slowly Changing Dimensions)

### Timestamp Strategy (recommended)

```sql
{% snapshot products_snapshot %}

{{
    config(
        target_database = 'analytics',
        target_schema = 'snapshots',
        unique_key = 'product_id',
        strategy = 'timestamp',
        updated_at = 'updated_at',
        invalidate_hard_deletes = True
    )
}}

SELECT
    product_id,
    product_name,
    category,
    price,
    is_active,
    updated_at
FROM {{ source('raw', 'products') }}

{% endsnapshot %}
```

### Check Strategy (for sources without reliable timestamps)

```sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema = 'snapshots',
        unique_key = 'customer_id',
        strategy = 'check',
        check_cols = ['email', 'first_name', 'last_name', 'country']
    )
}}

SELECT * FROM {{ source('crm', 'customers') }}

{% endsnapshot %}
```

### Snapshot Columns

dbt automatically adds these columns to snapshot tables:

| Column | Description |
|---|---|
| `dbt_scd_id` | Unique hash of the key + updated_at |
| `dbt_updated_at` | When the snapshot was run |
| `dbt_valid_from` | When this row version became valid |
| `dbt_valid_to` | When this row version was superseded (NULL = current) |

Query only current records:
```sql
SELECT * FROM {{ ref('products_snapshot') }}
WHERE dbt_valid_to IS NULL
```

### Snapshot Best Practices

| Practice | Why |
|---|---|
| `invalidate_hard_deletes: true` | Tracks row deletions in source |
| Dedicated `snapshots/` directory | Clear separation from models |
| Separate schema for snapshots | `analytics_snapshots` schema keeps snapshots isolated |
| Run snapshots in separate job | Snapshots can be slower; separate from model builds |
| Test snapshot uniqueness | `unique` test on `dbt_scd_id` |

---

## Seeds

Seeds are CSV files loaded as tables. Best for small, static reference data.

### When to Use Seeds

| ✅ Use seeds for | ❌ Don't use seeds for |
|---|---|
| Country/region codes | Large datasets |
| Product categories | Frequently changing data |
| Status code mappings | Data that requires ETL |
| Fiscal calendars | PII or sensitive data |
| Test/seed data for dev | Primary business data |

### Seed Configuration

```yaml
# dbt_project.yml
seeds:
  my_project:
    +schema: reference_data
    +quote_columns: false
    country_codes:
      +column_types:
        country_code: varchar(2)
        country_name: varchar(100)
        region: varchar(50)
```

### CSV Best Practices
- **One header row** — no multi-line headers
- **Snake_case headers** — consistent with model naming
- **No formulas** — plain values only
- **UTF-8 encoding** — no special character issues
- **< 1MB file size** — larger data belongs in ELT pipeline

---

## Model Organization Anti-Patterns

| ❌ Anti-Pattern | ✅ Better Approach |
|---|---|
| One giant monolith model | Break into staging → intermediate → marts |
| `SELECT *` in production models | Explicit column selection |
| Business logic in staging models | Keep staging clean, logic in intermediate/marts |
| `ref()` to raw sources | Always use `source()` for raw data |
| Joining 6+ tables in one model | Use intermediate models to manage complexity |
| No YAML config for models | Every model needs at least description + key tests |
| Hardcoded values in SQL | Use `var()`, seeds, or macros |
| `LIMIT 100` in production models | Use `--limit` flag in development only |
| All models as `table` | Use incremental for large tables, ephemeral for intermediates |

---

## Cross-Database Pattern Differences

### Snowflake-Specific

```sql
-- Snowflake uses MERGE natively
{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'merge',
        unique_key = 'id'
    )
}}

-- Snowflake clustering
{{
    config(
        cluster_by = ['customer_id', 'event_date']
    )
}}
```

### BigQuery-Specific

```sql
-- BigQuery partitioning
{{
    config(
        materialized = 'incremental',
        partition_by = {
            'field': 'event_date',
            'data_type': 'date',
            'granularity': 'day'
        },
        require_partition_filter = true
    )
}}

-- BigQuery uses insert_overwrite by partition
{{
    config(
        incremental_strategy = 'insert_overwrite'
    )
}}
```

### Databricks/Spark-Specific

```sql
-- Delta Lake merge
{{
    config(
        materialized = 'incremental',
        file_format = 'delta',
        incremental_strategy = 'merge',
        unique_key = 'id'
    )
}}

-- Unity Catalog three-level namespace
{{ source('catalog', 'schema', 'table') }}
```