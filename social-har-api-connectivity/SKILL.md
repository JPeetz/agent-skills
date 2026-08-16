---
name: social-har-api-connectivity
description: >
  Use this skill when an agent needs to connect to a social platform's posting or
  data API by capturing real browser traffic to a HAR (or live-recording via CDP)
  and deriving the exact request shape. Activates when a platform has no documented
  API wrapper you control, and you can operate it in a browser with authorized access.
  Includes HAR capture (or live record), host/action filtering to avoid token noise,
  dynamic-token flagging, standalone verification, embed-verification, and
  per-platform auth/limits knowledge sourced from social-platform-api-integration.
  Authorized use only — never to bypass auth or bot detection.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - social
  - har
  - api
  - reverse-engineering
  - connectivity
  - posting
  - integration
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# Social Platform API Connectivity via HAR

Connect a social platform's posting/data API by **capturing real browser traffic to
a HAR (or live-recording via CDP/Chrome-MCP), deriving the exact request shape,
verifying it standalone, then reusing the verified client** — without relying on a
paid aggregator. Combines the capture→derive→verify skeleton from
`har-api-reverse-engineering` with social-platform specifics.

## When to use
- A social platform has no documented API wrapper you control, but you can operate it
  in a browser with authorized access.
- You need the exact auth + request shape of a platform action (post, upload media,
  fetch analytics) rather than guessing.
- You want to add a platform to a posting pipeline and need a programmable client
  that does not route through a paid aggregator.

## Guardrails (authorized use only — non-negotiable)
- **Only for APIs you are authenticated AND authorized to use.** Does NOT bypass
  authentication, login walls, or bot detection. If a platform (TikTok, Meta, X)
  actively forbids scripting in its terms, respect that — use the official API or an
  audited scheduler (Buffer, Postiz) instead. 3rd-party ToS check first. When in
  doubt, official API key wins.
- **HAR = credential artifact.** chmod 600, never commit, never paste tokens into
  chat/logs. Resolve auth by label at runtime — never hardcode a captured token.
- **Live-record noise control:** raw HAR dumps overwhelm agent context. Filter to the
  platform's API host + specific action; paginate and process in chunks — do not feed
  the whole capture to the model at once.

## The workflow
1. **Capture or live-record** the platform's API call:
   - Standalone HAR: DevTools → Network → perform the action → Save all as HAR
     (`/tmp/<platform>.har`, chmod 600).
   - Live-record: Chrome DevTools MCP / Playwright, capturing only the target API
     host. **Filter + paginate** request listings before analysis.
2. **Isolate the API call** — drop analytics/beacon/static-assets. Keep only XHR/fetch
   entries for the target host.
3. **Derive** method, URL path + query, minimal headers (content-type, accept,
   origin/referer), and body. Flag dynamic tokens (session, csrf, nonce, signature,
   expiring auth) for runtime handling, not literal replay.
4. **Build a clean client** — minimal headers, body, auth from credential source by
   label (never the captured token).
5. **Verify standalone** — request from the agent (no browser); match status + response
   shape (fields/keys), not just a 200.
6. **Reuse the verified client** — parameterize (text, media path, target). Verify the
   embed actually landed (public endpoint confirming media field populated).
7. **Official-API shortcut:** check the platform's docs and per-platform references
   (social-platform-api-integration) BEFORE capture. If a documented API exists, use
   it and skip capture.

## Per-platform guidance
- **Bluesky / Mastodon**: open APIs (App Password / bearer) — prefer documented
  endpoints; HAR capture for undocumented specifics only.
- **Approve-gated / anti-automation**: TikTok → use Buffer/Postiz (Direct Post audit
  rejects owned-account pipelines). Meta/FB → official Graph API. X → API tier gating.
  For these, HAR capture is not a viable publish path — use official/audited routes.
- **Character limits** per platform differ per *field* (post vs bio). Build each
  caption to its own ceiling (X 280 → BSKY 300 → MASTODON 500 → IG 2200 → LI 3000 →
  FB 63k). Use a shared expand-to-limit helper.
- **Verify shape, not just status**: 200 with an error-shaped body = failure.

## Scripts
- `scripts/har_derive.py` — filter a captured HAR to a host, print clean request
  shape (minimal headers, redacted tokens, dynamic-token flags). Usage:
  `python3 har_derive.py /tmp/<platform>.har --host api.platform.com [--path-includes <substr>]`
  Output is deterministic; never echos Authorization/cookie values.

## Pitfalls
- Whole raw HAR fed to the model → context blowout / noise (#1 failure).
- Replaying captured token literal → expiry + secret leak. Auth by label at runtime.
- Copying full headers (content-length, sec-*, CORS) — use minimal set.
- 200 with error body treated as success — validate shape.
- Skip ToS check on TikTok/Meta → account risk.
- Forget embed check → image-less posts "succeed" silently.

## Deliverable / done state
- Parameterized client that correctly posts/reads the platform,
- Proven by standalone request returning expected response shape,
- Auth by credential label (no captured secrets baked in),
- HAR chmod 600 or deleted; leaked secrets rotated,
- Official API path checked and documented why capture was needed.

## References
- `social-platform-api-integration` — per-platform specifics (Bluesky, Mastodon,
  LinkedIn refresh, Buffer/TikTok, X API tiers, verification limits).
- `har-api-reverse-engineering` — generic HAR→client method this builds on.

## Verification
- Standalone request returns expected shape (no browser). If not, find the dynamic
  token or get proper auth. Do not ship an unverified client.