#!/usr/bin/env python3
"""Derive a clean API request shape from a HAR, filtering by host/action.

Filters a captured HAR to the target host + XHR/fetch entries, then prints each
apt request as method/URL + minimal headers + body, flagging dynamic tokens.

Usage:
    env -u PYTHONPATH /usr/local/bin/python3 har_derive.py /tmp/platform.har \
        --host api.platform.com [--path-includes post] [--lenient]

Never prints cookie/authorization values. Reads secrets-free request metadata only.
"""
import argparse, json, os, re, sys

SENSITIVE = ("cookie", "authorization", "x-csrf-token", "x-xsrf-token", "set-cookie")
DYNAMIC_RE = re.compile(r"(token|nonce|csrf|xsrf|session|signature|ts|timestamp|expir)", re.I)


def safe_excerpt(text, n=200):
    text = text or ""
    # redact anything that looks like a token/secret even in the body, handling
    # both `key: value` and JSON `"key": "value"` forms (leading quote optional)
    text = re.sub(r"([\"']?)(?:access_token|token|secret|password|apikey|api_key)(\"')?\s*[:=]\s*[\"'][^\"']{6,}[\"']",
                  r"\1\2=<redacted>", text, flags=re.I)
    return text[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("har")
    ap.add_argument("--host", required=True, help="API host filter, e.g. api.platform.com")
    ap.add_argument("--path-includes", default="", help="optional substring the URL path must match")
    ap.add_argument("--lenient", action="store_true", help="also include non-xhr entries")
    args = ap.parse_args()

    if not os.access(args.har, os.R_OK):
        print(f"ERROR: cannot read {args.har}")
        sys.exit(1)

    data = json.load(open(args.har))
    entries = data.get("log", {}).get("entries", [])

    host = args.host.lower()
    matched = 0
    for i, e in enumerate(entries):
        req = e.get("request", {})
        url = req.get("url", "")
        if host not in url.lower():
            continue
        rt = (req.get("resourceType") or e.get("_resourceType") or "").lower()
        if not args.lenient and rt not in ("xhr", "fetch", "xmlhttprequest", ""):
            continue
        if args.path_includes and args.path_includes not in url:
            continue

        matched += 1
        method = req.get("method", "GET")
        print(f"--- entry {i} [{method}] {url} ---")
        print(f"  resourceType: {rt or 'unknown'}")
        print(f"  status: {e.get('response', {}).get('status', '?')}")
        # minimal headers, redacting sensitive
        print("  headers (minimal, sensitive redacted):")
        for h in req.get("headers", []):
            n = h.get("name", "").lower()
            if n in ("content-type", "accept", "origin", "referer"):
                print(f"    {n}: {safe_excerpt(h.get('value'))}")
        # dynamic flag
        blob = json.dumps({"url": url, "headers": req.get("headers"), "post": req.get("postData", {})}).lower()
        flags = [k for k in DYNAMIC_RE.findall(blob)]
        if flags:
            print(f"  dynamic-candidate: {sorted(set(flags))}")
        pd = req.get("postData", {})
        if pd:
            print(f"  body: {safe_excerpt(pd.get('text'))}")
    if not matched:
        print(f"NO matching API entries for host={host} path_includes={args.path_includes!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()