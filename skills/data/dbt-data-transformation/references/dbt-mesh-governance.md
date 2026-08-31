# dbt Mesh Governance Reference

Enterprise-scale governance patterns for dbt Mesh: cross-project references, model contracts, access controls, group management, model versioning, and CI/CD governance workflows.

---

## What is dbt Mesh?

dbt Mesh is a multi-project architecture that enables independent teams to own, develop, and govern their data models while sharing governed interfaces across the organization. Think of it as **microservices for data transformation**.

```
┌──────────────────────────────────────────────────────────────────┐
│                     dbt Mesh Enterprise Pattern                   │
├─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┤
│  OPERATIONS  │  │   FINANCE    │  │  MARKETING   │  │ PRODUCT    │
│  PROJECT     │  │   PROJECT    │  │  PROJECT     │  │ PROJECT    │
├─────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤
│ Sources     │→ │ fct_orders   │→ │ dim_customer │  │ Sessions   │
│ Raw data    │  │ fct_revenue  │  │ fct_campaigns│  │ Funnels    │
│ ingestion   │  │ dim_accounts │  │ mkt_attrib.  │  │ Features   │
│ monitoring  │  │ fin_forecast │  │ seg_models   │  │ Events     │
├─────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤
│ Team: Data  │  │ Team: Finance│  │ Team: Growth │  │ Team: Prod │
│ Platform    │  │ Analytics    │  │ Marketing    │  │ Analytics  │
│ Access:     │  │ Access:      │  │ Access:      │  │ Access:    │
│  internal   │  │  protected   │  │  protected   │  │  private   │
└─────────────┘  └──────────────┘  └──────────────┘  └────────────┘
        │                │                  │               │
        └────────────────┴──────────────────┴───────────────┘
                  Cross-Project Refs (governed interfaces)
```

---

## Cross-Project References

### Setup: Declare Dependencies

In the downstream consumer project's `dependencies.yml`:

```yaml
# marketing_analytics/dependencies.yml
projects:
  - name: marketing_analytics
    description: Marketing attribution, campaign analysis, and customer segmentation.

dependencies:
  - project: finance_marts
  - project: product_analytics
```

Install:
```bash
dbt deps
```

### Three-Part Ref Syntax

```sql
-- Standard ref (within same project)
SELECT * FROM {{ ref('fct_orders') }}

-- Cross-project ref (to another project)
SELECT * FROM {{ ref('finance_marts', 'fct_orders') }}

-- Version-aware cross-project ref
SELECT * FROM {{ ref('finance_marts', 'fct_orders', version=2) }}

-- With a v: prefix alias
SELECT * FROM {{ ref('finance_marts', 'fct_orders', v=2) }}
```

### Access Resolution

Cross-project refs can only reference models with `access: public` or `access: protected`:

```yaml
# finance_marts model
models:
  - name: fct_revenue_daily
    group: finance
    access: protected          # ✅ Can be referenced by other projects
    config:
      contract:
        enforced: true

  - name: fct_salary_data
    group: finance
    access: private            # ❌ Cannot be referenced by other projects
```

### Best Practices

| Practice | Rationale |
|---|---|
| **One dependency declaration per cross-project consumer** | Clear ownership, explicit dependencies |
| **Pin project versions (dbt Cloud)** | `dependencies: [{project: finance_marts, version: 1.0.0}]` |
| **Use model versions for breaking changes** | Consumers can migrate incrementally |
| **Document cross-project interface** | Treat public/protected models as an API |
| **Tests on consuming side** | Validate data integrity across project boundaries |
| **Cross-project lineage in dbt Explorer** | Full DAG visibility across Mesh projects |

---

## Model Contracts

Model contracts enforce column-level guarantees: data types, constraints, and structure. They prevent downstream breakage when upstream models change.

### Full Contract Example

```yaml
models:
  - name: fct_orders
    description: Order-level transaction mart — governed interface for downstream consumers.
    group: finance
    access: protected
    config:
      materialized: table
      contract:
        enforced: true

    constraints:
      - type: primary_key
        columns: [order_id]
        name: pk_fct_orders
      - type: foreign_key
        columns: [customer_id]
        expression: ref('dim_customers')
        columns: [customer_id]
        name: fk_fct_orders_customers

    columns:
      - name: order_id
        data_type: integer
        description: Primary key. Unique order identifier.
        constraints:
          - type: not_null
          - type: unique

      - name: customer_id
        data_type: integer
        description: Foreign key to dim_customers.
        constraints:
          - type: not_null

      - name: order_date
        data_type: date
        description: Date the order was placed.
        constraints:
          - type: not_null

      - name: status
        data_type: varchar(50)
        description: Current order status.

      - name: total_amount
        data_type: decimal(18, 2)
        description: Total order amount in dollars.

      - name: updated_at
        data_type: timestamp
        description: Row last updated timestamp.
        constraints:
          - type: not_null
```

