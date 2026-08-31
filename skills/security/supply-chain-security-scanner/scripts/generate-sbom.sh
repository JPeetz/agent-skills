#!/usr/bin/env bash
# generate-sbom.sh — Generate SPDX or CycloneDX Software Bill of Materials
# Part of the supply-chain-security-scanner skill.
# Uses Syft to generate SBOMs, with optional signing via cosign.
#
# Usage:
#   generate-sbom.sh                              # CycloneDX JSON (default)
#   generate-sbom.sh --format spdx                # SPDX tag-value format
#   generate-sbom.sh --format cyclonedx-json      # CycloneDX JSON
#   generate-sbom.sh --format spdx-json           # SPDX JSON
#   generate-sbom.sh --sign --key cosign.key      # Sign the SBOM with cosign
#   generate-sbom.sh --path /path/to/project      # Scan specific directory
#   generate-sbom.sh --image nginx:1.25          # Generate SBOM for container image
#   generate-sbom.sh --upload                    # Upload to Dependency-Track

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${PROJECT_PATH:-.}"
FORMAT="cyclonedx-json"
SIGN=false
SIGN_KEY=""
TARGET_IMAGE=""
UPLOAD=false
DT_URL="${DEPENDENCY_TRACK_URL:-}"
DT_API_KEY="${DEPENDENCY_TRACK_API_KEY:-}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# ─── Argument Parsing ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --format)
      FORMAT="$2"
      shift
      ;;
    --sign)
      SIGN=true
      ;;
    --key)
      SIGN_KEY="$2"
      shift
      ;;
    --path)
      PROJECT_PATH="$2"
      shift
      ;;
    --image)
      TARGET_IMAGE="$2"
      shift
      ;;
    --upload)
      UPLOAD=true
      ;;
    --help|-h)
      echo "Usage: generate-sbom.sh [OPTIONS]"
      echo ""
      echo "Generate an SBOM (Software Bill of Materials) for a project or container image."
      echo ""
      echo "Options:"
      echo "  --format FORMAT     Output format (default: cyclonedx-json)"
      echo "                      Options: cyclonedx-json, cyclonedx-xml, spdx-json, spdx-tag-value, spdx-tv, github-json"
      echo "  --sign              Sign the generated SBOM with cosign"
      echo "  --key KEY_PATH      Path to cosign private key (required with --sign)"
      echo "  --path PATH         Project directory (default: current dir)"
      echo "  --image IMAGE       Container image to generate SBOM for"
      echo "  --upload            Upload to OWASP Dependency-Track instance"
      echo "                      (set DEPENDENCY_TRACK_URL and DEPENDENCY_TRACK_API_KEY env vars)"
      echo "  --help, -h          Show this help"
      echo ""
      echo "Examples:"
      echo "  generate-sbom.sh                                    # Default CycloneDX JSON"
      echo "  generate-sbom.sh --format spdx-json                 # SPDX 2.3 JSON"
      echo "  generate-sbom.sh --sign --key ~/.cosign/cosign.key # Sign the SBOM"
      echo "  generate-sbom.sh --image ghcr.io/owner/app:v1      # Container image SBOM"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# ─── Validate Input ───────────────────────────────────────────────────────────

if [[ "$SIGN" == "true" ]] && [[ -z "$SIGN_KEY" ]]; then
  echo "[ERROR] --sign requires --key <path-to-cosign-private-key>"
  exit 1
fi

validate_format() {
  case "$FORMAT" in
    cyclonedx-json|cyclonedx-xml|spdx-json|spdx-tag-value|spdx-tv|github-json|syft-json)
      ;;
    *)
      echo "[ERROR] Unsupported format: $FORMAT"
      echo "  Supported: cyclonedx-json, cyclonedx-xml, spdx-json, spdx-tag-value, github-json, syft-json"
      exit 1
      ;;
  esac
}

# ─── Tool Detection ──────────────────────────────────────────────────────────

check_tools() {
  local missing=()

  command -v syft &>/dev/null || missing+=(syft)

  if [[ "$SIGN" == "true" ]]; then
    command -v cosign &>/dev/null || missing+=(cosign)
  fi

  if [[ "$UPLOAD" == "true" ]]; then
    command -v curl &>/dev/null || missing+=(curl)
    if [[ -z "$DT_URL" ]]; then
      echo "[ERROR] Upload requires DEPENDENCY_TRACK_URL environment variable"
      exit 1
    fi
    if [[ -z "$DT_API_KEY" ]]; then
      echo "[ERROR] Upload requires DEPENDENCY_TRACK_API_KEY environment variable"
      exit 1
    fi
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "[ERROR] Missing required tools: ${missing[*]}"
    echo ""
    echo "Installation:"
    for tool in "${missing[@]}"; do
      case "$tool" in
        syft)
          echo "  syft:   brew install syft"
          echo "          OR curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin"
          ;;
        cosign)
          echo "  cosign: brew install cosign"
          ;;
        curl)
          echo "  curl:   pre-installed on macOS/Linux"
          ;;
      esac
    done
    exit 1
  fi
}

