# Design Tokens Guide

A practical reference for implementing the W3C Design Tokens Community Group
(DTCG) specification. Use this as a baseline when extracting, defining, and
organizing design tokens from any design source.

---

## 1. Token Structure (DTCG Format)

The W3C DTCG specification defines a JSON-based token format. This is the
standard interchange format — derive platform-specific output from it.

### 1.1 Minimal Token File

```json
{
  "color": {
    "primary": {
      "500": {
        "$type": "color",
        "$value": "#3b82f6",
        "$description": "Primary brand color, base"
      },
      "600": {
        "$type": "color",
        "$value": "#2563eb",
        "$description": "Primary brand color, hover state"
      }
    },
    "neutral": {
      "50": {
        "$type": "color",
        "$value": "#fafafa"
      },
      "900": {
        "$type": "color",
        "$value": "#171717"
      }
    }
  },
  "typography": {
    "fontFamily": {
      "sans": {
        "$type": "fontFamily",
        "$value": ["Inter", "system-ui", "-apple-system", "sans-serif"]
      }
    },
    "fontSize": {
      "base": {
        "$type": "dimension",
        "$value": "1rem"
      },
      "2xl": {
        "$type": "dimension",
        "$value": "1.5rem"
      }
    },
    "fontWeight": {
      "normal": {
        "$type": "number",
        "$value": 400
      },
      "bold": {
        "$type": "number",
        "$value": 700
      }
    }
  },
  "spacing": {
    "2": {
      "$type": "dimension",
      "$value": "0.5rem"
    },
    "4": {
      "$type": "dimension",
      "$value": "1rem"
    },
    "8": {
      "$type": "dimension",
      "$value": "2rem"
    }
  },
  "shadow": {
    "sm": {
      "$type": "shadow",
      "$value": {
        "color": "rgba(0, 0, 0, 0.05)",
        "offsetX": "0px",
        "offsetY": "1px",
        "blur": "2px",
        "spread": "0px"
      }
    },
    "md": {
      "$type": "shadow",
      "$value": {
        "color": "rgba(0, 0, 0, 0.1)",
        "offsetX": "0px",
        "offsetY": "4px",
        "blur": "6px",
        "spread": "-1px"
      }
    }
  },
  "borderRadius": {
    "md": {
      "$type": "dimension",
      "$value": "0.375rem"
    },
    "lg": {
      "$type": "dimension",
      "$value": "0.5rem"
    },
    "full": {
      "$type": "dimension",
      "$value": "9999px"
    }
  }
}
```

### 1.2 Token Types

| `$type` | Description | Example `$value` |
|---------|-------------|-----------------|
| `color` | A CSS-compatible color value | `"#3b82f6"`, `"rgb(59, 130, 246)"` |
| `dimension` | A CSS length value | `"1rem"`, `"16px"`, `"100%"` |
| `number` | A raw number (unitless) | `400`, `1.5` |
| `fontFamily` | Array of font family names | `["Inter", "sans-serif"]` |
| `fontWeight` | Font weight as string or number | `"bold"`, `700` |
| `duration` | Time value | `"200ms"`, `"0.3s"` |
| `shadow` | Box shadow object or array | `{ color, offsetX, offsetY, blur, spread }` |
| `cubicBezier` | Easing curve | `[0.4, 0, 0.2, 1]` |
| `typography` | Composite typography object | `{ fontFamily, fontSize, fontWeight, lineHeight }` |

---

## 2. CSS Custom Properties (Canonical Output)

CSS custom properties are the recommended canonical format for design tokens
in a design-to-code workflow. They work in all browsers, all frameworks, and
serve as the source of truth from which framework-specific configs derive.

### 2.1 Complete Token Set

