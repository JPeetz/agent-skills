#!/usr/bin/env bash
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6.0"]
# ///
#
# security-scan-k8s.sh — Scan Kubernetes YAML manifests for security violations
#
# Usage:
#   ./security-scan-k8s.sh <manifest.yaml> [--verbose] [--output json]
#   ./security-scan-k8s.sh ./deploy/ --html report.html
#
# Checks performed:
#   1. Privileged containers (CRITICAL)
#   2. Containers running as root (CRITICAL)
#   3. hostPath mounts (HIGH)
#   4. Missing securityContext (HIGH)
#   5. allowPrivilegeEscalation: true or unset (HIGH)
#   6. Capabilities not dropped to ALL (MEDIUM)
#   7. Missing resource limits (MEDIUM)
#   8. Missing resource requests (MEDIUM)
#   9. No readiness/liveness probes (LOW)
#  10. hostNetwork / hostPID / hostIPC enabled (CRITICAL)
#
# Prerequisites (optional, for enhanced scans):
#   - kubesec: brew install kubesec (or docker run)
#   - yq: brew install yq

set -euo pipefail

VERBOSE=false
OUTPUT_FORMAT="text"
REPORT_HTML=""
TARGET=""
KUBESEC_AVAILABLE=false
YQ_AVAILABLE=false

# Color codes for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

FAILURES=0
WARNINGS=0
PASSES=0

# -- Parse arguments -------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --output)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --html)
      REPORT_HTML="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 <manifest.yaml|directory> [--verbose] [--output json] [--html report.html]"
      echo ""
      echo "Scans Kubernetes YAML manifests for security violations."
      echo ""
      echo "Options:"
      echo "  --verbose, -v     Show detailed findings"
      echo "  --output FORMAT   Output format: text (default) or json"
      echo "  --html FILE       Generate HTML report"
      echo ""
      echo "Checks align with OWASP K8s Top 10, NSA/CISA, and CIS benchmarks."
      exit 0
      ;;
    -*)
      echo "ERROR: Unknown flag: $1" >&2
      exit 2
      ;;
    *)
      TARGET="$1"
      shift
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "ERROR: No manifest or directory specified." >&2
  echo "Usage: $0 <manifest.yaml|directory> [--verbose]" >&2
  exit 2
fi

# -- Check available tools -------------------------------------------
command -v kubesec &>/dev/null && KUBESEC_AVAILABLE=true || true
command -v yq &>/dev/null && YQ_AVAILABLE=true || true

if [[ "$YQ_AVAILABLE" == "false" ]]; then
  echo "[security-scan] WARNING: 'yq' not found. Some checks will be limited." >&2
  echo "[security-scan] Install: brew install yq" >&2
fi

# -- Report functions -------------------------------------------------
fail() {
  local check="$1"
  local detail="$2"
  local file="$3"
  ((FAILURES++))
  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    echo "{\"status\":\"FAIL\",\"check\":\"$check\",\"detail\":\"$detail\",\"file\":\"$file\"}"
  else
    echo -e "${RED}[FAIL]${NC} $check"
    echo "       File: $file"
    echo "       Detail: $detail"
    echo ""
  fi
}

warn() {
  local check="$1"
  local detail="$2"
  local file="$3"
  ((WARNINGS++))
  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    echo "{\"status\":\"WARN\",\"check\":\"$check\",\"detail\":\"$detail\",\"file\":\"$file\"}"
  else
    echo -e "${YELLOW}[WARN]${NC} $check"
    if [[ "$VERBOSE" == "true" ]]; then
      echo "       File: $file"
      echo "       Detail: $detail"
      echo ""
    fi
  fi
}

pass() {
  local check="$1"
  local file="$2"
  ((PASSES++))
  if [[ "$VERBOSE" == "true" ]]; then
    echo -e "${GREEN}[PASS]${NC} $check — $file"
  fi
}

# -- Collect YAML files ----------------------------------------------
collect_files() {
  local target="$1"
  local files=()

  if [[ -f "$target" ]]; then
    files+=("$target")
  elif [[ -d "$target" ]]; then
    while IFS= read -r -d '' f; do
      files+=("$f")
    done < <(find "$target" \( -name "*.yaml" -o -name "*.yml" \) -print0)
  else
    echo "ERROR: '$target' is not a file or directory." >&2
    exit 2
  fi

  printf '%s\0' "${files[@]}"
}

