#!/usr/bin/env bash
# verify-provenance.sh — Verify SLSA provenance and signature attestations
# Part of the supply-chain-security-scanner skill.
# Uses cosign and slsa-verifier to check build provenance for container images
# and build artifacts.
#
# Usage:
#   verify-provenance.sh --image <image>@<digest>                    # Verify container provenance
#   verify-provenance.sh --image <image>@<digest> --source <repo>    # With source validation
#   verify-provenance.sh --artifact <path> --provenance <url>        # Verify artifact provenance
#   verify-provenance.sh --image <image> --verify-signature-only     # Check signature only
#   verify-provenance.sh --policy policy.cue --image <image>@<digest> # Custom policy

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_FILE="provenance-report-${TIMESTAMP}.json"
FAIL_FAST=false
VERIFY_SIGNATURE_ONLY=false
STRICT=false

# cosign/slsa-verifier options
COSIGN_OPTS=""
SLSA_SOURCE_URI=""
SLSA_SOURCE_BRANCH=""
SLSA_BUILDER_ID=""
POLICY_FILE=""
TARGET_IMAGE=""
TARGET_ARTIFACT=""
PROVENANCE_PATH=""
PROVENANCE_URL=""

# ─── Color Output ─────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }

# ─── Argument Parsing ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image)
      TARGET_IMAGE="$2"
      shift
      ;;
    --artifact)
      TARGET_ARTIFACT="$2"
      shift
      ;;
    --provenance)
      PROVENANCE_PATH="$2"
      shift
      ;;
    --provenance-url)
      PROVENANCE_URL="$2"
      shift
      ;;
    --source)
      SLSA_SOURCE_URI="$2"
      shift
      ;;
    --branch)
      SLSA_SOURCE_BRANCH="$2"
      shift
      ;;
    --builder)
      SLSA_BUILDER_ID="$2"
      shift
      ;;
    --policy)
      POLICY_FILE="$2"
      shift
      ;;
    --verify-signature-only)
      VERIFY_SIGNATURE_ONLY=true
      ;;
    --strict)
      STRICT=true
      ;;
    --fail-fast)
      FAIL_FAST=true
      ;;
    --help|-h)
      echo "Usage: verify-provenance.sh [OPTIONS]"
      echo ""
      echo "Verify SLSA provenance and cryptographic signatures for container images"
      echo "and build artifacts."
      echo ""
      echo "Options:"
      echo "  --image IMAGE@DIGEST          Container image to verify (e.g., ghcr.io/owner/app@sha256:abc...)"
      echo "  --artifact PATH               File path to verify (requires --provenance or --provenance-url)"
      echo "  --provenance PATH             Path to local provenance attestation file (.intoto.jsonl)"
      echo "  --provenance-url URL          URL to download provenance attestation"
      echo "  --source URI                  Expected source repository (e.g., github.com/owner/repo)"
      echo "  --branch BRANCH               Expected source branch (e.g., main)"
      echo "  --builder ID                  Expected builder ID (e.g., https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v2.0.0)"
      echo "  --policy FILE                 CUE or Rego policy file for custom verification rules"
      echo "  --verify-signature-only       Only verify image signature, skip SLSA attestation checks"
      echo "  --strict                      Require provenance attestation (fail if none found)"
      echo "  --fail-fast                   Stop on first verification failure"
      echo "  --help, -h                    Show this help"
      echo ""
      echo "Examples:"
      echo "  verify-provenance.sh --image ghcr.io/owner/app@sha256:abc123"
      echo "  verify-provenance.sh --image ghcr.io/owner/app@sha256:abc123 --source github.com/owner/repo --branch main"
      echo "  verify-provenance.sh --artifact ./binary --provenance attestation.intoto.jsonl"
      echo "  verify-provenance.sh --image nginx:latest --verify-signature-only"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# ─── Validation ──────────────────────────────────────────────────────────────

if [[ -z "$TARGET_IMAGE" ]] && [[ -z "$TARGET_ARTIFACT" ]]; then
  err "Either --image or --artifact is required."
  echo "  Usage: verify-provenance.sh --image <image>@<digest>"
  echo "         verify-provenance.sh --artifact <path> --provenance <file>"
  exit 1
fi

if [[ -n "$TARGET_ARTIFACT" ]] && [[ -z "$PROVENANCE_PATH" ]] && [[ -z "$PROVENANCE_URL" ]]; then
  err "Artifact verification requires --provenance or --provenance-url."
  exit 1
fi

if [[ -n "$TARGET_IMAGE" ]]; then
  # Warn if no digest is specified (tag-based references are mutable)
  if [[ ! "$TARGET_IMAGE" =~ @sha256: ]]; then
    warn "Image reference does not include a digest (@sha256:...)."
    warn "Tag-based references are mutable and cannot be cryptographically verified."
    warn "Use: verify-provenance.sh --image <image>@sha256:<digest>"
    [[ "$STRICT" == "true" ]] && exit 1
  fi