```css
:root {
  /* ================================================================
     Colors — Primary Scale
     ================================================================ */
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

  /* Colors — Secondary Scale */
  --color-secondary-50: #f5f3ff;
  --color-secondary-500: #8b5cf6;
  --color-secondary-900: #4c1d95;

  /* Colors — Neutral Scale */
  --color-neutral-0: #ffffff;
  --color-neutral-50: #fafafa;
  --color-neutral-100: #f5f5f5;
  --color-neutral-200: #e5e5e5;
  --color-neutral-300: #d4d4d4;
  --color-neutral-400: #a3a3a3;
  --color-neutral-500: #737373;
  --color-neutral-600: #525252;
  --color-neutral-700: #404040;
  --color-neutral-800: #262626;
  --color-neutral-900: #171717;
  --color-neutral-950: #0a0a0a;

  /* Colors — Semantic */
  --color-success-500: #22c55e;
  --color-success-700: #15803d;
  --color-warning-500: #f59e0b;
  --color-warning-700: #b45309;
  --color-error-500: #ef4444;
  --color-error-700: #b91c1c;
  --color-info-500: #3b82f6;
  --color-info-700: #1d4ed8;

  /* ================================================================
     Typography
     ================================================================ */
  --font-family-sans: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  --font-family-display: 'Inter', system-ui, sans-serif;

  /* Font Sizes (rem-based for accessibility) */
  --font-size-xs: 0.75rem;     /* 12px */
  --font-size-sm: 0.875rem;    /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg: 1.125rem;    /* 18px */
  --font-size-xl: 1.25rem;     /* 20px */
  --font-size-2xl: 1.5rem;     /* 24px */
  --font-size-3xl: 1.875rem;   /* 30px */
  --font-size-4xl: 2.25rem;    /* 36px */
  --font-size-5xl: 3rem;       /* 48px */
  --font-size-6xl: 3.75rem;    /* 60px */

  /* Font Weights */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  /* Line Heights */
  --line-height-none: 1;
  --line-height-tight: 1.25;
  --line-height-snug: 1.375;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
  --line-height-loose: 2;

  /* Letter Spacing */
  --letter-spacing-tighter: -0.05em;
  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: 0;
  --letter-spacing-wide: 0.025em;
  --letter-spacing-wider: 0.05em;

  /* ================================================================
     Spacing (4px base)
     ================================================================ */
  --space-0: 0;
  --space-px: 1px;
  --space-0-5: 0.125rem;   /* 2px */
  --space-1: 0.25rem;      /* 4px */
  --space-1-5: 0.375rem;   /* 6px */
  --space-2: 0.5rem;       /* 8px */
  --space-2-5: 0.625rem;   /* 10px */
  --space-3: 0.75rem;      /* 12px */
  --space-3-5: 0.875rem;   /* 14px */
  --space-4: 1rem;         /* 16px */
  --space-5: 1.25rem;      /* 20px */
  --space-6: 1.5rem;       /* 24px */
  --space-7: 1.75rem;      /* 28px */
  --space-8: 2rem;         /* 32px */
  --space-9: 2.25rem;      /* 36px */
  --space-10: 2.5rem;      /* 40px */
  --space-11: 2.75rem;     /* 44px */
  --space-12: 3rem;        /* 48px */
  --space-14: 3.5rem;      /* 56px */
  --space-16: 4rem;        /* 64px */
  --space-20: 5rem;        /* 80px */
  --space-24: 6rem;        /* 96px */
  --space-28: 7rem;        /* 112px */
  --space-32: 8rem;        /* 128px */
  --space-36: 9rem;        /* 144px */
  --space-40: 10rem;       /* 160px */

  /* ================================================================
     Shadows
     ================================================================ */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  --shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);

  /* ================================================================
     Border Radius
     ================================================================ */
  --radius-none: 0;
  --radius-sm: 0.125rem;    /* 2px */
  --radius-md: 0.375rem;    /* 6px */
  --radius-lg: 0.5rem;      /* 8px */
  --radius-xl: 0.75rem;     /* 12px */
  --radius-2xl: 1rem;       /* 16px */
  --radius-3xl: 1.5rem;     /* 24px */
  --radius-full: 9999px;

  /* ================================================================
     Z-Index Scale
     ================================================================ */
  --z-0: 0;
  --z-10: 10;
  --z-20: 20;
  --z-30: 30;
  --z-40: 40;
  --z-50: 50;
  --z-auto: auto;

  /* ================================================================
     Transitions
     ================================================================ */
  --transition-duration-fast: 150ms;
  --transition-duration-normal: 200ms;
  --transition-duration-slow: 300ms;
  --transition-timing-ease: cubic-bezier(0.4, 0, 0.2, 1);
  --transition-timing-ease-in: cubic-bezier(0.4, 0, 1, 1);
  --transition-timing-ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

---

## 3. Framework-Specific Token Derivation

### 3.1 Tailwind CSS Configuration

Derive from CSS custom properties — keep values in sync:

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // ... secondary, neutral, semantic
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        // Tailwind's default scale maps well to a 4px base
        // Extend only what differs from default
      },
      borderRadius: {
        sm: '0.125rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        sm: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },
    },
  },
};
```

