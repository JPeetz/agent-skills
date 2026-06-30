#!/usr/bin/env bash
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6.0"]
# ///
#
# validate-k8s-manifest.sh — Validate Kubernetes YAML manifests against schema
#
# Usage:
#   ./validate-k8s-manifest.sh <manifest.yaml> [--strict] [--k8s-version 1.30]
#   ./validate-k8s-manifest.sh ./deploy/                     # validate directory
#   ./validate-k8s-manifest.sh <manifest.yaml> --output json  # JSON output
#
# Prerequisites (one of):
#   - kubeconform (recommended, fast Go binary): brew install kubeconform
#   - kubeval (legacy): brew install kubeval
#   - kubectl with --dry-run=server (fallback)
#
# This script is referenced by the kubernetes-operations skill.

set -euo pipefail

K8S_VERSION="${K8S_VERSION:-1.30}"
STRICT=false
OUTPUT_FORMAT="text"
MANIFEST=""
VALIDATOR=""

# -- Parse arguments -------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      STRICT=true
      shift
      ;;
    --k8s-version)
      K8S_VERSION="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 <manifest.yaml|directory> [--strict] [--k8s-version 1.30] [--output json|text]"
      echo ""
      echo "Validates Kubernetes YAML manifests against official schemas."
      echo ""
      echo "Options:"
      echo "  --strict          Treat warnings as errors"
      echo "  --k8s-version     Target Kubernetes version (default: 1.30)"
      echo "  --output          Output format: text (default) or json"
      echo ""
      echo "Supported validators (auto-detected):"
      echo "  kubeconform   — Preferred. Fast, actively maintained."
      echo "  kubeval       — Legacy validator."
      echo "  kubectl       — Fallback using --dry-run=server."
      exit 0
      ;;
    -*)
      echo "ERROR: Unknown flag: $1" >&2
      exit 2
      ;;
    *)
      MANIFEST="$1"
      shift
      ;;
  esac
done

if [[ -z "$MANIFEST" ]]; then
  echo "ERROR: No manifest or directory specified." >&2
  echo "Usage: $0 <manifest.yaml|directory> [--strict] [--k8s-version $K8S_VERSION]" >&2
  exit 2
fi

# -- Detect validator ------------------------------------------------
detect_validator() {
  if command -v kubeconform &>/dev/null; then
    VALIDATOR="kubeconform"
  elif command -v kubeval &>/dev/null; then
    VALIDATOR="kubeval"
  elif command -v kubectl &>/dev/null; then
    VALIDATOR="kubectl"
  else
    echo "ERROR: No validator found. Install one of:" >&2
    echo "  brew install kubeconform   # recommended" >&2
    echo "  brew install kubeval       # legacy" >&2
    echo "  or ensure kubectl is configured and cluster is reachable" >&2
    exit 1
  fi
  echo "[validate-k8s] Using validator: $VALIDATOR" >&2
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

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "ERROR: No YAML files found in '$target'." >&2
    exit 2
  fi

  printf '%s\0' "${files[@]}"
}

# -- Validate with kubeconform ---------------------------------------
run_kubeconform() {
  local files=("$@")
  local exit_code=0
  local kubeconform_args=(
    "-schema-location" "default"
    "-schema-location" "https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/v${K8S_VERSION}-standalone-strict/{{.ResourceKind}}-{{.KindSuffix}}.json"
    "-kubernetes-version" "${K8S_VERSION}"
    "-summary"
  )

  if [[ "$STRICT" == "true" ]]; then
    kubeconform_args+=("-strict")
  fi

  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    kubeconform_args+=("-output" "json")
  fi

  for f in "${files[@]}"; do
    echo "[validate-k8s] Validating: $f" >&2
    if ! kubeconform "${kubeconform_args[@]}" "$f"; then
      exit_code=1
    fi
  done

  return $exit_code
}

# -- Validate with kubeval -------------------------------------------
run_kubeval() {
  local files=("$@")
  local exit_code=0
  local kubeval_args=(
    "--kubernetes-version" "${K8S_VERSION}"
  )

  if [[ "$STRICT" == "true" ]]; then
    kubeval_args+=("--strict")
  fi

  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    kubeval_args+=("--output" "json")
  fi

  for f in "${files[@]}"; do
    echo "[validate-k8s] Validating: $f" >&2
    if ! kubeval "${kubeval_args[@]}" "$f"; then
      exit_code=1
    fi
  done

  return $exit_code
}

# -- Validate with kubectl (fallback) ---------------------------------
run_kubectl() {
  local files=("$@")
  local exit_code=0

  for f in "${files[@]}"; do
    echo "[validate-k8s] Validating: $f" >&2
    if kubectl apply --dry-run=server -f "$f" &>/dev/null; then
      echo "  PASS: $f" >&2
    else
      echo "  FAIL: $f" >&2
      exit_code=1
    fi
  done

  return $exit_code
}

# -- Main ------------------------------------------------------------
main() {
  detect_validator

  mapfile -d '' FILES < <(collect_files "$MANIFEST")

  echo "[validate-k8s] Manifest count: ${#FILES[@]}" >&2
  echo "[validate-k8s] Target K8s version: ${K8S_VERSION}" >&2

  case "$VALIDATOR" in
    kubeconform)
      if ! run_kubeconform "${FILES[@]}"; then
        echo "" >&2
        echo "========================================" >&2
        echo "  VALIDATION FAILED" >&2
        echo "  Check errors above." >&2
        echo "  Tip: Use --strict to catch warnings." >&2
        echo "========================================" >&2
        exit 1
      fi
      ;;
    kubeval)
      if ! run_kubeval "${FILES[@]}"; then
        echo "" >&2
        echo "========================================" >&2
        echo "  VALIDATION FAILED" >&2
        echo "  Check errors above." >&2
        echo "========================================" >&2
        exit 1
      fi
      ;;
    kubectl)
      if ! run_kubectl "${FILES[@]}"; then
        echo "" >&2
        echo "========================================" >&2
        echo "  VALIDATION FAILED" >&2
        echo "  Note: kubectl fallback requires cluster connectivity." >&2
        echo "  Install kubeconform for offline validation." >&2
        echo "========================================" >&2
        exit 1
      fi
      ;;
    *)
      echo "ERROR: Unknown validator: $VALIDATOR" >&2
      exit 1
      ;;
  esac

  echo "" >&2
  echo "========================================" >&2
  echo "  ALL VALIDATIONS PASSED" >&2
  echo "  ${#FILES[@]} manifest(s) OK" >&2
  echo "========================================" >&2
}

main
