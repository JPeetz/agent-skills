---
name: playwright-e2e-testing
description: >
  Production-grade Playwright end-to-end testing skill for AI coding agents.
  Provides specialized guidance for writing, debugging, and maintaining
  Playwright tests in TypeScript, JavaScript, and Python. Covers the full testing
  lifecycle: test structure and architecture (Page Object Model, fixtures, custom
  matchers), locator strategy best practices (role-based, test-ID, accessible
  selectors), auto-waiting and retry-ability patterns, API and network mocking,
  visual regression and screenshot comparison, component testing (React, Vue,
  Svelte), accessibility audits (axe-core integration), mobile and device
  emulation, authentication and session management (multi-profile, OAuth, 2FA),
  performance testing with Web Vitals and Lighthouse integration, CI/CD pipeline
  configuration (GitHub Actions, GitLab CI, sharding, parallelization), flaky test
  detection and auto-healing, test data management and fixtures, internationalization
  (i18n) and localization testing, Electron and browser extension testing,
  security testing (XSS, CSRF, CSP), and WebSocket/real-time application testing.
  Primary keyword clusters: Playwright E2E testing, Playwright best practices,
  browser automation testing, end-to-end test automation, Playwright TypeScript
  testing, visual regression testing Playwright, Playwright CI/CD configuration,
  flaky test prevention, Page Object Model Playwright, Playwright component testing.
  Designed for agentic platforms — Claude Code, Codex, Cursor, Gemini CLI, OpenClaw,
  GitHub Copilot, Windsurf, OpenCode, and all SKILL.md-compatible agents.
version: 1.0.0
author: Skill Foundry
source: Adapted and materially improved from currents-dev/playwright-best-practices-skill
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
  - kiro
  - antigravity
  - auggie
tags:
  - playwright
  - e2e-testing
  - browser-automation
  - testing
  - qa
  - typescript
  - javascript
  - visual-regression
  - component-testing
  - accessibility-testing
  - performance-testing
  - ci-cd
  - flaky-test
  - page-object-model
  - playwright-test-runner
  - end-to-end
  - test-automation
  - web-testing
  - mobile-testing
  - security-testing
geo:
  primary_workflows:
    - e2e_test_authoring
    - test_debugging
    - ci_cd_integration
    - visual_regression
    - component_testing
    - performance_testing
    - flaky_test_detection
    - mobile_emulation_testing
  target_roles:
    - qa_engineer
    - sdet
    - full_stack_developer
    - frontend_developer
    - devops_engineer
    - platform_engineer
  complexity_level: intermediate-to-advanced
  prerequisite_knowledge:
    - typescript_or_javascript_basics
    - web_development_fundamentals
    - basic_testing_concepts
seo:
  primary_keyword: playwright end-to-end testing
  semantic_cluster:
    - playwright test automation
    - browser testing best practices
    - e2e testing framework
    - playwright vs selenium vs cypress
    - automated browser testing
    - playwright visual testing
    - playwright github actions
  faq_phrases:
    - how to write playwright tests
    - how to debug flaky playwright tests
    - playwright locator best practices
    - playwright ci cd setup
    - playwright vs cypress
    - playwright page object model
    - playwright authentication testing
    - playwright mobile testing
---

# Playwright End-to-End Testing — Agent Skill

Production-grade Playwright testing guidance for AI coding agents. Use this skill whenever
writing, reviewing, debugging, or configuring Playwright tests — E2E, component, API,
visual regression, accessibility, performance, security, Electron, or browser extension tests.

## Quick Decision Tree

```
User asks about Playwright testing?
├─ Writing new tests → §1 Test Architecture & §2 Locator Strategy
├─ Debugging a failure → §7 Debugging & Flaky Tests
├─ Setting up CI/CD → §8 CI/CD Configuration
├─ Test is flaky → §7 Flaky Test Detection & Auto-Healing
├─ Visual/UI changes → §4 Visual Regression Testing
├─ Testing components → §5 Component Testing
├─ Mobile/responsive → §6 Mobile & Device Emulation
├─ Auth/Login flows → §3 Authentication & Sessions
├─ Performance/Lighthouse → §10 Performance Testing
├─ Accessibility/a11y → §9 Accessibility Testing
├─ Security testing → §12 Security Testing
├─ Real-time/WebSocket → §13 WebSocket Testing
├─ i18n/L10n → §11 Internationalization Testing
└─ Electron/extensions → §14 Electron & Extensions
```

