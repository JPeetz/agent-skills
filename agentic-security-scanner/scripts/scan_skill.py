#!/usr/bin/env python3
"""
Agentic Security Scanner — OWASP AST10 Compliance Scanner
Scans agent skill directories for security vulnerabilities.

Usage:
    python3 scan_skill.py --skill-dir <path> [--format json|sarif|text] [--output <file>]
    python3 scan_skill.py --skill-dir <path> --max-score 60 --ci  # exit 1 if score > max
"""
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    ast_id: str
    title: str
    severity: Severity
    file_path: str
    line_number: int
    description: str
    remediation: str
    confidence: str = "confirmed"


@dataclass
class ScanResult:
    skill_name: str
    skill_dir: str
    score: int
    risk_tier: str
    findings: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def risk_label(self) -> str:
        if self.score <= 20:
            return "L0 (Safe)"
        elif self.score <= 40:
            return "L1 (Low)"
        elif self.score <= 60:
            return "L2 (Elevated)"
        elif self.score <= 80:
            return "L3 (High)"
        return "Critical"


class SkillScanner:
    DANGEROUS_PATTERNS = [
        # AST01: Malicious patterns
        (r"curl\s+.*\|\s*(?:ba)?sh", "AST01", Severity.CRITICAL,
         "Pipe-to-shell from remote URL detected", "Remove remote pipe-to-shell; use verified local scripts"),
        (r"eval\s*\(.*\$", "AST01", Severity.HIGH,
         "eval() with dynamic input", "Replace eval() with safe alternatives"),
        (r"base64\s+-d.*\|", "AST01", Severity.HIGH,
         "Base64 decode piped to command", "Remove obfuscated command execution"),
        # AST03: Data exfiltration
        (r"(?:curl|wget).*-[sS].*\$\{?(?:API_KEY|TOKEN|SECRET|PASSWORD)", "AST03", Severity.CRITICAL,
         "Potential secret exfiltration in network call", "Never include secrets in network requests"),
        (r"(?:\.env|credentials|secrets).*>\s*(?:/tmp|/dev/tcp)", "AST03", Severity.HIGH,
         "Writing secrets to unsecured location", "Use secure credential storage"),
        # AST06: Insecure script execution
        (r"subprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True", "AST06", Severity.HIGH,
         "Subprocess with shell=True (injection risk)", "Use shell=False with argument lists"),
        (r"os\.system\s*\(.*\$", "AST06", Severity.MEDIUM,
         "os.system() with dynamic input", "Use subprocess.run with shell=False"),
    ]

    PROTECTED_FILES = ["SOUL.md", "MEMORY.md", "AGENTS.md", "IDENTITY.md", "USER.md"]

    def scan(self, skill_dir: str) -> ScanResult:
        path = Path(skill_dir)
        if not path.exists():
            raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

        result = ScanResult(
            skill_name=path.name,
            skill_dir=str(path),
            score=0,
            risk_tier="L0",
        )

        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            result.findings.append(Finding(
                "AST07", "Missing SKILL.md", Severity.CRITICAL,
                str(path), 0,
                "No SKILL.md file found — skill is missing its manifest",
                "Create a SKILL.md file with required frontmatter"
            ))
            result.score = 100
            return result

        content = skill_md.read_text()
        lines = content.split("\n")

        # Check for YAML frontmatter
        self._check_frontmatter(result, content, skill_md)

        # Check file permissions
        self._check_permissions(result, content, skill_md)

        # Scan all files for dangerous patterns
        self._scan_patterns(result, path)

        # Check for integrity fields
        self._check_integrity(result, content, skill_md)

        # Calculate score
        result.score = self._calculate_score(result)
        return result

    def _check_frontmatter(self, result: ScanResult, content: str, path: Path):
        if not content.startswith("---"):
            result.findings.append(Finding(
                "AST07", "Missing YAML frontmatter", Severity.HIGH,
                str(path), 1,
                "SKILL.md must start with YAML frontmatter containing metadata",
                "Add --- delimited YAML frontmatter with name, version, permissions"
            ))
            return

        # Check for required fields
        for field in ["name:", "version:", "description:"]:
            if field not in content[:1000]:
                result.findings.append(Finding(
                    "AST07", f"Missing required field: {field.rstrip(':')}",
                    Severity.MEDIUM,
                    str(path), 0,
                    f"Frontmatter missing required field '{field.rstrip(':')}'",
                    f"Add '{field}' to YAML frontmatter"
                ))

    def _check_permissions(self, result: ScanResult, content: str, path: Path):
        # AST04: Excessive permissions
        if "permissions:" not in content.lower():
            result.findings.append(Finding(
                "AST04", "Missing permissions declaration", Severity.HIGH,
                str(path), 0,
                "No permissions block found — skill may have unrestricted access",
                "Add explicit permissions.files and permissions.network blocks"
            ))
            return

        # Check for wildcards in file permissions
        if re.search(r'read:\s*\[.*"\*"', content):
            result.findings.append(Finding(
                "AST04", "Wildcard file read permission", Severity.HIGH,
                str(path), 0,
                "Unrestricted file read access — violates least privilege",
                "Specify explicit file paths instead of wildcards"
            ))

        if re.search(r'write:\s*\[.*"\*"', content):
            result.findings.append(Finding(
                "AST08", "Wildcard file write permission", Severity.CRITICAL,
                str(path), 0,
                "Unrestricted file write access — can modify any file",
                "Specify explicit write paths; add deny_write for protected files"
            ))

        # Check for protected files in deny_write
        if "deny_write:" in content:
            for protected in self.PROTECTED_FILES:
                if protected.lower() not in content.lower():
                    result.warnings.append(
                        f"Protected file '{protected}' not in deny_write list"
                    )
        else:
            result.findings.append(Finding(
                "AST08", "Missing deny_write for protected files", Severity.MEDIUM,
                str(path), 0,
                "No deny_write list — SOUL.md, MEMORY.md, AGENTS.md may be writable",
                "Add deny_write with protected identity files"
            ))

        # AST09: Network permissions
        if "network:" in content:
            if re.search(r'allow:\s*\[.*"\*"', content):
                result.findings.append(Finding(
                    "AST09", "Wildcard network allowlist", Severity.HIGH,
                    str(path), 0,
                    "Network allowlist contains wildcard — all domains allowed",
                    "Specify explicit domain allowlist; use deny: '*' as default"
                ))
            if 'deny:' not in content or '"*"' not in content:
                result.warnings.append("Network deny not set to '*' — non-allowlisted domains may be accessible")
        else:
            result.findings.append(Finding(
                "AST09", "Missing network permissions declaration", Severity.MEDIUM,
                str(path), 0,
                "No network permissions block — egress may be unrestricted",
                "Add permissions.network with allow/deny domain lists"
            ))

    def _scan_patterns(self, result: ScanResult, skill_dir: Path):
        for file_path in skill_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in [".md", ".py", ".sh", ".js", ".ts", ".yaml", ".yml", ".json"]:
                continue
            try:
                content = file_path.read_text()
            except Exception:
                continue

            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                for pattern, ast_id, severity, desc, remediation in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip if pattern is in a comment/example in docs
                        rel_path = str(file_path.relative_to(skill_dir))
                        result.findings.append(Finding(
                            ast_id, desc, severity,
                            rel_path, i,
                            f"Detected in line: {line.strip()[:100]}",
                            remediation
                        ))

    def _check_integrity(self, result: ScanResult, content: str, path: Path):
        if "content_hash:" not in content and "signature:" not in content:
            result.findings.append(Finding(
                "AST07", "Missing content integrity fields", Severity.LOW,
                str(path), 0,
                "No content_hash or signature found — skill cannot be verified for tampering",
                "Add content_hash (SHA-256) and signature (Ed25519) to frontmatter"
            ))

    def _calculate_score(self, result: ScanResult) -> int:
        weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 0,
        }
        score = sum(weights[f.severity] for f in result.findings)
        return min(score, 100)


