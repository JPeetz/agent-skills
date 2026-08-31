---
name: agentic-security-scanner
description: >-
  Scan and validate AI agent skills against the OWASP Agentic Skills Top 10
  (AST10) security framework. Detects malicious skills, prompt injection,
  data exfiltration, supply chain risks, and cross-platform metadata loss.
  Provides CI/CD-ready security gating with SARIF output.
version: 1.0.0
platforms: [openclaw, claude, codex, cursor, gemini, copilot, opencode, windsurf]
author:
  name: Skill Foundry (Forge)
  source: OWASP Agentic Skills Top 10, SkillSpector Scanner
license: MIT
risk_tier: L1
tags: [security, owasp, scanner, ast10, compliance, supply-chain, ci-cd]
requires:
  binaries: [jq, python3]
---

# Agentic Security Scanner

Scan and validate AI agent skills against the OWASP Agentic Skills Top 10
(AST10) — the definitive security framework for agent skill ecosystems.
Detect malicious skills, prompt injection sinks, data exfiltration paths,
supply chain risks, and cross-platform metadata loss before skills are
installed or published.

## When to Use This Skill

Use this skill when:
- Auditing a new or existing skill before installation
- Setting up CI/CD security gates for a skill repository
- Reviewing a third-party skill for security compliance
- Building a skill registry that requires security validation
- Investigating a security incident involving agent skills
- Any request like "scan this skill for security issues", "OWASP audit",
  "is this skill safe?", "validate skill security"

## The OWASP AST10 Framework

The OWASP Agentic Skills Top 10 (AST10) defines the 10 most critical
security risks in AI agent skills across all major platforms:
OpenClaw (`SKILL.md`), Claude Code (`skill.json`), Cursor/Codex
(`manifest.json`), and VS Code (`package.json`).

### AST01 — Malicious Skills

Skills that contain hidden destructive commands, backdoors, or malware.
- **Detection:** Scan for obfuscated shell commands, eval() calls,
  encoded payloads, suspicious curl/wget patterns
- **Risk:** Remote code execution on skill installation or invocation
- **CVEs:** CVE-2025-59536 (CVSS 8.7), CVE-2026-21852 (CVSS 5.3)

### AST02 — Prompt Injection in Skill Instructions

Skills with instructions that can be overridden by user input, causing
the agent to execute unintended actions.
- **Detection:** Check for unparameterized instruction templates,
  missing input sanitization, trust of external content
- **Risk:** Agent follows attacker-controlled instructions instead of
  skill author intent

### AST03 — Data Exfiltration via Skills

Skills that send sensitive data (env vars, API keys, source code) to
external endpoints without disclosure.
- **Detection:** Find network calls in skill scripts, check for
  unrestricted file read permissions, audit telemetry endpoints
- **Risk:** Secrets leakage, intellectual property theft

### AST04 — Excessive Permissions

Skills requesting broader permissions than their stated purpose requires.
- **Detection:** Compare declared permissions vs. actual usage
- **Risk:** Privilege escalation, lateral movement

### AST05 — Dependency Chain Attacks

Skills depending on unverified packages, unpinned versions, or
compromised repositories.
- **Detection:** Audit `requires.binaries`, `requires.packages`,
  check version pinning, verify dependency integrity
- **Risk:** Supply chain compromise through transitive dependencies

### AST06 — Insecure Script Execution

Skills executing scripts without sandboxing, input validation, or
output verification.
- **Detection:** Find shell-out patterns, unchecked script arguments,
  missing shebang validation
- **Risk:** Command injection through crafted inputs

### AST07 — Missing Integrity Verification

Skills without content hashes, signatures, or provenance records.
- **Detection:** Verify `content_hash`, `signature` fields present
  and valid in skill metadata
- **Risk:** Tampered skills installed undetected

### AST08 — Unsafe File Operations

Skills reading or writing files outside declared paths, using wildcards,
or accessing identity files (SOUL.md, MEMORY.md).
- **Detection:** Check `permissions.files.read` and `deny_write` for
  wildcards, verify no access to protected paths
- **Risk:** Identity corruption, configuration tampering

### AST09 — Network Egress Without Allowlisting

Skills opening network connections without declared domain allowlists.
- **Detection:** Check `permissions.network.allow` and `deny` fields,
  verify no catch-all patterns
- **Risk:** C2 communication, data exfiltration

### AST10 — Cross-Platform Metadata Loss

Security metadata weakened or lost when porting skills between platforms.
- **Detection:** Compare skill manifests across platform formats,
  verify all security fields survive translation
- **Risk:** Skills appear safe on one platform, dangerous on another

## Scanner Workflow

### Phase 1: Static Analysis

Run the scanner to produce a 0-100 risk score and AST01-AST10 mapping:

```
python3 scripts/scan_skill.py --skill-dir <path> --format sarif --output results.sarif
```

The scanner checks:
1. **Manifest completeness** — All security fields present
2. **Permission audit** — Permissions match stated purpose
3. **Dependency integrity** — Binaries, packages verified
4. **Script safety** — No dangerous patterns in scripts
5. **File access boundaries** — No path traversal or wildcards
6. **Network boundaries** — Domain allowlist enforcement
7. **Content integrity** — Hashes and signatures present
8. **Cross-platform fidelity** — No metadata loss across formats

### Phase 2: Risk Classification

| Score | Risk Tier | Action |
|-------|-----------|--------|
| 0-20  | L0 (Safe) | Allow installation |
| 21-40 | L1 (Low) | Review recommended |
| 41-60 | L2 (Elevated) | Manual review required |
| 61-80 | L3 (High) | Block until remediated |
| 81-100 | Critical | Reject permanently |

### Phase 3: CI/CD Integration

**GitHub Actions gate:**
```yaml
- name: Scan Skills
  run: |
    for skill in skills/*/; do
      python3 scripts/scan_skill.py --skill-dir "$skill" \
        --format sarif --output "results/$(basename $skill).sarif"
    done
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results/
- name: Gate on Score
  run: |
    python3 scripts/gate_score.py --max-score 60 --results-dir results/
```

### Phase 4: Remediation Guidance

For each finding, the scanner produces:
1. AST10 category and severity
2. File path and line number
3. Description of the risk
4. Concrete fix with code example
5. Verification command to confirm fix

## Installation

```bash
# Clone to your agent's skills directory
git clone https://github.com/skill-foundry/agentic-security-scanner.git \
  ~/.agents/skills/agentic-security-scanner

# Or via npx
npx skills add skill-foundry/agentic-security-scanner
```

## References

- OWASP Agentic Skills Top 10: https://owasp.org/www-project-agentic-skills-top-10
- SkillSpector Scanner: https://github.com/owasp/www-project-agentic-skills-top-10
- CVE-2025-59536: Claude Code RCE via repository-level config
- CVE-2026-21852: Claude Code API key exfiltration
- Universal Agentic Skill Format v1.0 (AST10 solution)

## Platform Notes

- **OpenClaw:** Validates `SKILL.md` YAML frontmatter with permissions block
- **Claude Code:** Validates `skill.json` and `.claude/skills/` directory structure
- **Cursor/Codex:** Validates `manifest.json` with tool declarations
- **VS Code:** Validates `package.json` extension contributions
- **Gemini CLI:** Validates skill directory with progressive disclosure metadata
