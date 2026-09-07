# Changelog

## 1.0.0 (2026-09-07)

Initial release of the Matt Pocock Dev Workflows meta-skill.

### Added

- **to-spec**: Synthesize conversation into structured spec on issue tracker. Proof-tested against original mattpocock/skills v0.3.0.
  - Spec template with Problem, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope
  - Seam identification protocol (prefer existing seams, propose highest possible new ones)

- **codebase-design**: Deep modules vocabulary and design discipline.
  - Full glossary (module, interface, depth, seam, adapter, leverage, locality)
  - Deep vs shallow module comparison framework
  - Dependency classification (in-process, local-substitutable, remote-but-owned, true-external)
  - Seam discipline rules (one adapter = hypothetical, two = real)
  - Design It Twice parallel sub-agent pattern for alternative interface exploration
  - Replace-don't-layer testing strategy

- **domain-modeling**: Shared language building for project contexts.
  - CONTEXT.md format with _Avoid_ notation
  - ADR format (minimal: 1-3 sentences, context-decision-why)
  - Multi-context support via CONTEXT-MAP.md
  - Active discipline: challenge, sharpen, stress-test, cross-reference, update inline

- **code-review**: Two-axis review (Standards + Spec) via parallel sub-agents.
  - Fowler smell baseline (12 smells from Refactoring ch.3)
  - Fixed-point pinning via three-dot diff
  - Spec source identification protocol
  - Deliberate separation of axes to prevent one masking the other

- **diagnosing-bugs**: 6-phase disciplined debug loop.
  - Phase 1: feedback loop construction (10 techniques from failing tests to HITL)
  - Phase 2: reproduce + minimise (every remaining element load-bearing)
  - Phase 3: 3-5 falsifiable hypotheses before testing
  - Phase 4: instrument (one variable at a time, tagged debug logs)
  - Phase 5: fix + regression test (correct seam required)
  - Phase 6: cleanup checklist
  - Secret redaction discipline throughout