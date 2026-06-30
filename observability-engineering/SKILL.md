---
name: observability-engineering
description: Production-grade observability engineering for AI agents: OpenTelemetry instrumentation, monitoring setup, log aggregation, distributed tracing, SLI/SLO management, alert design, and incident response workflows. Implements vendor-neutral telemetry standards with structured incident management.
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
domain: DevOps/Observability
version: 1.0.0
created: 2026-06-18
license: MIT
triggers:
  - set up monitoring
  - add observability
  - instrument with OpenTelemetry
  - create SLO
  - design alerts
  - incident response
  - distributed tracing
  - log aggregation
  - Grafana dashboard
  - Prometheus metrics
  - runbook
  - error budget
  - alert fatigue
  - trace context
  - RED metrics
  - USE methodology
near_miss_negatives:
  - fix this bug
  - deploy to Kubernetes
  - general DevOps questions without observability intent
seo:
  primary: observability agent skill
  clusters:
    - opentelemetry-instrumentation
    - slo-sli-alerting
    - incident-response-automation
    - distributed-tracing-setup
---

# Observability Engineering

Production-grade observability engineering for AI agents. Covers the full observability lifecycle: OpenTelemetry instrumentation, metrics collection, structured logging, distributed tracing, SLI/SLO management, alert design, and incident response workflows.

## When to Use This Skill

Invoke this skill when the user asks to:

- **Instrument** a service, application, or library with OpenTelemetry
- **Set up monitoring** dashboards, alerts, or metrics pipelines (Prometheus, Grafana, Datadog)
- **Design SLOs/SLIs** with error budgets and burn-rate alerts
- **Configure distributed tracing** with sampling strategies and context propagation
- **Aggregate logs** with structured JSON logging, trace correlation, and PII redaction
- **Build incident response** runbooks, communication templates, and postmortems
- **Manage observability-as-code** via Terraform/Pulumi for dashboards and alerts
- **Optimize observability costs** through cardinality management and retention policies

**Do NOT use this skill for:** general bug fixes (use code-review), Kubernetes deployment configuration (use a k8s skill), or generic DevOps questions without an observability intent.

---

## 1. OpenTelemetry Instrumentation

### 1.1 Quick-Start Patterns by Language

#### Node.js / TypeScript

