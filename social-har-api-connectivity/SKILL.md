---
name: social-har-api-connectivity
description: >
  Use this skill when an agent needs to connect to a social platform's API by
  driving Chrome (CLI + CDP) to capture the HAR including the login/authentication
  flow, extract session tokens, and reuse the verified session for programmatic
  posting — without relying on a paid aggregator. The agent drives Chrome headlessly,
  captures every network call during auth + posting, extracts the session, and builds
  a reusable client with authorized-use guardrails, per-platform ToS checks, embed
  verification, and noise filtering baked in. Authorized use only.
version: 2.0.0
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
  - chrome
  - cdp
  - posting
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# Social Platform API Connectivity via Chrome CLI HAR Capture

Connect an AI agent to any social platform's posting/data API by **driving Chrome
(CLI + CDP) to capture the HAR including the login/authentication flow, extract
session tokens, and reuse the verified session for programmatic posting** —
without relying on a paid aggregator.

## When to use
- You need an AI agent to post/read a social platform that has no clean API wrapper
  and you can authenticate as a user.
- You want to automate social media accounts but the platform has no documented API
  or its API tier is too restrictive.
- You need to capture the authentication flow (login, OAuth, session token) and
  reuse it programmatically — not just inspect static API calls.
- You're building a multi-platform posting pipeline and need a scriptable client
  without paying per-platform aggregator fees.

## Guardrails
- **Authorized accounts only.** Only automate accounts YOU own. Check platform ToS
  before scripting. This does NOT bypass CAPTCHAs, MFA, or bot detection.
- **Chrome CLI runs locally.** No credentials leave your machine. HAR files are
  saved with chmod 600 and deleted after extraction. Session tokens are ephemeral.
- **MFA/CAPTCHA:** Most social platforms have additional verification. The tool
  handles this by keeping the Chrome window visible for manual interaction.

## How it works
1. Start Chrome with remote debugging port (--remote-debugging-port=9223)
2. Connect via CDP (Chrome DevTools Protocol) over WebSocket
3. Enable Network capture — all HTTP traffic is logged
4. Navigate to the platform's login URL
5. User completes login (in visible window for MFA/CAPTCHA)
6. Tool detects login success via URL pattern
7. Extracts auth tokens, cookies, and API endpoints from captured traffic
8. Saves HAR + auth map to /tmp/ (chmod 600)
9. Prints a reusable client template

## The tool: chrome_capture_client.py
```bash
env -u PYTHONPATH /usr/local/bin/python3 chrome_capture_client.py \
  --login-url "https://platform.com/login" \
  --success-url-pattern "feed|dashboard|home" \
  --visible \
  --timeout 180 \
  --output /tmp/capture
```

### Output
- `capture.har` — all network traffic in HAR format
- `auth.json` — extracted cookies, auth headers, and body tokens (prefix only)
- Console summary with detected API host and reusable curl template

## Per-platform guidance
- **Bluesky/Mastodon:** Open APIs with App Password/bearer token — prefer them.
- **TikTok:** Anti-bot detection blocks automation. Use Buffer/Postiz instead.
- **Meta/Instagram:** Official Graph API via app review — prefer it.
- **X/Twitter:** Official API for posting; Chrome capture only for endpoints
  not in the API tier.
- **LinkedIn:** Official API + OAuth — prefer documented path.

## Pitfalls
- MFA/CAPTCHA is the #1 blocker — design your capture to expect manual completion.
- Raw HAR dumps overwhelm agent context — filter by host + XHR/fetch type.
- Expiring tokens: most platforms issue short-lived session cookies; re-capture
  or use a refresh pattern.
- CDP page targets close mid-capture on login redirects — the tool handles
  reframed navigation events.
- Never hardcode captured tokens — resolve auth from the vault by label.

## Verification
- Standalone request returns expected response shape (no browser).
- Post a test item and verify via a public getPost endpoint that the embed
  actually landed, not just that the create call returned ok.