fi

# ─── Tool Detection ──────────────────────────────────────────────────────────

check_tools() {
  local missing=()

  command -v cosign &>/dev/null || missing+=(cosign)

  if [[ "$VERIFY_SIGNATURE_ONLY" != "true" ]]; then
    command -v slsa-verifier &>/dev/null || missing+=(slsa-verifier)
  fi

  command -v jq &>/dev/null || missing+=(jq)

  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing required tools: ${missing[*]}"
    echo ""
    echo "Installation:"
    for tool in "${missing[@]}"; do
      case "$tool" in
        cosign)
          echo "  cosign:        brew install cosign"
          ;;
        slsa-verifier)
          echo "  slsa-verifier: go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest"
          ;;
        jq)
          echo "  jq:            brew install jq"
          ;;
      esac
    done
    exit 1
  fi

  info "All required tools available."
}

# ─── Verify Container Image Signature ────────────────────────────────────────

verify_image_signature() {
  local image="$1"
  local output_json="$2"
  local exit_code=0

  info "Verifying container image signature: $image"

  # Try keyless verification (default for most public images)
  if cosign verify \
    --output-file "$output_json" \
    "$image" 2>/tmp/cosign-verify-stderr; then
    ok "Image signature verified successfully (keyless / OIDC)"

    # Parse and display certificate information
    if [[ -f "$output_json" ]] && command -v jq &>/dev/null; then
      local issuer subject
      issuer=$(jq -r '.[0].certificateIssuer // "N/A"' "$output_json" 2>/dev/null)
      subject=$(jq -r '.[0].certificateSubject // "N/A"' "$output_json" 2>/dev/null)
      echo "  Issuer:  $issuer"
      echo "  Subject: $subject"
    fi
  else
    local stderr_msg
    stderr_msg=$(cat /tmp/cosign-verify-stderr 2>/dev/null || true)

    if echo "$stderr_msg" | grep -qi "no matching signatures"; then
      warn "No signatures found for $image"
      warn "  This image is unsigned. Its provenance cannot be verified."
      warn "  SLSA Level: 0 (no guarantees)"

      # Generate partial report for unsigned image
      jq -n '{
        status: "unsigned",
        image: $img,
        slsa_level: "0",
        timestamp: $ts,
        details: "No cryptographic signature found. The image lacks any provenance guarantees."
      }' --arg img "$image" --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > "$output_json"

      [[ "$STRICT" == "true" ]] && exit_code=1
    elif echo "$stderr_msg" | grep -qi "expired"; then
      fail "Signing certificate has expired for $image"
      exit_code=1
    else
      fail "Signature verification failed: ${stderr_msg:-unknown error}"
      exit_code=1
    fi
  fi

  return $exit_code
}

# ─── Verify SLSA Provenance ──────────────────────────────────────────────────

verify_slsa_provenance() {
  local image="$1"
  local output_json="$2"
  local exit_code=0

  info "Verifying SLSA provenance attestation: $image"

  local args=()
  args+=("--source-uri" "$SLSA_SOURCE_URI")

  if [[ -n "$SLSA_SOURCE_BRANCH" ]]; then
    args+=("--source-branch" "$SLSA_SOURCE_BRANCH")
  fi

  if [[ -n "$SLSA_BUILDER_ID" ]]; then
    args+=("--builder-id" "$SLSA_BUILDER_ID")
  fi

  if [[ -n "$POLICY_FILE" ]]; then
    args+=("--policy" "$POLICY_FILE")
  fi

  # Run slsa-verifier
  if slsa-verifier verify-image "$image" "${args[@]}" 2>/tmp/slsa-verify-stderr; then
    ok "SLSA provenance verified: $image"
    jq -n '{
      status: "verified",
      image: $img,
      source: $src,
      branch: $branch,
      builder: $builder,
      slsa_level: "2+",
      timestamp: $ts,
      details: "Provenance attestation verified. Source, branch, and builder match."
    }' \
      --arg img "$image" \
      --arg src "$SLSA_SOURCE_URI" \
      --arg branch "${SLSA_SOURCE_BRANCH:-unknown}" \
      --arg builder "${SLSA_BUILDER_ID:-unknown}" \
      --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > "$output_json"
  else
    local stderr_msg
    stderr_msg=$(cat /tmp/slsa-verify-stderr 2>/dev/null || true)

    if echo "$stderr_msg" | grep -qi "no attestation"; then
      fail "No SLSA provenance attestation found"
      warn "  The image is signed but has no build provenance attestation."
      warn "  SLSA Level: 1 (signed, but no attestation)"
      exit_code=1
    elif echo "$stderr_msg" | grep -qi "source.*mismatch"; then
      fail "Source repository mismatch"
      exit_code=1
    elif echo "$stderr_msg" | grep -qi "branch.*mismatch"; then
      fail "Source branch mismatch"
      exit_code=1
    elif echo "$stderr_msg" | grep -qi "builder.*mismatch"; then
      fail "Builder identity mismatch"
      exit_code=1
    else
      fail "SLSA verification failed: ${stderr_msg:-unknown error}"
      exit_code=1
    fi
  fi

  return $exit_code
}

