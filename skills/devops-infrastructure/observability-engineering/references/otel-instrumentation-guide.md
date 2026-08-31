# OpenTelemetry Instrumentation Guide

Multi-language OpenTelemetry instrumentation patterns, auto vs. manual approaches, and context propagation strategies.

---

## Table of Contents

1. [Quick Reference by Language](#1-quick-reference-by-language)
2. [Auto-Instrumentation Deep Dive](#2-auto-instrumentation-deep-dive)
3. [Manual Instrumentation Patterns](#3-manual-instrumentation-patterns)
4. [Context Propagation Strategies](#4-context-propagation-strategies)
5. [Common Pitfalls](#5-common-pitfalls)

---

## 1. Quick Reference by Language

### Package Map

| Language | SDK Package | OTLP Exporter (HTTP) | OTLP Exporter (gRPC) | Auto-Instrumentation Package |
|----------|------------|----------------------|---------------------|------------------------------|
| Node.js | `@opentelemetry/sdk-node` | `@opentelemetry/exporter-trace-otlp-http` | `@opentelemetry/exporter-trace-otlp-grpc` | `@opentelemetry/auto-instrumentations-node` |
| Python | `opentelemetry-sdk` | `opentelemetry-exporter-otlp-proto-http` | `opentelemetry-exporter-otlp-proto-grpc` | `opentelemetry-instrumentation-*` (per library) |
| Go | `go.opentelemetry.io/otel/sdk` | `otlptracehttp` / `otlpmetrichttp` | `otlptracegrpc` / `otlpmetricgrpc` | eBPF (experimental) |
| Java | `io.opentelemetry:opentelemetry-sdk` | `io.opentelemetry:opentelemetry-exporter-otlp` | Same (gRPC default) | `opentelemetry-javaagent.jar` |
| .NET | `OpenTelemetry` | `OpenTelemetry.Exporter.OpenTelemetryProtocol` | Same (both supported) | `OpenTelemetry.AutoInstrumentation` |
| Ruby | `opentelemetry-sdk` | `opentelemetry-exporter-otlp` | Same | `opentelemetry-instrumentation-all` |

### Environment Variables (Universal)

| Variable | Example | Purpose |
|----------|---------|---------|
| `OTEL_SERVICE_NAME` | `payment-service` | Logical service name (must be set) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4318` | OTLP HTTP endpoint |
| `OTEL_EXPORTER_OTLP_HEADERS` | `Authorization=Bearer token` | Auth headers for collector |
| `OTEL_TRACES_SAMPLER` | `traceidratio` | Sampling strategy |
| `OTEL_TRACES_SAMPLER_ARG` | `0.1` | Sample 10% of traces |
| `OTEL_RESOURCE_ATTRIBUTES` | `deployment.environment=production` | Additional resource labels |
| `OTEL_LOG_LEVEL` | `info` | SDK log verbosity |

### Resource Attributes (Recommended Minimum)

```yaml
# Set via OTEL_RESOURCE_ATTRIBUTES or programmatically
service.name:           "payment-service"     # Required
service.version:        "2.4.1"               # Strongly recommended
deployment.environment: "production"          # Strongly recommended
service.instance.id:    "pod-abc123"          # For scaling, pod name
telemetry.sdk.language: "python"              # Auto-set
telemetry.sdk.version:  "1.28.0"              # Auto-set
```

---

## 2. Auto-Instrumentation Deep Dive

### 2.1 Java Agent (Most Mature)

```bash
# Download
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# Run with agent
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.traces.exporter=otlp \
     -Dotel.metrics.exporter=otlp \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4318 \
     -jar app.jar
```

**Libraries instrumented automatically:**
- HTTP: Tomcat, Jetty, Netty, Spring WebMVC, JAX-RS
- gRPC: io.grpc
- DB: JDBC, R2DBC, MongoDB, Redis (Lettuce/Jedis), Elasticsearch
- Messaging: Kafka, JMS, RabbitMQ
- Other: Akka, GraphQL, Reactor, gRPC, Logback/Mapped Diagnostic Context (MDC)

### 2.2 Node.js Auto-Instrumentation

```bash
# Option 1: Load via environment variable (easiest)
export NODE_OPTIONS='--require @opentelemetry/auto-instrumentations-node/register'
export OTEL_SERVICE_NAME=order-service
node app.js

# Option 2: Programmatic (recommended — more control)
```

**Auto-instrumented modules:** `http`, `https`, `express`, `fastify`, `koa`, `@grpc/grpc-js`, `ioredis`, `redis`, `pg`, `mysql2`, `mongodb`, `kafkajs`, `amqplib`, `aws-sdk`, `graphql`, `nestjs`, `socket.io`

### 2.3 Python Auto-Instrumentation

```bash
# Install instrumentation packages
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install  # Installs instrumentation for all detected packages

# Run via opentelemetry-instrument CLI
OTEL_SERVICE_NAME=payment-service \
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
opentelemetry-instrument python app.py
```

**Auto-instrumented libraries:** `flask`, `django`, `fastapi`, `aiohttp`, `requests`, `urllib`, `psycopg2`, `pymongo`, `redis`, `kafka-python`, `celery`, `grpcio`, `sqlalchemy`, `mysql-connector`

### 2.4 .NET Auto-Instrumentation

```bash
# Install via NuGet
dotnet add package OpenTelemetry.AutoInstrumentation

# Configure via environment
export OTEL_SERVICE_NAME=order-api
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES=MyApp.Custom
export ASPNETCORE_HOSTINGSTARTUPASSEMBLIES=OpenTelemetry.AutoInstrumentation

dotnet run
```

**Auto-instrumented:** ASP.NET Core, HttpClient, Entity Framework Core, Npgsql, SQL Client, Redis (StackExchange), gRPC, RabbitMQ, Kafka

### 2.5 Go Auto-Instrumentation (eBPF / Experimental)

```go
// Go does not have equivalent auto-instrumentation agents.
// Two approaches for production:
//
// 1. Manual (recommended) — instrument explicitly:
import (
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
)

func main() {
    mux := http.NewServeMux()
    handler := otelhttp.NewHandler(mux, "server")
    http.ListenAndServe(":8080", handler)
}

// 2. eBPF-based auto-instrumentation (experimental):
//    github.com/open-telemetry/opentelemetry-go-instrumentation
//    Run with: OTEL_GO_AUTO_TARGET_EXE=/path/to/binary ./otel-go-instrumentation
```

### 2.6 Ruby Auto-Instrumentation

```ruby
# Gemfile
gem 'opentelemetry-sdk'
gem 'opentelemetry-exporter-otlp'
gem 'opentelemetry-instrumentation-all'

# config/initializers/opentelemetry.rb
require 'opentelemetry/sdk'

OpenTelemetry::SDK.configure do |c|
  c.service_name = 'payment-service'
  c.use_all(map: {
    'OpenTelemetry::Instrumentation::Rack' => { allowed_request_headers: ['x-request-id'] },
    'OpenTelemetry::Instrumentation::Redis' => { db_statement: :omit }
  })
end
```

**Auto-instrumented gems:** `rack`, `sinatra`, `rails`, `active_record`, `redis`, `faraday`, `http`, `restclient`, `net/http`, `sidekiq`, `kafka`, `grpc`

---

## 3. Manual Instrumentation Patterns

### 3.1 Creating Spans

```python
tracer = trace.get_tracer("order-service", "2.4.1")

# Synchronous context manager
def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.value", 99.95)
        result = do_work(order_id)
        span.set_status(trace.Status(trace.StatusCode.OK))
        return result

# Async context manager
async def handle_request(request):
    async with tracer.start_as_current_span("handle_request") as span:
        span.set_attribute("http.method", request.method)
        response = await dispatch(request)
        span.set_attribute("http.status_code", response.status)
        return response

# Manual lifecycle (when context managers won't work)
def complex_callback(data):
    span = tracer.start_span("process_callback")
    span.set_attribute("data.source", data.source)
    try:
        result = process(data)
        span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        raise
    finally:
        span.end()
```

### 3.2 Span Events vs. Attributes

| Mechanism | Best For | Examples | Impact |
|-----------|----------|---------|--------|
| **Attributes** | Structured data to query/filter | `http.status_code`, `db.operation` | Indexed, use for filtering |
| **Events** | Unique identifiers, debugging | `order.created {order_id}`, `cache.miss {key}` | Timestamped, not filterable |
| **Links** | Async flow correlation | Linking producer→consumer span | Separate trace context |

```python
# Attribute: use for filtering and grouping
span.set_attribute("http.method", "POST")

# Event: use for logging notable occurrences
span.add_event("cache_miss", {"key": session_key, "ttl_ms": remaining_ttl})

# Link: connect async operations (e.g., queue produces->consumer)
from opentelemetry.trace import Link, SpanContext, TraceFlags
link = Link(SpanContext(
    trace_id=producer_span.trace_id,
    span_id=producer_span.span_id,
    is_remote=True,
    trace_flags=TraceFlags(1),
))
with tracer.start_as_current_span("consumer_process", links=[link]):
    process_message()
```

### 3.3 Error Recording Across Languages

```python
# Python
try:
    result = process(order)
    span.set_status(Status(StatusCode.OK))
except ValueError as e:
    span.set_status(Status(StatusCode.ERROR, "Invalid order data"))
    span.record_exception(e, attributes={"order_id": order.id})
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.record_exception(e)
    raise  # Re-raise — let caller handle
```

```typescript
// TypeScript
try {
  const result = await processOrder(orderId);
  span.setStatus({ code: SpanStatusCode.OK });
} catch (err) {
  span.setStatus({
    code: SpanStatusCode.ERROR,
    message: err instanceof Error ? err.message : 'Unknown error'
  });
  span.recordException(err);
  throw err;
} finally {
  span.end();
}
```

```go
// Go
import "go.opentelemetry.io/otel/attribute"
import "go.opentelemetry.io/otel/codes"

func processOrder(ctx context.Context, orderID string) error {
    _, span := tracer.Start(ctx, "processOrder")
    defer span.End()

    if err := validate(orderID); err != nil {
        span.SetStatus(codes.Error, err.Error())
        span.SetAttributes(attribute.String("order.id", orderID))
        span.RecordError(err)
        return err
    }
    span.SetStatus(codes.Ok, "")
    return nil
}
```

### 3.4 Adding Custom Metrics

```python
from opentelemetry import metrics
from opentelemetry.metrics import Observation

meter = metrics.get_meter("order-service", "2.4.1")

# Counter — e.g. count orders placed
order_counter = meter.create_counter(
    "orders_created_total",
    description="Total number of orders created",
    unit="{orders}",
)

# Histogram — e.g. order value distribution
order_value_histogram = meter.create_histogram(
    "order_value",
    description="Order value distribution",
    unit="USD",
)

# UpDownCounter — e.g. active workers
active_workers = meter.create_up_down_counter(
    "active_workers",
    description="Number of active workers",
    unit="{workers}",
)

# Usage
order_counter.add(1, {"status": "completed", "payment_method": "card"})
order_value_histogram.record(99.95, {"region": "eu-west"})
active_workers.add(-1)  # worker finished
```

### 3.5 Recording Rules for Common Aggregations

```yaml
# groups/slo-metrics.yml
groups:
  - name: order_service_slo
    interval: 30s
    rules:
      - record: orders:total:rate5m
        expr: sum(rate(orders_created_total[5m]))
      - record: orders:errors:rate5m
        expr: sum(rate(orders_created_total{status="error"}[5m]))
      - record: orders:error_ratio:rate5m
        expr: |
          sum(rate(orders_created_total{status="error"}[5m]))
          /
          sum(rate(orders_created_total[5m]))
```

### 3.6 Instrumenting Database Queries

```typescript
// TypeScript — pg with manual instrumentation
import { trace } from '@opentelemetry/api';
import { Pool } from 'pg';

const tracer = trace.getTracer('database');
const pool = new Pool();

async function findUser(email: string) {
  const span = tracer.startSpan('SELECT users');
  span.setAttribute('db.system', 'postgresql');
  span.setAttribute('db.operation', 'SELECT');
  span.setAttribute('db.name', 'app_db');

  try {
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    span.setAttribute('db.result_count', result.rows.length);
    span.setStatus({ code: SpanStatusCode.OK });
    return result.rows[0];
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: (err as Error).message });
    span.recordException(err);
    throw err;
  } finally {
    span.end();
  }
}
```

### 3.7 Instrumenting Message Queues

```python
# Kafka producer with trace context injection
from opentelemetry.propagate import inject
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['kafka:9092'])

def publish_order(order):
    headers = {}
    inject(headers)  # Inject traceparent/tracestate into Kafka headers

    # Convert to Kafka-compatible headers (bytes)
    kafka_headers = [(k, v.encode()) for k, v in headers.items()]

    producer.send(
        'orders.created',
        value=order.serialize(),
        headers=kafka_headers,
    )
```

---

## 4. Context Propagation Strategies

### 4.1 W3C TraceContext (Default)

OpenTelemetry defaults to W3C TraceContext. Headers:

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: dd=ts,2019-08-06T12:00:00Z;tvid:12345
```

| Field | Description |
|-------|-------------|
| `00` | Version |
| `0af7...319c` | Trace ID (16-byte/32-char hex) |
| `b7ad...3331` | Span ID (8-byte/16-char hex) |
| `01` | Trace flags (01 = sampled) |

### 4.2 Propagation Across Transport Protocols

| Transport | Header / Mechanism | Default Propagator |
|-----------|-------------------|-------------------|
| HTTP | `traceparent` + `tracestate` headers | `W3CTraceContextPropagator` |
| gRPC | Metadata: `traceparent`, `tracestate` | `W3CTraceContextPropagator` |
| Kafka | Message headers | `W3CTraceContextPropagator` |
| RabbitMQ | AMQP headers `traceparent`, `tracestate` | `W3CTraceContextPropagator` |
| AWS SQS | Message attributes | Needs custom propagator |
| AWS Lambda | `_X_AMZN_TRACE_ID` | `AWSXRayPropagator` |

### 4.3 Custom Propagator Example (SQS)

```python
# Custom propagator for AWS SQS (which uses message attributes)
import json
from opentelemetry.propagators.textmap import TextMapPropagator

class SQSMessageAttrPropagator(TextMapPropagator):
    def inject(self, carrier, context=None, setter=None):
        ctx = context or trace.get_current_span().get_span_context()
        carrier['_otel_trace_id'] = {'StringValue': format_trace_id(ctx.trace_id), 'DataType': 'String'}
        carrier['_otel_span_id'] = {'StringValue': format_span_id(ctx.span_id), 'DataType': 'String'}
        carrier['_otel_trace_flags'] = {'StringValue': str(ctx.trace_flags), 'DataType': 'String'}

    def extract(self, carrier, context=None, getter=None):
        trace_id = parse_trace_id(carrier.get('_otel_trace_id', {}).get('StringValue', ''))
        span_id = parse_span_id(carrier.get('_otel_span_id', {}).get('StringValue', ''))
        return set_span_in_context(SpanContext(trace_id, span_id, is_remote=True), context)

# Set as propagator
from opentelemetry import propagate
propagate.set_global_textmap(SQSMessageAttrPropagator())
```

### 4.4 Propagation in Async / Concurrent Workloads

```python
# Threading — propagate context explicitly
import threading
from opentelemetry import context as otel_context

def thread_worker(ctx):
    # Attach the parent context in the thread
    token = otel_context.attach(ctx)
    try:
        with tracer.start_as_current_span("worker"):
            do_work()
    finally:
        otel_context.detach(token)

# Spawn thread with context
ctx = otel_context.get_current()
thread = threading.Thread(target=thread_worker, args=(ctx,))
thread.start()
```

```typescript
// Node.js — AsyncLocalStorage handles context automatically
// OpenTelemetry Node.js SDK uses AsyncLocalStorage under the hood
// All async operations within the same context tree share trace context

app.get('/api/orders', async (req, res) => {
  // Context is automatically propagated through async/await
  const orders = await db.query('SELECT * FROM orders');
  await sendToAnalytics(orders);
  res.json(orders);
  // Both db.query and sendToAnalytics share the same trace context
});
```

### 4.5 Verifying Propagation

```bash
# Check if context is propagated across services:
# 1. Start traces from a load generator
# 2. Query traces from both services in the backend (Grafana Tempo, Jaeger, etc.)
# 3. Verify the trace waterfall shows spans from both services

# Quick check: traceparent header should be visible
curl -v https://api.example.com/orders 2>&1 | grep -i traceparent
```

---

## 5. Common Pitfalls

### 5.1 Missing trace_id in Logs

**Problem:** Logs are emitted but `trace_id` field is missing.

**Fix:**
- Instrument the logging library (e.g., `LoggingInstrumentor().instrument()` in Python)
- Or manually extract context: `trace.get_current_span().get_span_context().trace_id`
- Verify: every log line from traced requests includes `trace_id`

### 5.2 Broken Context Propagation

**Problem:** Multi-service traces are broken — spans from service A and service B show in separate traces.

**Fix:**
- Verify HTTP clients are instrumented (auto-instrumentation covers this)
- Check `traceparent` header is present in outgoing requests
- For gRPC: ensure `otelgrpc.UnaryClientInterceptor()` or equivalent is applied
- For message queues: ensure headers are propagated in the message envelope
- For async: ensure context is propagated through thread boundaries (see §4.4)

### 5.3 Spans Not Ending

**Problem:** Missing spans or orphaned spans in the trace waterfall.

**Fix:**
- Always use `with` / `using` context managers for spans
- In error paths: `finally { span.end(); }`
- Set a timeout on `BatchSpanProcessor` for long-running spans
- Check for unclosed spans: `otel_sdk_processor_spans_dropped`

### 5.4 High Cardinality Labels

**Problem:** Prometheus/Mimir runs out of memory; query latency explodes.

**Fix:**
- Never put request/transaction/user IDs as span attributes
- If you must: use span events instead of attributes for unique identifiers
- Audit with: `topk(10, count by (__name__) ({__name__=~".+"}))` in Prometheus
- Set relabel rules to drop high-cardinality labels at the collector

### 5.5 Over-Sampling Wasting Budget

**Problem:** Trace storage costs are 10x the expected budget.

**Fix:**
- Set `OTEL_TRACES_SAMPLER=traceidratio` with `OTEL_TRACES_SAMPLER_ARG=0.1` (10%)
- Configure tail-based sampling in the collector to keep 100% of errors
- Set `exportIntervalMillis` higher (e.g., 15s instead of 1s) to batch more
- Shorten raw retention: traces beyond 3-7 days are rarely queried

### 5.6 Missing Service Maps

**Problem:** Service dependency graph (service map) is empty or incomplete.

**Fix:**
- Every service MUST set `OTEL_SERVICE_NAME` to a consistent, meaningful name
- Every service MUST propagate trace context to all downstream dependencies
- Every traced request must hit the same collector backend
- Verify: generate a trace that traverses 3+ services and check the service map in your backend

---

## References

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [OpenTelemetry SDK Configuration](https://opentelemetry.io/docs/concepts/sdk-configuration/)
- [opentelemetry-java-instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation)
- [opentelemetry-js-instrumentation](https://github.com/open-telemetry/opentelemetry-js)
- [opentelemetry-python-instrumentation](https://github.com/open-telemetry/opentelemetry-python)
- [opentelemetry-go-instrumentation](https://github.com/open-telemetry/opentelemetry-go-instrumentation)
- [W3C TraceContext](https://www.w3.org/TR/trace-context/)
