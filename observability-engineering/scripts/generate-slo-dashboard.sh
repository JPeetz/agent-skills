#!/usr/bin/env bash
# generate-slo-dashboard.sh
# Generates a Grafana SLO dashboard JSON from SLI definitions.
#
# This script creates a comprehensive SLO dashboard with:
#   - Error budget burn-down gauge
#   - Burn rate chart (short and long window)
#   - SLI compliance over time
#   - Latency distribution panels
#   - Top-N error endpionts table
#
# Usage:
#   ./generate-slo-dashboard.sh --name "Payment API" --slo-target 99.9 --window 30d \
#     --metrics-prefix "payment_api" --output dashboard.json
#
#   ./generate-slo-dashboard.sh --config sli-definitions.yaml  (coming soon)
#
# Requirements: jq

set -euo pipefail

# ─────────────────────────────────────────────
# Defaults
# ─────────────────────────────────────────────
DASHBOARD_NAME="SLO Dashboard"
SLO_TARGET="99.9"
WINDOW="30d"
METRICS_PREFIX="service"
OUTPUT_FILE="slo-dashboard.json"
UID="slo-dashboard-$(date +%s)"
VERSION=1

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)          DASHBOARD_NAME="$2";   shift 2 ;;
        --slo-target)    SLO_TARGET="$2";       shift 2 ;;
        --window)        WINDOW="$2";           shift 2 ;;
        --metrics-prefix) METRICS_PREFIX="$2";  shift 2 ;;
        --output|-o)     OUTPUT_FILE="$2";      shift 2 ;;
        --uid)           UID="$2";              shift 2 ;;
        --version)       VERSION="$2";          shift 2 ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --name <name>           Dashboard title (default: 'SLO Dashboard')"
            echo "  --slo-target <pct>      SLO target as percentage (default: 99.9)"
            echo "  --window <duration>     SLO compliance window (default: 30d)"
            echo "  --metrics-prefix <str>  Prometheus metric prefix (default: service)"
            echo "  --output <file>         Output file path (default: slo-dashboard.json)"
            echo "  --uid <uid>             Dashboard UID (default: auto-generated)"
            echo "  --version <int>         Dashboard version (default: 1)"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

# Convert SLO target to decimal for queries
SLO_DECIMAL=$(echo "scale=4; $SLO_TARGET / 100" | bc)
ERROR_BUDGET=$(echo "scale=4; 1 - $SLO_DECIMAL" | bc)
echo "Generating dashboard: $DASHBOARD_NAME"
echo "  SLO Target:       ${SLO_TARGET}%"
echo "  Error Budget:     ${ERROR_BUDGET} (1 - ${SLO_DECIMAL})"
echo "  Window:           $WINDOW"
echo "  Metrics prefix:   $METRICS_PREFIX"
echo "  Output:           $OUTPUT_FILE"

# ─────────────────────────────────────────────
# Panel Definitions (as JSON fragments)
# ─────────────────────────────────────────────

# Convert window to prometheus range vector
case "$WINDOW" in
    7d)  RANGE_VECTOR="7d"  ;;
    14d) RANGE_VECTOR="14d" ;;
    30d) RANGE_VECTOR="30d" ;;
    90d) RANGE_VECTOR="90d" ;;
    *)   RANGE_VECTOR="30d" ;;
esac

# Panel 1: Title / Row Header
title_panel=$(jq -n '{
    "type": "row",
    "title": "SLO Overview",
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0}
}')

