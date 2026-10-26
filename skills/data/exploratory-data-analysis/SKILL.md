---
name: exploratory-data-analysis
description: Use this skill when exploring an unfamiliar dataset, investigating data quality issues, validating data pipeline outputs before production use, reviewing SQL queries for correctness and performance, or producing a data quality scorecard for a data asset.
---

# Exploratory Data Analysis

## Overview

Systematic framework for exploratory data analysis, data quality validation, and query correctness review. Designed for data analysts, data engineers, and AI agents who need to understand, validate, and document data assets before building on them.

## When to Use

- Exploring an unfamiliar dataset for the first time
- Investigating data quality concerns (wrong totals, unexpected nulls, stale data)
- Validating data pipeline outputs before downstream consumption
- Reviewing SQL or data transformation queries for correctness
- Onboarding a new data source and assessing its quality profile
- Producing a formal data quality scorecard
- Analysing root cause of metric changes (drops, spikes)
- Preparing data for reporting or dashboard consumption

## 1: Exploratory Data Analysis (EDA)

### Load and Profile
Start by understanding the data's shape and basic characteristics:

```python
import pandas as pd
import numpy as np

df = pd.read_parquet('data.parquet')  # or CSV, DB export, etc.

# Basic shape
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Dtypes:\n{df.dtypes}")

# Summary statistics for numeric columns
print(df.describe())
# Summary for categorical
print(df.describe(include='object'))
```

### Null Analysis
Profile missing data systematically:

```python
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df) * 100).round(2)
null_profile = pd.DataFrame({'null_count': null_counts, 'null_pct': null_pct})
null_profile = null_profile[null_profile['null_count'] > 0].sort_values('null_pct', ascending=False)
print(null_profile)
```

**Flag columns above acceptable thresholds:**
| Null Rate | Severity | Action |
|-----------|----------|--------|
| < 1% | Low | Document; review if critical field |
| 1-5% | Medium | Investigate pattern (random vs systematic) |
| 5-20% | High | Flag as data quality issue |
| > 20% | Critical | Block downstream usage until resolved |

### Duplicate Detection

Check for both exact duplicates and key-based duplicates:

```python
# Exact row duplicates
exact_dupes = df.duplicated().sum()
print(f"Exact duplicate rows: {exact_dupes} ({exact_dupes/len(df)*100:.2f}%)")

# Key-based duplicates (if primary key identified)
key_columns = ['id', 'date']  # Adjust based on schema
key_dupes = df.duplicated(subset=key_columns).sum()
print(f"Key-based duplicates: {key_dupes}")
```

### Distribution Analysis

For numeric columns, examine distributions:

```python
import matplotlib.pyplot as plt

numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols[:5]:  # First 5 numeric columns
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    df[col].hist(ax=axes[0], bins=50)
    axes[0].set_title(f'{col} Distribution')
    df.boxplot(column=col, ax=axes[1])
    axes[1].set_title(f'{col} Box Plot')
    plt.tight_layout()
    plt.show()
```

**Check for:**
- Unexpected spikes or gaps
- Long-tail distributions that may need transformation
- Outliers beyond 1.5× IQR or 3σ
- Values that should be bounded but aren't

### Relationship Analysis

```python
# Correlation matrix for numeric columns
corr = df[numeric_cols].corr()
high_corr = corr[(corr.abs() > 0.7) & (corr.abs() < 1.0)]
high_corr_pairs = high_corr.stack().reset_index()
high_corr_pairs = high_corr_pairs[high_corr_pairs['level_0'] < high_corr_pairs['level_1']]
high_corr_pairs = high_corr_pairs.sort_values(0, ascending=False)
print("Highly correlated columns:")
print(high_corr_pairs)
```

## 2: Data Quality Audit

### Freshness Check

Verify the dataset is current:

```python
# Determine the latest record timestamp
latest_ts = df['updated_at'].max()  # Adjust column name
expected_lag = pd.Timedelta(hours=24)  # Adjust based on pipeline SLA
staleness = pd.Timestamp.now() - latest_ts
status = 'OK' if staleness < expected_lag else 'STALE'
print(f"Latest record: {latest_ts}")
print(f"Staleness: {staleness}")
print(f"Expected lag: {expected_lag}")
print(f"Status: {status}")
```

### Value Range Validation

Check columns against expected business rules:

