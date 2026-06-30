---
name: dbt-data-transformation
description: Production-grade dbt (data build tool) analytics engineering for AI agents: model development, testing, documentation, semantic layer, dbt Mesh governance, and migration workflows. Follows dbt Labs best practices for data transformation, incremental strategies, and multi-project collaboration.
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
domain: Data/Analytics Engineering
version: 1.0.0
---

# dbt Data Transformation — Agent Skill

Production-grade analytics engineering with dbt™ (data build tool). This skill covers the complete dbt workflow: model authoring, testing, documentation, semantic layer design, multi-project dbt Mesh governance, platform operations, and migration strategies.

## When to Use This Skill

### ✅ DO trigger when:

- **Create dbt model** — "Create a dbt model that transforms raw orders into a customer_orders mart"
- **Write dbt test** — "Write data tests for my staging models to ensure referential integrity"
- **dbt unit test** — "Add unit tests for this incremental model's merge logic"
- **Build semantic layer** — "Define MetricFlow semantic models and metrics for revenue reporting"
- **Migrate dbt** — "Migrate our v1.5 project to v1.9 with best practices"
- **dbt Mesh** — "Set up cross-project refs between our finance and marketing dbt projects"
- **MetricFlow** — "Create a saved query for monthly recurring revenue"
- **dbt project** — "Initialize a new dbt project following best-practice structure"
- **Debug dbt job** — "Troubleshoot this failed incremental model build"
- **Optimize dbt** — "Reduce warehouse costs for our daily dbt run"
- **Model contracts** — "Enforce model contracts on our marts models"
- **dbt documentation** — "Generate or improve dbt docs for our models"
- **Snapshots / SCD** — "Configure snapshot strategies for slowly changing dimensions"
- **Jinja macros** — "Write a Jinja macro for dynamic schema generation"

### ❌ DO NOT trigger for:

- **General SQL questions** — "How do I write a SELECT statement?" → Use `query-expert` skill
- **Data pipeline orchestration** — "How do I schedule an Airflow DAG?" → Use pipeline/orchestration skills
- **Snowflake/BigQuery admin** — "How do I create a Snowflake warehouse?" → Use warehouse-platform skills
- **General ETL/ELT design** — "Design our data ingestion pipeline" → Only if the answer is dbt-specific
- **Python data processing** — "Write a pandas script to clean data" → Use `python` or `data-analysis` skill

## Progressive Disclosure — Domain Selection

This skill is organized into 5 domains. At the start of each interaction, assess which domain the user needs and disclose only the relevant depth.

### Domain Map

```
Level 1: Analytics Engineering (always visible)
  └─ Model patterns, project structure, materializations, Jinja, sources, seeds
Level 2: Testing (disclose on test/singular/unit/generic trigger)
  └─ Data tests, unit tests, singular tests, custom generic tests, severity thresholds, Great Expectations
Level 3: Semantic Layer (disclose on MetricFlow/semantic/metric trigger)
  └─ MetricFlow, semantic models, metrics, dimensions, measures, saved queries
Level 4: dbt Mesh (disclose on cross-project/governance/contract trigger)
  └─ Cross-project refs, model contracts, access controls, groups, versions, governance
Level 5: Platform & Operations (disclose on job/CLI/migration/debug trigger)
  └─ Job troubleshooting, dbt MCP server, CLI commands, Fusion migration, warehouse optimization
```

### Trigger → Domain Routing

| User says | Disclose domain |
|---|---|
| "create model", "staging", "mart", "incremental", "snapshot", "seed", "Jinja macro", "ref()" | Level 1 |
| "test", "unit test", "data test", "singular test", "generic test", "freshness", "Great Expectations" | Level 2 |
| "MetricFlow", "semantic model", "metric", "dimension", "measure", "saved query" | Level 3 |
| "dbt Mesh", "cross-project ref", "model contract", "governance", "group", "access", "version" | Level 4 |
| "job failed", "debug", "migrate", "upgrade", "dbt MCP", "cost", "performance", "compile error" | Level 5 |

---

## Level 1: Analytics Engineering

### Project Structure (Best Practice)

```
my_dbt_project/
├── dbt_project.yml
├── packages.yml
├── macros/
│   ├── cross_db_utils.sql
│   └── generate_schema_name.sql
├── models/
│   ├── staging/
│   │   └── source_name/
│   │       ├── _source_name__models.yml
│   │       ├── stg_source_name__table1.sql
│   │       └── stg_source_name__table2.sql
│   ├── intermediate/
│   │   └── int_customer_metrics.sql
│   └── marts/
│       ├── finance/
│       │   ├── _finance__models.yml
│       │   └── fct_orders.sql
│       └── marketing/
│           └── dim_customers.sql
├── seeds/
│   └── country_codes.csv
├── snapshots/
│   └── products_snapshot.sql
├── tests/
│   ├── generic/
│   │   └── assert_positive_value.sql
│   └── singular/
│       └── check_order_totals.sql
└── analyses/
    └── customer_cohorts.sql
```

### Naming Conventions

