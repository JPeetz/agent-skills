# Changelog

All notable changes to the Production Engineering Workflows skill will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-23

### Added

- Initial release of the Production Engineering Workflows skill.
- Eight slash-command workflow entry points:
  - `/spec` — Spec-driven feature definition with PRD template
  - `/plan` — Atomic task decomposition with dependency ordering
  - `/build` — Test-driven incremental implementation (Red-Green-Refactor)
  - `/test` — Test pyramid enforcement (80/15/5) with DAMP/Beyoncé Rule
  - `/review` — Five-axis code review (security, correctness, quality,
    architecture, performance)
  - `/webperf` — Web performance audit (Core Web Vitals, Lighthouse,
    bundle analysis)
  - `/code-simplify` — Complexity reduction with Chesterton's Fence
    and incremental refactoring
  - `/ship` — Production deployment with feature flags, canary
    rollout, and rollback plans
- Integrated end-to-end pipeline with gate enforcement at every phase.
- Near-miss negative detection to avoid workflow activation for
  trivial changes.
- Comprehensive safety rules covering secrets, data destruction,
  rollback, and deployment.
- Platform compatibility notes for Claude Code, Codex, Cursor,
  Gemini CLI, OpenClaw, Copilot, Windsurf, and OpenCode.
- Supporting reference: SDLC best practices guide (`references/sdlc-patterns.md`).
- Validation script: `scripts/validate_skill.py` (PEP 723 compliant).
- Evaluation test cases: 5 near-miss negative scenarios and 5
  positive activation cases (`evals/test_cases.json`).
## [1.0.1] — 2026-06-25

### Changed
- Published to GitHub repository (JPeetz/agent-skills)
- Part of Skill Foundry Run 004
