# dbt Semantic Layer Reference

Comprehensive reference for MetricFlow-powered semantic modeling: semantic models, metrics, dimensions, measures, saved queries, and integration patterns.

---

## Architecture Overview

The dbt Semantic Layer, powered by MetricFlow, provides a governed metrics platform built on top of dbt models. It separates metric definitions from SQL, enabling consistent metrics across all consumption tools.

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                         │
│  Tableau │ Looker │ Power BI │ Hex │ Custom Apps │ AI/LLM   │
└────────────────────────┬────────────────────────────────────┘
                         │   dbt Semantic Layer APIs
                         │   (REST, JDBC, GraphQL)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    METRICFLOW ENGINE                         │
│  MetricFlow Server │ Query Optimization │ Join Resolution   │
└────────────────────────┬────────────────────────────────────┘
                         │   YAML configs
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SEMANTIC MODELS + METRICS                 │
│  Entities │ Dimensions │ Measures │ Metrics │ Saved Queries  │
└────────────────────────┬────────────────────────────────────┘
                         │   ref() references
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DBT MODELS                                │
│  fct_orders │ dim_customers │ fct_revenue │ dim_products     │
└─────────────────────────────────────────────────────────────┘
```

---

## Semantic Model Definition

A semantic model describes a dbt model in MetricFlow terms: entities, dimensions, and measures.

### Complete Semantic Model

```yaml
semantic_models:
  - name: orders
    description: |
      Order transaction data. One row per order placed.
      Primary semantic model for revenue, order volume, and customer purchase metrics.
    model: ref('fct_orders')

    defaults:
      agg_time_dimension: order_date

    entities:
      - name: order
        description: Individual order transaction.
        type: primary
        expr: order_id

      - name: customer
        description: Customer who placed the order.
        type: foreign
        expr: customer_id

      - name: product
        description: Product purchased (via order items join).
        type: foreign
        expr: product_id

    dimensions:
      # ─── Time Dimensions ───
      - name: order_date
        description: Date the order was placed.
        type: time
        type_params:
          time_granularity: day
        expr: order_date

      - name: order_month
        description: Month the order was placed.
        type: time
        type_params:
          time_granularity: month
        expr: DATE_TRUNC('month', order_date)

      - name: order_year
        description: Year the order was placed.
        type: time
        type_params:
          time_granularity: year
        expr: DATE_TRUNC('year', order_date)

      # ─── Categorical Dimensions ───
      - name: order_status
        description: Current status of the order.
        type: categorical
        expr: status

      - name: payment_method
        description: Method used for payment.
        type: categorical
        expr: payment_type

      - name: is_new_customer
        description: Whether this is the customer's first order.
        type: categorical
        expr: CASE WHEN customer_order_number = 1 THEN TRUE ELSE FALSE END

      - name: customer_segment
        description: Customer value segment based on LTV.
        type: categorical
        expr: customer_segment

      - name: country
        description: Shipping country for the order.
        type: categorical
        expr: shipping_country

    measures:
      # ─── Sum Measures ───
      - name: revenue
        description: Total gross revenue before discounts and refunds.
        agg: sum
        expr: total_amount
        create_metric: true

      - name: net_revenue
        description: Revenue net of discounts and refunds.
        agg: sum
        expr: net_amount
        create_metric: true

      - name: discount_amount
        description: Total discount value applied to orders.
        agg: sum
        expr: discount_amount

      - name: tax_amount
        description: Total tax collected.
        agg: sum
        expr: tax_amount

      # ─── Count Measures ───
      - name: order_count
        description: Count of distinct orders.
        agg: count_distinct
        expr: order_id
        create_metric: true

      - name: unique_customers
        description: Count of unique customers placing orders.
        agg: count_distinct
        expr: customer_id
        create_metric: true

      # ─── Average Measures ───
      - name: average_order_value
        description: Average gross revenue per order.
        agg: average
        expr: total_amount
        create_metric: true

      - name: items_per_order
        description: Average line items per order.
        agg: average
        expr: line_item_count

      # ─── Min/Max Measures ───
      - name: max_order_value
        description: Maximum single order value.
        agg: max
        expr: total_amount

      - name: min_order_value
        description: Minimum single order value.
        agg: min
        expr: total_amount
