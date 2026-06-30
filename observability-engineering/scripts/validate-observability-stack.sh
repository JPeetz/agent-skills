#!/usr/bin/env bash
# validate-observability-stack.sh
# Validates OpenTelemetry Collector config, Prometheus rules syntax,
# Grafana dashboard JSON validity, and Alertmanager configuration.
#
# Usage:
#   ./validate-observability-stack.sh [--config-dir /path/to/configs]
#
# Requires: otelcol, promtool, jq, amtool (optional)
# Install: follow each tool's installation guide

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

CONFIG_DIR="${1:-.}"
FAILURES=0
WARNINGS=0
PASSES=0

log_pass()  { echo -e "${GREEN}[PASS]${NC} $1"; ((PASSES+=1)); }
log_fail()  { echo -e "${RED}[FAIL]${NC} $1"; ((FAILURES+=1)); }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARNINGS+=1)); }
log_info()  { echo -e "${BOLD}[INFO]${NC} $1"; }
log_section() { echo ""; echo -e "${BOLD}━━━ $1 ━━━${NC}"; }

# ─────────────────────────────────────────────
# 1. OpenTelemetry Collector Config Validation
# ─────────────────────────────────────────────
validate_otel_collector() {
    log_section "OpenTelemetry Collector"

    if ! command -v otelcol &>/dev/null; then
        log_warn "otelcol binary not found in PATH — skipping collector config validation"
        log_info "Install: https://opentelemetry.io/docs/collector/installation/"
        return
    fi

    local otel_configs
    otel_configs=$(find "$CONFIG_DIR" -type f \( -name "otelcol*.yaml" -o -name "otelcol*.yml" -o -name "collector*.yaml" -o -name "collector*.yml" \) 2>/dev/null || true)

    if [ -z "$otel_configs" ]; then
        log_warn "No OpenTelemetry Collector config files found in $CONFIG_DIR"
        return
    fi

    while IFS= read -r config; do
        log_info "Validating: $config"
        if otelcol validate --config "$config" 2>&1; then
            log_pass "Collector config valid: $config"

            # Additional structural checks
            if grep -q "processors:" "$config"; then
                if grep -q "batch:" "$config"; then
                    log_pass "  batch processor configured"
                else
                    log_warn "  No batch processor — consider adding for performance"
                fi
                if grep -q "memory_limiter:" "$config"; then
                    log_pass "  memory_limiter processor configured"
                else
                    log_warn "  No memory_limiter — risk of OOM under load"
                fi
            fi

            if grep -q "tail_sampling:" "$config"; then
                log_pass "  tail_sampling processor configured"
            fi

            # Check pipeline wiring completeness
            if grep -q "pipelines:" "$config"; then
                local pipeline_count
                pipeline_count=$(grep -c "^    [a-z]*:" "$config" | grep -v "^0$" || true)
                log_info "  Pipelines detected: ${pipeline_count:-0}"
            fi
        else
            log_fail "Collector config invalid: $config"
        fi
    done <<< "$otel_configs"
}

# ─────────────────────────────────────────────
# 2. Prometheus Rules Validation
# ─────────────────────────────────────────────
validate_prometheus_rules() {
    log_section "Prometheus Rules"

    if ! command -v promtool &>/dev/null; then
        log_warn "promtool not found in PATH — skipping Prometheus rules validation"
        log_info "Install: https://prometheus.io/download/"
        return
    fi

    local rule_files
    rule_files=$(find "$CONFIG_DIR" -type f \( -name "*.rules.yml" -o -name "*.rules.yaml" -o -name "*_rules.yml" -o -name "*_rules.yaml" -o -name "alerts*.yml" -o -name "alerts*.yaml" -o -name "alerting*.yml" -o -name "alerting*.yaml" \) 2>/dev/null || true)

    if [ -z "$rule_files" ]; then
        log_warn "No Prometheus rule files found in $CONFIG_DIR"
        return
    fi

    while IFS= read -r rule_file; do
        log_info "Validating: $rule_file"

        if promtool check rules "$rule_file" 2>&1; then
            log_pass "Rules syntax valid: $rule_file"

            # Count rules for summary
            local group_count rule_count
            group_count=$(grep -c "^\s*-\s*name:" "$rule_file" 2>/dev/null || echo 0)
            rule_count=$(grep -c "^\s*-\s*alert:\|^\s*-\s*record:" "$rule_file" 2>/dev/null || echo 0)
            log_info "  Groups: $group_count, Rules: $rule_count"

            # Warnings on common anti-patterns
            if grep -q "severity:" "$rule_file"; then
                log_pass "  severity labels present"
            else
                log_warn "  No severity labels — alerts may not route correctly"
            fi

            if grep -q "runbook\|runbook_url\|runbook_url" "$rule_file"; then
                log_pass "  runbook annotations present"
            else
                log_warn "  No runbook annotations — every alert should have a runbook"
            fi
        else
            log_fail "Rules syntax invalid: $rule_file"
        fi
    done <<< "$rule_files"
}

