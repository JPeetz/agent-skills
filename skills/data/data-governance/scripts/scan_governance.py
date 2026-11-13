#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Governance coverage scanner for dbt projects.

Reads a dbt `target/manifest.json` (and optionally an owners registry) and scores
governance metadata coverage without connecting to the warehouse. Designed to run
in CI as a ratchet: it exits non-zero when the score falls below --min-score.

Checks per model
  - description present (>= --min-desc chars)
  - owner declared in meta.owner and known to the owners registry
  - classification in {public, internal, confidential, restricted}
  - retention declared
  - tier-1 models have column-level data tests
  - columns tagged pii: true declare a masking strategy

Usage
  python3 scan_governance.py target/manifest.json [--owners governance/owners.yml]
                             [--min-score 80] [--tier1-only] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
BASE_WEIGHTS = {"description": 25.0, "owner": 30.0, "classification": 25.0, "retention": 20.0}


def load_yaml(path: Path | None):
    """Load the owners registry. PyYAML is optional — fall back to a minimal
    parser so the scanner still runs in bare CI images."""
    if path is None:
        return None
    text = path.read_text()
    try:
        import yaml  # noqa: PLC0415

        return yaml.safe_load(text) or {}
    except ImportError:
        return _mini_yaml(text)


def _mini_yaml(text: str) -> dict:
    """Parse the flat two-level shape of governance/owners.yml without PyYAML."""
    root: dict = {"domains": {}}
    current = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip() or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip())
        key, _, value = line.strip().partition(":")
        value = value.strip().strip("\"'")
        if indent == 0:
            if key == "domains":
                continue
            root[key] = value
            continue
        if indent <= 2:
            current = key
            root["domains"][current] = {}
            continue
        if current:
            root["domains"][current][key] = value
    return root


def known_owners(registry: dict | None) -> set[str]:
    """Collect every valid owner handle from governance/owners.yml."""
    if not registry:
        return set()
    owners: set[str] = set()
    for domain, cfg in (registry.get("domains") or {}).items():
        owners.add(domain)
        if isinstance(cfg, dict):
            for key in ("owner", "accountable", "steward"):
                if cfg.get(key):
                    owners.add(str(cfg[key]))
    return owners


def node_meta(node: dict) -> dict:
    """dbt puts user meta in node.meta and (sometimes) node.config.meta."""
    meta: dict = {}
    meta.update(node.get("config", {}).get("meta") or {})
    meta.update(node.get("meta") or {})
    return meta


def has_tests(node_id: str, tests: list[dict]) -> bool:
    return any(node_id in (t.get("depends_on", {}).get("nodes") or []) for t in tests)


def scan(manifest: dict, owners: set[str], min_desc: int) -> dict:
    nodes = manifest.get("nodes", {}) or {}
    models = {k: v for k, v in nodes.items() if v.get("resource_type") == "model"}
    tests = [v for v in nodes.values() if v.get("resource_type") == "test"]

    findings: list[dict] = []
    for node_id, node in sorted(models.items()):
        meta = node_meta(node)
        tier = str(meta.get("tier", "")).strip()
        issues: list[str] = []
        earned = 0.0

        desc = (node.get("description") or "").strip()
        if len(desc) >= min_desc:
            earned += BASE_WEIGHTS["description"]
        else:
            issues.append("missing_description")

        owner = str(meta.get("owner", "")).strip()
        if owner and (not owners or owner in owners):
            earned += BASE_WEIGHTS["owner"]
        elif owner:
            issues.append(f"unknown_owner:{owner}")
        else:
            issues.append("missing_owner")

        classification = str(meta.get("classification", "")).strip().lower()
        if classification in CLASSIFICATIONS:
            earned += BASE_WEIGHTS["classification"]
        elif classification:
            issues.append(f"invalid_classification:{classification}")
        else:
            issues.append("missing_classification")

        if str(meta.get("retention", "")).strip():
            earned += BASE_WEIGHTS["retention"]
        else:
            issues.append("missing_retention")

        columns = node.get("columns") or {}
        pii_cols = [
            name
            for name, col in columns.items()
            if (col.get("meta") or {}).get("pii") in (True, "true", "True")
        ]
        unmasked = [
            name
            for name in pii_cols
            if not (columns[name].get("meta") or {}).get("masking")
        ]
        if unmasked:
            issues.append("pii_without_masking:" + ",".join(sorted(unmasked)))

        tier1_without_tests = tier == "1" and not has_tests(node_id, tests)
        if tier1_without_tests:
            issues.append("tier1_without_tests")

        findings.append(
            {
                "model": node.get("name", node_id),
                "unique_id": node_id,
                "tier": tier or None,
                "score": round(earned, 1),
                "pii_columns": sorted(pii_cols),
                "issues": issues,
            }
        )

    scored = [f for f in findings if f["score"] is not None]
    total = round(sum(f["score"] for f in scored) / len(scored), 1) if scored else 0.0
    tier1 = [f for f in scored if f["tier"] == "1"]
    tier1_score = (
        round(sum(f["score"] for f in tier1) / len(tier1), 1) if tier1 else 0.0
    )
    blocking = [
        f
        for f in scored
        if any(
            i.startswith(("pii_without_masking", "unknown_owner", "tier1_without_tests"))
            for i in f["issues"]
        )
    ]

    return {
        "models_scanned": len(scored),
        "tier1_models": len(tier1),
        "overall_score": total,
        "tier1_score": tier1_score,
        "models_below_threshold": len([f for f in scored if f["score"] < 100]),
        "blocking_findings": len(blocking),
        "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Scan dbt manifest for governance coverage")
    ap.add_argument("manifest", type=Path, help="path to target/manifest.json")
    ap.add_argument("--owners", type=Path, default=None, help="governance/owners.yml")
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--min-desc", type=int, default=20)
    ap.add_argument("--tier1-only", action="store_true", help="only print tier-1 findings")
    ap.add_argument("--json", dest="json_out", type=Path, default=None)
    args = ap.parse_args()

    if not args.manifest.exists():
        sys.exit(f"manifest not found: {args.manifest}")
    manifest = json.loads(args.manifest.read_text())
    report = scan(manifest, known_owners(load_yaml(args.owners)), args.min_desc)

    print(f"models scanned : {report['models_scanned']}")
    print(f"tier-1 models  : {report['tier1_models']}")
    print(f"overall score  : {report['overall_score']}/100")
    print(f"tier-1 score   : {report['tier1_score']}/100")
    print(f"blocking       : {report['blocking_findings']}\n")
    for f in report["findings"]:
        if args.tier1_only and f["tier"] != "1":
            continue
        if f["issues"]:
            print(f"  {f['score']:5.1f}  {f['model']:<40} {'; '.join(f['issues'])}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2))

    if report["overall_score"] < args.min_score:
        print(f"\nFAIL: score {report['overall_score']} < min {args.min_score}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
