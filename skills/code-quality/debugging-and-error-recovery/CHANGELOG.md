# Changelog

## v1.0.0 (2026-09-21)

### Initial Release — Systematic Root-Cause Debugging

- **Process-driven debugging workflow:** Stop-the-Line rule, 6-step triage checklist (Reproduce → Localize → Reduce → Fix Root Cause → Guard → Verify), with decision trees at each step
- **Anti-rationalization table:** 9 common rationalizations vs reality, drawn from real debugging failures
- **Progressive disclosure:** Core SKILL.md covers the essential workflow; references/ dive deeper into git bisect, error-specific patterns, instrumentation strategies
- **Error-specific triage trees:** Test failures, build failures, runtime errors, production incidents — each with a structured decision tree
- **Verification checklist:** 6-item end-to-end checklist with [ ] markers for tracking completion
- **Safe fallback patterns:** Graceful degradation, defensive defaults, no silent swallows
- **Treatment of error output as untrusted data:** Rules for safe handling of instructions embedded in error messages
- **Red flags:** 8 explicit warning signs of superficial debugging
- **Eval suite:** 5 positive test cases covering the core workflow, anti-rationalization, error-specific triage, safe fallbacks, and verification gates
- **Validated against scripts/validate_skill.py**

### Source Attribution

Adapted and materially improved from addyosmani/agent-skills (MIT licensed). Key improvements:
- Anti-rationalization table expanded from 5 to 9 entries
- Progressive disclosure structure with references for (git bisect, error-specific strategies)
- Safe fallback patterns section added
- Error output as untrusted data section added
- Verification checklist with [ ] markers
- Expanded error-specific triage with production incident pattern
- Eval suite with 5 coverage cases