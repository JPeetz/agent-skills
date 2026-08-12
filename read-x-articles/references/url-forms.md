# Reading X Articles — reference

## URL forms and what they give you

| URL form | Render-capable extractor | Bare `curl`/`urllib` | Note |
|---|---|---|---|
| `https://x.com/i/article/<ID>` | ✅ FULL body | ⚠️ often login shell | **Use this URL + a render tool.** |
| `https://x.com/<handle>/status/<id>` | ❌ wall | ❌ wall | Post page; not the article body. |
| `https://x.com/<handle>` | ⚠️ recent-post list only | ❌ wall | Profile page; discovery only. |
| `twitter.com/...` (legacy) | Same as x.com | Same | Redirects; treat identically. |

> **Key nuance (learned 2026-08-12):** the canonical `/i/article/<ID>` URL is
> necessary but a *plain* HTTP fetch (urllib/curl) can still return a
> login/JS shell. Use a JS-executing extractor (agent-grade `web_extract`) or a
> browser render to get the real body. Do not conclude the article is
> unreadable because a bare curl returned a shell.

## How to find the article ID from a status/share
- When a post IS an X Article, the author's "share" or article card points at
  `/i/article/<article_id>`.
- The status URL for an article-share post may carry the article link in its
  quote/attachment; fetch the status with a browser, or find the author's
  article card on their profile.
- If you only have a `/status/` post, prefer asking the user for the article
  link, or resolve it via a browser render.

## Fallback order (when plain `fetch`/`web_extract` fails)
1. Straight `web_extract`/fetch on `/i/article/<ID>` (works for the vast majority).
2. Browser tool to render the JS page, then read the DOM/rendered text.
3. X API (e.g. `xurl`): query the article tweet and read
   `data.article.plain_text`.

## Validation checklist
- [ ] Returned text contains the article's real thesis and body paragraphs
      (not just a title + "Log in or sign up for X").
- [ ] Paper length is plausible (essays return 1,000+ words of prose).
- [ ] The exact URL read is reported so the user can verify.