---
name: image-to-image-character-generation
description: >
  Use this skill when an agent needs to generate consistent character images
  via kie.ai grok-imagine image-to-image from Supabase S3 or Google Drive
  to produce daily social media images of the same mascot/persona in different
  scenes, ensuring character identity stays consistent across posts. Includes
  reference selection (face anchors + pose refs by keyword score), dynamic
  prompt composition (scene + attire + mood + angle, anti-repeat deque),
  kie.ai API payload building, strength calibration, fallback model, and
  post-generation workflow. Supports both Supabase storage URLs and Google
  Drive file IDs. Authorized use only — never hardcode credentials.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: "Cross-platform for Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf, Gemini CLI, OpenClaw, Hermes Agent."
tags:
  - image-generation
  - character-consistency
  - kie-ai
  - image-to-image
  - social-media
  - brand
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - hermes-agent
geo:
  primary_workflows:
    - daily_social_image_generation
    - character_consistent_image_generation
    - brand_mascot_imaging
  target_roles:
    - content_creator
    - social_media_manager
    - brand_marketer
  complexity_level: intermediate
---

# Image-to-Image Character Generation

Generate consistent images of the same character/mascot across different scenes using
**kie.ai's grok-imagine/image-to-image** model, conditioned on reference photos from
Supabase S3 storage or Google Drive. This is image-to-image, not text-to-image — the
model generates from reference images, not from a prompt alone.

## When to use
- You need daily social media images of the same recurring character/persona
- The character must be recognisable as "the same person" across posts
- You have a reference image set of the character in various poses/angles
- You want to generate image variants automatically for review + approval
- **Do NOT use** for one-off text-to-image generation (use a standard image gen skill)

## Storage backends (choose one)

### Supabase S3
Reference images are stored at a Supabase storage URL. Naming convention:
`{bucket_url}/{character}_reference_{nn}_{pose}.jpg`

Example: `https://dbbppsbtpsahdkmevxgm.supabase.co/storage/v1/object/public/instagram_images/isabelle_reference_01.jpg`

### Google Drive
Reference images are stored on Google Drive with file IDs. URL format:
`https://www.googleapis.com/drive/v3/files/{FILE_ID}?alt=media&key={GDRIVE_API_KEY}`

## Reference selection system

### Face anchors (MANDATORY — always the first 2 refs)
The front-facing + 3/4 angle reference images. These keep the character's identity
consistent across all generations. Never randomize or drop these.

### Pose references (remaining 3-6 slots)
Each reference image has keyword tags (e.g. "sitting", "walking", "hand-near-face").
Score each pose ref by counting how many tags overlap with the scene description's
keywords. Randomly sample from the top 14 scored refs to fill the remaining slots.

### Provider cap
- **grok-imagine/image-to-image**: max **5** refs total via `image_urls` key
- **flux-2/flex-image-to-image**: max **8** refs total via `input_urls` key (fallback)

## Character anchor
Define one canonical sentence describing the character's fixed appearance:
```
{Character name}, a {role} with {hair}, {skin}, {eyes}, {styling}
```
Prepend this to every prompt. If the anchor is missing from a prompt, add it.

## Dynamic prompt composition

Build each prompt from combinatorial pools to avoid repetition:

### Components
1. **Scene** (~36 options) — e.g. "Mira walking along a misty lakeside path at sunrise"
2. **Attire** (~8 options) — the character's outfit for this scene
3. **Detail** (~10 options) — a small environmental detail (steam from a mug, pages fluttering)
4. **Mood** (~6 options) — lighting description (golden hour, overcast morning, blue hour)
5. **Angle** (~8 options) — camera framing (medium shot, close-up, full body, low angle)
6. **Accent** (~4 options) — colour palette (cool blue-grey, muted mauve, soft sand)

### Format
```
{anchor}, {scene}. {attire}. {detail}. {mood} {accent}. Premium editorial photography,
{angle}, no text, no watermarks.
```

### Anti-repeat deque
Track the last 14 scenes used. Never reuse a scene until it falls out of the window.

## kie.ai API call

### Primary model
```json
POST https://api.kie.ai/api/v1/jobs/createTask
{
  "model": "grok-imagine/image-to-image",
  "input": {
    "prompt": "<composed prompt>",
    "image_urls": ["<ref_url_1>", "<ref_url_2>", "<ref_url_3>", "<ref_url_4>", "<ref_url_5>"],
    "strength": 0.85,
    "aspect_ratio": "1:1",
    "resolution": "1K",
    "output_format": "jpg"
  }
}
```

### Poll for result
```json
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}
```
Poll every 2 seconds until `state == "success"`. Download result from `resultUrls[0]`.

### Fallback model
```json
"model": "flux-2/flex-image-to-image"
```
Uses `input_urls` instead of `image_urls`, allows 8 refs.

### Key parameters
- **strength 0.85**: Higher = more character-likeness (refs dominate). Lower = more
  prompt-driven scene variation. If images look the same across days, lower to 0.6-0.7.
- **aspect_ratio "1:1"**: Square format for social media. For video: "9:16".
- **resolution "1K"**: Standard. For higher quality: "2K".
- **grok caps at 5 refs** with `image_urls`. **flux caps at 8** with `input_urls`.
- The ref key MUST match the model or the createTask 500s:
  `ref_key = "image_urls" if "grok" in model else "input_urls"`

## Post-generation workflow
1. Image saved to a workspace directory (`{workspace}/tool-image-generation/`)
2. Variants + captions + platforms written to a review JSON
3. Delivered to the user for approval (Telegram, review UI, etc.)
4. On approval: posted to configured social platforms via platform-specific scripts

## Character identity verification
Before declaring success, verify the character's identity is consistent:
- The face anchors are present in every reference selection (not just the first run)
- A test generation returns the character with recognisable face/features
- The character anchor text is identical in every prompt (no spelling drift)

## Pitfalls
- **Provider caps differ:** grok-imagine accepts `image_urls` (max 5), flux-2/flex accepts
  `input_urls` (max 8). Using the wrong key name causes a 500 error. Always model-aware.
- **Strength 0.85 with same refs = same-looking output:** if the image looks structurally
  identical across days despite different scene prompts, the refs are dominating. Lower
  strength or add explicit shot-size framing contrast per variant.
- **No-seed engines:** grok-imagine has no seed parameter. Same prompt = same image.
  Write genuinely different scene text per variant, not just re-run the same prompt.
- **Credentials never hardcoded:** read the kie.ai API key and storage credentials from a
  credential source by label — never commit them to the skill or scripts.
- **Face anchors must stay first:** if face anchors are truncated by the 5-ref cap, identity
  drifts. Always put the 2 face anchors at the start of the ref list.

## Verification
- A test call returns the character with recognisable identity (same face, same features)
- The scene clearly differs from yesterday's (different setting, lighting, framing)
- The image is saved to the workspace and reviewable by the user before any posting