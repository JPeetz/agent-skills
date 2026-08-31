#!/usr/bin/env bash
# =============================================================================
# security-scan-iac.sh — Run security scanners against IaC codebases
# =============================================================================
# Part of: Infrastructure as Code Guardian (Skill Foundry)
# Version: 1.0.0
#
# Auto-detects the IaC tool in a directory and runs the appropriate security
# scanners. Aggregates findings and produces a severity-ranked report.
#
# Supported scanners:
#   - Terraform:   tfsec, checkov, trivy config
#   - CloudFormation: cfn-nag, checkov
#   - Ansible:     ansible-lint (security rules), kics
#   - Bicep:       checkov (ARM/Bicep support)
#   - Pulumi:      checkov, Pulumi policy packs
#   - Universal:   gitleaks (secret detection), trufflehog (secrets)
#
# Usage:
#   ./security-scan-iac.sh [DIRECTORY] [OPTIONS]
#
# Options:
#   --tool TOOL         Force a specific tool
#   --secrets-only      Only run secret detection
#   --compliance FRAMEWORK  Filter by compliance framework (cis, soc2, pcidss, hipaa, iso27001)
#   --json              Output results as SARIF or JSON
#   --fail-on CRITICAL|HIGH|MEDIUM|LOW   Minimum severity to fail on (default: HIGH)
#   --quiet             Suppress informational output
#   -h, --help          Show this help
#
# Exit codes:
#   0 — No findings above threshold
#   1 — Findings above threshold detected
#   2 — No IaC files found
#   3 — Required scanners not installed
# =============================================================================

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ── Defaults ────────────────────────────────────────────────────────────────
TARGET_DIR="${1:-.}"
shift 2>/dev/null || true
FORCE_TOOL=""
SECRETS_ONLY=false
COMPLIANCE=""
JSON_OUTPUT=false
FAIL_ON="HIGH"
QUIET=false
TOTAL_CRITICAL=0
TOTAL_HIGH=0
TOTAL_MEDIUM=0
TOTAL_LOW=0
declare -A SCAN_RESULTS
declare -A FINDING_COUNTS

# ── Help ────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  head -38 "$0" | grep '^#' | sed 's/^# \?//'
  exit 0
fi

# ── Args ────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)          FORCE_TOOL="$2"; shift 2 ;;
    --secrets-only)  SECRETS_ONLY=true; shift ;;
    --compliance)    COMPLIANCE="$2"; shift 2 ;;
    --json)          JSON_OUTPUT=true; shift ;;
    --fail-on)       FAIL_ON="$2"; shift 2 ;;
    --quiet)         QUIET=true; shift ;;
    *)               TARGET_DIR="$1"; shift ;;
  esac
done

TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"
[[ -d "$TARGET_DIR" ]] || { echo -e "${RED}Error: $TARGET_DIR not found${NC}" >&2; exit 2; }

# ── Helpers ─────────────────────────────────────────────────────────────────
info()  { $QUIET || echo -e "${BLUE}[INFO]${NC}  $*"; }
pass()  { echo -e "  ${GREEN}✓${NC} $*"; }
fail()  { echo -e "  ${RED}✗${NC} $*"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $*"; }
header() { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }
finding() {
  local sev="$1"; local msg="$2"; local file="$3"; local line="${4:-}"
  local icon=""; local color=""
  case "$sev" in
    CRITICAL) icon="🔴"; color="$RED"; TOTAL_CRITICAL=$((TOTAL_CRITICAL + 1)) ;;
    HIGH)     icon="🟠"; color="$RED"; TOTAL_HIGH=$((TOTAL_HIGH + 1)) ;;
    MEDIUM)   icon="🟡"; color="$YELLOW"; TOTAL_MEDIUM=$((TOTAL_MEDIUM + 1)) ;;
    LOW)      icon="🟢"; color="$NC"; TOTAL_LOW=$((TOTAL_LOW + 1)) ;;
  esac
  echo -e "  $icon ${color}$sev${NC} — $msg"
  [[ -n "$file" ]] && echo -e "       ${file}${line:+:$line}"
}

