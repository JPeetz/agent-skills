# Statistical Methods

A practical guide to statistical approaches for data analysis. Covers what to
use, when to use it, and how to interpret results.

## Before You Start

### Check Your Assumptions

Most statistical tests make assumptions. Violating them can invalidate results.

| Test Family | Key Assumptions |
|-------------|----------------|
| Parametric (t-test, ANOVA, Pearson r) | Normality, homogeneity of variance, independence |
| Non-parametric (Mann-Whitney, Spearman ρ) | Independence, similar distribution shapes |
| Regression | Linearity, independence, homoscedasticity, normality of residuals |
| χ² (chi-square) | Expected frequencies ≥5 per cell, independence |

### Set Your Significance Level

Default to α = 0.05, but consider the context:
- **α = 0.01** for high-stakes decisions (medical, safety)
- **α = 0.05** for general business/research
- **α = 0.10** for exploratory analysis (clearly label as exploratory)

**Always report exact p-values**, not just "p < 0.05". "p = 0.049" and
"p = 0.001" are very different strengths of evidence.

## Descriptive Statistics

### Measures of Central Tendency

```python
import pandas as pd
import numpy as np

df['column'].mean()    # arithmetic mean — use for symmetric data
df['column'].median()  # median — use for skewed data or with outliers
df['column'].mode()    # mode — most frequent value(s)
```

| Measure | Best for | Sensitive to outliers? |
|---------|----------|----------------------|
| Mean | Symmetric, normal-like data | Yes |
| Median | Skewed data, income, response times | No |
| Mode | Categorical or discrete data | No |
| Trimmed mean | Compromise; trim top/bottom N% | Somewhat |

### Measures of Spread

```python
df['column'].std()                     # standard deviation
df['column'].var()                     # variance
df['column'].quantile(0.75) - df['column'].quantile(0.25)  # IQR
df['column'].max() - df['column'].min()  # range (fragile)
from scipy.stats import median_abs_deviation
median_abs_deviation(df['column'])     # MAD — robust alternative to std
```

### Distribution Shape

```python
df['column'].skew()      # skewness: >0 right-tailed, <0 left-tailed, 0 symmetric
df['column'].kurtosis()  # kurtosis: >0 heavy-tailed, <0 light-tailed (vs normal)

# Visual assessment
from scipy import stats
stats.probplot(df['column'].dropna(), dist="norm", plot=plt)  # Q-Q plot
```

## Hypothesis Testing

### Comparing Two Groups

#### Independent T-Test (parametric)

**When:** Comparing means of two independent groups. Data should be approximately
normal with similar variances.

```python
from scipy.stats import ttest_ind, mannwhitneyu

# Assumption check: normality
from scipy.stats import shapiro
stat, p = shapiro(group_a)
# p > 0.05 → data is consistent with normality

# Assumption check: equal variance
from scipy.stats import levene
stat, p = levene(group_a, group_b)
# p > 0.05 → variances are similar; use equal_var=True
# p ≤ 0.05 → variances differ; use equal_var=False (Welch's t-test)

# Run the test
stat, p = ttest_ind(group_a, group_b, equal_var=True)

# Report: t(df) = stat, p = p_value
# Effect size: Cohen's d
d = (group_a.mean() - group_b.mean()) / np.sqrt((group_a.std()**2 + group_b.std()**2) / 2)
```

**Interpreting Cohen's d:**
- |d| ≈ 0.2: small effect
- |d| ≈ 0.5: medium effect
- |d| ≈ 0.8: large effect

#### Mann-Whitney U Test (non-parametric)

**When:** Comparing two independent groups when data is ordinal or violates
normality. Tests whether one group tends to have larger values.

```python
stat, p = mannwhitneyu(group_a, group_b, alternative='two-sided')

# Effect size: rank-biserial correlation
# r = 1 - (2*U) / (n1*n2) — ranges from -1 to 1
n1, n2 = len(group_a), len(group_b)
r = 1 - (2 * stat) / (n1 * n2)
```

### Comparing Three or More Groups

#### One-Way ANOVA (parametric)

```python
from scipy.stats import f_oneway

stat, p = f_oneway(group_a, group_b, group_c)
# Significant ANOVA → run post-hoc test to find which groups differ
```

#### Post-Hoc: Tukey HSD

```python
# For pairwise comparisons after significant ANOVA
from statsmodels.stats.multicomp import pairwise_tukeyhsd

all_values = np.concatenate([group_a, group_b, group_c])
all_labels = (['A'] * len(group_a) + ['B'] * len(group_b) + ['C'] * len(group_c))
tukey = pairwise_tukeyhsd(all_values, all_labels, alpha=0.05)
print(tukey)
```

#### Kruskal-Wallis (non-parametric)