```

### Entity Types

| Entity Type | Description | When to Use |
|---|---|---|
| **primary** | The main entity this model describes | The model's grain (e.g., `order_id` in an orders model) |
| **foreign** | An entity that links to another semantic model | Join keys to other semantic models |
| **unique** | Entity with a unique constraint | When you need distinct counting (e.g., unique customers) |
| **natural** | Domain-specific entity | Custom entity relationships |

### Dimension Types

| Type | `type_params` | Use Case |
|---|---|---|
| **time** | `time_granularity: day\|week\|month\|quarter\|year` | Dates, timestamps for aggregation |
| **categorical** | None (default) | Status codes, segments, names |
| **continuous** | None | Numeric ranges (price ranges, age groups) |

### Measure Aggregation Types

| `agg` | Description | SQL Equivalent |
|---|---|---|
| `sum` | Sum of values | `SUM(expr)` |
| `count` | Row count | `COUNT(*)` |
| `count_distinct` | Distinct count | `COUNT(DISTINCT expr)` |
| `average` | Mean value | `AVG(expr)` |
| `min` | Minimum value | `MIN(expr)` |
| `max` | Maximum value | `MAX(expr)` |
| `median` | Median value | `PERCENTILE_CONT(0.5)` |
| `percentile` | Custom percentile | `PERCENTILE_CONT(pct)` |
| `sum_boolean` | Sum of boolean (count of true) | `SUM(CASE WHEN expr THEN 1 ELSE 0 END)` |
| `string` | String value (custom) | Custom SQL |

---

## Metrics

Metrics define how measures are combined, filtered, and derived.

### Simple Metrics

Direct measure with optional filters, aliases, or time constraints.

```yaml
metrics:
  - name: revenue
    description: Total gross revenue across all orders.
    label: Revenue
    type: simple
    type_params:
      measure: revenue
    filter: |
      {{ Dimension('order_status') }} != 'cancelled'
    config:
      meta:
        display_currency: USD
        number_format: "#,##0.00"
```

### Ratio Metrics

A numerator divided by a denominator — both from the same or different measures.

```yaml
metrics:
  - name: revenue_per_customer
    description: Average revenue generated per unique customer.
    label: Rev / Customer
    type: ratio
    type_params:
      numerator: revenue
      denominator: unique_customers

  - name: conversion_rate
    description: Percentage of customers who completed a purchase.
    label: Conversion Rate
    type: ratio
    type_params:
      numerator: purchased_customers
      denominator: total_customers
      numerator_filter: |
        {{ Dimension('order_status') }} = 'delivered'

  - name: gross_margin
    description: Gross margin as percentage of revenue.
    label: Gross Margin
    type: ratio
    type_params:
      numerator: revenue
      denominator: cogs
      numerator_where:
        - "{{ Dimension('order_status') }} != 'cancelled'"
```

### Derived Metrics

Mathematical expressions combining multiple metrics.

```yaml
metrics:
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

  - name: revenue_target_pct
    description: Revenue as percentage of target.
    label: Revenue vs Target %
    type: derived
    type_params:
      expr: revenue / NULLIF(revenue_target, 0) * 100
      metrics:
        - name: revenue
        - name: revenue_target

  - name: net_promoter_score
    description: Net Promoter Score (promoters - detractors) / total * 100.
    label: NPS
    type: derived
    type_params:
      expr: ((promoter_count - detractor_count) / NULLIF(total_respondents, 0)) * 100
      metrics:
        - name: promoter_count
        - name: detractor_count
        - name: total_respondents
```

### Cumulative Metrics

Running totals over time.

```yaml
metrics:
  - name: cumulative_revenue
    description: Running total of revenue from beginning to end of period.
    label: Cumulative Revenue
    type: cumulative
    type_params:
      measure: revenue
      window: 1 year
```

### Conversion Metrics

For funnel/step-conversion analysis.

```yaml
metrics:
  - name: checkout_to_purchase_rate
    description: Conversion from checkout start to completed purchase.
    label: Checkout → Purchase %
    type: conversion
    type_params:
      base_measure:
        name: unique_checkouts
        fill_nulls_with: 0
      conversion_measure:
        name: unique_purchases