```typescript
// packages: @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
// @opentelemetry/exporter-trace-otlp-http @opentelemetry/exporter-metrics-otlp-http
// @opentelemetry/sdk-logs @opentelemetry/exporter-logs-otlp-http

import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces`,
  }),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter({
      url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/metrics`,
    }),
    exportIntervalMillis: 15000,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: process.env.OTEL_SERVICE_NAME || 'my-service',
});

sdk.start();
process.on('SIGTERM', () => sdk.shutdown().then(() => process.exit(0)));
```

#### Python

```python
# packages: opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
# opentelemetry-instrumentation-flask opentelemetry-instrumentation-requests

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

resource = Resource(attributes={SERVICE_NAME: "my-service"})

# Traces
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Metrics
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
```

#### Go

```go
// modules: go.opentelemetry.io/otel go.opentelemetry.io/otel/sdk
// go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp
// go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    sdkmetric "go.opentelemetry.io/otel/sdk/metric"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func initOtel(ctx context.Context) (*sdktrace.TracerProvider, *sdkmetric.MeterProvider, error) {
    res, _ := resource.New(ctx,
        resource.WithAttributes(semconv.ServiceName("my-service")),
    )

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithResource(res),
        sdktrace.WithBatcher(otlptracehttp.New(ctx)),
    )
    otel.SetTracerProvider(tp)

    mp := sdkmetric.NewMeterProvider(
        sdkmetric.WithResource(res),
        sdkmetric.WithReader(otlpmetrichttp.NewReader(ctx)),
    )
    otel.SetMeterProvider(mp)

    return tp, mp, nil
}
```

#### Java

```java
// dependencies: opentelemetry-bom, opentelemetry-exporter-otlp
// Run with: java -javaagent:opentelemetry-javaagent.jar -jar app.jar
// Auto-instrumentation is the recommended approach for Java.

// Manual configuration (Spring Boot example):
@Configuration
public class OpenTelemetryConfig {
    @Bean
    public OpenTelemetry openTelemetry() {
        Resource resource = Resource.getDefault()
            .merge(Resource.create(Attributes.of(
                ResourceAttributes.SERVICE_NAME, "my-service")));

        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(
                OtlpHttpSpanExporter.builder().build()).build())
            .setResource(resource)
            .build();

        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
            .registerMetricReader(PeriodicMetricReader.builder(
                OtlpHttpMetricExporter.builder().build()).build())
            .setResource(resource)
            .build();

        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setMeterProvider(meterProvider)
            .build();
    }
}
```

#### .NET

```csharp
// packages: OpenTelemetry, OpenTelemetry.Exporter.OpenTelemetryProtocol
using OpenTelemetry;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OpenTelemetry.Metrics;

var resourceBuilder = ResourceBuilder.CreateDefault()
    .AddService("my-service");

using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .SetResourceBuilder(resourceBuilder)
    .AddOtlpExporter()
    .AddAspNetCoreInstrumentation()
    .AddHttpClientInstrumentation()
    .Build();

using var meterProvider = Sdk.CreateMeterProviderBuilder()
    .SetResourceBuilder(resourceBuilder)
    .AddOtlpExporter()
    .AddAspNetCoreInstrumentation()
    .AddRuntimeInstrumentation()
    .Build();
```

#### Ruby

```ruby
# gems: opentelemetry-sdk opentelemetry-exporter-otlp
# opentelemetry-instrumentation-all

require 'opentelemetry/sdk'
require 'opentelemetry/exporter/otlp'

OpenTelemetry::SDK.configure do |c|
  c.service_name = 'my-service'
  c.use_all # auto-instrument all registered libraries
  c.add_span_processor(
    OpenTelemetry::SDK::Trace::Export::BatchSpanProcessor.new(
      OpenTelemetry::Exporter::OTLP::Exporter.new
    )
  )
end
```

### 1.2 Auto-Instrumentation vs Manual Instrumentation

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **Auto-instrumentation** | HTTP frameworks, DB clients, gRPC, messaging | Zero code changes, fast coverage | Less semantic depth, some noise |
| **Manual spans** | Business logic, custom operations, critical paths | Full semantic control, business context | Requires code changes, risk of gaps |
| **Hybrid (recommended)** | Production services | Best coverage + business context | Requires planning |

**Auto-instrumentation agents:**

| Language | Agent/Approach |
|----------|---------------|
| Node.js | `@opentelemetry/auto-instrumentations-node` or `--require @opentelemetry/auto-instrumentations-node/register` |
| Python | `opentelemetry-instrument` CLI wrapper |
| Java | `opentelemetry-javaagent.jar` (JVM agent) |
| .NET | `OpenTelemetry.AutoInstrumentation` NuGet + env vars |
| Go | eBPF-based auto-instrumentation (experimental) |
| Ruby | `opentelemetry-instrumentation-all` gem |

### 1.3 Manual Span Creation Pattern

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.source", "api")

        # Nested span for a sub-operation
        with tracer.start_as_current_span("validate_inventory"):
            check_inventory(order_id)

        with tracer.start_as_current_span("charge_payment"):
            charge(order_id)

        span.set_status(trace.Status(trace.StatusCode.OK))
```

### 1.4 Context Propagation (W3C TraceContext)

All OpenTelemetry SDKs propagate trace context via W3C TraceContext headers by default:

```
traceparent: 00-{trace-id}-{parent-span-id}-{trace-flags}
tracestate: vendor-specific=value
```

**Multi-service propagation** is automatic when:
- HTTP clients are instrumented (auto-injection of headers)
- Message queues use OTel propagators
- All services use the same OTel exporter endpoint

**Custom propagation** for non-HTTP transports:

```python
from opentelemetry.propagate import inject, extract

# Inject trace context into carrier (dict, message headers, etc.)
carrier = {}
inject(carrier)
kafka_headers = carrier  # pass to Kafka message

# Extract on consumer side
ctx = extract(kafka_headers)
with tracer.start_as_current_span("consume", context=ctx):
    process_message()
```

---

## 2. Monitoring & Metrics

### 2.1 RED vs USE Methodology

#### RED (Rate, Errors, Duration) — for Services

| Metric | Signal | Prometheus Example |
|--------|--------|-------------------|
| **Rate** | Requests per second | `rate(http_requests_total[5m])` |
| **Errors** | Failed request rate | `rate(http_requests_total{status=~"5.."}[5m])` |
| **Duration** | Latency distribution | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |

**RED applies to:** HTTP APIs, gRPC services, worker pools, any request-driven service.

#### USE (Utilization, Saturation, Errors) — for Resources

| Metric | Signal | Prometheus Example |
|--------|--------|-------------------|
| **Utilization** | % resource used | `node_cpu_seconds_total{mode="idle"}` → `100 - rate(...)` |
| **Saturation** | Queue depth / load | `node_load1`, `node_memory_SwapFree_bytes` |
| **Errors** | Hardware/OS errors | `node_network_receive_errs_total` |

**USE applies to:** CPUs, memory, disks, network interfaces, database connection pools.

### 2.2 Prometheus Metric Types and Usage

```yaml
# Counter — only ever increases (request count, errors)
#   Functions: rate(), increase(), irate()
http_requests_total{method="GET", status="200"} 1023847

# Gauge — can go up and down (memory, queue depth, temp)
#   Functions: avg_over_time(), max_over_time(), delta()
process_resident_memory_bytes 1.342e+08

# Histogram — bucketed observations (latency, size)
#   Functions: histogram_quantile(), histogram_avg()
http_request_duration_seconds_bucket{le="0.1"} 450
http_request_duration_seconds_bucket{le="0.5"} 890
http_request_duration_seconds_bucket{le="+Inf"} 1000
http_request_duration_seconds_sum 1234.5
http_request_duration_seconds_count 1000

# Summary — client-side quantile computation (less flexible than histograms)
#   Prefer histograms in most cases.
```

### 2.3 Cardinality Management

**Cardinality** = number of unique label combinations. High cardinality kills Prometheus.

**DO:**
- Keep label values bounded (<100 unique values): `status_code`, `http_method`, `endpoint`
- Use `drop` relabel configs for noisy labels
- Pre-aggregate in the Collector: `batch` + `memory_limiter` processors

**DON'T:**
- ❌ Put user IDs, session IDs, or request IDs as labels
- ❌ Use unbounded dynamic values (timestamps, IPs, full URLs)
- ❌ Let GraphQL query names explode cardinality

**Relabel example to drop high-cardinality labels:**

```yaml
relabel_configs:
  - source_labels: [__name__]
    regex: 'http_request_duration_seconds_bucket'
    action: drop
    # Drop if url label is set (too many unique values)
  - source_labels: [url]
    regex: '.+'
    action: labeldrop
```

### 2.4 Recording Rules (Pre-computation)

```yaml
# rules/recording_rules.yml
groups:
  - name: http_aggregates
    interval: 30s
    rules:
      - record: job:http_requests_total:rate5m
        expr: rate(http_requests_total[5m])

      - record: job:http_request_errors:rate5m
        expr: rate(http_requests_total{status=~"5.."}[5m])

      - record: job:http_request_duration:p99
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

  - name: slo_dashboard
    interval: 30s
    rules:
      - record: slo:error_budget_remaining:ratio
        expr: |
          1 - (
            sum(rate(http_requests_total{status=~"5.."}[30d]))
            /
            sum(rate(http_requests_total[30d]))
          ) / 0.01  # 99% SLO
```

### 2.5 Grafana Dashboard Design

**Golden signals dashboard layout:**

| Row | Panels | Type |
|-----|--------|------|
| 1 | Request Rate + Error Rate | Graph (timeseries) |
| 2 | Latency p50/p90/p99 | Graph (timeseries) |
| 3 | Error Budget Remaining | Stat (gauge) |
| 4 | Top-N Endpoints by Latency | Table |
| 5 | Resource USE (CPU/Mem/Disk) | Graph (timeseries) |
| 6 | SLO Compliance (by endpoint) | Bar gauge |

---

## 3. Structured Logging

### 3.1 JSON Structured Logging Patterns

```json
{
  "timestamp": "2026-06-18T01:30:00.123Z",
  "level": "info",
  "message": "Order processed successfully",
  "service": "order-service",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "order_id": "ORD-12345",
  "customer_id": "CUST-789",
  "duration_ms": 234,
  "http": {
    "method": "POST",
    "path": "/api/orders",
    "status_code": 201
  }
}
```

### 3.2 Log Level Guidelines

| Level | Meaning | When to Use |
|-------|---------|------------|
| **ERROR** | Operation failed; needs human attention | Unhandled exceptions, payment failures, data loss |
| **WARN** | Something unexpected; recoverable | Retry exhaustion, degraded mode, deprecation |
| **INFO** | Key business events; normal operation | Order created, user registered, deployment |
| **DEBUG** | Detailed troubleshooting info | Request payload, SQL queries, cache hits/misses |
| **TRACE** | Extremely verbose; line-level detail | Function entry/exit, variable dumps |

### 3.3 Trace Correlation

Every log line MUST include `trace_id` and `span_id` when inside a traced span. This enables single-click log-to-trace correlation in Grafana/Datadog.

**Auto-injection patterns:**

```python
# Python: opentelemetry-instrumentation-logging auto-injects trace context
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)

# Now all log lines include:
# [2026-06-18 01:30:00,123] [INFO] [trace_id=0af7... span_id=b7ad...] message
```

```typescript
// Node.js: Winston transport with OTel context
import { trace } from '@opentelemetry/api';
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format((info) => {
      const span = trace.getActiveSpan();
      if (span) {
        info.trace_id = span.spanContext().traceId;
        info.span_id = span.spanContext().spanId;
      }
      return info;
    })(),
    winston.format.json()
  ),
});
```

### 3.4 Log Aggregation (Loki)

**Loki + Promtail pipeline:**

```yaml
# promtail-config.yml — scrape Kubernetes container logs
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    pipeline_stages:
      - json:
          expressions:
            level: level
            trace_id: trace_id
            service: service
      - labels:
          level:
          service:
      - output:
          source: message
