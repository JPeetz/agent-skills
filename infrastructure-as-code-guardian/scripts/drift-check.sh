#!/usr/bin/env bash
# =============================================================================
# drift-check.sh — Detect infrastructure drift across IaC tools
# =============================================================================
# Part of: Infrastructure as Code Guardian (Skill Foundry)
# Version: 1.0.0
#
# Runs drift detection commands for Terraform, Pulumi, CloudFormation, and
# Bicep. Returns a non-zero exit code when drift is detected so it can be
# used as a CI/CD gate or scheduled health check.
#
# Usage:
#   ./drift-check.sh [DIRECTORY] [OPTIONS]
#
# Options:
#   --tool TOOL         Force a specific tool (terraform|pulumi|cloudformation|bicep)
#   --stack STACK_NAME  CloudFormation stack name (required for CFn mode)
#   --json              Output results as JSON
#   --slack WEBHOOK     Post drift alert to Slack webhook URL
#   --auto-remediate    Attempt to reconcile drift automatically (Terraform only)
#   --fail-on-drift     Exit 1 if drift detected (default)
#   --warn-only         Exit 0 even if drift detected (report only)
#   --quiet             Suppress informational output
#   -h, --help          Show this help
#
# Exit codes:
#   0 — No drift detected (or --warn-only mode)
#   1 — Drift detected
#   2 — No IaC configuration found
#   3 — Tooling prerequisites not met
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
CFN_STACK_NAME=""
JSON_OUTPUT=false
SLACK_WEBHOOK=""
AUTO_REMEDIATE=false
FAIL_ON_DRIFT=true
WARN_ONLY=false
QUIET=false
DRIFT_DETECTED=false
DRIFT_DETAILS=""

# ── Help ────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  head -33 "$0" | grep '^#' | sed 's/^# \?//'
  exit 0
fi

# ── Args ────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)          FORCE_TOOL="$2"; shift 2 ;;
    --stack)         CFN_STACK_NAME="$2"; shift 2 ;;
    --json)          JSON_OUTPUT=true; shift ;;
    --slack)         SLACK_WEBHOOK="$2"; shift 2 ;;
    --auto-remediate) AUTO_REMEDIATE=true; shift ;;
    --fail-on-drift) FAIL_ON_DRIFT=true; WARN_ONLY=false; shift ;;
    --warn-only)     WARN_ONLY=true; FAIL_ON_DRIFT=false; shift ;;
    --quiet)         QUIET=true; shift ;;
    *)               TARGET_DIR="$1"; shift ;;
  esac
done

TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"
[[ -d "$TARGET_DIR" ]] || { echo -e "${RED}Error: $TARGET_DIR not found${NC}" >&2; exit 2; }