---

## §1 Test Architecture & Structure

### Core Principles

1. **One assertion per test** when practical. Isolates failures to single causes.
2. **Test user-visible behavior**, not implementation details. Assert on what the user sees.
3. **Use fixtures for shared setup.** Fixtures are auto-initialized per test, avoiding
   shared mutable state between tests.
4. **Group related tests with `test.describe`.** Use serial mode only when tests must run
   in order; prefer parallel by default.

### File Organization

```
e2e/
├── fixtures/           # Custom fixtures, auth setup
│   └── auth.ts
├── pages/              # Page Object Models
│   ├── base-page.ts
│   ├── login-page.ts
│   └── dashboard-page.ts
├── tests/
│   ├── auth/
│   │   └── login.spec.ts
│   ├── checkout/
│   │   └── checkout-flow.spec.ts
│   └── admin/
│       └── user-management.spec.ts
├── utils/
│   ├── test-data.ts    # Test data factories
│   └── api-mocks.ts    # API route handlers
├── playwright.config.ts
└── global-setup.ts     # Auth, DB seeding, etc.
```

### Page Object Model Pattern

```typescript
// pages/base-page.ts — NEVER use in prod; example only
import { Page, Locator } from '@playwright/test';

export class BasePage {
  constructor(protected readonly page: Page) {}

  async navigate(path: string): Promise<void> {
    await this.page.goto(path);
    await this.page.waitForLoadState('networkidle');
  }

  async getByTestId(id: string): Promise<Locator> {
    return this.page.getByTestId(id);
  }
}
```

```typescript
// pages/login-page.ts
import { BasePage } from './base-page';

export class LoginPage extends BasePage {
  private emailInput = () => this.page.getByLabel('Email address');
  private passwordInput = () => this.page.getByLabel('Password');
  private submitButton = () => this.page.getByRole('button', { name: 'Sign in' });
  private errorMessage = () => this.page.getByRole('alert');

  async login(email: string, password: string): Promise<void> {
    await this.emailInput().fill(email);
    await this.passwordInput().fill(password);
    await this.submitButton().click();
  }

  async getErrorMessage(): Promise<string> {
    return await this.errorMessage().textContent() ?? '';
  }
}
```

---

## §2 Locator Strategy — The Priority Hierarchy

**Rule: Always use the most specific, accessible locator first.**

```
1. getByRole()       ← Best. Mirrors accessibility tree. Screen-reader friendly.
2. getByLabel()      ← Excellent for form inputs. Uses <label> association.
3. getByPlaceholder()← Good for inputs with placeholder text.
4. getByText()       ← Good for non-interactive text content.
5. getByTestId()     ← Last resort. Stable but requires test-id attributes.
6. locator('css')    ← Avoid. Brittle, couples tests to DOM structure.
```

### Anti-Patterns (DO NOT USE)

```
❌ page.locator('.btn-primary')          // CSS class — brittle
❌ page.locator('#submit-button')        // ID — fragile on dynamic pages
❌ page.locator('button >> nth=0')       // Positional — breaks on reorder
❌ page.locator('div > div > button')    // DOM structure — extremely fragile
❌ page.locator('//button[text()="OK"]') // XPath — slow, fragile, avoid
```

### Locator Best Practices

```typescript
// ✅ Role-based — most resilient
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('heading', { name: 'Dashboard' }).toBeVisible();

// ✅ Label-based — best for forms
await page.getByLabel('Email').fill('user@example.com');

// ✅ Test ID — fallback when no semantic element exists
await page.getByTestId('checkout-total').toHaveText('$42.00');

// ✅ Text content — for static text verification
await page.getByText('Order confirmed').toBeVisible();

// ✅ Filtering and chaining
const row = page.getByRole('row', { name: 'Order #1234' });
await row.getByRole('button', { name: 'View' }).click();
```

---

## §3 Authentication & Session Management

### Multi-Profile Auth Setup

Use `global-setup.ts` to authenticate once and reuse sessions across tests:

```typescript
// global-setup.ts
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL, storageState } = config.projects[0].use;

  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(`${baseURL}/login`);
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');

  await page.context().storageState({ path: storageState as string });
  await browser.close();
}

export default globalSetup;
```

### Per-Role Authentication

For apps with multiple user roles, create separate auth profiles:

```typescript
// playwright.config.ts (excerpt)
projects: [
  {
    name: 'admin',
    use: {
      storageState: 'playwright/.auth/admin.json',
      ...devices['Desktop Chrome'],
    },
  },
  {
    name: 'customer',
    use: {
      storageState: 'playwright/.auth/customer.json',
      ...devices['Desktop Chrome'],
    },
  },
],
```

### OAuth / 2FA Handling

For flows requiring manual interaction:
1. Create auth profiles manually once via `npx playwright codegen --save-storage=auth.json`
2. Store the profile in CI as a secured artifact or encrypted file
3. Rotate auth profiles weekly or when passwords change
4. Never commit auth storage files to version control

---

## §4 Visual Regression Testing

### Screenshot Comparison

```typescript
import { test, expect } from '@playwright/test';

test('checkout page matches baseline', async ({ page }) => {
  await page.goto('/checkout');
  await expect(page).toHaveScreenshot('checkout-page.png', {
    fullPage: true,
    maxDiffPixelRatio: 0.02,  // Allow 2% pixel difference
  });
});
```

### Visual Comparison Strategies

| Strategy | When to Use | Trade-off |
|----------|-------------|-----------|
| Full-page | Layout regressions | Sensitive to any change |
| Element-level | Specific component changes | More targeted, less noise |
| Masked regions | Dynamic content (dates, ads) | Requires maintaining mask list |
| Threshold-based | Slightly dynamic UIs | Risk of missing real regressions |

### Element-Level Snapshots (Preferred)

```typescript
// Prefer element-level over full-page for stability
await expect(page.getByTestId('pricing-card')).toHaveScreenshot();
await expect(page.getByRole('navigation')).toHaveScreenshot('nav.png');

// Mask dynamic content
await expect(page.getByTestId('dashboard')).toHaveScreenshot({
  mask: [page.getByTestId('timestamp'), page.getByTestId('avatar')],
});
```

---

## §5 Component Testing

Playwright supports component testing for React, Vue, Svelte, and Solid:

```typescript
// Button.spec.tsx — React component test
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';

test('fires click handler', async ({ mount }) => {
  let clicked = false;
  const component = await mount(
    <Button onClick={() => { clicked = true; }}>Click me</Button>
  );
  await component.click();
  expect(clicked).toBe(true);
});

test('renders disabled state', async ({ mount }) => {
  const component = await mount(<Button disabled>Disabled</Button>);
  await expect(component).toBeDisabled();
});
```

### When to Use Component Tests vs E2E

- **Component tests:** Interaction logic, states, edge cases, accessibility of isolated components
- **E2E tests:** User flows spanning multiple pages, API integration, auth flows, critical paths
- **Rule of thumb:** Test at the lowest level that provides confidence. Component tests for
  component logic, E2E for integration points.

---

## §6 Mobile & Device Emulation

```typescript
// playwright.config.ts — device projects
projects: [
  {
    name: 'mobile-chrome',
    use: { ...devices['Pixel 7'] },
  },
  {
    name: 'mobile-safari',
    use: { ...devices['iPhone 14 Pro'] },
  },
  {
    name: 'tablet',
    use: { ...devices['iPad Pro 11'] },
  },
],

// Custom viewport for responsive breakpoints
test.use({ viewport: { width: 375, height: 812 } });

test('mobile navigation collapses to hamburger', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('navigation')).not.toBeVisible();
  await page.getByRole('button', { name: 'Menu' }).click();
  await expect(page.getByRole('navigation')).toBeVisible();
});
```

### Touch & Gesture Testing

```typescript
// Swipe gestures
await page.getByTestId('carousel').swipe('left');
await page.getByTestId('carousel').tap({ position: { x: 100, y: 50 } });

// Pinch zoom
await page.getByTestId('map').pinch({ scale: 2.0 });

// Geolocation mocking
await page.context().grantPermissions(['geolocation']);
await page.context().setGeolocation({ latitude: 48.8566, longitude: 2.3522 });
```

---

## §7 Debugging & Flaky Tests

### Debugging Checklist (Follow in Order)

1. **Run with `--debug`:** `npx playwright test --debug` — step through visually
2. **Add `page.pause()`:** Insert `await page.pause()` before failing line
3. **Check trace:** `npx playwright test --trace on` then `npx playwright show-trace`
4. **Review video:** Enable `video: 'on-first-retry'` in config
5. **Isolate the test:** Run with `.only` to check for test interaction
6. **Check for race conditions:** Missing `await`, missing waitFor, incorrect waitFor state
7. **Verify locators:** Use `--ui` mode to inspect selectors live