```

**LogQL queries:**

```logql
# Errors with trace correlation
{service="order-service", level="error"} | json | line_format "{{.message}}"

# Errors in the last hour, grouped by endpoint
sum by (http_path) (count_over_time({service="api-gateway"} | json | level="error" [1h]))
```

### 3.5 PII Redaction

```yaml
# OTel Collector redaction processor
processors:
  redaction:
    allow_all_keys: false
    allowed_keys:
      - trace_id
      - span_id
      - service
      - level
      - message
      - duration_ms
    blocked_values:
      - '.*@.*'                    # Email addresses
      - '\d{3}-\d{2}-\d{4}'       # SSN patterns
      - '\b\d{16}\b'              # Credit card numbers
```

---

## 4. Distributed Tracing

### 4.1 Trace Context Propagation Architecture

```
  Client                API Gateway           Order Service         Payment Service
    |                       |                       |                       |
    |--- HTTP GET -------->|                       |                       |
    |   traceparent=...    |                       |                       |
    |                       |--- gRPC call ------->|                       |
    |                       |   traceparent=...    |                       |
    |                       |                       |--- Kafka msg -------->|
    |                       |                       |   traceparent=...    |
    |                       |                       |   in message headers  |
```

### 4.2 Sampling Strategies

| Strategy | Description | When to Use | Config |
|----------|------------|-------------|--------|
| **AlwaysOn** | 100% of traces | Development, low-volume | `sampler=always_on` |
| **AlwaysOff** | 0% of traces | Testing, no telemetry needed | `sampler=always_off` |
| **Probability** | Fixed % of traces | Stable production (e.g., 10%) | `OTEL_TRACES_SAMPLER=traceidratio OTEL_TRACES_SAMPLER_ARG=0.1` |
| **Rate limiting** | Max N traces/sec | High-throughput services | `sampler=rate_limiting` |
| **Parent-based** | Follow parent's decision | Downstream services (default) | `sampler=parentbased_always_on` |
| **Tail-based** | Decision after span completes | Keep all errors + slow traces | Collector-level (load-balancing exporter) |

**Recommended production config:**

```yaml
# OTel Collector tail sampling — keep all errors + >1s latency
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: latency
        type: latency
        latency: {threshold_ms: 1000}
      - name: probabilistic
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

