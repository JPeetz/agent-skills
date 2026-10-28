# CHANGELOG — kie-ai-platform

## v1.0.0 — 2026-10-28

### Added
- Initial release of the Kie.ai platform API integration skill
- Async task model: `createTask`, `recordInfo` polling, `callBackUrl` webhooks
- Webhook HMAC-SHA256 signature verification (X-Webhook-Timestamp / X-Webhook-Signature)
- Auth guidance: `Authorization: Bearer` only — `x-api-key` silently returns 401
- File upload API (URL, stream, base64) with 24h expiry note
- Credits check, download URLs, rate limits, error code table
- Model coverage: image, video, music/audio, and chat models
- evals/evals.json with 7 cases (6 positive, 1 near-miss negative)