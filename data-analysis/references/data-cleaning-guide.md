# Data Cleaning Guide

## Principles

1. **Never modify source data in-place** — always work on a copy.
2. **Report every change** — document what was removed, imputed, or transformed
   with counts and percentages.
3. **Flag, don't silently fix** — suspicious patterns should be raised even if
   you don't act on them.
4. **Ask before irreversible decisions** — dropping rows, removing columns, or
   imputing critical values warrants user confirmation.

## Missing Values

### Detection

```python
# Count missing values per column
df.isnull().sum()

# Percentage missing per column
(df.isnull().sum() / len(df) * 100).round(2)

# Visualize missingness
import missingno as msno
msno.matrix(df)  # missing value matrix
msno.heatmap(df)  # correlation of missingness
```

### Decision Framework

| Missing % | Recommendation |
|-----------|---------------|
| < 5% | Drop rows or impute (mean/median/mode) |
| 5–20% | Impute with method appropriate to data type |
| 20–50% | Consider advanced imputation or treat as category |
| > 50% | Flag the column; consider dropping it entirely |
| > 80% | Drop the column — too sparse to be useful |

### Imputation Methods

**Numeric columns:**
- **Mean** — for normally distributed data without outliers
- **Median** — for skewed data or data with outliers
- **Mode** — rarely appropriate for continuous data
- **Forward/backward fill** — for time series with natural ordering
- **Interpolation** — for time series with gaps
- **KNN imputation** — for datasets where similar rows should have similar values
- **Model-based (regression)** — for critical variables when accuracy matters

```python
# Simple imputation
df['age'].fillna(df['age'].median(), inplace=True)
df['category'].fillna('Unknown', inplace=True)

# Time series forward fill
df['value'].fillna(method='ffill', inplace=True)

# Interpolation for time series gaps
df['temperature'] = df['temperature'].interpolate(method='linear')
```

**Categorical columns:**
- **Mode** — most frequent value
- **"Unknown" or "Missing"** — explicit missing category (preserves information)
- **Model-based prediction** — when the missing category is important

### Missingness Types

- **MCAR (Missing Completely At Random)**: No pattern — safe to drop or impute.
- **MAR (Missing At Random)**: Missingness depends on observed data — use those
  variables for imputation.
- **MNAR (Missing Not At Random)**: Missingness depends on the missing value
  itself — this is a problem. Flag it and investigate.

## Outlier Detection & Treatment

### Detection Methods

**1. IQR Method (robust, non-parametric):**
```python
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = df[(df['column'] < lower) | (df['column'] > upper)]
```

**2. Z-Score Method (assumes normality):**
```python
from scipy import stats
z_scores = np.abs(stats.zscore(df['column'].dropna()))
outliers = df[z_scores > 3]  # threshold of 3 standard deviations
```

**3. Modified Z-Score (robust to outliers):**
```python
median = df['column'].median()
mad = np.median(np.abs(df['column'] - median))
modified_z = 0.6745 * (df['column'] - median) / mad
outliers = df[np.abs(modified_z) > 3.5]
```

### Treatment Options

| Approach | When to Use | Trade-off |
|----------|------------|-----------|
| **Remove** | Outliers are errors or irrelevant | Loses data; only if confident they're wrong |
| **Cap (Winsorize)** | Keep but limit extreme values | Preserves sample size, reduces impact |
| **Transform (log, sqrt)** | Right-skewed data with legitimate extremes | Changes interpretation of variable |
| **Keep** | Outliers are valid and interesting | May distort statistical models |
| **Separate analysis** | Outliers are a distinct subgroup | More work, more insight |

```python
# Winsorize at 1st and 99th percentile
from scipy.stats import mstats
df['column_winsorized'] = mstats.winsorize(df['column'], limits=[0.01, 0.01])

# Log transform for right-skewed data
df['column_log'] = np.log1p(df['column'])  # log(1+x) handles zeros
```

## Type Coercion