### 4.3 Span Attributes Best Practices

```python
# DO: Use semantic conventions
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 201)
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.operation", "INSERT")

# DO: Add business context
span.set_attribute("order.value", 99.95)
span.set_attribute("order.items_count", 3)

# DON'T: High-cardinality attributes
# ❌ span.set_attribute("user.email", email)
# ❌ span.set_attribute("request.id", uuid4())
# ✔ Use span events for unique identifiers:
span.add_event("order_created", {"order_id": "ORD-12345"})
```

### 4.4 Error Recording

```python
from opentelemetry.trace import Status, StatusCode

try:
    result = process_order(order_id)
    span.set_status(Status(StatusCode.OK))
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.record_exception(e, attributes={"order_id": order_id})
    raise
```

### 4.5 Service Maps

Service maps are auto-generated by OTel backends (Grafana Tempo, Jaeger, Datadog) when trace context is consistently propagated across all services. Key requirements:

1. Every service MUST propagate trace context to downstream calls
2. Every service MUST export spans to the same collector/backend
3. Span names should follow semantic conventions for proper grouping

---

## 5. Semantic Conventions

### 5.1 Span Naming

```
<resource>.<operation>  — e.g., "HTTP GET", "gRPC OrderService/PlaceOrder"
<db.operation> <db.name>  — e.g., "SELECT users", "INSERT orders"
<messaging.operation> <messaging.destination>  — e.g., "process orders.new"
```

