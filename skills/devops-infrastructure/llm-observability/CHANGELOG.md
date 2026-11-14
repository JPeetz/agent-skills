# Changelog

All notable changes to the llm-observability skill.

## v1.0.0 — 2026-11-14

### Initial Release

Production observability for generative-AI systems: tracing, evaluation, cost
attribution, quality dashboards, and CI regression gates.

### What's Included

**Core Capabilities**

- Five-phase workflow: backend selection → instrumentation → evaluation →
  dashboards/alerts → CI regression gates
- OpenTelemetry GenAI semantic conventions (`gen_ai.*` attributes, span naming,
  `CLIENT` span kind) with development-status caveats and version-pinning advice
- Backend comparison: Langfuse, Arize Phoenix, LangSmith, Opik, Weave, plain OTLP
- Collector-based pipeline: content redaction, cost derivation, tail sampling,
  dual-export during migration
- Evaluator selection matrix (deterministic checks first, judges only where code
  cannot express the criterion)
- Judge calibration protocol: hand labels, ≥0.8 agreement, `temperature=0`,
  different model family from the system under test, structured verdicts
- Online (production sampling + user feedback) and offline (dataset) evaluation
- Six-panel dashboard spec and a rate/delta-based alert table with actions
- Aggregated-delta quality gates in CI with baselines committed to the repo
- Boundary section defining the split from `observability-engineering`:
  service SLOs and RED/USE metrics there, prompt/token/quality semantics here,
  with nested traces across the two

**References**

- `references/platform-selection.md` — decision matrix, self-host sizing, migration paths
- `references/otel-genai-attributes.md` — attribute and metric reference, drift notes
- `references/evaluation-playbook.md` — judge design, calibration, dataset curation

**Scripts**

- `scripts/langfuse-compose.sh` — bring up a local Langfuse stack (`up`/`smoke`/`down`)
- `scripts/check_genai_attrs.py` — lint exported OTLP/JSON traces for missing GenAI attributes

**Evals**

- 6 cases: 4 trigger cases (Langfuse instrumentation, OTLP export to an existing
  Collector, prompt-change quality gate, cost-spike investigation) and 2 near-miss
  negatives (plain service monitoring, prompt writing without measurement intent)

### Licence

MIT. Note that Arize Phoenix itself ships under ELv2; the licence here covers
this skill's documentation and scripts only.
