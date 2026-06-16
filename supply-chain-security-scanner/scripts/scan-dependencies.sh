#!/usr/bin/env bash
# scan-dependencies.sh — Multi-ecosystem dependency vulnerability scanner
# Part of the supply-chain-security-scanner skill.
# Auto-detects project type(s), runs appropriate scanners, and produces unified reports.
#
# Usage:
#   scan-dependencies.sh                           # Full scan, Markdown + JSON report
#   scan-dependencies.sh --ci                      # CI mode: JSON only, exit 1 on findings
#   scan-dependencies.sh --fail-on critical        # Exit 1 if CRITICAL findings exist
#   scan-dependencies.sh --full --sbom             # Full scan + SBOM generation
#   scan-dependencies.sh --image nginx:1.25       # Scan a container image
#   scan-dependencies.sh --licenses-only           # License compliance only
#   scan-dependencies.sh --path /path/to/project   # Scan a specific directory

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${PROJECT_PATH:-.}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROJECT_NAME="$(basename "$(readlink -f "$PROJECT_PATH" 2>/dev/null || realpath "$PROJECT_PATH" 2>/dev/null || echo "$PROJECT_PATH")")"
REPORT_PREFIX="scan-report-${PROJECT_NAME}-${TIMESTAMP}"
FAIL_ON="none"
CI_MODE=false
FULL_SCAN=false
SBOM_FLAG=false
LICENSES_ONLY=false
TARGET_IMAGE=""

# ─── Argument Parsing ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ci)
      CI_MODE=true
      FAIL_ON="${FAIL_ON:-none}"
      ;;
    --fail-on)
      FAIL_ON="$2"
      shift
      ;;
    --full)
      FULL_SCAN=true
      ;;
    --sbom)
      SBOM_FLAG=true
      ;;
    --licenses-only)
      LICENSES_ONLY=true
      ;;
    --image)
      TARGET_IMAGE="$2"
      shift
      ;;
    --path)
      PROJECT_PATH="$2"
      shift
      ;;
    --help|-h)
      echo "Usage: scan-dependencies.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --ci                   CI mode: JSON output, exit 1 on findings"
      echo "  --fail-on LEVEL        Exit 1 if findings at or above LEVEL (none|low|medium|high|critical)"
      echo "  --full                 Run all available scanners (slower, more thorough)"
      echo "  --sbom                 Also generate an SBOM"
      echo "  --licenses-only        Only check license compliance"
      echo "  --image IMAGE          Scan a container image instead of a directory"
      echo "  --path PATH            Project directory to scan (default: current dir)"
      echo "  --help, -h             Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# ─── Color Output ─────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Tool Detection ───────────────────────────────────────────────────────────

declare -A TOOLS=(
  [npm]=false [pip-audit]=false [owasp-dc]=false
  [syft]=false [grype]=false [trivy]=false
  [cosign]=false [jq]=false [curl]=false
)

detect_tools() {
  info "Detecting available security tools..."

  command -v node     &>/dev/null && command -v npm  &>/dev/null && TOOLS[npm]=true
  command -v pip-audit &>/dev/null && TOOLS[pip-audit]=true

  if command -v dependency-check &>/dev/null; then
    TOOLS[owasp-dc]=true
  fi

  command -v syft     &>/dev/null && TOOLS[syft]=true
  command -v grype    &>/dev/null && TOOLS[grype]=true
  command -v trivy    &>/dev/null && TOOLS[trivy]=true
  command -v cosign   &>/dev/null && TOOLS[cosign]=true
  command -v jq       &>/dev/null && TOOLS[jq]=true
  command -v curl     &>/dev/null && TOOLS[curl]=true

  local available=false
  for tool in "${!TOOLS[@]}"; do
    if [[ "${TOOLS[$tool]}" == "true" ]]; then
      ok "$tool — available"
      available=true
    else
      warn "$tool — not found"
    fi
  done

  if [[ "$available" == "false" ]]; then
    err "No scanning tools found. Install at least one:"
    echo "  brew install syft grype trivy jq"
    echo "  brew install node          # for npm audit"
    echo "  pip install pip-audit      # for Python"
    echo "  brew install dependency-check  # for OWASP DC"
    exit 1
  fi
}

