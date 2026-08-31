#!/usr/bin/env bash
# accessibility-compliance-audit — run axe-core against HTML files
# Usage: ./audit-html.sh <file-or-directory>
# Dependencies: npm install axe-cli (PEP 723 style)
set -euo pipefail

TARGET="${1:-.}"

echo "🔍 Running accessibility audit on: $TARGET"
echo ""

if ! command -v axe &>/dev/null && ! npx axe --version &>/dev/null; then
  echo "⚠️  axe-cli not found. Install with: npm install -g @axe-core/cli"
  echo "   Or run: npx @axe-core/cli $TARGET"
  exit 1
fi

if [ -f "$TARGET" ]; then
  axe "$TARGET" --stdout 2>/dev/null || echo "⚠️  Accessibility violations found in $TARGET"
elif [ -d "$TARGET" ]; then
  for f in "$TARGET"/*.html; do
    [ -f "$f" ] || continue
    echo "  Checking: $f"
    axe "$f" --stdout 2>/dev/null || echo "  ⚠️  Violations in $f"
  done
else
  echo "❌ Target not found: $TARGET"
  exit 1
fi

echo ""
echo "✅ Audit complete"