# ── Helpers ─────────────────────────────────────────────────────────────────
info()  { $QUIET || echo -e "${BLUE}[INFO]${NC}  $*"; }
pass()  { echo -e "  ${GREEN}✓${NC} $*"; }
drift() { echo -e "  ${RED}◈${NC} $*"; DRIFT_DETECTED=true; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $*"; }
header() { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

send_slack_alert() {
  if [[ -n "$SLACK_WEBHOOK" ]]; then
    local msg="{\"blocks\":[{\"type\":\"header\",\"text\":{\"type\":\"plain_text\",\"text\":\"🚨 Infrastructure Drift Detected\"}},{\"type\":\"section\",\"fields\":[{\"type\":\"mrkdwn\",\"text\":\"*Directory:*\\n$TARGET_DIR\"},{\"type\":\"mrkdwn\",\"text\":\"*Time:*\\n$(date -u '+%Y-%m-%d %H:%M:%S UTC')\"}]},{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"\\`\\`\\`$1\\`\\`\\`\"}}]}"
    curl -s -X POST -H 'Content-Type: application/json' -d "$msg" "$SLACK_WEBHOOK" > /dev/null 2>&1 || true
  fi
}

# ── Terraform Drift Detection ───────────────────────────────────────────────
check_terraform_drift() {
  header "Terraform Drift Detection"
  local result=0

  # Initialize
  info "Initializing Terraform backend..."
  if ! terraform -chdir="$TARGET_DIR" init -backend=true 2>&1 | tail -3; then
    warn "terraform init failed — may need backend credentials"
    return 1
  fi

  # Plan with detailed exit code
  info "Running terraform plan -detailed-exitcode..."
  local plan_out plan_rc
  set +e
  plan_out=$(terraform -chdir="$TARGET_DIR" plan -detailed-exitcode -out=/tmp/tfplan-drift-$$ 2>&1)
  plan_rc=$?
  set -e

  case $plan_rc in
    0)
      pass "terraform plan — no changes, infrastructure matches code"
      result=0
      ;;
    1)
      fail "terraform plan — error during planning"
      echo "$plan_out" | tail -20
      result=1
      ;;
    2)
      # Drift detected—there are changes
      info "terraform plan detected changes:"
      local changes
      changes=$(echo "$plan_out" | grep -E 'Plan:|to add|to change|to destroy' || echo "Changes detected")
      drift "terraform: drift detected"
      echo "$changes"
      DRIFT_DETAILS="$changes"

      # Extract resource-level changes
      echo "$plan_out" | grep -E '^[[:space:]]*[+#-]' | head -50 | while read -r line; do
        echo "       $line"
      done

      # Auto-remediate if requested
      if $AUTO_REMEDIATE; then
        info "Auto-remediating: applying terraform plan..."
        if terraform -chdir="$TARGET_DIR" apply -auto-approve /tmp/tfplan-drift-$$ 2>&1 | tail -10; then
          pass "terraform apply (auto-remediated drift)"
          result=1  # Still report that drift was found, even though it's fixed
        else
          fail "terraform apply failed during auto-remediation"
          result=1
        fi
      fi

      result=1
      ;;
  esac

  # Cleanup temp plan
  rm -f "/tmp/tfplan-drift-$$"

  return $result
}

# ── Pulumi Drift Detection ──────────────────────────────────────────────────
check_pulumi_drift() {
  header "Pulumi Drift Detection"
  local result=0

  if ! command -v pulumi &>/dev/null; then
    fail "pulumi CLI not found"
    return 1
  fi

  info "Running pulumi refresh --diff..."
  local ref_out ref_rc
  set +e
  ref_out=$(pulumi refresh --cwd="$TARGET_DIR" --diff --yes --suppress-outputs 2>&1)
  ref_rc=$?
  set -e

  if [[ $ref_rc -ne 0 ]]; then
    fail "pulumi refresh failed"
    echo "$ref_out" | tail -20
    return 1
  fi

  # Parse diff output for changes
  local changes
  changes=$(echo "$ref_out" | grep -E '^[[:space:]]*[+~-]' | head -50 || true)

  if [[ -n "$changes" ]]; then
    drift "pulumi: drift detected"
    echo "$changes" | while read -r line; do
      echo "       $line"
    done
    DRIFT_DETAILS="$changes"
    result=1
  else
    pass "pulumi refresh — no drift detected, state matches infrastructure"
    result=0
  fi

  return $result
}

# ── CloudFormation Drift Detection ──────────────────────────────────────────
check_cloudformation_drift() {
  header "CloudFormation Drift Detection"
  local result=0

  if [[ -z "$CFN_STACK_NAME" ]]; then
    # Try to auto-detect from directory
    CFN_STACK_NAME=$(basename "$TARGET_DIR" | sed 's/[^a-zA-Z0-9-]/-/g')
    info "No --stack provided, inferred: $CFN_STACK_NAME"
  fi

  if ! command -v aws &>/dev/null; then
    fail "AWS CLI not found"
    return 1
  fi

  # Start drift detection
  info "Initiating drift detection on stack: $CFN_STACK_NAME"
  local detect_id
  detect_id=$(aws cloudformation detect-stack-drift \
    --stack-name "$CFN_STACK_NAME" \
    --query 'StackDriftDetectionId' \
    --output text 2>&1)

  if [[ "$detect_id" == *"error"* || "$detect_id" == *"ValidationError"* ]]; then
    warn "Stack '$CFN_STACK_NAME' may not exist or is in a terminal state"
    echo "$detect_id"
    return 1
  fi

  info "Waiting for drift detection to complete (detection ID: $detect_id)..."
  local status
  while true; do
    status=$(aws cloudformation describe-stack-drift-detection-status \
      --stack-drift-detection-id "$detect_id" \
      --query 'DetectionStatus' \
      --output text 2>&1)
    case "$status" in
      DETECTION_COMPLETE) break ;;
      DETECTION_FAILED) fail "Drift detection failed"; return 1 ;;
      *) sleep 5 ;;
    esac
  done

  # Check stack drift status
  local stack_drift
  stack_drift=$(aws cloudformation describe-stack-drift-detection-status \
    --stack-drift-detection-id "$detect_id" \
    --query 'StackDriftStatus' \
    --output text 2>&1)

  if [[ "$stack_drift" == "DRIFTED" ]]; then
    drift "CloudFormation: stack $CFN_STACK_NAME is DRIFTED"
    # Get resource-level drifts
    local resource_drifts
    resource_drifts=$(aws cloudformation describe-stack-resource-drifts \
      --stack-name "$CFN_STACK_NAME" \
      --stack-resource-drift-status-filters MODIFIED DELETED \
      --query 'StackResourceDrifts[?ResourceType!=`null`].[LogicalResourceId,ResourceType,StackResourceDriftStatus,Difference]' \
      --output table 2>&1)
    echo "$resource_drifts"
    DRIFT_DETAILS="$resource_drifts"
    result=1
  elif [[ "$stack_drift" == "IN_SYNC" ]]; then
    pass "CloudFormation: stack $CFN_STACK_NAME is IN_SYNC"
    result=0
  else
    warn "CloudFormation: stack $CFN_STACK_NAME status: $stack_drift"
    result=0
  fi

  return $result
}