### 3.2 Theme UI / styled-system

```javascript
// theme.js
export default {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      900: '#1e3a8a',
    },
    neutral: {
      0: '#ffffff',
      100: '#f5f5f5',
      500: '#737373',
      900: '#171717',
    },
  },
  fonts: {
    body: 'Inter, system-ui, sans-serif',
    heading: 'Inter, system-ui, sans-serif',
    mono: 'JetBrains Mono, monospace',
  },
  fontSizes: [12, 14, 16, 18, 20, 24, 30, 36],
  space: [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128],
  radii: {
    sm: '2px',
    md: '6px',
    lg: '8px',
    xl: '12px',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 3px 0 rgba(0,0,0,0.1)',
    md: '0 4px 6px -1px rgba(0,0,0,0.1)',
    lg: '0 10px 15px -3px rgba(0,0,0,0.1)',
  },
};
```

---

## 4. Token Extraction from Design Sources

### 4.1 From Figma

Use the Figma API to extract design tokens programmatically:

```python
# Extract color and text styles from a Figma file
import requests

FIGMA_TOKEN = "figd_xxx"
FILE_KEY = "abc123"

headers = {"X-Figma-Token": FIGMA_TOKEN}

# Get file styles (named colors, text styles, effects)
styles = requests.get(
    f"https://api.figma.com/v1/files/{FILE_KEY}/styles",
    headers=headers
).json()

# Get file nodes for detailed values
nodes = requests.get(
    f"https://api.figma.com/v1/files/{FILE_KEY}",
    headers=headers
).json()

# Walk the document tree to extract:
# - Fill colors → --color-* tokens
# - Text node properties → --font-size-*, --font-weight-* tokens
# - Auto-layout spacing → --space-* tokens
# - Effect styles → --shadow-* tokens
# - Corner radius → --radius-* tokens
```

**Key Figma node properties to map:**

| Figma Property | Token Type |
|---------------|------------|
| `fills[].color` | `--color-*` |
| `fontSize` | `--font-size-*` |
| `fontName.family` | `--font-family-*` |
| `fontName.style` | `--font-weight-*` |
| `lineHeightPx` / `lineHeightPercent` | `--line-height-*` |
| `letterSpacing` | `--letter-spacing-*` |
| `itemSpacing` (auto-layout) | `--space-*` |
| `paddingLeft/Right/Top/Bottom` (auto-layout) | `--space-*` |
| `cornerRadius` | `--radius-*` |
| `effects[]` (DROP_SHADOW, INNER_SHADOW) | `--shadow-*` |
| `effects[]` (LAYER_BLUR) | Blur filters |

### 4.2 From Screenshots / Images

When extracting from screenshots, use a vision-capable model to identify:

1. **Layout structure** — header, sidebar, content grid, footer
2. **Color palette** — dominant colors, button colors, text colors.
   Note: Screenshot colors may be affected by compression, screen calibration,
   and color profiles. Always verify with the designer.
3. **Typography** — heading sizes, body text size. Font family is usually
   not identifiable from a screenshot — ask the user.
4. **Spacing** — approximate padding/margin/gaps. "~16px" is sufficient
   for prototyping; exact values need design specs.
5. **Component types** — buttons, inputs, cards, tables, navigation patterns

