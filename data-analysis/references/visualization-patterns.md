# Visualization Patterns

## Chart Selection Guide

Choosing the right chart is the most important visualization decision. The wrong
chart can obscure patterns or, worse, mislead.

### Decision Tree

```
What are you showing?
│
├─ Comparison between categories
│  ├─ Few categories (<10)        → Bar chart (horizontal or vertical)
│  ├─ Many categories (>10)        → Horizontal bar chart (sorted)
│  ├─ Part-to-whole (≤5 parts)    → Pie chart or donut chart
│  └─ Part-to-whole (>5 parts)    → Treemap or stacked bar
│
├─ Relationship between two numeric variables
│  ├─ Continuous × Continuous     → Scatter plot
│  ├─ With trend line              → Scatter + regression line
│  ├─ Many overlapping points      → Hexbin or 2D density
│  └─ Three variables              → Bubble chart or 3D scatter
│
├─ Distribution of a single variable
│  ├─ Shape overview               → Histogram
│  ├─ Smooth distribution          → KDE plot
│  ├─ Compare multiple groups      → Box plot or violin plot
│  └─ Identify outliers            → Box plot with swarm overlay
│
├─ Trend over time
│  ├─ Single series                → Line chart
│  ├─ Multiple series              → Multi-line chart
│  ├─ Cumulative                   → Area chart
│  ├─ Cyclical pattern             → Seasonal decomposition plot
│  └─ Forecast + actual            → Line + confidence band
│
├─ Correlation / Matrix
│  ├─ Variable relationships       → Heatmap of correlation matrix
│  ├─ Clustered correlations       → Clustermap
│  └─ Pairwise relationships       → Pair plot (scatter matrix)
│
├─ Geospatial
│  ├─ Points on map                → Scatter geo / dot map
│  ├─ Regional values              → Choropleth map
│  └─ Density                      → Heatmap overlay on map
│
└─ Rankings
   ├─ Top N items                  → Horizontal bar (sorted descending)
   ├─ Change in rank over time     → Slope chart or bump chart
   └─ Before/after comparison      → Dumbbell chart
```

## Chart-by-Chart Guide

### Bar Chart

**Use for:** Comparing quantities across categories.

**Do:**
- Sort bars by value (unless categories have a natural order)
- Use horizontal bars for long category labels
- Start y-axis at zero (bars encode length, not position)
- Use consistent bar width

**Don't:**
- Use 3D bars — they distort perception
- Use bar charts for distributions (histograms do that)
- Overcrowd with too many categories

```python
# seaborn — best for quick, clean bar charts
import seaborn as sns
sns.barplot(data=df, x='category', y='value', order=df.groupby('category')['value'].mean().sort_values().index)
plt.xticks(rotation=45)

# matplotlib — for full control
fig, ax = plt.subplots()
ax.barh(df['category'], df['value'])
ax.invert_yaxis()  # highest value at top
```

### Line Chart

**Use for:** Trends over time, continuous sequences.

**Do:**
- Use for time series data with a natural ordering
- Limit to 5–7 lines for readability
- Use distinct colors and line styles for accessibility
- Add markers for sparse data points