```python
from scipy.stats import kruskal

stat, p = kruskal(group_a, group_b, group_c)
# Non-parametric alternative to one-way ANOVA
```

### Categorical Data

#### Chi-Square Test of Independence

```python
from scipy.stats import chi2_contingency

# Create contingency table
contingency = pd.crosstab(df['category_a'], df['category_b'])

chi2, p, dof, expected = chi2_contingency(contingency)

# Cramér's V for effect size
n = contingency.sum().sum()
min_dim = min(contingency.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
```

**Interpreting Cramér's V:**
- ≈ 0.1: small effect
- ≈ 0.3: medium effect
- ≈ 0.5: large effect

## Correlation

### Choosing a Correlation Method

| Method | Data Type | Assumptions | Robust to outliers? |
|--------|-----------|-------------|-------------------|
| **Pearson r** | Continuous, linear | Normality, linearity | No |
| **Spearman ρ** | Ordinal or monotonic | Monotonic relationship | Yes |
| **Kendall τ** | Ordinal, small samples | None | Yes |

```python
from scipy.stats import pearsonr, spearmanr, kendalltau

# Pearson correlation
r, p = pearsonr(df['x'], df['y'])
# Spearman rank correlation
rho, p = spearmanr(df['x'], df['y'])
# Kendall's tau
tau, p = kendalltau(df['x'], df['y'])
```

### Correlation Matrix

```python
# Compute all pairwise correlations
corr_matrix = df.corr(method='pearson', numeric_only=True)
# or method='spearman'

# Extract top correlations (excluding self-correlations)
corr_pairs = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
corr_pairs = corr_pairs.stack().sort_values(ascending=False)
top_correlations = corr_pairs.head(10)
```

**Reporting:** "Revenue and ad spend were strongly correlated, r(98) = 0.78,
p < 0.001." Always include degrees of freedom (n − 2 for Pearson) and p-value.

**Warning:** Correlation ≠ causation. Always mention this when reporting
correlations, especially strong ones.

## Regression

### Simple Linear Regression

```python
from scipy.stats import linregress

slope, intercept, r_value, p_value, std_err = linregress(df['x'], df['y'])

# Report: y = {intercept:.2f} + {slope:.2f}*x, R² = {r_value**2:.3f}, p = {p_value:.4f}
```

### Multiple Linear Regression

```python
import statsmodels.api as sm

X = df[['feature_1', 'feature_2', 'feature_3']]
X = sm.add_constant(X)  # add intercept
y = df['target']

model = sm.OLS(y, X).fit()
print(model.summary())
```

**Key outputs to report:**
- R² and Adjusted R² (model fit)
- F-statistic and its p-value (overall model significance)
- Coefficients with p-values (per-variable significance)
- Check for multicollinearity: VIF > 10 is problematic

### Logistic Regression (Binary Outcome)

```python
import statsmodels.api as sm

X = sm.add_constant(df[['feature_1', 'feature_2']])
y = df['binary_outcome']  # must be 0/1

model = sm.Logit(y, X).fit()
print(model.summary())

# Odds ratios
odds_ratios = np.exp(model.params)
```

## Confidence Intervals

Always report confidence intervals alongside point estimates.

```python
from scipy import stats

# 95% CI for a mean
n = len(data)
mean = np.mean(data)
se = stats.sem(data)  # standard error of the mean
ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)

# 95% CI for a proportion
from statsmodels.stats.proportion import proportion_confint
ci_low, ci_high = proportion_confint(count=successes, nobs=total, alpha=0.05, method='wilson')

# Bootstrap CI (when parametric assumptions are violated)
def bootstrap_ci(data, statistic=np.mean, n_bootstrap=10000, ci=95):
    bootstrapped = [statistic(np.random.choice(data, size=len(data), replace=True))
                    for _ in range(n_bootstrap)]
    lower = np.percentile(bootstrapped, (100 - ci) / 2)
    upper = np.percentile(bootstrapped, 100 - (100 - ci) / 2)
    return lower, upper
```

**Reporting format:** "The average revenue was $45,200 (95% CI: $42,100–$48,300)."

## Normality Testing

```python
from scipy.stats import shapiro, normaltest, anderson

# Shapiro-Wilk (best for n < 2000)
stat, p = shapiro(df['column'].dropna())

# D'Agostino's K² (better for larger samples)
stat, p = normaltest(df['column'].dropna())

# Anderson-Darling (more detailed output)
result = anderson(df['column'].dropna(), dist='norm')
# result.statistic vs result.critical_values at various significance levels
```

**Important nuance:** With large samples (n > 5000), normality tests almost
always reject normality. In practice, rely on visual inspection (histogram +
Q-Q plot) and the Central Limit Theorem for large samples.

## Time Series Analysis

### Trend Detection

