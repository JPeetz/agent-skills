# Playwright Patterns — Reference

Production-grade patterns for Playwright automation. Covers Page Object Model, fixtures, CI/CD setup, concurrency, and advanced flows.

## Page Object Model (POM)

Encapsulate page structure and actions into reusable classes. Keeps tests readable and maintainable.

### Basic POM

```python
# pages/login_page.py
from playwright.async_api import Page, expect

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.submit_button = page.get_by_role("button", name="Sign In")
        self.error_banner = page.locator("[data-testid='login-error']")

    async def goto(self, base_url: str = ""):
        await self.page.goto(f"{base_url}/login", wait_until="networkidle")
        return self

    async def login(self, email: str, password: str) -> "DashboardPage":
        await self.email_input.fill(email)
        await self.password_input.fill(password)
        await self.submit_button.click()
        # Return the next page object for fluent chaining
        return DashboardPage(self.page)

    async def assert_error_visible(self, expected_text: str):
        await expect(self.error_banner).to_be_visible()
        await expect(self.error_banner).to_contain_text(expected_text)


# pages/dashboard_page.py
class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.welcome_message = page.get_by_test_id("welcome-message")
        self.user_menu = page.get_by_test_id("user-menu")

    async def assert_loaded(self):
        await expect(self.page).to_have_url("**/dashboard**")
        await expect(self.welcome_message).to_be_visible()
        return self

    async def get_user_name(self) -> str:
        return await self.welcome_message.text_content()
```

### Fluent POM Usage

```python
async def test_login_flow(page: Page):
    dashboard = await (
        LoginPage(page)
        .goto("https://app.example.com")
        .login("user@example.com", "password123")
        .assert_loaded()
    )
    assert "John" in await dashboard.get_user_name()
```

## Fixture Patterns (pytest)

### conftest.py — Shared Fixtures

```python
# tests/conftest.py
import pytest
from playwright.async_api import async_playwright, Browser, Page
from typing import AsyncGenerator

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async fixtures."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Session-scoped browser — reused across all tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]  # required for CI/Docker
        )
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser: Browser) -> AsyncGenerator[Page, None]:
    """Function-scoped page — fresh context per test for isolation."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True  # for staging environments
    )
    page = await context.new_page()
    yield page
    await context.close()

@pytest.fixture
async def authenticated_page(browser: Browser) -> AsyncGenerator[Page, None]:
    """Pre-authenticated page — saves login time across tests."""
    context = await browser.new_context()
    page = await context.new_page()
    # Seed authentication (cookies, localStorage, or API token)
    await context.add_cookies([
        {"name": "session", "value": "test-session-token", "url": "https://app.example.com"}
    ])
    yield page
    await context.close()
```

### Test Using Fixtures

```python
# tests/test_login.py
import pytest
from playwright.async_api import Page

@pytest.mark.asyncio
async def test_successful_login(page: Page):
    await page.goto("https://app.example.com/login")
    await page.get_by_label("Email").fill("user@example.com")
    await page.get_by_label("Password").fill("password123")
    await page.get_by_role("button", name="Sign In").click()
    await page.wait_for_url("**/dashboard**")
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install playwright pytest pytest-asyncio
          playwright install --with-deps chromium

      - name: Run E2E tests
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
        run: pytest tests/ --browser chromium --tracing=retain-on-failure

      - name: Upload traces on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces
          path: test-results/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
e2e-tests:
  image: mcr.microsoft.com/playwright/python:v1.45.0-noble
  script:
    - pip install pytest pytest-asyncio
    - pytest tests/ --browser chromium --tracing=retain-on-failure
  artifacts:
    when: on_failure
    paths:
      - test-results/
    expire_in: 7 days
```

### Docker Setup

```dockerfile
# Dockerfile.e2e
FROM mcr.microsoft.com/playwright/python:v1.45.0-noble

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["pytest", "tests/", "--browser", "chromium", "--tracing=retain-on-failure"]
```

## Concurrency Patterns

### Parallel Scraping with Semaphore

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_page(browser, semaphore, url):
    async with semaphore:
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            data = await page.locator(".product").evaluate_all(
                """els => els.map(e => ({
                    title: e.querySelector('h3')?.textContent,
                    price: e.querySelector('.price')?.textContent
                }))"""
            )
            return data
        finally:
            await context.close()