```python
# Example validation rules — adjust for your domain
validation_rules = {
    'age': {'min': 0, 'max': 120},
    'price': {'min': 0.0, 'max': 100000.0},
    'status': {'allowed': ['active', 'inactive', 'pending']},
    'email': {'pattern': r'.+@.+\..+'},
}

for col, rules in validation_rules.items():
    if col not in df.columns:
        print(f"WARNING: Column '{col}' not found in dataset")
        continue
    if 'min' in rules:
        violations = (df[col] < rules['min']).sum()
        if violations:
            print(f"{col}: {violations} values below {rules['min']}")
    if 'allowed' in rules:
        violations = (~df[col].isin(rules['allowed'])).sum()
        if violations:
            print(f"{col}: {violations} values outside allowed set {rules['allowed']}")
```

### Referential Integrity

If foreign key relationships are known:

```python
# Check orphan rate for key relationships
parent_keys = parent_df['id'].unique()
child_keys = df['parent_id'].unique()
orphans = [k for k in child_keys if k not in parent_keys and pd.notna(k)]
orphan_rate = len(orphans) / len(child_keys) * 100
print(f"Orphan rate: {orphan_rate:.2f}% ({len(orphans)} orphans)")
```

### Quality Scorecard

Rate each quality dimension:

| Dimension | Description | Score (1-5) | Evidence |
|-----------|-------------|-------------|----------|
| Completeness | No critical nulls above threshold | | |
| Consistency | Values follow expected formats and ranges | | |
| Uniqueness | Acceptable duplicate rate | | |
| Timeliness | Data within freshness SLA | | |
| Accuracy | Sample checks pass manual verification | | |
| Integrity | Foreign key relationships intact | | |

## 3: Query Validation

When reviewing SQL or data transformation queries:

### Correctness Check
- Does the query answer the stated question?
- Are JOIN conditions correct (no accidental Cartesian products)?
- Are aggregations correct (SUM vs COUNT, HAVING vs WHERE)?
- Are NULLs handled appropriately?
- Are window functions scoped correctly (PARTITION BY, ORDER BY)?
- Does it handle edge cases (empty tables, all-NULL columns)?

### Performance Check
- Are there full table scans on large tables without filters?
- Are JOINs on indexed columns?
- Are subqueries better written as CTEs or temp tables?
- Is DISTINCT masking a structural issue (missing JOIN condition)?
- Are there unnecessary SELECT * queries?
- Are filters applied before joins, not after?

### Security Check
- Is the query parameterized (no string concatenation of user input)?
- Does it expose more data than needed?
- Are permissions appropriate for the query's purpose?

### Query Review Checklist

```markdown
- [ ] Query intent is documented
- [ ] JOINs have explicit join conditions
- [ ] WHERE filters are sargable (index-friendly)
- [ ] Aggregations use the correct function and grouping
- [ ] NULL handling is explicit (COALESCE, IS NULL)
- [ ] Edge cases are handled (empty result sets)
- [ ] No SELECT * on wide tables
- [ ] Parameters are parameterized (no string interpolation)
- [ ] LIMIT pagination includes ORDER BY
- [ ] Query plan reviewed for expensive operations
```

## 4: Root Cause Analysis

When investigating a metric change (drop, spike, flatline):

1. **Verify the data** — Is the pipeline running? Are data sources healthy?
2. **Check the denominator** — Did the population change? (e.g., new segment, bot traffic)
3. **Segment the metric** — Break down by dimension: time, region, user type, platform
4. **Look for correlated changes** — Did a deployment, marketing campaign, or external event coincide?
5. **Check for data quality issues** — Nulls, dupes, integration errors
6. **Produce alongside comparison** — Compare to prior period, same period last year, expected range
7. **Document findings** — Include what was checked, what was found, what remains uncertain

## Assumptions & Dependencies

- This skill assumes access to the data (CSV, Parquet, database, or API)
- Validation rules should be defined by domain experts
- Freshness SLAs should be documented per pipeline
- Quality thresholds should be calibrated to business requirements
- The skill produces diagnostic output — it does not fix data quality issues automatically

## Output

When this skill completes, produce:

1. Data profile summary (shape, columns, types, nulls, duplicates)
2. Quality scorecard with dimension scores and evidence
3. List of data quality findings with severity ratings
4. Query review findings (if applicable)
5. Root cause analysis (if investigating a specific issue)