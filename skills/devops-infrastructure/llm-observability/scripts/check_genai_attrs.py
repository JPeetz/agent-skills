#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Lint exported OTLP/JSON traces for missing GenAI semantic-convention attributes.

Usage:
    python3 check_genai_attrs.py traces.json            # OTLP/JSON export ({"resourceSpans": [...]})
    python3 check_genai_attrs.py traces.json --json     # machine-readable output
    python3 check_genai_attrs.py --selftest             # run built-in fixture

Exit codes: 0 = no errors, 1 = missing required attributes, 2 = bad input.

Checks (per inference span, i.e. any span with gen_ai.operation.name):
  ERROR  gen_ai.provider.name          required
  ERROR  gen_ai.request.model          required for cost attribution
  ERROR  gen_ai.usage.input_tokens     required (inference operations only)
  ERROR  gen_ai.usage.output_tokens    required (inference operations only)
  WARN   gen_ai.response.model         aliases move; record what actually served
  WARN   gen_ai.response.finish_reasons  truncation/refusal is invisible without it
  WARN   error.type                    present only if status is ERROR
  WARN   gen_ai.conversation.id        missing on multi-turn apps
  WARN   gen_ai.prompt.version         prompt attribution
Also flags high-cardinality attributes used on spans that look like per-user data
(app.user.id, user.id, request.id) as WARN.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Iterable

INFERENCE_OPS = {"chat", "text_completion", "generate_content", "realtime_inference"}
REQUIRED = ("gen_ai.provider.name", "gen_ai.request.model")
TOKEN_ATTRS = ("gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens")
RECOMMENDED = (
    "gen_ai.response.model",
    "gen_ai.response.finish_reasons",
    "gen_ai.prompt.version",
)
HIGH_CARDINALITY = {"user.id", "app.user.id", "request.id", "gen_ai.conversation.id"}


def attr_value(v: dict[str, Any]) -> Any:
    if "stringValue" in v:
        return v["stringValue"]
    if "intValue" in v:
        return int(v["intValue"])
    if "doubleValue" in v:
        return float(v["doubleValue"])
    if "boolValue" in v:
        return bool(v["boolValue"])
    if "arrayValue" in v:
        return [attr_value(x) for x in v["arrayValue"].get("values", [])]
    return None


def iter_spans(doc: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    """Yield (service_name, span) from an OTLP/JSON export, or single-span shorthand."""
    if "resourceSpans" not in doc:
        spans = doc.get("spans") or ([doc] if "name" in doc else [])
        for s in spans:
            yield doc.get("service", "unknown"), s
        return
    for rs in doc["resourceSpans"]:
        svc = "unknown"
        for a in rs.get("resource", {}).get("attributes", []):
            if a.get("key") == "service.name":
                svc = attr_value(a.get("value", {})) or "unknown"
        for ss in rs.get("scopeSpans", []):
            for s in ss.get("spans", []):
                yield svc, s


def attributes(span: dict[str, Any]) -> dict[str, Any]:
    return {a["key"]: attr_value(a.get("value", {})) for a in span.get("attributes", []) if "key" in a}


def check(doc: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    inference_spans = 0
    for svc, span in iter_spans(doc):
        attrs = attributes(span)
        op = attrs.get("gen_ai.operation.name")
        if not op:
            continue
        inference_spans += 1
        name = span.get("name", "<unnamed>")
        where = f"{svc}/{name}"
        for key in REQUIRED:
            if key not in attrs or attrs[key] in (None, ""):
                findings.append({"severity": "ERROR", "span": where, "message": f"missing {key}"})
        if op in INFERENCE_OPS:
            for key in TOKEN_ATTRS:
                if key not in attrs or attrs[key] in (None, ""):
                    findings.append({"severity": "ERROR", "span": where, "message": f"missing {key} (cost and usage are blind)"})
        if span.get("status", {}).get("code") == 2 and "error.type" not in attrs:
            findings.append({"severity": "WARN", "span": where, "message": "span status ERROR but no error.type (unclassifiable failure)"})
        for key in RECOMMENDED:
            if key not in attrs:
                findings.append({"severity": "WARN", "span": where, "message": f"missing {key}"})
        for key in HIGH_CARDINALITY & attrs.keys():
            findings.append({"severity": "WARN", "span": where, "message": f"high-cardinality attribute {key} — keep on spans, never on metric labels"})
        if "gen_ai.input.messages" in attrs:
            findings.append({"severity": "INFO", "span": where, "message": "prompt content captured — confirm retention, PII redaction, and legal basis"})
    errors = sum(1 for f in findings if f["severity"] == "ERROR")
    return {
        "inference_spans": inference_spans,
        "errors": errors,
        "warnings": sum(1 for f in findings if f["severity"] == "WARN"),
        "findings": findings,
        "ok": errors == 0 and inference_spans > 0,
    }


SELFTEST_DOC = {
    "resourceSpans": [{
        "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "support-agent"}}]},
        "scopeSpans": [{"spans": [
            {"name": "chat gpt-4o", "attributes": [
                {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
                {"key": "gen_ai.provider.name", "value": {"stringValue": "openai"}},
                {"key": "gen_ai.request.model", "value": {"stringValue": "gpt-4o"}},
                {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "1200"}},
                {"key": "gen_ai.usage.output_tokens", "value": {"intValue": "180"}},
                {"key": "gen_ai.response.finish_reasons", "value": {"arrayValue": {"values": [{"stringValue": "stop"}]}}},
                {"key": "gen_ai.response.model", "value": {"stringValue": "gpt-4o-2024-08-06"}},
                {"key": "user.id", "value": {"stringValue": "u_8812"}},
            ]},
            {"name": "chat gpt-4o (broken)", "attributes": [
                {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
            ], "status": {"code": 2}},
        ]}],
    }],
}


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        res = check(SELFTEST_DOC)
        print(json.dumps(res, indent=2))
        print(f"\nselftest: {res['errors']} errors, {res['warnings']} warnings", file=sys.stderr)
        # Fixture has one healthy span and one span missing provider/model/both token attrs.
        return 0 if res["errors"] == 4 and res["warnings"] >= 5 else 1

    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    res = check(doc)
    if "--json" in argv:
        print(json.dumps(res, indent=2))
    else:
        print(f"inference spans: {res['inference_spans']}  errors: {res['errors']}  warnings: {res['warnings']}\n")
        for f in res["findings"]:
            print(f"[{f['severity']:5}] {f['span']}: {f['message']}")
        if res["inference_spans"] == 0:
            print("\nNo gen_ai spans found — instrumentation is not emitting GenAI attributes.")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
