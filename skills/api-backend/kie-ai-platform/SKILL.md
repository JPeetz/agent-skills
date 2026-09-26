---
name: kie-ai-platform
description: >-
  Use this skill when an agent needs to integrate with the Kie.ai API for
  image/video/audio generation, task management, file uploads, or callbacks.
  Activates when working with kie.ai models or the platform's asynchronous
  task API. Covers the full platform: image gen, video gen, music, chat,
  file upload, credits, webhook verification, and error handling.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - kie-ai
  - image-generation
  - video-generation
  - api
  - callbacks
  - file-upload
  - async-tasks
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# Kie.ai Platform API

[Kie.ai](https://kie.ai/?ref=7c7e62a37e5bbed684c789bbd7d6f0dd) is an API aggregator offering 30-80% cheaper access to
image, video, music, and chat models than official APIs. All generation tasks
are asynchronous. Prices at [kie.ai/pricing](https://kie.ai/pricing).
Full docs at [docs.kie.ai](https://docs.kie.ai).

**[Support Kie via this affiliate link](https://kie.ai/?ref=7c7e62a37e5bbed684c789bbd7d6f0dd) — no extra cost to you.**

## When to Use

- Generating images via GPT Image, Seedream, Flux-2, Grok Imagine, or any Kie model
- Generating or editing videos via Kling, Wan, Runway, Veo3.1, or similar
- Generating music/audio via Suno, ElevenLabs, or Gemini TTS
- Calling chat/LLM models offered at reduced prices
- Uploading files (free, no credit cost) for use as model inputs
- Monitoring credits and managing account usage
- Processing asynchronous task results via polling or webhooks

## Authentication

- **Header:** `Authorization: Bearer <api-key>`
- **Never use `x-api-key`** — returns HTTP 200 with `{"code":401,...}`
- Manage keys at [kie.ai/api-key](https://kie.ai/api-key)
- Supports IP whitelisting and per-key rate limits

## Base URLs

| Service | Base URL |
|---------|----------|
| Market API | `https://api.kie.ai` |
| File Upload API | `https://kieai.redpandaai.co` |

## Async Task Model

All generation requests are asynchronous. HTTP 200 only means the task was
**created**, not completed. Get results by either:

- **Providing a `callBackUrl`** (recommended for production) — Kie POSTs the result
- **Polling** the recordInfo endpoint

### Create Task

```
POST /api/v1/jobs/createTask
Authorization: Bearer <key>
```

Payload shape (varies per model, always has `model` and `input`):

```json
{
  "model": "gpt-image/1.5-image-to-image",
  "callBackUrl": "https://your-domain.com/api/callback",
  "input": { ... }
}
```

**Response:** `{"code":200,"msg":"success","data":{"taskId":"task_abc123"}}`

### Poll for Result

```
GET /api/v1/jobs/recordInfo?taskId={taskId}
Authorization: Bearer <key>
```

**Task states:** `waiting` → `queuing` → `generating` → `success` | `fail`

**Success response `data` fields:**
- `state`: `"success"` when complete
- `resultJson`: **Nested JSON string** — parse twice:
  `json.loads(data["resultJson"])["resultUrls"]`
- `costTime`: processing time in ms
- `creditsConsumed`: credit usage for this task
- `completeTime`: completion timestamp (Unix ms)

**Error response:** `failCode` (string), `failMsg` (string) on failure.

### Polling Best Practices

- **Use `callBackUrl` in production** — avoids polling entirely
- If polling: start at 2-3s intervals, use exponential backoff
- Stop polling after 10-15 minutes max
- Download result URLs immediately (they expire)

## Callbacks

Include `callBackUrl` in the createTask payload to receive an HTTP POST when
the task completes.

### Callback Payload (Success)

```json
POST <your-callBackUrl>
Content-Type: application/json

{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "task12345",
    "info": { "result_urls": ["https://..."] }
  }
}
```

### Callback Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success — image/video/audio ready |
| 400 | Content policy violation, invalid params |
| 451 | Failed to download from provided URL |
| 500 | Server error, retry |

### Webhook HMAC Verification

Enable on the Kie settings page to get a `webhookHmacKey`. Callbacks include:
- `X-Webhook-Timestamp` — Unix seconds
- `X-Webhook-Signature` — `base64(HMAC-SHA256(taskId + "." + timestamp, key))`

**Python verification:**
```python
import hmac, hashlib, base64
msg = f"{body['data']['taskId']}.{headers['x-webhook-timestamp']}"
expected = base64.b64encode(
    hmac.new(webhook_key.encode(), msg.encode(), hashlib.sha256).digest()
).decode()
assert hmac.compare_digest(headers['x-webhook-signature'], expected)
```

**Callback timeout:** Kie waits 15s for your server to respond.

## Common API

### Check Credits

```
GET /api/v1/chat/credit
```
Response: `{"code":200,"data":100}` (integer balance)

### Get Download URL (20 min validity)

```
POST /api/v1/common/download-url
{"url": "https://tempfile..."}
```
Response: `{"code":200,"data":"https://..."}`

## File Upload API (free, no credit cost)

Upload to `https://kieai.redpandaai.co`. Files expire after 24h.

### URL Upload (remote, ≤100MB, 30s timeout)
```
POST /api/file-url-upload
{"fileUrl":"https://...","uploadPath":"images","fileName":"img.jpg"}
```

### Stream Upload (binary, multipart)
```
POST /api/file-stream-upload (multipart/form-data)
file=<binary> | uploadPath=<path> | fileName=<name>
```

### Base64 Upload (≤10MB, ~33% size overhead)
```
POST /api/file-base64-upload
{"file":"base64string","uploadPath":"images","fileName":"img.jpg"}
```

### Upload Response
```json
{
  "success": true, "code": 200,
  "data": {
    "fileId": "file_abc123",
    "fileUrl": "https://kieai.redpandaai.co/files/...",
    "downloadUrl": "https://kieai.redpandaai.co/download/file_abc123"
  }
}
```

## Image Models

All use `POST /api/v1/jobs/createTask`. Check docs.kie.ai for each model's params.

### gpt-image/1.5-image-to-image (budget-friendly)
- Model: `gpt-image/1.5-image-to-image`
- `input` MUST be stringified JSON (`json.dumps()`) — NOT a nested dict
- `input_urls`: up to 16 URLs (JPEG/PNG/WebP, max 10MB each)
- Aspect ratios: `1:1`, `3:2`, `4:3`, `16:9`, `21:9`, etc.
- No `resolution` or `strength` or `output_format` params

**Request shape:**
```python
{
    "model": "gpt-image/1.5-image-to-image",
    "callBackUrl": "https://your-domain.com/callback",
    "input": json.dumps({
        "prompt": "Your image description",
        "input_urls": ["https://example.com/reference.jpg"],
        "aspect_ratio": "3:2",
        "quality": "medium"
    })
}
```

### Other Image Model Families
- **Seedream** 3.0–5.0 Pro — photorealistic, edit, layer decomposition
- **Google** — Imagen4 (fast/ultra), Nano Banana (edit, 2, 2 Lite, Pro)
- **Flux-2** — Pro/Flex text-to-image + image-to-image
- **Grok Imagine 2.0** — text-to-image, image-to-image, segment-map, edit
- **GPT Image** — 1.5, 2.0, 2.5 Flare/Sunburst (newer: 21:9, 4K)
- **Topaz** (upscale), **Recraft** (background removal, upscale)
- **Ideogram** v3 — text-to-image, edit, remix, character
- **Qwen** 2/2.1/3/3 Pro — text-to-image, image-to-image, edit
- **Wan 2.7** — image gen + editing
- **4o Image API** — dedicated GPT-4o endpoint at `/api/v1/gpt4o-image/generate`
- **Flux Kontext API** — dedicated endpoint

## Video Models

All use the same task-based API. Check docs for model-specific params.
- **Kling** 3.0, V3 Turbo, V2.1, V2.5, AI Avatar, Motion Control
- **Bytedance/Seedance** 2, 2 Fast, 2 Mini, 2.5, 1.5 Pro
- **Hailuo** 2.3/0.2 image/text-to-video pro/standard
- **Wan Video** 2.2–3.0 — text/image/video-to-video, animate, edit
- **Grok Imagine Video** — text/video, upscale, extend
- **MiniMax H3**, **PixVerse**, **Runway API** (dedicated with callbacks)
- **HappyHorse** 1.0/1.1, **OmniHuman 1.5**, **Gemini Omni**
- **Volcengine** lip-sync, **Veo3.1 API** (dedicated with callbacks)
- **Infinitalk** from-audio

## Music & Audio Models

| Model | Use |
|-------|-----|
| **ElevenLabs** | TTS, dialogue, audio isolation via task API |
| **Suno API** | Full music: generate, cover, extend, lyrics, MIDI, voice, WAV, music video |
| **Gemini TTS** | gemini-3-1-flash-tts, gemini-2-5-pro-tts |

## Chat Models (discounted)

- **GPT**: 5.2, 5.4, 5.5, 5.6 Luna/Terra/Sol, 6 Sol/Luna/Astra
- **Claude**: Opus 4.5–5, Sonnet 4.5–5, Haiku 4.5, Fable 5
- **Gemini**: 2.5 Pro, 3 Pro, 3.1 Pro, 3.5–3.8 Flash
- **Grok**: 4.3, 4.5, 4.6, 4.7
- **Others**: DeepSeek V4.1 Flash, Codex, Kimi K3

## Rate Limits

- **20 requests/10s** per account, ~100+ concurrent tasks supported
- HTTP 429 when exceeded (requests rejected, not queued)
- Contact support to request higher limits

## Data Retention

| Data | Retention |
|------|-----------|
| Generated media files | **14 days** |
| Log records (text/metadata) | **2 months** |
| Uploaded files | **24 hours** |
| Download URLs | **20 minutes** |

**Always download and store results immediately.**

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Bad/missing API key |
| 402 | Insufficient credits |
| 404 | Endpoint not found |
| 422 | Validation error |
| 429 | Rate limited |
| 455 | Maintenance |
| 500 | Server error |
| 501 | Generation failed |

## Pitfalls

- **Auth header:** `x-api-key` returns 401 silently. Always use `Authorization: Bearer`.
- **resultJson is double-encoded:** Parse twice: `json.loads(data["resultJson"])["resultUrls"]`
- **input (gpt-image):** Must be `json.dumps({...})` string, NOT a nested dict
- **File URLs:** Must be public URLs. Base64 data-URIs return "File type not supported"
- **Content safety (grok):** Keywords like "data center", "cyberpunk" trigger 431 rejection.
  Fallback to flux-2 or gpt-image.
- **Image storage:** URLs expire — download immediately after generation.

## Quick Reference (Python)

```python
import json, urllib.request
KIE_BASE = "https://api.kie.ai"

def create_task(model, input_data, callback_url=None):
    body = {"model": model}
    if callback_url:
        body["callBackUrl"] = callback_url
    body["input"] = json.dumps(input_data)
    req = urllib.request.Request(f"{KIE_BASE}/api/v1/jobs/createTask",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["data"]["taskId"]

def poll_task(task_id, max_polls=60, interval=5.0):
    for i in range(max_polls):
        req = urllib.request.Request(f"{KIE_BASE}/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"})
        d = json.loads(urllib.request.urlopen(req).read())["data"]
        if d["state"] == "success":
            return json.loads(d["resultJson"])
        elif d["state"] in ("fail", "error"):
            raise RuntimeError(d.get("failMsg", "?"))
        import time; time.sleep(interval)
    raise TimeoutError(f"Task not done after {max_polls * interval}s")

def get_credits():
    req = urllib.request.Request(f"{KIE_BASE}/api/v1/chat/credit",
        headers={"Authorization": f"Bearer {API_KEY}"})
    return json.loads(urllib.request.urlopen(req).read())["data"]
```