| Layer | Prefix | Example | Materialization |
|---|---|---|---|
| Staging | `stg_<source>__` | `stg_stripe__payments` | View |
| Intermediate | `int_` | `int_customer_orders` | Ephemeral / View |
| Fact tables | `fct_` | `fct_orders` | Table / Incremental |
| Dimension tables | `dim_` | `dim_customers` | Table |
| Snapshots | `snap_` prefix or filename | `snap_products` | Snapshot |
| Base (source 1:1) | `base_` | `base_stripe__invoices` | View |

### Materialization Decision Matrix

```
                    ┌──────────────────────────────────────────────┐
                    │           CHOOSE MATERIALIZATION              │
                    └──────────────────────────────────────────────┘
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                   View/Ephemeral    Table         Incremental
                        │               │               │
         ┌──────────────┤       ┌───────┤       ┌───────┤
         ▼              ▼       ▼               ▼
    Staging        Intermediate  Marts (fct/dim)  Large fact tables
    Light transforms  Joins     Small-medium    Append-only or
    No persistence    Chained   Snapshot        merge-update
    needed            deps     dimensions       patterns
```

**Rules of thumb:**
- **View**: Staging models, light transformations, always-fresh data needed. Zero storage cost.
- **Ephemeral**: Intermediate models only referenced by 1-2 downstream models. Avoids view stacking without table write cost.
- **Table**: Marts models (fct/dim), snapshot dimensions, models referenced by many downstream consumers. Rebuilt fully on each run.
- **Incremental**: Large fact tables (>1M rows), append-only pipelines, event data. Must define `is_incremental()` block and `unique_key`.

### Model Patterns

#### Staging Model

```sql
-- models/staging/stripe/stg_stripe__payments.sql
WITH source AS (
    SELECT * FROM {{ source('stripe', 'payments') }}
),

renamed AS (
    SELECT
        id                  AS payment_id,
        order_id,
        payment_method,
        status,
        amount              / 100.0 AS amount_dollars,   -- cents → dollars
        currency,
        created_at          AS payment_created_at,
        _batched_at         AS _batched_at
    FROM source
)

SELECT * FROM renamed
```

```yaml
# models/staging/stripe/_stripe__models.yml
version: 2

models:
  - name: stg_stripe__payments
    description: >
      Staged Stripe payment data. One row per payment transaction.
      Amounts are converted from cents to dollars.
    columns:
      - name: payment_id
        description: Primary key from Stripe.
        data_tests:
          - unique
          - not_null
      - name: order_id
        description: Foreign key to orders.
        data_tests:
          - not_null
          - relationships:
              to: ref('stg_jaffle_shop__orders')
              field: order_id
      - name: payment_method
        data_tests:
          - accepted_values:
              values: ['credit_card', 'debit_card', 'bank_transfer', 'gift_card']
      - name: amount_dollars
        description: Payment amount in USD (converted from cents).
        data_tests:
          - not_null
      - name: payment_created_at
        data_tests:
          - not_null
```

#### Intermediate Model

```sql
-- models/intermediate/int_customer_payments.sql
{{
    config(
        materialized = 'ephemeral'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_jaffle_shop__orders') }}
),

payments AS (
    SELECT * FROM {{ ref('stg_stripe__payments') }}
),

customer_payments AS (
    SELECT
        orders.customer_id,
        orders.order_id,
        SUM(payments.amount_dollars) AS total_amount,
        COUNT(DISTINCT payments.payment_id) AS payment_count,
        MAX(payments.payment_created_at) AS last_payment_at
    FROM orders
    LEFT JOIN payments USING (order_id)
    GROUP BY 1, 2
)

SELECT * FROM customer_payments
```

#### Fact Mart (Incremental)

```sql
-- models/marts/finance/fct_orders.sql
{{
    config(
        materialized = 'incremental',
        unique_key = 'order_id',
        incremental_strategy = 'merge',
        on_schema_change = 'sync_all_columns'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_jaffle_shop__orders') }}
    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

payments AS (
    SELECT * FROM {{ ref('int_customer_payments') }}
),

final AS (
    SELECT
        orders.order_id,
        orders.customer_id,
        orders.order_date,
        orders.status,
        orders.updated_at,
        COALESCE(payments.total_amount, 0) AS total_amount,
        COALESCE(payments.payment_count, 0) AS payment_count,
        payments.last_payment_at
    FROM orders
    LEFT JOIN payments USING (order_id)
)

SELECT * FROM final
```

#### Dimension Model (SCD Type 2 via Snapshot)

```sql
-- snapshots/products_snapshot.sql
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

SELECT * FROM {{ source('raw', 'products') }}

{% endsnapshot %}
```

### Source Configuration

```yaml
# models/sources.yml
version: 2

sources:
  - name: stripe
    database: raw
    schema: stripe_data
    description: Stripe payment processing data loaded by Fivetran.
    loader: fivetran
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _batched_at

    tables:
      - name: payments
        description: Raw payment transactions.
        columns:
          - name: id
            data_tests:
              - unique
              - not_null

      - name: refunds
        description: Raw refund transactions.

      - name: customers
```

