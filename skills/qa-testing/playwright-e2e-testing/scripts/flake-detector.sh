#!/bin/bash
# flake-detector.sh — Runs a Playwright test suite repeatedly to detect flaky tests
# Usage: ./flake-detector.sh [--runs=10] [--grep="pattern"] [--project="name"]
set -euo pipefail

RUNS=10
GREP_FILTER=""
PROJECT=""
SPEC_FILE="${1:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs=*) RUNS="${1#*=}"; shift ;;
    --grep=*) GREP_FILTER="--grep ${1#*=}"; shift ;;
    --project=*) PROJECT="--project ${1#*=}"; shift ;;
    *) SPEC_FILE="$1"; shift ;;
  esac
done

if [ -z "$SPEC_FILE" ]; then
  echo "Usage: ./flake-detector.sh <spec-file> [--runs=10] [--grep=pattern]"
  echo "Example: ./flake-detector.sh e2e/tests/checkout.spec.ts --runs=20"
  exit 1
fi

echo "🔬 Flake Detector — Running '$SPEC_FILE' $RUNS times"
echo "================================================"

PASSES=0
FAILURES=0
FLAKES=0
PREVIOUS_RESULT=""

# Disable retries to expose flakes
export PLAYWRIGHT_RETRIES=0

for i in $(seq 1 $RUNS); do
  printf "Run %2d/%d... " "$i" "$RUNS"

  if npx playwright test "$SPEC_FILE" $GREP_FILTER $PROJECT --reporter=line 2>&1 | tail -1 | grep -q "passed"; then
    RESULT="PASS"
    PASSES=$((PASSES + 1))
  else
    RESULT="FAIL"
    FAILURES=$((FAILURES + 1))
  fi

  echo "$RESULT"

  if [ -n "$PREVIOUS_RESULT" ] && [ "$RESULT" != "$PREVIOUS_RESULT" ]; then
    FLAKES=$((FLAKES + 1))
  fi
  PREVIOUS_RESULT="$RESULT"
done

echo ""
echo "================================================"
echo "📊 Results for $SPEC_FILE:"
echo "   Passes:   $PASSES/$RUNS"
echo "   Failures: $FAILURES/$RUNS"
echo "   Flakes:   $FLAKES (result changes between runs)"
echo ""

if [ $FLAKES -gt 0 ]; then
  echo "⚠️  FLAKY TEST DETECTED — Result changed between runs"
  echo "   Review test for: missing awaits, race conditions, time dependencies"
  echo "   Run with --debug to step through: npx playwright test $SPEC_FILE --debug"
  exit 1
elif [ $FAILURES -gt 0 ]; then
  echo "❌ TEST FAILED consistently — Not flaky, genuinely broken"
  exit 1
else
  echo "✅ TEST IS STABLE — $RUNS/$RUNS passed consistently"
fi