# Panel 2: Error Budget Remaining (Stat / Gauge)
error_budget_query="
  1 - (
    sum(rate(${METRICS_PREFIX}_requests_total{status=~\"5..\"}[${RANGE_VECTOR}]))
    /
    sum(rate(${METRICS_PREFIX}_requests_total[${RANGE_VECTOR}]))
  ) / ${ERROR_BUDGET}
"

budget_panel=$(jq -n --arg query "$error_budget_query" --arg title "Error Budget Remaining" '{
    "type": "stat",
    "title": $title,
    "gridPos": {"h": 5, "w": 6, "x": 0, "y": 1},
    "options": {
        "colorMode": "background",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": false},
        "textMode": "auto"
    },
    "fieldConfig": {
        "defaults": {
            "unit": "percentunit",
            "min": 0,
            "max": 1,
            "thresholds": {
                "mode": "absolute",
                "steps": [
                    {"color": "red", "value": null},
                    {"color": "red", "value": 0},           # < 0% budget (SLO breached)
                    {"color": "orange", "value": 0.1},      # < 10% alert
                    {"color": "yellow", "value": 0.5},      # < 50% caution
                    {"color": "green", "value": 1}           # >= 100% healthy
                ]
            }
        },
        "overrides": []
    },
    "targets": [{
        "expr": $query,
        "legendFormat": "Budget Remaining",
        "refId": "A"
    }]
}')

# Panel 3: Burn Rate (1h window)
burn_rate_fast_query="
  (
    sum(rate(${METRICS_PREFIX}_requests_total{status=~\"5..\"}[1h]))
    /
    sum(rate(${METRICS_PREFIX}_requests_total[1h]))
  ) / ${ERROR_BUDGET}
"

burn_rate_fast_panel=$(jq -n --arg query "$burn_rate_fast_query" '{
    "type": "timeseries",
    "title": "Burn Rate (1h window)",
    "gridPos": {"h": 5, "w": 6, "x": 6, "y": 1},
    "options": {
        "legend": {"calcs": ["max", "mean"], "displayMode": "table", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "none",
            "min": 0,
            "thresholds": {
                "mode": "absolute",
                "steps": [
                    {"color": "green", "value": null},
                    {"color": "green", "value": 0},
                    {"color": "yellow", "value": 3},
                    {"color": "orange", "value": 10},
                    {"color": "red", "value": 14.4}
                ]
            },
            "custom": {
                "lineInterpolation": "smooth",
                "showPoints": "never"
            }
        }
    },
    "targets": [{
        "expr": $query,
        "legendFormat": "Burn Rate (1h)",
        "refId": "A"
    }]
}')

# Panel 4: SLI Compliance (% good requests)
sli_compliance_query="
  sum(rate(${METRICS_PREFIX}_requests_total{status!~\"5..\"}[${RANGE_VECTOR}]))
  /
  sum(rate(${METRICS_PREFIX}_requests_total[${RANGE_VECTOR}]))
  * 100
"

sli_panel=$(jq -n --arg query "$sli_compliance_query" '{
    "type": "timeseries",
    "title": "SLI Compliance (%)",
    "gridPos": {"h": 5, "w": 6, "x": 12, "y": 1},
    "options": {
        "legend": {"calcs": ["mean", "min", "lastNotNull"], "displayMode": "table", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "percent",
            "min": 99,
            "max": 100,
            "thresholds": {
                "mode": "absolute",
                "steps": [
                    {"color": "red", "value": null},
                    {"color": "red", "value": 0},
                    {"color": "orange", "value": 99},
                    {"color": "green", "value": 99.95}
                ]
            },
            "custom": {"lineInterpolation": "smooth", "showPoints": "never"}
        }
    },
    "targets": [{
        "expr": $query,
        "legendFormat": "SLI",
        "refId": "A"
    }, {
        "expr": "100 - ${ERROR_BUDGET}",
        "legendFormat": "SLO Target",
        "refId": "B"
    }]
}')

# Panel 5: Request Volume + Error Rate
volume_rate_query="
  sum(rate(${METRICS_PREFIX}_requests_total[5m]))
"
error_rate_query="
  sum(rate(${METRICS_PREFIX}_requests_total{status=~\"5..\"}[5m]))
"

volume_panel=$(jq -n --arg vol "$volume_rate_query" --arg err "$error_rate_query" '{
    "type": "timeseries",
    "title": "Request Rate / Error Rate",
    "gridPos": {"h": 5, "w": 6, "x": 18, "y": 1},
    "options": {
        "legend": {"calcs": ["mean", "lastNotNull"], "displayMode": "table", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "reqps",
            "custom": {"lineInterpolation": "smooth", "showPoints": "never"}
        }
    },
    "targets": [
        {"expr": $vol, "legendFormat": "Requests/s", "refId": "A"},
        {"expr": $err, "legendFormat": "Errors/s", "refId": "B"}
    ]
}')

# Panel 6: Row — Latency Details
latency_row=$(jq -n '{
    "type": "row",
    "title": "Latency & Performance",
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 6}
}')

# Panel 7: Latency p50/p90/p99
latency_query_p50="
  histogram_quantile(0.50,
    sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket[5m])) by (le)
  )
"
latency_query_p90="
  histogram_quantile(0.90,
    sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket[5m])) by (le)
  )
"
latency_query_p99="
  histogram_quantile(0.99,
    sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket[5m])) by (le)
  )
"

latency_panel=$(jq -n --arg p50 "$latency_query_p50" --arg p90 "$latency_query_p90" --arg p99 "$latency_query_p99" '{
    "type": "timeseries",
    "title": "Latency p50 / p90 / p99",
    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 7},
    "options": {
        "legend": {"calcs": ["mean", "max"], "displayMode": "table", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "s",
            "custom": {"lineInterpolation": "smooth", "showPoints": "never"}
        }
    },
    "targets": [
        {"expr": $p50, "legendFormat": "p50", "refId": "A"},
        {"expr": $p90, "legendFormat": "p90", "refId": "B"},
        {"expr": $p99, "legendFormat": "p99", "refId": "C"}
    ]
}')

# Panel 8: Latency Heatmap / Distribution
distro_panel=$(jq -n '{
    "type": "timeseries",
    "title": "Latency Distribution",
    "gridPos": {"h": 6, "w": 12, "x": 12, "y": 7},
    "options": {
        "legend": {"displayMode": "hidden"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "reqps",
            "custom": {"fillOpacity": 30, "lineInterpolation": "smooth", "showPoints": "never"}
        }
    },
    "targets": [
        {"expr": "sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket{le=\"0.05\"}[5m]))", "legendFormat": "<50ms", "refId": "A"},
        {"expr": "sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket{le=\"0.1\"}[5m]))", "legendFormat": "<100ms", "refId": "B"},
        {"expr": "sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket{le=\"0.5\"}[5m]))", "legendFormat": "<500ms", "refId": "C"},
        {"expr": "sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket{le=\"1\"}[5m]))", "legendFormat": "<1s", "refId": "D"},
        {"expr": "sum(rate(${METRICS_PREFIX}_request_duration_seconds_bucket{le=\"+Inf\"}[5m]))", "legendFormat": "Total", "refId": "E"}
    ]
}')

# Panel 9: Row — Endpoint Details
endpoint_row=$(jq -n '{
    "type": "row",
    "title": "Per-Endpoint Breakdown",
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 13}
}')

# Panel 10: Top-N Error Endpoints Table
error_table_panel=$(jq -n '{
    "type": "table",
    "title": "Endpoints with Highest Error Rate",
    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 14},
    "options": {
        "footer": {"enablePagination": false},
        "sortBy": [{"displayName": "Error Rate", "desc": true}]
    },
    "fieldConfig": {
        "defaults": {
            "custom": {"align": "auto"}
        }
    },
    "targets": [{
        "expr": "topk(10, sum(rate(${METRICS_PREFIX}_requests_total{status=~\"5..\"}[5m])) by (endpoint) / sum(rate(${METRICS_PREFIX}_requests_total[5m])) by (endpoint))",
        "legendFormat": "{{endpoint}}",
        "refId": "A"
    }]
}')

# Panel 11: Endpoint Request Volume
endpoint_volume_panel=$(jq -n '{
    "type": "timeseries",
    "title": "Request Volume by Endpoint (Top 10)",
    "gridPos": {"h": 6, "w": 12, "x": 12, "y": 14},
    "options": {
        "legend": {"calcs": ["mean", "max"], "displayMode": "table", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
    },
    "fieldConfig": {
        "defaults": {
            "unit": "reqps",
            "custom": {"lineInterpolation": "smooth", "showPoints": "never"}
        }
    },
    "targets": [{
        "expr": "topk(10, sum(rate(${METRICS_PREFIX}_requests_total[5m])) by (endpoint))",
        "legendFormat": "{{endpoint}}",
        "refId": "A"
    }]
}')

# ─────────────────────────────────────────────
# Assemble the dashboard
# ─────────────────────────────────────────────
dashboard=$(jq -n \
    --arg title "$DASHBOARD_NAME" \
    --arg uid "$UID" \
    --arg version "$VERSION" \
    --argjson panel1 "$title_panel" \
    --argjson panel2 "$budget_panel" \
    --argjson panel3 "$burn_rate_fast_panel" \
    --argjson panel4 "$sli_panel" \
    --argjson panel5 "$volume_panel" \
    --argjson panel6 "$latency_row" \
    --argjson panel7 "$latency_panel" \
    --argjson panel8 "$distro_panel" \
    --argjson panel9 "$endpoint_row" \
    --argjson panel10 "$error_table_panel" \
    --argjson panel11 "$endpoint_volume_panel" \
    '{
        "dashboard": {
            "title": $title,
            "uid": $uid,
            "version": ($version | tonumber),
            "schemaVersion": 36,
            "timezone": "utc",
            "graphTooltip": 0,
            "panels": [$panel1, $panel2, $panel3, $panel4, $panel5, $panel6, $panel7, $panel8, $panel9, $panel10, $panel11],
            "refresh": "30s",
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "timepicker": {
                "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"],
                "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
            },
            "tags": ["slo", "observability", "generated"],
            "editable": true,
            "description": "SLO compliance dashboard for ${SLO_TARGET}% target over ${WINDOW}. Generated by observability-engineering skill on $(date +%Y-%m-%d)."
        },
        "overwrite": true
    }'
)

# Write output
echo "$dashboard" > "$OUTPUT_FILE"
echo ""
echo "Dashboard written to: $OUTPUT_FILE"
echo "File size: $(wc -c < "$OUTPUT_FILE") bytes"
echo ""
echo "Import this JSON into Grafana via:"
echo "  Grafana UI → Create → Import → Upload JSON file"
echo ""
echo "Or apply via Terraform:"
echo '  resource "grafana_dashboard" "slo" {'
echo '    config_json = file("'"$OUTPUT_FILE"'")'
echo '  }'