### Jinja Macro Patterns

#### Dynamic Schema Generation

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- elif target.name == 'prod' -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}

{%- endmacro %}
```

#### Custom Generic Test

```sql
-- macros/positive_values.sql
{% test positive_values(model, column_name) %}

    SELECT *
    FROM {{ model }}
    WHERE {{ column_name }} < 0

{% endtest %}
```

#### Multi-Database Date Spine

```sql
-- macros/date_spine.sql
{% macro date_spine(datepart, start_date, end_date) %}
    {% if target.type == 'bigquery' %}
        SELECT * FROM UNNEST(
            GENERATE_DATE_ARRAY(
                DATE('{{ start_date }}'),
                DATE('{{ end_date }}'),
                INTERVAL 1 {{ datepart }}
            )
        ) AS date_day
    {% elif target.type == 'snowflake' %}
        -- Snowflake implementation
        SELECT DATEADD({{ datepart }}, ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1,
            '{{ start_date }}'::DATE) AS date_day
        FROM TABLE(GENERATOR(ROWCOUNT => {{ dbt_utils.pretty_time() }}))
    {% endif %}
{% endmacro %}
```

### Seeds

```sql
-- seeds/country_codes.csv
country_code,country_name,region,sub_region
US,United States,Americas,North America
GB,United Kingdom,Europe,Northern Europe
DE,Germany,Europe,Western Europe
```

```yaml
# dbt_project.yml
seeds:
  my_project:
    country_codes:
      +column_types:
        country_code: varchar(2)
        country_name: varchar(100)
        region: varchar(50)
        sub_region: varchar(50)
```

### dbt_project.yml Best Practice

```yaml
name: 'my_analytics_project'
version: '1.0.0'
config-version: 2
require-dbt-version: [">=1.9.0", "<2.0.0"]

profile: 'my_project'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
asset-paths: ["assets"]

clean-targets:
  - "target"
  - "dbt_packages"
  - "logs"

flags:
  send_anonymous_usage_stats: False

vars:
  # Project-level variables
  surrogate_key_treat_nulls_as_empty_strings: True
  'dbt_date:time_zone': 'UTC'

models:
  my_analytics_project:
    staging:
      +materialized: view
      +schema: staging
      +tags: ['staging']
    intermediate:
      +materialized: ephemeral
      +schema: intermediate
      +tags: ['intermediate']
    marts:
      +materialized: table
      +schema: marts
      +tags: ['marts']
      finance:
        +schema: finance
      marketing:
        +schema: marketing

snapshots:
  my_analytics_project:
    +target_schema: snapshots

seeds:
  my_analytics_project:
    +schema: seeds
```

---

## Level 2: Testing

### Test Strategy Pyramid

```
                    ┌──────────────┐
                    │   Unit Tests  │  ← Isolated logic (Jinja, SQL logic)
                    │   (specific)  │
                    ├───────────────┤
                    │  Data Tests   │  ← Column-level (unique, not_null, etc.)
                    │  (generic)    │
                    ├───────────────┤
                    │ Singular Tests│  ← Complex business rules
                    │  (one-off)    │
                    ├───────────────┤
                    │  Source       │  ← Freshness + row count
                    │  Freshness    │
                    └───────────────┘
```

### Data Tests (Schema YAML)

The most common pattern — declared inline in model YAML files:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - unique
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: total_amount
        data_tests:
          - not_null
          - positive_values   # custom generic test
      - name: status
        data_tests:
          - not_null
          - accepted_values:
              values: ['pending', 'shipped', 'delivered', 'cancelled']
              config:
                severity: error
```

### Custom Generic Tests

Generic tests are reusable test functions defined as SQL files in `tests/generic/`.

```sql
-- tests/generic/assert_referential_integrity.sql
{% test assert_referential_integrity(model, column_name, to, field) %}

    SELECT {{ column_name }}
    FROM {{ model }}
    WHERE {{ column_name }} IS NOT NULL
    EXCEPT
    SELECT {{ field }}
    FROM {{ to }}

{% endtest %}
```

Usage in YAML:
```yaml
columns:
  - name: customer_id
    data_tests:
      - assert_referential_integrity:
          to: ref('dim_customers')
          field: customer_id
```

### Singular Tests

One-off SQL queries that return rows when a test fails:

```sql
-- tests/singular/check_order_total_consistency.sql
-- Orders with items should have total_amount > 0
-- Orders with total_amount = 0 should have no items

WITH order_items AS (
    SELECT order_id, COUNT(*) AS item_count
    FROM {{ ref('stg_jaffle_shop__order_items') }}
    GROUP BY 1
),

orders AS (
    SELECT order_id, total_amount
    FROM {{ ref('fct_orders') }}
)

SELECT
    o.order_id,
    o.total_amount,
    COALESCE(oi.item_count, 0) AS item_count
FROM orders o
LEFT JOIN order_items oi USING (order_id)
WHERE
    -- Fail: has items but amount is 0
    (COALESCE(oi.item_count, 0) > 0 AND o.total_amount <= 0)
    OR
    -- Fail: no items but amount > 0
    (COALESCE(oi.item_count, 0) = 0 AND o.total_amount > 0)
```

