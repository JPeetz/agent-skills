# Selector Strategies — Reference

Robust selector strategies for browser automation. Ordered by stability and maintainability — prefer the top, avoid the bottom.

## The Selector Hierarchy

```
Most Stable
    ↑
    │  1. data-testid       ← Purpose-built for testing; survives all refactors
    │  2. Role-based        ← Accessibility-first; semantic and stable
    │  3. Text content      ← User-visible; changes when UX changes
    │  4. Label             ← Tied to form field labels; stable for forms
    │  5. Placeholder       ← Decent temporary anchor; fragile over time
    │  6. CSS class/id      ← Tied to implementation; breaks on redesign
    │  7. XPath             ← Explicit DOM path; extremely brittle
    ↓
Least Stable
```

## 1. `data-testid` (★★★★★ — Best)

Purpose-built attribute that is never changed for visual reasons. Survives CSS rewrites, class renaming, and layout refactors.

```python
# Playwright helpers
page.get_by_test_id("submit-button")           # [data-testid="submit-button"]
page.get_by_test_id("user-name")
page.get_by_test_id("item-3")

# Raw locator
page.locator("[data-testid='sidebar-nav']")

# Filter children within a testid container
page.get_by_test_id("product-list").get_by_test_id("product-card").first
```

**Why it wins:** The attribute exists solely for testing. CSS, text, and structure can change freely without breaking tests.

### Implementing data-testid in Your Frontend

```tsx
// React
<button data-testid="checkout-submit">Place Order</button>

// Vue
<button :data-testid="'checkout-submit'">Place Order</button>

// Svelte
<button data-testid="checkout-submit">Place Order</button>
```

**Naming convention:** `{component}-{action}` or `{page}-{element}`
- `login-email-input`, `login-submit-button`
- `cart-item-3`, `cart-checkout-button`
- `nav-dashboard-link`, `nav-settings-link`

Don't use sequential indices unless the order is truly fixed (e.g., `cart-item-3` for a specific known item).

## 2. Role-Based (★★★★★ — Best for Accessibility)

Leverages ARIA roles and accessible names. These are naturally stable because they map to what users perceive.

```python
# Buttons
page.get_by_role("button", name="Submit")
page.get_by_role("button", name="Add to Cart")

# Links / navigation
page.get_by_role("link", name="Dashboard")
page.get_by_role("link", name="View Details")

# Form elements
page.get_by_role("textbox", name="Email")
page.get_by_role("checkbox", name="I agree to terms")
page.get_by_role("combobox", name="Country")
page.get_by_role("radio", name="Credit Card")

# Headings
page.get_by_role("heading", name="Welcome Back")
page.get_by_role("heading", name="Order Summary", level=2)

# Lists & tables
page.get_by_role("listitem")
page.get_by_role("row", name="Invoice #1234")
page.get_by_role("cell", name="$49.99")

# Alerts & dialogs
page.get_by_role("alert")
page.get_by_role("dialog", name="Confirm Delete")

# Images
page.get_by_role("img", name="Company Logo")

# Navigation landmarks
page.get_by_role("navigation")
page.get_by_role("banner")      # <header>
page.get_by_role("contentinfo") # <footer>
```

**Why it wins:** Screen readers depend on these roles. If the role breaks, accessibility breaks too — so teams are incentivized to keep them correct.

### Exact vs Include Name Matching

```python
# Exact match (default in Playwright)
page.get_by_role("button", name="Submit")       # Matches exactly "Submit"

# Include match (partial)
page.get_by_role("button", name="Submit", exact=False)  # Matches "Submit Form", "Submit and Pay"
```

## 3. Text Content (★★★★☆ — Good)

Matches user-visible text. Changes when the copy changes, but survives CSS and DOM restructuring.

```python
# Exact text
page.get_by_text("Sign In")
page.get_by_text("No results found")

# Partial text
page.get_by_text("Welcome back", exact=False)
page.get_by_text("results", exact=False)

# Text within a specific element type
page.locator("h1").get_by_text("Dashboard")

# Combining text with other constraints
page.get_by_text("Add to Cart").first  # if multiple matches exist
```

**Gotcha:** Text selectors match the full text node by default. `page.get_by_text("Submit")` won't match `<button>Submit Form</button>` unless you use `exact=False`.

## 4. Label (★★★★☆ — Good for Forms)

Tied to `<label>` elements. Inherently stable because labels are part of the form's UX contract.

```python
# Inputs with associated <label>
page.get_by_label("Email address")
page.get_by_label("Password")
page.get_by_label("Phone Number")

# Checkboxes
page.get_by_label("Receive marketing emails")

# Radio groups (use the legend/first label)
page.get_by_label("Shipping Method")
```

**Works with:**
```html
<!-- Explicit label -->
<label for="email">Email address</label>
<input id="email" type="email">

<!-- Implicit label -->
<label>Email address <input type="email"></label>

<!-- aria-label -->
<input aria-label="Email address" type="email">
```

## 5. Placeholder (★★★☆☆ — Acceptable)

Matches the `placeholder` attribute. Useful when labels aren't present, but less stable — placeholders often change for UX polish.