### Common Issues and Fixes

```python
# String numbers with commas, currency symbols
df['price'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)

# Mixed-type columns
df['mixed_col'] = pd.to_numeric(df['mixed_col'], errors='coerce')

# Date strings in various formats
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)

# Object columns that should be categorical
df['category'] = df['category'].astype('category')

# Boolean-like columns
df['flag'] = df['flag'].map({'yes': True, 'no': False, 'Y': True, 'N': False})
```

### Type Detection Heuristics

```python
def suggest_dtype(series):
    """Suggest the correct dtype for a pandas Series."""
    non_null = series.dropna()
    if len(non_null) == 0:
        return 'empty'

    # Check if all values are numeric
    try:
        pd.to_numeric(non_null)
        return 'numeric'
    except:
        pass

    # Check if values are dates
    try:
        pd.to_datetime(non_null.head(100))
        # If >80% parse, probably dates
        parsed = pd.to_datetime(non_null.head(100), errors='coerce')
        if parsed.notna().sum() / 100 > 0.8:
            return 'datetime'
    except:
        pass

    # Check cardinality for categorical
    unique_ratio = non_null.nunique() / len(non_null)
    if unique_ratio < 0.1:
        return 'categorical'

    return 'string'
```

## Deduplication

### Exact Duplicates

```python
# Count duplicates
n_dupes = df.duplicated().sum()
print(f"Found {n_dupes} exact duplicate rows ({n_dupes/len(df)*100:.2f}%)")

# Inspect before dropping
duplicates = df[df.duplicated(keep=False)]

# Drop duplicates, keep first occurrence
df_clean = df.drop_duplicates(keep='first')
```

### Fuzzy / Near-Duplicates

For text fields (names, addresses), exact matching may miss duplicates:

```python
# Check for near-duplicate names
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

# For larger datasets, use fuzzywuzzy or rapidfuzz
# pip install rapidfuzz
from rapidfuzz import fuzz
```

### Subset Duplicates

```python
# Check duplicates based on specific columns
df.duplicated(subset=['email']).sum()

# Drop based on subset, keep most recent
df.sort_values('created_at').drop_duplicates(subset=['user_id'], keep='last')
```

## Normalization & Scaling

When preparing data for machine learning models:

| Method | Formula | When to Use |
|--------|---------|-------------|
| **Min-Max** | `(x - min) / (max - min)` | Neural networks, bounded data |
| **Z-Score (Standard)** | `(x - mean) / std` | PCA, linear models, when data is ~normal |
| **Robust** | `(x - median) / IQR` | Data with outliers |
| **Log** | `log(x)` or `log(1+x)` | Heavy right skew |
| **Box-Cox** | `(x^λ - 1) / λ` | When you need normality |

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[numeric_cols]), columns=numeric_cols)
```

**Important:** Always fit scalers on training data only, then transform test data.

## Data Consistency Checks

Run these after every cleaning step:

```python
# Shape sanity check
assert len(df_clean) <= len(df_raw), "Cleaned data has MORE rows than raw?"

# Value range checks
assert (df['age'] >= 0).all(), "Negative ages detected"
assert (df['price'] >= 0).all(), "Negative prices detected"

# Referential integrity (if multiple related DataFrames)
# assert set(df_orders['customer_id']).issubset(set(df_customers['id']))

# Date range sanity
assert df['date'].max() <= pd.Timestamp.today(), "Future dates detected"
```

## Data Privacy

If a dataset may contain PII, flag it before analysis:

```python
import re

pii_patterns = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
}

for col in df.columns:
    for pii_type, pattern in pii_patterns.items():
        matches = df[col].astype(str).str.match(pattern).sum()
        if matches > 0:
            print(f"⚠️  Column '{col}' may contain {pii_type} ({matches} matches)")
```

**If PII is found:**
1. Warn the user immediately
2. Suggest anonymization: hashing, masking, or column removal
3. Do not proceed with analysis on identifiable data without explicit permission