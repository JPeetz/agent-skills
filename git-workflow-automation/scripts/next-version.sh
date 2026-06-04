#!/usr/bin/env bash
# git-workflow-automation — determine next semantic version
# Usage: ./next-version.sh [current-version]
set -euo pipefail

CURRENT="${1:-$(git describe --tags --abbrev=0 2>/dev/null || echo '0.0.0')}"
CURRENT="${CURRENT#v}"

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Check for breaking changes
if git log "v${CURRENT}..HEAD" --pretty=format:"%s" 2>/dev/null | grep -qE '(BREAKING CHANGE|!:)' ; then
  MAJOR=$((MAJOR + 1))
  MINOR=0
  PATCH=0
  echo "v${MAJOR}.${MINOR}.${PATCH} (MAJOR — breaking change detected)"
  exit 0
fi

# Check for features
if git log "v${CURRENT}..HEAD" --pretty=format:"%s" 2>/dev/null | grep -qE '^feat' ; then
  MINOR=$((MINOR + 1))
  PATCH=0
  echo "v${MAJOR}.${MINOR}.${PATCH} (MINOR — new feature detected)"
  exit 0
fi

# Check for fixes
if git log "v${CURRENT}..HEAD" --pretty=format:"%s" 2>/dev/null | grep -qE '^(fix|perf)' ; then
  PATCH=$((PATCH + 1))
  echo "v${MAJOR}.${MINOR}.${PATCH} (PATCH — bug fix detected)"
  exit 0
fi

echo "v${MAJOR}.${MINOR}.${PATCH} (NO CHANGE — no feat/fix/breaking commits)"