### 5.2 HTTP Semantic Conventions

| Attribute | Type | Example | Required |
|-----------|------|---------|----------|
| `http.method` | string | `GET`, `POST` | Yes |
| `http.status_code` | int | `200`, `404` | Yes (if available) |
| `http.route` | string | `/users/:id` | Recommended |
| `http.url` | string | `https://api.example.com/users/123` | Yes (client) |
| `http.target` | string | `/users/123?page=1` | Yes (server) |
| `http.request_content_length` | int | `1024` | Optional |
| `http.response_content_length` | int | `2048` | Optional |
| `network.protocol.version` | string | `1.1`, `2` | Recommended |

### 5.3 Database Semantic Conventions

| Attribute | Type | Example |
|-----------|------|---------|
| `db.system` | string | `postgresql`, `mongodb`, `redis` |
| `db.operation` | string | `SELECT`, `INSERT`, `find` |
| `db.name` | string | `users_db` |
| `db.statement` | string | `SELECT * FROM users WHERE id = ?` |
| `db.mongodb.collection` | string | `orders` |
| `db.redis.database_index` | int | `0` |

### 5.4 Messaging Conventions

| Attribute | Type | Example |
|-----------|------|---------|
| `messaging.system` | string | `kafka`, `rabbitmq`, `sqs` |
| `messaging.operation` | string | `process`, `receive`, `publish` |
| `messaging.destination` | string | `orders.new` |
| `messaging.kafka.consumer_group` | string | `order-processor` |
| `messaging.kafka.partition` | int | `3` |
| `messaging.message.id` | string | `msg-12345` |

---

## 6. SLI / SLO / SLA

### 6.1 Definitions

| Term | Definition | Example | Owner |
|------|-----------|---------|-------|
| **SLI** | Service Level Indicator — the metric | "Ratio of successful requests to total requests" | Engineering |
| **SLO** | Service Level Objective — the target | "99.9% of requests succeed over 30 days" | Product + Eng |
| **SLA** | Service Level Agreement — the contract | "99.5% uptime or 10% credit" | Legal + Business |

### 6.2 SLI Types

#### Availability SLI
```
Good: HTTP 200-499 (non-5xx)
Bad:  HTTP 5xx, timeouts, connection refused
SLI = good_requests / total_requests
```

#### Latency SLI
```
Good: requests completing within threshold (e.g., <300ms)
Bad:  requests exceeding threshold
SLI = fast_requests / total_requests
```

#### Freshness SLI
```
Good: data processed within freshness window (e.g., <5min stale)
Bad:  data older than freshness window
SLI = fresh_data_points / total_data_points
```

#### Coverage SLI
```
Good: data that passed validation/filtering
Bad:  data dropped/ignored
SLI = processed_data / total_ingested_data
```

### 6.3 Error Budget

```
Error Budget = 1 - SLO_target

For 99.9% SLO over 30 days:
  Total minutes:     43,200
  Allowed downtime:   43.2 minutes/month
  Error budget:       0.1%

Burn rate = actual_error_rate / budgeted_error_rate
  A burn rate of 1:   consuming budget at exactly the SLO pace
  A burn rate of 10:  consuming budget 10x faster than allowed
```

### 6.4 Multi-Window Burn Rate Alerts