# ─── Verify Artifact Provenance ──────────────────────────────────────────────

verify_artifact_provenance() {
  local artifact="$1"
  local provenance="$2"
  local output_json="$3"
  local exit_code=0

  info "Verifying artifact provenance: $artifact"

  local prov_path="$provenance"

  # Download provenance if URL provided
  if [[ "$provenance" =~ ^https?:// ]] || [[ -n "$PROVENANCE_URL" ]]; then
    local download_url="${PROVENANCE_URL:-$provenance}"
    prov_path="/tmp/provenance-${TIMESTAMP}.intoto.jsonl"
    info "Downloading provenance from: $download_url"
    curl -sSL -o "$prov_path" "$download_url" || {
      fail "Failed to download provenance from $download_url"
      return 1
    }
  fi

  if [[ ! -f "$artifact" ]]; then
    fail "Artifact not found: $artifact"
    return 1
  fi

  if [[ ! -f "$prov_path" ]]; then
    fail "Provenance file not found: $prov_path"
    return 1
  fi

  # Try cosign verify-blob first (for signed attestations)
  local cosign_ok=true
  cosign verify-blob \
    --signature "${prov_path}.sig" \
    --certificate "${prov_path}.cert" \
    "$artifact" 2>/dev/null || cosign_ok=false

  # Then try slsa-verifier for full SLSA chain
  local args=()
  if [[ -n "$SLSA_SOURCE_URI" ]]; then
    args+=("--source-uri" "$SLSA_SOURCE_URI")
  fi
  if [[ -n "$SLSA_SOURCE_BRANCH" ]]; then
    args+=("--source-branch" "$SLSA_SOURCE_BRANCH")
  fi

  if slsa-verifier verify-artifact "$artifact" \
    --provenance-path "$prov_path" \
    "${args[@]}" 2>/tmp/slsa-artifact-stderr; then
    ok "Artifact provenance verified: $artifact"

    jq -n '{
      status: "verified",
      artifact: $artifact,
      provenance: $prov,
      source: $src,
      branch: $branch,
      timestamp: $ts,
      details: "Artifact provenance verified. Build attestation is valid."
    }' \
      --arg artifact "$artifact" \
      --arg prov "$provenance" \
      --arg src "${SLSA_SOURCE_URI:-unknown}" \
      --arg branch "${SLSA_SOURCE_BRANCH:-unknown}" \
      --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > "$output_json"
  else
    local stderr_msg
    stderr_msg=$(cat /tmp/slsa-artifact-stderr 2>/dev/null || true)

    if [[ "$cosign_ok" == "true" ]]; then
      warn "SLSA full verification failed, but blob signature is valid"
      warn "  This may indicate an incomplete but partially-valid attestation."
    fi

    fail "Artifact provenance verification failed: ${stderr_msg:-unknown error}"
    exit_code=1
  fi

  return $exit_code
}

# ─── Generate Summary Report ─────────────────────────────────────────────────

generate_report() {
  local overall_status="$1"
  local image_result="$2"
  local slsa_result="$3"

  info "Generating verification report: $REPORT_FILE"

  jq -n '{
    report: {
      timestamp: $ts,
      overall_status: $status,
      target_image: $img,
      target_artifact: $artifact,
      verification_results: {
        signature: $sig_result,
        slsa_provenance: $slsa_result
      },
      recommendations: []
    }
  }' \
    --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --arg status "$overall_status" \
    --arg img "${TARGET_IMAGE:-N/A}" \
    --arg artifact "${TARGET_ARTIFACT:-N/A}" \
    --argjson sig_result "$(cat "$image_result" 2>/dev/null || echo '{}')" \
    --argjson slsa_result "$(cat "$slsa_result" 2>/dev/null || echo '{}')" \
    > "$REPORT_FILE" 2>/dev/null || echo '{"error":"report generation failed"}' > "$REPORT_FILE"

  ok "Report: $REPORT_FILE"
}

