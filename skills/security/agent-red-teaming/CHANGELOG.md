# Changelog — Agent Red Teaming

## [1.0.0] — 2026-11-14

- Initial release from Skill Foundry
- Nine-step engagement process: scope/safety rails → threat model → capability
  recon → prompt injection → tool misuse → memory poisoning → privilege
  escalation → output-validation bypass → score/report/retest
- OWASP Agentic Top 10 (ASI01–ASI10) coverage with per-category test strategies,
  evidence rules, and primary controls
- MITRE ATLAS tactic mapping per attack class, in the attack catalog and in
  `references/owasp-asi-mapping.md`
- Attack vectors: direct/indirect prompt injection across 7 carriers, tool
  misuse (traversal, SSRF, parameter pollution, chaining, scale abuse, confused
  deputy), memory and context poisoning including agent-writable config/skill
  surfaces, privilege and identity abuse (incl. inter-agent spoofing and
  unattended self-escalation), and output-validation bypass (markup/ANSI,
  schema breaks, downstream sink injection, beacon exfiltration)
- Canary-first evidence model: no finding without a trace excerpt and a canary
- Severity rubric scored on impact × reachability × precondition, with explicit
  anti-inflation rules
- Verdict taxonomy `PASS | FAIL | PARTIAL | BLOCKED-ENV` (no blank verdicts)
- 3 worked examples (RAG support copilot exfiltration; coding-agent credential
  read via repo-planted instructions; research-fleet memory poisoning with
  circular corroboration)
- 11 anti-patterns and a 17-item pre-completion verification checklist
- `references/owasp-asi-mapping.md` — ASI01–ASI10 table with failure description,
  test strategy, required evidence, and primary control layer
- `references/attack-payloads.jsonl` — 24 machine-readable probe records plus a
  schema record, usable directly as a test backlog
- `scripts/score_findings.py` — stdlib-only validator/aggregator for
  `tests.jsonl`: schema checks, coverage per ASI category, severity rollup, and
  a markdown summary ready for the report appendix
- `evals/evals.json` — 8 eval cases covering trigger accuracy, near-misses, and
  expected diagnostic content
