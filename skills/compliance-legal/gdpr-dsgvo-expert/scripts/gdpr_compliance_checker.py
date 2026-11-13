#!/usr/bin/env python3
"""GDPR/DSGVO compliance checker.

Scans a directory tree for personal data patterns and risky code practices and
reports a 0-100 compliance score with article-referenced recommendations.

Standard library only. Python 3.8+.

This is triage, not a compliance certificate. A clean scan means nothing
matched the rules below -- it does not mean the processing is lawful.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

VERSION = "0.1.0"

DEFAULT_EXCLUDES = {
    ".git", ".hg", ".svn", "node_modules", "venv", ".venv", "env", "dist",
    "build", "__pycache__", ".mypy_cache", ".pytest_cache", ".tox", "vendor",
    ".idea", ".vscode", "coverage", "htmlcov",
}

TEXT_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rb", ".php",
    ".cs", ".c", ".cpp", ".h", ".swift", ".rs", ".scala", ".sql", ".sh", ".bash",
    ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf", ".env", ".xml",
    ".html", ".htm", ".md", ".txt", ".csv", ".tf", ".properties", ".gradle",
}

MAX_BYTES = 2 * 1024 * 1024
SAMPLE_MAX = 120

# ---------------------------------------------------------------------------
# Rules
#
# weight: points deducted from 100 for the first hit; the second and third hits
# of the same rule deduct weight again at a decaying rate (see score()).
# ---------------------------------------------------------------------------

RULES = [
    # --- personal data patterns -------------------------------------------
    {
        "id": "PII001",
        "category": "personal_data",
        "title": "Email addresses in source",
        "pattern": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        "weight": 4,
        "article": "Art. 4(1)",
        "recommendation": (
            "Confirm each embedded address is synthetic or necessary. Real "
            "addresses in repositories persist in git history and are hard to erase."
        ),
    },
    {
        "id": "PII002",
        "category": "personal_data",
        "title": "Phone numbers in source",
        "pattern": r"(?<![\w.])(?:\+\d{1,3}[\s./-]?)?(?:\(\d{1,4}\)[\s./-]?)?\d{2,4}(?:[\s./-]\d{2,8}){1,3}(?![\w.])",
        "validator": "phone",
        "weight": 3,
        "article": "Art. 4(1)",
        "recommendation": "Keep sample numbers obviously fake (e.g. +49 30 0000000) or generate them.",
    },
    {
        "id": "PII003",
        "category": "personal_data",
        "title": "IP addresses in source",
        "pattern": r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?![\d.])",
        "weight": 3,
        "article": "Art. 4(1), recital 30",
        "recommendation": "IP addresses are personal data. Do not hardcode them; log them truncated or hashed.",
    },
    {
        "id": "FIN001",
        "category": "financial_data",
        "title": "IBAN-shaped strings",
        "pattern": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
        "weight": 8,
        "article": "Art. 4(1), Art. 32",
        "recommendation": "Remove real IBANs from code and fixtures; use documented test IBANs only.",
    },
    {
        "id": "FIN002",
        "category": "financial_data",
        "title": "Card-number-shaped strings",
        "pattern": r"\b(?:\d[ \-]?){12,18}\d\b",
        "validator": "luhn",
        "weight": 8,
        "article": "Art. 32, PCI-DSS 3.2",
        "recommendation": "Card data must never live in source or fixtures. Use processor tokens instead.",
    },
    # --- special category -------------------------------------------------
    {
        "id": "SPC001",
        "category": "special_category",
        "title": "Health data indicators",
        "keywords": [
            "diagnosis", "patient", "medical_record", "health_data", "icd10",
            "medication", "disability", "sick_leave", "krankheit", "gesundheit",
        ],
        "weight": 10,
        "article": "Art. 9(1)",
        "recommendation": (
            "Health data needs an Art. 9(2) condition plus Art. 32 safeguards. "
            "If this field is not strictly required, delete it."
        ),
    },
    {
        "id": "SPC002",
        "category": "special_category",
        "title": "Biometric or genetic data indicators",
        "keywords": ["biometric", "fingerprint", "face_id", "genetic", "dna_", "iris_scan"],
        "weight": 10,
        "article": "Art. 9(1)",
        "recommendation": "Biometric identification requires an explicit Art. 9(2) basis and usually a DPIA.",
    },
    {
        "id": "SPC003",
        "category": "special_category",
        "title": "Belief, ethnicity, or orientation indicators",
        "keywords": [
            "religion", "religious", "ethnicity", "ethnic_origin", "trade_union",
            "sexual_orientation", "political_opinion",
        ],
        "weight": 10,
        "article": "Art. 9(1)",
        "recommendation": "These fields are almost never necessary outside HR or research with a specific basis.",
    },
    # --- risky code practices ---------------------------------------------
    {
        "id": "RISK001",
        "category": "risky_practice",
        "title": "Personal data written to logs",
        "pattern": r"(?:logger?|log|console)\.(?:debug|info|warn|warning|error|log|exception)\s*\([^)\n]*(?:email|phone|password|token|ssn|iban|address|user\.|customer\.)",
        "weight": 10,
        "article": "Art. 5(1)(f), Art. 32",
        "recommendation": (
            "Log identifiers, not payloads. Redact or hash before logging; scrub "
            "existing log retention."
        ),
    },
    {
        "id": "RISK002",
        "category": "risky_practice",
        "title": "Bulk print/dump of user records",
        "pattern": r"(?:print|dump|pprint|var_dump)\s*\(\s*(?:user|customer|request\.body|req\.body|payload)",
        "weight": 8,
        "article": "Art. 5(1)(f)",
        "recommendation": "Remove debug dumps of request bodies; they carry every field the client sent.",
    },
    {
        "id": "RISK003",
        "category": "risky_practice",
        "title": "Indefinite retention marker",
        "pattern": r"(?i)(?:retention|retain|ttl|expires?)[\"']?\s*[:=]\s*[\"']?(?:none|null|nil|indefinite|forever|infinite|-1|0)[\"']?\s*[,}\n]",
        "weight": 10,
        "article": "Art. 5(1)(e)",
        "recommendation": "Set a concrete retention period and a deletion job. 'Indefinite' fails storage limitation.",
    },
    {
        "id": "RISK004",
        "category": "risky_practice",
        "title": "Hardcoded credential or API key",
        "pattern": r"(?i)(?:api[_-]?key|secret|password|passwd|token)[\"']?\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']",
        "weight": 12,
        "article": "Art. 32(1)(b)",
        "recommendation": "Move secrets to a vault or environment; rotate the exposed value.",
    },
    {
        "id": "RISK005",
        "category": "risky_practice",
        "title": "Personal data collected with no consent reference nearby",
        "pattern": r"(?i)(?:email|phone|newsletter)\s*[:=]\s*(?:request|req)\.(?:form|json|body|data)\[",
        "weight": 5,
        "article": "Art. 6(1)(a), Art. 7",
        "recommendation": (
            "Ensure a consent record (timestamp, version, wording) is stored next to "
            "the collected field, or that another Art. 6 basis covers it."
        ),
    },
    {
        "id": "RISK006",
        "category": "risky_practice",
        "title": "Third-country transfer indicator",
        "pattern": r"(?i)(?:https?://[^\s\"']*(?:\.cn|\.ru|\.in|\.br)\b|transfer(?:ring)?_to_us|s3\.amazonaws\.com)",
        "weight": 4,
        "article": "Art. 44-49",
        "recommendation": (
            "Document the transfer mechanism (adequacy decision, SCCs, BCRs) and "
            "re-check it -- adequacy decisions change."
        ),
    },
]

RISK_BANDS = [
    (85, "low", "No structural issues matched the rules. Verify legal bases by hand."),
    (65, "moderate", "Fixable findings: logging of PII, missing retention markers."),
    (40, "high", "Systemic problems: special category data or hardcoded PII without safeguards."),
    (0, "critical", "Likely unlawful processing. Escalate before shipping."),
]

COMPILED = []
for _rule in RULES:
    _c = dict(_rule)
    if "pattern" in _rule:
        _c["_regex"] = re.compile(_rule["pattern"])
    if "keywords" in _rule:
        _c["_keywords"] = re.compile(
            r"\b(?:" + "|".join(re.escape(k) for k in _rule["keywords"]) + r")\b",
            re.IGNORECASE,
        )
    COMPILED.append(_c)


def iter_files(root, excludes, include_tests):
    test_markers = ("/test/", "/tests/", "/spec/", "/specs/", "/__tests__/", "/fixtures/")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        for name in filenames:
            path = os.path.join(dirpath, name)
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXT_EXTS and name not in (".env", "Dockerfile", "Makefile"):
                continue
            if not include_tests:
                norm = path.replace(os.sep, "/")
                if any(m in norm for m in test_markers):
                    continue
                if re.search(r"(?:^|/)(?:test_.*|.*_test|.*\.test|.*\.spec)\.[a-z]+$", norm):
                    continue
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


def luhn_valid(number):
    """Luhn checksum -- keeps the card-number rule from flagging epochs and IDs."""
    digits = [int(c) for c in number if c.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


DATE_LIKE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$|^\d{1,2}\.\d{1,2}\.\d{2,4}$|^\d{1,3}(?:\.\d{1,3}){3}$")


def phone_valid(text):
    """Reject dates, versions, and dotted quads the shape regex would swallow."""
    text = text.strip()
    if DATE_LIKE.match(text):
        return False
    digits = sum(1 for c in text if c.isdigit())
    return 7 <= digits <= 15


def scan_file(path, rel, max_per_rule):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    hits = []
    for rule in COMPILED:
        regex = rule.get("_regex") or rule.get("_keywords")
        count = 0
        for lineno, line in enumerate(lines, 1):
            if len(line) > 2000:
                line = line[:2000]
            match = regex.search(line)
            if not match:
                continue
            if rule.get("validator") == "luhn" and not luhn_valid(match.group(0)):
                continue
            if rule.get("validator") == "phone" and not phone_valid(match.group(0)):
                continue
            count += 1
            if count <= max_per_rule:
                sample = match.group(0).strip()
                if len(sample) > SAMPLE_MAX:
                    sample = sample[:SAMPLE_MAX] + "..."
                hits.append(
                    {
                        "rule": rule["id"],
                        "category": rule["category"],
                        "title": rule["title"],
                        "article": rule["article"],
                        "file": rel,
                        "line": lineno,
                        "match": sample,
                        "recommendation": rule["recommendation"],
                        "weight": rule["weight"],
                    }
                )
        # record overflow so the count stays honest
        if count > max_per_rule:
            hits.append(
                {
                    "rule": rule["id"],
                    "category": rule["category"],
                    "title": rule["title"],
                    "article": rule["article"],
                    "file": rel,
                    "line": 0,
                    "match": f"... and {count - max_per_rule} more occurrence(s) of {rule['id']} in this file",
                    "recommendation": rule["recommendation"],
                    "weight": 0,
                    "overflow": True,
                }
            )
    return hits


def compute_score(findings):
    weight_by_rule = {r["id"]: r["weight"] for r in RULES}
    per_rule = {}
    for f in findings:
        if f.get("overflow"):
            continue
        per_rule[f["rule"]] = per_rule.get(f["rule"], 0) + 1

    deduction = 0.0
    for rule_id, count in per_rule.items():
        base = weight_by_rule.get(rule_id, 3)
        # first hit full weight, second half, third quarter, capped at 1.75x
        multiplier = sum(1.0 / (2 ** i) for i in range(min(count, 3)))
        deduction += base * multiplier

    return max(0, min(100, int(round(100 - deduction))))


def band_for(score):
    for threshold, label, meaning in RISK_BANDS:
        if score >= threshold:
            return label, meaning
    return "critical", RISK_BANDS[-1][2]


def build_report(root, findings, files_scanned, band, meaning, score):
    by_category = {}
    by_rule = {}
    for f in findings:
        by_category[f["category"]] = by_category.get(f["category"], 0) + 1
        if not f.get("overflow"):
            key = f["rule"]
            by_rule.setdefault(
                key,
                {
                    "rule": key,
                    "title": f["title"],
                    "article": f["article"],
                    "count": 0,
                    "recommendation": f["recommendation"],
                    "weight": f["weight"],
                },
            )
            by_rule[key]["count"] += 1

    recommendations = sorted(by_rule.values(), key=lambda r: -r["weight"] * r["count"])
    for rec in recommendations:
        rec.pop("weight", None)

    return {
        "tool": "gdpr_compliance_checker",
        "version": VERSION,
        "root": os.path.abspath(root),
        "files_scanned": files_scanned,
        "score": score,
        "risk_band": band,
        "risk_meaning": meaning,
        "finding_count": len(findings),
        "findings_by_category": by_category,
        "recommendations": recommendations,
        "findings": findings,
        "disclaimer": (
            "Triage output only. A clean score does not establish lawful processing; "
            "legal basis, retention, and transfers require DPO or counsel review."
        ),
    }


def print_text(report):
    print(f"GDPR/DSGVO compliance scan: {report['root']}")
    print(f"Files scanned: {report['files_scanned']}")
    print(
        f"Score: {report['score']}/100  [{report['risk_band'].upper()}]  "
        f"{report['risk_meaning']}"
    )
    print(f"Findings: {report['finding_count']}")
    if report["findings_by_category"]:
        print("\nBy category:")
        for cat, count in sorted(report["findings_by_category"].items(), key=lambda kv: -kv[1]):
            print(f"  {cat}: {count}")

    if report["findings"]:
        print("\nFindings:")
        for f in report["findings"]:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"  [{f['rule']}] {loc}  {f['title']} ({f['article']})")
            if f["match"]:
                print(f"      match: {f['match']}")

    if report["recommendations"]:
        print("\nPrioritized recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec['title']} -- {rec['article']} ({rec['count']}x)")
            print(f"     {rec['recommendation']}")

    print(f"\n{report['disclaimer']}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scan a codebase for GDPR/DSGVO risks. Stdlib only.",
    )
    parser.add_argument("path", nargs="?", default=".", help="directory to scan (default: .)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--fail-under",
        type=int,
        default=None,
        metavar="SCORE",
        help="exit 1 if the score is below this value (CI gate)",
    )
    parser.add_argument(
        "--max-per-rule",
        type=int,
        default=5,
        help="maximum locations printed per rule per file (default: 5)",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="also scan test and fixture directories (off by default)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="additional directory name to skip (repeatable)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.path):
        parser.error(f"not a directory: {args.path}")

    excludes = set(DEFAULT_EXCLUDES) | set(args.exclude)
    findings = []
    files_scanned = 0
    for path in iter_files(os.path.abspath(args.path), excludes, args.include_tests):
        rel = os.path.relpath(path, os.path.abspath(args.path))
        files_scanned += 1
        findings.extend(scan_file(path, rel, args.max_per_rule))

    findings.sort(key=lambda f: (f["file"], f["line"]))
    score = compute_score(findings)
    band, meaning = band_for(score)
    report = build_report(args.path, findings, files_scanned, band, meaning, score)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)

    if args.fail_under is not None and score < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
