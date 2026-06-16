# Browser Testing Workflows — Reference

Production testing patterns for common web application flows. Each workflow includes setup, execution, assertions, and error handling.

## Login Flow Testing

### Standard Email/Password Login

```python
import pytest
from playwright.async_api import Page, expect

@pytest.mark.asyncio
async def test_login_success(page: Page):
    """Happy path: valid credentials redirect to dashboard."""
    await page.goto("/login", wait_until="networkidle")

    await page.get_by_label("Email").fill(os.environ["TEST_EMAIL"])
    await page.get_by_label("Password").fill(os.environ["TEST_PASSWORD"])
    await page.get_by_role("button", name="Sign In").click()

    # Verify redirect
    await expect(page).to_have_url("**/dashboard**", timeout=10000)
    await expect(page.get_by_text("Welcome back")).to_be_visible()

@pytest.mark.asyncio
async def test_login_invalid_credentials(page: Page):
    """Error path: wrong password shows error message."""
    await page.goto("/login")

    await page.get_by_label("Email").fill("wrong@example.com")
    await page.get_by_label("Password").fill("wrongpassword")
    await page.get_by_role("button", name="Sign In").click()

    await expect(page.get_by_role("alert")).to_be_visible()
    await expect(page.get_by_role("alert")).to_contain_text("Invalid credentials")
    # Confirm we stayed on login page
    await expect(page).to_have_url("**/login**")

@pytest.mark.asyncio
async def test_login_empty_fields(page: Page):
    """Validation: empty form shows field-level errors."""
    await page.goto("/login")
    await page.get_by_role("button", name="Sign In").click()

    # Check for validation errors
    await expect(page.get_by_text("Email is required")).to_be_visible()
    await expect(page.get_by_text("Password is required")).to_be_visible()
```

### OAuth / Social Login

```python
@pytest.mark.asyncio
async def test_google_login(page: Page):
    """OAuth flow: Google sign-in button redirects to Google."""
    await page.goto("/login")
    await page.get_by_role("button", name="Sign in with Google").click()

    # Should redirect to Google's OAuth page
    await expect(page).to_have_url(lambda url: "accounts.google.com" in url)
```

### Password Visibility Toggle

```python
@pytest.mark.asyncio
async def test_password_visibility_toggle(page: Page):
    await page.goto("/login")
    password_input = page.get_by_label("Password")
    toggle = page.get_by_test_id("password-toggle")

    # Default: masked
    await password_input.fill("secret123")
    assert await password_input.get_attribute("type") == "password"

    # Toggle: revealed
    await toggle.click()
    assert await password_input.get_attribute("type") == "text"

    # Toggle again: masked
    await toggle.click()
    assert await password_input.get_attribute("type") == "password"
```

### Rate Limiting

```python
@pytest.mark.asyncio
async def test_login_rate_limit(page: Page):
    """After N failed attempts, account should be temporarily locked."""
    await page.goto("/login")

    for i in range(6):  # Assuming 5-attempt limit
        await page.get_by_label("Email").fill(f"user{i}@example.com")
        await page.get_by_label("Password").fill("wrong")
        await page.get_by_role("button", name="Sign In").click()
        await page.wait_for_timeout(500)  # Brief pause for UI update

    # Should show rate-limit message
    await expect(
        page.get_by_text("Too many attempts")
    ).to_be_visible(timeout=5000)

    # Login button should be disabled
    await expect(page.get_by_role("button", name="Sign In")).to_be_disabled()
```

## Form Validation Workflow

### Multi-Field Validation

```python
@pytest.mark.asyncio
async def test_registration_form_validation(page: Page):
    await page.goto("/register")

    # Submit empty form
    await page.get_by_role("button", name="Create Account").click()

    errors = {
        "name": "Name is required",
        "email": "Email is required",
        "password": "Password must be at least 8 characters",
        "terms": "You must accept the terms",
    }

    for _field, message in errors.items():
        await expect(page.get_by_text(message)).to_be_visible()

@pytest.mark.asyncio
async def test_email_format_validation(page: Page):
    await page.goto("/register")

    invalid_emails = [
        ("not-an-email", "Please enter a valid email"),
        ("missing@domain", "Please enter a valid email"),
        ("@no-local-part.com", "Please enter a valid email"),
    ]

    for email, expected_error in invalid_emails:
        await page.get_by_label("Email").clear()
        await page.get_by_label("Email").fill(email)
        await page.get_by_label("Email").press("Tab")  # Trigger blur validation
        await expect(page.get_by_text(expected_error)).to_be_visible()

@pytest.mark.asyncio
async def test_password_strength_meter(page: Page):
    await page.goto("/register")
    strength_indicator = page.get_by_test_id("password-strength")

    # Weak password
    await page.get_by_label("Password").fill("12345")
    await expect(strength_indicator).to_contain_text("Weak")

    # Strong password
    await page.get_by_label("Password").fill("Tr0ub4dor&3Xampl3!")
    await expect(strength_indicator).to_contain_text("Strong")
```