print_summary() {
  local overall_status="$1"

  echo ""
  echo "══════════════════════════════════════════════════════════════"
  echo "  Provenance Verification Report"
  echo "══════════════════════════════════════════════════════════════"
  [[ -n "$TARGET_IMAGE" ]]    && echo "  Image:       $TARGET_IMAGE"
  [[ -n "$TARGET_ARTIFACT" ]] && echo "  Artifact:    $TARGET_ARTIFACT"
  echo "  Status:      $overall_status"
  echo "  Report:      $REPORT_FILE"
  echo ""
  echo "  Interpretations:"
  echo "  - VERIFIED:     Cryptographic provenance confirmed"
  echo "  - SIGNED-ONLY:  Image signed, no build attestation (SLSA 1)"
  echo "  - UNSIGNED:     No signature, no provenance (SLSA 0)"
  echo "  - FAILED:       Verification attempted but failed"
  echo "══════════════════════════════════════════════════════════════"
}

# ─── Cleanup ─────────────────────────────────────────────────────────────────

cleanup() {
  rm -f /tmp/cosign-verify-stderr /tmp/slsa-verify-stderr /tmp/slsa-artifact-stderr
  # Don't remove downloaded provenance — user may need it
}

trap cleanup EXIT

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
  echo "══════════════════════════════════════════════════════════════"
  echo "  Provenance Verification v1.0.0"
  echo "══════════════════════════════════════════════════════════════"
  echo ""

  check_tools
  echo ""

  # ─── Image Verification ──────────────────────────────────────────────────

  if [[ -n "$TARGET_IMAGE" ]]; then
    local sig_result="/tmp/provenance-sig-${TIMESTAMP}.json"
    local slsa_result="/tmp/provenance-slsa-${TIMESTAMP}.json"
    local sig_exit=0
    local slsa_exit=0
    local overall_status="UNKNOWN"

    # Step 1: Verify signature
    verify_image_signature "$TARGET_IMAGE" "$sig_result" || sig_exit=$?
    echo ""

    if [[ "$VERIFY_SIGNATURE_ONLY" == "true" ]]; then
      generate_report "SIGNATURE_CHECK" "$sig_result" '{"status":"skipped"}'
      if [[ $sig_exit -eq 0 ]]; then
        print_summary "SIGNATURE_VERIFIED"
        exit 0
      else
        print_summary "SIGNATURE_FAILED"
        exit 1
      fi
    fi

    # Step 2: Verify SLSA provenance (if signature verified or strict mode)
    if [[ $sig_exit -eq 0 ]] || [[ "$STRICT" == "true" ]]; then
      verify_slsa_provenance "$TARGET_IMAGE" "$slsa_result" || slsa_exit=$?
      echo ""
    else
      echo '{"status":"skipped","reason":"signature_verification_failed"}' > "$slsa_result"
      slsa_exit=1
    fi

    # Determine overall status
    if [[ $sig_exit -eq 0 ]] && [[ $slsa_exit -eq 0 ]]; then
      overall_status="VERIFIED"
    elif [[ $sig_exit -eq 0 ]]; then
      overall_status="SIGNED_ONLY"
    else
      overall_status="UNSIGNED"
    fi

    generate_report "$overall_status" "$sig_result" "$slsa_result"
    print_summary "$overall_status"

    if [[ "$overall_status" == "VERIFIED" ]] || [[ "$overall_status" == "SIGNED_ONLY" ]]; then
      exit 0
    else
      exit 1
    fi
  fi

  # ─── Artifact Verification ────────────────────────────────────────────────

  if [[ -n "$TARGET_ARTIFACT" ]]; then
    local artifact_result="/tmp/provenance-artifact-${TIMESTAMP}.json"
    local artifact_exit=0

    local provenance_src="${PROVENANCE_PATH:-$PROVENANCE_URL}"

    verify_artifact_provenance "$TARGET_ARTIFACT" "$provenance_src" "$artifact_result" || artifact_exit=$?
    echo ""

    # Generate report
    jq -n '{
      report: {
        timestamp: $ts,
        overall_status: (if $exit == 0 then "VERIFIED" else "FAILED" end),
        target_artifact: $artifact,
        provenance: $prov,
        details: $details
      }
    }' \
      --arg ts "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      --argjson exit $artifact_exit \
      --arg artifact "$TARGET_ARTIFACT" \
      --arg prov "${PROVENANCE_PATH:-$PROVENANCE_URL}" \
      --argjson details "$(cat "$artifact_result" 2>/dev/null || echo '{}')" \
      > "$REPORT_FILE"

    echo "══════════════════════════════════════════════════════════════"
    echo "  Provenance Verification Report"
    echo "══════════════════════════════════════════════════════════════"
    echo "  Artifact:    $TARGET_ARTIFACT"
    echo "  Provenance:  ${PROVENANCE_PATH:-$PROVENANCE_URL}"
    echo "  Report:      $REPORT_FILE"
    echo "══════════════════════════════════════════════════════════════"

    exit $artifact_exit
  fi
}

main