### Unit Tests (dbt v1.8+)

Unit tests validate model transformation logic in isolation — no warehouse data needed.

```yaml
# models/marts/finance/_finance__models.yml
unit_tests:
  - name: test_fct_orders_incremental_merge
    description: >
      Verify incremental merge logic: existing rows are updated,
      new rows are inserted, unchanged rows are preserved.
    model: fct_orders

    given:
      # Existing data in the incremental model
      - input: ref('stg_jaffle_shop__orders')
        rows:
          - {order_id: 1, customer_id: 100, status: 'pending', updated_at: '2024-01-01'}
          - {order_id: 3, customer_id: 102, status: 'shipped', updated_at: '2024-01-01'}
      - input: ref('int_customer_payments')
        rows:
          - {order_id: 1, customer_id: 100, total_amount: 50, payment_count: 1}
          - {order_id: 3, customer_id: 102, total_amount: 75, payment_count: 1}

      # Format for existing model data in incremental context
      - input: this
        rows:
          - {order_id: 1, customer_id: 100, total_amount: 50, status: 'pending', updated_at: '2024-01-01'}
          - {order_id: 2, customer_id: 101, total_amount: 100, status: 'shipped', updated_at: '2024-01-01'}

    expect:
      rows:
        # order_id=1: updated in source, should be overwritten
        - {order_id: 1, customer_id: 100, total_amount: 50, status: 'pending'}
        # order_id=2: not in source, should be preserved
        - {order_id: 2, customer_id: 101, total_amount: 100, status: 'shipped'}
        # order_id=3: new in source, should be inserted
        - {order_id: 3, customer_id: 102, total_amount: 75, status: 'shipped'}
```

### Test Severity Configuration

```yaml
# dbt_project.yml — global test severity defaults
tests:
  my_project:
    +severity: warn     # default for all tests

models:
  my_project:
    marts:
      +severity: error  # marts tests are errors

# Override per-test in YAML
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - unique:
              severity: error     # this one must pass
          - not_null:
              severity: error
```

### Great Expectations Integration

For advanced data quality needs beyond dbt native tests:

```bash
# Install the dbt-expectations package
# Add to packages.yml:
packages:
  - package: calogica/dbt_expectations
    version: ">=0.10.0,<0.11.0"
```

```yaml
# Usage in model YAML
models:
  - name: fct_orders
    columns:
      - name: total_amount
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
              row_condition: "status != 'cancelled'"
              strictly: false
      - name: status
        data_tests:
          - dbt_expectations.expect_column_values_to_be_in_set:
              value_set: ['pending', 'shipped', 'delivered', 'cancelled']
      - name: payment_count
        data_tests:
          - dbt_expectations.expect_column_values_to_be_of_type:
              column_type: integer
```

### Source Freshness

```yaml
sources:
  - name: stripe
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
      filter: "DATE(created_at) >= CURRENT_DATE - 7"
    loaded_at_field: _batched_at
```

Run freshness checks:
```bash
dbt source freshness          # All sources
dbt source freshness --select source:stripe.payments  # Specific source
```

---

## Level 3: Semantic Layer

### Overview

The dbt Semantic Layer, powered by MetricFlow, transforms dbt models into a governed metrics platform. Semantic models define entities, dimensions, and measures in YAML — then MetricFlow generates optimized SQL for any metric query across any combination of dimensions.

### Semantic Model

```yaml
# models/marts/finance/_semantic_models.yml
semantic_models:
  - name: orders
    description: Order-level revenue and transaction data.
    model: ref('fct_orders')

    defaults:
      agg_time_dimension: order_date

    entities:
      - name: order
        type: primary
        expr: order_id
      - name: customer
        type: foreign
        expr: customer_id
      - name: location
        type: foreign
        expr: location_id

    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
        expr: order_date
      - name: order_status
        type: categorical
        expr: status
      - name: is_first_order
        type: categorical
        expr: CASE WHEN order_number = 1 THEN TRUE ELSE FALSE END
      - name: order_year
        type: time
        type_params:
          time_granularity: year
        expr: DATE_TRUNC('year', order_date)

    measures:
      - name: revenue
        description: Total gross revenue before discounts.
        agg: sum
        expr: total_amount
        create_metric: true
      - name: order_count
        description: Count of distinct orders.
        agg: count_distinct
        expr: order_id
        create_metric: true
      - name: average_order_value
        description: Average revenue per order.
        agg: average
        expr: total_amount
      - name: total_discounts
        agg: sum
        expr: discount_amount
      - name: unique_customers
        agg: count_distinct
        expr: customer_id
```

### Metrics