def format_output(result: ScanResult, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({
            "skill": result.skill_name,
            "score": result.score,
            "risk_tier": result.risk_label,
            "findings": [
                {
                    "id": f.ast_id,
                    "title": f.title,
                    "severity": f.severity.value,
                    "file": f.file_path,
                    "line": f.line_number,
                    "description": f.description,
                    "remediation": f.remediation,
                }
                for f in result.findings
            ],
            "warnings": result.warnings,
        }, indent=2)

    elif fmt == "sarif":
        return json.dumps({
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Agentic Security Scanner",
                        "version": "1.0.0",
                        "rules": [
                            {"id": f"AST{i:02d}", "name": f"OWASP AST{i:02d}"}
                            for i in range(1, 11)
                        ]
                    }
                },
                "results": [
                    {
                        "ruleId": f.ast_id,
                        "level": "error" if f.severity in [Severity.CRITICAL, Severity.HIGH] else "warning",
                        "message": {"text": f.description},
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {"uri": f.file_path},
                                "region": {"startLine": f.line_number}
                            }
                        }],
                        "properties": {
                            "remediation": f.remediation,
                            "severity": f.severity.value,
                        }
                    }
                    for f in result.findings
                ]
            }]
        }, indent=2)

    else:  # text
        lines = [
            f"🔍 Scan Report: {result.skill_name}",
            f"{'='*50}",
            f"Score: {result.score}/100 — {result.risk_label}",
            f"Findings: {len(result.findings)}",
            f"Warnings: {len(result.warnings)}",
            "",
        ]
        if result.findings:
            lines.append("Findings:")
            for f in result.findings:
                lines.append(f"  [{f.ast_id}] {f.severity.value.upper()}: {f.title}")
                lines.append(f"    File: {f.file_path}:{f.line_number}")
                lines.append(f"    {f.description}")
                lines.append(f"    Fix: {f.remediation}")
                lines.append("")
        if result.warnings:
            lines.append("Warnings:")
            for w in result.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="OWASP AST10 Skill Security Scanner")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    parser.add_argument("--format", choices=["json", "sarif", "text"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", help="Write output to file")
    parser.add_argument("--max-score", type=int, default=100,
                        help="Exit with code 1 if score exceeds this (CI gate)")
    args = parser.parse_args()

    scanner = SkillScanner()
    result = scanner.scan(args.skill_dir)
    output = format_output(result, args.format)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    if result.score > args.max_score:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
