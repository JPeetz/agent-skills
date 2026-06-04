#!/usr/bin/env bash
# ci-cd-pipeline-generator — validate generated pipeline config
# Usage: ./validate-pipeline.sh <config-file> [--platform github|gitlab|circleci|jenkins]
set -euo pipefail

CONFIG_FILE="${1:-}"
PLATFORM="${2:-github}"

if [ -z "$CONFIG_FILE" ]; then
  echo "Usage: $0 <config-file> [--platform github|gitlab|circleci|jenkins]"
  exit 1
fi

echo "🔍 Validating CI/CD pipeline: $CONFIG_FILE"
echo "   Platform: $PLATFORM"

# Common security checks
echo ""
echo "--- Security Checks ---"

# Check for hardcoded secrets
if grep -Eq '(password|secret|token|key)\s*[:=]\s*["'"'"'][a-zA-Z0-9]' "$CONFIG_FILE" 2>/dev/null; then
  echo "❌ WARNING: Possible hardcoded credentials detected"
else
  echo "✅ No obvious hardcoded credentials"
fi

# Check for action versions pinned to tags (GitHub Actions)
if [ "$PLATFORM" = "github" ]; then
  UNPINNED=$(grep -oP 'uses:\s+\S+@v\d+' "$CONFIG_FILE" 2>/dev/null || true)
  if [ -n "$UNPINNED" ]; then
    echo "❌ WARNING: Actions not pinned to SHA:"
    echo "$UNPINNED"
  else
    echo "✅ Actions pinned to commit SHAs (or no version tags found)"
  fi
fi

echo ""
echo "--- Structure Checks ---"
if grep -q 'jobs:' "$CONFIG_FILE" 2>/dev/null; then
  echo "✅ Jobs section present"
else
  echo "❌ Missing jobs section"
fi

if grep -qEi '(npm test|pytest|go test|cargo test|jest|mocha)' "$CONFIG_FILE" 2>/dev/null; then
  echo "✅ Test step detected"
else
  echo "⚠️  No test step detected"
fi

echo ""
echo "✅ Validation complete"