#!/usr/bin/env bash
# api-design-first — validate OpenAPI spec with spectral linting
# Usage: ./validate-spec.sh <spec-file>
# Dependencies: npm install -g @stoplight/spectral-cli
set -euo pipefail

SPEC="${1:-openapi.yaml}"

if [ ! -f "$SPEC" ]; then
  echo "❌ Spec file not found: $SPEC"
  exit 1
fi

echo "🔍 Validating OpenAPI spec: $SPEC"

if command -v spectral &>/dev/null; then
  spectral lint "$SPEC"
elif command -v npx &>/dev/null; then
  npx @stoplight/spectral-cli lint "$SPEC"
else
  echo "⚠️  spectral not installed. Install with: npm install -g @stoplight/spectral-cli"
  echo "   Performing basic YAML validation only..."
  if command -v python3 &>/dev/null; then
    python3 -c "import yaml; yaml.safe_load(open('$SPEC'))" && echo "✅ Valid YAML"
  fi
fi

echo "✅ Validation complete"