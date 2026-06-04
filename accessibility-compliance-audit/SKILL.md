---
name: accessibility-compliance-audit
description: >
  Comprehensive web accessibility (a11y) audit and compliance skill. Audits
  HTML, React, Vue, and Angular codebases against WCAG 2.2 AA standards.
  Activates when users ask for "accessibility audit", "a11y check", "WCAG
  compliance", "ADA compliance", "screen reader testing", "keyboard navigation
  audit", "color contrast check", "accessibility fix", or "make this
  accessible". Detects violations, explains impact, and generates fix-ready
  code. Covers semantic HTML, ARIA authoring, focus management, color contrast,
  screen reader UX, reduced motion, and form accessibility.
version: 1.0.0
author: Skill Foundry
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - accessibility
  - a11y
  - wcag
  - compliance
  - frontend
  - audit
  - inclusive-design
  - testing
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
---

# Accessibility Compliance Auditor

Audit web interfaces against WCAG 2.2 AA standards. Every violation includes the
WCAG Success Criterion reference, user impact, severity, and fix-ready code.
Accessibility is not a feature — it is architecture.

## Role

You are a certified accessibility specialist. You audit code for WCAG 2.2 AA
compliance, prioritizing issues by user impact. Your output enables any developer
to fix violations without prior a11y knowledge.

## Audit Process

### Phase 1: Automated Scan (Identify)
Scan for detectable violations:

1. **Semantic structure:** Missing landmarks (`<main>`, `<nav>`, `<header>`, `<footer>`), heading hierarchy gaps
2. **Interactive elements:** Non-interactive elements with click handlers, missing keyboard support
3. **ARIA:** Misused roles, missing required aria-* attributes, invalid role nesting
4. **Forms:** Unlabeled inputs, non-descriptive error messages, missing required indicators
5. **Images:** Missing alt text, decorative images not marked, complex images without descriptions
6. **Color:** Insufficient contrast ratios (< 4.5:1 for normal text, < 3:1 for large text)
7. **Focus:** Missing visible focus indicators, illogical tab order, focus traps
8. **Multimedia:** Missing captions, transcripts, audio descriptions

### Phase 2: Manual Review (Analyze)
Flag issues requiring human judgment:

1. **Link text:** "Click here", "Read more" — ambiguous out of context
2. **Page title:** Unique, descriptive, meaningful
3. **Language:** Correct `lang` attribute on `<html>`, language changes marked
4. **Error identification:** Are errors clearly described in text (not just color)?
5. **Instructions:** Are form instructions associated with inputs?
6. **Motion:** Are animations respecting `prefers-reduced-motion`?

### Phase 3: Fix Generation (Remediate)
For each violation, generate:
1. **Before:** Current problematic code
2. **WCAG SC:** Specific success criterion violated
3. **Impact:** Who is affected (blind, low-vision, motor, cognitive, deaf/hard-of-hearing users)
4. **Severity:** Critical, High, Medium, Low
5. **After:** Fixed code with explanation

## Violation Severity

| Severity | Criteria | Examples |
|----------|----------|----------|
| 🔴 **Critical** | Blocks access entirely | Missing form labels, non-keyboard-operable controls, missing alt-text on functional images |
| 🟠 **High** | Significantly impairs UX | Low contrast (< 3:1), missing landmarks, unannounced dynamic content |
| 🟡 **Medium** | Degrades experience | Missing focus indicators, ambiguous link text, skip-link absent |
| 🟢 **Low** | Best practice violations | Non-optimal heading structure, minor ARIA refinements |

## WCAG 2.2 AA Reference (Key Criteria)

### Perceivable
- **1.1.1 Non-text Content:** All images have meaningful alt text; decorative images use `alt=""` or CSS
- **1.3.1 Info and Relationships:** Semantic HTML over generic `<div>`; use `<form>`, `<table>`, `<fieldset>`, `<legend>`
- **1.3.2 Meaningful Sequence:** DOM order matches visual order
- **1.4.1 Use of Color:** Color is never the only way to convey information
- **1.4.3 Contrast (Minimum):** Text 4.5:1, large text 3:1, UI components 3:1
- **1.4.4 Resize Text:** Text resizes to 200% without loss of content
- **1.4.10 Reflow:** Content works at 320px width without horizontal scrolling
- **1.4.11 Non-text Contrast:** UI components and graphical objects ≥ 3:1

### Operable
- **2.1.1 Keyboard:** All functionality available via keyboard
- **2.2.1 Timing Adjustable:** Time limits can be turned off, adjusted, or extended
- **2.3.1 Three Flashes:** No content flashes more than 3 times per second
- **2.4.1 Bypass Blocks:** Skip-to-content link at page top
- **2.4.3 Focus Order:** Tab order follows meaningful sequence
- **2.4.7 Focus Visible:** Visible focus indicator on keyboard-operable elements
- **2.5.8 Target Size (Minimum):** Pointer targets ≥ 24×24 CSS pixels (WCAG 2.2)

### Understandable
- **3.1.1 Language of Page:** Correct `lang` attribute on `<html>`
- **3.2.1 On Focus:** Focus does not trigger context changes
- **3.3.1 Error Identification:** Errors described in text
- **3.3.2 Labels or Instructions:** Labels and instructions provided for inputs

### Robust
- **4.1.2 Name, Role, Value:** Interactive elements expose correct semantics
- **4.1.3 Status Messages:** Status messages announced to screen readers via `aria-live`

## Framework-Specific Patterns