# ─────────────────────────────────────────────
# 3. Grafana Dashboard JSON Validation
# ─────────────────────────────────────────────
validate_grafana_dashboards() {
    log_section "Grafana Dashboards"

    if ! command -v jq &>/dev/null; then
        log_warn "jq not found in PATH — skipping dashboard JSON validation"
        log_info "Install: brew install jq (macOS) or apt install jq (Linux)"
        return
    fi

    local dashboard_files
    dashboard_files=$(find "$CONFIG_DIR" -type f -name "*.json" 2>/dev/null || true)

    if [ -z "$dashboard_files" ]; then
        log_warn "No JSON dashboard files found in $CONFIG_DIR"
        return
    fi

    while IFS= read -r dashboard; do
        log_info "Validating: $dashboard"

        # Validate JSON syntax
        if jq empty "$dashboard" 2>/dev/null; then
            log_pass "Valid JSON: $dashboard"

            # Check for Grafana dashboard structure
            if jq -e '.dashboard // .id' "$dashboard" &>/dev/null; then
                log_pass "  Appears to be a Grafana dashboard"

                # Panel count
                local panel_count
                panel_count=$(jq '[.panels[]? // .dashboard.panels[]?] | length' "$dashboard" 2>/dev/null || echo 0)
                log_info "  Panels: $panel_count"

                # Dashboard title
                local title
                title=$(jq -r '.title // .dashboard.title // "unnamed"' "$dashboard" 2>/dev/null)
                log_info "  Title: $title"

                # Check for common panel types
                local has_graph has_stat has_table has_gauge
                has_graph=$(jq '[.. | select(.type? == "timeseries" or .type? == "graph")] | length' "$dashboard" 2>/dev/null || echo 0)
                has_stat=$(jq '[.. | select(.type? == "stat")] | length' "$dashboard" 2>/dev/null || echo 0)
                has_table=$(jq '[.. | select(.type? == "table")] | length' "$dashboard" 2>/dev/null || echo 0)
                has_gauge=$(jq '[.. | select(.type? == "gauge" or .type? == "bargauge")] | length' "$dashboard" 2>/dev/null || echo 0)
                log_info "  Layout: ${has_graph} timeseries, ${has_stat} stat, ${has_table} table, ${has_gauge} gauge"
            else
                log_warn "  Not sure if this is a Grafana dashboard — missing .dashboard or .id"
            fi
        else
            log_fail "Invalid JSON: $dashboard"
        fi
    done <<< "$dashboard_files"
}

# ─────────────────────────────────────────────
# 4. Alertmanager Config Validation
# ─────────────────────────────────────────────
validate_alertmanager() {
    log_section "Alertmanager"

    if ! command -v amtool &>/dev/null; then
        log_warn "amtool not found in PATH — skipping Alertmanager config validation"
        log_info "Install: https://prometheus.io/download/ (part of alertmanager)"
        return
    fi

    local am_configs
    am_configs=$(find "$CONFIG_DIR" -type f \( -name "alertmanager*.yml" -o -name "alertmanager*.yaml" \) 2>/dev/null || true)

    if [ -z "$am_configs" ]; then
        log_warn "No Alertmanager config files found in $CONFIG_DIR"
        return
    fi

    while IFS= read -r am_config; do
        log_info "Validating: $am_config"
        if amtool check-config "$am_config" 2>&1; then
            log_pass "Alertmanager config valid: $am_config"

            # Check for key features
            if grep -q "pagerduty\|opsgenie\|victorops" "$am_config"; then
                log_pass "  On-call integration configured"
            else
                log_warn "  No external on-call integration detected"
            fi

            if grep -q "inhibit_rules:" "$am_config"; then
                log_pass "  Inhibition rules configured"
            else
                log_warn "  No inhibition rules — may get alert storms during outages"
            fi

            if grep -q "repeat_interval:" "$am_config"; then
                log_pass "  Repeat interval configured"
            else
                log_warn "  No explicit repeat_interval — defaults to 1h"
            fi
        else
            log_fail "Alertmanager config invalid: $am_config"
        fi
    done <<< "$am_configs"
}

# ─────────────────────────────────────────────
# 5. OTEL_ENV Validation (check environment)
# ─────────────────────────────────────────────
validate_otel_env() {
    log_section "OpenTelemetry Environment"

    local otel_vars=(
        OTEL_SERVICE_NAME
        OTEL_EXPORTER_OTLP_ENDPOINT
        OTEL_TRACES_SAMPLER
        OTEL_TRACES_SAMPLER_ARG
        OTEL_RESOURCE_ATTRIBUTES
        OTEL_LOG_LEVEL
    )

    local found_any=false
    for var in "${otel_vars[@]}"; do
        if [ -n "${!var:-}" ]; then
            log_pass "$var = ${!var}"
            found_any=true
        fi
    done

    if [ "$found_any" = false ]; then
        log_info "No OTEL_* environment variables set (this is expected in CI)"
    fi

    # OTEL_SERVICE_NAME is the most critical
    if [ -z "${OTEL_SERVICE_NAME:-}" ]; then
        log_warn "OTEL_SERVICE_NAME is not set — services will export as 'unknown_service'"
    fi
}

# ─────────────────────────────────────────────
# 6. Summary
# ─────────────────────────────────────────────
print_summary() {
    log_section "Summary"
    local total=$((PASSES + FAILURES + WARNINGS))
    echo -e "Total checks:  ${BOLD}$total${NC}"
    echo -e "Passed:        ${GREEN}${BOLD}$PASSES${NC}"
    echo -e "Failed:        ${RED}${BOLD}$FAILURES${NC}"
    echo -e "Warnings:      ${YELLOW}${BOLD}$WARNINGS${NC}"
    echo ""

    if [ "$FAILURES" -gt 0 ]; then
        echo -e "${RED}${BOLD}✗ Validation FAILED — $FAILURES error(s) found${NC}"
        exit 1
    else
        echo -e "${GREEN}${BOLD}✓ All validations passed${NC}"
        exit 0
    fi
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
main() {
    echo -e "${BOLD}"
    echo "╔══════════════════════════════════════════════╗"
    echo "║   Observability Stack Validator             ║"
    echo "║   Config Directory: $CONFIG_DIR"
    echo "╚══════════════════════════════════════════════╝"
    echo -e "${NC}"

    validate_otel_env
    validate_otel_collector
    validate_prometheus_rules
    validate_grafana_dashboards
    validate_alertmanager
    print_summary
}

main