# Locator Strategies Reference

## Priority Hierarchy

Always use the most specific, accessible, and resilient locator first.

### Tier 1: Semantic Locators (Always Preferred)

| Locator | Usage | Resilience |
|---------|-------|------------|
| `getByRole('button', { name: 'Submit' })` | Any interactive element | ★★★★★ |
| `getByLabel('Email')` | Form inputs with `<label>` | ★★★★★ |
| `getByText('Welcome back')` | Static text content | ★★★★☆ |
| `getByPlaceholder('Search...')` | Inputs with placeholder | ★★★☆☆ |
| `getByAltText('Logo')` | Images with alt text | ★★★★☆ |
| `getByTitle('Close')` | Elements with title attr | ★★★☆☆ |

### Tier 2: Data Attributes (Fallback)

| Locator | Usage | Resilience |
|---------|-------|------------|
| `getByTestId('checkout-button')` | When no semantic element exists | ★★★☆☆ |

### Tier 3: CSS/XPath (Avoid)

| Locator | Usage | Resilience |
|---------|-------|------------|
| `locator('.btn-primary')` | CSS class targeting | ★☆☆☆☆ |
| `locator('#submit')` | ID targeting | ★★☆☆☆ |
| `locator('button >> nth=0')` | Positional | ☆☆☆☆☆ |

## Anti-Patterns — Examples to Avoid

```typescript
// ❌ POSITIONAL — breaks when DOM changes
await page.locator('button').first().click();
await page.locator('div > div:nth-child(3) > button').click();

// ❌ CSS CLASS — coupling to styling
await page.locator('.bg-blue-500.hover\\:bg-blue-600').click();

// ❌ XPath — slow, fragile, unreadable
await page.locator('//div[@class="modal"]//button[contains(text(),"OK")]').click();

// ❌ Visible text that changes with i18n
await page.getByText('Submit').click(); // Will break in other languages
```

## Best Practice Patterns

```typescript
// ✅ Role + accessible name
await page.getByRole('button', { name: /submit/i }).click();

// ✅ Label association
await page.getByLabel('Email address').fill('user@test.com');

// ✅ Role filter with current state
await page.getByRole('button', { name: 'Save', disabled: false }).click();

// ✅ Chained selectors for repeated structures
const row = page.getByRole('row', { name: /Order #1234/ });
await row.getByRole('button', { name: 'View details' }).click();

// ✅ Filter by text for dynamic lists
await page.getByRole('listitem').filter({ hasText: 'In stock' }).click();

// ✅ Test ID as escape hatch
await page.getByTestId('pricing-total').toHaveText('$99.00');
```

## Framework-Specific Guidance

### React

- Use `data-testid` attributes sparingly; prefer accessible roles
- Components should expose ARIA roles and labels properly
- Use `getByRole` with accessible names from your component API

### Angular

- Leverage built-in accessibility (Angular components often have good roles)
- Use `data-cy` or `data-test` attributes consistently
- Angular Material components have predictable role patterns

### Vue

- Use `data-test` as fallback; prefer semantic HTML
- Vue Test Utils integration works with component mounting
- Template refs don't map to DOM; don't rely on them