# -- Core checks ------------------------------------------------------
scan_file() {
  local file="$1"

  [[ "$VERBOSE" == "true" ]] && echo "--- Scanning: $file ---" >&2

  # Read the file content
  local content
  content=$(cat "$file")

  # Check 1: Privileged containers (CRITICAL)
  if echo "$content" | grep -q "privileged: true"; then
    fail "C01: Privileged Container" "Container has privileged: true — full host access. Remove immediately." "$file"
  else
    pass "C01: No Privileged Container" "$file"
  fi

  # Check 2: Running as root (CRITICAL)
  if echo "$content" | grep -q "runAsUser: 0"; then
    fail "C02: Running as Root" "Container explicitly set to run as root (UID 0)." "$file"
  elif echo "$content" | grep -q "runAsNonRoot: false"; then
    fail "C02: Running as Root" "runAsNonRoot explicitly set to false." "$file"
  else
    if echo "$content" | grep -q "runAsNonRoot: true"; then
      pass "C02: Non-Root User" "$file"
    else
      warn "C02: Non-Root Not Enforced" "runAsNonRoot is not explicitly set to true." "$file"
    fi
  fi

  # Check 3: hostPath mounts (HIGH)
  if echo "$content" | grep -q "hostPath:"; then
    hostpaths=$(echo "$content" | grep -A1 "hostPath:" | grep "path:" || true)
    fail "C03: hostPath Mount" "hostPath volume detected. Paths: $(echo "$hostpaths" | tr '\n' ' ')" "$file"
  else
    pass "C03: No hostPath" "$file"
  fi

  # Check 4: securityContext presence (HIGH)
  if echo "$content" | grep -q "securityContext:"; then
    pass "C04: securityContext Present" "$file"
  else
    fail "C04: Missing securityContext" "No securityContext defined for container. Apply PSS restricted profile." "$file"
  fi

  # Check 5: allowPrivilegeEscalation (HIGH)
  if echo "$content" | grep -q "allowPrivilegeEscalation: false"; then
    pass "C05: Privilege Escalation Disabled" "$file"
  elif echo "$content" | grep -q "allowPrivilegeEscalation: true"; then
    fail "C05: Privilege Escalation Allowed" "allowPrivilegeEscalation is explicitly true." "$file"
  else
    warn "C05: Privilege Escalation Not Set" "allowPrivilegeEscalation is not set. Default is true — set to false." "$file"
  fi

  # Check 6: Capabilities dropped (MEDIUM)
  if echo "$content" | grep -A5 "capabilities:" | grep -q "drop:"; then
    if echo "$content" | grep -A5 "capabilities:" | grep -q "ALL"; then
      pass "C06: ALL Capabilities Dropped" "$file"
    else
      warn "C06: Capabilities Partially Dropped" "Not all capabilities are dropped. Recommend drop: ['ALL']." "$file"
    fi
  else
    if echo "$content" | grep -q "capabilities:"; then
      warn "C06: Capabilities Not Dropped" "Capabilities section exists but no drop list. Add drop: ['ALL']." "$file"
    else
      warn "C06: Capabilities Not Configured" "No capabilities section. Add drop: ['ALL']." "$file"
    fi
  fi

  # Check 7: Resource limits (MEDIUM)
  if echo "$content" | grep -A10 "resources:" | grep -q "limits:"; then
    pass "C07: Resource Limits Set" "$file"
  else
    fail "C07: Missing Resource Limits" "No resource limits defined. Risk of resource starvation (FM-2)." "$file"
  fi

  # Check 8: Resource requests (MEDIUM)
  if echo "$content" | grep -A10 "resources:" | grep -q "requests:"; then
    pass "C08: Resource Requests Set" "$file"
  else
    fail "C08: Missing Resource Requests" "No resource requests defined. Scheduler cannot make informed decisions." "$file"
  fi

  # Check 9: Health probes (LOW)
  local has_readiness=false
  local has_liveness=false
  echo "$content" | grep -q "readinessProbe" && has_readiness=true
  echo "$content" | grep -q "livenessProbe" && has_liveness=true

  if [[ "$has_readiness" == "true" ]] && [[ "$has_liveness" == "true" ]]; then
    pass "C09: Health Probes" "$file"
  elif [[ "$has_readiness" == "true" ]]; then
    warn "C09: Missing livenessProbe" "readinessProbe exists but livenessProbe is missing." "$file"
  elif [[ "$has_liveness" == "true" ]]; then
    warn "C09: Missing readinessProbe" "livenessProbe exists but readinessProbe is missing." "$file"
  else
    warn "C09: No Health Probes" "Neither readinessProbe nor livenessProbe defined (FM-5)." "$file"
  fi

  # Check 10: hostNetwork/hostPID/hostIPC (CRITICAL)
  if echo "$content" | grep -q "hostNetwork: true"; then
    fail "C10: hostNetwork Enabled" "Pod uses host network namespace — bypasses NetworkPolicies." "$file"
  fi
  if echo "$content" | grep -q "hostPID: true"; then
    fail "C10: hostPID Enabled" "Pod shares host PID namespace — can see all processes." "$file"
  fi
  if echo "$content" | grep -q "hostIPC: true"; then
    fail "C10: hostIPC Enabled" "Pod shares host IPC namespace." "$file"
  fi
  if ! echo "$content" | grep -q "hostNetwork: true\|hostPID: true\|hostIPC: true"; then
    pass "C10: No Host Namespace Sharing" "$file"
  fi
}

