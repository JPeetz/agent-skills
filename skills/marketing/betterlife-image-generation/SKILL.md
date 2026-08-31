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
- Read from credential source by label — never hardcode.

## Reference images (Supabase S3 storage)

Reference images are stored in Supabase storage at:
`https://dbbppsbtpsahdkmevxgm.supabase.co/storage/v1/object/public/instagram_images/`

File naming: `{character}_reference_{nn}_{pose}.jpg`

### Reference selection
- **Face anchors (MANDATORY):** front + 3/4 angle references. Always in the first 2 slots.
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