```yaml
# models/marts/finance/_metrics.yml
metrics:
  - name: revenue
    description: Total gross revenue across all orders.
    label: Revenue
    type: simple
    type_params:
      measure: revenue

  - name: average_order_value
    description: Average basket value per order.
    label: Avg. Order Value
    type: simple
    type_params:
      measure: average_order_value

  - name: rolling_7d_revenue
    description: Rolling 7-day revenue for trend analysis.
    label: 7-Day Revenue
    type: simple
    type_params:
      measure: revenue
    filter: |
      {{ TimeDimension('order_date', 'day') }} >= DATEADD('day', -7, CURRENT_DATE())

  - name: revenue_growth_pct
    description: Period-over-period revenue growth rate.
    label: Revenue Growth %
    type: derived
    type_params:
      expr: (revenue - revenue_prev_period) / NULLIF(revenue_prev_period, 0) * 100
      metrics:
        - name: revenue
        - name: revenue
          offset_window: 1 period
          alias: revenue_prev_period

  - name: customer_lifetime_value
    description: Average total revenue per unique customer.
    label: Customer LTV
    type: ratio
    type_params:
      numerator: revenue
      denominator: unique_customers

  - name: discount_rate
    description: Discounts as a percentage of gross revenue.
    label: Discount Rate %
    type: ratio
    type_params:
      numerator: total_discounts
      denominator: revenue
```

### Saved Queries

```yaml
# models/marts/finance/_saved_queries.yml
saved_queries:
  - name: monthly_revenue_by_status
    description: Monthly revenue broken down by order status.
    label: Monthly Revenue by Status
    query_params:
      metrics:
        - revenue
      group_by:
        - TimeDimension('order_date', 'month')
        - Dimension('order_status')
      order_by:
        - TimeDimension('order_date', 'month')
      where:
        - "{{ Dimension('order_status') }} != 'cancelled'"

  - name: top_customers_ltv
    description: Top 25 customers by lifetime value.
    label: Top 25 Customer LTV
    query_params:
      metrics:
        - customer_lifetime_value
      group_by:
        - Dimension('customer_name')
      order_by:
        - Metric('customer_lifetime_value', descending=true)
      limit: 25

  - name: weekly_revenue_trend
    description: Weekly revenue trend with 7-day rolling and growth rate.
    label: Weekly Revenue Trend
    query_params:
      metrics:
        - revenue
        - rolling_7d_revenue
        - revenue_growth_pct
      group_by:
        - TimeDimension('order_date', 'week')
      order_by:
        - TimeDimension('order_date', 'week')
```

### Semantic Layer Commands

```bash
# Validate semantic manifests
dbt parse
mf validate-configs          # MetricFlow config validation

# List available entities
mf list entities

# List metrics
mf list metrics

# Query metrics via CLI
mf query --metrics revenue --group-by metric_time__week

# Query with filter
mf query --metrics revenue,order_count \
  --group-by metric_time__month \
  --where "{{ Dimension('order_status') }} = 'shipped'"

# Export query to various formats
mf query --metrics revenue --group-by metric_time__day --explain
```

### MetricFlow Time Dimensions

When querying metrics, MetricFlow automatically creates `metric_time` as the canonical time dimension:

```bash
# Primary time grain from semantic model defaults
mf query --metrics revenue --group-by metric_time

# Specific grain
mf query --metrics revenue --group-by metric_time__day
mf query --metrics revenue --group-by metric_time__week
mf query --metrics revenue --group-by metric_time__month
mf query --metrics revenue --group-by metric_time__quarter
mf query --metrics revenue --group-by metric_time__year
```

---

## Level 4: dbt Mesh — Multi-Project Governance

### Architecture

dbt Mesh enables enterprise-scale data transformation by splitting a monolithic project into coordinated sub-projects that share models through governed interfaces.

```
┌─────────────────────────────────────────────────────────┐
│                    dbt Mesh Architecture                 │
├─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐│
│ Source  │  │ Staging  │  │  Marts   │  │  Downstream  ││
│ Project │→│ Project  │→│  Project │→│   Consumer    ││
│         │  │          │  │          │  │   Projects    ││
├─────────┤  ├──────────┤  ├──────────┤  ├──────────────┤│
│ Raw data│  │ Standard │  │ Business │  │ BI / ML /    ││
│ sources │  │ ized     │  │ logic    │  │ Reverse ETL  ││
│         │  │ models   │  │ models   │  │              ││
└─────────┘  └──────────┘  └──────────┘  └──────────────┘│
     │              │              │              │        │
     └──────────────┴──────────────┴──────────────┘        │
                    Cross-Project Refs                     │
                    Model Contracts                        │
                    Access Controls                        │
                    Versioning                             │
└─────────────────────────────────────────────────────────┘
```

### Cross-Project Refs

In a downstream project's `dependencies.yml`:

```yaml
# dependencies.yml — in the downstream/consumer project
projects:
  - name: finance_marts
    description: Finance department dbt models.

dependencies:
  - project: finance_marts
```

Then reference models from the upstream project using three-part refs:

```sql
-- models/marts/marketing/fct_marketing_attribution.sql
-- Cross-project ref to the finance project's orders model
SELECT
    campaign_id,
    SUM({{ ref('finance_marts', 'fct_orders') }}.total_amount) AS attributed_revenue
FROM {{ ref('stg_marketing__campaigns') }}
LEFT JOIN {{ ref('finance_marts', 'fct_orders') }}
    ON campaigns.order_id = {{ ref('finance_marts', 'fct_orders') }}.order_id
GROUP BY 1
```