# ─── Project Metadata Detection ──────────────────────────────────────────────

detect_metadata() {
  PROJECT_NAME="$(basename "$(readlink -f "$PROJECT_PATH" 2>/dev/null || realpath "$PROJECT_PATH" 2>/dev/null || echo "$PROJECT_PATH")")"

  # Attempt to detect version from common files
  PROJECT_VERSION="0.0.0"
  if [[ -f "$PROJECT_PATH/package.json" ]]; then
    PROJECT_VERSION=$(jq -r '.version // "0.0.0"' "$PROJECT_PATH/package.json" 2>/dev/null || echo "0.0.0")
  elif [[ -f "$PROJECT_PATH/pyproject.toml" ]]; then
    PROJECT_VERSION=$(grep -m1 '^version' "$PROJECT_PATH/pyproject.toml" | sed 's/version\s*=\s*"\([^"]*\)"/\1/' 2>/dev/null || echo "0.0.0")
  elif [[ -f "$PROJECT_PATH/Cargo.toml" ]]; then
    PROJECT_VERSION=$(grep -m1 '^version' "$PROJECT_PATH/Cargo.toml" | sed 's/version\s*=\s*"\([^"]*\)"/\1/' 2>/dev/null || echo "0.0.0")
  elif [[ -f "$PROJECT_PATH/setup.py" ]]; then
    PROJECT_VERSION=$(grep -m1 'version=' "$PROJECT_PATH/setup.py" | sed "s/.*version=['\"]\([^'\"]*\)['\"].*/\1/" 2>/dev/null || echo "0.0.0")
  fi

  echo "[INFO] Project: $PROJECT_NAME v$PROJECT_VERSION"
}

# ─── File Extension Mapping ──────────────────────────────────────────────────

get_extension() {
  case "$FORMAT" in
    cyclonedx-json)  echo "cdx.json" ;;
    cyclonedx-xml)   echo "cdx.xml" ;;
    spdx-json)       echo "spdx.json" ;;
    spdx-tag-value|spdx-tv) echo "spdx" ;;
    github-json)     echo "github.json" ;;
    syft-json)       echo "syft.json" ;;
    *)               echo "json" ;;
  esac
}

get_content_type() {
  case "$FORMAT" in
    cyclonedx-json) echo "application/vnd.cyclonedx+json" ;;
    cyclonedx-xml)  echo "application/vnd.cyclonedx+xml" ;;
    spdx-json)      echo "application/spdx+json" ;;
    *)              echo "application/json" ;;
  esac
}

# ─── Generate SBOM ────────────────────────────────────────────────────────────

generate_sbom() {
  local ext
  ext=$(get_extension)

  if [[ -n "$TARGET_IMAGE" ]]; then
    SBOM_FILE="sbom-image-$(echo "$TARGET_IMAGE" | tr '/:' '-')-${TIMESTAMP}.${ext}"
    echo "[INFO] Generating SBOM for image: $TARGET_IMAGE"
    syft "$TARGET_IMAGE" --output "$FORMAT" > "$SBOM_FILE"
  else
    SBOM_FILE="sbom-${PROJECT_NAME}-${PROJECT_VERSION}-${TIMESTAMP}.${ext}"
    echo "[INFO] Generating SBOM for: $PROJECT_PATH"
    echo "       Format: $FORMAT"
    syft dir:"$PROJECT_PATH" --output "$FORMAT" > "$SBOM_FILE"
  fi

  local size
  size=$(wc -c < "$SBOM_FILE" 2>/dev/null | tr -d ' ')

  echo "[OK]   SBOM generated: $SBOM_FILE ($size bytes)"
  echo "$SBOM_FILE"
}

# ─── Validate SBOM ────────────────────────────────────────────────────────────

validate_sbom() {
  local sbom_file="$1"
  echo "[INFO] Validating SBOM..."

  # Check for NTIA minimum elements (CycloneDX JSON)
  if [[ "$FORMAT" == "cyclonedx-json" ]] && command -v jq &>/dev/null; then
    local has_name has_version has_timestamp has_components
    has_name=$(jq -r '.metadata.component.name // empty' "$sbom_file" 2>/dev/null)
    has_version=$(jq -r '.metadata.component.version // empty' "$sbom_file" 2>/dev/null)
    has_timestamp=$(jq -r '.metadata.timestamp // empty' "$sbom_file" 2>/dev/null)
    has_components=$(jq -r '.components | length // 0' "$sbom_file" 2>/dev/null)

    if [[ -n "$has_name" ]]; then
      echo "  ✓ Component name: $has_name"
    else
      echo "  ✗ Missing: component name"
    fi

    if [[ -n "$has_version" ]]; then
      echo "  ✓ Component version: $has_version"
    else
      echo "  ✗ Missing: component version"
    fi

    if [[ -n "$has_timestamp" ]]; then
      echo "  ✓ Timestamp: $has_timestamp"
    else
      echo "  ✗ Missing: timestamp"
    fi

    echo "  ✓ Components found: $has_components"
  else
    echo "  (jq not available; skipping structural validation)"
  fi

  # Validate JSON syntax if applicable
  if [[ "$sbom_file" == *.json ]] || [[ "$FORMAT" == *json* ]]; then
    if command -v jq &>/dev/null; then
      if jq empty "$sbom_file" 2>/dev/null; then
        echo "  ✓ Valid JSON syntax"
      else
        echo "  ✗ Invalid JSON syntax!"
        return 1
      fi
    fi
  fi
}