### Dynamic Form Fields

```python
@pytest.mark.asyncio
async def test_conditional_fields(page: Page):
    """Fields that appear/disappear based on previous selections."""
    await page.goto("/register")

    # Select "Business" account type
    await page.get_by_label("Account Type").select_option("business")

    # Business-only fields should appear
    await expect(page.get_by_label("Company Name")).to_be_visible()
    await expect(page.get_by_label("VAT Number")).to_be_visible()

    # Switch to "Personal"
    await page.get_by_label("Account Type").select_option("personal")

    # Business-only fields should disappear
    await expect(page.get_by_label("Company Name")).to_be_hidden()
    await expect(page.get_by_label("VAT Number")).to_be_hidden()
```

### Multi-Step Wizard

```python
@pytest.mark.asyncio
async def test_multi_step_wizard(page: Page):
    await page.goto("/onboarding")

    # Step 1: Personal Info
    await page.get_by_label("Full Name").fill("Jane Doe")
    await page.get_by_label("Email").fill("jane@example.com")
    await page.get_by_role("button", name="Next").click()
    await expect(page.get_by_text("Step 2 of 4")).to_be_visible()

    # Step 2: Company Info
    await page.get_by_label("Company").fill("Acme Corp")
    await page.get_by_label("Industry").select_option("Technology")
    await page.get_by_role("button", name="Next").click()

    # Step 3: Preferences
    await page.get_by_label("Receive newsletter").check()
    await page.get_by_role("button", name="Next").click()

    # Step 4: Confirm
    await expect(page.get_by_text("Jane Doe")).to_be_visible()
    await expect(page.get_by_text("Acme Corp")).to_be_visible()
    await page.get_by_role("button", name="Complete Setup").click()

    # Success
    await expect(page.get_by_text("Setup complete")).to_be_visible()

@pytest.mark.asyncio
async def test_wizard_back_navigation(page: Page):
    """Navigate back and verify fields retain their values."""
    await page.goto("/onboarding")
    await page.get_by_label("Full Name").fill("Jane Doe")
    await page.get_by_role("button", name="Next").click()

    # Go back
    await page.get_by_role("button", name="Back").click()
    await expect(page.get_by_label("Full Name")).to_have_value("Jane Doe")

@pytest.mark.asyncio
async def test_wizard_step_indicator(page: Page):
    """Verify the step progress indicator updates correctly."""
    await page.goto("/onboarding")
    steps = page.get_by_test_id("step-indicator")

    assert "step 1" in (await steps.text_content()).lower()
    await page.get_by_role("button", name="Next").click()
    assert "step 2" in (await steps.text_content()).lower()
```

## Navigation Testing

### Link Integrity

```python
@pytest.mark.asyncio
async def test_nav_links_load_pages(page: Page):
    """Verify all main navigation links load without errors."""
    await page.goto("/")

    nav_links = page.locator("nav a")
    link_count = await nav_links.count()

    for i in range(link_count):
        link = nav_links.nth(i)
        href = await link.get_attribute("href")
        text = await link.text_content()

        if not href or href.startswith(("http", "mailto:", "tel:")):
            continue  # Skip external, mail, and tel links

        await link.click()
        await page.wait_for_load_state("networkidle")

        # Page should not show an error
        error_indicators = await page.locator(
            ".error-page, [data-testid='error-boundary'], h1:has-text('404'), h1:has-text('500')"
        ).count()
        assert error_indicators == 0, f"Navigation to '{href}' ({text}) showed an error page"

        await page.go_back()
```

### URL-Based Navigation

```python
@pytest.mark.asyncio
async def test_protected_routes_redirect_to_login(page: Page):
    """Unauthenticated users should be redirected to login."""
    protected_paths = [
        "/dashboard",
        "/settings",
        "/billing",
        "/admin",
    ]

    for path in protected_paths:
        await page.goto(path, wait_until="domcontentloaded")
        await expect(page).to_have_url("**/login**", timeout=5000)
        assert f"redirect={path}" in page.url.lower() or "returnurl" in page.url.lower(), \
            f"Missing redirect param for {path}"

@pytest.mark.asyncio
async def test_404_page(page: Page):
    await page.goto("/non-existent-page-abc123")

    await expect(page.locator("h1")).to_contain_text(
        re.compile(r"not found|404|doesn.?t exist", re.IGNORECASE)
    )
    # Should still have site navigation
    await expect(page.locator("nav")).to_be_visible()
```

