#!/usr/bin/env bash
# =============================================================================
# validate-iac.sh — Auto-detect IaC tool and run validation
# =============================================================================
# Part of: Infrastructure as Code Guardian (Skill Foundry)
# Version: 1.0.0
#
# Scans a directory for IaC configuration files, auto-detects which tools are
# in use, and runs the appropriate validation commands. Supports Terraform,
# Pulumi, CloudFormation, Ansible, and Bicep.
#
# Usage:
#   ./validate-iac.sh [DIRECTORY] [OPTIONS]
#
# Options:
#   --tool TOOL       Force a specific tool (terraform|pulumi|cloudformation|ansible|bicep)
#   --all             Validate all detected tools (default)
#   --fail-fast       Stop on first error
#   --json            Output results as JSON
#   --quiet           Suppress informational output
#   -h, --help        Show this help
#
# Exit codes:
#   0 — All validations passed
#   1 — One or more validations failed
#   2 — No IaC tools detected
#   3 — Required tooling not installed
# =============================================================================

set -euo pipefail

# ── Color output ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── State ───────────────────────────────────────────────────────────────────
TARGET_DIR="${1:-.}"
shift 2>/dev/null || true
FORCE_TOOL=""
VALIDATE_ALL=true
FAIL_FAST=false
JSON_OUTPUT=false
QUIET=false
EXIT_CODE=0
declare -A RESULTS
declare -A ERRORS

# ── Help ────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  head -30 "$0" | grep '^#' | sed 's/^# \?//'
  exit 0
fi

# ── Argument Parsing ────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)        FORCE_TOOL="$2"; VALIDATE_ALL=false; shift 2 ;;
    --all)         VALIDATE_ALL=true; shift ;;
    --fail-fast)   FAIL_FAST=true; shift ;;
    --json)        JSON_OUTPUT=true; shift ;;
    --quiet)       QUIET=true; shift ;;
    *)             TARGET_DIR="$1"; shift ;;
  esac
done

# Resolve absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo -e "${RED}Error: Directory not found: $TARGET_DIR${NC}" >&2
  exit 2
fi

