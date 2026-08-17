---
name: betterlife-image-generation
description: >
  Use this skill when an agent needs to generate BetterLife daily social media
  images via kie.ai's grok-imagine/image-to-image model, conditioned on Mira
  reference photos from Google Drive. Activates for the morning social post
  generation pipeline. Includes the full API payload, reference selection rules,
  character anchor, prompt composition, anti-repetition system, and fallback
  model. Authorized use only — never hardcode credentials.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - betterlife
  - image-generation
  - kie-ai
  - social-media
  - mira
  - character-consistency
  - image-to-image
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
---

# BetterLife Daily Social Image Generation (kie.ai image-to-image)

Generate the daily BetterLife social media image using **kie.ai's grok-imagine/image-to-image**
model, conditioned on Mira reference photos from Google Drive. This is **image-to-image**,
not text-to-image — the model generates from reference images, not from a prompt alone.

## Architecture
```
Compose Prompt (scene + attire + mood + angle)
  → Select 8 Mira reference images (5 for grok) from 20 GDrive photos
    → Send to kie.ai grok-imagine/image-to-image (strength 0.85)
      → Fallback: flux-2/flex-image-to-image on failure
        → Save to ~/workspace/tool-image-generation/
```

## Credentials
- **KIE_API_KEY** — for the kie.ai API
- **BETTERLIFE_GDRIVE_API_KEY** — Google Drive API key for reference images
- Read from credential source by label — never hardcode.

## Reference images (20 Mira photos on Google Drive)
All 20 refs have file IDs on Google Drive. URL format:
`https://www.googleapis.com/drive/v3/files/{FILE_ID}?alt=media&key={GDRIVE_API_KEY}`

| ID | Name | Tags |
|----|------|------|
| 1mhvlkciwkTMjI5uImDUl2lCKSWJ74NZ_ | front | front, direct, face |
| 1bnlCeQFSBjicFALUV_1-15Ig3KEeaN_k | 3-4 | 3-4, angle, portrait |
| 1ZZRSS6slwHNBBYpd54VHYdFsTwgFR1Y0 | profile | profile, side |
| 1tX-IHi7tQvNQUvGgyY9x1Aw3rcAumkGI | medium | medium, upper-body, waist-up |
| 1I84U8XAsRCOxTuv8myF0Oqj9sjpVsm9W | full-body | full-body, standing |
| 1WHK2Um-I5Phz1qd6KQAUFsvmuufcf8g4 | sitting | sitting, seated, rest |
| 1jwzZUlPp_qiuNh3-Ab4QhtKJ3vlkk_e3 | standing-phone | standing, casual, hand-near-face |
| 1490krB_MKxKk4CU1SlXce9oJNLkdiTLf | cross-legged | sitting, cross-legged, meditation |
| 1xda8rmTfO__ZmM81wwYjB4sXwuwP9f97 | kneeling | kneeling, lower, ground |
| 1VHhnEYImykdLUcSDJrswRmcPnzLSRUid | walking | walking, movement, active |
| 1xidQ2uOO3X20AOXEt6MQcJVuFoPaID45 | leaning | leaning, arms-crossed, relaxed |
| 1fiHrUfIw4Gxaa7rIdJK4TRkckTKIDVeK | hand-near-face | hand-near-face, thinking |
| 16vVPso4fb59penpJDVRdOBrBdv9GyFEx | laughing | laughing, candid, happy |
| 1ZCjwWNf4yTlubo9N-8Mxc1f-FGmNwyPg | looking-down | looking-down, contemplative |
| 1mlK7XyyNkQo-t0VxIUlFtMubrTC0kC4X | looking-up | looking-up, away, aspiring |
| 13QvANWBrsAq1_4rXlkzxFjexibluCCcy | surprised | surprised, eyes-wide |
| 1YAwUV8rYuN3bixMCysE8WURkRb3qikNJ | concerned | concerned, worried |
| 1d0MqjAZaoYo2IRu9RZEyAmMDT_dSii-o | content | content, peaceful, calm |
| 1Dy9AZnUivy4wQ7npCN6J1CfGKAwIW75I | focused | focused, serious |
| 1beX1U0rSnDELB17qYySsv05hslFqEQ3_ | warm-smile | smile, warm, friendly |

### Reference selection
- **Face anchors (MANDATORY):** ref_01 (front) + ref_02 (3/4). Always in the first 2 slots.
- **Pose refs (3-6 remaining):** scored by tag overlap with scene keywords, randomly sampled
  from top 14. Grok caps at 5 total refs, flux at 8.

## Character anchor
```
Mira, a wellness coach with natural beauty, shoulder-length dark hair,
warm olive skin, kind eyes, minimal makeup
```

## Prompt composition
Format: `{anchor}, {scene}. {attire}. {detail}. {mood} {accent}. Premium editorial wellness photography, {angle}, no text, no watermarks.`

Components picked combinatorially to avoid repeats: 36 scenes, 8 attires, 10 details, 6 moods, 8 angles, 4 accents.

## kie.ai API call
```json
POST https://api.kie.ai/api/v1/jobs/createTask
{
  "model": "grok-imagine/image-to-image",
  "input": {
    "prompt": "<composed prompt>",
    "image_urls": ["<5 ref URLs>"],
    "strength": 0.85,
    "aspect_ratio": "1:1", "resolution": "1K", "output_format": "jpg"
  }
}
```
Poll GET /api/v1/jobs/recordInfo?taskId={id} every 2s until state=="success".

**Fallback:** flux-2/flex-image-to-image (uses `input_urls`, allows 8 refs).

## Key parameters
- **strength 0.85** — higher = more Mira-likeness, lower = more prompt-driven scene
- **Known limitation:** at strength 0.85 with the same 20 refs, output is structurally dominated
  by the refs. Scene words shift background but not composition. For genuine variety, lower
  strength or add shot-size/framing contrast per variant.

## Post-generation
1. Image saved to `~/workspace/tool-image-generation/betterlife-{theme}-{date}-v{n}.jpg`
2. Review JSON at `/tmp/bl-social-review.json`
3. Posted via `bl_social_post.py` on approval