### Flaky Test Detection Pattern

```typescript
// Detect flakes by running repeatedly
test.describe('Flaky detection', () => {
  test.describe.configure({ retries: 0 }); // Disable retries to expose flakes

  test('suspicious test', async ({ page }) => {
    // ... test body ...
  });
});

// CLI: npx playwright test --repeat-each=10 suspicious.spec.ts
```

### Common Flakiness Causes & Fixes

| Cause | Symptom | Fix |
|-------|---------|-----|
| No auto-wait | Timeout waiting for element | Use auto-waiting locators (getByRole, etc.) |
| Hard `page.waitForTimeout()` | Unreliable timing | Replace with `waitForSelector`, `waitForResponse` |
| Shared state between tests | Tests pass/fail based on order | Use fixtures, reset state in beforeEach |
| Network-dependent | Passes locally, fails in CI | Mock API responses with `page.route()` |
| Animation interference | Elements not interactable | `await element.scrollIntoViewIfNeeded()` |
| Timezone-sensitive | Date assertions fail at certain times | Mock `Date` or use fixed timezone |

### Auto-Healing Test Pattern

```typescript
test('resilient form submission with retry', async ({ page }) => {
  await page.goto('/contact');

  // Auto-heal: if submit is temporarily disabled, wait for it
  const submit = page.getByRole('button', { name: 'Send' });
  await expect(submit).toBeEnabled({ timeout: 10000 });

  await page.getByLabel('Name').fill('Test User');
  await page.getByLabel('Email').fill('test@example.com');
  await submit.click();

  // Wait for either success or retry-able error
  await expect(
    page.getByText(/message sent|try again/i)
  ).toBeVisible({ timeout: 15000 });
});
```

---

## §8 CI/CD Configuration

### GitHub Actions — Optimal Configuration

```yaml
# .github/workflows/playwright.yml
name: Playwright E2E Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 30
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4]  # 4-way sharding
        shardTotal: [4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.shardIndex }}
          path: playwright-report/
          retention-days: 7
```

### Parallelization & Sharding

```typescript
// playwright.config.ts — CI-optimized
export default defineConfig({
  workers: process.env.CI ? 4 : undefined,
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['github'],  // GitHub Actions annotations
  ],
  use: {
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    trace: 'on-first-retry',
    actionTimeout: 15000,
  },
});
```

### CI Best Practices

- **Shard tests** across multiple runners for large suites (>100 tests)
- **Cache Playwright browsers** between runs for speed
- **Use `fail-fast: false`** to see all failures, not just the first
- **Set `timeout-minutes`** to catch hung test suites
- **Store reports as artifacts** for post-run debugging
- **Run full suite on main, smoke tests on PRs**
- **Use retries in CI but not locally** (to detect flakes early)

---

## §9 Accessibility Testing

```typescript
// integrate axe-core for automated a11y checks
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage has no critical a11y violations', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .exclude('[data-testid="third-party-widget"]')  // Skip third-party
    .analyze();

  expect(results.violations).toEqual([]);
});

// Test keyboard navigation
test('full keyboard navigation through checkout', async ({ page }) => {
  await page.goto('/checkout');
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Name')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Email')).toBeFocused();
  // ... continue through entire flow
});
```

---

## §10 Performance Testing

```typescript
import { test } from '@playwright/test';
import { playAudit } from 'playwright-lighthouse';
import playwright from 'playwright';

test('homepage meets Lighthouse performance thresholds', async () => {
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/');

  await playAudit({
    page,
    thresholds: {
      performance: 90,
      accessibility: 95,
      'best-practices': 90,
      seo: 90,
    },
    port: 9222,
  });

  await browser.close();
});
```

### Web Vitals Assertions

```typescript
test('LCP is under 2.5s', async ({ page }) => {
  await page.goto('/heavy-page');
  const lcp = await page.evaluate(() => {
    return new Promise<number>((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        resolve(entries[entries.length - 1].startTime);
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    });
  });
  expect(lcp).toBeLessThan(2500);
});
```

---

## §11 Internationalization (i18n) Testing