```yaml
# Prometheus alerting rules for burn rate alerts
groups:
  - name: slo_burn_rate
    rules:
      # Fast burn: significant event, page on-call
      - alert: SLOErrorBudgetBurnCritical
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) > (0.01 * 14.4)  # 1% budget, 14.4x burn rate = 1h
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burning 14.4x: 1h to exhaustion"
          runbook: "https://runbooks.example.com/slo-burn-critical.md"

      # Slow burn: warning, create ticket
      - alert: SLOErrorBudgetBurnWarning
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[6h]))
            /
            sum(rate(http_requests_total[6h]))
          ) > (0.01 * 3)  # 1% budget, 3x burn rate = 6h
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error budget burning 3x: 6h window exceeded"
          runbook: "https://runbooks.example.com/slo-burn-warning.md"
```

### 6.5 SLO Dashboard JSON Pattern

See `scripts/generate-slo-dashboard.sh` for automated dashboard generation from SLI definitions.

---

## 7. Alerting

### 7.1 Alert Design Principles

1. **Alert on symptoms, not causes** — Alert on "user-facing error rate > 0.1%" not "CPU > 80%"
2. **Every alert must have a runbook** — No runbook = no alert
3. **Eliminate toil alerts** — Automate the response or remove the alert
4. **Page on SLO breaches only** — Everything else can be a ticket/chat notification
5. **Test alerts regularly** — Chaos engineering, fire drills, GameDays

### 7.2 Severity Classification

| Severity | Label | Response | Example |
|----------|-------|----------|---------|
| **SEV0** | Critical | Page on-call immediately, 5min ack | Complete outage, data loss, SLO budget exhausted in <1h |
| **SEV1** | High | Page on-call, 30min ack | Major feature broken, >50% error rate, budget burning at 10x |
| **SEV2** | Medium | Create ticket, SLA 4h response | Single endpoint degraded, slow burn rate detected |
| **SEV3** | Low | Create ticket, SLA 24h response | Non-critical component issue, capacity warning |
| **SEV4** | Info | No action needed | Deprecation notice, planned maintenance |

### 7.3 Alert Routing (Alertmanager)

```yaml
# alertmanager.yml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'on-call-pager'
      repeat_interval: 5m
      group_wait: 10s

    - match:
        severity: warning
      receiver: 'engineering-slack'
      repeat_interval: 1h

    - match_re:
        service: '(order|payment).*'
      receiver: 'payments-team'

receivers:
  - name: 'on-call-pager'
    pagerduty_configs:
      - routing_key: 'your-pagerduty-key'
        severity: critical

  - name: 'engineering-slack'
    slack_configs:
      - channel: '#alerts-eng'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'

  - name: 'payments-team'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/T...'
```

### 7.4 On-Call Rotation

```yaml
# PagerDuty / Opsgenie escalation policy pattern
# Level 1: Primary on-call (5 min ack)
# Level 2: Secondary on-call (10 min ack, auto-escalate if L1 doesn't ack)
# Level 3: Engineering manager (30 min ack)

# Key practices:
# - Rotations should be at least 1 week (not daily)
# - Never have a single point of failure in the rotation
# - Shadow rotations for new on-call engineers
# - Post-on-call writeup within 24h of rotation end
```

### 7.5 Alert Fatigue Prevention

- **Remove flapping alerts immediately** — If it fires and resolves 5x in an hour, it's broken
- **Aggregate during incidents** — Group related alerts, don't page for every instance
- **Tune thresholds quarterly** — Review false positive rates
- **"Business hours only" for SEV2 and below** — Don't wake people up for non-urgent issues
- **Inhibit alerts** — Don't page for payment-service down if the network is down

```yaml
# Alertmanager inhibition rule
inhibit_rules:
  - source_match:
      alertname: 'NetworkPartition'  # Don't alert on...
    target_match_re:
      alertname: '.*Down'            # ...anything-down if network is partitioned
    equal: ['datacenter']
```

---

## 8. Incident Response

### 8.1 Incident Severity Levels

| Level | Description | Response Time | Communication Cadence |
|-------|-------------|---------------|----------------------|
| **SEV0** | Full outage, data loss, security breach | Immediate | Every 30 min |
| **SEV1** | Major functionality broken, high error rate | 5 min | Every 1 hour |
| **SEV2** | Partial degradation, single feature affected | 30 min | Every 4 hours |
| **SEV3** | Minor issue, no user impact | 4 hours | Status page update |

### 8.2 Incident Commander (IC) Role

The IC is responsible for **coordination**, NOT necessarily fixing the problem.