### Breadcrumb Navigation

```python
@pytest.mark.asyncio
async def test_breadcrumb_navigation(page: Page):
    await page.goto("/products/category/subcategory/item-123")

    breadcrumbs = page.get_by_test_id("breadcrumbs").get_by_role("link")
    await expect(breadcrumbs).to_have_count(4)  # Home > Products > Category > Item

    # Click the second breadcrumb (Products)
    await breadcrumbs.nth(1).click()
    await expect(page).to_have_url("**/products**")
```

## Search & Filter Testing

### Basic Search

```python
@pytest.mark.asyncio
async def test_search_functionality(page: Page):
    await page.goto("/products")

    await page.get_by_placeholder("Search products").fill("laptop")
    await page.keyboard.press("Enter")
    await page.wait_for_load_state("networkidle")

    # Results should appear
    results = page.get_by_test_id("search-result")
    await expect(results.first).to_be_visible(timeout=10000)

    # All visible results should contain "laptop" (case-insensitive)
    count = await results.count()
    assert count > 0, "No search results found"

    for i in range(min(count, 10)):
        text = await results.nth(i).text_content()
        assert "laptop" in text.lower(), f"Result {i} doesn't mention 'laptop'"

@pytest.mark.asyncio
async def test_search_empty_state(page: Page):
    await page.goto("/products")
    await page.get_by_placeholder("Search products").fill("xyznonexistent12345")
    await page.keyboard.press("Enter")

    await expect(page.get_by_text("No results found")).to_be_visible()
    # Should suggest clearing filters or searching differently
    await expect(page.get_by_role("button", name="Clear")).to_be_visible()
```

### Faceted Filters

```python
@pytest.mark.asyncio
async def test_filter_combination(page: Page):
    await page.goto("/products")

    # Apply category filter
    await page.get_by_role("checkbox", name="Electronics").check()
    await page.wait_for_load_state("networkidle")

    # Apply price range
    await page.get_by_label("Min Price").fill("100")
    await page.get_by_label("Max Price").fill("500")
    await page.get_by_role("button", name="Apply").click()
    await page.wait_for_load_state("networkidle")

    # Verify filter badges are shown
    await expect(page.get_by_text("Electronics")).to_be_visible()
    await expect(page.get_by_text("$100 - $500")).to_be_visible()

    # Results should be filtered
    result_count = await page.get_by_test_id("result-count").text_content()
    assert int(re.search(r"\d+", result_count).group()) > 0

@pytest.mark.asyncio
async def test_clear_all_filters(page: Page):
    await page.goto("/products?category=electronics&min=100&max=500")
    await page.get_by_role("button", name="Clear All").click()

    # All filter badges should be gone
    await expect(page.get_by_test_id("active-filters")).to_be_empty()
```

### Sort Order

```python
@pytest.mark.asyncio
async def test_sort_by_price(page: Page):
    await page.goto("/products")

    await page.get_by_label("Sort by").select_option("price-asc")

    # Extract prices and verify ascending order
    prices = await page.get_by_test_id("product-price").all_text_contents()
    numeric_prices = [float(p.replace("$", "").replace(",", "")) for p in prices]
    assert numeric_prices == sorted(numeric_prices), "Prices not in ascending order"

    # Switch to descending
    await page.get_by_label("Sort by").select_option("price-desc")
    prices = await page.get_by_test_id("product-price").all_text_contents()
    numeric_prices = [float(p.replace("$", "").replace(",", "")) for p in prices]
    assert numeric_prices == sorted(numeric_prices, reverse=True)
```

## Shopping Cart & Checkout

### Add to Cart

```python
@pytest.mark.asyncio
async def test_add_to_cart(page: Page):
    await page.goto("/products/item-42")

    # Verify add-to-cart button exists and click it
    add_button = page.get_by_role("button", name="Add to Cart")
    await expect(add_button).to_be_enabled()
    await add_button.click()

    # Cart count should update
    await expect(page.get_by_test_id("cart-count")).to_have_text("1", timeout=5000)

    # Toast/notification
    await expect(page.get_by_text("Added to cart")).to_be_visible()

@pytest.mark.asyncio
async def test_add_to_cart_with_options(page: Page):
    """Product with size/color variants."""
    await page.goto("/products/item-42")

    # Select options before adding
    await page.get_by_label("Size").select_option("M")
    await page.get_by_label("Color").click()
    await page.get_by_text("Navy Blue").click()

    await page.get_by_role("button", name="Add to Cart").click()
    await expect(page.get_by_text("Navy Blue — Size M added to cart")).to_be_visible()
```

