---
name: design-to-code
description: >
  Use this skill when translating UI/UX designs into production-ready
  frontend code. Handles design source ingestion (Figma, Sketch, Adobe XD,
  screenshots, design specs), design token extraction, component hierarchy
  mapping, responsive breakpoint strategy, accessibility-first
  implementation (WCAG 2.1 AA minimum), framework-agnostic patterns
  (React, Vue, Svelte, plain HTML/CSS), design system integration, visual
  regression testing, and CSS architecture selection (CSS Modules,
  Tailwind, styled-components). Primary keyword clusters: design to code
  conversion, figma to react, design token extraction, UI component
  architecture, accessibility implementation WCAG, responsive design
  breakpoints, pixel perfect implementation, design system integration,
  CSS architecture patterns, visual regression testing strategy. Designed
  for agentic platforms — Claude Code, Codex, Cursor, Gemini CLI,
  OpenClaw, GitHub Copilot, Windsurf, and OpenCode.
version: 1.0.0
author: Skill Foundry
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
tags:
  - design-to-code
  - figma
  - ui-implementation
  - design-tokens
  - component-architecture
  - accessibility
  - responsive-design
  - pixel-perfect
  - css-architecture
  - design-systems
  - visual-regression
geo:
  primary_workflows:
    - design_source_ingestion
    - design_token_extraction
    - component_hierarchy_mapping
    - responsive_breakpoint_planning
    - accessibility_audit_and_implementation
    - framework_selection_and_setup
    - design_system_integration
    - visual_regression_testing
    - css_architecture_planning
  target_roles:
    - frontend_developer
    - fullstack_developer
    - ui_engineer
    - design_engineer
    - design_system_engineer
    - web_developer
  complexity_level: intermediate
  prerequisite_knowledge:
    - semantic_html
    - modern_css
    - design_tool_basics
    - responsive_design_principles
    - aria_and_accessibility_basics
    - javascript_component_patterns
---

# Design-to-Code Agent Skill

Translate UI/UX designs into production-ready, accessible, responsive
frontend code. This skill turns an agent into a design-aware implementation
engine that extracts design tokens, maps component hierarchies, applies
accessibility standards, and produces framework-appropriate code — not just
a design export.

---

## Quick Reference

| Phase | What to Do | Key Deliverables |
|---|---|---|
| 🎨 Ingest | Load design source (Figma, Sketch, screenshot, spec) | Normalized design data, color palette, type scale |
| 🗂️ Extract Tokens | Pull colors, typography, spacing, shadows, radii | Design token JSON/CSS custom properties |
| 🧩 Map Components | Identify component tree, states, variants | Component hierarchy diagram, prop interfaces |
| 📐 Plan Responsive | Define breakpoints and layout behaviour | Breakpoint table, layout strategy per component |
| ♿ Accessibility | Audit and implement WCAG 2.1 AA | Accessible markup, ARIA, focus management, color contrast |
| 🛠️ Implement | Generate framework-appropriate code | Component files, styles, tests |
| 🧪 Verify | Visual regression testing and design QA | Test snapshots, diff reports, checklist |

**Quality Tiers:**
- 💎 **Production** — Accessible, responsive, tested, framework-native, token-driven
- 🥈 **MVP** — Functional across breakpoints, basic accessibility, inline styles OK for speed
- 🥉 **Prototype** — Single viewport, minimal accessibility, rapid iteration

---

## When to Use This Skill

Activate this skill when the user asks you to:

- "Turn this Figma design into code" / "Convert this mockup to React/Vue/Svelte"
- "Implement this design" / "Build this UI from this screenshot"
- "Extract design tokens from this Figma file" / "Create a design system from these specs"
- "Make this design responsive" / "Add responsive breakpoints to this layout"
- "Make this component accessible" / "Ensure WCAG 2.1 AA compliance"
- "Set up a component from this Sketch/XD design"
- "Create a pixel-perfect implementation of this design"
- "Integrate this design with our existing design system"
- "Set up visual regression tests for these components"
- Any request containing "design" + "code", "implement", "build", "convert", or "translate"

Additionally, activate proactively when a conversation includes a design
artifact (Figma link, screenshot, design spec) and the user's intent is
implementation.

### Do NOT Activate For

