# Changelog

All notable changes to the observability-engineering skill.

## v1.0.0 — 2026-06-18

### Initial Release

Synthesized from:
- **observability-engineer** (mk-knight23/AGENTS-COLLECTION) — monitoring, metrics, and incident response patterns
- **OpenTelemetry skill** (dash0hq/agent-skills) — OpenTelemetry SDK instrumentation and context propagation
- **SRE best practices** — Google SRE book, incident management frameworks, postmortem templates

### What's Included

**Core Capabilities:**
- OpenTelemetry instrumentation across 6+ languages (Node.js, Python, Go, Java, .NET, Ruby)
- Auto-instrumentation and manual span creation patterns
- Context propagation (W3C TraceContext) across HTTP, gRPC, and messaging
- Prometheus/Grafana monitoring with RED/USE methodology
- Structured JSON logging with trace correlation (Loki/ELK)
- Distributed tracing with head-based and tail-based sampling strategies
- Full semantic conventions for HTTP, database, and messaging spans
- SLI/SLO/SLA framework with error budget calculation
- Multi-window burn rate alerting
- Alert design principles and Alertmanager routing configuration
- Incident response playbook with severity classification and communication templates
- Postmortem structure and timeline reconstruction
- Observability-as-Code patterns (Terraform/Pulumi)
- GitOps workflow for dashboards and alert configuration
- Cost optimization guidance (cardinality management, sampling, retention policies)

**Material Improvements Over Sources:**
- Unified previously separate concerns (monitoring, logging, tracing, incident response) into one cohesive skill
- Added SLI/SLO frameworks with error budget mathematics not present in source skills
- Included observability-as-code patterns for GitOps workflows
- Added incident postmortem templates with timeline reconstruction
- Provided cost optimization guidance (cardinality management, sampling calculator)
- Added production readiness and debugging checklists
- Multi-language coverage (6+ languages vs typical 2-3 in source skills)

**Deliverables:**
- `SKILL.md` — 11-section comprehensive observability skill
- `references/otel-instrumentation-guide.md` — Multi-language OpenTelemetry patterns deep-dive
- `references/sli-slo-cookbook.md` — SLI definition patterns, error budget formulas, burn rate alert configs
- `references/incident-response.md` — Incident classification, IC role, templates, postmortem structure
- `scripts/validate-observability-stack.sh` — OTel Collector config, Prometheus rules, Grafana dashboard validation
- `scripts/generate-slo-dashboard.sh` — Automated Grafana SLO dashboard JSON generation from SLI definitions
- `evals/eval_cases.json` — 5 trigger cases + 2 near-miss negatives
