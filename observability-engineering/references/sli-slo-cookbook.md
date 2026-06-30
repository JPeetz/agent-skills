# SLI / SLO Cookbook

SLI definition patterns, error budget formulas, and burn rate alert configurations for production observability.

---

## Table of Contents

1. [SLI Patterns](#1-sli-patterns)
2. [Error Budget Mechanics](#2-error-budget-mechanics)
3. [Burn Rate Alert Configurations](#3-burn-rate-alert-configurations)
4. [SLO Dashboard Design](#4-slo-dashboard-design)
5. [Multi-Service SLO Strategies](#5-multi-service-slo-strategies)
6. [SLO Review Cadence](#6-slo-review-cadence)

---

## 1. SLI Patterns

### 1.1 Common SLI Types

| SLI Type | What It Measures | Good Count | Bad Count | Query Pattern |
|----------|-----------------|------------|-----------|---------------|
| **Availability** | Success rate | HTTP 2xx/3xx/4xx | HTTP 5xx, timeouts | `http_requests{status!~"5.."} / http_requests_total` |
| **Latency** | Speed compliance | Duration ≤ threshold | Duration > threshold | `http_request_duration_seconds_bucket{le="0.3"} / ..._count` |
| **Freshness** | Data timeliness | Updated within window | Older than window | `data_timestamp_seconds - time() ≥ -300` |
| **Coverage** | Data completeness | Processed data | Dropped data | `events_processed / events_ingested` |
| **Throughput** | Processing rate | Rate ≥ minimum | Rate < minimum | `rate(events_processed[5m])` |
| **Durability** | Data persistence | Acknowledged writes | Lost data | `1 - (lost_events / total_events)` |
| **Correctness** | Data accuracy | Correct outputs | Incorrect outputs | `correct_events / total_events` |

### 1.2 Availability SLI Patterns

#### Standard Availability

```
SLI = sum(rate(http_requests_total{status!~"5.."}[$WINDOW]))
    / sum(rate(http_requests_total[$WINDOW]))

Good:   200, 201, 301, 302, 400, 401, 403, 404, 422, 429
Bad:    500, 502, 503, 504, timeouts, connection refused
```

**Grafana / PromQL:**

```promql
# Availability over 30 days
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
```

#### Degraded Availability

Some services consider 4xx client errors as "user mistakes" and exclude them from the SLO:

```promql
sum(rate(http_requests_total{status=~"2..|3.."}[30d]))
/
sum(rate(http_requests_total{status!~"4.."}[30d]))
```

#### Batch Job Availability

```promql
# Job success ratio (batch/worker)
sum(rate(job_completed_total{status="success"}[7d]))
/
sum(rate(job_completed_total[7d]))
```

### 1.3 Latency SLI Patterns

#### Request Latency

```
SLI = count of requests ≤ threshold / total requests

Examples:
  Critical:  p99 < 100ms   → SLI threshold: 100ms
  Normal:    p99 < 500ms   → SLI threshold: 500ms
  Relaxed:   p99 < 2000ms  → SLI threshold: 2s
```

```promql
# Latency SLI for <300ms threshold (using histogram)
sum(rate(http_request_duration_seconds_bucket{le="0.3"}[30d]))
/
sum(rate(http_request_duration_seconds_count[30d]))
```

#### Multi-Tier Latency SLI

Different endpoints have different latency expectations:

```promql
# Per-route latency SLI
(
  sum(rate(http_request_duration_seconds_bucket{le="0.1", endpoint=~"/healthz|/readyz"}[30d]))
  +
  sum(rate(http_request_duration_seconds_bucket{le="0.5", endpoint="/api/orders"}[30d]))
  +
  sum(rate(http_request_duration_seconds_bucket{le="2", endpoint="/api/reports"}[30d]))
)
/
sum(rate(http_request_duration_seconds_count[30d]))
```

### 1.4 Freshness SLI (Data Pipelines)

```promql
# If data events carry a timestamp:
#   freshness_seconds = time() - event_timestamp_seconds
# SLI: what % of data is within freshness window?

# Using a metric that reports max staleness
(
  count by (dataset) (
    max_over_time(data_staleness_seconds[5m]) < 300
  )
)
/
count by (dataset) (data_staleness_seconds)
```

### 1.5 Defining SLIs for Different Service Types

| Service Type | Primary SLI | Secondary SLI | Example Threshold |
|-------------|------------|---------------|-------------------|
| **API Gateway** | Availability | Latency (p99) | 99.95%, <200ms |
| **Payment Service** | Availability | Latency (p95) | 99.99%, <500ms |
| **Batch Processor** | Success rate | Freshness | 99.9%, <5min |
| **Database** | Query success | Latency (p99) | 99.99%, <100ms |
| **CDN / Static** | Availability | Latency | 99.99%, <50ms |
| **Message Queue** | Publish success | Consumer lag | 99.99%, <10s lag |
| **Data Lake** | Ingestion rate | Freshness | 99%, <1hr |

---

## 2. Error Budget Mechanics

### 2.1 Error Budget Calculation

```
Error Budget = 1 - SLO Target
Budget Consumed = (1 - observed_SLI) / (1 - SLO_target)
Budget Remaining = 1 - Budget Consumed

Example — 99.9% SLO over 30 days:
  Total requests:    10,000,000
  Error budget:            10,000  (0.1%)
  If 5,000 errors in 30 days:
    Budget consumed: 5,000 / 10,000 = 50%
    Budget remaining: 50%
```

### 2.2 Allowed Downtime Table

| SLO | Per Day | Per Week | Per 30 Days | Per Quarter |
|-----|---------|----------|-------------|-------------|
| **99.9%** ("three nines") | 86.4s | 10m 5s | 43m 12s | 2h 10m |
| **99.95%** | 43.2s | 5m 2s | 21m 36s | 1h 5m |
| **99.99%** ("four nines") | 8.6s | 1m 0s | 4m 19s | 13m 0s |
| **99.999%** ("five nines") | 0.9s | 6s | 25.9s | 1m 18s |

### 2.3 Error Budget Burn Rate

```
Burn Rate = (1 - observed_SLI) / (1 - SLO_target)

Burn rate of 1:    Consuming budget exactly at the allowed rate
Burn rate of 10:   Consuming budget 10x faster than allowed
Burn rate of 14.4: Will exhaust 30-day budget in ~2 days (48h)
Burn rate of 36:   Will exhaust 30-day budget in ~1 day (20h)
Burn rate of 720:  Will exhaust 30-day budget in ~1 hour
```

### 2.4 Burn Rate to Exhaustion Table (30-day window)

| Burn Rate | Time to exhaust 30d budget | Alert Severity |
|-----------|---------------------------|----------------|
| 1x | 30 days | No alert |
| 2x | 15 days | Info |
| 3x | 10 days | Warning (slow burn) |
| 6x | 5 days | Warning |
| 10x | 3 days | High |
| 14.4x | ~2 days (48h) | Critical |
| 36x | ~20 hours | Critical |
| 144x | ~5 hours | Critical |
| 720x | ~1 hour | Critical |

---

## 3. Burn Rate Alert Configurations

### 3.1 Standard Multi-Window Burn Rate Alerts

Based on Google SRE Workbook recommendation: two windows per burn rate (short window + long window).

```yaml
# PrometheusRule: SLO Alerting
# Configures multi-window, multi-burn-rate alerts for a 99.9% SLO
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: slo-http-requests
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    - name: slo-rules
      interval: 30s
      rules:
        # ── Recording Rules ──
        - record: sli:http_requests:error_ratio_1m
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[1m]))
            /
            sum(rate(http_requests_total[1m]))

        - record: sli:http_requests:error_ratio_5m
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))

        - record: sli:http_requests:error_ratio_30m
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[30m]))
            /
            sum(rate(http_requests_total[30m]))

        - record: sli:http_requests:error_ratio_6h
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[6h]))
            /
            sum(rate(http_requests_total[6h]))

        - record: sli:http_requests:error_budget_remaining
          expr: 1 - (sli:http_requests:error_ratio_30m / 0.001)

        # ── Burn Rate Alerts ──
        # Critical: budget burning 14.4x (1h window, 5m short window)
        - alert: SLOBurnRateCritical
          expr: |
            sli:http_requests:error_ratio_1m > (0.001 * 14.4)
            and
            sli:http_requests:error_ratio_5m > (0.001 * 14.4)
          for: 2m
          labels:
            severity: critical
            slo: "99.9%"
          annotations:
            summary: "SLO error budget burning at critical rate (14.4x)"
            description: |
              Error ratio over 1m/5m exceeds 14.4x the 99.9% SLO budget rate.
              Budget will be exhausted in ~48 hours at this rate.
            runbook: "https://runbooks.example.com/slo-burn-critical.md"

        # Warning: budget burning 3x (6h window, 30m short window)
        - alert: SLOBurnRateWarning
          expr: |
            sli:http_requests:error_ratio_30m > (0.001 * 3)
            and
            sli:http_requests:error_ratio_6h > (0.001 * 3)
          for: 5m
          labels:
            severity: warning
            slo: "99.9%"
          annotations:
            summary: "SLO error budget burning at warning rate (3x)"
            description: |
              Error ratio over 30m/6h exceeds 3x the 99.9% SLO budget rate.
              Under 10% error budget remaining.
            runbook: "https://runbooks.example.com/slo-burn-warning.md"

        # Info: budget below 50%
        - alert: SLOBudgetLow
          expr: sli:http_requests:error_budget_remaining < 0.5
          for: 5m
          labels:
            severity: info
          annotations:
            summary: "Error budget below 50%"
            description: "Error budget remaining: {{ $value | humanizePercentage }}"
```

### 3.2 Burn Rate Thresholds by SLO Target

```yaml
# Burn rate thresholds for common SLO targets
# Format: burn_rate_threshold (windows: short, long)

# For 99.9% SLO (error budget = 0.001):
#   Fast burn threshold:  0.001 * 14.4 = 0.0144 (1.44% error rate)
#   Slow burn threshold:  0.001 * 3    = 0.003  (0.3% error rate)

# For 99.99% SLO (error budget = 0.0001):
#   Fast burn threshold:  0.0001 * 14.4 = 0.00144 (0.144% error rate)
#   Slow burn threshold:  0.0001 * 3    = 0.0003  (0.03% error rate)

# For 99.5% SLO (error budget = 0.005):
#   Fast burn threshold:  0.005 * 14.4 = 0.072 (7.2% error rate)
#   Slow burn threshold:  0.005 * 3    = 0.015 (1.5% error rate)
```

### 3.3 Burn Rate Alert Calculator (CLI)

```bash
# Calculate burn rate thresholds for a given SLO target
calculate_slo_thresholds() {
    local slo_target=$1
    local budget
    budget=$(echo "scale=10; 1 - ($slo_target / 100)" | bc)

    echo "SLO Target:             ${slo_target}%"
    echo "Error Budget:           $budget"
    echo ""
    echo "Fast Burn (14.4x):      $(echo "scale=6; $budget * 14.4 * 100" | bc)% error rate"
    echo "  Window: 1m + 5m, for: 2m"
    echo "Slow Burn (3x):         $(echo "scale=6; $budget * 3 * 100" | bc)% error rate"
    echo "  Window: 30m + 6h, for: 5m"
    echo ""
    echo "Time to exhaust budget at 14.4x: ~48 hours"
    echo "Time to exhaust budget at 3x:    ~10 days"
    echo "Time to exhaust budget at 1x:    30 days"
}

# Usage
calculate_slo_thresholds 99.95
# Output:
#   SLO Target:             99.95%
#   Error Budget:           .0005
#   Fast Burn (14.4x):      .0072% error rate
#   Slow Burn (3x):         .0015% error rate
```

### 3.4 Per-Endpoint SLO Alerts

```yaml
# Alerting per critical endpoint
groups:
  - name: per_endpoint_slo
    rules:
      - alert: EndpointSLOCritical
        expr: |
          (
            sum by (endpoint) (rate(http_requests_total{status=~"5.."}[1m]))
            /
            sum by (endpoint) (rate(http_requests_total[1m]))
          )
          > 0.01
          and
          (
            sum by (endpoint) (rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum by (endpoint) (rate(http_requests_total[5m]))
          )
          > 0.01
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Endpoint {{ $labels.endpoint }} error rate > 1%"
```

---

## 4. SLO Dashboard Design

### 4.1 Key Dashboard Panels

| Panel | Type | Purpose |
|-------|------|---------|
| Error Budget Remaining | Stat (gauge) | Percentage of remaining budget |
| SLI Compliance | Timeseries | % good requests over time |
| Burn Rate | Timeseries | Fast (1h) + Slow (6h) burn rates |
| Error Budget Burn-down | Timeseries | Budget consumed over SLO window |
| Request Volume | Timeseries | Rate + error rate overlay |
| Latency p50/p90/p99 | Timeseries | Latency distribution |
| Top-N Error Endpoints | Table | Highest error rate endpoints |
| SLO Target line | Threshold overlay | Reference line on all panels |

### 4.2 Prometheus Recording Rules for Dashboard Performance

```yaml
groups:
  - name: slo_dashboard
    interval: 30s
    rules:
      # Pre-aggregate for faster dashboard queries
      - record: dashboard:slo:availability_30d
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[30d]))
          /
          sum(rate(http_requests_total[30d]))

      - record: dashboard:slo:error_budget_remaining
        expr: |
          1 - (
            sum(rate(http_requests_total{status=~"5.."}[30d]))
            /
            sum(rate(http_requests_total[30d]))
          ) / 0.001  # Replace with your SLO budget

      - record: dashboard:slo:burn_rate_1h
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) / 0.001  # Replace with your SLO budget

      - record: dashboard:slo:latency_p99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          )
```

---

## 5. Multi-Service SLO Strategies

### 5.1 Composite SLO

When a user request traverses multiple services, the overall SLO is the **product** of each service's SLO:

```
Composite SLO = SLO_service_A × SLO_service_B × SLO_service_C

Example:
  API Gateway:       99.99%
  Payment Service:   99.99%
  Database:          99.999%
  ─────────────────────────────
  Composite user SLO: 99.979%
```

### 5.2 Tiered SLO Model

```
Critical Path SLOs (99.99%):
  ├── User authentication
  ├── Payment processing
  └── Database writes

Important Path SLOs (99.9%):
  ├── Product search
  ├── Order history
  └── Notification delivery

Best Effort SLOs (99%):
  ├── Analytics pipeline
  ├── Recommendation engine
  └── Report generation
```

### 5.3 Dependency-Based SLO Attribution

```
When service B depends on service A:
  Service B's SLO = Service B's own SLO / Service A's SLO

Example:
  Service A (auth):  99.99%
  Service B (orders): 99.95%
  ──────────────────────────
  Service B's own performance SLO: 99.95% / 99.99% = 99.96%
```

---

## 6. SLO Review Cadence

### 6.1 Recommended Review Cycle

| Frequency | Activity | Who |
|-----------|----------|-----|
| **Weekly** | Check error budget burn rate in dashboard | On-call engineer |
| **Monthly** | Review SLO attainment report; adjust dashboards | Service team |
| **Quarterly** | Re-evaluate SLO targets; review budget consumption trends | Product + Engineering |
| **Annually** | Adjust SLO tiers with business stakeholders | Engineering + Product leadership |

### 6.2 SLO Target Adjustment Decision Matrix

| Budget Consumption | Trend | Action |
|--------------------|-------|--------|
| <50% used | Consistent | Consider tightening SLO (e.g., 99.9% → 99.95%) |
| >80% used | Growing | Review reliability investments; loosen SLO or improve |
| >100% used | Frequent | SLO is unrealistic for current investment; lower target or allocate resources |
| >100% used | Rare (postmortem follow-up) | Accept one-time miss; no change to target |

### 6.3 SLO Review Template

```markdown
## Monthly SLO Review — {team}

### Service: {service_name}
### Period: {YYYY-MM-DD} → {YYYY-MM-DD}

### Summary
- Current SLO target: {99.9%}
- Actual SLI: {99.92%}
- Error budget consumed: {20%}
- Burn rate events: {3 warnings, 0 criticals}

### Notable Events
- {date}: {deploy vX.Y caused 5min 500 spike — consumed 0.5% budget}
- {date}: {db performance regression, TTR: 15min}

### Actions
- [ ] Re-evaluate latency SLI threshold (currently 300ms, p99 actual is 180ms → tighten?)
- [ ] Add endpoint-specific SLO for /api/payments
- [ ] Review burn rate alert sensitivity (0 false positives this month)

### Decision
SLO target: ☐ Keep at {99.9%} / ☐ Tighten to {99.95%} / ☐ Loosen to {99.5%}
```

---

## References

- [Google SRE Book — SLO Chapter](https://sre.google/workbook/implementing-slos/)
- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Grafana SLO Dashboard Tutorial](https://grafana.com/go/observabilitycon/2023/grafana-slo-dashboard/)