The following inputs are **near-miss negatives** — they mention design or
code language but are not design-to-code tasks:

- **Pure code generation without a design**: "Write a React form component" — no visual design input, so plain coding.
- **Design critique/review**: "What do you think of this design?" — opinion, not implementation.
- **Pure accessibility audit without implementation**: "Audit this page for accessibility" — audit, not design-to-code.
- **Design tool usage questions**: "How do I create an auto-layout in Figma?" — tool instruction, not code generation.
- **Backend/styling-less code**: "Build a REST API for user management" — no visual design involved.
- **Pure CSS framework questions**: "What's better, Tailwind or CSS Modules?" — opinion, not implementation.
- **Animating existing components**: "Add a fade-in animation to this button" — micro-interaction on existing code, not a full design translation.
- **Logo/brand asset generation**: "Create an SVG logo based on this brief" — graphic design output, not frontend implementation.
- **Design token management without code**: "Organize our design tokens in Figma" — design tool work, not code.

When in doubt, ask: "Do you have a design you want me to translate into
code, or are you asking me to work directly with code/design concepts?"

---

## Common Pitfalls & Anti-Patterns

### ❌ Implementer Anti-Patterns

1. **Skipping the design analysis phase** — Jumping straight to code without
   understanding the design's intent, hierarchy, and reusable patterns. Always
   ingest and analyze before you code.

2. **Hardcoding design values** — Using raw pixel values (`color: #3B82F6`)
   instead of design tokens (`color: var(--color-primary-500)`). Token-driven
   code is maintainable; hardcoded values rot.

3. **Accessibility as an afterthought** — Adding ARIA at the end rather than
   building accessible from the start. Retrofit accessibility is always
   incomplete.

4. **Responsive as a second pass** — Implementing desktop-first then
   "making it responsive" leads to fragile media-query spaghetti. Plan
   breakpoints and layout strategy before writing a single rule.

5. **Div-soup markup** — Nesting `<div>` inside `<div>` rather than using
   semantic HTML (`<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`).
   Semantic elements are free accessibility and SEO wins.

6. **Over-engineering the component tree** — Creating 12 components for a
   simple card because "atomic design says so." Map hierarchy to what the
   design actually calls for, not an ideology.

7. **Copying Figma auto-layout directly** — Figma's stacking model doesn't
   always map 1:1 to CSS Flexbox/Grid. Translate the intent, not the
   implementation.

8. **Ignoring existing design system tokens** — Using colors/spacing that
   diverge from the project's token set. "Close enough" values accumulate
   into an inconsistent codebase.

9. **Testing only one viewport** — Verifying at 1440px and calling it done.
   Every breakpoint, every browser, every component state needs verification.

10. **Skipping visual regression testing** — Assuming your implementation
    matches the design because it "looks right." Screenshot diffs catch
    what the human eye misses.

### ✅ Implementation Quality Checklist

Before declaring a design-to-code task complete, verify:

- [ ] All design sources were ingested and analyzed
- [ ] Design tokens are extracted and referenced as CSS custom properties or token variables
- [ ] Component hierarchy matches the design's visual hierarchy
- [ ] All defined breakpoints have been implemented and tested
- [ ] WCAG 2.1 AA compliance verified (contrast, focus, labels, semantics)
- [ ] Framework conventions followed (component structure, styling approach)
- [ ] No hardcoded design values — all through tokens
- [ ] Visual regression baselines captured and tests pass
- [ ] Component states accounted for (hover, focus, active, disabled, loading, empty, error)
- [ ] Keyboard navigation works end-to-end
- [ ] Screen reader announcement is meaningful
- [ ] Dark mode / theme variants considered (if applicable)

---

## Workflow

### Phase 1: Ingest the Design Source

1. **Identify the design source type:**
   - **Figma**: Extract via Figma API, Figma plugin export, or screenshot +
     manual annotation. For API access, use the Figma file key and node IDs.
     ```bash
     # Extract Figma file as JSON
     curl -H "X-Figma-Token: $FIGMA_TOKEN" \
       "https://api.figma.com/v1/files/FILE_KEY"
     ```
   - **Sketch**: Parse `.sketch` files (they are ZIP archives with JSON inside).
     Extract via `unzip` and read `document.json` + `pages/`.
   - **Adobe XD**: Export via XD plugin or Adobe's Design Automation API.
   - **Screenshots / image files**: Use image analysis (vision model) to
     identify layout, colors, typography, spacing, and components. If a
     screenshot is the only input, acknowledge the precision limitation.
   - **Design specs / redlines**: Parse spec documents for explicit
     measurements, colors, and type scales.

