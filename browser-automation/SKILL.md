---
name: browser-automation
description: >
  Browser automation with Playwright — testing, scraping, monitoring,
  form submission, screenshot capture, and multi-page interaction flows.
  Covers setup, navigation, element interaction, assertions, and cleanup.
  Primary keyword clusters: Playwright browser automation, end-to-end testing
  with Playwright, web scraping Python Playwright, headless browser testing,
  automated form submission Playwright, synthetic monitoring browser, screenshot
  capture automation, CI/CD browser testing, page object model Playwright.
  Designed for agentic platforms — Claude Code, Codex, Cursor, Gemini CLI,
  OpenClaw, GitHub Copilot, Windsurf, and OpenCode.
version: 1.1.0
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
  - browser
  - playwright
  - testing
  - scraping
  - automation
  - e2e
  - screenshot
  - form-automation
  - monitoring
  - ci-cd
geo:
  primary_workflows:
    - e2e_testing
    - web_scraping
    - form_automation
    - screenshot_capture
    - synthetic_monitoring
    - multi_page_flows
  target_roles:
    - qa_engineer
    - devops_engineer
    - full_stack_developer
    - data_engineer
  complexity_level: intermediate
  prerequisite_knowledge:
    - python_basics
    - async_await_patterns
    - html_css_selectors
---

# Browser Automation — Agent Skill

