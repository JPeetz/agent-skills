#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Validate and summarise an agent red-teaming tests.jsonl.

Usage:
    python3 score_findings.py tests.jsonl
    python3 score_findings.py tests.jsonl --markdown summary.md
    python3 score_findings.py tests.jsonl --json

Checks every record against the schema in SKILL.md, then prints coverage per
OWASP ASI category, a severity rollup, and the findings that need attention.
Exit code 1 on schema errors or on a FAIL without trace evidence — an
unverifiable finding is a defect in the report, not a result.
"""
import json
import sys
from collections import Counter, defaultdict

ASIS = [f"ASI{i:02d}" for i in range(1, 11)]
VERDICTS = {"PASS", "FAIL", "PARTIAL", "BLOCKED-ENV"}
SEVERITIES = {"critical": 4, "high": 3, "medium": 2, "low": 1}
REQUIRED = ["id", "asi", "carrier", "expected", "observed", "evidence", "verdict"]
CORE = REQUIRED + ["severity", "remediation", "preconditions"]


def load(path):
    records, errors = [], []
    with open(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: invalid JSON ({exc.msg})")
                continue
            rec["_line"] = lineno
            records.append(rec)
    return records, errors


def validate(records):
    problems = []
    seen = set()
    for rec in records:
        tag = f"line {rec['_line']} ({rec.get('id', '?')})"
        missing = [k for k in REQUIRED if not str(rec.get(k, "")).strip()]
        if missing:
            problems.append(f"{tag}: missing {', '.join(missing)}")
        if rec.get("id") in seen:
            problems.append(f"{tag}: duplicate id")
        seen.add(rec.get("id"))
        if rec.get("asi") and rec["asi"] not in ASIS:
            problems.append(f"{tag}: unknown asi '{rec['asi']}'")
        if rec.get("verdict") and rec["verdict"] not in VERDICTS:
            problems.append(f"{tag}: verdict must be one of {sorted(VERDICTS)}")
        if rec.get("severity") and str(rec["severity"]).lower() not in SEVERITIES:
            problems.append(f"{tag}: severity must be one of {sorted(SEVERITIES)}")
        if rec.get("verdict") == "FAIL" and len(str(rec.get("evidence", ""))) < 12:
            problems.append(f"{tag}: FAIL without usable trace evidence")
        if rec.get("verdict") == "PASS" and not str(rec.get("evidence", "")).strip():
            problems.append(f"{tag}: PASS with no evidence of the block")
        if rec.get("verdict") == "BLOCKED-ENV" and not str(rec.get("observed", "")).strip():
            problems.append(f"{tag}: BLOCKED-ENV must state why it could not be tested")
        soft = [k for k in CORE if not str(rec.get(k, "")).strip()]
        if soft:
            problems.append(f"{tag}: incomplete for reporting ({', '.join(soft)})")
    return problems


def summarise(records):
    per_asi = defaultdict(Counter)
    severity = Counter()
    for rec in records:
        per_asi[rec.get("asi", "?")][rec.get("verdict", "?")] += 1
        if rec.get("verdict") in ("FAIL", "PARTIAL"):
            severity[str(rec.get("severity", "unrated")).lower()] += 1
    fails = sorted(
        [r for r in records if r.get("verdict") in ("FAIL", "PARTIAL")],
        key=lambda r: SEVERITIES.get(str(r.get("severity", "")).lower(), 0),
        reverse=True,
    )
    return per_asi, severity, fails


def render(records, problems, path):
    per_asi, severity, fails = summarise(records)
    out = []
    out.append(f"# Red team summary — `{path}`\n")
    out.append(f"Probes: **{len(records)}**  |  "
               f"FAIL: **{sum(1 for r in records if r.get('verdict') == 'FAIL')}**  |  "
               f"PARTIAL: **{sum(1 for r in records if r.get('verdict') == 'PARTIAL')}**  |  "
               f"BLOCKED-ENV: **{sum(1 for r in records if r.get('verdict') == 'BLOCKED-ENV')}**\n")
    out.append("## Coverage by ASI category\n")
    out.append("| ASI | probes | PASS | FAIL | PARTIAL | BLOCKED-ENV | status |")
    out.append("|---|---|---|---|---|---|---|")
    for asi in ASIS:
        c = per_asi.get(asi, Counter())
        total = sum(c.values())
        if not total:
            status = "NOT TESTED"
        elif c.get("BLOCKED-ENV", 0) == total:
            status = "BLOCKED-ENV"
        elif c.get("FAIL", 0):
            status = "FAIL"
        elif c.get("PARTIAL", 0):
            status = "PARTIAL"
        else:
            status = "PASS"
        out.append(f"| {asi} | {total} | {c.get('PASS',0)} | {c.get('FAIL',0)} | "
                   f"{c.get('PARTIAL',0)} | {c.get('BLOCKED-ENV',0)} | {status} |")
    out.append("\n## Findings by severity\n")
    if severity:
        for sev in ("critical", "high", "medium", "low", "unrated"):
            if severity.get(sev):
                out.append(f"- **{sev}**: {severity[sev]}")
    else:
        out.append("- none")
    out.append("\n## Confirmed and partial findings\n")
    if not fails:
        out.append("_No FAIL or PARTIAL records._")
    else:
        out.append("| id | ASI | severity | carrier | observed | remediation |")
        out.append("|---|---|---|---|---|---|")
        for r in fails:
            def cell(k):
                return str(r.get(k, "")).replace("|", "\\|")[:120]
            out.append(f"| {cell('id')} | {cell('asi')} | {cell('severity')} | "
                       f"{cell('carrier')} | {cell('observed')} | {cell('remediation')} |")
    out.append("\n## Schema problems\n")
    if problems:
        out.extend(f"- {p}" for p in problems)
    else:
        out.append("_None._")
    untested = [a for a in ASIS if not per_asi.get(a)]
    out.append("\n## Before you ship the report\n")
    out.append("- Untested categories (must be declared out of scope with a reason): "
               + (", ".join(untested) if untested else "none"))
    out.append("- Every FAIL/PARTIAL needs a reproduction step and a retest status.")
    out.append("- Verdicts are PASS/FAIL/PARTIAL/BLOCKED-ENV only — no blanks.")
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    markdown_path = None
    as_json = "--json" in argv
    if "--markdown" in argv:
        idx = argv.index("--markdown")
        if idx + 1 < len(argv):
            markdown_path = argv[idx + 1]

    records, errors = load(path)
    problems = errors + validate(records)
    per_asi, severity, fails = summarise(records)

    if as_json:
        print(json.dumps({
            "probes": len(records),
            "coverage": {a: dict(per_asi.get(a, {})) for a in ASIS},
            "severity": dict(severity),
            "schema_problems": problems,
        }, indent=2))
    else:
        report = render(records, problems, path)
        print(report)
        if markdown_path:
            with open(markdown_path, "w") as fh:
                fh.write(report)
            print(f"wrote {markdown_path}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
