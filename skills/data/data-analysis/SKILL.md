---
name: data-analysis
description: >
  Comprehensive data analysis agent skill for loading, cleaning, exploring,
  visualizing, and reporting on structured datasets. Supports CSV, JSON, Excel,
  and SQL data sources. Produces statistical summaries, correlation matrices,
  time series analysis, regression models, hypothesis tests, and
  publication-quality visualizations.
version: 1.0.0
author: Skill Foundry
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
tags:
  - data-analysis
  - visualization
  - statistics
  - pandas
  - matplotlib
  - seaborn
  - plotly
  - reporting
  - csv
  - json
  - excel
  - sql
---

# Data Analysis Agent Skill

## Overview

A production-grade agent skill for end-to-end data analysis workflows. Use this
skill when you need to load datasets, inspect structure, clean messy data,
perform statistical analyses, create visualizations, or generate structured
reports from tabular data.

## When to Trigger

Activate this skill when the user asks to:

- **Analyze data**: "Analyze this CSV", "What patterns do you see in sales.csv?",
  "Explore this dataset", "Summarize the data in users.json"
- **Create charts/graphs**: "Make a bar chart of…", "Plot revenue over time",
  "Visualize the correlation matrix", "Show me a heatmap of…"
- **Find patterns**: "Find trends in this data", "Is there a correlation between
  X and Y?", "Cluster customers from this data", "Detect anomalies in…"
- **Generate reports**: "Create a report from survey_results.xlsx",
  "Summarize quarterly metrics", "Build a dashboard from sales data"
- **Clean data**: "Clean this messy dataset", "Fix missing values in…",
  "Normalize these columns", "Deduplicate this CSV"
- **Statistical testing**: "Run a t-test on group A vs B", "Check if this
  distribution is normal", "Perform regression analysis", "Calculate
  confidence intervals"

### Near-Miss Negatives — Do NOT Trigger

- Questions about **database schema design** without actual data (e.g.,
  "What columns should my users table have?")
