# Testing Types Decision Matrix

## When to Use Which Test Type

| Scenario | Test Type | Tool | Cost | Confidence |
|----------|-----------|------|------|------------|
| Component renders correctly | Component | Playwright CT | Low | Medium |
| Button click fires handler | Component | Playwright CT | Low | High |
| Form validation logic | Component | Playwright CT | Low | High |
| API integration | Integration/E2E | Playwright | Medium | High |
| Full user checkout flow | E2E | Playwright | High | Very High |
| Visual layout regression | Visual | Playwright Screenshots | Low | Medium |
| Color contrast compliance | Accessibility | axe-core + Playwright | Low | High |
| Page load speed | Performance | Lighthouse + Playwright | Low | Medium |
| Cross-browser rendering | E2E | Playwright (multi-browser) | High | High |
| Mobile layout | E2E | Playwright device emulation | Medium | Medium |

## Test Type Selection Flowchart

```
Is the test about...
├─ Visual appearance only? → Visual Regression (screenshots)
├─ Isolated component logic? → Component Test (CT)
├─ User interaction in a browser? → E2E Test
│  ├─ Full user flow? → E2E (multi-page)
│  ├─ Form submission? → E2E (page.route for API mocking)
│  └─ Real API calls? → E2E (integration)
├─ Performance/Lighthouse? → Performance Test
├─ Accessibility compliance? → A11y Test (with axe-core)
├─ Security (XSS, CSRF, CSP)? → Security Test
└─ Mobile/touch/gesture? → E2E with device emulation
```

## Prioritization Matrix for Existing Projects

### Critical Path Tests (Must Have)
- Login/Authentication flows
- Core checkout/purchase flow
- Primary user onboarding
- Data creation/editing flows

### Important Tests (Should Have)
- Secondary user flows
- Error states and recovery
- Permission/RBAC testing
- Form validation edge cases

### Nice-to-Have Tests (Could Have)
- Visual regression of non-critical pages
- Performance benchmarks
- Third-party integration smoke tests
- i18n coverage for non-primary locales

## Test Count Guidelines by App Size

| App Size | Min E2E Tests | Max E2E Tests | Ideal Runtime |
|----------|---------------|---------------|---------------|
| Small (< 10 pages) | 5 | 20 | < 5 min |
| Medium (10-50 pages) | 20 | 100 | < 15 min |
| Large (50+ pages) | 50 | 300 | < 30 min |
| Enterprise | 100 | 500+ | < 45 min (with sharding) |

## Coverage Strategy

1. **Smoke tests** — 5-10 critical-path tests, run on every PR, < 2 min
2. **Full regression** — All tests, run on main merge, nightly
3. **Visual snapshot** — Run on main merge only (expensive)

## Migration Guidance

### From Cypress

| Cypress | Playwright |
|---------|-----------|
| `cy.get('[data-cy=btn]')` | `page.getByTestId('btn')` |
| `cy.intercept()` | `page.route()` |
| `cy.fixture()` | Import JSON directly |
| `cy.clock()` | `page.clock.install()` |
| `cy.session()` | `storageState` in config |

### From Selenium

| Selenium | Playwright |
|----------|-----------|
| `driver.findElement(By.id())` | `page.locator('#id')` / `page.getByRole()` |
| `WebDriverWait` | Auto-waiting (built-in) |
| `driver.manage().window()` | `page.setViewportSize()` |
| Grid/Remote | Sharding in CI matrix |
| `driver.quit()` | Automatic cleanup |