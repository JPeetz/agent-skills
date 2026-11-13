#!/usr/bin/env bash
# pact_ci_gate.sh — config-validated can-i-deploy gate for CI.
#
# Fails closed: missing configuration is an error, not a skip.
#
# Usage:
#   PACT_BROKER_BASE_URL=... PACT_BROKER_TOKEN=... \
#   PACTICIPANT=orders-api VERSION=$(git rev-parse HEAD) ENVIRONMENT=production \
#   ./pact_ci_gate.sh
#
# Optional:
#   PACT_BROKER_CLI   command prefix, default "pact-broker"
#   DRY_RUN=1         print the command instead of running it

set -euo pipefail

PACT_BROKER_CLI="${PACT_BROKER_CLI:-pact-broker}"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 2
}

require() {
  local name="$1"
  [ -n "${!name:-}" ] || fail "$name is not set. The gate refuses to run without it."
}

require PACT_BROKER_BASE_URL
require PACT_BROKER_TOKEN
require PACTICIPANT
require VERSION
require ENVIRONMENT

command -v "${PACT_BROKER_CLI%% *}" >/dev/null 2>&1 || \
  fail "'$PACT_BROKER_CLI' not found. Install the pact_broker-client gem or use the pactfoundation/pact-cli image."

cmd=(
  $PACT_BROKER_CLI can-i-deploy
  --pacticipant "$PACTICIPANT"
  --version "$VERSION"
  --to-environment "$ENVIRONMENT"
  --broker-base-url "$PACT_BROKER_BASE_URL"
  --broker-token "$PACT_BROKER_TOKEN"
)

printf 'Checking compatibility: %s@%s -> %s\n' "$PACTICIPANT" "$VERSION" "$ENVIRONMENT"

if [ "${DRY_RUN:-0}" = "1" ]; then
  printf 'DRY RUN: %s\n' "${cmd[*]}"
  exit 0
fi

set +e
output="$("${cmd[@]}" 2>&1)"
status=$?
set -e

printf '%s\n' "$output"

if [ "$status" -ne 0 ]; then
  cat >&2 <<'MSG'

DEPLOY BLOCKED by the Pact compatibility gate.

Typical causes:
  1. The provider has not published a verification result for this pact yet.
     -> run provider verification with publishVerificationResult: true
  2. A verification genuinely failed: the contract and the provider disagree.
     -> fix the provider, or correct an over-strict matcher in the consumer.
  3. The pacticipant name or version does not exist in the broker.
     -> check for a typo and confirm the pact was published with this SHA.
  4. The target environment is undefined, or no deployment has been recorded,
     so the broker has nothing to compare against.
     -> create the environment and ensure record-deployment runs post-deploy.

Do not bypass this gate with --force or by deleting the step. A bypassed gate
means production compatibility is unverified, which is exactly the failure mode
contract testing exists to prevent.
MSG
  exit "$status"
fi

printf 'OK: %s@%s is compatible with %s. Proceed with deploy.\n' "$PACTICIPANT" "$VERSION" "$ENVIRONMENT"