# -- Kubesec integration (optional) -----------------------------------
run_kubesec() {
  local file="$1"
  echo "[security-scan] Running kubesec on: $file" >&2

  if command -v kubesec &>/dev/null; then
    kubesec scan "$file" 2>/dev/null || true
  elif command -v docker &>/dev/null; then
    docker run -i kubesec/kubesec:latest scan - < "$file" 2>/dev/null || true
  fi
}

# -- JSON summary -----------------------------------------------------
json_summary() {
  echo "{"
  echo "  \"summary\": {"
  echo "    \"total_files\": ${TOTAL_FILES},"
  echo "    \"failures\": ${FAILURES},"
  echo "    \"warnings\": ${WARNINGS},"
  echo "    \"passes\": ${PASSES},"
  echo "    \"passed\": $([[ $FAILURES -eq 0 ]] && echo "true" || echo "false")"
  echo "  }"
  echo "}"
}

# -- HTML Report -----------------------------------------------------
generate_html() {
  local output="$1"
  local pass_status="PASSED"
  [[ $FAILURES -gt 0 ]] && pass_status="FAILED"

  cat > "$output" <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kubernetes Security Scan Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; background: #f5f5f5; }
    h1 { color: #1a1a1a; border-bottom: 3px solid #2563eb; padding-bottom: 0.5rem; }
    .summary { background: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .pass { color: #16a34a; font-weight: bold; }
    .fail { color: #dc2626; font-weight: bold; }
    .warn { color: #d97706; font-weight: bold; }
    .check { border-left: 4px solid #2563eb; padding: 0.5rem 1rem; margin: 0.5rem 0; background: white; }
    .failure { border-left-color: #dc2626; background: #fef2f2; }
    .warning { border-left-color: #d97706; background: #fffbeb; }
    .success { border-left-color: #16a34a; background: #f0fdf4; }
    footer { margin-top: 2rem; font-size: 0.85rem; color: #666; }
  </style>
</head>
<body>
  <h1>🔒 Kubernetes Security Scan Report</h1>
  <div class="summary">
    <p><strong>Status:</strong> <span class="$([[ $FAILURES -gt 0 ]] && echo 'fail' || echo 'pass')">$pass_status</span></p>
    <p><strong>Target:</strong> $TARGET</p>
    <p><strong>Files Scanned:</strong> ${TOTAL_FILES}</p>
    <p><strong>Failures:</strong> <span class="fail">${FAILURES}</span></p>
    <p><strong>Warnings:</strong> <span class="warn">${WARNINGS}</span></p>
    <p><strong>Passes:</strong> <span class="pass">${PASSES}</span></p>
    <p><strong>Generated:</strong> $(date -u +"%Y-%m-%dT%H:%M:%SZ")</p>
  </div>
  <p>See terminal output for detailed per-file findings.</p>
  <footer>
    Generated by kubernetes-operations/scripts/security-scan-k8s.sh<br>
    Checks aligned with OWASP K8s Top 10, NSA/CISA, and CIS benchmarks.
  </footer>
</body>
</html>
HTMLEOF
  echo "[security-scan] HTML report written to: $output" >&2
}

# -- Main ------------------------------------------------------------
main() {
  echo "[security-scan] Starting security scan..." >&2
  echo "[security-scan] Target: $TARGET" >&2
  echo "[security-scan] Kubesec available: $KUBESEC_AVAILABLE" >&2
  echo "========================================" >&2
  echo "" >&2

  mapfile -d '' FILES < <(collect_files "$TARGET")
  TOTAL_FILES=${#FILES[@]}

  echo "[security-scan] Files found: ${TOTAL_FILES}" >&2
  echo "" >&2

  for f in "${FILES[@]}"; do
    scan_file "$f"

    if [[ "$KUBESEC_AVAILABLE" == "true" ]]; then
      run_kubesec "$f"
      echo "" >&2
    fi
  done

  echo "========================================" >&2
  echo "  SCAN SUMMARY" >&2
  echo "  Files: ${TOTAL_FILES}" >&2
  echo -e "  ${RED}Failures: ${FAILURES}${NC}" >&2
  echo -e "  ${YELLOW}Warnings: ${WARNINGS}${NC}" >&2
  echo -e "  ${GREEN}Passes: ${PASSES}${NC}" >&2
  echo "========================================" >&2

  if [[ -n "$REPORT_HTML" ]]; then
    generate_html "$REPORT_HTML"
  fi

  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    json_summary
  fi

  if [[ $FAILURES -gt 0 ]]; then
    echo "" >&2
    echo "⛔ SECURITY SCAN FAILED — ${FAILURES} critical/high issues found." >&2
    echo "   Address failures before deploying to production." >&2
    exit 1
  else
    echo "" >&2
    echo "✅ SECURITY SCAN PASSED" >&2
    exit 0
  fi
}

main