**IC responsibilities:**
1. Declare the incident and severity
2. Set up the incident channel (Slack/Zoom)
3. Assign roles: Ops Lead, Comms Lead, Scribe
4. Maintain the incident timeline
5. Decide when to escalate
6. Declare incident resolved
7. Schedule and lead the postmortem

### 8.3 Communication Templates

#### Incident Declaration (Slack)

```
🚨 INCIDENT DECLARED: {title}
Severity: {SEV0/SEV1/SEV2}
IC: {name}
Ops Lead: {name}
Incident Channel: #{channel}
Zoom: {link}

Summary: {one-line description of what's happening}
Customer Impact: {who is affected and how}
Start Time: {ISO timestamp}
```

#### Status Update (Every 30-60 min)

```
📊 INCIDENT UPDATE #{N}: {title}
Time elapsed: {duration}
Status: {investigating/mitigating/resolved}

Current understanding:
- {bullet point findings}

Actions taken:
- {bullet point actions}

Next steps:
- {bullet point next actions}

ETA to resolution: {estimate}
```

#### Incident Resolution

```
✅ INCIDENT RESOLVED: {title}
Duration: {start_time} to {end_time} ({total_duration})
Severity: {SEV0/SEV1/SEV2}

Root Cause: {brief description}
Fix: {what was done to resolve}
Customer Impact: {final impact summary}

Postmortem: scheduled for {date} — {link}
Ticket: {ticket link}
```

### 8.4 Timeline Reconstruction Template

```markdown
## Incident Timeline: {title}

| Time (UTC) | Event | Source | Actor |
|------------|-------|--------|-------|
| 14:00 | Deploy v2.4.1 started | Deployment tool | @engineer |
| 14:03 | Latency spike detected (>500ms) | Grafana alert | System |
| 14:05 | Alert fired: SLOErrorBudgetBurnCritical | Alertmanager | System |
| 14:07 | IC declared SEV1 | Slack | @ic-name |
| 14:12 | Identified deploy as trigger | Ops investigation | @ops-lead |
| 14:15 | Rollback initiated | CI/CD | @ops-lead |
| 14:18 | Metrics recovering | Grafana | System |
| 14:22 | Service fully recovered | Grafana | System |
| 14:30 | Incident resolved | Slack | @ic-name |
```

### 8.5 Postmortem Structure

```markdown
# Postmortem: {incident title}

**Date:** YYYY-MM-DD
**Authors:** {names}
**Severity:** {SEV0/SEV1/SEV2}
**Duration:** {start → end, total duration}

## Summary
{2-3 sentence summary of what happened and impact}

## Customer Impact
- Who was affected and for how long
- What functionality was degraded/unavailable
- Error budget consumed: X% of monthly budget

## Timeline
{Same format as Section 8.4 — copy from incident channel}

## Root Cause Analysis
### Direct Cause
{The technical thing that broke}

### Contributing Factors
- {Why the direct cause was possible}
- {What allowed it to propagate}
- {What delayed detection}

## Detection
- How was it detected? (Alert, user report, social media)
- How long from start to detection? (TTD)
- How long from detection to resolution? (TTR)
- Could detection have been faster? How?

## Resolution
- What action resolved the incident?
- Was any data lost or corrupted?

## Action Items
| Priority | Action | Owner | Due |
|----------|--------|-------|-----|
| P0 | {critical fix to prevent recurrence} | @owner | YYYY-MM-DD |
| P1 | {improvement} | @owner | YYYY-MM-DD |
| P2 | {nice-to-have} | @owner | YYYY-MM-DD |

## Lessons Learned
- What went well
- What went poorly
- Where we got lucky (near-misses)
```

---

## 9. Observability as Code

### 9.1 Terraform: Grafana Dashboards + Alerts

```hcl
# grafana-dashboard.tf
resource "grafana_dashboard" "service_overview" {
  folder      = grafana_folder.services.id
  config_json = file("${path.module}/dashboards/service-overview.json")
}

resource "grafana_alert_rule" "error_rate" {
  name           = "High Error Rate - Order Service"
  folder_uid     = grafana_folder.alerts.uid
  rule_group     = "service-alerts"
  for            = "5m"
  condition      = "C"
  no_data_state  = "NoData"
  exec_err_state = "Error"

  # Query: error rate > 1%
  queries {
    ref_id      = "A"
    datasource_uid = "prometheus"
    expr        = "sum(rate(http_requests_total{service=\"order\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"order\"}[5m])) > 0.01"
  }

  annotations = {
    runbook_url = "https://runbooks.example.com/order-service-errors.md"
  }

  labels = {
    severity = "critical"
  }
}
```

