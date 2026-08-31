#!/usr/bin/env bash
# git-workflow-automation — generate changelog from git history
# Usage: ./generate-changelog.sh [--since TAG] [--output FILE]
set -euo pipefail

SINCE="${2:-$(git describe --tags --abbrev=0 2>/dev/null || echo '')}"
OUTPUT="${4:-CHANGELOG.md}"

echo "# Changelog" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "## [Unreleased]" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if [ -n "$SINCE" ]; then
  echo "📝 Generating changelog from $SINCE to HEAD..."
  RANGE="$SINCE..HEAD"
else
  echo "📝 Generating changelog from first commit..."
  RANGE=""
fi

# Added (feat)
echo "### Added" >> "$OUTPUT"
git log "$RANGE" --pretty=format:"- %s" --grep="^feat" 2>/dev/null | sed 's/^feat\(([^)]*)\)\?: /- /' >> "$OUTPUT" || echo "- (none)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Fixed (fix)
echo "### Fixed" >> "$OUTPUT"
git log "$RANGE" --pretty=format:"- %s" --grep="^fix" 2>/dev/null | sed 's/^fix\(([^)]*)\)\?: /- /' >> "$OUTPUT" || echo "- (none)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Performance
echo "### Performance" >> "$OUTPUT"
git log "$RANGE" --pretty=format:"- %s" --grep="^perf" 2>/dev/null | sed 's/^perf\(([^)]*)\)\?: /- /' >> "$OUTPUT" || echo "- (none)" >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "✅ Changelog written to $OUTPUT"