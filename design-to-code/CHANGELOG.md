# Changelog — Design-to-Code Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-06-23

### Added
- Initial release by Skill Foundry
- Design source ingestion workflow (Figma, Sketch, Adobe XD, screenshots,
  design specs)
- Design token extraction with CSS custom properties as canonical format
- W3C DTCG-compatible token naming conventions and validation checklist
- Component hierarchy mapping with props, states, variants, and slots
- Responsive breakpoint strategy (mobile-first recommended, 6-breakpoint
  system with layout change documentation table)
- Accessibility-first implementation (WCAG 2.1 AA minimum):
  - Semantic HTML element decision table
  - ARIA usage patterns for complex widgets
  - Color contrast requirements and focus indicator implementation
  - Keyboard navigation and focus management
  - Screen reader considerations and audit checklist
- Framework-agnostic implementation patterns:
  - React + TypeScript with CSS Modules
  - Vue 3 Composition API
  - Svelte
  - Plain HTML/CSS Web Components
- CSS architecture selection guide with decision matrix:
  - CSS Modules, Tailwind CSS, styled-components, Vanilla CSS Custom
    Properties, Sass/SCSS, zero-runtime CSS-in-JS
- Visual regression testing strategy with Playwright example and diff
  thresholds
- Design system integration patterns (token mapping, component extension,
  discrepancy flagging)
- SEO-optimized description with primary keyword clusters
- GEO metadata block for structured AI engine summarization
- Common pitfalls and anti-patterns (10 implementer anti-patterns)
- Implementation quality self-checklist (12 items)
- Safety rules including IP respect, accessibility mandate, and fidelity
  honesty
- Platform compatibility notes for all 8 platforms
- QUICK REFERENCE table with phases, activities, and quality tiers
- Near-miss negative examples (9 non-trigger inputs)
- 8 eval cases (5 positive, 3 near-miss negatives)
- `design-tokens-guide.md` reference with W3C DTCG spec
- PEP 723 validation script with token format and WCAG detection checks
## v1.0.1 — 2026-06-25

### Changed
- Published to GitHub repository (JPeetz/agent-skills)
- Part of Skill Foundry Run 004
