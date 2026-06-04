#!/usr/bin/env bash
# git-workflow-automation — validate Conventional Commits compliance
# Usage: ./validate-commits.sh [range]
set -euo pipefail

RANGE="${1:-HEAD~10..HEAD}"
VIOLATIONS=0

echo "🔍 Validating commits in range: $RANGE"
echo ""

while IFS= read -r line; do
  HASH=$(echo "$line" | cut -d' ' -f1)
  MSG=$(echo "$line" | cut -d' ' -f2-)

  # Check conventional commit format
  if ! echo "$MSG" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?: .+'; then
    echo "❌ $HASH: Non-conventional commit: $MSG"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi

  # Check subject line length
  SUBJECT=$(echo "$MSG" | head -1)
  if [ ${#SUBJECT} -gt 72 ]; then
    echo "⚠️  $HASH: Subject line > 72 chars (${#SUBJECT})"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(git log "$RANGE" --pretty=format:"%h %s")

echo ""
if [ "$VIOLATIONS" -eq 0 ]; then
  echo "✅ All commits follow Conventional Commits"
else
  echo "❌ $VIOLATIONS violation(s) found"
fi