### Model Contracts

Model contracts enforce data shape guarantees at the boundary between projects, preventing downstream breakage.

```yaml
# In the upstream project
models:
  - name: fct_orders
    description: Order-level transaction mart.
    config:
      materialized: table
      contract:
        enforced: true
    constraints:
      - type: primary_key
        columns: [order_id]
      - type: foreign_key
        columns: [customer_id]
        expression: ref('dim_customers')
        columns: [customer_id]
    columns:
      - name: order_id
        data_type: integer
        constraints:
          - type: not_null
      - name: customer_id
        data_type: integer
        constraints:
          - type: not_null
      - name: order_date
        data_type: date
        constraints:
          - type: not_null
      - name: total_amount
        data_type: decimal(18,2)
      - name: status
        data_type: varchar
      - name: updated_at
        data_type: timestamp
```

When `contract: {enforced: true}` is set, dbt will:
1. Check that the model's actual columns match the contract definition
2. Add `on_schema_change: fail` behavior for incremental models
3. Fail the build if any constraint violations are detected

### Access Controls (Groups)

```yaml
# dbt_project.yml — group definitions
groups:
  - name: finance
    owner:
      name: Finance Analytics Team
      email: finance-analytics@company.com
      slack: "#fin-data"
    access: private   # private | protected | public

  - name: marketing
    owner:
      name: Marketing Analytics Team
      email: marketing-analytics@company.com
      slack: "#mkt-data"
    access: private
```

```yaml
# In model YAML — assign models to groups
models:
  - name: fct_orders
    group: finance
    access: protected   # Available to other groups via cross-project refs
    config:
      contract:
        enforced: true

  - name: fct_revenue_forecast
    group: finance
    access: private     # Finance team only

  - name: dim_customers
    group: marketing
    access: public      # Available to all projects
```

### Model Versions

When breaking changes are needed, use model versions to provide a migration path:

```yaml
models:
  - name: fct_orders
    latest_version: 2
    versions:
      - v: 2
        columns:
          - name: order_id
            data_type: integer
          - name: customer_id
            data_type: integer
          - name: total_amount
            data_type: decimal(18,2)
          - include: '*'
            exclude: [legacy_status]
          - name: status_code
            data_type: varchar

      - v: 1
        columns:
          - include: '*'
          - name: legacy_status
            data_type: varchar
        deprecation_date: 2026-12-31
```

Downstream projects reference specific versions:
```sql
SELECT * FROM {{ ref('finance_marts', 'fct_orders', version=2) }}
```

### Governance Best Practices

1. **Start with a single project** — Only split into Mesh when you have clear ownership boundaries
2. **Contracts on public/protected models** — Every model with `access: public` or `access: protected` should have an enforced contract
3. **Semantic versioning** — Use model versions (`v: 1`, `v: 2`) with deprecation dates for breaking changes
4. **dbt Mesh gateway** — Use dbt Explorer or dbt Cloud's discovery API for cross-project lineage
5. **Shared macros package** — Publish common macros (date spine, surrogate keys, cross-db utilities) as a shared dbt package
6. **CI/CD for contracts** — Run `dbt build --select state:modified+contract` in CI to validate contract changes

---

## Level 5: Platform & Operations

### CLI Command Reference

```bash
# ─── Core Commands ───
dbt run                          # Build models
dbt run --select tag:finance     # Build tagged models
dbt run --select +fct_orders     # Build upstream + model
dbt run --select fct_orders+     # Build model + downstream
dbt run --select 1_fct_orders+2  # Build model + 2 levels downstream
dbt run --exclude tag:pii        # Exclude tagged models

# ─── Testing ───
dbt test                         # Run all tests
dbt test --select fct_orders     # Tests for specific model
dbt test --select source:*       # Source freshness only
dbt build                        # run + test (preferred in CI)

# ─── Compilation ───
dbt compile                      # Compile all models, check syntax
dbt compile --no-populate-cache  # Fresh compile
dbt parse                        # Parse project structure (fast)

# ─── Documentation ───
dbt docs generate                # Generate docs site
dbt docs serve                   # Serve docs at localhost:8080

# ─── Debugging ───
dbt debug                        # Check connection + config
dbt debug --config-dir           # Show config directory

# ─── Seeds & Snapshots ───
dbt seed                         # Load CSV seeds
dbt seed --select country_codes  # Specific seed
dbt snapshot                     # Run snapshots

# ─── State & Artifacts ───
dbt ls                           # List all resources in DAG
dbt ls --select source:*         # List sources
dbt ls --resource-type model     # List models
dbt ls --output json             # JSON output for automation

# ─── Freshness ───
dbt source freshness             # Check all source freshness
dbt source freshness --select source:stripe.payments

# ─── Graph Operators ───
# +model     : model and all upstream parents
# model+     : model and all downstream children
# @model     : model and all parents + children
# 2+model    : model and 2 levels of upstream
# model+2    : model and 2 levels of downstream
# tag:name   : all resources with tag
# source:*   : all sources
# fqn:path   : fully qualified name match
```

