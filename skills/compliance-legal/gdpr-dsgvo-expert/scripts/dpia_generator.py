#!/usr/bin/env python3
"""DPIA generator for GDPR Art. 35.

Performs the threshold assessment (Art. 35(3) triggers plus the WP248
nine-criteria test) and renders a Data Protection Impact Assessment document.

Standard library only. Python 3.8+.

A generated DPIA is a draft skeleton. The risk ratings and the residual-risk
acceptance are decisions for the controller and the DPO, not for this script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

VERSION = "0.1.0"

# WP248rev.01 criteria. Two or more generally means a DPIA is required.
WP248_CRITERIA = [
    ("evaluation", "Evaluation or scoring, including profiling and predicting"),
    ("automated_decision", "Automated decision-making with legal or similarly significant effect"),
    ("systematic_monitoring", "Systematic monitoring of data subjects"),
    ("sensitive_data", "Sensitive data or data of a highly personal nature (Art. 9, Art. 10)"),
    ("large_scale", "Data processed on a large scale"),
    ("dataset_matching", "Matching or combining datasets"),
    ("vulnerable_subjects", "Data concerning vulnerable data subjects"),
    ("innovative_technology", "Innovative use or application of new technological solutions"),
    ("rights_prevention", "Processing prevents data subjects from exercising a right or using a service"),
]

SPEC_TEMPLATE = {
    "project_name": "Customer analytics platform",
    "controller": "Example GmbH, Berlin",
    "dpo": "dpo@example.com",
    "author": "Privacy engineering",
    "date": "",
    "purposes": [
        "Personalise product recommendations",
        "Measure feature adoption",
    ],
    "data_categories": [
        "Account identifiers",
        "Email addresses",
        "Usage events",
        "Purchase history",
    ],
    "special_category": False,
    "special_category_detail": "",
    "public_area": False,
    "data_subjects": ["Customers", "Prospects"],
    "subject_count": 50000,
    "retention": "24 months from last activity, then deleted by scheduled job",
    "recipients": ["Analytics processor (EU-hosted)", "Payment processor"],
    "transfers": [],
    "legal_basis": "Art. 6(1)(b) contract for fulfilment; Art. 6(1)(f) legitimate interests for analytics",
    "criteria": {
        "evaluation": True,
        "automated_decision": False,
        "systematic_monitoring": True,
        "sensitive_data": False,
        "large_scale": True,
        "dataset_matching": True,
        "vulnerable_subjects": False,
        "innovative_technology": False,
        "rights_prevention": False,
    },
    "security_measures": [
        "Encryption at rest (AES-256) and in transit (TLS 1.3)",
        "Role-based access control with quarterly review",
        "Pseudonymised identifiers in the analytics store",
    ],
    "consultation_required": False,
}


def today():
    return dt.date.today().isoformat()


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    merged = dict(SPEC_TEMPLATE)
    merged["criteria"] = dict(SPEC_TEMPLATE["criteria"])
    merged.update(spec or {})
    if isinstance(spec.get("criteria"), dict):
        merged["criteria"] = dict(SPEC_TEMPLATE["criteria"], **spec["criteria"])
    if not merged.get("date"):
        merged["date"] = today()
    return merged


def spec_from_args(args):
    spec = dict(SPEC_TEMPLATE)
    # Flags start from a clean assessment -- never inherit the example's criteria.
    spec["criteria"] = {cid: False for cid, _ in WP248_CRITERIA}
    if args.name:
        spec["project_name"] = args.name
    if args.controller:
        spec["controller"] = args.controller
    if args.dpo:
        spec["dpo"] = args.dpo
    if args.purpose:
        spec["purposes"] = args.purpose
    if args.data_category:
        spec["data_categories"] = args.data_category
    if args.subjects:
        spec["data_subjects"] = args.subjects
    if args.subjects_count:
        spec["subject_count"] = args.subjects_count
    if args.retention:
        spec["retention"] = args.retention
    if args.legal_basis:
        spec["legal_basis"] = args.legal_basis
    if args.special_category:
        spec["special_category"] = True
        spec["criteria"]["sensitive_data"] = True
    if args.systematic_monitoring:
        spec["criteria"]["systematic_monitoring"] = True
    if args.automated_decision:
        spec["criteria"]["automated_decision"] = True
    if args.large_scale:
        spec["criteria"]["large_scale"] = True
    spec["date"] = today()
    spec["_minimal"] = True
    return spec


def assess(spec):
    """Return the threshold assessment dict."""
    criteria = spec.get("criteria", {})
    met = [cid for cid, _ in WP248_CRITERIA if criteria.get(cid)]
    if spec.get("special_category") and "sensitive_data" not in met:
        met.append("sensitive_data")

    triggers = []

    # Art. 35(3) statutory triggers
    if criteria.get("evaluation") and criteria.get("systematic_monitoring"):
        triggers.append(
            "Art. 35(3)(a): systematic and extensive evaluation of personal aspects "
            "based on automated processing, including profiling"
        )
    if criteria.get("large_scale") and (spec.get("special_category") or criteria.get("sensitive_data")):
        triggers.append(
            "Art. 35(3)(b): large-scale processing of Art. 9 special category data "
            "or Art. 10 criminal-conviction data"
        )
    if criteria.get("systematic_monitoring") and criteria.get("large_scale") and spec.get("public_area"):
        triggers.append(
            "Art. 35(3)(c): systematic monitoring of a publicly accessible area on a large scale"
        )

    # WP248 two-of-nine test
    wp248_required = len(met) >= 2

    required = bool(triggers) or wp248_required
    return {
        "criteria_met": met,
        "criteria_count": len(met),
        "criteria_detail": [
            {"id": cid, "description": desc, "met": criteria.get(cid, False)}
            for cid, desc in WP248_CRITERIA
        ],
        "art_35_3_triggers": triggers,
        "wp248_required": wp248_required,
        "dpia_required": required,
        "rationale": (
            f"{len(met)} of the nine WP248 criteria are met"
            + (" and an Art. 35(3) trigger applies" if triggers else "")
            + ". Two or more criteria generally require a DPIA."
            if required
            else f"Only {len(met)} of the nine WP248 criteria are met and no Art. 35(3) "
            "trigger applies. A DPIA is not mandatory; record this negative assessment."
        ),
    }


def risk_register(spec, assessment):
    """Derive risks from the declared processing characteristics."""
    risks = []
    criteria = spec.get("criteria", {})
    count = spec.get("subject_count") or 0

    def add(rid, area, desc, likelihood, severity, mitigation, article):
        risks.append(
            {
                "id": rid,
                "area": area,
                "description": desc,
                "likelihood": likelihood,
                "severity": severity,
                "mitigation": mitigation,
                "article": article,
            }
        )

    if criteria.get("sensitive_data") or spec.get("special_category"):
        add(
            "R-01",
            "Special category data",
            "Processing Art. 9 data without a specific condition or with wider access "
            "than the purpose requires.",
            "High",
            "High",
            "Confirm the Art. 9(2) condition per purpose, restrict access by role, "
            "encrypt at rest and in transit, and record the condition in the ROPA.",
            "Art. 9, Art. 32",
        )

    if criteria.get("automated_decision"):
        add(
            "R-02",
            "Automated decision-making",
            "Decisions with legal or similarly significant effect taken without "
            "meaningful human review, producing an unexplained adverse outcome.",
            "Medium",
            "High",
            "Provide Art. 22(3) safeguards: human intervention, an explanation of the "
            "logic, and a contest mechanism.",
            "Art. 22",
        )

    if criteria.get("systematic_monitoring"):
        add(
            "R-03",
            "Monitoring",
            "Subjects are unaware of the extent of monitoring, defeating transparency "
            "and creating a chilling effect.",
            "Medium",
            "Medium",
            "Layered notice at the point of collection, documented purpose limitation, "
            "and a defined observation window.",
            "Art. 5(1)(a), Art. 12-14",
        )

    if criteria.get("evaluation"):
        add(
            "R-04",
            "Profiling",
            "Profiles are inaccurate or applied outside the purpose they were built for.",
            "Medium",
            "Medium",
            "Validate model inputs, document feature provenance, and block reuse for "
            "incompatible purposes.",
            "Art. 5(1)(b), Art. 22",
        )

    if count >= 100000 or criteria.get("large_scale"):
        add(
            "R-05",
            "Scale",
            "A single defect affects a large population before it is detected.",
            "Medium",
            "High",
            "Staged rollout, anomaly alerting on access volume, and a tested incident "
            "response with a 72-hour notification path.",
            "Art. 33, Art. 34",
        )

    if criteria.get("dataset_matching"):
        add(
            "R-06",
            "Data combination",
            "Combining datasets creates a profile more intrusive than either source, "
            "or re-identifies pseudonymised records.",
            "Medium",
            "High",
            "Document the join keys, minimise the combined fields, and re-test "
            "re-identification risk after each new source.",
            "Art. 5(1)(c), Art. 6(4)",
        )

    if spec.get("transfers"):
        add(
            "R-07",
            "International transfer",
            "Transfer rests on an adequacy decision or SCCs that are outdated or "
            "not implemented in practice.",
            "Medium",
            "High",
            "Verify the current status of the mechanism, complete a transfer impact "
            "assessment, and record supplementary measures.",
            "Art. 44-49",
        )

    if criteria.get("vulnerable_subjects"):
        add(
            "R-08",
            "Vulnerable subjects",
            "Children, employees, or patients cannot freely refuse, so consent or "
            "objection is not meaningful.",
            "High",
            "High",
            "Use a basis other than consent where power is imbalanced and add "
            "age-appropriate or works-council safeguards.",
            "Art. 7, Art. 8, recital 43",
        )

    if not spec.get("retention") or "indefinite" in str(spec.get("retention", "")).lower():
        add(
            "R-09",
            "Retention",
            "Data held without a defined deletion point accumulates beyond the purpose.",
            "High",
            "Medium",
            "Define a retention period per data category and implement a tested "
            "deletion job including backups.",
            "Art. 5(1)(e), Art. 17",
        )

    if not risks:
        add(
            "R-10",
            "Baseline",
            "Ordinary confidentiality and integrity risk for stored personal data.",
            "Low",
            "Medium",
            "Apply access control, encryption, and audit logging; review annually.",
            "Art. 32",
        )

    return risks


def render_markdown(spec, assessment, risks):
    L = []
    a = L.append
    a(f"# Data Protection Impact Assessment — {spec['project_name']}")
    a("")
    a(f"**Controller:** {spec.get('controller', 'not specified')}  ")
    a(f"**DPO:** {spec.get('dpo', 'not specified')}  ")
    a(f"**Author:** {spec.get('author', 'not specified')}  ")
    a(f"**Date:** {spec.get('date', today())}  ")
    a(f"**Version:** 1.0 (draft for DPO review)")
    a("")
    a("> This DPIA was assembled from a declared processing description. The risk")
    a("> ratings and the residual-risk acceptance must be reviewed and signed by the")
    a("> Data Protection Officer. It is not legal advice.")
    a("")

    a("## 1. Threshold Assessment (Art. 35)")
    a("")
    a(f"**DPIA required:** {'YES' if assessment['dpia_required'] else 'NO'}")
    a("")
    a(assessment["rationale"])
    a("")
    a("| Criterion (WP248) | Met |")
    a("|---|---|")
    for c in assessment["criteria_detail"]:
        a(f"| {c['description']} | {'yes' if c['met'] else 'no'} |")
    a("")
    if assessment["art_35_3_triggers"]:
        a("**Art. 35(3) triggers:**")
        a("")
        for t in assessment["art_35_3_triggers"]:
            a(f"- {t}")
        a("")
    if not assessment["dpia_required"]:
        a("No trigger fired. Keep this section as the documented negative assessment and")
        a("re-assess if the processing, its scale, or its data categories change.")
        a("")

    a("## 2. Systematic Description of the Processing (Art. 35(7)(a))")
    a("")
    a("### Purposes")
    a("")
    for p in spec.get("purposes") or ["not specified"]:
        a(f"- {p}")
    a("")
    a("### Data categories")
    a("")
    for d in spec.get("data_categories") or ["not specified"]:
        a(f"- {d}")
    if spec.get("special_category"):
        a(f"- **Special category (Art. 9):** {spec.get('special_category_detail') or 'declared, detail missing — fill in'}")
    a("")
    a("### Data subjects")
    a("")
    for s in spec.get("data_subjects") or ["not specified"]:
        a(f"- {s}")
    a("")
    a(f"**Approximate number of data subjects:** {spec.get('subject_count', 'not specified')}")
    a("")
    a(f"**Retention:** {spec.get('retention', 'not specified')}")
    a("")
    a("### Recipients and processors")
    a("")
    for r in spec.get("recipients") or ["none declared"]:
        a(f"- {r}")
    a("")
    a("### International transfers")
    a("")
    if spec.get("transfers"):
        for t in spec["transfers"]:
            a(f"- {t} — mechanism must be documented (adequacy decision, SCCs, BCRs)")
    else:
        a("- None declared.")
    a("")
    a("### Data flow")
    a("")
    a("```")
    a("collection point -> primary store -> processing -> derived stores -> deletion")
    a("```")
    a("")
    a("Fill in the concrete systems and confirm the deletion step is automated and tested.")
    a("")

    a("## 3. Necessity and Proportionality (Art. 35(7)(b))")
    a("")
    a(f"**Legal basis:** {spec.get('legal_basis', 'not specified')}")
    a("")
    a("| Question | Assessment |")
    a("|---|---|")
    a("| Is each data category necessary for the stated purpose? | to complete |")
    a("| Could the purpose be achieved with less data or less granular data? | to complete |")
    a("| Is the retention period the shortest defensible one? | to complete |")
    a("| Are the data subjects' reasonable expectations respected? | to complete |")
    a("| Is there a less intrusive alternative (aggregation, on-device processing)? | to complete |")
    a("")

    a("## 4. Risks to Rights and Freedoms (Art. 35(7)(c))")
    a("")
    a("| ID | Area | Risk | Likelihood | Severity | Mitigation | Reference |")
    a("|---|---|---|---|---|---|---|")
    for r in risks:
        a(
            f"| {r['id']} | {r['area']} | {r['description']} | {r['likelihood']} | "
            f"{r['severity']} | {r['mitigation']} | {r['article']} |"
        )
    a("")

    a("## 5. Measures Envisaged (Art. 35(7)(d))")
    a("")
    for m in spec.get("security_measures") or ["not specified"]:
        a(f"- {m}")
    a("")
    a("Add: access-review cadence, logging and monitoring, incident response contact,")
    a("and the deletion verification method.")
    a("")

    a("## 6. Residual Risk and Sign-off")
    a("")
    a("| Risk ID | Residual likelihood | Residual severity | Accepted? | Owner |")
    a("|---|---|---|---|---|")
    for r in risks:
        a(f"| {r['id']} | | | | |")
    a("")
    a("Residual risk is high where a risk remains high after mitigation. If residual")
    a("risk cannot be reduced to an acceptable level, Art. 36 requires prior")
    a("consultation with the supervisory authority before processing begins.")
    a("")
    a("**DPO opinion:** ____________________________________  Date: ____________")
    a("")
    a("**Controller decision:** _____________________________  Date: ____________")
    a("")

    a("## 7. Review")
    a("")
    a("Art. 35(11) requires review when the risk changes — new data sources, new")
    a("recipients, a scale change, or a change in the legal framework. Set a review")
    a("date now:")
    a("")
    a(f"**Next review:** {(dt.date.fromisoformat(spec['date']) + dt.timedelta(days=365)).isoformat()}")
    a("")
    return "\n".join(L)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assess DPIA thresholds and generate a GDPR Art. 35 DPIA document.",
    )
    parser.add_argument("--spec", help="JSON processing description (see --template)")
    parser.add_argument("--template", action="store_true", help="print an example spec JSON and exit")
    parser.add_argument("--output", "-o", help="write to this file instead of stdout")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="markdown document (default) or the assessment as JSON",
    )
    parser.add_argument("--name", help="project name")
    parser.add_argument("--controller", help="controller name and address")
    parser.add_argument("--dpo", help="DPO contact")
    parser.add_argument("--purpose", action="append", help="processing purpose (repeatable)")
    parser.add_argument("--data-category", action="append", help="data category (repeatable)")
    parser.add_argument("--subjects", action="append", help="data subject group (repeatable)")
    parser.add_argument("--subjects-count", type=int, help="approximate number of data subjects")
    parser.add_argument("--retention", help="retention period")
    parser.add_argument("--legal-basis", help="legal basis per purpose")
    parser.add_argument("--special-category", action="store_true", help="Art. 9 data is processed")
    parser.add_argument("--systematic-monitoring", action="store_true")
    parser.add_argument("--automated-decision", action="store_true")
    parser.add_argument("--large-scale", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    if args.template:
        print(json.dumps(SPEC_TEMPLATE, indent=2))
        return 0

    if args.spec:
        try:
            spec = load_spec(args.spec)
        except (OSError, ValueError) as exc:
            print(f"error: cannot read spec {args.spec}: {exc}", file=sys.stderr)
            return 2
    else:
        spec = spec_from_args(args)
        if not args.name:
            print(
                "note: no --spec and no --name given; generating the example DPIA.",
                file=sys.stderr,
            )

    assessment = assess(spec)
    risks = risk_register(spec, assessment)

    if args.format == "json":
        payload = {
            "tool": "dpia_generator",
            "version": VERSION,
            "project_name": spec["project_name"],
            "date": spec["date"],
            "assessment": assessment,
            "risk_count": len(risks),
            "risks": risks,
            "disclaimer": "Assessment support only; the DPIA determination belongs to the DPO.",
        }
        out = json.dumps(payload, indent=2)
    else:
        out = render_markdown(spec, assessment, risks)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"wrote {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