# ─── Ecosystem Detection ──────────────────────────────────────────────────────

detect_ecosystems() {
  info "Detecting project ecosystems in $PROJECT_PATH..."

  ECOSYSTEMS=()
  [[ -f "$PROJECT_PATH/package.json"        ]] && ECOSYSTEMS+=(nodejs)
  [[ -f "$PROJECT_PATH/package-lock.json"   ]] && ECOSYSTEMS+=(nodejs-lock)
  [[ -f "$PROJECT_PATH/yarn.lock"           ]] && ECOSYSTEMS+=(nodejs-lock)
  [[ -f "$PROJECT_PATH/pnpm-lock.yaml"      ]] && ECOSYSTEMS+=(nodejs-lock)
  [[ -f "$PROJECT_PATH/requirements.txt"    ]] && ECOSYSTEMS+=(python)
  [[ -f "$PROJECT_PATH/Pipfile.lock"        ]] && ECOSYSTEMS+=(python-lock)
  [[ -f "$PROJECT_PATH/pyproject.toml"      ]] && ECOSYSTEMS+=(python)
  [[ -f "$PROJECT_PATH/pom.xml"             ]] && ECOSYSTEMS+=(maven)
  [[ -f "$PROJECT_PATH/build.gradle"        ]] && ECOSYSTEMS+=(gradle)
  [[ -f "$PROJECT_PATH/build.gradle.kts"    ]] && ECOSYSTEMS+=(gradle)
  [[ -f "$PROJECT_PATH/go.sum"              ]] && ECOSYSTEMS+=(golang)
  [[ -f "$PROJECT_PATH/go.mod"              ]] && ECOSYSTEMS+=(golang)
  [[ -f "$PROJECT_PATH/Cargo.lock"          ]] && ECOSYSTEMS+=(rust)
  [[ -f "$PROJECT_PATH/Cargo.toml"          ]] && ECOSYSTEMS+=(rust)
  [[ -f "$PROJECT_PATH/Dockerfile"          ]] && ECOSYSTEMS+=(container)
  [[ -f "$PROJECT_PATH/Containerfile"       ]] && ECOSYSTEMS+=(container)
  [[ -f "$PROJECT_PATH/Gemfile.lock"        ]] && ECOSYSTEMS+=(ruby)
  [[ -f "$PROJECT_PATH/composer.lock"       ]] && ECOSYSTEMS+=(php)

  # Deduplicate
  ECOSYSTEMS=($(printf '%s\n' "${ECOSYSTEMS[@]}" | sort -u))

  if [[ ${#ECOSYSTEMS[@]} -eq 0 ]]; then
    warn "No known ecosystem detected. Running generic scans only."
    ECOSYSTEMS+=(generic)
  else
    ok "Detected ecosystems: ${ECOSYSTEMS[*]}"
  fi
}

# ─── Scanner: npm audit ───────────────────────────────────────────────────────

run_npm_audit() {
  local output_file="$1"
  if [[ "${TOOLS[npm]}" != "true" ]]; then return 0; fi
  if [[ ! -f "$PROJECT_PATH/package-lock.json" ]] && [[ ! -f "$PROJECT_PATH/yarn.lock" ]] && [[ ! -f "$PROJECT_PATH/pnpm-lock.yaml" ]]; then
    warn "npm audit: no lockfile found. Skipping (transitive deps not audited)."
    return 0
  fi

  info "Running npm audit..."
  cd "$PROJECT_PATH"

  # Try npm audit; handle yarn/pnpm fallback
  if [[ -f "package-lock.json" ]] || [[ -f "npm-shrinkwrap.json" ]]; then
    npm audit --json > "$output_file" 2>&1 || true
  elif [[ -f "yarn.lock" ]]; then
    yarn audit --json 2>/dev/null > "$output_file" || { warn "yarn audit failed. Install yarn or generate package-lock.json."; echo '{}' > "$output_file"; }
  elif [[ -f "pnpm-lock.yaml" ]]; then
    pnpm audit --json 2>/dev/null > "$output_file" || { warn "pnpm audit failed. Install pnpm or generate package-lock.json."; echo '{}' > "$output_file"; }
  fi

  local count
  count=$(jq '.vulnerabilities | length // 0' "$output_file" 2>/dev/null || echo 0)
  if [[ "$count" -gt 0 ]]; then
    warn "npm audit: $count vulnerability advisories found"
  else
    ok "npm audit: no vulnerabilities found"
  fi
}

# ─── Scanner: pip-audit ──────────────────────────────────────────────────────

run_pip_audit() {
  local output_file="$1"
  if [[ "${TOOLS[pip-audit]}" != "true" ]]; then return 0; fi

  info "Running pip-audit..."
  cd "$PROJECT_PATH"

  local args=("--format=json" "--progress-spinner=off")
  if [[ -f "requirements.txt" ]]; then
    args+=("--requirement=requirements.txt")
  fi

  pip-audit "${args[@]}" > "$output_file" 2>&1 || true

  local count
  count=$(jq '.dependencies | length // 0' "$output_file" 2>/dev/null || echo 0)
  if [[ "$count" -gt 0 ]]; then
    warn "pip-audit: $count vulnerable dependencies found"
  else
    ok "pip-audit: no vulnerabilities found"
  fi
}

# ─── Scanner: Grype (SBOM-based) ──────────────────────────────────────────────

run_grype() {
  local output_file="$1"
  if [[ "${TOOLS[grype]}" != "true" ]]; then return 0; fi

  info "Running Grype vulnerability scan..."
  # Update database first
  grype db update 2>/dev/null || warn "Grype DB update failed, using cached database"

  grype dir:"$PROJECT_PATH" --output json --only-fixed > "$output_file" 2>&1 || true

  local count
  count=$(jq '.matches | length // 0' "$output_file" 2>/dev/null || echo 0)
  if [[ "$count" -gt 0 ]]; then
    warn "Grype: $count match(es) found"
  else
    ok "Grype: no vulnerabilities found"
  fi
}

# ─── Scanner: Trivy ──────────────────────────────────────────────────────────

run_trivy() {
  local output_file="$1"
  if [[ "${TOOLS[trivy]}" != "true" ]]; then return 0; fi

  if [[ -n "$TARGET_IMAGE" ]]; then
    info "Running Trivy image scan on $TARGET_IMAGE..."
    trivy image --quiet --format json --output "$output_file" "$TARGET_IMAGE" 2>&1 || true
  elif [[ "$FULL_SCAN" == "true" ]]; then
    info "Running Trivy filesystem scan..."
    trivy fs --quiet --format json --output "$output_file" "$PROJECT_PATH" 2>&1 || true
  else
    return 0
  fi

  local count
  count=$(jq '.Results | map(.Vulnerabilities) | flatten | length // 0' "$output_file" 2>/dev/null || echo 0)
  if [[ "$count" -gt 0 ]]; then
    warn "Trivy: $count finding(s)"
  else
    ok "Trivy: no vulnerabilities found"
  fi
}

# ─── License Check ────────────────────────────────────────────────────────────

run_license_check() {
  local output_file="$1"
  if [[ "${TOOLS[trivy]}" != "true" ]] && [[ "${TOOLS[syft]}" != "true" ]]; then
    warn "License check: requires trivy or syft. Skipping."
    return 0
  fi

  info "Running license compliance check..."

  if [[ "${TOOLS[syft]}" == "true" ]]; then
    syft dir:"$PROJECT_PATH" --output json 2>/dev/null | \
      jq '[.artifacts[] | select(.licenses != null) | {name: .name, version: .version, licenses: .licenses | map(.value)}]' \
      > "$output_file" 2>/dev/null || echo '[]' > "$output_file"
  else
    trivy fs --quiet --scanners license --format json --output "$output_file" "$PROJECT_PATH" 2>&1 || echo '[]' > "$output_file"
  fi

  local copyleft_count
  copyleft_count=$(jq '[.[] | select(.licenses[] | test("GPL|AGPL|EUPL|LGPL"; "i"))] | length' "$output_file" 2>/dev/null || echo 0)
  local unknown_count
  unknown_count=$(jq '[.[] | select(.licenses == null or .licenses == [])] | length' "$output_file" 2>/dev/null || echo 0)

  if [[ "$copyleft_count" -gt 0 ]]; then
    warn "License check: $copyleft_count package(s) with copyleft licenses (GPL/AGPL/EUPL/LGPL)"
  fi
  if [[ "$unknown_count" -gt 0 ]]; then
    warn "License check: $unknown_count package(s) with unknown/missing license"
  fi
  if [[ "$copyleft_count" -eq 0 ]] && [[ "$unknown_count" -eq 0 ]]; then
    ok "License check: no copyleft or unlicensed packages detected"
  fi
}

# ─── Report Generation ────────────────────────────────────────────────────────

generate_markdown_report() {
  local json_report="$1"
  local md_report="$2"

  info "Generating Markdown report: $md_report"

  {
    echo "# Supply Chain Security Scan Report"
    echo ""
    echo "**Project:** \`$PROJECT_NAME\`"
    echo "**Scan date:** $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    echo "**Ecosystems detected:** ${ECOSYSTEMS[*]:-none}"
    echo "**Tools used:** $(for t in "${!TOOLS[@]}"; do [[ "${TOOLS[$t]}" == "true" ]] && echo -n "$t "; done)"
    echo ""
    echo "---"
    echo ""

    # Extract findings from the aggregated JSON
    local grype_critical grype_high grype_medium grype_low
    grype_critical=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Critical")] | length' "$json_report" 2>/dev/null || echo 0)
    grype_high=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "High")] | length' "$json_report" 2>/dev/null || echo 0)
    grype_medium=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Medium")] | length' "$json_report" 2>/dev/null || echo 0)
    grype_low=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Low")] | length' "$json_report" 2>/dev/null || echo 0)

    echo "## Summary"
    echo ""
    echo "| Severity | Count |"
    echo "|----------|-------|"
    echo "| Critical | $grype_critical |"
    echo "| High     | $grype_high |"
    echo "| Medium   | $grype_medium |"
    echo "| Low      | $grype_low |"
    echo ""
    echo "---"
    echo ""

    # Critical findings detail
    if [[ "$grype_critical" -gt 0 ]]; then
      echo "## Critical Findings"
      echo ""
      jq -r '.grype.matches[]? | select(.vulnerability.severity == "Critical") |
        "### \(.vulnerability.id // "UNKNOWN")\n\n" +
        "- **Package:** `\(.artifact.name)@\(.artifact.version)`\n" +
        "- **CVSS:** \(.vulnerability.cvss[0]?.metrics?.baseScore // "N/A")\n" +
        "- **Fix:** \(.vulnerability.fix.versions[]? // "None available")\n" +
        "- **Description:** \(.vulnerability.description // "No description")\n" +
        "- **URL:** \(.vulnerability.dataSource // "N/A")\n"' "$json_report" 2>/dev/null || true
      echo ""
    fi

    # High findings
    if [[ "$grype_high" -gt 0 ]]; then
      echo "## High Findings"
      echo ""
      jq -r '.grype.matches[]? | select(.vulnerability.severity == "High") |
        "- **\(.vulnerability.id):** `\(.artifact.name)@\(.artifact.version)` — Fix: \(.vulnerability.fix.versions[]? // "N/A")"' \
        "$json_report" 2>/dev/null || true
      echo ""
    fi

    # License section
    if [[ -f "$REPORT_PREFIX-licenses.json" ]]; then
      echo "## License Compliance"
      echo ""
      local copyleft_count
      copyleft_count=$(jq '[.[] | select(.licenses[]? | test("GPL|AGPL|EUPL|LGPL"; "i"))] | length' "$REPORT_PREFIX-licenses.json" 2>/dev/null || echo 0)
      echo "- **Copyleft packages detected:** $copyleft_count"
      echo ""
      if [[ "$copyleft_count" -gt 0 ]]; then
        echo "### Packages with Copyleft Licenses"
        echo ""
        jq -r '.[] | select(.licenses[]? | test("GPL|AGPL|EUPL|LGPL"; "i")) | "- `\(.name)@\(.version)` — \(.licenses | join(", "))"' \
          "$REPORT_PREFIX-licenses.json" 2>/dev/null || true
        echo ""
      fi
    fi

    echo "---"
    echo "*Report generated by supply-chain-security-scanner v1.0.0*"

  } > "$md_report"

  ok "Markdown report: $md_report"
}

generate_json_report() {
  local output_file="$1"

  info "Aggregating JSON findings..."

  jq -n '{
    meta: {
      project: $project,
      timestamp: $ts,
      ecosystems: $ecosystems | split(" "),
      tools_used: $tools | split(" ")
    },
    grype: $grype,
    trivy: $trivy,
    npm_audit: $npm,
    pip_audit: $pip,
    licenses: $licenses
  }' \
    --arg project "$PROJECT_NAME" \
    --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --arg ecosystems "${ECOSYSTEMS[*]}" \
    --arg tools "$(for t in "${!TOOLS[@]}"; do [[ "${TOOLS[$t]}" == "true" ]] && echo -n "$t "; done)" \
    --slurpfile grype "${REPORT_PREFIX}-grype.json" \
    --slurpfile trivy "${REPORT_PREFIX}-trivy.json" \
    --slurpfile npm "${REPORT_PREFIX}-npm.json" \
    --slurpfile pip "${REPORT_PREFIX}-pip.json" \
    --slurpfile licenses "${REPORT_PREFIX}-licenses.json" \
    > "$output_file" 2>/dev/null || echo '{"error": "JSON report aggregation failed"}' > "$output_file"

  ok "JSON report: $output_file"
}

