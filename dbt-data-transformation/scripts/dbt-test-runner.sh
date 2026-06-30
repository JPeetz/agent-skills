#!/usr/bin/env bash
# =============================================================================
# dbt-test-runner.sh
# =============================================================================
# Runs dbt tests with severity filtering and generates structured test reports.
#
# Usage:
#   ./dbt-test-runner.sh [--project-dir <path>] [--target <target>]
#                        [--severity error|warn] [--select <selector>]
#                        [--output json|table] [--report-file <path>]
#                        [--fail-fast] [--include-warnings]
#
# Options:
#   --project-dir       Path to dbt project root (default: current directory)
#   --target            dbt target profile (default: dev)
#   --severity          Filter tests by minimum severity: error | warn (default: warn)
#   --select            dbt node selection syntax (models, tags, etc.)
#   --output            Output format: json | table (default: table)
#   --report-file       Write structured JSON report to this path
#   --fail-fast         Exit on first test failure
#   --include-warnings  Treat warnings as failures in exit code
#   --help              Show this help
#
# Exit codes:
#   0 — All tests passed (or only warnings without --include-warnings)
#   1 — One or more tests failed
#   2 — Test execution error (dbt error, config issue)
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Defaults ---
PROJECT_DIR="$(pwd)"
TARGET="dev"
SEVERITY="warn"
SELECTOR=""
OUTPUT_FORMAT="table"
REPORT_FILE=""
FAIL_FAST=false
INCLUDE_WARNINGS=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-dir)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --target)
            TARGET="$2"
            shift 2
            ;;
        --severity)
            SEVERITY="$2"
            shift 2
            ;;
        --select)
            SELECTOR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --report-file)
            REPORT_FILE="$2"
            shift 2
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --include-warnings)
            INCLUDE_WARNINGS=true
            shift
            ;;
        --help)
            sed -n '2,/^$/p' "$0" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 2
            ;;
    esac
done

cd "$PROJECT_DIR"

# --- Validate severity ---
if [[ "$SEVERITY" != "error" ]] && [[ "$SEVERITY" != "warn" ]]; then
    echo -e "${RED}Invalid severity: '$SEVERITY'. Must be 'error' or 'warn'.${NC}"
    exit 2
fi

# --- Check dbt availability ---
if ! command -v dbt &> /dev/null; then
    echo -e "${RED}dbt CLI not found. Please install dbt and ensure it is in PATH.${NC}"
    exit 2
fi

# --- Build dbt command ---
DBT_CMD="dbt test --target $TARGET"
if [[ -n "$SELECTOR" ]]; then
    DBT_CMD="$DBT_CMD --select $SELECTOR"
fi
if [[ "$FAIL_FAST" == true ]]; then
    DBT_CMD="$DBT_CMD --fail-fast"
fi

# --- Timestamps ---
START_TIME=$(date +%s)
START_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# =============================================================================
# Run Tests
# =============================================================================
echo -e "${BLUE}━━━ dbt Test Runner ━━━${NC}"
echo -e "  Project:    ${CYAN}$PROJECT_DIR${NC}"
echo -e "  Target:     ${CYAN}$TARGET${NC}"
echo -e "  Severity:   ${CYAN}$SEVERITY${NC}"
echo -e "  Selector:   ${CYAN}${SELECTOR:-all tests}${NC}"
echo -e "  Fail fast:  ${CYAN}$FAIL_FAST${NC}"
echo -e "  Start time: ${CYAN}$START_TIMESTAMP${NC}"
echo ""

# --- Run dbt tests ---
# We capture output and exit code separately
TEMP_OUTPUT=$(mktemp /tmp/dbt-test-output.XXXXXX)
trap "rm -f $TEMP_OUTPUT" EXIT

set +e  # Don't exit on dbt test failures — we handle them
eval "$DBT_CMD" 2>&1 | tee "$TEMP_OUTPUT"
DBT_EXIT_CODE=${PIPESTATUS[0]}
set -e

END_TIME=$(date +%s)
END_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DURATION=$((END_TIME - START_TIME))

# =============================================================================
# Parse Results
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Test Results ━━━${NC}"

# Parse dbt output for test counts
# dbt v1.8+ outputs summary lines like:
#   "PASS=42 WARN=3 ERROR=5 SKIP=0 TOTAL=50"
# dbt v1.5-v1.7 outputs differently — try multiple patterns

