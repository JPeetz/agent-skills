// k6-helpers.js — reusable building blocks for k6 performance tests.
// Import with: import { rampStages, sloThresholds, ... } from './k6-helpers.js';
// Requires k6 >= v0.50 for stable k6/browser and arrival-rate executors.

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const businessErrors = new Rate('business_errors');

/** Linear ramp to `targetRps` rps, hold, then ramp down. Use with ramping-arrival-rate. */
export function rampStages({ targetRps, rampUp = '2m', hold = '10m', rampDown = '1m' }) {
  return [
    { target: targetRps, duration: rampUp },
    { target: targetRps, duration: hold },
    { target: 0, duration: rampDown },
  ];
}

/** Step-stress profile: each step multiplies load by `factor` until `maxRps`. */
export function stressStages({ startRps = 10, maxRps = 1000, factor = 2, step = '3m' }) {
  const stages = [];
  for (let rps = startRps; rps <= maxRps; rps *= factor) {
    stages.push({ target: Math.min(rps, maxRps), duration: step });
  }
  stages.push({ target: 0, duration: '1m' });
  return stages;
}

/** Instant spike: 1x -> multiplier x in seconds, brief hold, drop back. */
export function spikeStages({ baseRps, multiplier = 10, hold = '2m' }) {
  return [
    { target: baseRps, duration: '1m' },
    { target: baseRps * multiplier, duration: '10s' },
    { target: baseRps * multiplier, duration: hold },
    { target: baseRps, duration: '1m' },
  ];
}

/** SLO thresholds. All values are explicit so the gate is auditable. */
export function sloThresholds({ p95 = 400, p99 = 900, errorRate = 0.01, tag = null } = {}) {
  const suffix = tag ? `{endpoint:${tag}}` : '';
  return {
    [`http_req_duration${suffix}`]: [`p(95)<${p95}`, `p(99)<${p99}`],
    [`http_req_failed${suffix}`]: [`rate<${errorRate}`],
    'business_errors': ['rate<0.01'],
  };
}

/** JSON GET/POST helpers that tag every request by logical endpoint. */
export function apiGet(baseUrl, path, token, endpoint) {
  return http.get(`${baseUrl}${path}`, {
    headers: authHeaders(token),
    tags: { endpoint: endpoint || path },
  });
}

export function apiPost(baseUrl, path, body, token, endpoint) {
  return http.post(`${baseUrl}${path}`, JSON.stringify(body), {
    headers: authHeaders(token),
    tags: { endpoint: endpoint || path },
  });
}

export function authHeaders(token) {
  const h = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

/** Standard assertions: status, latency sanity, and JSON shape. */
export function expectOk(res, { maxMs = 0, json = false } = {}) {
  const ok = check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    ...(maxMs ? { [`latency < ${maxMs}ms`]: (r) => r.timings.duration < maxMs } : {}),
    ...(json ? { 'body parses': (r) => { try { r.json(); return true; } catch { return false; } } } : {}),
  });
  businessErrors.add(!ok);
  return res;
}

/** Realistic think time with jitter so VUs do not synchronize into a thundering herd. */
export function thinkTime(min = 0.5, max = 3) {
  sleep(min + Math.random() * (max - min));
}

/** Deterministic pseudo-random index from the current iteration (reproducible runs). */
export function pickIndex(length) {
  return (__VU * 7919 + __ITER * 104729) % length;
}

/** Basic auth token fetch for setup() — reads credentials from env, never hardcode. */
export function fetchToken(baseUrl, path = '/api/auth/token') {
  const res = http.post(`${baseUrl}${path}`, JSON.stringify({
    client_id: __ENV.CLIENT_ID,
    client_secret: __ENV.CLIENT_SECRET,
    audience: __ENV.AUDIENCE || 'api',
  }), { headers: { 'Content-Type': 'application/json' } });
  if (res.status !== 200) {
    throw new Error(`auth failed: ${res.status} ${res.body}`);
  }
  return res.json('access_token');
}

/** Fail fast on misconfiguration rather than producing a meaningless green run. */
export function requireEnv(names) {
  const missing = names.filter((n) => !__ENV[n]);
  if (missing.length) throw new Error(`missing env vars: ${missing.join(', ')}`);
}
