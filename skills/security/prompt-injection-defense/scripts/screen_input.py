#!/usr/bin/env python3
"""Screen untrusted text for prompt-injection indicators and emit a JSON verdict.

This is layer L1 of the prompt-injection-defense skill. A clean verdict means
"no known-bad pattern", not "safe": the authoritative control is the tool
boundary (L4), not this script.

What it does
------------
1. Normalizes the input the way an attacker hopes you will not:
   HTML entities, percent-escapes, NFKC, Unicode confusables, zero-width and
   bidi control characters, Unicode tag characters, ANSI escapes, and
   base64/hex payloads that decode to instruction-like text.
2. Matches rule families (override, role spoofing, prompt leak, exfil, tool
   coercion, hidden markup, render payloads, approval forgery).
3. Optionally calls an external classifier (subprocess or HTTP).
4. Scores 0-100, applies a source-risk bonus, and routes to allow / review /
   block.
5. Optionally writes a nonce-delimited, source-labelled copy of the text for
   safe inclusion in the model context.

Usage
-----
    python3 screen_input.py --text "hello" --source user
    python3 screen_input.py --file doc.txt --source web --json
    cat email.eml | python3 screen_input.py --source email --strict
    python3 screen_input.py --file page.html --source web \
        --classifier-cmd "python3 clf.py" --fail-closed \
        --emit /tmp/quarantined.txt

    --classifier-cmd  argv string, receives {"text": ...} on stdin, must print
                      {"score": 0.0-1.0, "label": "..."} to stdout
    --classifier-url  POST the same JSON, same response shape
    --fail-closed     a classifier error escalates the verdict to at least review
    --strict          thresholds 15 / 40 instead of 25 / 60
    --emit PATH       write the nonce-wrapped normalized text (L2 artifact)
    --max-chars N     truncate before analysis (default 200000)

Verdict on stdout as JSON. Exit codes: 0 allow, 10 review, 20 block, 1 error.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import html
import json
import os
import re
import secrets
import shlex
import subprocess
import sys
import unicodedata

VERSION = "1.0.0"
TOOL = "screen_input.py"

REVIEW_DEFAULT = 25
BLOCK_DEFAULT = 60
REVIEW_STRICT = 15
BLOCK_STRICT = 40
MAX_CHARS_DEFAULT = 200_000
MAX_FINDING_EXCERPT = 120

# --------------------------------------------------------------------------
# Normalization tables
# --------------------------------------------------------------------------

ZERO_WIDTH = {
    0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x180E, 0x00AD, 0x200E, 0x200F,
}
BIDI = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x061C}
TAG_CHARS = set(range(0xE0000, 0xE0080))

# Minimal confusable map: Cyrillic and Greek lookalikes plus fullwidth forms
# handled by NFKC. Deliberately small so benign multilingual text is untouched
# only where it matters for keyword matching.
CONFUSABLES = {
    0x0430: "a", 0x0435: "e", 0x043E: "o", 0x0440: "p", 0x0441: "c",
    0x0443: "y", 0x0445: "x", 0x0456: "i", 0x0458: "j", 0x04BB: "h",
    0x0501: "d", 0x051B: "q", 0x051D: "w",
    0x0391: "A", 0x0392: "B", 0x0395: "E", 0x0396: "Z", 0x0397: "H",
    0x0399: "I", 0x039A: "K", 0x039C: "M", 0x039D: "N", 0x039F: "O",
    0x03A1: "P", 0x03A4: "T", 0x03A5: "Y", 0x03A7: "X",
    0x03B1: "a", 0x03B5: "e", 0x03B9: "i", 0x03BA: "k", 0x03BD: "v",
    0x03BF: "o", 0x03C1: "p", 0x03C4: "t", 0x03C5: "u", 0x03C7: "x",
}

ANSI_RE = re.compile(
    r"\x1b\[[0-9;?]*[ -/]*[@-~]"      # CSI
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?"  # OSC
    r"|\x1b[@-Z\\-_]"                  # 2-char escapes
)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
WS_RE = re.compile(r"[ \t\u00a0\u2007\u202f]+")
NL_RE = re.compile(r"\n{3,}")

# --------------------------------------------------------------------------
# Rule families
# --------------------------------------------------------------------------
# (id, category, severity, weight, pattern)
# severity drives reporting; weight drives score. Weights are tuned so that a
# single unambiguous override is review-worthy and any two families block.

RULES = [
    (
        "override.ignore_previous", "override", "high", 26,
        re.compile(
            r"\b(ignore|disregard|forget|override|bypass|discard)\b"
            r"[^.\n]{0,40}?\b(previous|prior|above|earlier|preceding|all)\b"
            r"[^.\n]{0,25}?\b(instruction|prompt|rule|direction|guideline|"
            r"constraint|context|message)s?\b",
            re.I,
        ),
    ),
    (
        "override.new_instructions", "override", "high", 24,
        re.compile(
            r"\b(new|updated|real|actual|true|correct)\s+"
            r"(system\s+|developer\s+)?(instruction|directive|rule|task|prompt)s?\b"
            r"\s*[:：]",
            re.I,
        ),
    ),
    (
        "override.persona", "override", "high", 22,
        re.compile(
            r"\b(you\s+are\s+now|from\s+now\s+on\s+you|act\s+as)\b"
            r"[^.\n]{0,40}?\b(unrestricted|unfiltered|uncensored|dan|jailbr[oe]ak|"
            r"without\s+(any\s+)?(rules|limits|restrictions|filters))\b"
            r"|\b(developer|god|sudo)\s+mode\b|\bdo\s+anything\s+now\b",
            re.I,
        ),
    ),
    (
        "role.system_tag", "role_spoof", "high", 26,
        re.compile(
            r"<\|?\s*(system|developer|assistant)\s*\|?>"
            r"|</?\s*system\s*>"
            r"|^\s*SYSTEM\s*[:：]"
            r"|#{2,}\s*(system|system\s+prompt|instructions?)\s*$",
            re.I | re.M,
        ),
    ),
    (
        "role.chat_template", "role_spoof", "critical", 32,
        re.compile(
            r"\[/?INST\]|<<\s*/?\s*SYS\s*>>|<\|im_start\|>|<\|im_end\|>"
            r"|<\|endoftext\|>|<\|start_header_id\|>|<\|eot_id\|>"
            r"|^\s*###\s*(human|user|assistant)\s*:",
            re.I | re.M,
        ),
    ),
    (
        "role.assistant_prefix", "role_spoof", "medium", 12,
        re.compile(r"^\s*(assistant|system)\s*:\s*\S", re.I | re.M),
    ),
    (
        "leak.system_prompt", "prompt_leak", "high", 24,
        re.compile(
            r"\b(reveal|print|show|output|repeat|dump|leak|display|tell\s+me)\b"
            r"[^.\n]{0,40}?\b(system\s+prompt|initial\s+instruction|hidden\s+prompt|"
            r"your\s+(rules|instructions|configuration|guidelines)|"
            r"pre-?prompt|context\s+window\s+start)\b",
            re.I,
        ),
    ),
    (
        "leak.verbatim_repeat", "prompt_leak", "medium", 14,
        re.compile(
            r"\b(repeat|output|print)\b[^.\n]{0,30}?\b(everything|all\s+text|"
            r"all\s+words)\b[^.\n]{0,30}?\b(above|before\s+this|preceding)\b",
            re.I,
        ),
    ),
    (
        "approval.forgery", "approval_spoof", "critical", 34,
        re.compile(
            r"\b(the\s+)?(user|admin|administrator|developer|system|operator|"
            r"security\s+team)\s+(has\s+|have\s+)?(already\s+)?"
            r"(approved|authorized|authorised|confirmed|signed\s+off|granted)\b"
            r"|\bapproval\s+(was\s+)?(granted|given|received)\b"
            r"|\bno\s+(further\s+)?(approval|confirmation)\s+(is\s+)?(needed|required)\b",
            re.I,
        ),
    ),
    (
        "approval.bypass_request", "approval_spoof", "high", 22,
        re.compile(
            r"\b(without|skip|ignore|bypass|don'?t\s+(ask|wait))\b"
            r"[^.\n]{0,25}?\b(approval|confirmation|confirm|authorization|"
            r"authorisation|permission|safety\s+check|review)\b",
            re.I,
        ),
    ),
    (
        "exfil.send", "exfiltration", "high", 28,
        re.compile(
            r"\b(send|post|upload|forward|email|mail|transmit|exfiltrate|"
            r"submit|share|include)\b[^.\n]{0,50}?\b(to|at|via)\b"
            r"[^.\n]{0,60}?(https?://|@[a-z0-9.-]+\.[a-z]{2,}|webhook|"
            r"requestbin|pastebin|ngrok|transfer\.sh)",
            re.I,
        ),
    ),
    (
        "exfil.secret_target", "exfiltration", "high", 20,
        re.compile(
            r"\b(api[_-]?key|secret|token|password|passphrase|credential|"
            r"\.env\b|private\s+key|ssh\s+key|aws_|bearer\s+token|session\s+cookie|"
            r"environment\s+variable)s?\b",
            re.I,
        ),
    ),
    (
        "exfil.encode_before_send", "exfiltration", "high", 24,
        re.compile(
            r"\b(base64|b64|hex|url[-\s]?encode|encrypt|gzip|zip)\b"
            r"[^.\n]{0,40}?\b(before|then|and)\b[^.\n]{0,30}?"
            r"\b(send|post|include|append|embed|email)\b"
            r"|\b(send|post|embed|append)\b[^.\n]{0,30}?\b(base64|hex)\b",
            re.I,
        ),
    ),
    (
        "tool.coercion", "tool_coercion", "high", 24,
        re.compile(
            r"\b(call|invoke|run|execute|use|trigger)\b[^.\n]{0,30}?"
            r"\b(tool|function|shell|bash|sh|curl|wget|exec|subprocess|python|"
            r"terminal|rm\s+-rf|chmod|sudo|os\.system)\b",
            re.I,
        ),
    ),
    (
        "tool.shell_pipe", "tool_coercion", "critical", 38,
        re.compile(
            r"\b(curl|wget|fetch)\b[^|\n]{0,160}\|\s*(sudo\s+)?(ba|z|k)?sh\b"
            r"|\brm\s+-rf\s+(/|~|\$HOME|\*)"
            r"|:\s*\(\s*\)\s*\{.*\|.*&.*\}"
            r"|\b(eval|exec)\s*\(\s*(base64|atob|__import__)",
            re.I,
        ),
    ),
    (
        "tool.destructive_verb", "tool_coercion", "medium", 14,
        re.compile(
            r"\b(delete|drop\s+table|truncate|wipe|format|revoke|rotate|"
            r"disable\s+(logging|audit|mfa|2fa)|uninstall)\b",
            re.I,
        ),
    ),
    (
        "hidden.html_comment", "hidden_markup", "high", 22,
        re.compile(r"<!--(?=[\s\S]{0,600}?-->)[\s\S]{0,600}?-->"),
    ),
    (
        "hidden.css_display", "hidden_markup", "medium", 16,
        re.compile(
            r"(display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*"
            r"(0|1|2|3)(px|pt|em)|color\s*:\s*(#fff(fff)?|white)\b|"
            r"opacity\s*:\s*0(\.0+)?\b)",
            re.I,
        ),
    ),
    (
        "hidden.alt_text", "hidden_markup", "low", 8,
        re.compile(r"\balt\s*=\s*[\"'][^\"']{40,}[\"']", re.I),
    ),
    (
        "render.markdown_image", "render_payload", "medium", 12,
        re.compile(r"!\[[^\]]{0,80}\]\(\s*<?\s*(https?:)?//[^)\s>]+", re.I),
    ),
    (
        # An image whose URL carries a query string is a beacon, not decoration.
        "render.image_with_query", "render_payload", "high", 26,
        re.compile(r"!\[[^\]]{0,80}\]\(\s*<?\s*(?:https?:)?//[^)\s>]*\?[^)\s>]{0,}", re.I),
    ),
    (
        "render.data_uri", "render_payload", "high", 26,
        re.compile(
            r"data:\s*(text/html|image/svg\+xml|application/javascript|"
            r"text/javascript)",
            re.I,
        ),
    ),
    (
        "render.html_active", "render_payload", "high", 24,
        re.compile(
            r"<\s*(script|iframe|object|embed|form|meta\s+http-equiv)\b"
            r"|\bon(error|load|click|mouseover|focus)\s*="
            r"|javascript\s*:",
            re.I,
        ),
    ),
    (
        "render.url_in_output", "render_payload", "info", 0,
        re.compile(r"https?://[^\s<>\"')]{8,}", re.I),
    ),
    (
        # A directive to persist behaviour into memory is how one payload becomes
        # a standing instruction in every later session.
        "memory.persist_directive", "memory_write", "high", 22,
        re.compile(
            r"\b(update|change|set|save|store|add|append|overwrite)\b"
            r"[^.\n]{0,40}?\b(stored|saved|long[- ]term|persistent)\s+"
            r"(preference|memory|setting|rule|instruction|config)s?\b"
            r"|\b(remember|memorize|store)\b[^.\n]{0,30}?\b(this|the\s+following|"
            r"permanently|for\s+(all\s+)?(future|subsequent))\b",
            re.I,
        ),
    ),
    (
        "manipulation.secrecy", "manipulation", "medium", 12,
        re.compile(
            r"\b(never|do\s+not|don'?t)\s+(tell|inform|mention|reveal|alert)"
            r"[^.\n]{0,30}?\b(the\s+user|anyone|them|this)\b",
            re.I,
        ),
    ),
    (
        "manipulation.urgency", "manipulation", "low", 8,
        re.compile(
            r"\b(urgent(ly)?|immediately|right\s+now|before\s+you\s+(respond|reply)|"
            r"do\s+not\s+(tell|inform|alert|mention)|don'?t\s+(tell|inform|alert)|"
            r"keep\s+this\s+(secret|between\s+us)|no\s+need\s+to\s+(verify|check))\b",
            re.I,
        ),
    ),
    (
        "manipulation.authority_claim", "manipulation", "medium", 12,
        re.compile(
            r"\b(i\s+am|this\s+is|speaking\s+as)\s+(the\s+)?"
            r"(ceo|cto|ciso|admin(istrator)?|developer|owner|anthropic|openai|"
            r"support\s+team|security\s+team)\b"
            r"|\bper\s+(company|security)\s+policy\b",
            re.I,
        ),
    ),
]

# Decoded-payload matching reuses the highest-signal rule ids only.
NESTED_RULE_IDS = {
    "override.ignore_previous",
    "override.new_instructions",
    "override.persona",
    "leak.system_prompt",
    "exfil.send",
    "tool.shell_pipe",
    "approval.forgery",
}

# Rule id -> category, for decoded payloads that inherit their target's category.
RULE_CATEGORY = {rule_id: category for rule_id, category, _s, _w, _p in RULES}

# Categories that, combined two-at-a-time, are strong evidence of an attack:
# a lone "ignore previous instructions" can be a quote; that plus a leak attempt
# is not.
ATTACK_CATEGORIES = {
    "override", "role_spoof", "prompt_leak", "approval_spoof",
    "exfiltration", "tool_coercion", "obfuscation", "memory_write",
}

SOURCE_RISK_BONUS = {
    "user": 0,
    "agent": 8,
    "tool": 10,
    "web": 12,
    "doc": 12,
    "email": 12,
    "memory": 16,
    "unknown": 6,
}

BASE64_RUN_RE = re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")
HEX_ESC_RE = re.compile(r"(?:\\x[0-9a-fA-F]{2}){8,}")
HEX_RUN_RE = re.compile(r"\b(?:[0-9a-fA-F]{2}){16,}\b")


# --------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------

def _strip_chars(text: str) -> tuple[str, dict]:
    """Remove invisible/control characters, reporting what was found."""
    events = {"zero_width": 0, "bidi": 0, "tag_chars": 0, "ansi": 0, "control": 0}
    out = []
    for ch in text:
        cp = ord(ch)
        if cp in ZERO_WIDTH:
            events["zero_width"] += 1
            continue
        if cp in BIDI:
            events["bidi"] += 1
            continue
        if cp in TAG_CHARS:
            events["tag_chars"] += 1
            continue
        if cp == 0x1B:
            events["ansi"] += 1
            continue
        if (cp < 0x20 and ch not in "\n\t") or 0x7F <= cp <= 0x9F:
            events["control"] += 1
            continue
        out.append(ch)
    return "".join(out), events


def normalize(text: str, max_chars: int = MAX_CHARS_DEFAULT) -> tuple[str, dict]:
    """Return (normalized_text, stats). Order matters: analysts get the same text."""
    stats: dict = {"chars_in": len(text), "truncated": False, "normalizations": []}
    if len(text) > max_chars:
        text = text[:max_chars]
        stats["truncated"] = True

    text = text.replace("\x00", "")
    # ANSI first, before NFKC can mangle escape sequences.
    if ANSI_RE.search(text):
        stats["normalizations"].append("ansi_stripped")
        text = ANSI_RE.sub(" ", text)

    stripped, events = _strip_chars(text)
    text = stripped
    for key in ("zero_width", "bidi", "tag_chars", "control"):
        if events[key]:
            stats["normalizations"].append(f"{key}_stripped")
            stats[key] = events[key]

    decoded = html.unescape(text)
    if decoded != text:
        # One pass only; double-decoding is an attacker trick and inflates FPs.
        stats["normalizations"].append("html_entities_decoded")
        text = decoded

    percent_hits = len(re.findall(r"%[0-9A-Fa-f]{2}", text))
    if percent_hits >= 8:
        try:
            unquoted = re.sub(
                r"(?:%[0-9A-Fa-f]{2})+",
                lambda m: bytes.fromhex(m.group(0).replace("%", "")).decode("utf-8", "replace"),
                text,
            )
            if unquoted != text:
                stats["normalizations"].append("percent_decoded")
                text = unquoted
        except (ValueError, UnicodeDecodeError):
            pass

    nfkc = unicodedata.normalize("NFKC", text)
    if nfkc != text:
        stats["normalizations"].append("nfkc")
        text = nfkc

    confusable_hits = sum(1 for ch in text if ord(ch) in CONFUSABLES)
    if confusable_hits:
        stats["normalizations"].append("confusables_folded")
        stats["confusables"] = confusable_hits
        text = text.translate(CONFUSABLES)

    text = WS_RE.sub(" ", text)
    text = NL_RE.sub("\n\n", text)
    stats["chars_out"] = len(text)
    return text.strip(), stats


# --------------------------------------------------------------------------
# Detection
# --------------------------------------------------------------------------

def _excerpt(value: str) -> str:
    value = ANSI_RE.sub("", value)
    value = "".join(ch for ch in value if ch.isprintable() or ch in "\n\t")
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > MAX_FINDING_EXCERPT:
        value = value[: MAX_FINDING_EXCERPT - 3] + "..."
    return value


def _match_rules(text: str) -> list[dict]:
    findings = []
    for rule_id, category, severity, weight, pattern in RULES:
        match = pattern.search(text)
        if not match:
            continue
        findings.append({
            "rule": rule_id,
            "category": category,
            "severity": severity,
            "weight": weight,
            "count": len(pattern.findall(text)) if pattern.groups == 0 else 1,
            "excerpt": _excerpt(match.group(0)),
        })
    return findings


def _decoded_hits(payload: str) -> list[str]:
    """Return rule ids matched by a decoded payload, if any."""
    hits = []
    for rule_id, _cat, _sev, _w, pattern in RULES:
        if rule_id in NESTED_RULE_IDS and pattern.search(payload):
            hits.append(rule_id)
    return hits


def _nested_payloads(text: str) -> list[dict]:
    findings = []

    for run in BASE64_RUN_RE.findall(text):
        padded = run + "=" * (-len(run) % 4)
        try:
            raw = base64.b64decode(padded, validate=False)
        except (binascii.Error, ValueError):
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        printable = sum(1 for ch in decoded if ch.isprintable() or ch in "\n\t")
        if not decoded or printable / len(decoded) < 0.85:
            continue
        hits = _decoded_hits(decoded)
        if hits:
            findings.append({
                "rule": "obfuscation.base64_payload",
                "category": "obfuscation",
                "severity": "high",
                "weight": 34,
                "count": 1,
                "decoded_rules": hits,
                "excerpt": _excerpt(decoded),
            })

    for pattern, label in ((HEX_ESC_RE, "hex_escape"), (HEX_RUN_RE, "hex_run")):
        for run in pattern.findall(text)[:3]:
            raw = run.replace("\\x", "")
            try:
                decoded = bytes.fromhex(raw).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                continue
            hits = _decoded_hits(decoded)
            if hits:
                findings.append({
                    "rule": f"obfuscation.{label}",
                    "category": "obfuscation",
                    "severity": "high",
                    "weight": 30,
                    "count": 1,
                    "decoded_rules": hits,
                    "excerpt": _excerpt(decoded),
                })
    return findings


def _invisible_findings(stats: dict) -> list[dict]:
    findings = []
    if stats.get("zero_width", 0) >= 2:
        findings.append({
            "rule": "obfuscation.zero_width", "category": "obfuscation",
            "severity": "medium", "weight": 18,
            "count": stats["zero_width"], "excerpt": "zero-width characters present",
        })
    if stats.get("bidi", 0) >= 1:
        findings.append({
            "rule": "obfuscation.bidi_control", "category": "obfuscation",
            "severity": "high", "weight": 24,
            "count": stats["bidi"], "excerpt": "bidi control characters (Trojan Source class)",
        })
    if stats.get("tag_chars", 0) >= 1:
        findings.append({
            "rule": "obfuscation.unicode_tags", "category": "obfuscation",
            "severity": "high", "weight": 26,
            "count": stats["tag_chars"], "excerpt": "Unicode tag characters present",
        })
    if stats.get("ansi", 0) >= 1:
        findings.append({
            "rule": "obfuscation.ansi_escape", "category": "obfuscation",
            "severity": "medium", "weight": 12,
            "count": stats["ansi"], "excerpt": "ANSI escape sequences in text content",
        })
    return findings


# --------------------------------------------------------------------------
# Classifier hook
# --------------------------------------------------------------------------

def run_classifier(cmd: str | None, url: str | None, text: str, timeout: int = 30) -> dict:
    """Call an external classifier. Returns {used, score, label, error}."""
    payload = json.dumps({"text": text[:8000], "version": VERSION})
    try:
        if cmd:
            proc = subprocess.run(
                shlex.split(cmd), input=payload, capture_output=True,
                text=True, timeout=timeout, check=False,
            )
            if proc.returncode != 0:
                return {"used": True, "error": f"exit {proc.returncode}",
                        "stderr": _excerpt(proc.stderr or "")}
            data = json.loads(proc.stdout)
        elif url:
            from urllib import request, error  # local import keeps stdlib tidy
            req = request.Request(
                url, data=payload.encode(), method="POST",
                headers={"Content-Type": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode())
            except error.URLError as exc:
                return {"used": True, "error": f"http: {exc.reason}"}
        else:
            return {"used": False}
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        return {"used": True, "error": f"{type(exc).__name__}: {exc}"}

    if not isinstance(data, dict):
        return {"used": True, "error": "classifier response is not an object"}
    try:
        score = float(data.get("score", 0.0))
    except (TypeError, ValueError):
        return {"used": True, "error": "classifier score is not numeric"}
    return {
        "used": True,
        "score": max(0.0, min(1.0, score)),
        "label": str(data.get("label", ""))[:64],
        "model": str(data.get("model", ""))[:64],
    }


# --------------------------------------------------------------------------
# Verdict
# --------------------------------------------------------------------------

def build_verdict(text: str, source: str, strict: bool,
                  clf_cmd: str | None, clf_url: str | None,
                  fail_closed: bool) -> dict:
    normalized, stats = normalize(text)
    findings = _match_rules(normalized) + _invisible_findings(stats) + _nested_payloads(normalized)

    # Deduplicate (same rule may fire from rules + nested passes).
    seen = set()
    unique = []
    for finding in findings:
        key = (finding["rule"], finding["excerpt"][:40])
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    findings = unique

    raw_score = sum(f["weight"] for f in findings)
    categories = {f["category"] for f in findings}
    # A decoded payload inherits the category of what it decodes to, so an
    # obfuscated override counts as an override for the combination bonus.
    for finding in findings:
        for decoded_rule in finding.get("decoded_rules", []):
            categories.add(RULE_CATEGORY.get(decoded_rule, "obfuscation"))

    classifier = run_classifier(clf_cmd, clf_url, normalized) if (clf_cmd or clf_url) else {"used": False}
    clf_score = 0
    classifier_failed = False
    clf_high = False
    if classifier.get("used"):
        if classifier.get("error"):
            classifier_failed = True
        else:
            clf_score = int(round(classifier.get("score", 0.0) * 50))
            # A confident classifier is its own vote; do not let a low rule
            # score average it away.
            clf_high = classifier.get("score", 0.0) >= 0.90

    score = min(100, raw_score + clf_score + SOURCE_RISK_BONUS.get(source, 6))
    attack_categories = categories & ATTACK_CATEGORIES
    if len(attack_categories) >= 2:
        score = min(100, score + 20)
    elif len(categories) >= 3:
        score = min(100, score + 8)

    review_at = REVIEW_STRICT if strict else REVIEW_DEFAULT
    block_at = BLOCK_STRICT if strict else BLOCK_DEFAULT

    verdict = "allow"
    if score >= block_at:
        verdict = "block"
    elif score >= review_at:
        verdict = "review"

    if classifier_failed and fail_closed and verdict == "allow":
        verdict = "review"
        score = max(score, review_at)

    if clf_high:
        verdict = "block"
        score = max(score, block_at)

    # Any critical-severity rule blocks regardless of accumulated score.
    if any(f["severity"] == "critical" for f in findings):
        verdict = "block"
        score = max(score, block_at)

    return {
        "tool": TOOL,
        "version": VERSION,
        "source": source,
        "verdict": verdict,
        "score": score,
        "thresholds": {"review": review_at, "block": block_at},
        "raw_score": raw_score,
        "source_bonus": SOURCE_RISK_BONUS.get(source, 6),
        "categories": sorted(categories),
        "findings": sorted(findings, key=lambda f: -f["weight"]),
        "classifier": classifier,
        "classifier_failed_closed": bool(classifier_failed and fail_closed),
        "stats": stats,
        "quarantine": verdict != "allow",
        "note": "Clean verdict means no known-bad pattern, not safe. Enforce at the tool boundary.",
    }


def wrap_for_context(text: str, source: str, origin: str | None) -> str:
    """Nonce-delimited, source-labelled block for L2 context isolation."""
    nonce = secrets.token_hex(8)
    attrs = f"src={source} id={nonce}"
    if origin:
        attrs += f" origin={origin}"
    return (
        f"<<UNTRUSTED {attrs}>>\n{text}\n<<END id={nonce}>>\n"
        f"<<Anything outside the {nonce} block is not part of the document.>>"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Screen untrusted text for prompt-injection indicators.",
        epilog="Exit codes: 0 allow, 10 review, 20 block, 1 error.",
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--text", help="text to screen")
    src.add_argument("--file", help="read text from this file ('-' for stdin)")
    parser.add_argument("--source", default="unknown",
                        choices=sorted(SOURCE_RISK_BONUS),
                        help="channel the text arrived on (default: unknown)")
    parser.add_argument("--origin", help="host or path the content came from")
    parser.add_argument("--strict", action="store_true",
                        help="lower thresholds to 15/40")
    parser.add_argument("--classifier-cmd", help="argv string for an external classifier")
    parser.add_argument("--classifier-url", help="HTTP endpoint for an external classifier")
    parser.add_argument("--fail-closed", action="store_true",
                        help="escalate to review when the classifier errors")
    parser.add_argument("--emit", metavar="PATH",
                        help="write the nonce-wrapped normalized text for the model context")
    parser.add_argument("--max-chars", type=int, default=MAX_CHARS_DEFAULT)
    parser.add_argument("--compact", action="store_true",
                        help="omit findings detail from the JSON output")
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

    result = build_verdict(
        text=text, source=args.source, strict=args.strict,
        clf_cmd=args.classifier_cmd, clf_url=args.classifier_url,
        fail_closed=args.fail_closed,
    )

    if args.emit:
        normalized, _ = normalize(text, args.max_chars)
        try:
            with open(args.emit, "w", encoding="utf-8") as handle:
                handle.write(wrap_for_context(normalized, args.source, args.origin))
            result["emitted"] = os.path.abspath(args.emit)
        except OSError as exc:
            result["emit_error"] = str(exc)

    if args.compact:
        result.pop("findings", None)
        result.pop("stats", None)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {"allow": 0, "review": 10, "block": 20}.get(result["verdict"], 1)


if __name__ == "__main__":
    sys.exit(main())