**Fidelity caveat:** Always prefix screenshot-based implementations with:
"I'm working from a screenshot, so colors and measurements are approximate.
Please verify: [list of values that need confirmation]."

### 4.3 From Design Spec Documents

Parse design spec documents for explicit tokens. Common formats:

- **Redlines / annotation documents:** Extract explicit pixel values,
  hex codes, font specifications.
- **Design system documentation (Zeroheight, Storybook):** Reference
  existing token names and values.
- **Handoff documents (Zeplin, Avocode, Figma Dev Mode):** Automated
  extraction of CSS values. These tools often provide copy-pasteable
  CSS — use as reference, not as the final source (they may not use
  tokens).

---

## 5. Token Validation Rules

When generating tokens, verify against these rules:

### 5.1 Color Rules
- [ ] All colors have a 50–900 scale or a documented reason for fewer steps
- [ ] Semantic colors (success, warning, error, info) are defined
- [ ] Neutral scale covers 0 (white) through 950 (near-black)
- [ ] Color contrast between any two adjacent tokens in a scale is perceptible
- [ ] Dark mode variants defined if applicable (use `prefers-color-scheme` media query)

### 5.2 Typography Rules
- [ ] Font sizes use `rem` units (not `px`) for browser zoom compatibility
- [ ] Base font size is 1rem (16px default)
- [ ] A type scale with at least 6 steps is defined (xs through 4xl)
- [ ] Line heights are unitless values (1.25, 1.5) for proportional scaling
- [ ] Font weight scale covers at least normal (400) through bold (700)

### 5.3 Spacing Rules
- [ ] Spacing uses a consistent base unit (4px or 8px)
- [ ] All spacing values are multiples of the base unit
- [ ] Spacing scale covers at least 0px through 128px
- [ ] Spacing tokens use `rem` for root-relative scaling

### 5.4 Shadow Rules
- [ ] Shadow scale has at least 3 elevation levels (sm, md, lg)
- [ ] Shadow color uses rgba/hsla for transparency
- [ ] Elevation increases correspond to increased blur and spread

### 5.5 General Rules
- [ ] Token names are descriptive (not `--color-1`, `--color-2`)
- [ ] Token names follow a consistent convention (kebab-case with numeric scales)
- [ ] All tokens have a single source of truth (CSS custom properties or DTCG JSON)
- [ ] Framework configs are derived from the canonical token source
- [ ] No raw values in component code — only token references

---

## 6. Token Transformation Pipeline (Style Dictionary)

For projects that need to maintain tokens across multiple platforms, use
[Style Dictionary](https://amzn.github.io/style-dictionary/):

```javascript
// config.json
{
  "source": ["tokens/**/*.json"],
  "platforms": {
    "css": {
      "transformGroup": "css",
      "buildPath": "dist/css/",
      "files": [{
        "destination": "tokens.css",
        "format": "css/variables",
        "options": {
          "outputReferences": true
        }
      }]
    },
    "scss": {
      "transformGroup": "scss",
      "buildPath": "dist/scss/",
      "files": [{
        "destination": "_tokens.scss",
        "format": "scss/variables"
      }]
    },
    "js": {
      "transformGroup": "js",
      "buildPath": "dist/js/",
      "files": [{
        "destination": "tokens.js",
        "format": "javascript/es6"
      }]
    },
    "tailwind": {
      "transformGroup": "js",
      "buildPath": "dist/tailwind/",
      "files": [{
        "destination": "tokens.tailwind.js",
        "format": "javascript/module"
      }]
    }
  }
}
```

---

## 7. References

- [W3C Design Tokens Community Group](https://tr.designtokens.org/) —
  Official DTCG specification draft
- [Style Dictionary](https://amzn.github.io/style-dictionary/) —
  Multi-platform token transformation
- [Figma Tokens Plugin](https://docs.tokens.studio/) —
  Token management inside Figma
- [Tailwind CSS Customization](https://tailwindcss.com/docs/theme) —
  Tailwind theme configuration
- [CSS Custom Properties (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties) —
  CSS custom properties reference
- [open-props](https://open-props.style/) —
  Open-source design tokens as CSS custom properties