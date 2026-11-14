# Changelog

## [1.0.0] — 2026-11-14

- Initial release
- Trust boundary enumeration across eight channels (system, user, retrieved,
  tool output, memory, peer agent, model output, rendered surface)
- Seven-layer defense pipeline from boundary mapping through monitoring, with
  the tool boundary (L4) as the only hard enforcement point
- Context isolation: nonce-delimited provenance blocks, datamarking, and the
  dual-LLM quarantined-extraction pattern
- System prompt hardening template with an explicit instruction hierarchy
- Input screening with normalization-first matching (NFKC, confusables,
  zero-width, bidi/Trojan Source, Unicode tags, ANSI, entity/percent, base64/hex)
- Tool-boundary enforcement: argument validation, argument provenance/tainting,
  per-task capability scoping, reversibility-based approval gates, sandboxing
- Output validation: canary tokens, secret/PII scanning, exfil-URL detection,
  markdown/HTML/terminal render sanitizing
- Adversarial testing methodology measuring ASR per family and FPR on benign input
- Monitoring, detection signals, kill switches, and an incident response sequence
- 3 worked examples (RAG document assistant, coding agent on untrusted issues,
  inbox triage with send authority)
- 13 anti-patterns
- `scripts/screen_input.py` — stdlib-only screener with classifier hook
  (subprocess or HTTP), fail-closed option, source-aware scoring, and
  nonce-wrapped context emission
- `scripts/scan_agent_output.py` — stdlib-only output scanner with canary
  detection, Luhn-validated card detection, entropy+keyword secret heuristics,
  and per-mode sanitizers
- `references/attack-catalog.md` — 15 attack families with payload examples
- `references/defense-matrix.md` — 26 controls × 15 families, strength ratings,
  failure modes, minimum viable defense per deployment archetype, and a
  15-item verification checklist
- Aligned to OWASP LLM01:2025 and Anthropic guardrails guidance; complements
  `agentic-security-scanner` (install-time), `threat-modeling` (design-time)
  and `vulnerability-management` (remediation)