# ── Scanner Checks ──────────────────────────────────────────────────────────
command_exists() { command -v "$1" &>/dev/null; }
has_any_scanner() {
  command_exists tfsec || command_exists checkov || command_exists trivy || \
  command_exists cfn_nag_scan || command_exists gitleaks || command_exists trufflehog
}
check_scanner_deps() {
  local missing=()
  command_exists gitleaks || missing+=("gitleaks")
  command_exists checkov || missing+=("checkov")
  if [[ ${#missing[@]} -gt 0 ]]; then
    warn "Recommended scanners missing: ${missing[*]}"
    echo "  Install: brew install gitleaks checkov"
    echo "  Or: pip install checkov && brew install gitleaks/tap/gitleaks"
  fi
}

# ── Universal Scans ─────────────────────────────────────────────────────────
scan_secrets() {
  header "Secret Detection"
  local found=0

  if command_exists gitleaks; then
    info "gitleaks detect..."
    local gitleaks_out
    if gitleaks_out=$(gitleaks detect --source "$TARGET_DIR" --no-git --verbose --exit-code 0 2>&1); then
      local count
      count=$(echo "$gitleaks_out" | grep -c 'leak' || true)
      if [[ "$count" -gt 0 ]]; then
        fail "gitleaks: $count potential secret(s) found"
        finding "CRITICAL" "Secrets detected in code (gitleaks)" "$TARGET_DIR"
        $JSON_OUTPUT || echo "$gitleaks_out" | grep 'leak' | head -10 | while read -r l; do
          echo "       $l"
        done
        found=1
      else
        pass "gitleaks: no secrets found"
      fi
    fi
  fi

  if command_exists trufflehog; then
    info "trufflehog filesystem..."
    local th_out
    if th_out=$(trufflehog filesystem "$TARGET_DIR" --no-update --no-verification --fail 2>&1 || true); then
      local th_count
      th_count=$(echo "$th_out" | grep -c 'Found verified result' || true)
      if [[ "$th_count" -gt 0 ]]; then
        fail "trufflehog: $th_count secret(s) found"
        finding "CRITICAL" "Secrets detected in code (trufflehog)" "$TARGET_DIR"
        found=1
      else
        pass "trufflehog: no verified secrets"
      fi
    fi
  fi

  # Fallback: basic grep for common secret patterns
  if ! command_exists gitleaks && ! command_exists trufflehog; then
    warn "gitleaks/trufflehog not installed — running basic grep scan"
    local patterns=(
      'AKIA[0-9A-Z]{16}'                     # AWS Access Key
      'sk-[a-zA-Z0-9]{32,}'                  # Stripe/OpenAI keys
      '-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----'
      'ghp_[a-zA-Z0-9]{36}'                  # GitHub PAT
      'xox[bpras]-[a-zA-Z0-9-]+'             # Slack tokens
    )
    local grep_found=0
    for pattern in "${patterns[@]}"; do
      local matches
      matches=$(grep -rnI "$pattern" "$TARGET_DIR" --include='*.tf' --include='*.ts' --include='*.py' --include='*.yaml' --include='*.yml' --include='*.json' --include='*.bicep' 2>/dev/null || true)
      if [[ -n "$matches" ]]; then
        echo "$matches" | while read -r line; do
          echo "       $line"
        done
        grep_found=$((grep_found + $(echo "$matches" | wc -l | tr -d ' ')))
      fi
    done
    if [[ "$grep_found" -gt 0 ]]; then
      fail "grep: $grep_found potential secrets(s) found"
      found=1
    else
      pass "grep (basic): no common secret patterns detected"
    fi
  fi

  return $found
}

# ── Terraform Security ──────────────────────────────────────────────────────
scan_terraform() {
  header "Terraform Security Scan"
  local found=0
  local compliance_arg=""

  [[ -n "$COMPLIANCE" ]] && compliance_arg="--framework $COMPLIANCE"

  # tfsec
  if command_exists tfsec; then
    info "Running tfsec..."
    local tfsec_out tfsec_rc
    set +e
    tfsec_out=$(tfsec "$TARGET_DIR" --no-color --format default $compliance_arg 2>&1)
    tfsec_rc=$?
    set -e
    local tfsec_count
    tfsec_count=$(echo "$tfsec_out" | grep -cE '\[(critical|high|warning)\]' || true)
    if [[ $tfsec_rc -ne 0 || "$tfsec_count" -gt 0 ]]; then
      fail "tfsec: $tfsec_count finding(s)"
      $JSON_OUTPUT || echo "$tfsec_out" | grep -E '\[(critical|high|warning)\]' | head -10 | while read -r l; do
        echo "       $l"
      done
      found=1
    else
      pass "tfsec: no findings"
    fi
  else
    warn "tfsec not installed (brew install tfsec)"
  fi

  # checkov
  if command_exists checkov; then
    info "Running checkov (Terraform checks)..."
    local ck_out ck_rc
    set +e
    ck_out=$(checkov -d "$TARGET_DIR" --quiet --compact $compliance_arg 2>&1)
    ck_rc=$?
    set -e
    local failed
    failed=$(echo "$ck_out" | grep -c 'FAILED' || true)
    if [[ $ck_rc -ne 0 || "$failed" -gt 0 ]]; then
      fail "checkov: $failed failed check(s)"
      $JSON_OUTPUT || echo "$ck_out" | grep 'FAILED' | head -10 | while read -r l; do
        echo "       $l"
      done
      found=1
    else
      pass "checkov: passed"
    fi
  fi

  # trivy
  if command_exists trivy; then
    info "Running trivy config..."
    local trivy_out trivy_rc
    set +e
    trivy_out=$(trivy config "$TARGET_DIR" --severity HIGH,CRITICAL --quiet 2>&1)
    trivy_rc=$?
    set -e
    if [[ $trivy_rc -ne 0 ]]; then
      local trivy_count
      trivy_count=$(echo "$trivy_out" | grep -cE 'HIGH|CRITICAL' || true)
      fail "trivy: $trivy_count HIGH/CRITICAL finding(s)"
      $JSON_OUTPUT || echo "$trivy_out" | head -20
      found=1
    else
      pass "trivy config: no HIGH/CRITICAL findings"
    fi
  fi

  return $found
}

# ── CloudFormation Security ─────────────────────────────────────────────────
scan_cloudformation() {
  header "CloudFormation Security Scan"
  local found=0

  if command_exists cfn_nag_scan; then
    local templates
    templates=$(find "$TARGET_DIR" -maxdepth 3 \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) -exec grep -l 'AWSTemplateFormatVersion\|"Resources"' {} \; 2>/dev/null)
    for t in $templates; do
      local rel="${t#$TARGET_DIR/}"
      info "cfn_nag: $rel"
      local nag_out nag_rc
      set +e
      nag_out=$(cfn_nag_scan --input-path "$t" --output-format txt 2>&1)
      nag_rc=$?
      set -e
      local nag_count
      nag_count=$(echo "$nag_out" | grep -cE '\| (FAIL|WARN)' || true)
      if [[ $nag_rc -ne 0 || "$nag_count" -gt 0 ]]; then
        fail "cfn_nag: $nag_count finding(s) in $rel"
        $JSON_OUTPUT || echo "$nag_out" | grep -E '\| (FAIL|WARN)' | head -10
        found=1
      else
        pass "cfn_nag: $rel — clean"
      fi
    done
    [[ -z "$templates" ]] && warn "No CloudFormation templates detected"
  else
    warn "cfn_nag_scan not installed (gem install cfn-nag)"
  fi

  # checkov also covers CloudFormation
  if command_exists checkov; then
    info "Running checkov (CloudFormation checks)..."
    local ck_out ck_rc
    set +e
    ck_out=$(checkov -d "$TARGET_DIR" --quiet --compact --framework cloudformation 2>&1 || true)
    ck_rc=$?
    set -e
    local failed
    failed=$(echo "$ck_out" | grep -c 'FAILED' || true)
    [[ "$failed" -gt 0 ]] && { fail "checkov (CFn): $failed failed check(s)"; found=1; } || pass "checkov (CFn): passed"
  fi

  return $found
}

# ── Pulumi Security ─────────────────────────────────────────────────────────
scan_pulumi() {
  header "Pulumi Security Scan"
  local found=0

  if command_exists checkov; then
    info "Running checkov (Pulumi/Python/TypeScript)..."
    local ck_out ck_rc
    set +e
    ck_out=$(checkov -d "$TARGET_DIR" --quiet --compact --framework terraform_plan 2>&1 || true)
    ck_rc=$?
    set -e
    local failed
    failed=$(echo "$ck_out" | grep -c 'FAILED' || true)
    [[ "$failed" -gt 0 ]] && { fail "checkov (Pulumi): $failed failed check(s)"; found=1; } || pass "checkov (Pulumi): passed"
  fi

  if command_exists pulumi; then
    if [[ -f "$TARGET_DIR/Pulumi.yaml" ]]; then
      info "Checking Pulumi policy pack..."
      if pulumi policy validate-config --cwd "$TARGET_DIR" 2>/dev/null; then
        pass "pulumi policy validate: passed"
      else
        warn "pulumi policy validation skipped (no policy pack configured)"
      fi
    fi
  fi

  return $found
}

# ── Ansible Security ────────────────────────────────────────────────────────
scan_ansible() {
  header "Ansible Security Scan"
  local found=0

  if command_exists ansible-lint; then
    info "Running ansible-lint with security profiles..."
    local lint_out lint_rc
    set +e
    lint_out=$(ansible-lint "$TARGET_DIR" --profile production --nocolor 2>&1)
    lint_rc=$?
    set -e
    if [[ $lint_rc -ne 0 ]]; then
      local lint_count
      lint_count=$(echo "$lint_out" | tail -3)
      fail "ansible-lint: findings detected"
      echo "$lint_out" | tail -5
      found=1
    else
      pass "ansible-lint (production profile): passed"
    fi
  fi

  if command_exists checkov; then
    info "Running checkov (Ansible checks)..."
    local ck_out ck_rc
    set +e
    ck_out=$(checkov -d "$TARGET_DIR" --quiet --compact --framework ansible 2>&1 || true)
    ck_rc=$?
    set -e
    local failed
    failed=$(echo "$ck_out" | grep -c 'FAILED' || true)
    [[ "$failed" -gt 0 ]] && { fail "checkov (Ansible): $failed failed check(s)"; found=1; } || pass "checkov (Ansible): passed"
  fi

  return $found
}

# ── Bicep Security ──────────────────────────────────────────────────────────
scan_bicep() {
  header "Bicep Security Scan"
  local found=0

  if command_exists checkov; then
    info "Running checkov (Bicep/ARM checks)..."
    local ck_out ck_rc
    set +e
    ck_out=$(checkov -d "$TARGET_DIR" --quiet --compact --framework bicep --framework arm 2>&1 || true)
    ck_rc=$?
    set -e
    local failed
    failed=$(echo "$ck_out" | grep -c 'FAILED' || true)
    [[ "$failed" -gt 0 ]] && { fail "checkov (Bicep): $failed failed check(s)"; found=1; } || pass "checkov (Bicep): passed"
  fi

  # Azure CLI best-practice analyzer
  if command_exists az; then
    local bicep_files
    bicep_files=$(find "$TARGET_DIR" -maxdepth 3 -name '*.bicep')
    for b in $bicep_files; do
      local rel="${b#$TARGET_DIR/}"
      local bpa_out bpa_rc
      set +e
      bpa_out=$(az bicep lint --file "$b" 2>&1)
      bpa_rc=$?
      set -e
      if echo "$bpa_out" | grep -qi 'error\|warning'; then
        warn "az bicep lint: $rel has warnings"
        echo "$bpa_out" | grep -i 'warning\|error' | head -5
      else
        pass "az bicep lint: $rel — clean"
      fi
    done
  fi

  return $found
}

# ── Detection ───────────────────────────────────────────────────────────────
detect_tools() {
  local tools=()
  find "$TARGET_DIR" -maxdepth 3 -name '*.tf' 2>/dev/null | head -1 > /dev/null && tools+=("terraform")
  find "$TARGET_DIR" -maxdepth 3 \( -name 'Pulumi.yaml' -o -name 'Pulumi.yml' \) 2>/dev/null | head -1 > /dev/null && tools+=("pulumi")
  find "$TARGET_DIR" -maxdepth 3 \( -name '*.template' -o -name '*.cfn.yaml' -o -name '*.cfn.json' \) 2>/dev/null | head -1 > /dev/null && tools+=("cloudformation")
  find "$TARGET_DIR" -maxdepth 3 \( -name 'site.yml' -o -name 'playbook.yml' \) 2>/dev/null | head -1 > /dev/null && tools+=("ansible")
  find "$TARGET_DIR" -maxdepth 3 -name '*.bicep' 2>/dev/null | head -1 > /dev/null && tools+=("bicep")
  echo "${tools[@]}"
}

# ── Main ────────────────────────────────────────────────────────────────────
echo -e "${BOLD}IaC Security Scan Report${NC}"
echo -e "Directory:  ${BLUE}$TARGET_DIR${NC}"
echo -e "Time:       $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo -e "Fail on:    ${RED}$FAIL_ON${NC}"
[[ -n "$COMPLIANCE" ]] && echo -e "Framework:  ${YELLOW}$COMPLIANCE${NC}"
echo ""

check_scanner_deps

# Always run secret scan (unless explicitly disabled by --tool)
if ! $SECRETS_ONLY; then
  # Determine tools
  if [[ -n "$FORCE_TOOL" ]]; then
    TOOLS=("$FORCE_TOOL")
    info "Forced tool: $FORCE_TOOL"
  else
    read -ra TOOLS <<< "$(detect_tools)"
  fi

  if [[ ${#TOOLS[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No IaC files detected${NC}"
    # Still run secrets scan
    scan_secrets || true
    exit 2
  fi

  info "Detected tools: ${TOOLS[*]}"

  # Always scan secrets
  scan_secrets || true

  # Tool-specific scans
  for tool in "${TOOLS[@]}"; do
    case "$tool" in
      terraform)      scan_terraform;      SCAN_RESULTS[terraform]=$? ;;
      pulumi)         scan_pulumi;         SCAN_RESULTS[pulumi]=$? ;;
      cloudformation) scan_cloudformation; SCAN_RESULTS[cloudformation]=$? ;;
      ansible)        scan_ansible;        SCAN_RESULTS[ansible]=$? ;;
      bicep)          scan_bicep;          SCAN_RESULTS[bicep]=$? ;;
    esac
  done
