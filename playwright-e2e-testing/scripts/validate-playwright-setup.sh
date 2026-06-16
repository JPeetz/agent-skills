#!/bin/bash
# validate-playwright-setup.sh — Validates Playwright installation and browser availability
# Usage: ./validate-playwright-setup.sh [--ci]
set -euo pipefail

CI_MODE=false
if [[ "${1:-}" == "--ci" ]]; then
  CI_MODE=true
fi

echo "🔍 Validating Playwright setup..."

# Check Node.js
if ! command -v node &>/dev/null; then
  echo "❌ Node.js is not installed. Install Node.js 18+ first."
  exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 18+ required. Found: $(node -v)"
  exit 1
fi
echo "✅ Node.js $(node -v)"

# Check Playwright package
if ! npx playwright --version &>/dev/null; then
  echo "⚠️  Playwright not found. Install with: npm install -D @playwright/test"
  exit 1
fi
echo "✅ Playwright $(npx playwright --version)"

# Check browsers
BROWSERS=("chromium" "firefox" "webkit")
MISSING_BROWSERS=()

for browser in "${BROWSERS[@]}"; do
  if [ "$CI_MODE" = true ] && [ "$browser" != "chromium" ]; then
    continue  # In CI, only chromium is commonly needed
  fi
  if ! npx playwright install --dry-run "$browser" 2>/dev/null | grep -q "already installed"; then
    MISSING_BROWSERS+=("$browser")
  fi
done

if [ ${#MISSING_BROWSERS[@]} -gt 0 ]; then
  echo "⚠️  Missing browsers: ${MISSING_BROWSERS[*]}"
  echo "   Run: npx playwright install ${MISSING_BROWSERS[*]}"
  echo "   Or with deps: npx playwright install --with-deps ${MISSING_BROWSERS[*]}"
else
  echo "✅ All required browsers installed"
fi

# Check config file
if [ -f "playwright.config.ts" ] || [ -f "playwright.config.js" ]; then
  echo "✅ playwright.config found"
else
  echo "⚠️  No playwright.config found in current directory"
fi

# Check test directory
if [ -d "e2e" ] || [ -d "tests" ] || [ -d "__tests__" ]; then
  echo "✅ Test directory found"
else
  echo "⚠️  No e2e/ or tests/ directory found"
fi

if [ "$CI_MODE" = true ]; then
  echo ""
  echo "🏗️  CI mode: installing system dependencies..."
  npx playwright install --with-deps chromium 2>/dev/null || \
    echo "⚠️  Could not auto-install system deps. Ensure Docker image includes them."
fi

echo ""
echo "✅ Playwright validation complete."