```

---

## MetricFlow `metric_time`

MetricFlow automatically generates `metric_time` as a unified time dimension across all time-aware semantic models.

### How It Works

When a semantic model has a `defaults.agg_time_dimension`, MetricFlow uses that dimension as `metric_time` for metric queries:

```yaml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_date     # ← This becomes metric_time
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
```

When querying:
```bash
# All equivalent (use first matching agg_time_dimension)
mf query --metrics revenue --group-by metric_time__day
mf query --metrics revenue --group-by metric_time__month
mf query --metrics revenue --group-by metric_time__quarter
mf query --metrics revenue --group-by metric_time__year
```

### Multi-Model metric_time

When a query involves multiple semantic models with different time dimensions, MetricFlow resolves the join intelligently using `metric_time` as the canonical time axis.

---

## Saved Queries

Saved queries define reusable metric queries for dashboards, embedded analytics, or API consumers.

```yaml
saved_queries:
  - name: monthly_revenue_trend
    description: Monthly revenue with growth rate for executive dashboards.
    label: Monthly Revenue Trend
    query_params:
      metrics:
        - revenue
        - revenue_growth_pct
        - average_order_value
      group_by:
        - TimeDimension('order_date', 'month')
      order_by:
        - TimeDimension('order_date', 'month')
      where:
        - "{{ Dimension('order_status') }} != 'cancelled'"

  - name: revenue_by_segment_and_country
    description: Revenue breakdown by customer segment and shipping country.
    label: Revenue by Segment & Country
    query_params:
      metrics:
        - revenue
        - order_count
        - revenue_per_customer
      group_by:
        - Dimension('customer_segment')
        - Dimension('country')
      order_by:
        - Metric('revenue', descending=true)
      limit: 50

  - name: top_25_customers
    description: Top customers ranked by lifetime value.
    label: Top 25 Customers
    query_params:
      metrics:
        - revenue
        - order_count
        - average_order_value
      group_by:
        - Dimension('customer_name')
      order_by:
        - Metric('revenue', descending=true)
      limit: 25

  - name: daily_kpi_dashboard
    description: Daily KPI snapshot for company-wide dashboard.
    label: Daily KPIs
    query_params:
      metrics:
        - revenue
        - net_revenue
        - order_count
        - average_order_value
        - unique_customers
        - revenue_growth_pct
        - revenue_per_customer
        - conversion_rate
      group_by:
        - TimeDimension('order_date', 'day')
      where:
        - "{{ TimeDimension('order_date', 'day') }} >= CURRENT_DATE - 30"
      order_by:
        - TimeDimension('order_date', 'day')

  - name: weekly_retention_analysis
    description: Weekly cohort retention for product analytics.
    label: Weekly Retention
    query_params:
      metrics:
        - returning_customers
        - new_customers
      group_by:
        - TimeDimension('order_date', 'week')
      order_by:
        - TimeDimension('order_date', 'week')

  - name: discount_impact_analysis
    description: Revenue vs discount analysis by order status.
    label: Discount Impact
    query_params:
      metrics:
        - revenue
        - discount_amount
        - discount_rate
      group_by:
        - Dimension('order_status')
        - TimeDimension('order_date', 'month')
      order_by:
        - TimeDimension('order_date', 'month')
```

---

## Semantic Layer Commands

### MetricFlow CLI

```bash
# Validate configs
mf validate-configs

# List all semantic objects
mf list entities
mf list dimensions --semantic-model orders
mf list measures --semantic-model orders
mf list metrics
mf list saved-queries

# Query metrics
mf query --metrics revenue --group-by metric_time__month

# Query multiple metrics
mf query --metrics revenue,order_count,average_order_value \
  --group-by metric_time__week

# Query with categorical dimension
mf query --metrics revenue \
  --group-by Dimension('customer_segment') \
  --group-by metric_time__month

# Query with filter
mf query --metrics revenue,order_count \
  --group-by metric_time__day \
  --where "{{ Dimension('order_status') }} = 'delivered'"

# Query with date range
mf query --metrics revenue \
  --group-by metric_time__day \
  --where "{{ TimeDimension('order_date', 'day') }} BETWEEN '2024-01-01' AND '2024-12-31'"

# Query with ordering and limit
mf query --metrics revenue \
  --group-by Dimension('country') \
  --order-by Metric('revenue', descending=true) \
  --limit 10

# Explain query (show generated SQL)
mf query --metrics revenue --group-by metric_time__month --explain

# Export results
mf query --metrics revenue --group-by metric_time__month --output csv > report.csv
mf query --metrics revenue --group-by metric_time__month --output json
```

### dbt Semantic Layer Commands

```bash
# Generate semantic manifest
dbt parse    # generates semantic_manifest.json

