#!/usr/bin/env bash
# api-design-first — start Prism mock server from spec
# Usage: ./generate-mock.sh <spec-file> [port]
set -euo pipefail

SPEC="${1:-openapi.yaml}"
PORT="${2:-4010}"

if [ ! -f "$SPEC" ]; then
  echo "❌ Spec file not found: $SPEC"
  exit 1
fi

echo "🚀 Starting mock server for: $SPEC"
echo "   URL: http://localhost:$PORT"

if command -v prism &>/dev/null; then
  prism mock "$SPEC" -p "$PORT"
elif command -v npx &>/dev/null; then
  npx @stoplight/prism-cli mock "$SPEC" -p "$PORT"
else
  echo "❌ Prism not installed."
  echo "   Install with: npm install -g @stoplight/prism-cli"
  exit 1
fi