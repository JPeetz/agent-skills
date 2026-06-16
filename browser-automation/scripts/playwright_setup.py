# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.45.0",
# ]
# ///

"""
Playwright Setup & Validation — Browser Automation Skill

Validates that Playwright is installed, checks which browsers are available,
and runs a quick smoke test against a known-good page.

Usage:
    python playwright_setup.py                # full validation
    python playwright_setup.py --smoke-only   # only the smoke test
    python playwright_setup.py --install      # install missing browsers

Exit codes:
    0 — all checks passed
    1 — Playwright package not installed
    2 — no browsers found
    3 — smoke test failed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# ── Terminal output helpers ──────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def ok(msg: str) -> None:
    print(f"  {GREEN}✔{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}✘{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}⚠{RESET} {msg}")


def info(msg: str) -> None:
    print(f"  {CYAN}→{RESET} {msg}")


def header(msg: str) -> None:
    print(f"\n{BOLD}{msg}{RESET}")
    print("-" * len(msg))


# ── Checks ───────────────────────────────────────────────────────────

def check_playwright_package() -> bool:
    """Verify the playwright Python package is importable."""
    header("1. Playwright Python package")
    try:
        import playwright
        ok(f"playwright {playwright.__version__ or '(version unavailable)'}")
        return True
    except ImportError:
        fail("playwright is not installed")
        info("Install with: pip install playwright")
        return False


def check_browsers() -> bool:
    """Check which Playwright browsers are installed."""
    header("2. Browser availability")
    from playwright.sync_api import sync_playwright

    browsers_found: list[str] = []

    with sync_playwright() as p:
        for name in ["chromium", "firefox", "webkit"]:
            try:
                browser_type = getattr(p, name)
                browser = browser_type.launch(headless=True)
                version = browser.version
                browser.close()
                browsers_found.append(f"{name} ({version})")
                ok(f"{name} ready — {version}")
            except Exception as e:
                warn(f"{name} not available: {e}")

    if not browsers_found:
        fail("No Playwright browsers found")
        info("Install browsers with: playwright install")
        return False

    ok(f"{len(browsers_found)} browser(s) available")
    return True


def smoke_test(url: str = "https://httpbin.org/get") -> bool:
    """Run a quick smoke test — navigate, check title, take a screenshot."""
    header("3. Smoke test")
    from playwright.sync_api import sync_playwright

    tmp_dir = Path("/tmp/playwright-smoke")
    tmp_dir.mkdir(exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            info(f"Navigating to {url} …")
            response = page.goto(url, wait_until="domcontentloaded", timeout=15000)

            # Assertions
            assert response is not None, "No response received"

            status = response.status
            if 200 <= status < 400:
                ok(f"HTTP {status}")
            else:
                warn(f"HTTP {status} (non-ok but non-fatal)")

            title = page.title()
            ok(f"Title: '{title}'" if title else "Page has no title (acceptable)")

            # Screenshot
            screenshot_path = tmp_dir / "smoke-test.png"
            page.screenshot(path=str(screenshot_path))
            ok(f"Screenshot saved → {screenshot_path}")

            # Evaluate some JS — verify the runtime works
            document_ready = page.evaluate("() => document.readyState")
            ok(f"document.readyState = {document_ready}")

            browser.close()

        # Clean up
        screenshot_path.unlink(missing_ok=True)

        print(f"\n  {GREEN}{BOLD}✔ Smoke test passed!{RESET}")
        return True

    except Exception as e:
        fail(f"Smoke test failed: {e}")
        # Try to save diagnostic screenshot
        try:
            if "page" in locals():
                page.screenshot(path=str(tmp_dir / "smoke-failure.png"))
                info(f"Failure screenshot → {tmp_dir / 'smoke-failure.png'}")
        except Exception:
            pass
        return False


def install_browsers() -> None:
    """Run playwright install for missing browsers."""
    header("Installing Playwright browsers")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--with-deps"],
            check=True,
        )
        ok("Browsers installed successfully")
    except subprocess.CalledProcessError as e:
        fail(f"Browser installation failed: {e}")
        sys.exit(2)


def show_diagnostics() -> None:
    """Print environment information for debugging."""
    header("Diagnostics")
    info(f"Python: {sys.version}")
    info(f"Executable: {sys.executable}")

    try:
        import playwright
        info(f"Playwright path: {playwright.__file__}")
    except ImportError:
        info("Playwright: not installed")

    try:
        import playwright.async_api
        info("Async API: available")
    except ImportError:
        info("Async API: not available")

    # Check for common CI issues
    import os
    if os.environ.get("CI"):
        info("CI environment detected — ensure --no-sandbox is configured")
    if "GITHUB_ACTIONS" in os.environ:
        info("GitHub Actions detected")


# ── CLI ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Playwright Setup & Validation — Browser Automation Skill"
    )
    parser.add_argument(
        "--smoke-only",
        action="store_true",
        help="Run only the smoke test",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install missing Playwright browsers",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Show environment diagnostics",
    )
    parser.add_argument(
        "--url",
        default="https://httpbin.org/get",
        help="URL for smoke test (default: https://httpbin.org/get)",
    )

    args = parser.parse_args()

    print(f"\n{BOLD}Playwright Setup & Validation{RESET}")
    print("Browser Automation Skill — Skill Foundry\n")

    if args.diagnostics:
        show_diagnostics()
        return

    if args.install:
        install_browsers()

    if args.smoke_only:
        success = smoke_test(args.url)
        sys.exit(0 if success else 3)

    # Full validation
    results: list[bool] = []

    results.append(check_playwright_package())
    if not results[-1]:
        print(f"\n{RED}{BOLD}✘ Playwright not installed. Exiting.{RESET}")
        info("Run: pip install playwright")
        sys.exit(1)

    results.append(check_browsers())
    if not results[-1]:
        print(f"\n{RED}{BOLD}✘ No browsers available. Exiting.{RESET}")
        info("Run: playwright install")
        info("Or: python playwright_setup.py --install")
        sys.exit(2)

    results.append(smoke_test(args.url))

    # Summary
    header("Summary")
    passed = sum(results)
    total = len(results)
    print(f"  {passed}/{total} checks passed")

    if all(results):
        print(f"\n  {GREEN}{BOLD}✔ All checks passed — you're ready to automate!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n  {RED}{BOLD}✘ {total - passed} check(s) failed{RESET}\n")
        sys.exit(3)


if __name__ == "__main__":
    main()