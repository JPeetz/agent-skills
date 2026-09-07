---
name: "clean-pro-review-gates"
description: "Combined 5-gate review framework that catches AI-generated code failures before shipping — code quality (15 LLM failure modes), tests, docs, security (OWASP Top 10:2025/CWE Top 25/LLM Top 10), and CI/CD/container/IaC hardening. Use when reviewing any AI-generated or modified code, tests, docs, or infrastructure before merging. Each gate maps violations to published research on how LLMs systematically fail."
version: "1.0.0"
author: "JPeetz (adapted from Khaled Ghallab)"
license: "MIT"
metadata:
  hermes:
    tags: [code-review, quality-gate, security, lsm-failure-modes, test-review, docs-review, infra-hardening, owasp, pre-merge, review-gate]
    related_skills: [github-code-review, systematic-debugging, test-driven-development, requesting-code-review, github-pr-workflow]
---

# clean-pro-review-gates — Unified 5-Gate Review Framework

## Overview

This is a **combined meta-skill** that integrates five review gates into a single, unified framework. It catches the systematic ways AI coding agents produce bad code, tests, documentation, security holes, and insecure infrastructure — each rule traced to a primary source (Clean Code, SOLID, OWASP, CWE) or published 2022–2026 research on LLM code generation.

Generic "follow clean code" instructions don't catch what LLMs actually get wrong. This skill adds the AI-specific layer: swallowed exceptions, hallucinated APIs, mock fallbacks declared as success, over-eager abstraction, docs written from memory instead of from the source, test bloat that asserts implementation instead of behavior, and plausible-but-insecure code that ships injection, missing authorization, and slopsquatted dependencies.

The security gate also covers code that *calls* LLMs — prompt-injection containment, model output treated as untrusted input, agent-tool least privilege, prompt secrets, consumption caps, and RAG tenant isolation — mapped to the OWASP LLM Top 10.

## The Five Gates

| Gate | What It Guards | When to Apply | Reference |
|------|---------------|---------------|-----------|
| **GATE 1: Code Quality** | Production code — Clean Code, SOLID, DRY/KISS/YAGNI, plus 15 documented LLM failure modes | After an agent writes, edits, refactors, or fixes implementation code | `references/code-quality-gate.md` |
| **GATE 2: Test Review** | Test code — behavior-over-implementation, justified mocks, no framework re-testing, no near-duplicate bloat | After an agent writes or changes tests | `references/test-review-gate.md` |
| **GATE 3: Docs Review** | Documentation — every symbol, flag, endpoint, and code sample verified against the source; docs-vs-code drift | After an agent writes or changes docs, or code changes documented behavior | `references/docs-review-gate.md` |
| **GATE 4: Security Review** | Security — injection, broken access control, CSRF, secrets, weak crypto, SSRF, LLM-app risks, supply chain | After code touching untrusted input, auth, secrets, I/O, dependencies, or LLM/agent calls | `references/security-review-gate.md` |
| **GATE 5: Infra Hardening** | CI/CD workflow injection, `pull_request_target` misuse, overprivileged tokens, unpinned actions/images, root containers, wildcard IAM | After workflow YAML, Dockerfiles, compose files, or IaC changes | `references/infra-hardening-gate.md` |

## When to Use

Use this skill when:
- **The user asks "review this PR" or "is this safe to merge?"** — run all 5 gates on the diff
- **An AI agent produced code, tests, docs, or infra config** — run the relevant gates before presenting the work
- **The user asks for a security review** — run Gate 4 (Security) and Gate 5 (Infra) at minimum
- **Before merging any change** — run at minimum Gates 1 (Code) and 4 (Security)
- **A PR contains test changes** — also run Gate 2 (Tests)
- **A PR contains documentation changes** — also run Gate 3 (Docs)
- **A PR contains CI/CD, Docker, or IaC changes** — also run Gate 5 (Infra)

DO NOT USE for: factual/conceptual questions, pure architecture discussion without code, prose/creative writing, data analysis, or running existing tools (linters, formatters, test runners).

## How to Use

This skill operates in **three modes**:

### Guard-pass mode (recommended)
After code has been generated, edited, refactored, or fixed, run all applicable gates on the diff or target files. Fix violations before presenting, committing, or merging.

### Live mode (explicit)
When the user invokes this skill before writing, apply all relevant gate rules while writing, then run the self-check before delivery.