### Performance Optimization

#### Query Performance

```sql
-- ✅ DO: Use ephemeral for chain-of-transformations
{{
    config(materialized = 'ephemeral')
}}

-- ✅ DO: Filter early in incremental models
{% if is_incremental() %}
    WHERE event_date > (SELECT MAX(event_date) FROM {{ this }})
{% endif %}

-- ✅ DO: Cluster/partition on large incremental tables
{{
    config(
        materialized = 'incremental',
        unique_key = 'event_id',
        partition_by = {'field': 'event_date', 'data_type': 'date'},
        cluster_by = ['customer_id', 'event_type']
    )
}}
```

```sql
-- ❌ DON'T: Use SELECT * in production models
SELECT * FROM {{ ref('stg_orders') }}

-- ✅ DO: Explicit column selection
SELECT
    order_id,
    customer_id,
    order_date,
    status,
    total_amount
FROM {{ ref('stg_orders') }}
```

```sql
-- ❌ DON'T: Join before filtering
SELECT * FROM huge_orders o
JOIN huge_customers c ON o.customer_id = c.id
WHERE o.order_date >= '2024-01-01'

-- ✅ DO: Filter inline in CTEs before joining
WITH recent_orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    WHERE order_date >= '2024-01-01'
),
active_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
    WHERE is_active = TRUE
)
SELECT * FROM recent_orders o
JOIN active_customers c ON o.customer_id = c.id
```

#### Warehouse Cost Optimization

| Strategy | When to Use | Cost Impact |
|---|---|---|
| **Views over tables** for staging | Light transforms, no persistence needed | Eliminates storage + compute on full refresh |
| **Ephemeral models** for chain transforms | Intermediate models with 1-2 dependents | Zero materialization cost |
| **Incremental with merge** | Large fact tables, ~daily updates | 10-100x less compute than full rebuild |
| **`on_schema_change: sync_all_columns`** | Avoid full-refresh on column changes | Prevents expensive full rebuilds |
| **`full_refresh: false` config** | Prevent accidental full refreshes | Blocks expensive recomputation |
| **Targeted `--select` in CI** | `dbt build --select state:modified+` | Build only what changed |
| **Defer to production** | `dbt run --defer` in CI | Reuse prod artifacts, build only changed |
| **Warehouse-specific optimizations** | Snowflake clustering, BQ partitioning | Query cost reduction |

```yaml
# dbt_project.yml — avoid full refreshes
models:
  my_project:
    marts:
      +full_refresh: false      # Prevent accidental full refreshes
      +on_schema_change: sync_all_columns  # Schema evolution without rebuild
```

#### Node Selection for CI Efficiency

```bash
# In CI — build only what changed
dbt build --select state:modified+ \
  --defer \
  --state ./target

# Run only new/modified models + their first downstream
dbt build --select state:modified+1

# Run modified models with a specific config
dbt build --select state:modified,config.materialized:incremental
```

### Job Troubleshooting Guide

#### Common Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `Database Error: relation does not exist` | Missing upstream model or source | Run upstream: `dbt run --select +model_name` |
| `Compilation Error: 'ref' is undefined` | Missing dependency | Check ref path, run `dbt deps` |
| `Incremental model: unique_key is required` | Missing config on incremental model | Add `unique_key` to config block |
| `Snapshot target not found` | Snapshot strategy requires target | Ensure `target_schema` is configured |
| `Contract enforcement failed` | Column mismatch with contract | Run `dbt build` to rebuild; update contract if intentional |
| `Source freshness error` | Stale data in source table | Check ELT pipeline, adjust freshness thresholds |
| `dbt_modules or dbt_packages path not found` | Missing packages | Run `dbt deps` |
| `Macro not found` | Missing package or typo | Check package install and macro name |
| `Circular dependency detected` | Models referencing each other | Restructure DAG, use intermediate models |
| `Relation would exceed byte limit` | Model too large for config | Add partitioning, optimize incremental logic |

#### Debugging Workflow

```
1. dbt parse              → Validate syntax and structure first
2. dbt compile            → Check SQL compilation
3. dbt run --select model → Isolate the failing model
4. Check logs for SQL     → Inspect the compiled SQL query
5. Test upstream models   → Verify data quality at source
6. dbt --debug run        → Full debug mode with verbose logging
```

### dbt MCP Server Configuration

For AI-assisted dbt development, configure the dbt MCP server:

```json
// .cursor/mcp.json or claude_desktop_config.json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp-server"],
      "env": {
        "DBT_PROFILES_DIR": "/Users/username/.dbt",
        "DBT_PROJECT_DIR": "/Users/username/projects/my_dbt_project",
        "DBT_TARGET": "dev"
      }
    }
  }
}
```

dbt MCP Server capabilities:
- **dbt_compile**: Compile a model and return compiled SQL
- **dbt_run**: Execute model builds
- **dbt_test**: Run tests for specified models
- **dbt_docs_generate**: Generate project documentation
- **dbt_list**: List project resources and DAG
- **dbt_semantic_query**: Execute MetricFlow queries

