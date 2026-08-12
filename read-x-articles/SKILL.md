---
name: read-x-articles
description: >
  Read X (Twitter) long-form Articles end-to-end from a shared x.com link, in
  any AI coding agent. Activates when a user drops an x.com or twitter.com URL
  (especially an X Article like /i/article/ID) and expects it read, or says
  "read this X post/article/thread". Resolves the canonical /i/article/ID URL
  (which serves plain text) instead of giving up on the login/JS wall that hits
  profile and /status/ pages. Includes browser-tool and API fallbacks.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - x
  - twitter
  - articles
  - web-extract
  - reading
  - long-form
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# Read X (Twitter) Articles

Turn any X link a user shares into the full article text. Do NOT default to "I
can't read X" — X long-form Articles DO extract cleanly via the right URL.

## When to Use
- A user drops an `x.com/...` or `twitter.com/...` link and expects you to read it.
- The link is an X **Article** (long-form essay/interview) — canonical path
  `/i/article/<ID>`.
- You need primary source text from an X essay/thread as material for work
  (e.g. writing, video scripts, analysis).
- Anyone claims "X content can't be read" — that is the signal to trigger, not
  capitulate.

## The core insight (learned 2026-08-12)
- X **Articles** are readable end-to-end at the canonical
  **`https://x.com/i/article/<ID>`** **when fetched by a JS-executing
  web-extractor / browser tool** — that returns the FULL body, not a snippet.
- **Bare HTTP fetch (`urllib`/`curl`) of the article often returns a login/JS
  shell.** The canonical URL is necessary but a plain request is NOT sufficient
  — you need a render-capable tool. This is why `web_extract` (SE/agent-grade)
  succeeds where `curl` fails.
- **`/status/<id>` posts and profile pages** are JS-rendered and hit the
  login wall → they come back empty even to a browser. That is the apparent
  "can't read X." The fix is resolving the article URL AND using the right
  fetch tool, not giving up.

## Steps

1. **Try first, judge later.** When given any X link, immediately attempt it
   with a web-extract/browser tool. Declaring it unreadable *before* trying is
   the exact mistake this skill prevents.
2. **Use the right fetcher:** prefer the agent's `web_extract`-style tool or a
   browser render — NOT bare `curl`/`urllib`. If the only tool is a plain HTTP
   client, expect a login shell and fall back to a browser.
3. **If it's a `/status/` URL or returns a login/JS shell**, resolve the
   canonical article URL:
   - The article ID often appears in the status link's query/path when the
     post is an article share.
   - Find the author's `/i/article/<ID>` share link on their profile, or ask
     the user for the article link directly.
   - Then fetch `https://x.com/i/article/<ID>` with a render-capable tool.
4. **Validate the body**: a real extract contains substantive paragraphs, NOT
   just "Log in or sign up for X." A 1,900+ word essay returns complete.
5. **Fallbacks if a render-capable extract still fails**:
   - Use a **browser tool** (CDP-style) to render the JS page, then read the
     rendered text/DOM.
   - If the account has X API access (e.g. an `xurl`-style CLI), query the
     article tweet and read `data.article.plain_text`. A dead/unauthed CLI
     token is NOT a blocker — prefer web/browser first.
6. **Use the content.** It's legitimate primary source. Quote it and cite the
   author. If it's a community take (e.g. a power-user writing about a product),
   it's still real material for summaries, scripts, and analysis.

## Pitfalls
- Do not assume "articles are paywalled/login-walled." The canonical
  `/i/article/<ID>` endpoint serves plain text; the wall applies to the
  JS-rendered profile/status pages, not this endpoint.
- A dead X API token (401) is unrelated to article reading — do not block the
  task on fixing xurl/auth when web extraction works.
- Verify you got the actual article (thesis + body), not just a title + login
  prompt, before treating it as read.

## Verification
- Did the extraction return the article's real prose (title, paragraphs,
  thesis) rather than a shell? If yes, it's read.
- Report the exact URL you read + a short grounded summary so the user can
  verify.