### 9.2 GitOps Workflow for Monitoring Config

```
monitoring-config/
├── dashboards/
│   ├── service-overview.json
│   ├── slo-compliance.json
│   └── infrastructure-overview.json
├── alerts/
│   ├── slo-burn-rate.yml
│   ├── infrastructure.yml
│   └── application.yml
├── rules/
│   ├── recording-rules.yml
│   └── silencers.yml
├── terraform/
│   ├── main.tf
│   └── variables.tf
└── .github/workflows/
    └── deploy-monitoring.yml
```

**GitOps workflow:**
1. PR to change dashboard/alert → code review
2. Merge to main → CI runs `promtool check rules` + dashboard JSON validation
3. CI applies via Terraform to Grafana/Prometheus
4. Drift detection cron job reconciles every hour

---

## 10. Cost Optimization

### 10.1 Cardinality Management Checklist

- [ ] Audit metric label cardinality monthly
- [ ] Set `max_cardinality` limits on high-risk dimensions
- [ ] Use `drop` relabel configs for unused labels
- [ ] Pre-aggregate with recording rules (reduce raw data retention)
- [ ] Monitor `prometheus_tsdb_head_series` for growth trends

### 10.2 Sampling Cost Calculator

```
Annual trace storage cost = traces_per_second * avg_spans_per_trace
  * avg_span_size_bytes * 86400 * 365 * sampling_rate * $per_GB

Example (head sampling at 10%):
  1000 req/s * 10 spans * 1KB * 86400 * 365 * 0.10 * $0.50/GB
  = 1000 * 10 * 1024 * 86400 * 365 * 0.10 * 0.0000000005
  ≈ $16,181/year

Example (tail sampling at 1% with error/slow retention):
  Same base but keep 1% normal + 100% errors + 100% slow (>1s)
  If 5% errors and 2% slow, total retained ≈ 8%
  ≈ $12,945/year — savings of 20%
```

### 10.3 Retention Policies

| Data Type | Hot Storage | Warm Storage | Cold Storage | Rationale |
|-----------|------------|--------------|--------------|-----------|
| Metrics (raw) | 7 days | 30 days | — | High volume, fast query is key |
| Metrics (aggregated) | 30 days | 90 days | 1 year | For capacity planning, trends |
| Traces | 3 days | 14 days | — | Debugging window; sample for long-term |
| Logs | 7 days | 30 days | 90 days | Compliance often requires longer |

---

## 11. Quick-Start Checklists

### Production Readiness Checklist

- [ ] Auto-instrumentation enabled for all services
- [ ] Manual spans for business-critical operations
- [ ] Trace context propagated across all service boundaries
- [ ] RED metrics dashboards for all user-facing services
- [ ] USE metrics dashboards for all infrastructure
- [ ] Structured JSON logging with trace_id in every log line
- [ ] SLOs defined and SLO dashboards published
- [ ] Burn rate alerts configured (fast + slow burn)
- [ ] Alert routing tested end-to-end
- [ ] Runbooks linked in every alert annotation
- [ ] Incident response playbook documented
- [ ] On-call rotation configured and tested
- [ ] Cardinality audit completed
- [ ] Sampling strategy reviewed and documented
- [ ] Dashboard JSON validated in CI
- [ ] Alert rules syntax-checked in CI

### Debugging with Observability (Troubleshooting Flow)

1. **Start with the alert** → Which SLO is burning? Which service?
2. **Check the SLO dashboard** → Isolate the failing endpoint or dependency
3. **Look at traces** → Find a representative failing trace, follow the waterfall
4. **Correlate with logs** → Click from trace span to logs (via trace_id)
5. **Check recent deploys** → Overlay deployment markers on dashboards
6. **Check dependent service SLOs** → Is the failure upstream?
7. **Post-incident** → Update runbook, file action items from postmortem

---

## References

- `references/otel-instrumentation-guide.md` — Multi-language instrumentation deep-dive
- `references/sli-slo-cookbook.md` — SLI patterns, error budgets, burn rate configs
- `references/incident-response.md` — Full incident management playbook
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Google SRE Book — SLO Chapter](https://sre.google/workbook/implementing-slos/)