### Migration Guide (Older → Modern dbt)

#### Key Migration Steps (v1.5+ → v1.9+)

| From | To | Action |
|---|---|---|
| `dbt_project.yml` config-version: 1 | config-version: 2 | Restructure `dbt_project.yml` |
| `source-paths` | `model-paths` | Rename in `dbt_project.yml` |
| `data-paths` | `seed-paths` | Rename in `dbt_project.yml` |
| Materializations in `dbt_project.yml` | In-model `{{ config() }}` blocks | Prefer inline config for clarity |
| `tests:` key | `data_tests:` key | Rename test definitions |
| `version: 1` schema tests | `data_tests` generic tests | Port to new syntax |
| Manual DAG documentation | dbt Docs + dbt Explorer | Generate automatically |
| Monolithic project | dbt Mesh cross-project refs | Decompose by domain |
| No contracts | Model contracts on public models | Add to public/protected models |
| Manual metric definitions | MetricFlow semantic models | Define semantic models |
| dbt Core | dbt Cloud or dbt Core 1.9+ | Evaluate Cloud for governance features |

```bash
# Upgrade dbt-core and adapters
pip install --upgrade dbt-core dbt-snowflake  # or dbt-bigquery, dbt-postgres, etc.

# Reinstall packages
dbt deps

# Recompile entire project
dbt compile --no-populate-cache

# Run tests to validate
dbt test --select source:*
dbt build --select state:modified+
```

---

## Cross-Domain Best Practices

### YAML DRY Patterns (Doc Blocks)

```yaml
# macros/doc_blocks.yml
version: 2

# Reusable column descriptions
docs:
  - name: pk_column
    description: Primary key. Unique identifier for this record.

  - name: audit_columns
    description: |
      Audit columns populated by the ELT pipeline:
      - `created_at`: Timestamp when the record was first loaded
      - `updated_at`: Timestamp when the record was last modified
      - `_batched_at`: Timestamp of the ELT batch that processed this record

  - name: amount_column
    description: Monetary amount in USD, expressed in dollars (not cents).
```

Usage:
```yaml
columns:
  - name: order_id
    description: '{{ doc("pk_column") }}'
  - name: total_amount
    description: '{{ doc("amount_column") }}'
```

### model-paths and Project Organization

```yaml
# dbt_project.yml
model-paths: ["models"]
models:
  my_project:
    staging:
      +tags: ["staging"]
      +materialized: view
    intermediate:
      +tags: ["intermediate"]
      +materialized: ephemeral
    marts:
      +tags: ["marts"]
      +materialized: table
```

### Tags for Build Selectors

```yaml
models:
  - name: fct_orders
    config:
      tags: ['marts', 'finance', 'daily', 'pii:indirect']
```

```bash
dbt run --select tag:daily          # Run daily models
dbt build --select tag:finance      # Build + test finance models
dbt run --exclude tag:pii:indirect  # Skip PII models
```

### DO / DON'T Summary

| ✅ DO | ❌ DON'T |
|---|---|
| Use `ref()` for all model references | Hardcode table/view names in SQL |
| Use `source()` for raw data references | Query raw tables directly |
| Stage all sources before transformation | Transform raw source data directly |
| Define `unique_key` on incremental models | Use incremental without merge strategy |
| Add descriptions to all models and columns | Ship undocumented models |
| Use contracts for Mesh public models | Expose models without contracts |
| Declare `severity: error` on critical tests | Let critical tests fail silently as warnings |
| Use ephemeral for chain-of-transformations | Materialize every intermediate step |
| Version-breaking changes with deprecation dates | Break downstream consumers silently |
| Run `dbt compile` before `dbt run` in new work | Skip compilation checks |
| Prefer `dbt build` in CI/CD pipelines | Use separate `dbt run` + `dbt test` calls |
| Filter early in CTEs for incremental models | JOIN before filtering |
| Use `on_schema_change: sync_all_columns` | Let schema changes force full refreshes |

---

## References

This skill includes detailed reference guides:

- **[dbt Model Patterns](references/dbt-model-patterns.md)** — Staging, intermediate, and marts patterns; materialization decision matrix; incremental strategies; snapshots; seeds
- **[dbt Mesh Governance](references/dbt-mesh-governance.md)** — Cross-project refs, model contracts, access levels, group management, versioning, CI/CD governance
- **[dbt Semantic Layer](references/dbt-semantic-layer.md)** — MetricFlow patterns, semantic models, metrics dimensions, saved queries, integration patterns

---

## Support Scripts

- **[validate-dbt-project.sh](scripts/validate-dbt-project.sh)** — Validates project structure, compiles models, checks DAG integrity
- **[dbt-test-runner.sh](scripts/dbt-test-runner.sh)** — Runs tests with severity filtering, generates structured test reports

## Evaluation Suite

See **[evals/eval_cases.json](evals/eval_cases.json)** for trigger detection test cases and quality assertions.
