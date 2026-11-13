# Sources and Further Reading

Primary material behind this skill. Both are MIT-licensed and maintained by
GreenSock (a Webflow company).

## Official AI skills (source of the decision rules)

- **greensock/gsap-skills** — <https://github.com/greensock/gsap-skills>
  Official agent skills for GSAP: core API, timelines, ScrollTrigger, plugins,
  framework integration, performance. This skill's structure follows theirs;
  the anti-slop checklist and the CSS-vs-GSAP decision table are this repo's
  additions. License: MIT. Risk level stated by the project: LOW.
- Plugin bundles in that repo: `.claude-plugin/`, `.cursor-plugin/`,
  plus `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` for agent-specific loading.

## Core documentation

- GSAP docs home — <https://gsap.com/docs/v3/>
- `gsap.to()` / `from()` / `fromTo()` —
  <https://gsap.com/docs/v3/GSAP/gsap.to()>, `/gsap.from()`, `/gsap.fromTo()`
- Timelines — <https://gsap.com/docs/v3/GSAP/Timeline/>
  (position parameter details: <https://gsap.com/docs/v3/GSAP/Timeline/#positioning-animation-in-a-timeline>)
- Easing visualiser — <https://gsap.com/docs/v3/Eases/>
- `gsap.matchMedia()` — <https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/>
- `gsap.context()` — <https://gsap.com/docs/v3/GSAP/gsap.context()/>
- `gsap.quickTo()` — <https://gsap.com/docs/v3/GSAP/gsap.quickTo()/>
- `gsap.defaults()` / config — <https://gsap.com/docs/v3/GSAP/gsap.defaults()/>
- Utility methods (`toArray`, `getProperty`, `pipe`) —
  <https://gsap.com/docs/v3/GSAP/UtilityMethods/>

## ScrollTrigger

- Main page — <https://gsap.com/docs/v3/Plugins/ScrollTrigger/>
- **Common mistakes** (the highest-value page for review) —
  <https://gsap.com/resources/st-mistakes>
  Covers nested ScrollTriggers, pinning in transformed ancestors, implicit ends,
  and refresh behaviour.
- `ScrollTrigger.refresh()` —
  <https://gsap.com/docs/v3/Plugins/ScrollTrigger/static.refresh()/>
- `ScrollTrigger.normalizeScroll()` /
  `ScrollTrigger.config()` — for mobile address-bar resize handling
  (`ignoreMobileResize`).

## Framework integration

- React + `useGSAP` — <https://gsap.com/resources/React/>
- `@gsap/react` package — <https://www.npmjs.com/package/@gsap/react>
- Vue and Svelte guidance live in the same React/GSAP resource section
  (`gsap.context()` is the shared primitive).

## Accessibility

- WCAG 2.3.1 Three Flashes or Below Threshold —
  <https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html>
- WCAG 2.3.3 Animation from Interactions —
  <https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html>
- `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>
- Vestibular disorder guidance (A List Apart, "Designing Safer Web Animation
  For Motion Sensitivity") —
  <https://alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity/>

## Performance

- Rendering performance / compositor-friendly properties —
  <https://web.dev/articles/rendering-performance>
- `will-change` (and why not to overuse it) —
  <https://developer.mozilla.org/en-US/docs/Web/CSS/will-change>
- Layout thrashing / forced synchronous layout —
  <https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing>
- Interaction to Next Paint —
  <https://web.dev/articles/inp>

## Related skills in this repo

- `frontend-ui-engineering` — component structure the animation attaches to.
- `design-to-code` — design intent, tokens, motion as part of the system.
- `ui-verification` — proving the animation renders and does not shift layout.
- `accessibility-compliance-audit` — reduced-motion and flash thresholds as
  auditable rules.