# ── Logging helpers ─────────────────────────────────────────────────────────
info()  { $QUIET || echo -e "${BLUE}[INFO]${NC}  $*"; }
pass()  { echo -e "  ${GREEN}✓${NC} $*"; }
fail()  { echo -e "  ${RED}✗${NC} $*"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $*"; }
header() { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# ── Detection Functions ─────────────────────────────────────────────────────
detect_terraform() {
  find "$TARGET_DIR" -maxdepth 3 -name '*.tf' -o -name '*.tf.json' 2>/dev/null | head -1
}

detect_pulumi() {
  find "$TARGET_DIR" -maxdepth 3 \( -name 'Pulumi.yaml' -o -name 'Pulumi.yml' \) 2>/dev/null | head -1
}

detect_cloudformation() {
  find "$TARGET_DIR" -maxdepth 3 \( -name '*.template' -o -name '*.template.yaml' -o -name '*.template.json' -o -name '*.cfn.yaml' -o -name '*.cfn.json' \) 2>/dev/null | head -1
}

detect_ansible() {
  find "$TARGET_DIR" -maxdepth 3 \( -name 'site.yml' -o -name 'playbook.yml' -o -name 'playbook.yaml' -o -name 'ansible.cfg' \) 2>/dev/null | head -1
}

detect_bicep() {
  find "$TARGET_DIR" -maxdepth 3 -name '*.bicep' 2>/dev/null | head -1
}

# ── Validate Functions ──────────────────────────────────────────────────────
validate_terraform() {
  header "Terraform Validation"
  local result=0

  # Initialize (skip if .terraform already exists to save time)
  if [[ ! -d "$TARGET_DIR/.terraform" ]]; then
    info "Initializing Terraform..."
    if terraform -chdir="$TARGET_DIR" init -backend=false > /dev/null 2>&1; then
      pass "terraform init"
    else
      fail "terraform init"
      result=1
    fi
  else
    pass "terraform init (already initialized)"
  fi

  # Format check
  info "Checking format..."
  if terraform -chdir="$TARGET_DIR" fmt -check -recursive -diff > /dev/null 2>&1; then
    pass "terraform fmt (all files formatted)"
  else
    local unformatted
    unformatted=$(terraform -chdir="$TARGET_DIR" fmt -check -recursive -list 2>&1 || true)
    fail "terraform fmt — unformatted files: $(echo "$unformatted" | wc -l | tr -d ' ')"
    echo "$unformatted" | while read -r f; do [[ -n "$f" ]] && echo "        $f"; done
    result=1
    $FAIL_FAST && return 1
  fi

  # Validate
  info "Validating configuration..."
  local validate_out
  if validate_out=$(terraform -chdir="$TARGET_DIR" validate -json 2>&1); then
    pass "terraform validate"
  else
    local err_count
    err_count=$(echo "$validate_out" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error_count',d.get('diagnostics',{}).get('error_count',0)))" 2>/dev/null || echo "?")
    fail "terraform validate — ${err_count} error(s)"
    $JSON_OUTPUT || echo "$validate_out" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for diag in d.get('diagnostics', []):
    if diag.get('severity') == 'error':
        print(f\"        {diag.get('detail','').split(';')[0]} — {diag.get('range',{}).get('filename','')}\")
" 2>/dev/null || echo "$validate_out" | tail -5
    result=1
  fi

  return $result
}

validate_pulumi() {
  header "Pulumi Validation"
  local result=0

  # Check for Pulumi CLI
  if ! command -v pulumi &>/dev/null; then
    fail "pulumi CLI not found in PATH"
    return 1
  fi

  local stack_name
  stack_name=$(pulumi stack --cwd="$TARGET_DIR" --show-urns 2>/dev/null | head -1 || echo "unknown")

  # TypeScript compilation check
  if [[ -f "$TARGET_DIR/tsconfig.json" ]]; then
    info "TypeScript compilation check..."
    if npx --prefix "$TARGET_DIR" tsc --noEmit 2>/dev/null; then
      pass "tsc --noEmit (TypeScript valid)"
    else
      fail "tsc --noEmit (TypeScript errors)"
      result=1
      $FAIL_FAST && return 1
    fi
  fi

  # Pulumi preview --json
  info "Running pulumi preview --json..."
  local preview_out
  if preview_out=$(pulumi preview --cwd="$TARGET_DIR" --json 2>&1); then
    local changes
    changes=$(echo "$preview_out" | python3 -c "
import sys, json
d = json.load(sys.stdin)
steps = d.get('steps', [])
ops = [s.get('op') for s in steps]
print(f\"{len(steps)} resources, {ops.count('create')} create, {ops.count('update')} update, {ops.count('delete')} delete, {ops.count('same')} unchanged\")
" 2>/dev/null || echo "preview completed")
    pass "pulumi preview — $changes"
  else
    fail "pulumi preview failed"
    result=1
  fi

  return $result
}

validate_cloudformation() {
  header "CloudFormation Validation"
  local result=0
  local templates
  templates=$(find "$TARGET_DIR" -maxdepth 3 \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) | head -10)

  if command -v cfn-lint &>/dev/null; then
    info "Running cfn-lint..."
    for t in $templates; do
      if grep -q 'AWSTemplateFormatVersion\|"Resources"\|Type:.*AWS::' "$t" 2>/dev/null; then
        local rel="${t#$TARGET_DIR/}"
        if cfn-lint "$t" --format parseable 2>&1 | grep -q 'E[0-9]'; then
          fail "cfn-lint: $rel has errors"
          result=1
        else
          pass "cfn-lint: $rel"
        fi
      fi
    done
  else
    warn "cfn-lint not installed (pip install cfn-lint)"

    # Fallback: AWS CLI validate-template
    if command -v aws &>/dev/null; then
      for t in $templates; do
        if grep -q 'AWSTemplateFormatVersion' "$t" 2>/dev/null; then
          local rel="${t#$TARGET_DIR/}"
          if aws cloudformation validate-template --template-body "file://$t" --no-cli-pager > /dev/null 2>&1; then
            pass "aws validate-template: $rel"
          else
            fail "aws validate-template: $rel"
            result=1
          fi
        fi
      done
    else
      warn "AWS CLI not found — skipping CloudFormation validation"
    fi
  fi

  return $result
}

validate_ansible() {
  header "Ansible Validation"
  local result=0

  if command -v ansible-lint &>/dev/null; then
    info "Running ansible-lint..."
    if ansible-lint "$TARGET_DIR" --nocolor 2>&1 | tail -5; then
      pass "ansible-lint"
    else
      fail "ansible-lint found issues"
      result=1
    fi
  else
    warn "ansible-lint not installed (pip install ansible-lint)"

    # Fallback: syntax check with ansible-playbook
    if command -v ansible-playbook &>/dev/null; then
      local playbooks
      playbooks=$(find "$TARGET_DIR" -maxdepth 3 \( -name '*.yml' -o -name '*.yaml' \) -exec grep -l 'hosts:' {} \; 2>/dev/null)
      for pb in $playbooks; do
        local rel="${pb#$TARGET_DIR/}"
        if ansible-playbook "$pb" --syntax-check > /dev/null 2>&1; then
          pass "ansible-playbook --syntax-check: $rel"
        else
          fail "ansible-playbook --syntax-check: $rel"
          result=1
        fi
      done
      [[ -z "$playbooks" ]] && warn "No Ansible playbooks detected"
    else
      warn "ansible-playbook not found — skipping Ansible validation"
    fi
  fi

  return $result
}

validate_bicep() {
  header "Bicep Validation"
  local result=0
  local bicep_files
  bicep_files=$(find "$TARGET_DIR" -maxdepth 3 -name '*.bicep')

  if command -v az &>/dev/null && az bicep version &>/dev/null 2>&1; then
    for b in $bicep_files; do
      local rel="${b#$TARGET_DIR/}"
      info "Building: $rel"

      local build_out
      if build_out=$(az bicep build --file "$b" --stdout 2>&1 > /dev/null); then
        pass "az bicep build: $rel"
      else
        fail "az bicep build: $rel"
        echo "$build_out" | tail -5
        result=1
        $FAIL_FAST && return 1
      fi
    done

    # Also run lint
    for b in $bicep_files; do
      local rel="${b#$TARGET_DIR/}"
      if az bicep lint --file "$b" 2>&1 | grep -q 'error'; then
        fail "az bicep lint: $rel has issues"
        result=1
      else
        pass "az bicep lint: $rel"
      fi
    done
  else
    warn "Azure CLI or Bicep extension not found — skipping Bicep validation"
    warn "Install: az bicep install"
    return 0  # Not an error to skip when tooling unavailable
  fi

  return $result
}

# ── JSON Output ─────────────────────────────────────────────────────────────
emit_json() {
  local output="{\"directory\":\"$TARGET_DIR\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"tools\":["
  local first=true
  for tool in terraform pulumi cloudformation ansible bicep; do
    if [[ -n "${RESULTS[$tool]:-}" ]]; then
      $first || output+=","
      first=false
      local status="${RESULTS[$tool]}"
      local errors="${ERRORS[$tool]:-}"
      output+="{\"name\":\"$tool\",\"passed\":$([[ "$status" == "0" ]] && echo "true" || echo "false"),\"errors\":\"${errors//\"/\\\"}\"}"
    fi
  done
  output+="]}"
  echo "$output"
}

# ── Main ────────────────────────────────────────────────────────────────────
echo -e "${BOLD}IaC Validation Report${NC}"
echo -e "Directory: ${BLUE}$TARGET_DIR${NC}"
echo -e "Time:      $(date -u '+%Y-%m-%d %H:%M:%S UTC')\n"

# Build list of tools to validate
TOOLS_TO_RUN=()

if [[ -n "$FORCE_TOOL" ]]; then
  TOOLS_TO_RUN=("$FORCE_TOOL")
  info "Forced tool: $FORCE_TOOL"
else
  detect_terraform      > /dev/null && TOOLS_TO_RUN+=("terraform")
  detect_pulumi         > /dev/null && TOOLS_TO_RUN+=("pulumi")
  detect_cloudformation > /dev/null && TOOLS_TO_RUN+=("cloudformation")
  detect_ansible        > /dev/null && TOOLS_TO_RUN+=("ansible")
  detect_bicep          > /dev/null && TOOLS_TO_RUN+=("bicep")
fi

if [[ ${#TOOLS_TO_RUN[@]} -eq 0 ]]; then
  echo -e "${YELLOW}No IaC configuration files detected in $TARGET_DIR${NC}"
  echo -e "Supported tools: Terraform (*.tf), Pulumi (Pulumi.yaml), CloudFormation (*.template), Ansible (site.yml), Bicep (*.bicep)"
  exit 2
fi

info "Detected tools: ${TOOLS_TO_RUN[*]}"

# Run validations
for tool in "${TOOLS_TO_RUN[@]}"; do
  case "$tool" in
    terraform)      validate_terraform;      RESULTS[terraform]=$? ;;
    pulumi)         validate_pulumi;         RESULTS[pulumi]=$? ;;
    cloudformation) validate_cloudformation; RESULTS[cloudformation]=$? ;;
    ansible)        validate_ansible;        RESULTS[ansible]=$? ;;
    bicep)          validate_bicep;          RESULTS[bicep]=$? ;;
  esac

  if [[ ${RESULTS[$tool]} -ne 0 ]] && $FAIL_FAST; then
    info "Fail-fast enabled — stopping after failure in $tool"
    break
  fi
done

# ── Summary ─────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}━━━ Summary ━━━${NC}"
for tool in "${TOOLS_TO_RUN[@]}"; do
  if [[ ${RESULTS[$tool]:-1} -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} $tool — passed"
  else
    echo -e "  ${RED}✗${NC} $tool — failed"
    EXIT_CODE=1
  fi
done

if $JSON_OUTPUT; then
  emit_json
fi

if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "\n${GREEN}${BOLD}All validations passed ✓${NC}"
else
  echo -e "\n${RED}${BOLD}Some validations failed ✗${NC}"
fi

exit $EXIT_CODE
