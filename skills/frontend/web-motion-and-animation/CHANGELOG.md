# Changelog — Web Motion and Animation

All notable changes to this skill package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.0.0 — 2026-11-13

### Added

- Initial release by Skill Foundry (@artisan)
- Engine decision rule: CSS transition vs GSAP, with a requirement-to-engine
  table and two hard floors (no layout-property animation, reduced-motion branch
  mandatory)
- Install and plugin registration guidance (`gsap`, `@gsap/react`,
  `gsap/ScrollTrigger`), including the all-plugins-free note and the silent
  missing-registration failure
- Core API coverage: `gsap.to` / `from` / `fromTo` semantics, tween handles
  (`play`/`reverse`/`seek`/`kill`), easing table by intent, duration bands,
  `stagger` (including `from: "center"`), `gsap.defaults`, `gsap.set`,
  `autoAlpha`, `getProperty`, `quickTo`
- `gsap.matchMedia()` for responsive branches and `prefers-reduced-motion`,
  combining conditions in one query object and requiring a complete end state in
  the reduce branch
- Timeline patterns: sequencing, position parameters table (`"-=0.3"`, `"<"`,
  `"<0.1"`, labels, absolute), labels, control surface, and two interruption
  patterns (`reversed(!reversed())`, `overwrite: "auto"`)
- ScrollTrigger: reveal / scrub / pin recipes, the four standard bugs (implicit
  end, non-linear ease on scrub, pin inside transformed ancestor, re-playing
  reveals), `refresh()` after layout change, `invalidateOnRefresh`, and cleanup
- Framework integration for React (`useGSAP`, `scope`, dependencies,
  `contextSafe`, StrictMode, SSR), Vue 3, and Svelte, unified on
  `ctx.revert()` as the cleanup primitive
- Performance guardrails: transform/opacity only, `will-change` budget, layout
  thrash avoidance, ScrollTrigger over native scroll listeners, off-screen
  teardown, stagger vs per-element tweens, `quickTo`, 4x CPU throttle testing
- Accessibility: reduced-motion CSS block plus why it does not affect GSAP,
  JS `matchMedia` branch for scroll effects, no scroll-jacking without escape,
  3 Hz flash limit, focus timing around `autoAlpha`, motion never the only signal
- Anti-slop review checklist (14 items) covering engine choice, properties,
  timing, reduced motion, scoping, cleanup, ScrollTrigger config, interruption,
  `will-change`, input blocking, layout shift, and narrative justification
- `references/sources.md` with primary documentation links and further reading
- `evals/evals.json` with 3 scored scenarios (basic tween, timeline,
  ScrollTrigger) plus 2 negative triggers