# ── Bicep / ARM Drift Detection ─────────────────────────────────────────────
check_bicep_drift() {
  header "Bicep / Azure Drift Detection"
  local result=0

  if ! command -v az &>/dev/null; then
    fail "Azure CLI not found"
    return 1
  fi

  # Find main.bicep or first .bicep file
  local bicep_file
  bicep_file=$(find "$TARGET_DIR" -maxdepth 2 -name 'main.bicep' -o -name '*.bicep' | head -1)

  if [[ -z "$bicep_file" ]]; then
    warn "No .bicep files found"
    return 0
  fi

  info "Running az deployment group what-if for: $(basename "$bicep_file")"

  # Try to determine resource group from context or convention
  local rg_name
  rg_name=$(grep -oP 'resourceGroupName:\s*["\x27]\K[^"\x27]+' "$bicep_file" 2>/dev/null | head -1 || echo "")
  [[ -z "$rg_name" ]] && rg_name=$(basename "$(dirname "$bicep_file")" 2>/dev/null || echo "iac-drift-check")

  info "Resource group: $rg_name"

  local whatif_out whatif_rc
  set +e
  whatif_out=$(az deployment group what-if \
    --resource-group "$rg_name" \
    --template-file "$bicep_file" \
    --query "changes[?changeType!='NoChange'].[changeType,resourceName]" \
    --output table 2>&1)
  whatif_rc=$?
  set -e

  if [[ $whatif_rc -ne 0 ]]; then
    warn "what-if deployment failed — resource group may not exist or auth issue"
    echo "$whatif_out" | tail -10
    return 0  # Don't fail if what-if can't run (may be first deploy)
  fi

  local changes
  changes=$(echo "$whatif_out" | grep -v -E '^(Result|---|$)' | wc -l | tr -d ' ')

  if [[ "$changes" -gt 0 ]]; then
    drift "Bicep: $changes resource change(s) detected"
    echo "$whatif_out"
    DRIFT_DETAILS="$whatif_out"
    result=1
  else
    pass "Bicep: no drift detected — infrastructure matches template"
    result=0
  fi

  return $result
}

# ── Ansible Drift (configuration drift) ─────────────────────────────────────
check_ansible_drift() {
  header "Ansible Configuration Drift"
  local result=0

  if ! command -v ansible-playbook &>/dev/null; then
    fail "ansible-playbook not found"
    return 1
  fi

  # Find playbooks
  local playbooks
  playbooks=$(find "$TARGET_DIR" -maxdepth 2 \( -name 'site.yml' -o -name 'playbook.yml' -o -name 'playbook.yaml' \) | head -1)

  if [[ -z "$playbooks" ]]; then
    warn "No Ansible playbooks found"
    return 0
  fi

  info "Running ansible-playbook --check --diff for drift detection..."
  local check_out check_rc
  set +e
  check_out=$(ansible-playbook "$playbooks" --check --diff 2>&1)
  check_rc=$?
  set -e

  # Count changed tasks
  local changed
  changed=$(echo "$check_out" | grep -c 'changed=' || true)

  if [[ "$changed" -gt 0 ]]; then
    drift "Ansible: $changed task(s) would change — indicates configuration drift"
    echo "$check_out" | grep -E 'changed=|TASK|diff|CHANGED' | head -30
    DRIFT_DETAILS="$check_out"
    result=1
  else
    pass "Ansible: no configuration drift — all tasks idempotent"
    result=0
  fi

  return $result
}