async def scrape_all(urls: list[str], max_concurrent: int = 3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = [scrape_page(browser, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()
        return results
```

### pytest-xdist for Parallel Tests

```bash
# Run tests across 4 workers (1 browser per worker)
pytest tests/ -n 4 --dist loadscope

# conftest.py: use scope="session" for browser, scope="function" for page
```

## Network Patterns

### Request/Response Interception

```python
# Mock an API endpoint — no backend needed
await page.route("**/api/profile", lambda route: route.fulfill(
    status=200,
    content_type="application/json",
    body='{"name": "Test", "email": "test@example.com"}'
))

# Abort noisy third-party requests (analytics, ads, etc.)
await page.route("**/*", lambda route: (
    route.abort() if any(d in route.request.url for d in [
        "google-analytics.com", "doubleclick.net", "facebook.com/tr"
    ]) else route.continue_()
))

# Collect all API requests for debugging
api_calls = []
page.on("request", lambda req: (
    api_calls.append({"method": req.method, "url": req.url})
    if "/api/" in req.url else None
))
```

### Wait for Specific API Response

```python
async with page.expect_response(
    lambda resp: "/api/search" in resp.url and resp.status == 200,
    timeout=10000
) as response_event:
    await page.get_by_test_id("search-button").click()

response = await response_event.value
data = await response.json()
assert len(data["results"]) > 0
```

## Authentication Patterns

### Cookie-Based Auth (Fastest)

```python
context = await browser.new_context()
await context.add_cookies([
    {
        "name": "auth_token",
        "value": "eyJhbGciOi...",
        "domain": ".example.com",
        "path": "/",
        "httpOnly": True,
        "secure": True,
        "sameSite": "Lax"
    }
])
page = await context.new_page()
await page.goto("https://app.example.com/dashboard")
```

### localStorage-Based Auth

```python
context = await browser.new_context()
page = await context.new_page()
await page.goto("https://app.example.com")

# Inject auth state before the app loads
await page.evaluate("""
    () => {
        localStorage.setItem('token', arguments[0]);
        localStorage.setItem('user', JSON.stringify(arguments[1]));
    }
""", "jwt-token-here", {"id": 1, "name": "Test User"})

await page.goto("https://app.example.com/dashboard")
```

### Programmatic Login (Realistic)

```python
async def authenticate_and_save_state(browser, email: str, password: str, state_path: str):
    """Log in once, save state, reuse across tests."""
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://app.example.com/login")
    await page.get_by_label("Email").fill(email)
    await page.get_by_label("Password").fill(password)
    await page.get_by_role("button", name="Sign In").click()
    await page.wait_for_url("**/dashboard**")

    # Save auth state for reuse
    await context.storage_state(path=state_path)
    await context.close()

    # Reuse saved state
    context = await browser.new_context(storage_state=state_path)
    page = await context.new_page()
    await page.goto("https://app.example.com/dashboard")
```

## Mobile & Responsive Patterns

```python
# Mobile device emulation
iphone = p.devices["iPhone 15 Pro"]
context = await browser.new_context(**iphone)
page = await context.new_page()

# Custom viewport for responsive testing
VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1280, "height": 720},
    "wide": {"width": 1920, "height": 1080},
}

@pytest.mark.parametrize("viewport_name,viewport", VIEWPORTS.items())
async def test_responsive_layout(browser, viewport_name, viewport):
    context = await browser.new_context(**viewport)
    page = await context.new_page()
    await page.goto("https://example.com")
    # Assert no horizontal overflow, hamburger menu on mobile, etc.
    await context.close()
```

## Tracing & Debugging

```python
# Enable trace for a specific test
context = await browser.new_context()
await context.tracing.start(screenshots=True, snapshots=True)
page = await context.new_page()

try:
    await page.goto("https://example.com")
    # ... test actions ...
finally:
    await context.tracing.stop(path="trace.zip")

# View trace: playwright show-trace trace.zip
```

### Debug with Playwright Inspector

```python
# Launch with inspector (interactive debugging)
browser = await p.chromium.launch(headless=False)
page = await browser.new_page()

# Set breakpoint equivalent
await page.pause()  # Opens Playwright Inspector
```

## Anti-Detection Patterns

```python
# Avoid being blocked by bot detection
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
    timezone_id="America/New_York",
    permissions=["geolocation"],
    geolocation={"latitude": 40.7128, "longitude": -74.0060},
    color_scheme="light",
)

# Stealthier navigation (evade simple WebDriver checks)
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
""")
```

> **Warning:** These anti-detection techniques are for legitimate automation on sites you own or have permission to access. Do not use to bypass bot protection on sites where scraping is prohibited.