### Review mode (triggered)
When the user asks you to review, audit, critique, or rate code: produce a structured findings report organized by gate. Do not edit code in review mode unless asked.

## Workflow

### Standard 5-Gate Review Process

```
STEP 1: Scope the Review
  └─ What changed? (git diff main...HEAD --stat or PR file list)
  └─ Which gates apply? (code always; tests if *_test.*; docs if *.md; 
      security if any security-sensitive path; infra if .github/|Dockerfile|*.tf)

STEP 2: Run Each Gate
  └─ Gate 1 (Code Quality) — Read references/code-quality-gate.md, apply imperatives 1–24
  └─ Gate 2 (Tests)       — Read references/test-review-gate.md, apply rules 1–10 (+ LLM rules)
  └─ Gate 3 (Docs)        — Read references/docs-review-gate.md, verify every claim against source
  └─ Gate 4 (Security)    — Read references/security-review-gate.md, apply imperatives 1–27
  └─ Gate 5 (Infra)       — Read references/infra-hardening-gate.md, apply imperatives 1–18

STEP 3: Cross-Gate Findings
  └─ A symbol in docs (Gate 3) that doesn't exist = also a code quality issue (Gate 1)
  └─ A security finding (Gate 4) in a CI step = also an infra finding (Gate 5)
  └─ Missing tests (Gate 2) for a new security-critical code path = cross-reference

STEP 4: Report
  └─ Organized by severity (Critical / High / Medium / Low)
  └─ Each finding: gate + rule, location, why it matters, suggested fix
  └─ Cross-gate findings called out explicitly

STEP 5: Self-Check Before Delivery
  └─ Run the self-check for each gate that applied
  └─ Fix all violations before presenting
```

### Quick-Start (single command review)

```bash
# Get the diff
git diff main...HEAD

# Run all 5 gates in sequence:
# 1. Check code quality
# 2. Check test quality (if tests changed)
# 3. Check docs accuracy (if docs changed)
# 4. Check security (always for production code)
# 5. Check infra config (if workflows/Dockerfiles/IaC changed)
```

Report findings in this format:

```
## clean-pro-review-gates Report

### 🔴 Critical
- [Gate 4, Rule 2] `src/auth.py:45` — SQL injection via string concatenation
- [Gate 5, Rule 2] `.github/workflows/ci.yml:12` — `pull_request_target` with fork checkout

### 🟠 High
- [Gate 1, Rule 12] `src/payments.py:88` — returns hardcoded success, implements nothing
- [Gate 2, Rule 2] `tests/test_auth.py:15` — mock of internal helper instead of boundary

### 🟡 Medium
- [Gate 3, Rule 1] `docs/api.md:42` — references `POST /invoices` endpoint that doesn't exist
- [Gate 1, Rule 5] `src/processor.py:3-15` — line-by-line comments restating code

### 🔵 Low / Note
- [Gate 5, Rule 10] Dockerfile uses version tag, not digest pin on base image
```

## Examples

| Scenario | Gates to Apply | Mode |
|----------|---------------|------|
| Agent implements a new API endpoint | 1 (Code), 4 (Security) | Guard-pass |
| Agent writes tests for an existing module | 2 (Tests) | Guard-pass |
| PR adds .github/workflows/deploy.yml | 5 (Infra), 4 (Security) | Guard-pass |
| User asks "review this entire PR" | 1, 2, 3, 4, 5 (all) | Review |
| User asks "write a secure payment module" | 1 (Code), 4 (Security) | Live |
| User asks "update the README and add docstrings" | 3 (Docs), 1 (Code) | Live |
| User asks "audit our CI/CD pipeline" | 5 (Infra) | Review |

## Severity Guide (Across All Gates)

- **Critical** — exploitable now by an unauthenticated or low-privilege attacker, or breaks a production gate: injection, missing authorization, secret in source, workflow script injection, `pull_request_target` with fork secrets, wildcard IAM on production, `0.0.0.0/0` to database
- **High** — exploitable with conditions, or degrades security posture significantly: CSRF, weak crypto, known-CVE dependency, `write-all` token, root container, public bucket, mock in production code, docs with false API signatures
- **Medium** — defense-in-depth gaps, bloat, drift, or noise that will cause future problems: unpinned base images, missing resource limits, test bloat, doc filler, generic naming
- **Low / Note** — hardening suggestions, cosmetic issues, nice-to-have improvements