- Questions about **spreadsheet software UI** (e.g., "How do I freeze a row in
  Google Sheets?")
- General **math / statistics theory** questions without a dataset context
  (e.g., "Explain the central limit theorem")
- Pure **SQL query writing** without a data-analysis intent (e.g., "Write a
  query to join three tables" — use a SQL skill instead)
- Questions about **ETL pipeline architecture** or data engineering (e.g.,
  "Design a data ingestion pipeline")

## Step-by-Step Workflow

Follow these phases in order. Skip phases that don't apply (e.g., if data is
already clean) but always **state that you're skipping** and why.

### Phase 1: Load

Determine the data source and load it into a DataFrame.

```
CSV    → pd.read_csv(filepath, ...)
JSON   → pd.read_json(filepath, ...)
Excel  → pd.read_excel(filepath, sheet_name=...)
SQL    → pd.read_sql_query(query, connection)
```

**Checklist:**
- [ ] Identify encoding (try UTF-8, Latin-1, detect automatically)
- [ ] For CSV: inspect delimiter (comma, tab, semicolon), quote character
- [ ] For Excel: list available sheets, load the right one
- [ ] For JSON: handle nested structures with `pd.json_normalize()` if needed
- [ ] For SQL: confirm read-only access, never run destructive queries
- [ ] Load a sample first if the dataset is large (>100k rows)

### Phase 2: Inspect

Understand what you're working with before touching anything.

```python
df.shape          # rows × columns
df.info()         # dtypes, non-null counts, memory
df.head(10)       # first rows
df.tail(5)        # last rows
df.describe()     # numeric summary stats
df.describe(include='object')  # categorical summary
df.dtypes         # column types
df.columns.tolist()  # column names
```

**Checklist:**
- [ ] Report shape: rows × columns
- [ ] List all columns with their dtypes
- [ ] Show summary statistics for numeric columns
- [ ] Show value counts for low-cardinality categorical columns
- [ ] Flag potential issues: wrong dtypes, placeholder values, suspicious zeros

### Phase 3: Clean

Address data quality issues. **Never modify the source file** without prompting
the user first. Work on a copy.

**Common operations:**

| Issue | Approach |
|-------|----------|
| Missing values | `df.isnull().sum()` → decide drop vs impute |
| Wrong dtypes | `pd.to_numeric()`, `pd.to_datetime()`, `astype()` |
| Outliers | IQR method, Z-score, domain-specific thresholds |
| Duplicates | `df.duplicated().sum()` → `df.drop_duplicates()` |
| Inconsistent strings | `.str.strip()`, `.str.lower()`, `.str.replace()` |
| Date parsing | `pd.to_datetime()` with format or infer |
| Normalization | Min-max scaling, Z-score standardization |
| Categorical encoding | One-hot, label encoding for ML prep |

**Rules:**
1. Always work on `df_clean = df.copy()`, never mutate the original in-place
   without explicit user consent.
2. Report every change: "Dropped 47 duplicate rows (2.3% of data)", "Imputed
   missing age values with median (142 cells)".
3. Flag suspicious patterns even if you don't fix them: "Column 'salary' has
   340 zero values — verify if these are legitimate."
4. If a cleaning decision is irreversible, ask first.

### Phase 4: Analyze

Apply appropriate analytical methods based on the question.

**Exploratory Data Analysis (EDA):**
- Univariate: histograms, box plots, value counts per column
- Bivariate: scatter plots, correlation coefficients, grouped means
- Multivariate: pair plots, correlation matrix heatmap, PCA

**Statistical Methods (see `references/statistical-methods.md`):**

| Goal | Method |
|------|--------|
| Compare two groups | Independent t-test, Mann-Whitney U |
| Compare 3+ groups | One-way ANOVA, Kruskal-Wallis |
| Relationship between two continuous vars | Pearson/Spearman correlation |
| Predict continuous outcome | Linear regression, polynomial regression |
| Predict categorical outcome | Logistic regression |
| Check normality | Shapiro-Wilk test, Q-Q plot |
| Detect time trends | Moving averages, decomposition, stationarity tests |
| Find clusters | K-means, hierarchical clustering, DBSCAN |
| Reduce dimensions | PCA, t-SNE (visualization only) |

**Time Series specifics:**
- Set datetime index: `df.set_index('date', inplace=True)`
- Resample: `df.resample('M').mean()`
- Rolling windows: `df['value'].rolling(7).mean()`
- Decomposition: trend, seasonal, residual

### Phase 5: Visualize

Choose the right chart for the data and question. See
`references/visualization-patterns.md` for the full guide.

**Library selection:**
- **Static, publication-quality**: `matplotlib` + `seaborn`
- **Interactive, exploratory**: `plotly`
- **Statistical plots**: `seaborn` (box, violin, pair, joint, heatmap)

**Quick reference:**

| Data Type | Question | Chart |
|-----------|----------|-------|
| Categorical × Numeric | Compare amounts | Bar chart, box plot |
| Numeric × Numeric | Relationship | Scatter plot, line chart |
| Time × Numeric | Trend over time | Line chart, area chart |
| Categorical × Categorical | Cross-tabulation | Heatmap, stacked bar |
| Distribution | Shape of data | Histogram, KDE, violin |
| Part-to-whole | Proportions | Pie chart* (≤5 categories), treemap |
| Correlation matrix | Relationships | Heatmap |
| Rankings | Order | Horizontal bar chart |

*Pie charts: use only when ≤5 categories and values sum to a meaningful whole.
Prefer bar charts otherwise.

**Best practices:**
- Always label axes and add a title
- Use accessible color palettes (avoid red-green for colorblind users)
- Sort bar charts by value unless categories have a natural order
- Add data source and date to chart footnotes
- For interactive charts, include hover tooltips

### Phase 6: Report

Synthesize findings into a structured report.

**Report structure:**
1. **Executive Summary** — 2–3 sentences with the key finding
2. **Data Overview** — source, shape, date range, columns
3. **Data Quality** — issues found, actions taken
4. **Key Findings** — bullet points with numbers, ranked by importance
5. **Visualizations** — inline charts with captions
6. **Statistical Results** — test statistics, p-values, effect sizes
7. **Limitations & Caveats** — data gaps, assumptions, edge cases
8. **Recommendations** — actionable next steps or further analysis

**Output formats:**
- **Quick answer**: plain text summary in chat with key numbers
- **Detailed report**: Markdown document with embedded charts
- **Dashboard**: interactive HTML with plotly (offer if >5 charts)
- **Export**: offer to save cleaned data and charts as files

## Tool-Aware Implementation

### Python Libraries

This skill assumes Python 3.9+ with the following libraries available.
Check availability before use; install missing packages as needed.

```python
# Core
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Interactive
import plotly.express as px
import plotly.graph_objects as go

# Statistics
from scipy import stats
from scipy.stats import norm, ttest_ind, f_oneway, pearsonr, spearmanr

# Optional: machine learning
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression
```

**Matplotlib setup for non-interactive environments:**
```python
import matplotlib
matplotlib.use('Agg')  # headless rendering
```

**Plotly in notebooks vs scripts:**
```python
# In Jupyter/notebook environments:
import plotly.io as pio
pio.renderers.default = 'notebook'

# For saving to files:
fig.write_html('chart.html')
fig.write_image('chart.png')
```

### Platform-Specific Notes

| Platform | Matplotlib backend | File output | Notes |
|----------|-------------------|-------------|-------|
| Claude Code | Agg | write to files | Save charts as PNG/HTML, display from disk |
| Codex | Agg | write to files | Same approach |
| Cursor | Agg or interactive | write to files | Can open HTML in preview |
| Gemini CLI | Agg | write to files | Save charts, display paths |
| OpenClaw | Agg | write to files | Use canvas for HTML output |
| Copilot | Agg | write to files | Standard file-based approach |

## Safety & Guardrails

1. **Never modify source data in-place** — always create a copy or backup before
   transformations. Offer to save cleaned data as a new file.
2. **Flag data quality issues** — don't silently fix problems. Report missing
   values, outliers, and type inconsistencies before and after cleaning.
3. **Statistical honesty** — report p-values and effect sizes, not just
   "significant" or "not significant". Don't p-hack by running multiple tests
   without correction. Mention when sample sizes are too small for reliable
   inference.
4. **Privacy awareness** — if a dataset appears to contain PII (emails, phone
   numbers, names), warn the user and suggest anonymization before analysis.
5. **Large file handling** — for files >100MB, use chunked reading
   (`chunksize` parameter) or sample before full analysis. Warn about memory
   constraints.
6. **SQL safety** — use read-only connections. Never run INSERT, UPDATE,
   DELETE, DROP, or ALTER. Use transactions or connection strings that enforce
   read-only mode.
7. **Deterministic results** — set random seeds for reproducible analysis:
   `np.random.seed(42)`.

## Scripts

### `scripts/validate_dataset.py`

PEP 723 compliant data quality validation script. Run with:

```bash
python scripts/validate_dataset.py path/to/dataset.csv
# or
python scripts/validate_dataset.py path/to/dataset.json
# or
python scripts/validate_dataset.py path/to/dataset.xlsx --sheet "Sheet1"
```

Produces a structured quality report covering missing values, outliers, type
consistency, duplicates, and basic statistics. See script docstring for details.

## References

- **[data-cleaning-guide.md](references/data-cleaning-guide.md)** — Handling
  nulls, outliers, type coercion, deduplication, and normalization patterns.
- **[visualization-patterns.md](references/visualization-patterns.md)** — Chart
  type selection guide, color best practices, accessibility considerations.
- **[statistical-methods.md](references/statistical-methods.md)** — Descriptive
  statistics, hypothesis testing, regression, correlation, confidence intervals,
  and when to use each method.