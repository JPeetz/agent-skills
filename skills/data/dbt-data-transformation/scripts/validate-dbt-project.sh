#!/usr/bin/env bash
# =============================================================================
# validate-dbt-project.sh
# =============================================================================
# Validates a dbt project: structure check, compile, DAG integrity.
#
# Usage:
#   ./validate-dbt-project.sh [--project-dir <path>] [--target <target>]
#
# Options:
#   --project-dir   Path to dbt project root (default: current directory)
#   --target        dbt target profile (default: dev)
#   --skip-dag      Skip DAG validation (faster)
#   --strict        Fail on warnings as well as errors
#   --help          Show this help
#
# Exit codes:
#   0 — All checks passed
#   1 — Structural validation failed
#   2 — dbt compile failed
#   3 — DAG validation failed
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Defaults ---
PROJECT_DIR="$(pwd)"
TARGET="dev"
SKIP_DAG=false
STRICT=false

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
        --skip-dag)
            SKIP_DAG=true
            shift
            ;;
        --strict)
            STRICT=true
            shift
            ;;
        --help)
            sed -n '2,/^$/p' "$0" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

PASSED=0
FAILED=0
WARNINGS=0

# --- Helpers ---
log_section() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
log_pass()   { echo -e "  ${GREEN}✓${NC} $1"; PASSED=$((PASSED + 1)); }
log_fail()   { echo -e "  ${RED}✗${NC} $1"; FAILED=$((FAILED + 1)); }
log_warn()   { echo -e "  ${YELLOW}⚠${NC} $1"; WARNINGS=$((WARNINGS + 1)); }
log_info()   { echo -e "  ${BLUE}ℹ${NC} $1"; }

# =============================================================================
# Phase 1: Structural Validation
# =============================================================================
log_section "Phase 1: Structural Validation"

# Check dbt_project.yml exists
if [[ -f "dbt_project.yml" ]]; then
    log_pass "dbt_project.yml found"
else
    log_fail "dbt_project.yml not found — not a dbt project directory"
    exit 1
fi

# Check required directories
REQUIRED_DIRS=("models" "macros")
OPTIONAL_DIRS=("seeds" "snapshots" "tests" "analyses" "assets")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        log_pass "Required directory '$dir/' exists"
    else
        log_fail "Required directory '$dir/' is missing"
    fi
done

for dir in "${OPTIONAL_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        log_pass "Optional directory '$dir/' exists"
    else
        log_warn "Optional directory '$dir/' not found (may be intentional)"
    fi
done

# Check for packages.yml / dependencies.yml
if [[ -f "packages.yml" ]]; then
    log_pass "packages.yml found"
elif [[ -f "dependencies.yml" ]]; then
    log_pass "dependencies.yml found (dbt Mesh)"
else
    log_warn "No packages.yml or dependencies.yml found"
fi

# Check config-version in dbt_project.yml
CONFIG_VERSION=$(grep -E '^\s*config-version\s*:\s*' dbt_project.yml 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo "0")
if [[ "$CONFIG_VERSION" -ge 2 ]]; then
    log_pass "config-version: $CONFIG_VERSION (modern)"
else
    log_warn "config-version is $CONFIG_VERSION — consider upgrading to config-version: 2"
fi

# Check for model naming conventions
MODEL_COUNT=$(find models -name "*.sql" -type f 2>/dev/null | wc -l | tr -d ' ')
log_info "Found $MODEL_COUNT model files"

# Check for staging models
STG_COUNT=$(find models -name "stg_*.sql" -type f 2>/dev/null | wc -l | tr -d ' ')
log_info "Staging models: $STG_COUNT"

# Check for marts models
MART_COUNT=$(find models -name "fct_*.sql" -o -name "dim_*.sql" -type f 2>/dev/null | wc -l | tr -d ' ')
log_info "Mart models (fct_/dim_): $MART_COUNT"

# Check for YAML configs
YAML_COUNT=$(find models -name "*.yml" -type f 2>/dev/null | wc -l | tr -d ' ')
log_info "Model YAML config files: $YAML_COUNT"

# Check for SQL models without corresponding YAML
SQL_WITHOUT_YAML=0
for sql_file in $(find models -name "*.sql" -type f 2>/dev/null); do
    model_dir=$(dirname "$sql_file")
    if ! find "$model_dir" -maxdepth 1 -name "*.yml" 2>/dev/null | grep -q .; then
        SQL_WITHOUT_YAML=$((SQL_WITHOUT_YAML + 1))
    fi
done
if [[ "$SQL_WITHOUT_YAML" -gt 0 ]]; then
    log_warn "$SQL_WITHOUT_YAML SQL models found in directories without YAML config files"
fi

