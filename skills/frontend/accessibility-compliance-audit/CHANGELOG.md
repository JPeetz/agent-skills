# CHANGELOG — accessibility-compliance-audit

## v1.0.0 — 2026-06-04

### Added
- Initial release of Accessibility Compliance Auditor agent skill
- WCAG 2.2 AA complete audit framework (Perceivable, Operable, Understandable, Robust)
- Automated scan phase: 8 violation categories (semantics, interactive, ARIA, forms, images, color, focus, multimedia)
- Manual review phase: 6 judgment-required areas (link text, titles, language, errors, instructions, motion)
- Fix generation phase: Before/After code with WCAG SC reference, user impact, and severity
- 4-tier severity classification: Critical, High, Medium, Low
- Framework-specific patterns: React, Vue, Angular with good/bad examples
- ARIA authoring rules including "First Rule of ARIA"
- Color contrast analysis with specific WCAG SC references
- Keyboard support checklist (7 items)
- Screen reader UX checklist (8 items)
- prefers-reduced-motion CSS pattern (WCAG 2.2 SC 2.3.3)
- Form validation patterns with aria-describedby and role="alert"
- 6 red lines — things never to suggest (feature removal, aria-hidden shortcuts, color-only fixes, etc.)
- Structured audit output format with file/line references
- Summary generation: violation counts, quick wins, systemic patterns
- 6 eval cases with near-miss negatives
- Testing scripts: audit-html.sh, check-contrast.py, generate-report.sh
- Reference docs: WCAG 2.2 Quick Reference, ARIA Authoring Guide, Contrast Cheatsheet, Screen Reader Patterns

### Why
Accessibility skills exist in the ecosystem (33-skill packs, 40-skill inclusive design packs)
but they are fragmented and primarily designer-facing. This skill provides an
engineer-facing, comprehensive audit covering the full WCAG 2.2 AA standard
with framework-specific fix code. It bridges the gap between design-focused
a11y skills and engineering implementation.