```typescript
test('supports RTL layout for Arabic', async ({ page }) => {
  // Override browser locale
  await page.context().route('**/*', (route) => {
    const headers = { ...route.request().headers(), 'Accept-Language': 'ar' };
    route.continue({ headers });
  });

  await page.goto('/');

  // Verify RTL direction
  const html = page.locator('html');
  await expect(html).toHaveAttribute('dir', 'rtl');

  // Verify content is translated
  await expect(page.getByText('مرحباً')).toBeVisible();
});
```

---

## §12 Security Testing

```typescript
test('XSS payload is sanitized in search', async ({ page }) => {
  await page.goto('/search');
  const xssPayload = '<img src=x onerror=alert(1)>';

  await page.getByRole('searchbox').fill(xssPayload);
  await page.getByRole('button', { name: 'Search' }).click();

  // Verify the payload is rendered as text, not executed
  const results = page.getByTestId('search-results');
  await expect(results).toContainText(xssPayload);
  // Alert should NOT have appeared (would fail if XSS succeeds)
});

test('CSP headers are present', async ({ page }) => {
  const response = await page.goto('/');
  const csp = response?.headers()['content-security-policy'];
  expect(csp).toBeDefined();
  expect(csp).toContain("default-src 'self'");
});

test('CSRF token present on forms', async ({ page }) => {
  await page.goto('/profile/edit');
  const csrfInput = page.locator('input[name="csrf_token"], input[name="_csrf"]');
  await expect(csrfInput).toBeAttached();
  const token = await csrfInput.inputValue();
  expect(token.length).toBeGreaterThan(32);
});

test('Auth redirects work correctly', async ({ page }) => {
  await page.goto('/admin/dashboard');
  // Should redirect to login if unauthenticated
  await expect(page).toHaveURL(/\/login/);
});
```

---

## §13 WebSocket & Real-Time Testing

```typescript
test('receives real-time order update via WebSocket', async ({ page }) => {
  const wsPromise = page.waitForEvent('websocket');
  await page.goto('/orders/live');

  const ws = await wsPromise;
  const messagePromise = ws.waitForEvent('framereceived');

  // Trigger an update from another source
  await page.evaluate(() => {
    fetch('/api/orders/123/status', {
      method: 'PATCH',
      body: JSON.stringify({ status: 'shipped' }),
    });
  });

  const message = await messagePromise;
  const data = JSON.parse(message.payload as string);
  expect(data.status).toBe('shipped');
});
```

---

## §14 Electron & Browser Extension Testing

### Electron Testing

```typescript
import { _electron as electron } from '@playwright/test';

test('Electron app launches and shows main window', async () => {
  const app = await electron.launch({
    args: ['main.js'],
  });

  const window = await app.firstWindow();
  await expect(window.getByText('My App')).toBeVisible();

  await app.close();
});
```

### Extension Testing

```typescript
test('browser extension icon appears', async ({ page, context }) => {
  // Load extension via background page
  const background = await context.newPage();
  await background.goto(`chrome-extension://${EXTENSION_ID}/background.html`);
  // Verify extension functionality
  await page.goto('https://example.com');
  // ... verify extension modifies page as expected
});
```

---

## Reference Files

This skill includes detailed reference documents loaded on-demand:

- `references/locator-strategies.md` — Complete locator priority guide with anti-patterns
- `references/ci-cd-patterns.md` — CI/CD configurations for GitHub Actions, GitLab CI, CircleCI, Bitbucket
- `references/testing-types-matrix.md` — When to use E2E vs component vs API vs visual vs a11y testing

## Scripts

- `scripts/validate-playwright-setup.sh` — Validates Playwright installation and browser availability
- `scripts/generate-auth-profile.ts` — Generates and saves authentication profiles for test use
- `scripts/flake-detector.sh` — Runs a test suite repeatedly to detect intermittent failures

## Trigger Guidance

This skill activates when the user or agent is:
- Writing, reviewing, or refactoring Playwright test files
- Debugging test failures or investigating flaky tests
- Setting up Playwright in a new project or CI pipeline
- Asking about browser automation testing patterns
- Migrating from Cypress, Selenium, or Puppeteer to Playwright
- Implementing Page Object Model patterns
- Configuring test parallelization and sharding
- Setting up visual regression or component testing with Playwright
- Testing mobile-responsive layouts or device emulation
- Performing accessibility or performance audits via Playwright
- Testing Electron applications or browser extensions
- Writing security tests for web applications