**Don't:**
- Use for categorical data (that's a bar chart)
- Connect across missing time periods without indicating gaps
- Use dual axes unless the relationship between scales is the story

```python
# Single line
sns.lineplot(data=df, x='date', y='revenue')

# Multiple series
sns.lineplot(data=df, x='date', y='value', hue='category')

# With rolling average overlay
df['rolling_avg'] = df['value'].rolling(7).mean()
plt.plot(df['date'], df['value'], alpha=0.3, label='Daily')
plt.plot(df['date'], df['rolling_avg'], linewidth=2, label='7-day avg')
```

### Scatter Plot

**Use for:** Relationship between two numeric variables.

**Do:**
- Add a regression line if showing correlation
- Use alpha transparency for dense datasets
- Size or color encode a third variable when useful
- Label notable outliers

**Don't:**
- Use when one axis is categorical (use box plot or strip plot)
- Overplot without transparency with >1,000 points

```python
# Basic scatter
sns.scatterplot(data=df, x='ad_spend', y='revenue', alpha=0.5)

# With regression line
sns.regplot(data=df, x='ad_spend', y='revenue', scatter_kws={'alpha': 0.3})

# Size and color for third/fourth variable
sns.scatterplot(data=df, x='gdp', y='life_expectancy', size='population', hue='continent', alpha=0.7)
```

### Heatmap

**Use for:** Matrix data, correlation matrices, cross-tabulations.

**Do:**
- Use a diverging colormap for correlation matrices (values from -1 to 1)
- Annotate cells when the grid is small (<10×10)
- Center the colormap at 0 for diverging data
- Sort rows and columns by clustering for pattern discovery

**Don't:**
- Use more than ~50 rows/columns without clustering
- Use for data that isn't meaningfully arranged as a grid

```python
# Correlation heatmap
corr = df.corr(numeric_only=True)
mask = np.triu(np.ones_like(corr, dtype=bool))  # mask upper triangle
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, linewidths=0.5)

# Cross-tabulation heatmap
pivot = df.pivot_table(values='revenue', index='region', columns='product', aggfunc='sum')
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd')
```

### Box Plot

**Use for:** Comparing distributions across categories.

**Do:**
- Use for 2–20 categories
- Sort by median for meaningful ordering
- Add swarm or strip overlay for small datasets (<200 points)
- Show individual points alongside the box

**Don't:**
- Use for very small samples (<10 points per group)
- Compare more than 20 categories (becomes unreadable)

```python
# Basic box plot
sns.boxplot(data=df, x='category', y='value', order=medians.index)

# Box + individual points for small datasets
sns.boxplot(data=df, x='group', y='score')
sns.stripplot(data=df, x='group', y='score', color='black', alpha=0.3, size=3)

# Violin plot — richer distribution shape
sns.violinplot(data=df, x='group', y='score', inner='quartile')
```

### Pie Chart

**Use for:** Part-to-whole when there are **≤5 categories** and values sum to a
meaningful whole.

**Do:**
- Label percentages directly on or near slices
- Use a donut chart (slightly better perceptual accuracy)
- Order slices by size, largest first (clockwise from 12 o'clock)

**Don't:**
- Use for >5 categories — switch to a bar chart
- Use for non-exhaustive categories (that don't sum to 100%)
- Use 3D exploded pie charts — they distort proportion perception
- Use for comparison across multiple pies — bar charts are better

> **Rule of thumb:** When in doubt, use a bar chart instead of a pie chart.
> Humans are much better at comparing lengths than angles.

```python
# Only when appropriate
colors = sns.color_palette('pastel')[0:len(df)]
plt.pie(df['value'], labels=df['category'], colors=colors,
        autopct='%1.1f%%', startangle=90, pctdistance=0.85)
plt.axis('equal')
```

### Histogram & Distribution

```python
# Histogram with KDE overlay
sns.histplot(data=df, x='value', kde=True, bins='auto')

# Multiple distributions overlaid
sns.histplot(data=df, x='value', hue='group', element='step', stat='density', common_norm=False)

# Separate distributions (facets)
g = sns.FacetGrid(df, col='group')
g.map(sns.histplot, 'value')
```

## Color Best Practices

### Accessibility

- **Avoid red-green** for differentiating categories — ~8% of males are
  colorblind. Use blue-orange, purple-yellow, or blue-red instead.
- **Don't rely on color alone** — add patterns, labels, or shapes.
- **Test with a colorblind simulator** like [Coblis](https://www.color-blindness.com/coblis-color-blindness-simulator/).

### Color Palette Selection

| Data Type | Palette | Example |
|-----------|---------|---------|
| Sequential (low→high) | `Blues`, `YlOrRd`, `viridis` | Temperature, density, count |
| Diverging (± from center) | `RdBu_r`, `coolwarm`, `PiYG` | Correlation, change, sentiment |
| Categorical (distinct) | `Set2`, `tab10`, `husl` | Groups, regions, products |
| Highlight one category | Grays + one bright color | "Our product vs competitors" |

```python
# Seaborn built-in palettes
sns.color_palette('viridis', as_cmap=True)     # sequential
sns.color_palette('RdBu_r', as_cmap=True)      # diverging
sns.color_palette('Set2')                      # categorical

# Colorblind-friendly categorical palette
cb_palette = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC',
              '#CA9161', '#FBAFE4', '#949494', '#ECE133', '#56B4E9']
```

### Background & Style

```python
# Clean, modern style
sns.set_style('whitegrid')
sns.set_context('notebook')  # 'paper', 'notebook', 'talk', 'poster'

# Dark background for presentations
plt.style.use('dark_background')

# Remove chart junk
sns.despine()  # removes top and right spines
```

## Plotly Interactive Charts

For interactive exploration, dashboards, or HTML reports:

```python
import plotly.express as px
import plotly.graph_objects as go

# Interactive scatter
fig = px.scatter(df, x='gdp', y='life_expectancy', size='population',
                 color='continent', hover_name='country',
                 trendline='ols', title='GDP vs Life Expectancy')
fig.show()  # in notebooks
fig.write_html('chart.html')  # save to file

# Interactive line chart
fig = px.line(df, x='date', y='value', color='category',
              title='Revenue by Category Over Time')

# Interactive bar chart
fig = px.bar(df.groupby('category')['value'].sum().reset_index(),
             x='category', y='value', color='category',
             title='Total Value by Category')

# Dashboard with subplots
from plotly.subplots import make_subplots
fig = make_subplots(rows=2, cols=2,
                    subplot_titles=('Revenue', 'Users', 'Conversion', 'Churn'))
```

## Annotation & Labeling

Every chart should answer these questions at a glance:
1. **What** is being shown? (title)
2. **What** are the axes? (axis labels)
3. **What** are the units? (in axis labels or subtitle)
4. **Where** did the data come from? (source footnote)

```python
fig, ax = plt.subplots(figsize=(10, 6))

# The chart
sns.barplot(data=df, x='month', y='revenue', ax=ax)

# Labels
ax.set_title('Monthly Revenue — 2025', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Revenue (USD)', fontsize=11)

# Formatting
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Annotation for key insight
ax.annotate('Black Friday peak', xy=(10, 450000), xytext=(8, 480000),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10, color='red')

# Source footnote
fig.text(0.02, -0.02, 'Source: Internal Sales DB, Jan–Dec 2025',
         fontsize=8, color='gray', style='italic')

plt.tight_layout()
```

## Common Visualization Mistakes

| Mistake | Fix |
|---------|-----|
| 3D charts for 2D data | Use 2D — 3D distorts perception |
| Pie chart with 10+ slices | Use horizontal bar chart |
| Truncated y-axis (not starting at 0) | Start bar chart y-axis at 0 |
| No axis labels | Always label axes with units |
| Overplotting (dense scatter) | Use alpha, hexbin, or sampling |
| Rainbow colormap (jet) | Use perceptually uniform colormaps (viridis, magma) |
| Dual y-axes with different scales | Rarely justified; use faceted charts instead |
| Too many colors/patterns | Limit to 5–7 distinct colors in a single chart |
| Missing legend or unclear legend | Label directly on chart when possible |

## Saving & Exporting

```python
# Static images (matplotlib/seaborn)
plt.savefig('chart.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig('chart.pdf', bbox_inches='tight')  # vector format

# Interactive HTML (plotly)
fig.write_html('dashboard.html', include_plotlyjs='cdn')
fig.write_image('chart.png', scale=2)  # requires kaleido: pip install kaleido

# High-DPI for presentations and retina displays
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
```

## Dashboard Layout

When creating multi-chart reports:

1. **Top-left**: The most important chart (attention gravitates here)
2. **Top**: Summary KPIs or headline numbers
3. **Middle**: Detailed breakdowns, distributions
4. **Bottom-right**: Supporting detail, methodology notes

For plotly dashboards, use `make_subplots` or combine multiple `write_html` files
into a single HTML document.