# List semantic layer resources
dbt ls --resource-type semantic_model
dbt ls --resource-type metric
dbt ls --resource-type saved_query
dbt ls --resource-type exposure
```

---

## Multi-Model Semantic Design

### Joining Semantic Models

When a metric query requires dimensions from multiple semantic models, MetricFlow resolves the join automatically using entity relationships:

```yaml
semantic_models:
  - name: orders
    entities:
      - name: customer
        type: foreign
        expr: customer_id
    measures:
      - name: revenue
        agg: sum
        expr: total_amount

  - name: customers
    entities:
      - name: customer
        type: primary
        expr: customer_id
    dimensions:
      - name: customer_name
        type: categorical
        expr: full_name
      - name: customer_country
        type: categorical
        expr: country
```

Now you can query `revenue` grouped by `customer_country` and MetricFlow automatically joins the `orders` and `customers` semantic models:

```bash
mf query --metrics revenue --group-by Dimension('customer_country')
```

### Multiple Granularities

```yaml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_date
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: order_week
        type: time
        type_params:
          time_granularity: week
        expr: DATE_TRUNC('week', order_date)
    measures:
      - name: revenue
        agg: sum

  - name: order_items
    defaults:
      agg_time_dimension: created_date
    entities:
      - name: order
        type: foreign
        expr: order_id
    dimensions:
      - name: created_date
        type: time
        type_params:
          time_granularity: day
    measures:
      - name: total_quantity
        agg: sum
        expr: quantity
```

---

## Config & Metadata

### Metric Metadata

```yaml
metrics:
  - name: revenue
    config:
      meta:
        display_currency: USD
        number_format: "#,##0.00"
        category: "Finance"
        sensitivity: "Public"
        sla: "Daily by 08:00 UTC"
```

### Exposures

Link metrics to dashboards, reports, and downstream consumers:

```yaml
exposures:
  - name: executive_dashboard
    type: dashboard
    description: Daily revenue and growth metrics for executive leadership.
    url: https://looker.company.com/dashboards/exec
    maturity: high
    owner:
      name: Finance Analytics
      email: finance-analytics@company.com
    depends_on:
      - ref('fct_orders')
      - ref('dim_customers')
      - metric('revenue')
      - metric('revenue_growth_pct')
      - metric('average_order_value')
    meta:
      tool: Looker
      refresh_cadence: daily
```

---

## Validation and Testing

```bash
# Validate semantic configs
mf validate-configs

# Test metric queries return expected structure
mf query --metrics revenue --group-by metric_time__month --limit 1

# Verify all metrics compile
for metric in $(mf list metrics --output json | jq -r '.[].name'); do
    echo "Validating: $metric"
    mf query --metrics "$metric" --group-by metric_time__day --limit 1 --quiet || echo "FAILED: $metric"
done
```

---

## Best Practices

| Practice | Rationale |
|---|---|
| **One semantic model per grain** | Each semantic model should represent one distinct entity grain |
| **Use `create_metric: true` for key measures** | Auto-generate metrics for common measures |
| **Add descriptions to all objects** | Descriptions appear in downstream BI tools |
| **Use `defaults.agg_time_dimension`** | Enables `metric_time` convenience grouping |
| **Validate with `--explain`** | Inspect generated SQL before trusting results |
| **Set number formatting in `config.meta`** | Consistent formatting across BI tools |
| **Use `filter` for reusable metric constraints** | Avoid repeating filters in every saved query |
| **Version metrics with `label` changes** | Use labels for display names, `name` for stable references |
| **Test metric queries as part of CI** | Catch metric breakage before it reaches dashboards |
| **Document the semantic DAG** | Show how metrics flow from models → semantic models → metrics → saved queries |

---

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Better Approach |
|---|---|
| One semantic model for the entire DAG | One semantic model per distinct grain/entity |
| All measures as metrics | Only promote frequently-queried measures to metrics |
| Business logic in MetricFlow `expr` | Business logic belongs in dbt models; MetricFlow is for aggregation |
| No time dimension defaults | Always set `defaults.agg_time_dimension` |
| Missing `description` on metrics | Every metric should have a business description |
| Redundant semantic models | If two models share the same grain, they may be the same semantic model |
| Hardcoded date filters in metrics | Use MetricFlow filter params or `TimeDimension` for dynamic filtering |
| No validation in CI | Run `mf validate-configs` and sample queries in CI |