## Cross-Gate Interactions

| Intersection | What to Watch For |
|-------------|-------------------|
| Gate 1 (Code) + Gate 4 (Security) | Code that compiles and runs but is insecure by design (plausible-but-insecure pattern) |
| Gate 2 (Tests) + Gate 4 (Security) | Tests that weaken security controls to pass (e.g., commented-out auth check) |
| Gate 3 (Docs) + Gate 1 (Code) | Docs that describe a function signature that doesn't match the implementation |
| Gate 4 (Security) + Gate 5 (Infra) | A security vulnerability in the app that a hardened CI/CD pipeline could have caught |
| Gate 5 (Infra) + Gate 4 (Security) | Secrets in build args/layers (infra) that also violate security secrets rules |

## Pitfalls (IMPORTANT)

1. **Do not skip gates.** If the diff touches any test file, run Gate 2. If it touches any .md file, run Gate 3. The cost of skipping a gate is a shipped defect in that category.
2. **Do not weaken security to make CI pass.** This is the most dangerous AI failure mode across all 5 gates. A gate that only passes by disabling a check means the check is the message.
3. **Do not blend gates in reporting.** Each finding must name its gate and rule number so the author knows which surface to fix.
4. **Do not apply style preferences across gates.** Gate 1 is about code quality; Gate 3 is about docs accuracy. Don't flag code style in the docs gate.
5. **Cross-gate findings must be explicit.** If a docs claim is false AND the code has a security issue, report both findings with their respective gate numbers.
6. **This skill does not replace linters, formatters, test runners, SAST scanners, or secret scanners.** It is the judgment layer — what the tools miss, which finding matters.
7. **Live mode is for explicit invocation only.** Do not apply guard rules during initial code generation unless the user invoked the skill. Apply them after generation.
8. **The AI failure modes section in each gate is the highest-leverage read.** Read it first — these are the patterns most likely in your own output.
9. **Demo config is not production config.** The model emits the tutorial default (root user, `write-all`, open ingress, `latest`) because that is what training data contains. Re-derive each privilege from actual need.
10. **Confidence in the prose is not evidence of safety in the code.** The most dangerous vulnerabilities are the well-commented ones (Perry et al., CCS 2023).

## Verification

Before finalizing any review:

1. Run the self-check for each gate that applied:
   - Gate 1: Walk imperatives 1–24. Fix every violation.
   - Gate 2: Every test justifies its existence? No mock of internal helpers?
   - Gate 3: Every symbol, flag, endpoint verified against actual source?
   - Gate 4: Every untrusted-input boundary parameterized/encoded/allow-listed?
   - Gate 5: Every workflow has minimal `permissions:`? Every action SHA-pinned?

2. Cross-gate consistency check:
   - Do docs and code agree on every symbol and behavior?
   - Are security-critical code paths covered by tests?
   - Does the CI pipeline actually run the security checks the code needs?

3. Report: Present findings organized by gate and severity. Lead with cross-gate findings. Do not edit in review mode unless asked.

## Sources

This skill draws on published research and primary sources:

- **Clean Code** (Martin, 2008) — naming, functions, comments, formatting
- **Refactoring** (Fowler, 2nd ed.) — behavior preservation, abstraction discipline
- **The Pragmatic Programmer** (Hunt & Thomas) — DRY principle
- **OWASP Top 10:2025** — web application security risks
- **CWE Top 25 (2025)** — most dangerous software weaknesses
- **OWASP LLM Top 10** — LLM application security risks
- **OWASP CI/CD Security Risks (CICD-SEC)** — pipeline hardening
- **CIS Docker Benchmark** — container security
- Pearce et al., "Asleep at the Keyboard" (IEEE S&P 2022) — ~40% of AI-generated programs vulnerable
- Perry et al., "Do Users Write More Insecure Code with AI Assistants?" (ACM CCS 2023) — overconfidence effect
- Spracklen et al., "Package Hallucinations" (USENIX Security '25) — ~19.7% hallucination rate
- GitClear "AI Copilot Code Quality 2025" — 8× duplication growth, function size 142→267 LoC
- Karpathy — LLM exception suppression observation
- Fowler — "Patterns for Reducing Friction in AI-Assisted Development"
- Kabir et al., CHI 2024 — half of AI answers contain incorrect information