```python
# Simple linear trend
from scipy.stats import linregress
slope, intercept, r, p, se = linregress(range(len(df)), df['value'])

# Moving averages
df['ma_7'] = df['value'].rolling(7).mean()
df['ma_30'] = df['value'].rolling(30).mean()
```

### Seasonality

```python
from statsmodels.tsa.seasonal import seasonal_decompose

# Requires setting a datetime index with regular frequency
result = seasonal_decompose(df['value'], model='additive', period=12)
result.trend      # long-term trend
result.seasonal   # repeating pattern
result.residual   # noise
```

### Stationarity

```python
from statsmodels.tsa.stattools import adfuller

stat, p, lags, obs, crit = adfuller(df['value'].dropna())
# p < 0.05 → series is stationary
# p ≥ 0.05 → series has a unit root (non-stationary); consider differencing
```

## Effect Sizes — Always Report

Statistical significance (p-value) tells you if an effect exists. Effect size
tells you if it matters.

| Test | Effect Size | Small | Medium | Large |
|------|------------|-------|--------|-------|
| t-test | Cohen's d | 0.2 | 0.5 | 0.8 |
| ANOVA | η² (eta-squared) | 0.01 | 0.06 | 0.14 |
| Correlation | r (or ρ, τ) | 0.1 | 0.3 | 0.5 |
| Chi-square | Cramér's V | 0.1 | 0.3 | 0.5 |
| Regression | R² | 0.02 | 0.13 | 0.26 |
| Mann-Whitney | Rank-biserial r | 0.1 | 0.3 | 0.5 |

```python
# Cohen's d from a t-test
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    s_pooled = np.sqrt(((n1-1)*group1.std()**2 + (n2-1)*group2.std()**2) / (n1+n2-2))
    return (group1.mean() - group2.mean()) / s_pooled

# Eta-squared from one-way ANOVA
def eta_squared(f_stat, df_between, df_within):
    return (f_stat * df_between) / (f_stat * df_between + df_within)
```

## Multiple Testing Correction

When running many tests, the probability of false positives increases.

```python
from statsmodels.stats.multitest import multipletests

# List of p-values from multiple tests
p_values = [0.001, 0.02, 0.03, 0.04, 0.15, 0.20, 0.50]

# Bonferroni correction (most conservative)
reject_bonf, p_corrected_bonf, _, _ = multipletests(p_values, method='bonferroni')

# Benjamini-Hochberg (controls false discovery rate — preferred for exploratory)
reject_bh, p_corrected_bh, _, _ = multipletests(p_values, method='fdr_bh')

# Report: "After Benjamini-Hochberg correction for 7 comparisons, 3 tests
# remained significant at α = 0.05."
```

## Sample Size Considerations

**Too small:** Underpowered, can only detect large effects, wide confidence
intervals.

**Too large:** Statistically significant results may have no practical importance.
Always report effect sizes.

**Rule of thumb for common tests:**
- t-test: ≥30 per group for CLT to apply
- Correlation: ≥30 for stable estimates
- Regression: ≥10–15 observations per predictor
- Chi-square: ≥5 expected frequency per cell

## Reporting Checklist

For every statistical result, report ALL of:
- [ ] **Test used** and why it was chosen
- [ ] **Test statistic** (t, F, χ², r, etc.) with degrees of freedom
- [ ] **P-value** (exact, not just threshold)
- [ ] **Effect size** with interpretation (small/medium/large)
- [ ] **Confidence interval** (95% CI by default)
- [ ] **Sample size(s)**
- [ ] **Assumptions checked** and any violations noted

**Example report:**
> "An independent-samples t-test showed that enterprise customers generated
> significantly higher revenue (M = $52,400, SD = $18,200) than SMB customers
> (M = $31,600, SD = $14,800), t(198) = 8.76, p < 0.001, Cohen's d = 1.24,
> 95% CI of difference [$16,100, $25,300]. This is a large effect. Levene's
> test indicated unequal variances (p = 0.03), so Welch's correction was
> applied. Both groups had n ≥ 50, satisfying the central limit theorem."

## Common Pitfalls

1. **P-hacking**: Running many tests and only reporting significant ones.
   → Pre-register hypotheses or use multiple testing correction.
2. **Ignoring effect sizes**: "Significant" ≠ meaningful with large samples.
   → Always report and interpret effect sizes.
3. **Correlation ≠ causation**: Strong correlations can be confounded.
   → Acknowledge limitations; suggest controlled experiments for causal claims.
4. **Ignoring assumptions**: Using parametric tests on non-normal data.
   → Check assumptions; use non-parametric alternatives when needed.
5. **Spurious precision**: Reporting means to 6 decimal places when SD is large.
   → Report to precision justified by the data.
6. **Simpson's Paradox**: Trends in subgroups reverse when aggregated.
   → Always check for confounding variables and segment where appropriate.