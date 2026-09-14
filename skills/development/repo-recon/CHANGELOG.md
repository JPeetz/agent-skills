# CHANGELOG — repo-recon

## v1.0.0 — 2026-09-14

### Added
- Initial release of the Repo Recon agent skill (packaged from
  adityaarakeri/senior-agent-skills)
- Systematic five-step recon pass: Read the map, Learn the commands, Trace
  one flow end-to-end, Note conventions then match them, Write it down
- Structured SKILL.md sections: Overview, When to Use, The Recon Pass,
  Standing Rules, Definition of Done, Common Mistakes, Cross-reference
- Standing rules incl. search-before-assuming and verify-before-believing,
  with code kept strictly read-only during the pass
- Definition of Done checklist with explicit zero-source-changes gate
- Cross-reference to anti-over-engineering (record deferred cleanups, never
  start them during recon)
- Trigger-friendly description starting with "Use this skill when"
- 5 eval cases with near-miss negative
- MIT License (c) 2026 JPeetz

### Why
Most agent failures on unfamiliar repos come from skipping reconnaissance:
guessed commands that break the build, edits that violate local conventions,
and changes to the wrong module. Existing onboarding content is either
tool-specific or too heavy. This skill packages the lightweight senior-agent
recon loop into a triggerable, portable SKILL.md with a hard gate: no source
changes until the map, commands, flow trace, and conventions are written down.