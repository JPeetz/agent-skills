---
name: "web-motion-and-animation"
description: "Use this skill when animating: CSS, GSAP, ScrollTrigger"
version: "1.0.0"
author: "{'name': 'Skill Foundry (@artisan)', 'source': 'Greensock GSAP Skills, GSAP.com/docs'}"
license: "MIT"
metadata:
  hermes:
    tags: [frontend, animation, gsap, motion, scrolltrigger, accessibility]
    related_skills:
      - frontend-ui-engineering
      - design-to-code
      - ui-verification
      - accessibility-compliance-audit
  openclaw:
    original_name: "web-motion-and-animation"
permissions:
  files:
    read: true
    write: true
  network:
    allow: []
  dangerous:
    allowed: false
platforms:
  - claude-code
  - openclaw
  - cursor
  - codex
  - opencode
  - gemini-cli
---

# Web Motion and Animation

Motion is a design decision with a runtime cost. This skill covers the two engines
that ship most web motion — CSS transitions and GSAP — and the discipline that
keeps either from hurting layout, input latency, or the people who asked their OS
to stop moving things.

- **IS:** choosing an engine, writing tweens and timelines, wiring ScrollTrigger,
  scoping and cleaning up in React/Vue/Svelte, reviewing motion for performance
  and accessibility.
- **IS NOT:** designing a page's visual language (`design-to-code`), proving the
  motion renders in a browser (`ui-verification`), or authoring Lottie/AE
  pipelines.

## Decision rule: CSS vs GSAP

Pick the smaller engine that satisfies the requirement. Reaching for GSAP on a
hover fade is the most common motion defect in generated code: 30-70 kB and a JS
dependency for something the compositor does for free.

| Requirement | Engine |
|---|---|
| Single element, single state change (hover, focus, open/close, toast) | CSS `transition` |
| Looping decorative animation, no JS-driven state | CSS `@keyframes` |
| Orchestrating 3+ elements with relative timing or overlaps | GSAP timeline |
| Must be paused, reversed, seeked, or restarted by user input | GSAP timeline (a seekable object) |
| Progress tied to scroll position, or pinning | GSAP + ScrollTrigger |
| Mid-flight interruption with correct state, or `Flip`/`MotionPath`/`SplitText`/`DrawSVG` | GSAP + plugin |
| Animating a value that drives canvas, WebGL, SVG path data, or a CSS variable | GSAP (tweens the number; you render) |
| `stagger`, or `repeat: -1` with `yoyo` | GSAP (`stagger` is one line; CSS needs `nth-child` per item) |

Two hard floors, either engine:

- **Never animate layout properties.** `width`, `height`, `top`, `left`, `margin`,
  `padding`, `font-size` force layout every frame. Animate `transform` and
  `opacity`; use `scale`/`clip-path` when the design wants size.