PASS_COUNT=$(grep -oP 'PASS=\K\d+' "$TEMP_OUTPUT" 2>/dev/null | tail -1 || echo "0")
WARN_COUNT=$(grep -oP 'WARN=\K\d+' "$TEMP_OUTPUT" 2>/dev/null | tail -1 || echo "0")
ERROR_COUNT=$(grep -oP 'ERROR=\K\d+' "$TEMP_OUTPUT" 2>/dev/null | tail -1 || echo "0")
SKIP_COUNT=$(grep -oP 'SKIP=\K\d+' "$TEMP_OUTPUT" 2>/dev/null | tail -1 || echo "0")
TOTAL_COUNT=$(grep -oP 'TOTAL=\K\d+' "$TEMP_OUTPUT" 2>/dev/null | tail -1 || echo "0")

# Fallback: count pass/fail/error lines if no summary found
if [[ "$TOTAL_COUNT" == "0" ]]; then
    PASS_COUNT=$(grep -c 'PASS' "$TEMP_OUTPUT" 2>/dev/null || echo "0")
    FAIL_COUNT=$(grep -c 'FAIL' "$TEMP_OUTPUT" 2>/dev/null || echo "0")
    WARN_COUNT=$(grep -c 'WARN' "$TEMP_OUTPUT" 2>/dev/null || echo "0")
    ERROR_COUNT=$(grep -c 'ERROR' "$TEMP_OUTPUT" 2>/dev/null || echo "0")
    TOTAL_COUNT=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
fi