Production-grade browser automation using [Playwright](https://playwright.dev). Covers end-to-end testing, web scraping, synthetic monitoring, form automation, and screenshot capture — with safe defaults, robust selectors, and CI/CD portability.

---

## Quick Reference

| Task | Pattern | Selection Priority |
|---|---|---|
| Launch browser (sync) | `sync_playwright() → p.chromium.launch(headless=True)` | Default for one-off scripts |
| Launch browser (async) | `async_playwright() → await p.chromium.launch()` | Required for pytest suites |
| Find element (best) | `page.get_by_test_id("foo")` | 🥇 data-testid |
| Find element (good) | `page.get_by_role("button", name="Submit")` | 🥈 role-based |
| Find element (ok) | `page.get_by_text("Sign In")` | 🥉 user-visible text |
| Find element (last) | `page.locator("form#login input")` | ⚠️ CSS/XPath fallback |
| Fill a form field | `page.get_by_label("Email").fill("user@example.com")` | Prefer labels |
| Click & wait for result | `await expect(page.get_by_text("Success")).to_be_visible()` | Auto-retries 5s |
| Wait without sleeping | `page.wait_for_selector("[data-testid='result']", state="visible")` | Never `time.sleep()` |
| Screenshot | `page.screenshot(full_page=True)` | Redact PII before saving |
| Navigate SPA pages | `page.goto(url, wait_until="networkidle")` | React/Vue/Angular |
| CI/Docker | Add `args=["--no-sandbox"]` to `launch()` | Required on Linux containers |
| Handle errors | Use context managers (`async with` blocks) | Auto-cleanup on exceptions |
| Wait for API response | `async with page.expect_response(...)` | No brittle sleeps |
| Respectful scraping | `RespectfulScraper` with 1-3s delay | Check robots.txt first |

---

## When to Use This Skill

Trigger this skill when the user asks for:

- **Browser testing** — "write an e2e test for the login flow", "test this form", "check if the dashboard loads", "automate browser regression tests"
- **Web scraping** — "extract all product prices from this page", "scrape the table data", "get the article text", "crawl product listings from this site"
- **Form automation** — "fill out this multi-step form", "submit the registration", "bulk-upload via the web UI", "automate this checkout flow"
- **Screenshot capture** — "take a screenshot of the page", "capture the error state", "full-page screenshot of this blog", "screenshot every page of this site"
- **Synthetic monitoring** — "check if the site is up and the login works", "monitor this checkout flow every 5 minutes", "set up health-check for the dashboard"
- **Multi-page flows** — "go through the onboarding wizard", "walk through the purchase funnel", "verify the password-reset flow", "test the entire signup-to-purchase journey"

Do NOT trigger for:

- Asking about browser features without automation intent ("what browsers support WebGPU?")
- General Playwright API questions without a concrete task ("how does page.waitForSelector work?")
- Discussing browser compatibility in the abstract
- Requests to manually test something in a browser
- UI/UX design feedback without automation
- Asking "what's different between Chrome and Firefox rendering?" — factual, no automation

---

## Common Pitfalls & Anti-Patterns

### ❌ NEVER do these

1. **`time.sleep(N)` — brittle, slow, and flaky**
   - Instead: `page.wait_for_selector()`, `page.wait_for_load_state()`, `expect().to_be_visible()`

2. **Hardcoding credentials in scripts**
   - Instead: `os.environ["TEST_PASSWORD"]`, `.env` files, or CI secrets

3. **Committing screenshots with PII to version control**
   - Instead: Redact sensitive fields, use `clip` parameter, or skip screenshots in CI

4. **Scraping without rate limits — you'll get IP-banned**
   - Instead: Use `RespectfulScraper` pattern, 1+ second delays, respect `robots.txt`

5. **Using brittle CSS selectors like `.col-md-4 > div:nth-child(3) > a`**
   - Instead: Prioritize `data-testid`, `get_by_role`, `get_by_label`, `get_by_text`

6. **Mixing sync and async Playwright APIs in the same script**
   - Pick one API and stay consistent. `sync_playwright()` for scripts, `async_playwright()` for test suites.

7. **Forgetting `--no-sandbox` in Docker/CI**
   - Add `args=["--no-sandbox"]` to every `launch()` call. Without it, Chromium refuses to start.

8. **Using `page.content()` for data extraction instead of `.evaluate_all()` or `.text_content()`**
   - `page.content()` returns raw HTML that you then have to parse. Use Playwright's built-in extraction.

9. **Not handling cookie banners or modals before interacting with page content**
   - Always dismiss cookie consents, accept dialogs, or close overlays before interacting.

10. **Leaving browser processes open on script error**
    - Always use context managers (`async with` / `with` blocks) — they clean up even on exceptions.

### ✅ Debugging Checklist (when things go wrong)

- [ ] Did you wait for the element to be visible before interacting?
- [ ] Is the selector valid? Test with `playwright codegen` to verify.
- [ ] Are you using the right `wait_until` strategy for your page type (SPA vs MPA)?
- [ ] If in CI/Docker, did you add `--no-sandbox`?
- [ ] Is there a cookie consent modal blocking interaction?
- [ ] Are you behind a proxy/VPN that interferes with browser network?
- [ ] Did the page trigger a download dialog? Handle with `page.on("download")`.
- [ ] Is the browser closed too early? Check `finally` block or context manager exit order.

---

## Workflow

Follow this ordered pipeline for every browser automation task:

### 1. Setup

```python
# Synchronous (preferred for simple scripts)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (compatible; AutomationBot/1.0)"
    )
    page = context.new_page()

# Async (required for pytest-playwright, larger suites)
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

asyncio.run(main())
```

**Decision points:**

- **Headless vs headed:** Use `headless=True` by default. Use `headless=False` when the user needs to observe the action or debug a visual issue.
- **Sync vs async:** Use sync for one-off scripts and quick tasks. Use async when writing pytest fixtures, concurrent scrapers, or large test suites.
- **Chromium vs Firefox vs WebKit:** Default to Chromium for broadest compatibility. Use Firefox/WebKit only when explicitly requested for cross-browser testing.

**CI tip:** If the user mentions CI/CD, add `args=["--no-sandbox"]` to `launch()` for Docker/Linux environments.

### 2. Navigation

```python
# Basic navigation with timeout
try:
    page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
except playwright._impl._api_types.TimeoutError:
    print("Navigation timed out — site may be down or slow")
    raise

# Wait for network idle (SPA-heavy pages)
page.goto("https://spa-app.example.com", wait_until="networkidle")

# Useful post-navigation waits
page.wait_for_load_state("domcontentloaded")   # HTML parsed
page.wait_for_load_state("load")                # all resources loaded
page.wait_for_load_state("networkidle")         # no network for 500ms
```

**Navigation strategies by page type:**

| Page type | `wait_until` | Additional wait |
|---|---|---|
| Server-rendered (MPA) | `domcontentloaded` | None usually |
| SPA / React / Vue | `networkidle` | `wait_for_selector` on key element |
| Streaming / WebSocket | `domcontentloaded` | Wait for specific content or state |
| Slow third-party embeds | `load` | Ignore third-party timeouts |

### 3. Interaction

**Selectors — in order of preference:**

```python
# 1. data-testid (most stable)
page.click("[data-testid='submit-button']")

# 2. Role-based (accessible)
page.get_by_role("button", name="Submit").click()

# 3. Text content (user-visible stable)
page.get_by_text("Sign In").click()

# 4. Label (forms)
page.get_by_label("Email address").fill("user@example.com")

# 5. Placeholder
page.get_by_placeholder("Search...").fill("query")

# 6. CSS/XPath (last resort)
page.locator("form#login input[name='email']").fill("user@example.com")
```

**Common interaction patterns:**

```python
# Form filling
await page.get_by_label("Email").fill("user@example.com")
await page.get_by_label("Password").fill("s3cret")
await page.get_by_role("button", name="Log In").click()

# Dropdown / select
await page.select_option("select#country", value="DE")

# Checkbox / radio
await page.get_by_label("I agree to terms").check()

# File upload
await page.set_input_files("input[type='file']", "/path/to/file.pdf")

# Hover and nested interactions
await page.get_by_text("Products").hover()
await page.get_by_text("New Arrivals").click()

# Keyboard shortcuts
await page.keyboard.press("Enter")
await page.keyboard.press("Control+A")
```

**Wait strategies:**

```python
# Never use time.sleep(). Use these instead:
await page.wait_for_selector("[data-testid='result']", state="visible", timeout=10000)
await page.wait_for_function("() => document.querySelector('.spinner') === null")
await page.wait_for_url("**/dashboard**")
await page.wait_for_load_state("networkidle")

# For dynamic content that appears/disappears
await expect(page.get_by_text("Loading...")).to_be_hidden(timeout=15000)
await expect(page.get_by_text("Results")).to_be_visible(timeout=15000)

# For network-triggered updates
async with page.expect_response(lambda r: "/api/results" in r.url):
    await page.click("[data-testid='search-button']")
```

### 4. Assertion

```python
from playwright.async_api import expect

# Page-level
await expect(page).to_have_title("Dashboard — My App")
await expect(page).to_have_url("https://app.example.com/dashboard")

# Element visibility
await expect(page.get_by_text("Welcome back")).to_be_visible()
await expect(page.locator(".error-banner")).to_be_hidden()

# Content
await expect(page.get_by_test_id("user-name")).to_have_text("John Doe")
await expect(page.get_by_test_id("item-count")).to_contain_text("5")

# Form state
await expect(page.get_by_label("Email")).to_have_value("user@example.com")
await expect(page.get_by_label("Agree")).to_be_checked()

# Screenshot-based verification
screenshot = await page.screenshot(full_page=True)
# For visual regression, combine with pixelmatch or Percy

# Custom assertions for scraping
items = await page.locator(".product-card").count()
assert items >= 10, f"Expected at least 10 products, found {items}"
```

**Assertion retry behavior:** Playwright `expect` auto-retries for up to 5 seconds (configurable). This is usually what you want — it handles async rendering without brittle sleeps.

### 5. Cleanup

```python
# With context managers (recommended)
async with async_playwright() as p:
    async with await p.chromium.launch() as browser:
        async with await browser.new_page() as page:
            await page.goto("https://example.com")
            # ... work ...
# Everything auto-closes at block exit

# Manual cleanup (when not using context managers)
await page.close()
await context.close()
await browser.close()
await p.stop()  # playwright instance
```

**Always clean up.** Orphaned browser processes leak memory and ports. Context managers are the safest default — they handle cleanup even on exceptions.

## Error Handling

```python
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

async def robust_navigation(url: str, retries: int = 2):
    """Navigate with retry logic for flaky networks."""
    for attempt in range(retries + 1):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            return
        except PlaywrightTimeout:
            if attempt == retries:
                raise
            print(f"Navigation attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(2 ** attempt)  # exponential backoff

# Stale element recovery
try:
    await page.click("[data-testid='dynamic-button']")
except PlaywrightTimeout:
    # Element may have been removed and re-rendered
    await page.wait_for_selector("[data-testid='dynamic-button']", state="attached")
    await page.click("[data-testid='dynamic-button']")

# Network failure handling
try:
    await page.goto("https://flaky-service.example.com")
except Exception as e:
    if "net::ERR_" in str(e):
        raise RuntimeError(f"Network error accessing page: {e}")
    raise

# Modal/dialog handling (accept before interaction)
page.on("dialog", lambda dialog: dialog.accept())
```

### Common Error Patterns

| Error | Likely cause | Fix |
|---|---|---|
| `TimeoutError` on `goto` | Slow page, network issue | Increase timeout, add retry, check URL |
| `TimeoutError` on selector | Element not rendered yet | Wait for visibility, check selector |
| `Error: strict mode violation` | Selector matches multiple elements | Use `.first`, `.nth()`, or refine selector |
| `Error: Target closed` | Page/browser was closed early | Check cleanup order, use context managers |
| `Error: Element is not visible` | Element exists in DOM but hidden | Wait for `state="visible"` |
| `net::ERR_CONNECTION_REFUSED` | Site is down | Retry, raise clear error, log for monitoring |

## Safety Rules

### Rate Limiting & Respectful Scraping

```python
import time
from typing import List

class RespectfulScraper:
    """Scraper with built-in politeness delays."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request = 0.0
        self._jitter = __import__("random").uniform

    async def wait(self):
        """Enforce minimum delay between requests."""
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed + self._jitter(0, self.max_delay - self.min_delay))
        self._last_request = time.monotonic()

    async def get(self, page, url: str) -> None:
        await self.wait()
        await page.goto(url)
```

**Golden rules:**

1. **Delay between requests** — at least 1 second between page loads, longer for small sites
2. **Respect `robots.txt`** — check if scraping is allowed
3. **Set a user agent that identifies your automation** — don't impersonate real browsers
4. **Limit concurrent connections** — no more than 2-3 parallel pages to the same domain
5. **Stop on error patterns** — if you get 429s, 403s, or captchas, back off
6. **Don't scrape auth-walled content** without explicit permission

### Credential Safety

```python
# ✅ DO: Read from environment variables
EMAIL = os.environ["TEST_EMAIL"]
PASSWORD = os.environ["TEST_PASSWORD"]

# ✅ DO: Read from a .env file (gitignored)
from dotenv import load_dotenv
load_dotenv()

# ❌ DON'T: Hardcode credentials
# EMAIL = "admin@company.com"  # NEVER DO THIS

# ❌ DON'T: Log credentials
# print(f"Logging in as {EMAIL} with password {PASSWORD}")  # NEVER
```

### Screenshot Safety

- Redact sensitive fields before capture when possible
- Never commit screenshots with PII to version control
- Use viewport clipping for targeted captures: `page.screenshot(clip={"x": 0, "y": 0, "width": 800, "height": 600})`

## Quick-Start Templates

### Template: E2E Login Test

```python
import os
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.environ.get("BASE_URL", "https://app.example.com")
EMAIL = os.environ["TEST_EMAIL"]
PASSWORD = os.environ["TEST_PASSWORD"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")

    # Fill & submit
    page.get_by_label("Email").fill(EMAIL)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign In").click()

    # Assert redirect
    expect(page).to_have_url(f"{BASE_URL}/dashboard", timeout=10000)
    expect(page.get_by_text("Welcome")).to_be_visible()

    browser.close()
    print("✅ Login test passed")
```

### Template: Web Scraper

```python
import json
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://books.toscrape.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    books = page.locator(".product_pod").evaluate_all("""
        els => els.map(el => ({
            title: el.querySelector('h3 a')?.getAttribute('title') || '',
            price: el.querySelector('.price_color')?.textContent || '',
            availability: el.querySelector('.availability')?.textContent?.trim() || ''
        }))
    """)

    print(json.dumps(books, indent=2))
    browser.close()
```

### Template: Multi-Page Monitoring Flow

```python
import os
import sys
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = os.environ.get("MONITOR_URL", "https://example.com")

def check_flow() -> bool:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Step 1: Homepage loads
            page.goto(URL, wait_until="domcontentloaded", timeout=15000)
            assert page.title(), "Page has no title"

            # Step 2: Search works
            page.get_by_placeholder("Search").fill("test")
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")

            # Step 3: Results appear
            assert page.locator(".search-results").is_visible(), "No results container"
            print(f"[{datetime.now(timezone.utc).isoformat()}] ✅ Flow healthy")
            return True

        except Exception as e:
            print(f"[{datetime.now(timezone.utc).isoformat()}] ❌ Flow failed: {e}")
            # Save diagnostic screenshot
            page.screenshot(path=f"error-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = check_flow()
    sys.exit(0 if success else 1)
```

## Advanced Patterns

### Page Object Model

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.submit_button = page.get_by_role("button", name="Sign In")
        self.error_message = page.locator(".alert-error")

    async def goto(self):
        await self.page.goto("/login", wait_until="networkidle")

    async def login(self, email: str, password: str):
        await self.email_input.fill(email)
        await self.password_input.fill(password)
        await self.submit_button.click()

    async def get_error(self) -> str:
        await self.error_message.wait_for(state="visible")
        return await self.error_message.text_content()
```

### Network Interception

```python
# Mock API responses for stable tests
await page.route("**/api/users/**", lambda route: route.fulfill(
    status=200,
    content_type="application/json",
    body='{"id": 1, "name": "Test User"}'
))

# Capture network requests for debugging
requests = []
page.on("request", lambda req: requests.append(f"{req.method} {req.url}"))
page.on("response", lambda res: print(f"{res.status} {res.url}"))

# Wait for specific API call to complete
async with page.expect_response(lambda r: "/api/submit" in r.url) as response_info:
    await page.click("[data-testid='submit']")
response = await response_info.value
assert response.status == 200
```

### Visual Regression (Screenshot Diffing)

```python
# Capture and compare screenshots
await page.screenshot(path="baseline.png", full_page=True)
# Use with pixelmatch, Percy, or Chromatic for automated diffing

# Element-level screenshot
await page.locator(".pricing-table").screenshot(path="pricing.png")

# Clip to a specific region (avoid dynamic content)
await page.screenshot(
    path="header.png",
    clip={"x": 0, "y": 0, "width": 1280, "height": 200}
)
```

## Platform Compatibility Notes

### Claude Code (VS Code / CLI)
- Sync API preferred for quick scripts
- Use `subprocess.run(["python", "script.py"])` to execute
- Install: `pip install playwright && playwright install chromium`

### Codex
- Async API for concurrent task handling
- Each session gets its own browser context for isolation
- Use the `save_screenshot` pattern for visual feedback

### Cursor
- Native Python execution, both sync and async work
- `.cursor/rules` can store common Playwright patterns
- Leverage the built-in terminal for `playwright codegen`

### Gemini CLI
- Well-suited for one-shot scraping and monitoring tasks
- Package scripts as standalone Python files
- Use `gemini run script.py` for execution

### OpenClaw
- Install via `pip install playwright` in the OpenClaw environment
- Run scripts through exec tool with PTY for headed mode debugging
- Screenshots are auto-attached in chat output

### GitHub Copilot
- Works natively in VS Code with Python extension
- Chat can generate complete Playwright scripts
- Use `// @ts-check` comments for inline documentation

### Windsurf
- Native Python execution in the IDE terminal
- Use sync API for quick tasks; async for larger test suites
- Store reusable POM classes in project workspace

### OpenCode
- Execute scripts as standalone Python files
- Prefer async API with context managers for safety
- Install Playwright via `pip install playwright && playwright install`

---

## References

- **Playwright docs:** https://playwright.dev/python/docs/intro
- **Selectors guide:** https://playwright.dev/python/docs/selectors
- **API reference:** https://playwright.dev/python/docs/api/class-playwright
- **Best practices:** https://playwright.dev/python/docs/best-practices
- **CI configuration:** https://playwright.dev/python/docs/ci

See also the companion reference files in this skill:

- [`references/playwright-patterns.md`](references/playwright-patterns.md) — POM, fixtures, CI setup
- [`references/selector-strategies.md`](references/selector-strategies.md) — Robust selector hierarchy
- [`references/browser-testing-workflows.md`](references/browser-testing-workflows.md) — Testing patterns