```python
page.get_by_placeholder("Search products...")
page.get_by_placeholder("Enter your email")
page.get_by_placeholder("MM/DD/YYYY")
```

**Caveat:** Placeholders are supplementary, not primary UX. They may be removed or changed by designers. Use only when `get_by_label` isn't available.

## 6. CSS Selectors (★★☆☆☆ — Fragile)

Tied to implementation details — class names, IDs, DOM structure. Survives content changes but breaks on redesign.

```python
# ID (moderately stable, but IDs should be unique)
page.locator("#login-form")
page.locator("#submit-btn")

# Class (fragile — classes change with CSS refactors)
page.locator(".btn-primary")
page.locator(".user-profile .avatar")

# Attribute
page.locator("input[name='email']")
page.locator("[type='submit']")

# Hierarchy (very fragile — breaks on any DOM restructuring)
page.locator("div.container > form > div:nth-child(2) > input")

# Combining
page.locator("form#login input[type='email']")
page.locator(".modal .footer button:has-text('Confirm')")
```

**When to use CSS:** When you're scraping a third-party site that doesn't have testids, and you need to target specific elements. Combine with text/role filters to add stability.

```python
# Better than pure CSS: CSS + role/text filtering
page.locator("form").get_by_role("button", name="Submit")
page.locator(".product-grid").get_by_text("Add to Cart")
```

## 7. XPath (★★☆☆☆ — Most Brittle)

Explicit DOM traversal. Breaks on virtually any DOM change. Only use as absolute last resort.

```python
# Absolute path (NEVER use this)
page.locator("/html/body/div[2]/div[1]/form/div[3]/button")

# Relative with text constraint (marginally better)
page.locator("//button[contains(text(), 'Submit')]")
page.locator("//div[@class='result']//span[@data-price]")

# Following sibling, parent traversal (fragile)
page.locator("//label[text()='Email']/following-sibling::input")
page.locator("//span[text()='Delete']/ancestor::tr")
```

**Only justification for XPath:** When you need complex DOM relationship queries that CSS can't express, AND you can't use role/text selectors. This should be < 1% of selectors.

## Strategy Selection Decision Tree

```
Can you add data-testid to the source?
  ├─ YES → Use data-testid. Done. ⭐
  └─ NO  → Is the element interactive and semantic?
            ├─ YES → Use get_by_role(). ⭐
            └─ NO  → Does the text stay the same across locales?
                      ├─ YES → Use get_by_text(). ✔
                      └─ NO  → Is there an associated label?
                                ├─ YES → Use get_by_label(). ✔
                                └─ NO  → Is there a reasonably stable CSS path?
                                          ├─ YES → Use CSS + text/role filter. ⚠
                                          └─ NO  → XPath as last resort. ❌
```

## Common Pitfalls

### Strict Mode Violations

Playwright enforces strict mode by default — a selector that matches multiple elements will throw.

```python
# ❌ Throws if multiple "Add to Cart" buttons exist
await page.get_by_text("Add to Cart").click()

# ✅ Fix with .first, .nth(), or .filter()
await page.get_by_text("Add to Cart").first.click()
await page.get_by_text("Add to Cart").nth(2).click()
await page.get_by_test_id("product-3").get_by_text("Add to Cart").click()
```

### Dynamic IDs

```python
# ❌ Generated IDs change on every render
page.locator("#component-abc123-def456")

# ✅ Use stable attributes
page.get_by_test_id("user-profile")
```

### CSS Module Class Names

```python
# ❌ CSS modules produce hashed class names like .Button_hash1a2b3c
page.locator(".Button_hash1a2b3c")

# ✅ Use testid or role
page.get_by_role("button", name="Submit")
```

### i18n / Localized Text

```python
# ❌ Breaks when locale changes
page.get_by_text("Sign In")

# ✅ Use testid if i18n is a concern
page.get_by_test_id("login-submit")
# Or use data attributes
page.locator("[data-action='login']")
```

## Selector Debugging

```python
# Count matches
count = await page.locator(".product-card").count()
print(f"Found {count} elements")

# Inspect what matches
texts = await page.locator("button").all_text_contents()
print(texts)

# Verify visibility
is_visible = await page.get_by_test_id("submit").is_visible()
print(f"Submit visible: {is_visible}")

# Playwright codegen (auto-generates selectors by clicking)
# Terminal: playwright codegen https://example.com

# Playwright Inspector
await page.pause()
```

## Framework-Specific Selectors

### React
```tsx
// Good: data-testid
<button data-testid="submit-order">Place Order</button>

// Also works: aria-label with dynamic content
<button aria-label={`Delete ${item.name}`}>Delete</button>
```

### Vue
```html
<!-- Good: data-testid with : binding -->
<button :data-testid="`item-${item.id}-delete`">Delete</button>

<!-- Good: role with dynamic name -->
<button :aria-label="`Delete ${item.name}`">Delete</button>
```

### Angular
```html
<!-- Good: data-testid with property binding -->
<button [attr.data-testid]="'user-' + userId + '-edit'">Edit</button>
```

### Shadow DOM
```python
# Playwright pierces shadow DOM automatically
page.locator("custom-element").get_by_role("button", name="Submit")

# Explicit shadow piercing
page.locator("custom-element").locator("css=button")
```