2. **Normalize the design data.** Regardless of source, produce:
   - **Color palette** — all named colors with hex/RGB/HSL values
   - **Typography scale** — font families, sizes, weights, line heights,
     letter spacing per text style
   - **Spacing scale** — consistent spacing units (4px/8px base recommended)
   - **Shadow definitions** — box-shadow values per elevation level
   - **Border radii** — consistent corner radius tokens
   - **Component inventory** — every distinct UI element, its states, and
     how it repeats

3. **If the design source is incomplete** (screenshot, rough mockup), ask the
   user for clarification on:
   - Exact color values (approximated from a screenshot may be off)
   - Font family names (not guessable from a screenshot)
   - Interactive states not visible in a static image
   - Responsive behaviour at different breakpoints

### Phase 2: Extract and Define Design Tokens

Extract a structured token system. Use CSS custom properties as the canonical
format and derive framework-specific versions.

```css
:root {
  /* Colors — Primary */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;

  /* Colors — Neutral */
  --color-neutral-50: #fafafa;
  --color-neutral-100: #f5f5f5;
  /* ...through 900 */

  /* Typography */
  --font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Spacing — 4px base scale */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

  /* Border Radius */
  --radius-sm: 0.125rem;   /* 2px */
  --radius-md: 0.375rem;   /* 6px */
  --radius-lg: 0.5rem;     /* 8px */
  --radius-xl: 0.75rem;    /* 12px */
  --radius-2xl: 1rem;      /* 16px */
  --radius-full: 9999px;
}
```