### Cart Operations

```python
@pytest.mark.asyncio
async def test_cart_quantity_update(page: Page):
    """Prequisite: item already in cart."""
    await page.goto("/cart")
    await page.get_by_test_id("cart-item").first.wait_for(state="visible")

    # Get initial total
    initial_total = await page.get_by_test_id("cart-total").text_content()

    # Increase quantity
    await page.get_by_test_id("quantity-increase").first.click()
    await page.wait_for_timeout(500)  # Wait for total to update

    # Total should change
    updated_total = await page.get_by_test_id("cart-total").text_content()
    assert updated_total != initial_total

@pytest.mark.asyncio
async def test_remove_from_cart(page: Page):
    await page.goto("/cart")
    initial_count = await page.get_by_test_id("cart-item").count()
    assert initial_count > 0

    # Remove first item
    await page.get_by_test_id("remove-item").first.click()

    # Confirm count decreased
    await expect(page.get_by_test_id("cart-item")).to_have_count(
        initial_count - 1, timeout=3000
    )

@pytest.mark.asyncio
async def test_empty_cart(page: Page):
    await page.goto("/cart")
    await expect(page.get_by_text("Your cart is empty")).to_be_visible()
    await expect(page.get_by_role("button", name="Checkout")).to_be_disabled()
```

## Responsive Testing

```python
VIEWPORTS = {
    "mobile_sm": {"width": 320, "height": 568},
    "mobile_lg": {"width": 414, "height": 896},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1280, "height": 720},
    "wide": {"width": 1920, "height": 1080},
}

@pytest.mark.parametrize("name,size", [
    (name, size) for name, size in VIEWPORTS.items()
])
@pytest.mark.asyncio
async def test_nav_responsive(browser, name, size):
    context = await browser.new_context(viewport=size)
    page = await context.new_page()
    await page.goto("/")

    if size["width"] < 768:
        # Mobile: hamburger menu should be visible, regular nav hidden
        await expect(page.get_by_test_id("hamburger-menu")).to_be_visible()
        await expect(page.locator("nav.desktop-nav")).to_be_hidden()
    else:
        # Desktop: full nav visible, hamburger hidden
        await expect(page.locator("nav.desktop-nav")).to_be_visible()
        await expect(page.get_by_test_id("hamburger-menu")).to_be_hidden()

    await context.close()

@pytest.mark.asyncio
async def test_no_horizontal_scroll(browser):
    """No viewport should trigger horizontal overflow."""
    for name, size in VIEWPORTS.items():
        context = await browser.new_context(viewport=size)
        page = await context.new_page()
        await page.goto("/")

        scroll_width = await page.evaluate(
            "() => document.documentElement.scrollWidth"
        )
        viewport_width = await page.evaluate(
            "() => window.innerWidth"
        )
        assert scroll_width <= viewport_width, \
            f"Horizontal scroll detected at {name} ({size['width']}px): " \
            f"scrollWidth={scroll_width}, innerWidth={viewport_width}"

        await context.close()
```

## Error State Testing

### Network Errors

```python
@pytest.mark.asyncio
async def test_offline_state(page: Page):
    await page.goto("/")

    # Simulate going offline
    await page.context.set_offline(True)

    # Try to navigate
    try:
        await page.get_by_role("link", name="Products").click()
    except Exception:
        pass  # May throw — that's expected

    # App should show offline indicator
    await expect(page.get_by_text(
        re.compile(r"offline|no connection|no internet", re.IGNORECASE)
    )).to_be_visible(timeout=5000)

    # Restore connectivity
    await page.context.set_offline(False)
```

### Server Errors (5xx)

```python
@pytest.mark.asyncio
async def test_server_error_handling(page: Page):
    # Mock API to return 500
    await page.route("**/api/products**", lambda route: route.fulfill(
        status=500,
        content_type="application/json",
        body='{"error": "Internal Server Error"}'
    ))

    await page.goto("/products")

    # App should show a user-friendly error
    await expect(page.get_by_text(
        re.compile(r"something went wrong|error loading|try again", re.IGNORECASE)
    )).to_be_visible()

    # Retry button should be available
    await expect(page.get_by_role("button", name="Retry")).to_be_visible()
```

