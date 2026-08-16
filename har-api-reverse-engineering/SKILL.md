---
name: har-api-reverse-engineering
description: >
  Use this skill when an agent needs to call a website's hidden or undocumented API:
  capture real browser requests into a HAR file, derive the exact request shape, build
  a clean replayable client, verify it outside the browser, and reuse the verified
  client. Activates when a backend has no documented API, or when you must reproduce
  the precise request (method, URL, headers, JSON body) of an action you can only
  perform in a browser. Authorized use only — never to bypass auth or bot detection.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - har
  - api
  - reverse-engineering
  - curl
  - network
  - web
  - debugging
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# HAR-Capture API Reverse Engineering

Turn a website's hidden/undocumented API into a verified, reusable client by
**capturing real browser requests to a HAR file, then deriving and replaying them**
— instead of reverse-engineering by trial and error against a "hidden" endpoint.

## When to use
- A site you can *operate in a browser* has no documented API (or none is known)
  and you need an agent to call its backend directly instead of driving the UI.
- You need the exact request shape (method, URL, headers, JSON body) of an action
  rather than guessing by trial and error.
- A browser-only workflow is repeated often enough that a verified programmatic
  shortcut beats manual steps every time.

## Guardrails (read first — non-negotiable)
- **Authorization:** only capture/replay APIs you are **authenticated AND authorized**
  to use (your own site, a client site you operate, or a service whose terms permit
  scripting). This technique does NOT bypass authentication or bot detection, and
  must never be used to defeat them. If the API needs auth you do not hold, STOP —
  the answer is to obtain proper access, not to replay someone else's session.
- **Third-party terms:** on anything you do not own, check the terms. Aggressive
  scripted replay can trip bot/rate detection regardless of intent. When in doubt,
  prefer an official API key + documented endpoint.
- **Secrets hygiene:** HAR files embed cookies, tokens, Authorization headers, and
  sometimes request bodies containing keys. Treat a HAR like a credential file:
  - chmod 600 every HAR you keep; never commit one to a repo; never paste it (or the
    tokens inside) into chat or logs.
  - Before reusing derived requests, re-issue auth from your credential source by
    label — never hardcode captured tokens into code.
- **Fragility:** replayed requests can fail if the API uses expiring signatures,
  CSRF/nonce tokens, or one-time session values. The verification step catches this —
  do not skip it.

## The workflow
1. **Capture a HAR** while operating the real site:
   - Chrome DevTools: F12 → Network → record → perform the action → right-click →
     Save all as HAR.
   - Or drive it headlessly (Playwright/CDP) capturing request/response headers and
     post data.
   - Save to a temp path (`/tmp/<name>.har`) and chmod 600 — not into your project tree.
2. **Derive the API details** from the HAR entries: pick the XHR/fetch entries for the
   action. For each: `method`, `url`, request `headers` (only content-type, accept,
   origin/referer matter — drop cookies/auth for now), and `postData`. Identify
   dynamic tokens (session id, csrf, nonce, signature) separately — those need
   runtime handling, not literal replay.
3. **Build a clean request** — do NOT copy the whole header block. Reconstruct minimal
   calls (curl / Python requests / any HTTP client) with: URL, method, Content-Type,
   the JSON/form body, and auth resolved from your credential source by label (never
   the captured token).
4. **Run separate from the browser** and compare the response to the one in the HAR.
   Match on status code, key fields, and the specific JSON shape you care about —
   not byte-for-byte idempotency.
   - Non-2xx or shape mismatch ⇒ likely a dynamic token or missing/rotated auth →
     re-inspect the HAR for an expiring value, refresh auth, retry.
5. **Verify once, then reuse:** once the derived client returns the correct response
   outside the browser, wrap it as a small, parameterized function. Reuse that
   verified client for downstream apps. Keep the verification evidence (exact URL +
   returned status/shape) in your summary when reporting success — do not claim
   success from an unverified replay.

## Deliverable / done state
- A small parameterized client (function/script) that calls the hidden API correctly,
- Proven by a real request made outside the browser that returns the expected response,
- Auth sourced from the credential source by label (no captured secrets baked in),
- HAR either deleted or chmod 600, and any exposed secret rotated if it leaked.

## Pitfalls
- Replaying a captured `Authorization`/cookie literally = secret leakage + likely
  expiry; resolve auth at run time by label.
- Copying the full header set from the HAR (content-length, sec-fetch, unexpected CORS
  headers) — reuse only the minimal needed headers.
- Treating a 200 that returns an error-shaped body as success — validate the response
  *shape*, not just the status.
- Skipping the standalone verification step — signature/nonce APIs break silently on
  replay.
- HAR files are blueprint artifacts that embed live credentials: never let one land
  in a repo or a shared data source.

## Verification
- The derived request returns the expected status + response shape when run standalone
  (no browser). If it does not, do not ship it — find the dynamic token or get proper
  auth.

## References
- `references/har-extraction.md` — reading a HAR entry to method/URL/headers/body.