# Normalize to integers
PASS_COUNT=${PASS_COUNT//[!0-9]/}
WARN_COUNT=${WARN_COUNT//[!0-9]/}
ERROR_COUNT=${ERROR_COUNT//[!0-9]/}
SKIP_COUNT=${SKIP_COUNT//[!0-9]/}
TOTAL_COUNT=${TOTAL_COUNT//[!0-9]/}

: "${PASS_COUNT:=0}"
: "${WARN_COUNT:=0}"
: "${ERROR_COUNT:=0}"
: "${SKIP_COUNT:=0}"
: "${TOTAL_COUNT:=0}"

# --- Table output (default) ---
if [[ "$OUTPUT_FORMAT" == "table" ]]; then
    printf "  %-12s %s\n" "Status" "Count"
    printf "  %-12s %s\n" "────────────" "─────"
    printf "  ${GREEN}%-12s${NC} %d\n" "PASS" "$PASS_COUNT"
    printf "  ${YELLOW}%-12s${NC} %d\n" "WARN" "$WARN_COUNT"
    printf "  ${RED}%-12s${NC} %d\n" "ERROR" "$ERROR_COUNT"
    printf "  ${CYAN}%-12s${NC} %d\n" "SKIP" "$SKIP_COUNT"
    printf "  %-12s %s\n" "────────────" "─────"
    printf "  %-12s %d\n" "TOTAL" "$TOTAL_COUNT"
fi

# --- Determine exit code ---
EXIT_CODE=0
if [[ "$ERROR_COUNT" -gt 0 ]]; then
    EXIT_CODE=1
fi
if [[ "$INCLUDE_WARNINGS" == true ]] && [[ "$WARN_COUNT" -gt 0 ]]; then
    EXIT_CODE=1
fi
if [[ "$DBT_EXIT_CODE" -ne 0 ]] && [[ "$DBT_EXIT_CODE" -ne 1 ]]; then
    # dbt itself failed (exit code 2+), not just test failures
    EXIT_CODE=2
fi

# --- Severity-filtered result ---
echo ""
if [[ "$SEVERITY" == "error" ]]; then
    if [[ "$ERROR_COUNT" -gt 0 ]]; then
        echo -e "${RED}✗ Test run FAILED — $ERROR_COUNT error-level test(s) failed.${NC}"
        EXIT_CODE=1
    else
        echo -e "${GREEN}✓ All error-level tests passed.${NC}"
    fi
else
    if [[ "$ERROR_COUNT" -gt 0 ]]; then
        echo -e "${RED}✗ Test run FAILED — $ERROR_COUNT error(s).${NC}"
    elif [[ "$WARN_COUNT" -gt 0 ]]; then
        echo -e "${YELLOW}⚠ Tests completed with $WARN_COUNT warning(s).${NC}"
    else
        echo -e "${GREEN}✓ All $TOTAL_COUNT tests passed.${NC}"
    fi
fi

# =============================================================================
# Failed Test Details
# =============================================================================
if [[ "$ERROR_COUNT" -gt 0 ]] || [[ "$WARN_COUNT" -gt 0 ]]; then
    echo ""
    echo -e "${BLUE}━━━ Failure Details ━━━${NC}"

    # Extract test failure details from dbt output
    # Look for lines with FAIL or ERROR status indicators
    FAILURES=$(grep -E '(FAIL|ERROR)\s+\S+' "$TEMP_OUTPUT" 2>/dev/null | head -20 || echo "")

    if [[ -n "$FAILURES" ]]; then
        echo "$FAILURES" | while IFS= read -r line; do
            if echo "$line" | grep -q "FAIL"; then
                echo -e "  ${RED}FAIL${NC}  $line" | sed 's/FAIL\s*//'
            elif echo "$line" | grep -q "ERROR"; then
                echo -e "  ${RED}ERROR${NC} $line" | sed 's/ERROR\s*//'
            fi
        done
    else
        echo -e "  ${YELLOW}⚠ Detailed failure information not available in output.${NC}"
        echo "    Check the full log above for specific test failures."
    fi

    # Show failed test count per severity
    echo ""
    echo "  Affected resources:"

    # Try to extract individual test names from error output
    grep -oP '(?<=Failure in test )\S+' "$TEMP_OUTPUT" 2>/dev/null | sort -u | while IFS= read -r test_name; do
        echo -e "    ${RED}•${NC} $test_name"
    done
fi

# =============================================================================
# Performance Summary
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Performance ━━━${NC}"

# Format duration
if [[ "$DURATION" -lt 60 ]]; then
    DURATION_DISPLAY="${DURATION}s"
elif [[ "$DURATION" -lt 3600 ]]; then
    DURATION_DISPLAY="$((DURATION / 60))m $((DURATION % 60))s"
else
    DURATION_DISPLAY="$((DURATION / 3600))h $(((DURATION % 3600) / 60))m"
fi

echo -e "  Duration:    ${CYAN}$DURATION_DISPLAY${NC}"
echo -e "  Tests/sec:   ${CYAN}$(awk "BEGIN {printf \"%.1f\", $TOTAL_COUNT / ($DURATION + 1)}")${NC}"
echo ""

# =============================================================================
# JSON Report
# =============================================================================
if [[ -n "$REPORT_FILE" ]]; then
    REPORT_DIR=$(dirname "$REPORT_FILE")
    mkdir -p "$REPORT_DIR"

    # Calculate pass rate
    if [[ "$TOTAL_COUNT" -gt 0 ]]; then
        PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASS_COUNT / $TOTAL_COUNT) * 100}")
    else
        PASS_RATE="0.0"
    fi

    # Determine overall status
    if [[ "$ERROR_COUNT" -gt 0 ]]; then
        STATUS="failed"
    elif [[ "$WARN_COUNT" -gt 0 ]]; then
        STATUS="warning"
    else
        STATUS="passed"
    fi

    cat > "$REPORT_FILE" << JSONEOF
{
  "report": {
    "generated_at": "$END_TIMESTAMP",
    "project_dir": "$PROJECT_DIR",
    "target": "$TARGET",
    "severity_filter": "$SEVERITY",
    "selector": "${SELECTOR:-all}",
    "fail_fast": $FAIL_FAST,
    "include_warnings": $INCLUDE_WARNINGS
  },
  "execution": {
    "start_time": "$START_TIMESTAMP",
    "end_time": "$END_TIMESTAMP",
    "duration_seconds": $DURATION,
    "duration_display": "$DURATION_DISPLAY",
    "dbt_exit_code": $DBT_EXIT_CODE
  },
  "results": {
    "total": $TOTAL_COUNT,
    "passed": $PASS_COUNT,
    "warnings": $WARN_COUNT,
    "errors": $ERROR_COUNT,
    "skipped": $SKIP_COUNT,
    "pass_rate_pct": $PASS_RATE,
    "status": "$STATUS"
  }
}
JSONEOF

    echo -e "${GREEN}✓ JSON report written to: $REPORT_FILE${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

exit $EXIT_CODE