### Slow Network Simulation

```python
@pytest.mark.asyncio
async def test_loading_states(page: Page):
    # Simulate slow 3G
    await page.route("**/*", lambda route: route.continue_() if route.request.resource_type != "fetch"
                     else route.fulfill(status=200, body="{}"))
    # Better: use built-in throttling in Playwright
    # Not directly available in Python API, but chromium args can simulate

    await page.goto("/products")

    # Loading skeletons/spinners should appear
    await expect(page.get_by_test_id("loading-skeleton")).to_be_visible()
    # Eventually content loads
    await expect(page.get_by_test_id("product-list")).to_be_visible(timeout=30000)
```

## Accessibility Testing

```python
@pytest.mark.asyncio
async def test_keyboard_navigation(page: Page):
    """Verify tab navigation works through the login form."""
    await page.goto("/login")

    # Tab through the form (focus order: email → password → submit → forgot password)
    await page.keyboard.press("Tab")
    await expect(page.get_by_label("Email")).to_be_focused()

    await page.keyboard.press("Tab")
    await expect(page.get_by_label("Password")).to_be_focused()

    await page.keyboard.press("Tab")
    await expect(page.get_by_role("button", name="Sign In")).to_be_focused()

    await page.keyboard.press("Tab")
    await expect(page.get_by_role("link", name="Forgot Password")).to_be_focused()

@pytest.mark.asyncio
async def test_aria_attributes(page: Page):
    """Verify critical ARIA landmarks are present."""
    await page.goto("/")

    # Page should have main navigation and content regions
    await expect(page.locator("[role='navigation']")).to_be_attached()
    await expect(page.locator("[role='main'], main")).to_be_attached()

    # Error messages should have alert role
    await page.goto("/login")
    await page.get_by_role("button", name="Sign In").click()  # Empty submit
    await expect(page.locator("[role='alert']")).to_be_attached()
```

## File Upload Testing

```python
@pytest.mark.asyncio
async def test_file_upload(page: Page):
    await page.goto("/upload")

    # Single file
    await page.set_input_files("input[type='file']", "tests/fixtures/document.pdf")
    await expect(page.get_by_text("document.pdf")).to_be_visible()

    # Multiple files
    await page.set_input_files("input[type='file']", [
        "tests/fixtures/doc1.pdf",
        "tests/fixtures/doc2.pdf",
    ])

    await page.get_by_role("button", name="Upload").click()
    await expect(page.get_by_text("2 files uploaded")).to_be_visible()

@pytest.mark.asyncio
async def test_file_upload_validation(page: Page):
    await page.goto("/upload")

    # Try to upload disallowed file type
    await page.set_input_files("input[type='file']", "tests/fixtures/image.exe")
    await expect(page.get_by_text("File type not allowed")).to_be_visible()

    # Try to upload oversized file (mock the file)
    # This depends on how the app validates — client-side vs server-side
```

## Performance Assertions

```python
@pytest.mark.asyncio
async def test_page_load_performance(page: Page):
    """Assert page loads within performance budget."""
    start = page.evaluate("() => performance.timing.navigationStart")
    await page.goto("/", wait_until="load")

    load_time = await page.evaluate(
        "() => performance.timing.loadEventEnd - performance.timing.navigationStart"
    )

    # Page should load within 3 seconds
    assert load_time < 3000, f"Page load took {load_time}ms (budget: 3000ms)"

    # Critical content should be visible quickly
    dom_content_loaded = await page.evaluate(
        "() => performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart"
    )
    assert dom_content_loaded < 1500, f"DOMContentLoaded took {dom_content_loaded}ms"

@pytest.mark.asyncio
async def test_no_console_errors(page: Page):
    """Test that the page doesn't log console errors."""
    errors: list[str] = []
    page.on("pageerror", lambda err: errors.append(str(err)))

    await page.goto("/")
    await page.wait_for_load_state("networkidle")

    assert len(errors) == 0, f"Console errors found: {errors}"

@pytest.mark.asyncio
async def test_no_failed_requests(page: Page):
    """Test that no requests fail with 4xx/5xx."""
    failed: list[str] = []

    def check_response(response):
        if response.status >= 400 and response.url.startswith("https://example.com"):
            failed.append(f"{response.status} {response.url}")

    page.on("response", check_response)
    await page.goto("/")
    await page.wait_for_load_state("networkidle")

    assert len(failed) == 0, f"Failed requests: {failed}"
```