### Contract Enforcement Behavior

| When | Behavior |
|---|---|
| Column missing from model output | Build fails with contract violation |
| Column has wrong data type | Build fails (type mismatch) |
| Constraint violated at build time | Build fails (constraint error; platform-dependent) |
| New columns added to model but not in contract | Build fails (contract requires all columns declared) |
| Incremental model with `on_schema_change: fail` | Build fails on schema drift |

### Constraint Types

```yaml
constraints:
  # Primary key
  - type: primary_key
    columns: [order_id, line_item_id]

  # Foreign key
  - type: foreign_key
    columns: [customer_id]
    expression: ref('dim_customers')
    columns: [customer_id]

  # Not null
  - type: not_null
    columns: [order_id, customer_id, order_date]

  # Unique
  - type: unique
    columns: [order_id]

  # Check (platform-dependent)
  - type: check
    expression: "total_amount >= 0"
```

### Column Constraints vs Data Tests

| | Constraints | Data Tests |
|---|---|---|
| **Enforcement time** | At build time | At test time |
| **Purpose** | Schema/structure guarantee | Data quality validation |
| **Blocks builds?** | Yes (with enforced contract) | No (separate step) |
| **Use for** | Types, nullability, keys | Business rules, value ranges |
| **Supported by** | Warehouse-native DDL | dbt generic/singular tests |

---

## Access Controls

### Access Levels

```yaml
# dbt_project.yml
models:
  my_project:
    +access: protected          # Default for all models in project

# Per-model override
models:
  - name: stg_source__raw_table
    access: private             # Only this project group can reference
  - name: fct_orders
    access: protected           # Other projects in the account can reference
  - name: dim_customers
    access: public              # Any project in the organization can reference
```

| Access Level | Within Project | Cross-Project | Use Case |
|---|---|---|---|
| **private** | ✅ All refs allowed | ❌ No cross-project access | Internal implementation details, staging models |
| **protected** | ✅ All refs allowed | ✅ Cross-project refs allowed | Core business models, shared dimensions |
| **public** | ✅ All refs allowed | ✅ Cross-project refs allowed | Organization-wide shared models |

### Group Definitions

Groups provide ownership metadata and access boundaries:

```yaml
# dbt_project.yml
groups:
  - name: finance
    owner:
      name: Finance Analytics Team
      email: finance-analytics@company.com
      slack: "#fin-data-eng"
      github: "@finance-data-team"
    access: private

  - name: marketing
    owner:
      name: Marketing Analytics
      email: marketing-analytics@company.com
      slack: "#mkt-analytics"
      github: "@mkt-eng"
    access: private
```

### Model-to-Group Assignment

```yaml
models:
  - name: fct_orders
    group: finance
    access: protected

  - name: dim_customers
    group: finance
    access: public

  - name: stg_finance__gl_entries
    group: finance
    access: private

  - name: fct_campaign_performance
    group: marketing
    access: protected
```

### Ownership and Alerting

Group metadata enables:
- **dbt Explorer** shows which team owns each model
- **Slack notifications** for job failures route to group owner
- **GitHub CODEOWNERS** can auto-assign reviews based on dbt groups

---

## Model Versioning

Model versions enable breaking changes with migration paths for consumers.

### Defining Versions

```yaml
models:
  - name: fct_orders
    latest_version: 2
    config:
      contract:
        enforced: true
    versions:
      # Version 2 (current) — migrated to use status_code instead of legacy_status
      - v: 2
        columns:
          - name: order_id
            data_type: integer
            constraints:
              - type: not_null
          - name: customer_id
            data_type: integer
          - name: order_date
            data_type: date
          - name: total_amount
            data_type: decimal(18,2)
          - name: status_code
            data_type: varchar(20)
            description: Standardized status code (active, completed, cancelled, refunded).

      # Version 1 (deprecated) — legacy column name
      - v: 1
        columns:
          - include: '*'
          - name: legacy_status
            data_type: varchar(50)
            description: Deprecated. Use status_code in v2.
        deprecation_date: 2026-12-31
```

### Version Columns

- Use `include: '*'` to inherit all base columns
- Add `include: '*'` with `exclude` to selectively remove
- Version-specific columns are only in that version's contract

