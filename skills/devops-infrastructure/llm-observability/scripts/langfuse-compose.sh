#!/usr/bin/env bash
# /// script
# requires-python = ">=3.9"
# ///
# Bring up a local Langfuse stack and smoke-test OTLP ingestion.
#
#   ./langfuse-compose.sh up      # start postgres/clickhouse/redis/langfuse-web
#   ./langfuse-compose.sh smoke   # send one OTLP span, verify it is queryable
#   ./langfuse-compose.sh down    # stop and remove volumes
#
# Requires: docker (compose v2), curl, jq, base64.
set -euo pipefail

HOST="${LANGFUSE_HOST:-http://localhost:3000}"
DIR="${LANGFUSE_DIR:-.langfuse-local}"
COMPOSE="$DIR/docker-compose.yml"

log() { printf '\033[36m[langfuse]\033[0m %s\n' "$*"; }
die() { printf '\033[31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }

write_compose() {
  mkdir -p "$DIR"
  cat > "$COMPOSE" <<'YAML'
services:
  langfuse-web:
    image: langfuse/langfuse:3    # must be >= 3.22 for /api/public/otel ingestion
    restart: unless-stopped
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/langfuse
      CLICKHOUSE_URL: http://clickhouse:8123
      CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: ""
      REDIS_HOST: redis
      NEXTAUTH_URL: http://localhost:3000
      NEXTAUTH_SECRET: local-dev-secret-change-in-prod
      SALT: local-dev-salt-change-in-prod
      TELEMETRY_ENABLED: "false"
    depends_on:
      db: { condition: service_healthy }
      clickhouse: { condition: service_healthy }
      redis: { condition: service_started }
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: langfuse
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 12
  clickhouse:
    image: clickhouse/clickhouse-server:24
    restart: unless-stopped
    environment:
      CLICKHOUSE_DB: langfuse
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8123/ping || exit 1"]
      interval: 5s
      retries: 12
  redis:
    image: redis:7
    restart: unless-stopped
YAML
  log "compose written to $COMPOSE (dev secrets — never reuse in production)"
}

cmd_up() {
  need docker
  [ -f "$COMPOSE" ] || write_compose
  docker compose -f "$COMPOSE" up -d
  log "waiting for $HOST/api/public/health ..."
  for i in $(seq 1 60); do
    if curl -fsS "$HOST/api/public/health" >/dev/null 2>&1; then
      log "up: $HOST  (create a project in the UI, copy pk-lf-/sk-lf-)"
      return 0
    fi
    sleep 2
  done
  die "Langfuse did not become healthy in 120s — check: docker compose -f $COMPOSE logs langfuse-web"
}

cmd_smoke() {
  need curl; need base64
  local pk="${LANGFUSE_PUBLIC_KEY:?set LANGFUSE_PUBLIC_KEY=pk-lf-...}"
  local sk="${LANGFUSE_SECRET_KEY:?set LANGFUSE_SECRET_KEY=sk-lf-...}"
  local auth; auth="$(printf '%s:%s' "$pk" "$sk" | base64 | tr -d '\n')"
  local now_ns; now_ns="$(date +%s)000000000"
  local end_ns="$(( $(date +%s) + 1 ))000000000"

  local payload
  payload=$(cat <<JSON
{"resourceSpans":[{"resource":{"attributes":[
  {"key":"service.name","value":{"stringValue":"llm-observability-smoke"}}]},
 "scopeSpans":[{"scope":{"name":"smoke"},"spans":[{
  "traceId":"$(printf '%032x' $RANDOM$RANDOM$RANDOM)",
  "spanId":"$(printf '%016x' $RANDOM$RANDOM)",
  "name":"chat gpt-4o-mini","kind":3,
  "startTimeUnixNano":"$now_ns","endTimeUnixNano":"$end_ns",
  "attributes":[
    {"key":"gen_ai.operation.name","value":{"stringValue":"chat"}},
    {"key":"gen_ai.provider.name","value":{"stringValue":"openai"}},
    {"key":"gen_ai.request.model","value":{"stringValue":"gpt-4o-mini"}},
    {"key":"gen_ai.response.model","value":{"stringValue":"gpt-4o-mini-2024-07-18"}},
    {"key":"gen_ai.usage.input_tokens","value":{"intValue":"42"}},
    {"key":"gen_ai.usage.output_tokens","value":{"intValue":"17"}},
    {"key":"gen_ai.response.finish_reasons","value":{"arrayValue":{"values":[{"stringValue":"stop"}]}}}
  ],
  "status":{"code":1}
}]}]}
JSON
)

  local code
  code=$(curl -sS -o /tmp/langfuse-smoke.out -w '%{http_code}' \
    -X POST "$HOST/api/public/otel/v1/traces" \
    -H "Content-Type: application/json" \
    -H "Authorization: Basic $auth" \
    -H "x-langfuse-ingestion-version: 4" \
    --data "$payload")
  [ "$code" = "200" ] || { cat /tmp/langfuse-smoke.out; die "OTLP ingest returned HTTP $code (401 = bad keys, 404 = wrong endpoint)"; }
  log "OTLP ingest OK (HTTP 200). Open $HOST and look for trace 'chat gpt-4o-mini' in project 'llm-observability-smoke'."
  log "Check that cost is non-zero; if zero, add a model definition for gpt-4o-mini."
}

cmd_down() {
  [ -f "$COMPOSE" ] && docker compose -f "$COMPOSE" down -v || log "nothing to stop"
}

case "${1:-up}" in
  up) cmd_up ;;
  smoke) cmd_smoke ;;
  down) cmd_down ;;
  *) die "usage: $0 {up|smoke|down}" ;;
esac