# =============================================================================
# Phase 2: dbt Parse & Compile
# =============================================================================
log_section "Phase 2: Compilation"

# Check if dbt is installed
if ! command -v dbt &> /dev/null; then
    log_warn "dbt CLI not found in PATH — skipping compilation checks"
    if [[ "$STRICT" == true ]]; then
        log_fail "dbt CLI is required in strict mode"
    fi
else
    # dbt parse (fast syntax check)
    log_info "Running: dbt parse --target $TARGET"
    if dbt parse --target "$TARGET" --quiet 2>&1; then
        log_pass "dbt parse succeeded"
    else
        log_fail "dbt parse failed — check for syntax errors in your models"
    fi

    # dbt compile without cache
    log_info "Running: dbt compile --no-populate-cache --target $TARGET"
    if dbt compile --no-populate-cache --target "$TARGET" 2>&1; then
        log_pass "dbt compile --no-populate-cache succeeded"
    else
        log_fail "dbt compile --no-populate-cache failed"
        log_info "  Check the error output above for details."
        log_info "  Common issues: missing sources, invalid refs, Jinja syntax errors."
    fi

    # Check for packages
    if [[ -f "packages.yml" ]] || [[ -f "dependencies.yml" ]]; then
        if [[ -d "dbt_packages" ]] || [[ -d "dbt_modules" ]]; then
            log_pass "Package dependencies are installed (dbt_packages/ exists)"
        else
            log_warn "packages.yml found but dbt_packages/ missing — run 'dbt deps'"
        fi
    fi
fi

# =============================================================================
# Phase 3: DAG Validation
# =============================================================================
if [[ "$SKIP_DAG" == true ]]; then
    log_section "Phase 3: DAG Validation (SKIPPED)"
else
    log_section "Phase 3: DAG Validation"

    if ! command -v dbt &> /dev/null; then
        log_warn "dbt CLI not found — skipping DAG validation"
    else
        # List all models
        MODEL_LIST=$(dbt ls --resource-type model --target "$TARGET" --quiet 2>/dev/null || echo "")
        MODEL_COUNT_DBT=$(echo "$MODEL_LIST" | grep -c '.' 2>/dev/null || echo "0")
        log_info "dbt reports $MODEL_COUNT_DBT total models in DAG"

        # Check for circular dependencies
        if dbt ls --resource-type model --target "$TARGET" 2>&1 | grep -qi "circular"; then
            log_fail "Circular dependency detected in DAG"
        else
            log_pass "No circular dependencies detected"
        fi

        # Check for orphaned models (defined but not connected to DAG)
        ORPHAN_COUNT=$(dbt ls --resource-type model --select "source:*+" --exclude "source:*" --target "$TARGET" --quiet 2>/dev/null | wc -l | tr -d ' ' || echo "0")
        TOTAL_MODELS=$(dbt ls --resource-type model --target "$TARGET" --quiet 2>/dev/null | wc -l | tr -d ' ' || echo "0")
        if [[ "$ORPHAN_COUNT" -gt 0 ]] && [[ "$TOTAL_MODELS" -gt 0 ]]; then
            ORPHAN_PCT=$((ORPHAN_COUNT * 100 / TOTAL_MODELS))
            if [[ "$ORPHAN_PCT" -gt 20 ]]; then
                log_warn "$ORPHAN_COUNT models appear disconnected from sources — consider adding source refs"
            else
                log_pass "Model connectivity looks good ($ORPHAN_COUNT potential orphans out of $TOTAL_MODELS)"
            fi
        fi

        # List exposure if available
        EXPOSURE_COUNT=$(dbt ls --resource-type exposure --target "$TARGET" --quiet 2>/dev/null | wc -l | tr -d ' ' || echo "0")
        if [[ "$EXPOSURE_COUNT" -gt 0 ]]; then
            log_info "Exposures defined: $EXPOSURE_COUNT"
        fi
    fi
fi

# =============================================================================
# Summary
# =============================================================================
log_section "Validation Summary"

echo -e "  ${GREEN}Passed:  $PASSED${NC}"
echo -e "  ${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "  ${RED}Failed:  $FAILED${NC}"

if [[ "$STRICT" == true ]] && [[ "$WARNINGS" -gt 0 ]]; then
    echo -e "\n${RED}Strict mode: treating $WARNINGS warning(s) as failures.${NC}"
    FAILED=$((FAILED + WARNINGS))
fi

if [[ "$FAILED" -gt 0 ]]; then
    echo -e "\n${RED}✗ Validation FAILED — $FAILED check(s) did not pass.${NC}"
    exit 1
else
    echo -e "\n${GREEN}✓ All checks passed.${NC}"
    exit 0
fi