**Token naming conventions:**
- Use the [W3C Design Tokens Community Group format](https://tr.designtokens.org/)
  where possible: `color.primary.500`, `spacing.md`, `typography.heading.lg`.
- In CSS custom properties, use kebab-case dot-separated or dash-separated:
  `--color-primary-500` or `--typography-heading-lg`.
- For framework-specific code (Tailwind config, Theme UI, styled-system),
  derive the token structure from the CSS custom properties.

**Token validation checklist:**
- [ ] All colors have a 50–900 scale (or a documented reason not to)
- [ ] Font sizes use relative units (`rem`) for accessibility
- [ ] Spacing uses a consistent base unit (4px or 8px)
- [ ] No raw values in component code — only token references
- [ ] Dark mode tokens defined if the design supports it

See `references/design-tokens-guide.md` for the full W3C DTCG token
specification and advanced patterns.

### Phase 3: Map the Component Hierarchy

1. **Identify the top-level layout structure:**
   - Header, main content area, sidebar, footer
   - Page-level grid or layout container

2. **Decompose into component tree:**
   ```
   Page
   ├── Header
   │   ├── Logo
   │   ├── Navigation
   │   │   └── NavItem (repeating)
   │   └── UserMenu
   │       ├── Avatar
   │       └── Dropdown
   ├── MainContent
   │   ├── HeroBanner
   │   │   ├── Heading
   │   │   ├── Subheading
   │   │   └── CTAButton
   │   ├── FeatureGrid
   │   │   └── FeatureCard (repeating)
   │   │       ├── Icon
   │   │       ├── Title
   │   │       └── Description
   │   └── TestimonialCarousel
   │       └── TestimonialCard (repeating)
   └── Footer
       ├── FooterLinks
       └── SocialIcons
   ```

3. **For each component, define:**
   - **Props/interface** — what data flows in
   - **States** — default, hover, focus, active, disabled, loading, empty,
     error (list all that apply)
   - **Variants** — primary/secondary for buttons, compact/default/expanded
     for cards, etc.
   - **Slots/children** — where does content get injected
   - **Responsive behaviour** — how does it change at each breakpoint

4. **Identify shared/reusable patterns:**
   - Buttons, inputs, cards, avatars — extract as base components
   - Layout primitives — Container, Grid, Stack, Flex
   - Typography components — Heading, Text, Caption

5. **For each reusable component, check if an equivalent exists** in the
   project's design system. If yes, extend it rather than creating a new one.

### Phase 4: Define Responsive Breakpoint Strategy

1. **Choose a breakpoint system:**
   - **Mobile-first** (recommended): Start at the smallest viewport and add
     complexity as screen size increases. Use `min-width` media queries.
   - **Desktop-first**: Start at the largest viewport and simplify for
     smaller screens. Use `max-width` media queries. Less common but valid
     for desktop-heavy applications.

2. **Define breakpoint values.** Common breakpoints:
   | Name | Width | Typical Device |
   |------|-------|----------------|
   | `xs` | 0px+ | All phones |
   | `sm` | 640px+ | Large phones, small tablets |
   | `md` | 768px+ | Tablets |
   | `lg` | 1024px+ | Small laptops, large tablets landscape |
   | `xl` | 1280px+ | Desktops |
   | `2xl` | 1536px+ | Large desktops |

3. **For each breakpoint, document layout changes:**
   | Component | < 640px | 640–1024px | > 1024px |
   |-----------|---------|------------|----------|
   | Navigation | Hamburger menu | Hamburger menu | Horizontal nav |
   | FeatureGrid | 1 column | 2 columns | 3 columns |
   | HeroBanner | Stacked (image below text) | Stacked | Side-by-side |
   | Sidebar | Hidden, toggle overlay | Collapsible | Persistent |

4. **Implement responsive utilities.** Create CSS custom properties or
   utility classes for media queries. For Tailwind, use the built-in
   breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`).

5. **Test at every breakpoint.** Do not trust that a component will work at
   intermediate sizes. 720px can expose layout bugs that 640px and 768px
   hide.

### Phase 5: Accessibility-First Implementation

**Minimum standard: WCAG 2.1 Level AA.** If the user's project requires AAA,
escalate accordingly.

#### 5.1 Semantic HTML

Use the correct HTML element for every piece of content. This is the
single highest-impact accessibility decision.

| Content | Correct Element | Avoid |
|---------|----------------|-------|
| Page header | `<header>` | `<div class="header">` |
| Primary navigation | `<nav aria-label="Main">` | `<div class="nav">` |
| Main content | `<main>` | `<div class="content">` |
| Standalone sections | `<section>` (with heading) | `<div>` |
| Articles / blog posts | `<article>` | `<div>` |
| Sidebar / complementary | `<aside>` | `<div>` |
| Page footer | `<footer>` | `<div class="footer">` |
| Data tables | `<table>`, `<thead>`, `<tbody>`, `<th scope="">` | `<div>` grid |
| Lists of items | `<ul>`, `<ol>`, `<li>` | `<div>` repeated |
| Buttons that perform actions | `<button>` | `<div onclick="">` |
| Links that navigate | `<a href="">` | `<button onclick="navigate()">` |
| Images with meaning | `<img alt="description">` | `<img>` (missing alt) |
| Decorative images | `<img alt="">` | `<img alt="icon">` |
| Form inputs | `<label>` + `<input>` paired with `for`/`id` | Placeholder-only inputs |
| Headings | `<h1>`–`<h6>` in logical order (no skips) | `<div class="heading">` |
| Figures with captions | `<figure>` + `<figcaption>` | `<div>` + `<p>` |

#### 5.2 ARIA — Use Only When HTML Isn't Enough

**First rule of ARIA: don't use ARIA if native HTML can do it.** ARIA adds
complexity and is easy to get wrong.

When ARIA is necessary:

| Pattern | ARIA Usage |
|---------|-----------|
| Tabs | `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls` |
| Modal dialogs | `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus trap |
| Accordions | `aria-expanded` on trigger, `aria-controls` linking to panel |
| Live regions | `aria-live="polite"` for dynamic content updates |
| Custom dropdowns | `role="listbox"`, `role="option"`, `aria-activedescendant` |
| Alerts/toasts | `role="alert"` or `aria-live="assertive"` |
| Progress bars | `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| Disclosure widgets | `aria-expanded`, `aria-controls` |

#### 5.3 Color and Contrast

- **Text contrast ratio**: 4.5:1 minimum for normal text, 3:1 for large text
  (18px+ bold or 24px+ regular). WCAG AA requirement.
- **Non-text contrast**: 3:1 minimum for UI components and graphical objects
  (button borders, input borders, icons).
- **Never use color alone** to convey information. Error states need both
  red color AND an icon/text indicator. Links need underlines (not just
  color change).
- **Focus indicators**: Every interactive element must have a visible focus
  style. Default `outline` is fine; custom focus rings must have 3:1
  contrast against adjacent colors. `:focus-visible` is preferred over
  `:focus` for mouse users.

```css
/* Good focus indicator */
:focus-visible {
  outline: 3px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Avoid — removes focus entirely */
*:focus { outline: none; }
```

#### 5.4 Keyboard Navigation

- **Tab order** must follow visual order. Avoid positive `tabindex` values;
  use `tabindex="0"` to add to the natural order or `tabindex="-1"` for
  programmatic focus only.
- **Interactive elements** must be reachable and operable via keyboard:
  buttons, links, form controls, custom widgets.
- **Skip links**: Provide a "Skip to main content" link as the first
  focusable element.
- **Modals**: Trap focus inside the modal while open. Restore focus to the
  trigger element on close.
- **Dropdown/Menus**: Arrow keys navigate items. Escape closes. Enter/Space
  selects.

#### 5.5 Screen Reader Considerations

- **Descriptive link text**: "Learn more about pricing" not "Click here".
- **Image alt text**: Describe what the image communicates, not what it is.
  "Golden retriever fetching a ball in a park" not "Photo of dog".
- **Form labels**: Every input must have an associated `<label>`. Use
  `aria-label` or `aria-labelledby` only when a visible label is not
  possible.
- **Dynamic content**: Use `aria-live` regions for content that updates
  without page reload (search results, chat messages, notifications).
- **Heading hierarchy**: One `<h1>` per page. Headings should form a logical
  outline without skipping levels (no `<h1>` to `<h3>` without `<h2>`).

#### 5.6 Accessibility Audit Checklist

Before shipping, verify:
- [ ] Page has a unique, descriptive `<title>`
- [ ] `<html>` has a `lang` attribute
- [ ] All images have appropriate `alt` text
- [ ] Color contrast meets WCAG AA minimums (use a checker tool)
- [ ] Focus order is logical and visible
- [ ] Skip link is present and functional
- [ ] Forms have associated labels and error messages
- [ ] Page is navigable by keyboard alone (try tabbing through)
- [ ] ARIA roles, states, and properties are valid (use axe DevTools or
  Lighthouse)
- [ ] Dynamic content updates are announced to screen readers

### Phase 6: Framework-Agnostic Implementation Patterns

Produce code appropriate to the project's framework. This skill does not
favor one framework — adapt to what the project uses.

#### 6.1 React (with TypeScript)

```tsx
// Button component — React + CSS Modules
import styles from './Button.module.css';
import { type ComponentPropsWithoutRef, forwardRef } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', isLoading, children, disabled, className, ...props }, ref) => {
    const classes = [
      styles.button,
      styles[variant],
      styles[size],
      isLoading && styles.loading,
      className,
    ].filter(Boolean).join(' ');

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? <Spinner size={size} /> : children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

#### 6.2 Vue 3 (Composition API)

```vue
<script setup lang="ts">
import { computed } from 'vue';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

const props = withDefaults(defineProps<{
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
}>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
});

const classes = computed(() => [
  `btn btn--${props.variant}`,
  `btn--${props.size}`,
  { 'btn--loading': props.loading },
]);
</script>

<template>
  <button
    :class="classes"
    :disabled="disabled || loading"
    :aria-busy="loading"
  >
    <Spinner v-if="loading" :size="size" />
    <slot v-else />
  </button>
</template>
```

#### 6.3 Svelte

```svelte
<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let loading = false;
  export let disabled = false;
</script>

<button
  class="btn btn--{variant} btn--{size}"
  class:btn--loading={loading}
  {disabled}
  aria-busy={loading}
  on:click
  {...$$restProps}
>
  {#if loading}
    <Spinner {size} />
  {:else}
    <slot />
  {/if}
</button>
```

#### 6.4 Plain HTML/CSS (Web Components)

```html
<!-- Usage -->
<ds-button variant="primary" size="md">Click me</ds-button>

<script>
class DsButton extends HTMLElement {
  static observedAttributes = ['variant', 'size', 'loading', 'disabled'];

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  render() {
    const variant = this.getAttribute('variant') || 'primary';
    const size = this.getAttribute('size') || 'md';
    const loading = this.hasAttribute('loading');
    const disabled = this.hasAttribute('disabled');

    this.setAttribute('role', 'button');
    this.setAttribute('tabindex', disabled ? '-1' : '0');
    this.setAttribute('aria-busy', String(loading));
    this.className = `ds-button ds-button--${variant} ds-button--${size} ${loading ? 'ds-button--loading' : ''}`;

    this.innerHTML = loading
      ? '<ds-spinner size="' + size + '"></ds-spinner>'
      : '<slot></slot>';
  }
}

customElements.define('ds-button', DsButton);
</script>
```

### Phase 7: CSS Architecture Selection

Choose and apply the appropriate CSS strategy based on the project context.

| Approach | Best For | Trade-offs |
|----------|----------|------------|
| **CSS Modules** | Component-heavy apps with scoping needs. Pairs well with React, Vue, Svelte. | No global utilities. Need separate global stylesheet for resets/base. |
| **Tailwind CSS** | Rapid prototyping, utility-first teams, consistent design tokens. | HTML verbosity. Learning curve. Heavier HTML markup. |
| **styled-components** | CSS-in-JS with dynamic theming. React-centric. | Runtime overhead. Bundle size. Harder to extract critical CSS. |
| **Vanilla CSS Custom Properties** | Framework-agnostic, design systems, web components. | No scoping built-in. Requires naming conventions (BEM). |
| **Sass/SCSS** | Teams with SCSS legacy, complex mixin/functions needs. | Compilation step. Can produce bloated output without discipline. |
| **CSS-in-JS (zero-runtime)** | Static extraction (Vanilla Extract, Panda CSS, Linaria). | Build-time dependency. Smaller ecosystem than runtime CSS-in-JS. |

**Decision matrix:**
1. **If the project already uses a CSS approach**, match it. Consistency > personal preference.
2. **If starting fresh and speed matters**, Tailwind CSS or plain CSS custom properties.
3. **If building a design system**, CSS custom properties + CSS Modules for components.
4. **If heavy runtime theming is needed**, styled-components or Theme UI.

### Phase 8: Visual Regression Testing Strategy

1. **Set up a visual testing tool** — Chromatic (Storybook), Percy, Playwright
   screenshot comparison, or BackstopJS.

2. **Define test scenarios:**
   - Every component in every meaningful state (default, hover, focus, etc.)
   - Every breakpoint
   - Every theme variant (light/dark)
   - Edge cases: very long text, missing images, empty states, error states

3. **Capture baselines** from the initial implementation and compare against
   design references (Figma exports, design screenshots).

4. **Establish a regression workflow:**
   ```
   Implement → Capture baseline → Compare to design → Fix diffs → Re-capture
   ```

5. **Example Playwright visual test:**
   ```typescript
   import { test, expect } from '@playwright/test';

   test('Button component matches design', async ({ page }) => {
     await page.goto('/components/button');
     await expect(page.locator('[data-testid="button-primary"]')).toHaveScreenshot(
       'button-primary.png',
       { maxDiffPixelRatio: 0.01 }
     );
   });
   ```

6. **Acceptable diff thresholds:**
   - **Pixel-perfect**: 0% diff (brand pages, landing pages, core UI)
   - **Near-perfect**: <0.5% diff (internal tools, dashboards)
   - **Tolerance**: <2% diff (rapid prototyping, early-stage products)

### Phase 9: Design System Integration

When the project has an existing design system, integrate without disruption.

1. **Audit the existing system** — what tokens, components, and patterns
   already exist?

2. **Map new design elements to existing tokens:**
   - If the design uses a color that matches `--color-primary-500`, use it.
   - If the design introduces a new color not in the system, flag it:
     "This design specifies `#7C3AED` which is not in our design system.
     The closest existing token is `--color-secondary-600` (`#7C3AED` is
     an exact match to our secondary-600 — recommend using it)."

3. **Extend components rather than creating duplicates.** If a `Card`
   component exists but the design needs a slightly different variant,
   add a prop rather than creating `SpecialCard`.

4. **If the design contradicts the design system**, flag the discrepancy
   and ask whether the design should change or the design system should
   be updated.

5. **Token synchronization** — If the project has a token pipeline (e.g.,
   Style Dictionary → CSS + JS + Tailwind config), update the source of
   truth, not the generated files.

---

## Safety Rules

**ABSOLUTE RULES — never violate these:**

1. **Respect intellectual property.** Never reproduce copyrighted designs,
   illustrations, logos, or brand assets without explicit permission or
   license. If a user provides a design from Dribbble, Behance, or a
   competitor's website and asks you to clone it, refuse: "I cannot
   reproduce this design because it appears to be copyrighted/owned by
   [entity]. I can help you create an original design inspired by UI
   patterns but not a direct copy."

2. **Never ship hardcoded secrets.** If a design includes API keys,
   tokens, or credentials in code examples, flag them and strip them.
   Use environment variables.

3. **Always use HTTPS** for external assets (fonts, images, CDN resources).
   Mixed content is a security risk.

4. **Respect user privacy.** Don't add third-party trackers, analytics,
   or telemetry to generated code without the user's explicit request.
   Screen readers and accessibility tools must not be blocked.

5. **Be honest about fidelity.** When working from a screenshot (not a
   design file), preface output with: "I'm working from a screenshot,
   so colors and exact measurements are approximate. Please verify
   the following values against your design spec."

6. **Don't silently replace the design intent.** If the design has a
   complex interaction that would be expensive to implement, don't
   simplify it without asking. Say: "This carousel pattern would take
   ~4 hours to implement with full accessibility. A simpler tabbed
   layout would take ~1 hour. Which do you prefer?"

7. **Accessibility is non-negotiable.** Every implementation must meet
   WCAG 2.1 AA at minimum. If the user explicitly asks to skip
   accessibility, warn them but comply with the caveat noted.

8. **Don't generate inaccessibly.** Never produce code with `outline: none`
   without a replacement focus indicator. Never use `tabindex` values
   greater than 0. Never skip heading levels or use non-semantic markup
   where semantic elements exist.

---

## Platform Compatibility Notes

This skill is designed to work across AI coding platforms with minor
adaptations:

| Platform | Notes |
|----------|-------|
| **Claude Code** | Figma API integration works well. Can parse design JSON. Good for token extraction pipelines. |
| **Codex (OpenAI)** | Strong at component generation. Paste design specs or describe the design verbally. Screenshot analysis works well. |
| **Cursor** | Can read existing codebase for design system context. File system access helps with token integration. |
| **Gemini CLI** | Large context window useful for ingesting full design specs. Use `web_fetch` for Figma API. |
| **OpenClaw** | Exec for Figma CLI/API calls. GitHub skill for PR-based design review. Image analysis for screenshots. |
| **GitHub Copilot** | Works within IDE context. Best for incremental component implementation with existing design system access. |
| **Windsurf** | Can access workspace files and design assets. Execute design-to-code in context of existing project. |
| **OpenCode** | Terminal-based. Best with explicit design specs pasted or described textually. Can run token extraction scripts. |

### Platform-Specific Adjustments

- **If Figma API token is unavailable**: ask the user to export the design as
  SVG/PNG or paste a design spec document. Screenshot analysis is the fallback.
- **If image/vision analysis is not available**: ask the user to describe the
  design in text (layout, colors, typography, spacing). Work from description.
- **If a specific framework is not specified**: default to the framework the
  project already uses. If no project exists, ask the user.
- **For Discord/Slack delivery**: use bullet lists, not markdown tables. Split
  large code blocks across multiple messages. Wrap links in `<>`.
- **For platforms without file system access**: inline tokens and styles
  directly in generated output rather than referencing external files.

---

## References

- `references/design-tokens-guide.md` — W3C Design Tokens Community Group
  specification and implementation guide
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/) —
  Official WCAG 2.1 guidelines
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/) —
  ARIA design patterns and widget examples
- [Figma API Documentation](https://www.figma.com/developers/api) —
  Figma REST API reference
- [Style Dictionary](https://amzn.github.io/style-dictionary/) —
  Design token transformation tool
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) —
  Color contrast verification
- [axe DevTools](https://www.deque.com/axe/) — Automated accessibility testing
- [Chromatic](https://www.chromatic.com/) — Visual regression testing for
  Storybook