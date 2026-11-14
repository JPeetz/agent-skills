#!/usr/bin/env python3
"""Scan agent output for canaries, secrets, exfiltration channels and render payloads.

This is layer L5 of the prompt-injection-defense skill: the model's output is
semi-trusted and leaves the boundary twice — into downstream systems and into a
human's browser or terminal. This script checks both.

What it does
------------
1. Canary detection: any canary token planted in the system prompt or a decoy
   credential appearing in output means prompt leak or context copying. A hit
   blocks, unconditionally.
2. Secret and PII detection with Luhn validation for card numbers and an
   entropy + keyword gate for generic tokens (keeps false positives down).
3. Exfiltration channels: remote markdown/HTML images, data: URIs, known
   webhook and collaborator domains, and URLs carrying high-entropy parameters.
4. Render sanitizing per mode: chat/markdown (images, links, active HTML,
   javascript: URLs), html (same plus event handlers), terminal (ANSI/OSC,
   including OSC 8 hyperlinks, C0/C1 controls, bidi overrides).

Usage
-----
    python3 scan_agent_output.py --file reply.md --mode chat \
        --canary "$CANARY_PROMPT" --canary "$CANARY_DECOY" --out /tmp/safe.md
    python3 scan_agent_output.py --text "$(cat out.txt)" --mode terminal
    python3 scan_agent_output.py --file reply.md --mode chat \
        --allow-host cdn.example.com --pii --emit-text

    --out PATH        write the sanitized text (the safe artifact)
    --emit-text       include the sanitized text in the JSON on stdout
    --pii             also flag email addresses and phone numbers
    --redact          replace matches with [REDACTED:<kind>] instead of dropping
    --strict-links    also rewrite links to non-allowlisted hosts; by default links
                      are kept because they need a click, while images are blocked
                      because they fire on render
    --allow-host      host permitted for images and links (repeatable)
    --canary-file     file with one canary token per line
    AGENT_CANARY_TOKENS env var: comma-separated canary tokens

Verdict on stdout as JSON. Exit codes: 0 pass, 10 redacted, 20 block, 1 error.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import sys
from urllib.parse import urlsplit, unquote

VERSION = "1.0.0"
TOOL = "scan_agent_output.py"

MAX_EXCERPT = 100

WEBHOOK_HOSTS = (
    "webhook.site", "requestbin.net", "requestbin.io", "pipedream.net",
    "ngrok.io", "ngrok-free.app", "burpcollaborator.net", "interact.sh",
    "oast.fun", "oast.me", "canarytokens.com", "transfer.sh", "file.io",
    "pastebin.com", "gofile.io", "0x0.st", "anonfiles.com",
)

# --------------------------------------------------------------------------
# Secret / PII patterns
# --------------------------------------------------------------------------
# (id, category, severity, weight, regex)
PATTERNS = [
    ("secret.aws_access_key", "secret", "critical", 40,
     re.compile(r"\b(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b")),
    ("secret.aws_secret_key", "secret", "critical", 40,
     re.compile(r"(?i)aws_?secret_?access_?key\s*[=:]\s*[\"']?([A-Za-z0-9/+=]{40})")),
    ("secret.github_token", "secret", "critical", 40,
     re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("secret.openai_key", "secret", "critical", 40,
     re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b")),
    ("secret.anthropic_key", "secret", "critical", 40,
     re.compile(r"\bsk-ant-(?:api|admin)[0-9]*-[A-Za-z0-9_-]{20,}\b")),
    ("secret.slack_token", "secret", "critical", 40,
     re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("secret.stripe_key", "secret", "critical", 40,
     re.compile(r"\b(?:sk|rk)_live_[0-9a-zA-Z]{20,}\b")),
    ("secret.google_api_key", "secret", "critical", 40,
     re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("secret.private_key", "secret", "critical", 45,
     re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("secret.jwt", "secret", "high", 30,
     re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("secret.connection_string", "secret", "critical", 38,
     re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp|"
                r"mssql|clickhouse)://[^\s:/@]{1,64}:[^\s@]{3,}@")),
    ("secret.bearer_header", "secret", "high", 28,
     re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+([A-Za-z0-9._~+/=-]{20,})")),
    ("secret.env_dump", "secret", "high", 26,
     re.compile(r"(?im)^\s*(?:[A-Z][A-Z0-9_]{2,40})\s*=\s*\S{8,}\s*$")),
    ("pii.credit_card", "pii", "high", 30,
     re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("pii.ssn", "pii", "high", 26,
     re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("pii.email", "pii", "low", 8,
     re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("pii.phone", "pii", "low", 6,
     re.compile(r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\(\d{2,4}\)|\d{3})[ -]?\d{3}[ -]?\d{2,4}(?!\d)")),
]

ENTROPY_TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_-]{32,}")
SECRET_KEYWORD_RE = re.compile(
    r"(?i)\b(key|token|secret|passw(or)?d|credential|auth|bearer|private)\b"
)

# Download/content-disposition style payloads
EXFIL_MD_IMAGE_RE = re.compile(
    r"!\[([^\]\n]{0,200})\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
EXFIL_HTML_IMG_RE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*([\"']?)([^\"'\s>]+)\1[^>]*>", re.I)
EXFIL_DATA_URI_RE = re.compile(r"data:\s*[a-z]+/[a-z0-9.+-]+;base64,([A-Za-z0-9+/=]{16,})", re.I)
EXFIL_MD_LINK_RE = re.compile(
    r"(?<!!)\[([^\]\n]{0,200})\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
EXFIL_RAW_URL_RE = re.compile(r"https?://[^\s<>\"')\]]{6,}", re.I)

# --------------------------------------------------------------------------
# Render sanitizer regexes
# --------------------------------------------------------------------------
DANGEROUS_BLOCK_RE = re.compile(
    r"<\s*(script|style|iframe|object|embed|form|noscript)\b[^>]*>.*?<\s*/\s*\1\s*>",
    re.I | re.S,
)
SELF_CLOSING_DANGER_RE = re.compile(
    r"<\s*(iframe|object|embed|script|form|meta|link|base)\b[^>]*/?>", re.I
)
EVENT_ATTR_RE = re.compile(r"\s+on[a-z]{3,}\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
JS_URL_RE = re.compile(r"(?i)(javascript|vbscript)\s*:")
STYLE_URL_RE = re.compile(r"url\s*\(\s*['\"]?\s*(javascript|data):", re.I)
STYLE_ATTR_RE = re.compile(r"\s+style\s*=\s*(?:\"[^\"]*\"|'[^']*')", re.I)

ANSI_RE = re.compile(
    r"\x1b\[[0-9;?]*[ -/]*[@-~]"
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?"
    r"|\x1b[@-Z\\-_]"
    r"|\]8;;[^\x07\x1b]*(?:\x07|\x1b\\)?"
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
BIDI_RE = re.compile(r"[\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c]")
ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200d\u2060\ufeff\u180e\u00ad]")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts: dict[str, int] = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    total = len(value)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def luhn_ok(number: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", number)]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def mask(value: str, keep: int = 6) -> str:
    value = value.replace("\n", " ")
    if len(value) <= keep + 4:
        return value[:2] + "*" * max(0, len(value) - 2)
    return f"{value[:keep]}...{value[-2:]} ({len(value)} chars)"


def host_of(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def is_remote(url: str) -> bool:
    lowered = url.strip().lower()
    return lowered.startswith(("http://", "https://", "//"))


# --------------------------------------------------------------------------
# Detection
# --------------------------------------------------------------------------

def load_canaries(values: list[str], canary_file: str | None) -> list[str]:
    canaries = [v.strip() for v in values if v and v.strip()]
    env = os.environ.get("AGENT_CANARY_TOKENS", "")
    canaries += [v.strip() for v in env.split(",") if v.strip()]
    if canary_file:
        try:
            with open(canary_file, "r", encoding="utf-8", errors="replace") as handle:
                canaries += [line.strip() for line in handle if line.strip()]
        except OSError as exc:
            print(json.dumps({"tool": TOOL, "error": f"canary file: {exc}"}))
            raise SystemExit(1)
    return [c for c in dict.fromkeys(canaries) if len(c) >= 6]


def check_canaries(text: str, canaries: list[str]) -> list[dict]:
    """Any canary appearance means prompt leak or context copying."""
    hits = []
    compact_text = None
    for token in canaries:
        variants = [
            token,
            base64.b64encode(token.encode()).decode().rstrip("="),
            unquote(token),
        ]
        matched = None
        for variant in variants:
            if len(variant) < 6:
                continue
            idx = text.find(variant)
            if idx != -1:
                matched = {
                    "canary": mask(token, 4),
                    "match": "literal" if variant == token else "encoded",
                    "offset": idx,
                    "context": mask(text[max(0, idx - 20): idx + 40], 0),
                }
                break
        if matched is None:
            # Fallback: whitespace-tolerant compare, only after every literal
            # variant has failed.
            if compact_text is None:
                compact_text = re.sub(r"\s+", "", text).lower()
            compact = re.sub(r"\s+", "", token).lower()
            if len(compact) >= 6 and compact in compact_text:
                matched = {"canary": mask(token, 4), "match": "whitespace-tolerant"}
        if matched:
            hits.append(matched)
    return hits


def scan_patterns(text: str, include_pii: bool) -> list[dict]:
    findings = []
    for pid, category, severity, weight, pattern in PATTERNS:
        if category == "pii" and not include_pii and pid in ("pii.email", "pii.phone"):
            continue
        for match in pattern.finditer(text):
            value = match.group(0)
            if pid == "pii.credit_card":
                if not luhn_ok(value):
                    continue
            if pid == "pii.phone" and len(re.sub(r"\D", "", value)) < 7:
                continue
            if pid == "secret.env_dump":
                # Require a secret-looking value, not any KEY=value line.
                rhs = value.split("=", 1)[1] if "=" in value else ""
                if not (shannon_entropy(rhs.strip()) > 3.0 or SECRET_KEYWORD_RE.search(value)):
                    continue
            findings.append({
                "id": pid, "category": category, "severity": severity,
                "weight": weight, "excerpt": mask(value),
                "offset": match.start(), "count": 1,
            })
            break  # one example per pattern is enough for a verdict
    return findings


def scan_entropy(text: str) -> list[dict]:
    findings = []
    for match in ENTROPY_TOKEN_RE.finditer(text):
        token = match.group(0)
        if len(token) < 40:
            continue
        if shannon_entropy(token) < 4.3:
            continue
        has_digit = any(c.isdigit() for c in token)
        has_alpha = any(c.isalpha() for c in token)
        if not (has_digit and has_alpha):
            continue
        window = text[max(0, match.start() - 60): match.start()]
        if not SECRET_KEYWORD_RE.search(window):
            continue
        findings.append({
            "id": "secret.high_entropy", "category": "secret", "severity": "high",
            "weight": 26, "excerpt": mask(token), "offset": match.start(), "count": 1,
        })
        break
    return findings


def scan_exfil(text: str, allow_hosts: set[str]) -> list[dict]:
    findings = []

    def add(pid: str, severity: str, weight: int, value: str, offset: int) -> None:
        findings.append({
            "id": pid, "category": "exfiltration", "severity": severity,
            "weight": weight, "excerpt": mask(value, 30), "offset": offset, "count": 1,
        })

    for match in EXFIL_MD_IMAGE_RE.finditer(text):
        url = match.group(2)
        if not is_remote(url):
            continue
        host = host_of(url)
        if host in allow_hosts:
            continue
        query = urlsplit(url).query if "://" in url else ""
        weight = 38 if query else 30
        add("exfil.markdown_image", "high", weight, url, match.start())
        if query and (len(query) > 40 or shannon_entropy(unquote(query)) > 3.6):
            add("exfil.encoded_query", "critical", 40, url, match.start())

    for match in EXFIL_HTML_IMG_RE.finditer(text):
        url = match.group(2)
        if is_remote(url) and host_of(url) not in allow_hosts:
            add("exfil.html_image", "high", 30, url, match.start())

    for match in EXFIL_DATA_URI_RE.finditer(text):
        add("exfil.data_uri", "high", 32, match.group(0)[:60], match.start())

    for match in EXFIL_RAW_URL_RE.finditer(text):
        url = match.group(0)
        host = host_of(url)
        if any(host == bad or host.endswith("." + bad) for bad in WEBHOOK_HOSTS):
            add("exfil.webhook_domain", "critical", 40, url, match.start())
            continue
        query = urlsplit(url).query
        if query:
            decoded = unquote(query)
            if len(decoded) > 120 and shannon_entropy(decoded) > 4.0:
                add("exfil.high_entropy_query", "high", 30, url, match.start())

    return findings


# --------------------------------------------------------------------------
# Sanitizing
# --------------------------------------------------------------------------

def sanitize(text: str, mode: str, allow_hosts: set[str], redact: bool,
             strict_links: bool = False) -> tuple[str, dict]:
    stats = {"mode": mode, "images_blocked": 0, "links_blocked": 0,
             "tags_removed": 0, "control_chars_removed": 0}

    if mode == "terminal":
        before = text
        text = ANSI_RE.sub("", text)
        text = CONTROL_RE.sub("", text)
        text = BIDI_RE.sub("", text)
        text = ZERO_WIDTH_RE.sub("", text)
        stats["control_chars_removed"] = len(before) - len(text)
        return text, stats

    if mode in ("chat", "markdown", "html"):
        text, n = DANGEROUS_BLOCK_RE.subn("", text)
        stats["tags_removed"] += n
        text, n = SELF_CLOSING_DANGER_RE.subn("", text)
        stats["tags_removed"] += n
        text, n = EVENT_ATTR_RE.subn("", text)
        stats["tags_removed"] += n
        text, n = STYLE_ATTR_RE.subn("", text) if mode == "html" else (text, 0)
        stats["tags_removed"] += n
        text = JS_URL_RE.sub("blocked-scheme:", text)
        text = STYLE_URL_RE.sub("blocked-uri(", text)
        text = BIDI_RE.sub("", text)

        def image_repl(match: re.Match) -> str:
            alt, url = match.group(1), match.group(2)
            if not is_remote(url):
                return f"[image removed: {url.split(':', 1)[0]} URI]" if url.lower().startswith("data:") else match.group(0)
            host = host_of(url)
            if host in allow_hosts:
                return match.group(0)
            stats["images_blocked"] += 1
            return f"[image removed: {host or 'unknown host'}]"

        text = EXFIL_MD_IMAGE_RE.sub(image_repl, text)

        def link_repl(match: re.Match) -> str:
            label, url = match.group(1), match.group(2)
            lowered = url.strip().lower()
            if lowered.startswith(("javascript:", "vbscript:", "data:")):
                stats["links_blocked"] += 1
                return label or "[link removed]"
            if not is_remote(url):
                return match.group(0)
            host = host_of(url)
            if host in allow_hosts:
                return match.group(0)
            stats["links_blocked"] += 1
            return f"{label} (link blocked: {host or 'unknown host'})"

        # Links need a click to fire, so rewriting them is opt-in. Schemes that
        # execute on click are always neutralized.
        if strict_links:
            text = EXFIL_MD_LINK_RE.sub(link_repl, text)
        else:
            text = EXFIL_MD_LINK_RE.sub(
                lambda m: f"{m.group(1)} ({m.group(2)})" if m.group(2).strip().lower().startswith(("javascript:", "vbscript:", "data:")) else m.group(0),
                text,
            )

        if redact:
            text = EXFIL_DATA_URI_RE.sub("[REDACTED:data-uri]", text)

    return text, stats


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def analyze(text: str, args: argparse.Namespace) -> tuple[dict, str]:
    allow_hosts = {h.lower().strip() for h in (args.allow_host or []) if h.strip()}
    canaries = load_canaries(args.canary or [], args.canary_file)

    canary_hits = check_canaries(text, canaries)
    findings = scan_patterns(text, args.pii) + scan_entropy(text)
    findings += scan_exfil(text, allow_hosts)

    sanitized, stats = sanitize(text, args.mode, allow_hosts, args.redact, args.strict_links)

    if args.redact:
        for pid, category, severity, weight, pattern in PATTERNS:
            if category == "pii" and not args.pii and pid in ("pii.email", "pii.phone"):
                continue
            sanitized = pattern.sub(lambda m, p=pid: f"[REDACTED:{p.split('.')[-1]}]", sanitized)

    changed = sanitized != text
    critical = any(f["severity"] == "critical" for f in findings)

    if canary_hits or critical:
        verdict = "block"
    elif findings or changed:
        verdict = "redact"
    else:
        verdict = "pass"

    score = min(100, sum(f["weight"] for f in findings) + (50 if canary_hits else 0))

    result = {
        "tool": TOOL,
        "version": VERSION,
        "verdict": verdict,
        "score": score,
        "mode": args.mode,
        "canary_hits": canary_hits,
        "findings": sorted(findings, key=lambda f: -f["weight"]),
        "categories": sorted({f["category"] for f in findings} | ({"canary"} if canary_hits else set())),
        "sanitizer": stats,
        "changed": changed,
        "sanitized_chars": len(sanitized),
        "note": "A pass means no known pattern matched. It is not proof the output is safe.",
    }
    if args.emit_text:
        result["sanitized_text"] = sanitized
    return result, sanitized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan agent output for canaries, secrets, exfil channels, render payloads.",
        epilog="Exit codes: 0 pass, 10 redacted, 20 block, 1 error.",
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--text", help="output text to scan")
    src.add_argument("--file", help="read output from this file ('-' for stdin)")
    parser.add_argument("--mode", default="chat",
                        choices=["chat", "markdown", "html", "terminal", "none"],
                        help="rendering target (default: chat)")
    parser.add_argument("--canary", action="append", metavar="TOKEN",
                        help="canary token to look for (repeatable)")
    parser.add_argument("--canary-file", help="file with one canary token per line")
    parser.add_argument("--allow-host", action="append", metavar="HOST",
                        help="host allowed for images and links (repeatable)")
    parser.add_argument("--pii", action="store_true", help="also flag emails and phone numbers")
    parser.add_argument("--strict-links", action="store_true",
                        help="also rewrite links to non-allowlisted hosts (default: keep, "
                             "since a link needs a click)")
    parser.add_argument("--redact", action="store_true",
                        help="replace secret matches with [REDACTED:<kind>]")
    parser.add_argument("--out", metavar="PATH", help="write the sanitized text here")
    parser.add_argument("--emit-text", action="store_true",
                        help="include sanitized text in the JSON on stdout")
    parser.add_argument("--compact", action="store_true", help="omit findings from the JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    try:
        if args.text is not None:
            text = args.text
        elif args.file:
            if args.file == "-":
                text = sys.stdin.read()
            else:
                with open(args.file, "r", encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
        elif not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            parser.error("provide --text, --file, or pipe text on stdin")
            return 1
    except OSError as exc:
        print(json.dumps({"tool": TOOL, "error": f"read failed: {exc}"}))
        return 1

    result, sanitized = analyze(text, args)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(sanitized)
            result["written"] = os.path.abspath(args.out)
        except OSError as exc:
            result["write_error"] = str(exc)

    if args.compact:
        result.pop("findings", None)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {"pass": 0, "redact": 10, "block": 20}.get(result["verdict"], 1)


if __name__ == "__main__":
    sys.exit(main())