else
  scan_secrets || true
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}━━━ Findings Summary ━━━${NC}"
echo -e "  🔴 CRITICAL: $TOTAL_CRITICAL"
echo -e "  🟠 HIGH:     $TOTAL_HIGH"
echo -e "  🟡 MEDIUM:   $TOTAL_MEDIUM"
echo -e "  🟢 LOW:      $TOTAL_LOW"

# Determine exit code
EXIT_CODE=0
case "$FAIL_ON" in
  LOW)
    [[ $((TOTAL_CRITICAL + TOTAL_HIGH + TOTAL_MEDIUM + TOTAL_LOW)) -gt 0 ]] && EXIT_CODE=1
    ;;
  MEDIUM)
    [[ $((TOTAL_CRITICAL + TOTAL_HIGH + TOTAL_MEDIUM)) -gt 0 ]] && EXIT_CODE=1
    ;;
  HIGH)
    [[ $((TOTAL_CRITICAL + TOTAL_HIGH)) -gt 0 ]] && EXIT_CODE=1
    ;;
  CRITICAL)
    [[ $TOTAL_CRITICAL -gt 0 ]] && EXIT_CODE=1
    ;;
esac

if $JSON_OUTPUT; then
  cat <<JSONEOF
{
  "directory": "$TARGET_DIR",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "findings": {
    "critical": $TOTAL_CRITICAL,
    "high": $TOTAL_HIGH,
    "medium": $TOTAL_MEDIUM,
    "low": $TOTAL_LOW
  },
  "fail_on": "$FAIL_ON",
  "passed": $([[ $EXIT_CODE -eq 0 ]] && echo "true" || echo "false"),
  "compliance": "${COMPLIANCE:-none}"
}
JSONEOF
fi

if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "\n${GREEN}${BOLD}Security scan passed ✓${NC} — no findings above $FAIL_ON threshold"
else
  echo -e "\n${RED}${BOLD}Security scan failed ✗${NC} — findings above $FAIL_ON threshold"
  echo -e "Review findings and fix before proceeding to production deployment."
fi

exit $EXIT_CODE