### Cross-Project Version Resolution

```yaml
# Consumer project
dependencies:
  - project: finance_marts
    version: 2.0.0      # Pin to project version
```

```sql
-- Explicit version pin in ref
SELECT * FROM {{ ref('finance_marts', 'fct_orders', version=1) }}  -- still on v1
SELECT * FROM {{ ref('finance_marts', 'fct_orders', version=2) }}  -- migrated to v2
SELECT * FROM {{ ref('finance_marts', 'fct_orders') }}             -- uses latest_version
```

### Version Deprecation Lifecycle

```
v1 (active) ──→ v1 (deprecated, deprecation_date set) ──→ v1 (removed)
                  │                                          │
                  └── Warning shown in dbt docs              └── Build fails for v1 consumers
```

---

## Governance Workflows

### CI/CD Pipeline for Contracts

```yaml
# GitHub Actions example for dbt Mesh CI
name: dbt Mesh CI

on:
  pull_request:
    paths:
      - 'models/**/*.sql'
      - 'models/**/*.yml'

jobs:
  contract-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dbt
        run: pip install dbt-core dbt-snowflake

      - name: Install dependencies
        run: dbt deps

      - name: Build changed models with contract checks
        run: |
          dbt build \
            --select state:modified+ \
            --state ./target \
            --defer \
            --target ci

      - name: Validate contracts on public/protected models
        run: |
          dbt ls --select config.contract.enforced:true --output json > contracts.json
          # Verify all public/protected models have contracts
```

### Contract Coverage Audit

```bash
# Find public/protected models WITHOUT contracts
dbt ls --select access:public,access:protected --exclude config.contract.enforced:true

# Find all models with enforced contracts
dbt ls --select config.contract.enforced:true

# Find models violating contracts in current state
dbt build --select state:modified+config.contract.enforced:true
```

### Governance Checklist

- [ ] All `access: public` models have enforced contracts
- [ ] All `access: protected` models have enforced contracts
- [ ] Every model has a group assignment
- [ ] Group owners have Slack channels configured
- [ ] Model versions have deprecation dates for removed fields
- [ ] Breaking changes use new model versions (not just column rename)
- [ ] Cross-project dependencies are declared in `dependencies.yml`
- [ ] CI runs `dbt build --select state:modified+` with `--defer`
- [ ] dbt Explorer shows full cross-project lineage
- [ ] Freshness checks exist on all cross-project source references

---

## Mesh Migration Guide (Monolith → Mesh)

### When to Split

| Signal | Action |
|---|---|
| Multiple teams editing the same project | Split by team domain |
| Long CI runtimes (>30 min) | Split by domain for parallel builds |
| Unclear model ownership | Assign groups, consider splitting |
| Different SLAs per domain | Split by freshness requirements |
| Breaking changes block other teams | Mesh with versions for safe evolution |
| Single `dbt_project.yml` >500 lines | Decompose into sub-projects |

### Migration Steps

1. **Audit current project** — Identify domain boundaries (finance, marketing, product, etc.)
2. **Identify shared interfaces** — Which models are used across domain boundaries? These become public/protected.
3. **Define contracts** — Add enforced contracts to shared models BEFORE splitting
4. **Split by domain** — Create sub-projects; internal models become `private`
5. **Wire cross-project refs** — Update downstream consumers to use three-part ref syntax
6. **Migrate incrementally** — One domain at a time; keep monolith running until all migrated
7. **Deprecate old references** — Use model versions; set deprecation dates for old monolith refs

### Post-Migration Validation

```bash
# In each consumer project
dbt deps                                # Install cross-project dependencies
dbt parse                               # Validate refs resolve correctly
dbt compile --no-populate-cache          # Full compilation check
dbt test --select source:*              # Validate source references
dbt build --select state:modified+       # Changed-model build + test

# Cross-project lineage
dbt docs generate                       # Generate docs with cross-project DAG
dbt ls --output json > manifest.json    # Export for lineage analysis
```

---

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Better Approach |
|---|---|
| No contracts on cross-project models | All public/protected models have enforced contracts |
| Breaking column rename without version | New model version with deprecation of old column |
| Every model is `access: public` | Default to `private` or `protected`; public only when truly shared |
| Circular cross-project dependencies | Refactor to avoid A→B→A cycles |
| One team owns the Mesh architecture | Each domain team owns their project |
| Cross-project refs without freshness checks | Freshness checks on source tables upstream |
| Monolith split without migration period | Run old and new projects in parallel for overlap |