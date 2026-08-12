#!/usr/bin/env python3
"""read_x_article.py — resolve + try to fetch an X Article as plain text.

Usage:
  python3 read_x_article.py [URL]

Fetches the canonical /i/article/<ID> URL. NOTE (learned 2026-08-12): a bare
HTTP fetch can return a login/JS shell — the canonical URL is necessary but not
sufficient. For the reliable path use a JS-executing web-extract/browser tool.
This script is best-effort; if it prints a login-shell signature, that IS the
signal to switch to a render-capable tool (per the SKILL.md fallbacks).

Self-contained: stdlib only (urllib). No API key required.
"""
import re, sys, urllib.request, urllib.error
from html.parser import HTMLParser

_ARTICLE_RE = re.compile(r"/i/article/(\d+)", re.I)
STATUS_RE = re.compile(r"(?:x\.com|twitter\.com)/[^/]+/status/(\d+)", re.I)


class _TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
    def handle_data(self, data):
        if not self._skip:
            t = data.strip()
            if t:
                self.parts.append(t)


def resolve_article_id(url):
    m = _ARTICLE_RE.search(url)
    if m:
        return m.group(1)
    # A /status/ link may itself BE an article-share; we can't know the article
    # id without the page. Report that and return None.
    return None


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    p = _TextExtract()
    p.feed(raw)
    return "\n".join(p.parts)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        # default: read a known-good public example (HUD article) to prove capability
        url = "https://x.com/i/article/2086811327574741012"
    aid = resolve_article_id(url)
    if not aid:
        print("Not an /i/article/<ID> URL; resolve the canonical article URL first.")
        return 2
    canonical = f"https://x.com/i/article/{aid}"
    print(f"# Fetching {canonical}")
    text = fetch(canonical)
    if not text or "Log in or sign up" in text:
        print("# Returned a login/JS shell — use a browser render fallback.")
        return 1
    print(text[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())