- **The reduced-motion branch is not optional.** See [Accessibility](#accessibility).

If both engines are already in the bundle, follow the local convention per class
of effect. Two systems fighting over one element's `transform` is a bug factory.

## Install and register

```bash
npm install gsap                 # core
npm install gsap @gsap/react     # React projects use the official hook
```

```js
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger); // once, at app entry module scope
```

Every plugin is free (post-Webflow) and installs from the public `gsap` package —
no Club token, no private registry. Registering twice is harmless; registering
*never* fails silently with "invalid property" warnings, not an error.

## Core API

`gsap.to` animates **from the current state to the given state**. `gsap.from`
animates **from the given state to the current state** (the element's CSS is the
destination). `gsap.fromTo` defines both ends and is the only safe choice when
the start state is unknown or the element may already be mid-animation.

```js
gsap.to(".card", { x: 40, opacity: 1, duration: 0.6, ease: "power2.out" });
gsap.from(".card", { y: 24, autoAlpha: 0, duration: 0.6, ease: "power2.out" });
gsap.fromTo(".card", { scale: 0.96 }, { scale: 1, duration: 0.4 });
```

A tween is a handle: `tween.play()`, `reverse()`, `seek(0.5)`, `kill()`,
`.paused(true)` in the vars for a controlled start.

**Easing.** Default is `power1.out`. Pick by intent:

| Intent | Ease |
|---|---|
| Entering (decelerate into place) | `power2.out` / `power3.out` |
| Leaving (accelerate away) | `power2.in` |
| Moving between two on-screen positions | `power2.inOut` |
| Physical snap / bounce | `back.out(1.7)` sparingly; `elastic` rarely |
| Anything scroll-scrubbed | `none` — the scrollbar is the easing |

Never `linear` for a UI state change, never `elastic` for something clicked
repeatedly. Durations: feedback 0.15-0.25s, element transitions 0.3-0.5s,
page-level reveals 0.6-0.9s. Past 1s a UI animation reads as latency.

**Stagger** replaces hand-written per-item delays:

```js
gsap.from(".list li", { y: 20, autoAlpha: 0, stagger: 0.06, duration: 0.5 });
gsap.from(".grid > *", { scale: 0.9, autoAlpha: 0, stagger: { each: 0.05, from: "center" } });
```

**Defaults** keep timing consistent across a codebase; **`gsap.set`** writes a
state instantly with no tween:

```js
gsap.defaults({ duration: 0.5, ease: "power2.out" });
gsap.set(".hidden-until-animated", { autoAlpha: 0 });
```

`autoAlpha` is `opacity` plus `visibility` — at 0 it also leaves the tab order and
the accessibility tree, which bare `opacity: 0` does not. Prefer it for anything
that fades in and out of interactivity.

`gsap.getProperty(el, "x")` reads a current numeric value. `gsap.quickTo(el, "x",
{ duration: 0.4 })` returns a reusable setter for high-frequency input (pointer
move, drag) without allocating a tween per event — the right tool for cursor
followers.

## Responsive + reduced motion: gsap.matchMedia

`gsap.matchMedia()` is the only correct way to branch GSAP by breakpoint or
motion preference. Its `revert()` restores every inline style the animations
wrote, which is what makes breakpoint changes safe.

```js
const mm = gsap.matchMedia();

mm.add("(min-width: 768px)", () => {
  gsap.from(".hero-title", { y: 60, autoAlpha: 0, duration: 0.8 });
});
mm.add("(max-width: 767px)", () => {
  gsap.from(".hero-title", { y: 20, autoAlpha: 0, duration: 0.4 });
});

mm.revert(); // on unmount
```

Combine conditions in one query object so a single branch owns the reduced-motion
decision instead of scattering `matchMedia` checks:

```js
mm.add(
  { isDesktop: "(min-width: 768px)", reduceMotion: "(prefers-reduced-motion: reduce)" },
  (context) => {
    const { isDesktop, reduceMotion } = context.conditions;

    if (reduceMotion) {
      gsap.set(".reveal", { autoAlpha: 1, y: 0 }); // land on the final state
      return;
    }
    gsap.from(".reveal", {
      y: isDesktop ? 40 : 16,
      autoAlpha: 0,
      stagger: 0.08,
      duration: isDesktop ? 0.7 : 0.45,
    });
  }
);
```

The branch that runs under `reduce` must still produce a **complete, usable final
state** — visible and positioned where the animation would have left it, never
stuck at `autoAlpha: 0`.

## Timeline patterns

A timeline is a container with its own playhead. Use one whenever more than one
tween needs to relate to another in time.

```js
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });

tl.from(".modal-backdrop", { autoAlpha: 0 })
  .from(".modal-panel", { y: 24, autoAlpha: 0 }, "-=0.3")     // overlap 0.3s
  .from(".modal-panel button", { y: 8, autoAlpha: 0, stagger: 0.04 }, "<0.1");
```

**Position parameter** — the third argument decides *when* a child starts:

| Value | Meaning |
|---|---|
| *(omitted)* | After the previous child ends |
| `"-=0.3"` | 0.3s before the previous child ends |
| `"+=0.2"` | 0.2s after the previous child ends |
| `"<"` / `"<0.1"` | At / 0.1s after the previous child **starts** |
| `"myLabel"`, `"myLabel+=0.2"` | Relative to a label |
| `2.5` | Absolute time |

**Labels** keep long sequences editable without re-counting durations:

```js
tl.addLabel("enter")
  .from(".step-1", { autoAlpha: 0 })
  .addLabel("swap")
  .to(".step-1", { autoAlpha: 0 })
  .from(".step-2", { autoAlpha: 0 }, "swap+=0.2");
```

**Control surface:** `play()`, `pause()`, `reverse()`, `restart()`, `seek("swap")`,
`progress(0.5)`, `timeScale(2)`, `kill()`, `eventCallback("onComplete", fn)`;
`tl.then(fn)` resolves when it finishes.

**Interruption.** The naive bug is `restart()` on every click: three clicks give
three restarts and a stuttering element.

```js
// 1. Reverse from wherever it is; don't restart mid-flight
const open = gsap.timeline({ paused: true }).from(".panel", { y: 20, autoAlpha: 0 });
toggle.addEventListener("click", () => open.reversed(!open.reversed()));

// 2. If a tween must retarget, overwrite what it was doing
gsap.to(el, { x: targetX, duration: 0.4, overwrite: "auto" });
```

`overwrite: "auto"` kills only the conflicting properties of other tweens on that
element, not the whole tween. Use `"auto"`, not `true`, unless you want every
property killed. For hover in/out, `overwrite: "auto"` on both tweens plus a
short duration is the whole pattern.

## ScrollTrigger

Register once, then attach via the `scrollTrigger` property.

```js
// Reveal once, on entry
gsap.from(".feature", {
  y: 40, autoAlpha: 0, duration: 0.6,
  scrollTrigger: { trigger: ".feature", start: "top 80%", once: true },
});

// Scrub: playhead follows scrollbar; number = catch-up smoothing in seconds
gsap.to(".progress-bar", {
  scaleX: 1, ease: "none",
  scrollTrigger: { trigger: "main", start: "top top", end: "bottom bottom", scrub: 0.5 },
});

// Pin: hold an element while the timeline advances
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".panel", start: "top top", end: "+=800",
    pin: true, scrub: 1, anticipatePin: 1,
    invalidateOnRefresh: true, // re-read start values on resize
  },
});
tl.from(".panel h2", { y: 60, autoAlpha: 0 }).to(".panel img", { scale: 1.1 }, "<");
```

The four standard bugs and their rules:

- **Implicit `end`.** A scrubbed animation with no `end` gets a one-pixel span and
  snaps. Always state it.
- **Non-linear ease on a scrub.** Any ease but `"none"` fights the scrollbar and
  reads as lag.
- **Pinning inside a transformed ancestor.** `transform`, `filter`,
  `perspective`, `will-change` on an ancestor create a containing block; the pin
  then engages against the wrong parent. Check `.pin-spacer` placement when a pin
  jumps.
- **Reveals that replay.** A scrubbed reveal on every scroll-back is rarely the
  design. `once: true` or `toggleActions: "play none none reverse"` states intent.

**Refresh after layout changes.** ScrollTrigger measures on creation; images
loading, fonts swapping, an accordion opening, or async content all move
everything downstream:

```js
ScrollTrigger.refresh();                                   // after content settles
document.fonts.ready.then(() => ScrollTrigger.refresh());  // fonts
```

Call it debounced after the event that changed layout — never per scroll or per
frame. Use `invalidateOnRefresh: true` so tweens re-read their start values.

**Cleanup** is not optional; a stale trigger keeps listening and throws on a
detached element:

```js
st.kill();                                       // one trigger
ScrollTrigger.getAll().forEach(t => t.kill());   // full-page swap only
```

Inside `gsap.context()` / `useGSAP`, `ctx.revert()` kills the triggers it
created — which is why scoping matters. In an SPA, reverting the route's context
is the teardown; the `getAll().kill()` sweep belongs to a full document swap.

## Framework integration

The failure is identical everywhere: effects run twice (StrictMode), or a tween
is created against an element that unmounts first, leaving inline styles and
listeners on a dead node.

### React

Use the official `@gsap/react` hook — it wraps `gsap.context()` and reverts on
unmount, which makes StrictMode's double-invoke harmless.

```jsx
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(useGSAP, ScrollTrigger);

export function Hero() {
  const scope = useRef(null);

  useGSAP(() => {
    gsap.from(".title", { y: 40, autoAlpha: 0, duration: 0.7 });
    gsap.from(".cta", { y: 16, autoAlpha: 0, delay: 0.2 });
  }, { scope });          // selectors scoped to this ref

  return <section ref={scope}><h1 className="title">…</h1><a className="cta">…</a></section>;
}
```

- **Always pass `scope`.** Without it, `.title` selects every match in the
  document and the second mounted component steals the first one's animation.
- **Pass `dependencies`** (`{ scope, dependencies: [open] }`) when the animation
  depends on state; omit it for entrance animations that run once.
- **`contextSafe`** wraps anything that runs after the effect (event handlers):
  `const { contextSafe } = useGSAP({ scope }); const onClick = contextSafe(() => gsap.to(...))`.
- **Don't "fix" StrictMode** with a `useRef` guard — that leaves the first
  context unreverted. Let `useGSAP` revert it.
- **SSR:** GSAP touches `document`/`window`. Guard with
  `typeof window !== "undefined"` or keep animation in a `"use client"` component.

### Vue 3 and Svelte

`gsap.context()` for selector scoping, and the framework's teardown hook:

```js
// Vue 3
let ctx;
const root = ref(null);
onMounted(() => {
  ctx = gsap.context(() => {
    gsap.from(".item", { y: 24, autoAlpha: 0, stagger: 0.06 });
  }, root.value);
});
onBeforeUnmount(() => ctx?.revert());

// Svelte: onMount returns the teardown
onMount(() => {
  const ctx = gsap.context(() => gsap.from(".card", { scale: 0.95, autoAlpha: 0 }), node);
  return () => ctx.revert();
});
```

In Svelte 5 runes the same teardown goes in `$effect(() => { …; return () => ctx.revert(); })`.

Across all three: **`ctx.revert()` / `mm.revert()` is the cleanup primitive**, not
`kill()` per tween. `revert()` restores inline styles, reverts ScrollTriggers, and
returns the DOM to its pre-animation state — what a re-mount expects.

## Performance guardrails

- **`transform` and `opacity` only.** Everything else in a 60fps loop is layout
  or paint per frame. `x`/`y` → `translate`, `scale`, `rotation`; GSAP composes
  the `transform` for you.
- **`will-change` is a budget.** Each promoted layer costs GPU memory (a
  full-viewport layer is several MB at 3x). Add it to the 5-10 elements
  animating in the current view and remove it when the animation completes. Never
  `* { will-change: transform }`.
- **Avoid layout thrash.** Don't read `getBoundingClientRect()`, `offsetWidth`, or
  `scrollTop` in a handler that also writes styles — that forces synchronous
  layout per frame. ScrollTrigger batches reads and writes; that is a performance
  reason to prefer it.
- **ScrollTrigger over `scroll` listeners.** A native listener writing styles
  runs on the main thread every tick; ScrollTrigger coalesces and can use the
  compositor.
- **Kill off-screen work.** A paused timeline still holds references. For
  off-screen sections prefer `once: true` over a repeating idle animation.
- **`stagger` is one tween; `.forEach(el => gsap.to(el, …))` is N.** With 200
  items that is 200 ticker entries versus one.
- **`quickTo` for pointer-driven motion** — one allocation instead of one tween
  per `mousemove`.
- **Test at 4x CPU throttle.** Smooth on an M-series laptop and stuttering on a
  mid-range Android is the normal outcome, not the exception.

## Accessibility

`prefers-reduced-motion: reduce` is a first-class branch, not a CSS afterthought.
Users who set it are frequently people with vestibular disorders — parallax,
large zoom, and scroll-jacking are the specific triggers.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

That block neutralises CSS animations but **does nothing to GSAP**, which writes
inline styles and never reads the media query on its own. Hence the
`mm.add({ reduceMotion: … })` branch, plus an explicit guard for scroll effects:

```js
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  gsap.set(".parallax-layer", { y: 0, clearProps: "transform" });
  return; // no scrub, no pin, no parallax
}
```

Beyond the media query:

- **No scroll-jacking without an escape.** A wheel-hijacked horizontal section
  needs a visible way out and must still advance on Page Down / arrows.
- **No flashing above 3 Hz** (WCAG 2.3.1). That includes strobing "glitch"
  effects.
- **Focus never animates out of view.** Move focus before or after the tween,
  never mid-tween, and never to a `visibility: hidden` node — `autoAlpha: 0` sets
  exactly that, so restore `autoAlpha: 1` before calling `focus()`.
- **Don't churn the accessibility tree on a timer.** A toast fading via
  `autoAlpha` is fine; a live region whose text swaps every 200ms floods a screen
  reader.
- **Motion is never the only signal.** A shake meaning "invalid" needs a message
  and `aria-invalid`; an animated checkmark needs text.

## Anti-slop review checklist

Run against any motion diff before calling it done:

- [ ] **Engine justified** — CSS for a state change, GSAP only where timing,
      seek, or scroll requires it.
- [ ] **Only `transform`/`opacity` animate** — no `width`, `height`, `top`,
      `left`, `margin`, `font-size` in a tween.
- [ ] **Durations in the 0.15-0.9s band** and consistent with siblings (shared
      `gsap.defaults` or a token).
- [ ] **Reduced-motion branch exists and its end state is complete** — visible and
      positioned, not stuck at `autoAlpha: 0`.
- [ ] **Selectors are scoped** (`useGSAP({ scope })`, `gsap.context(fn, root)`,
      `mm.add`) — no bare `document.querySelectorAll` inside an effect.
- [ ] **Cleanup exists** (`ctx.revert()`, `mm.revert()`, `st.kill()`), and
      StrictMode's double-invoke produces no doubled animation.
- [ ] **Scrubbed animations use `ease: "none"`** and an explicit `end`.
- [ ] **`ScrollTrigger.refresh()`** runs after fonts/images/content load, with
      `invalidateOnRefresh: true` where start values depend on layout.
- [ ] **Interruption handled** — `reversed(!reversed())` or `overwrite: "auto"`,
      not `restart()` on every trigger.
- [ ] **`will-change` only on currently-animating elements**, removed after.
- [ ] **No input blocked** — no lingering `pointer-events: none`, no `body
      overflow: hidden` left behind when a modal closes.
- [ ] **No layout shift** — animated items don't leave a gap that collapses;
      `autoAlpha` where space must be preserved.
- [ ] **Focus and screen-reader behaviour survive** the animation.
- [ ] **The motion is not decorative noise.** Every animation communicates a
      state change, a spatial relationship, or a hierarchy — else delete it.

## Sources

Derived from the official GSAP AI skills (`greensock/gsap-skills`, MIT) and the
GSAP v3 documentation. See [references/sources.md](references/sources.md).