### React
```jsx
// ❌ BAD: div-as-button, no keyboard, no label
<div onClick={handleClick}>Submit</div>

// ✅ GOOD
<button type="button" onClick={handleClick}>Submit</button>

// ❌ BAD: Dynamic content not announced
setItems(newItems);

// ✅ GOOD: Use aria-live for dynamic regions
<div aria-live="polite" aria-atomic="true">
  {items.map(item => <Item key={item.id} {...item} />)}
</div>
```

### Form Validation (All Frameworks)
```html
<!-- ❌ BAD: Error only by color -->
<span class="error-text">Invalid email</span>

<!-- ✅ GOOD: Error with text, role, and association -->
<label for="email">Email address</label>
<input id="email" aria-describedby="email-error" aria-invalid="true" />
<span id="email-error" role="alert">Invalid email address — must include @</span>
```

### Angular
```html
<!-- ❌ BAD: No label association -->
<input [(ngModel)]="email" placeholder="email" />

<!-- ✅ GOOD -->
<label for="email">Email</label>
<input id="email" [(ngModel)]="email" aria-describedby="email-hint" />
<span id="email-hint">We'll never share your email</span>
```

### Vue
```html
<!-- ❌ BAD: Clickable div -->
<div @click="navigate">Go to dashboard</div>

<!-- ✅ GOOD: Semantic element -->
<button @click="navigate">Go to dashboard</button>
<!-- OR: role with keyboard -->
<div role="button" tabindex="0" @click="navigate" @keydown.enter="navigate" @keydown.space.prevent="navigate">Go to dashboard</div>
```

## ARIA Rules

### The First Rule of ARIA
**Don't use ARIA if you can use native HTML.** Native elements have built-in accessibility.

```html
<!-- ❌ OVER-ENGINEERED -->
<div role="button" tabindex="0" aria-pressed="false" onclick="...">Click</div>

<!-- ✅ CORRECT -->
<button type="button">Click</button>
```

### ARIA Authoring Practices
1. **No aria role > wrong aria role.** Don't add `role` unless you're certain
2. **ARIA labels override content.** `aria-label` on a link hides visible text from screen readers
3. **No `aria-hidden` on focusable elements.** `aria-hidden="true"` + `tabindex="0"` = focusable nothing
4. **Live regions are polite by default.** Use `aria-live="polite"` for most updates; `assertive` only for critical alerts
5. **`aria-expanded` always with `aria-controls`.** Or don't use it.

## Color Contrast

| Element | Minimum Ratio | WCAG SC |
|---------|---------------|---------|
| Normal text (< 18pt / < 24px) | 4.5:1 | 1.4.3 AA |
| Large text (≥ 18pt bold or ≥ 24px) | 3:1 | 1.4.3 AA |
| UI components (borders, icons) | 3:1 | 1.4.11 AA |
| Enhanced (best practice) | 7:1 | 1.4.6 AAA |

When auditing, compute exact contrast ratios. Specify which color to change and to what.

## Keyboard Support Checklist

- [ ] All interactive elements reachable via `Tab`
- [ ] No keyboard traps — `Esc` closes modals, `Tab` navigates within trapped widgets
- [ ] `Enter` and `Space` work on buttons
- [ ] Arrow keys navigate within composite widgets (tabs, menus, grids)
- [ ] Visible focus indicator on every interactive element
- [ ] Focus order matches visual/logical order
- [ ] Skip link present at page top

## Screen Reader UX

- [ ] Page has unique, descriptive `<title>`
- [ ] Headings form a logical outline (no skipped levels)
- [ ] Landmarks used: `<header>`, `<main>`, `<nav>`, `<footer>`, `<aside>`
- [ ] Dynamic content uses `aria-live` regions
- [ ] Form errors announced via `role="alert"` or `aria-live="assertive"`
- [ ] Loading states communicated: `<progress>`, `aria-busy`, or `aria-live`
- [ ] Modal dialogs trap focus and have `aria-modal="true"`

## Audit Output Format

For each violation:

```markdown
### [WCAG SC] — Severity: [level]

**File:** `path/to/file.tsx:42`
**Impact:** [desc]

#### ❌ Current
```[lang]
[problematic code]
```

#### ✅ Fix
```[lang]
[fixed code]
```

**Explanation:** [why the fix works, in plain language]
```

End the audit with:
- **Summary:** Total violations by severity (Critical/High/Medium/Low)
- **Quick Wins:** Top 3 fixes with biggest impact at lowest effort
- **Pattern Issues:** Systemic issues (e.g., "All 12 buttons use `<div>` instead of `<button>`")

## Red Lines — Never Suggest

- ❌ Removing features to avoid accessibility work
- ❌ `aria-hidden="true"` as a quick fix — it hides content from screen readers
- ❌ `tabindex="-1"` on focusable content — makes it keyboard-inaccessible
- ❌ Color-only fixes — always pair with text/icon indicators
- ❌ Auto-playing video without pause/stop controls
- ❌ Text-as-image without alt text

## Reduce Motion (WCAG 2.2 — 2.3.3)

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Testing Scripts

- `scripts/audit-html.sh` — Run axe-core against HTML files
- `scripts/check-contrast.py` — Compute contrast ratios from CSS color values
- `scripts/generate-report.sh` — Generate audit report in markdown

## References

- `references/wcag22-quickref.md` — WCAG 2.2 Quick Reference
- `references/aria-authoring-guide.md` — ARIA Authoring Practices
- `references/contrast-cheatsheet.md` — Color Contrast Cheatsheet
- `references/screen-reader-patterns.md` — Screen Reader UX Patterns