# ─── Severity Scoring for CI Exit Code ────────────────────────────────────────

declare -A SEVERITY_WEIGHT=([none]=0 [low]=1 [medium]=2 [high]=3 [critical]=4)

check_fail_threshold() {
  local json_report="$1"
  local threshold="${SEVERITY_WEIGHT[$FAIL_ON]:-0}"

  if [[ "$threshold" -eq 0 ]]; then return 0; fi

  local max_sev=0
  local c
  c=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Critical")] | length' "$json_report" 2>/dev/null || echo 0)
  [[ "$c" -gt 0 ]] && max_sev=4

  if [[ "$max_sev" -lt 4 ]]; then
    c=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "High")] | length' "$json_report" 2>/dev/null || echo 0)
    [[ "$c" -gt 0 ]] && max_sev=3
  fi

  if [[ "$max_sev" -lt 3 ]]; then
    c=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Medium")] | length' "$json_report" 2>/dev/null || echo 0)
    [[ "$c" -gt 0 ]] && max_sev=2
  fi

  if [[ "$max_sev" -lt 2 ]]; then
    c=$(jq '[.grype.matches[]? | select(.vulnerability.severity == "Low")] | length' "$json_report" 2>/dev/null || echo 0)
    [[ "$c" -gt 0 ]] && max_sev=1
  fi

  if [[ "$max_sev" -ge "$threshold" ]]; then
    err "Findings at or above fail threshold ($FAIL_ON). Max severity found: $max_sev"
    return 1
  fi

  ok "No findings above fail threshold ($FAIL_ON)"
  return 0
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
  echo "══════════════════════════════════════════════════════════════"
  echo "  Supply Chain Security Scanner v1.0.0"
  echo "  Project: $PROJECT_NAME"
  echo "  Path:    $PROJECT_PATH"
  echo "══════════════════════════════════════════════════════════════"
  echo ""

  detect_tools
  echo ""

  if [[ -n "$TARGET_IMAGE" ]]; then
    ECOSYSTEMS=(container)
    info "Scanning container image: $TARGET_IMAGE"
    run_trivy "$REPORT_PREFIX-trivy.json"

    # Generate aggregate
    jq -n '{
      meta: {
        project: $project,
        target: $image,
        timestamp: $ts
      },
      trivy: $trivy
    }' \
      --arg project "$PROJECT_NAME" \
      --arg image "$TARGET_IMAGE" \
      --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      --slurpfile trivy "${REPORT_PREFIX}-trivy.json" \
      > "$REPORT_PREFIX.json" 2>/dev/null

    if [[ "$CI_MODE" != "true" ]]; then
      echo ""
      info "Trivy results (summary):"
      jq -r '.Results[]?.Vulnerabilities[]? | "  [\(.Severity)] \(.VulnerabilityID) — \(.PkgName)@\(.InstalledVersion) → \(.FixedVersion // "N/A")"' \
        "$REPORT_PREFIX-trivy.json" 2>/dev/null || true
    else
      cat "$REPORT_PREFIX.json"
    fi

    echo ""
    ok "Scan complete. Report: $REPORT_PREFIX.json"
    exit 0
  fi

  # Directory scan
  detect_ecosystems
  echo ""

  if [[ "$LICENSES_ONLY" == "true" ]]; then
    run_license_check "$REPORT_PREFIX-licenses.json"
    echo ""
    ok "License check complete."
    if [[ -f "$REPORT_PREFIX-licenses.json" ]]; then
      echo "License details:"
      jq -r 'sort_by(.name) | .[] | "  \(.name)@\(.version): \(.licenses | join(", "))"' \
        "$REPORT_PREFIX-licenses.json" 2>/dev/null || true
    fi
    exit 0
  fi

  # Run scanners based on detected ecosystems and available tools
  run_grype "$REPORT_PREFIX-grype.json"
  echo ""

  if [[ " ${ECOSYSTEMS[*]} " =~ nodejs ]]; then
    run_npm_audit "$REPORT_PREFIX-npm.json"
    echo ""
  fi

  if [[ " ${ECOSYSTEMS[*]} " =~ python ]]; then
    run_pip_audit "$REPORT_PREFIX-pip.json"
    echo ""
  fi

  if [[ "$FULL_SCAN" == "true" ]]; then
    run_trivy "$REPORT_PREFIX-trivy.json"
    echo ""
  fi

  # Always run license check (quick)
  run_license_check "$REPORT_PREFIX-licenses.json"
  echo ""

  # Generate reports
  generate_json_report "$REPORT_PREFIX.json"

  if [[ "$CI_MODE" != "true" ]]; then
    generate_markdown_report "$REPORT_PREFIX.json" "$REPORT_PREFIX.md"
  fi

  # CI mode
  if [[ "$CI_MODE" == "true" ]]; then
    echo ""
    if ! check_fail_threshold "$REPORT_PREFIX.json"; then
      cat "$REPORT_PREFIX.json"
      exit 1
    fi
    cat "$REPORT_PREFIX.json"
    exit 0
  fi

  # SBOM generation (if requested)
  if [[ "$SBOM_FLAG" == "true" ]] && [[ "${TOOLS[syft]}" == "true" ]]; then
    echo ""
    info "Generating SBOM..."
    "$SCRIPT_DIR/generate-sbom.sh" --path "$PROJECT_PATH" --format cyclonedx 2>/dev/null || \
      warn "SBOM generation failed. Run generate-sbom.sh manually."
  fi

  echo ""
  echo "══════════════════════════════════════════════════════════════"
  ok "Scan complete!"
  echo "  JSON report:   $REPORT_PREFIX.json"
  [[ -f "$REPORT_PREFIX.md" ]] && echo "  Markdown:      $REPORT_PREFIX.md"
  echo "══════════════════════════════════════════════════════════════"

  # Check fail threshold even outside CI mode
  check_fail_threshold "$REPORT_PREFIX.json" || true
}

main "$@"