# ─── Sign SBOM ────────────────────────────────────────────────────────────────

sign_sbom() {
  local sbom_file="$1"
  echo "[INFO] Signing SBOM with cosign..."

  if [[ ! -f "$SIGN_KEY" ]]; then
    echo "[ERROR] Cosign key not found: $SIGN_KEY"
    echo "  Generate one with: cosign generate-key-pair"
    exit 1
  fi

  cosign sign-blob --key "$SIGN_KEY" --output-signature "${sbom_file}.sig" --output-certificate "${sbom_file}.cert" "$sbom_file"

  echo "[OK]   SBOM signed: ${sbom_file}.sig"
  echo "[OK]   Certificate:  ${sbom_file}.cert"
}

# ─── Upload to Dependency-Track ───────────────────────────────────────────────

upload_to_dependency_track() {
  local sbom_file="$1"

  if [[ "$UPLOAD" != "true" ]]; then
    return 0
  fi

  echo "[INFO] Uploading SBOM to OWASP Dependency-Track..."
  echo "       URL: $DT_URL"

  local project_name="${PROJECT_NAME}"
  if [[ -n "$TARGET_IMAGE" ]]; then
    project_name="image-$(echo "$TARGET_IMAGE" | tr '/:' '-')"
  fi

  # Create or get project
  local project_uuid
  project_uuid=$(curl -s -X PUT "$DT_URL/api/v1/project" \
    -H "X-Api-Key: $DT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$project_name\",\"classifier\":\"APPLICATION\"}" | \
    jq -r '.uuid // empty' 2>/dev/null)

  if [[ -z "$project_uuid" ]]; then
    echo "[WARN] Could not create/find project in Dependency-Track. Trying upload anyway."
    project_uuid=""
  fi

  # Upload SBOM
  local upload_url="${DT_URL}/api/v1/bom"
  local response
  response=$(curl -s -w "\n%{http_code}" -X POST "$upload_url" \
    -H "X-Api-Key: $DT_API_KEY" \
    -F "autoCreate=true" \
    -F "projectName=${project_name}" \
    -F "bom=@${sbom_file}" 2>/dev/null)

  local http_code
  http_code=$(echo "$response" | tail -1)

  if [[ "$http_code" == "200" ]]; then
    echo "[OK]   SBOM uploaded successfully to Dependency-Track"
  else
    echo "[WARN] Upload returned HTTP $http_code"
    echo "  Verify DEPENDENCY_TRACK_URL and DEPENDENCY_TRACK_API_KEY."
    echo "  Response: ${response:0:500}"
  fi
}

# ─── Summary ──────────────────────────────────────────────────────────────────

print_summary() {
  local sbom_file="$1"
  echo ""
  echo "══════════════════════════════════════════════════════════════"
  echo "  SBOM Generation Complete"
  echo "══════════════════════════════════════════════════════════════"
  echo "  SBOM:     $sbom_file"
  echo "  Format:   $FORMAT"
  echo "  Project:  $PROJECT_NAME v$PROJECT_VERSION"
  [[ -n "$TARGET_IMAGE" ]] && echo "  Image:    $TARGET_IMAGE"
  [[ "$SIGN" == "true" ]] && echo "  Signed:   ${sbom_file}.sig"
  [[ "$UPLOAD" == "true" ]] && echo "  Upload:   Dependency-Track ($DT_URL)"
  echo ""
  echo "  Next steps:"
  echo "  1. Review the SBOM for completeness"
  echo "  2. Scan for vulnerabilities: grype sbom:$sbom_file"
  echo "  3. Commit SBOM to repository for audit trail"
  echo "  4. Attach SBOM to release artifacts"
  echo "══════════════════════════════════════════════════════════════"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
  validate_format
  check_tools
  detect_metadata

  echo ""

  local sbom_file
  sbom_file=$(generate_sbom)
  validate_sbom "$sbom_file"

  if [[ "$SIGN" == "true" ]]; then
    sign_sbom "$sbom_file"
  fi

  if [[ "$UPLOAD" == "true" ]]; then
    upload_to_dependency_track "$sbom_file"
  fi

  print_summary "$sbom_file"
}

main