# ── Detection ───────────────────────────────────────────────────────────────
detect_tool() {
  find "$TARGET_DIR" -maxdepth 3 -name '*.tf' 2>/dev/null | head -1 > /dev/null && { echo "terraform"; return; }
  find "$TARGET_DIR" -maxdepth 3 \( -name 'Pulumi.yaml' -o -name 'Pulumi.yml' \) 2>/dev/null | head -1 > /dev/null && { echo "pulumi"; return; }
  find "$TARGET_DIR" -maxdepth 3 \( -name '*.template' -o -name '*.cfn.yaml' -o -name '*.cfn.json' \) 2>/dev/null | head -1 > /dev/null && { echo "cloudformation"; return; }
  find "$TARGET_DIR" -maxdepth 3 -name '*.bicep' 2>/dev/null | head -1 > /dev/null && { echo "bicep"; return; }
  find "$TARGET_DIR" -maxdepth 3 \( -name 'site.yml' -o -name 'playbook.yml' \) 2>/dev/null | head -1 > /dev/null && { echo "ansible"; return; }
  echo ""
}

# ── Main ────────────────────────────────────────────────────────────────────
echo -e "${BOLD}IaC Drift Detection Report${NC}"
echo -e "Directory:  ${BLUE}$TARGET_DIR${NC}"
echo -e "Time:       $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo -e "Mode:       $($AUTO_REMEDIATE && echo 'Auto-remediate' || echo 'Detect only')"
echo ""

# Determine tool
TOOL="${FORCE_TOOL:-$(detect_tool)}"

if [[ -z "$TOOL" ]]; then
  echo -e "${YELLOW}No IaC configuration files detected in $TARGET_DIR${NC}"
  exit 2
fi

info "Detected tool: $TOOL"

# Run drift check
DRIFT_EXIT=0
case "$TOOL" in
  terraform)      check_terraform_drift;      DRIFT_EXIT=$? ;;
  pulumi)         check_pulumi_drift;         DRIFT_EXIT=$? ;;
  cloudformation) check_cloudformation_drift; DRIFT_EXIT=$? ;;
  bicep)          check_bicep_drift;          DRIFT_EXIT=$? ;;
  ansible)        check_ansible_drift;        DRIFT_EXIT=$? ;;
  *)
    echo -e "${RED}Unknown tool: $TOOL${NC}" >&2
    exit 2
    ;;
esac

# ── Summary ─────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}━━━ Drift Status ━━━${NC}"

if $DRIFT_DETECTED; then
  echo -e "  ${RED}◈ DRIFT DETECTED${NC} — Infrastructure state differs from code"

  if [[ -n "$SLACK_WEBHOOK" ]]; then
    info "Sending Slack alert..."
    send_slack_alert "$DRIFT_DETAILS"
  fi

  if $JSON_OUTPUT; then
    cat <<JSONEOF
{
  "directory": "$TARGET_DIR",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tool": "$TOOL",
  "drift_detected": true,
  "details": "$(echo "$DRIFT_DETAILS" | head -5 | tr '\n' ' ' | sed 's/"/\\"/g')"
}
JSONEOF
  fi

  if $WARN_ONLY; then
    echo -e "\n${YELLOW}⚠ Drift detected but --warn-only mode — exiting 0${NC}"
    exit 0
  fi

  exit 1
else
  echo -e "  ${GREEN}✓ IN SYNC${NC} — Infrastructure matches code definitions"

  if $JSON_OUTPUT; then
    cat <<JSONEOF
{
  "directory": "$TARGET_DIR",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tool": "$TOOL",
  "drift_detected": false,
  "details": "infrastructure matches code"
}
JSONEOF
  fi

  exit 0
fi
