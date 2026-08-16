---
name: social-har-api-connectivity
description: >
  Use this skill when an agent needs to connect to a social platform's API by
  prompting the user to pick a platform, driving Chrome to the login page,
  capturing all network traffic as the user logs in (handling MFA/CAPTCHA),
  extracting session tokens, and building a reusable posting client.
  The agent orchestrates; the user handles credentials. Authorized use only.
version: 3.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - social
  - har
  - api
  - connectivity
  - reverse-engineering
  - chrome
  - cdp
  - posting
  - login
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# Social Platform API Connectivity via Chrome CLI HAR Capture

Connect an AI agent to any social platform's posting/data API. **The agent asks
the user which platform, drives Chrome to the login page, the user logs in
(credentials + MFA/CAPTCHA in a visible browser), the agent captures every
network request and saves the session tokens for reuse.**

This is an interactive workflow: the agent orchestrates, the user authenticates.

## The interactive workflow (the agent drives this)
1. **Prompt the user:** "Which social platform do you want to connect?"
   Present the supported list. Wait for their choice.
2. **Validate the choice.** If the platform has an official API that's
   preferable, recommend that first. If the platform blocks automation
   (TikTok), say so.
3. **Start Chrome** with CDP in **visible mode**:
   ```
   /Applications/Google Chrome.app/Contents/MacOS/Google Chrome \
     --remote-debugging-port=9223 --user-data-dir=/tmp/capture-profile \
     --no-first-run --no-default-browser-check --disable-gpu --window-size=1280,800
   ```
4. **Navigate** to the platform's login URL (from the table below).
5. **Tell the user:** "Chrome is open at the [Platform] login page. Log in with
   your credentials in the browser window. I'm monitoring the network — I'll
   detect when you're logged in. Take your time."
6. **Wait** while the user logs in. Keep waiting until the URL changes to a
   post-login page (feed/dashboard/home).
7. **Stop capture.** Extract session cookies, auth tokens, and API endpoints
   from the captured traffic. Save to a temp directory (chmod 600).
8. **Confirm to the user:** "Connected to [Platform]. Session captured. I can
   now post/read on your behalf."
9. **Build a reusable client** using the extracted session. Store the credential
   reference by label. Verify with a test call.

## Supported platforms
| Platform | Login URL | Recommended? |
|---|---|---|
| Bluesky | https://bsky.app/login | Prefer AT Protocol + App Password |
| Mastodon | [instance]/auth/sign_in | Prefer bearer token API |
| X/Twitter | https://x.com/login | Capture for endpoints not in API tier |
| LinkedIn | https://www.linkedin.com/login | Prefer official OAuth |
| Instagram | https://www.instagram.com/accounts/login/ | Prefer Meta Graph API |
| Facebook | https://www.facebook.com/login | Prefer Meta Graph API |
| TikTok | https://www.tiktok.com/login | ⚠️ Capturable but fragile (anti-bot) | Try if needed, but Buffer is more reliable |
| Reddit | https://www.reddit.com/login | Prefer OAuth script app |
| Pinterest | https://www.pinterest.com/login | Prefer official API if approved |
| Threads | https://www.threads.net/login | Capture may help for undocumented |
| YouTube | https://accounts.google.com/ | For YouTube Data API, prefer OAuth |

## The tool: chrome_capture_client.py
The agent runs this script to automate Chrome + CDP + capture:

```
env -u PYTHONPATH /usr/local/bin/python3 chrome_capture_client.py \
  --login-url "https://platform.com/login" \
  --success-url-pattern "feed|dashboard|home" \
  --visible \
  --timeout 180 \
  --output /tmp/capture
```

The agent tells the user the browser is open, waits for login completion,
then processes the results.

## Credential hygiene
- Extracted tokens and cookies are written to `/tmp/<name>/auth.json` (chmod 600).
- The agent reads them by path at runtime — never hardcode captured tokens.
- Sessions expire (hours to days). Note the capture time and re-capture when stale.
- Never commit the capture directory or auth.json to any repository.

## Pitfalls
- MFA is expected — the visible window is for the user to complete 2FA.
- User must not close the Chrome window until the agent confirms capture is done.
- TikTok has anti-bot detection that will block most capture attempts — warn first.
- The user must check they're logging into the correct account.
- Tokens are ephemeral — re-capture when they expire.

## Verification
- After capture, the agent makes a test call to confirm the session is valid.
- A test post item is created and verified via a public endpoint.
- The agent reports the platform, detected API host, and session status.