---
name: agent-n-video-pipeline
description: >
  Use this skill when producing a fully-local "Agent N presents a message" video on
  the 16GB Apple-Silicon M5 executor: Kokoro mature TTS → LTX-2.3 MLX A2V
  talking render with native lip sync → karaoke captions → trim → QA → X caption.
  Replaces the old cloud Herald pipeline (grok-imagine + volcengine) with zero
  cloud cost. Activates for Herald release videos, Agent N announcements, and
  newsletter video messages.
version: 1.0.0
author: Hermes Agent
license: MIT
compatibility: >
  Cross-platform: Hermes Agent (default profile orchestrates, M5 executor
  renders locally). Scripts are plain bash/python + ffmpeg + ComfyUI REST.
platforms:
  - hermes-agent
tags:
  - video
  - agent-n
  - ltx
  - local-generation
  - talking-head
  - herald
---

# Agent N Video Pipeline (Fully Local on M5)

Produce a character-consistent "Agent N presents a message" video entirely on
the 16 GB Apple-Silicon M5 executor. Port of the cloud Herald pipeline
(`hermes_build/herald_pipeline.sh` + `build_final_video.py`) that replaces both
cloud legs (grok-imagine image-to-video, volcengine lip-sync) with ONE local
MLX leg (LTX-2.3 A2V, native audio-to-video).

## One-command usage

```bash
# in the repo: scripts/ dir
./herald_pipeline_m5.sh --spec <spec.json> --anchor agentn_anchor_v1.png
# optional: --m5 192.168.212.46  (default)  --voice <path> (skip TTS)
```

Spec JSON = single source of truth, same schema as the cloud Herald version:
`{ "script": "...", "prompt": "...", "out": "...", "duration": N, "voice": "..." }`.
Default spec (research-receipts) is embedded.

## Stages (all local)

1. **TTS** — Kokoro sid 10 (mature female voice) via `kokoro_tts.py`
   (sherpa-onnx; model `~/.hermes/kokoro/kokoro-multi-lang-v1_0/`, download the
   `kokoro-multi-lang-v1_0.tar.bz2` bundle from k2-fsa/sherpa-onnx
   `tts-models` release if purged). Override with `--voice` to skip.
2. **Talking render + lip sync in ONE leg** — `build_final_video_m5.py` queues
   LTX-2.3 MLX A2V on the M5 via ComfyUI REST: anchor image + audio →
   speaking video. 512×512, frames = duration×24, cfg 3.0, low_ram,
   `dgrauet/ltx-2.3-mlx-q4`. Then poll + pull the mp4.
3. **Karaoke captions** — `karaoke_burn.py` (PressStart2P, word-synced to the
   TRUE script). Unchanged from the cloud pipeline.
4. **Trim** — ffmpeg to voice duration +2.5 s.
5. **QA gate** — `qa_review.py` (deterministic). Call separately in the repo.
6. **X caption** — `x_caption.py` (mentions @NousResearch/@Teknium).

## Segmented mode (recommended for >10 s messages)

Render in 3–8 s chunks, each re-anchored on the Agent N image (identity lock,
no cumulative drift), then concat (each segment carries its synced audio) →
karaoke on the stitched video. `queue_segments.py` does this: split voice by
sentence boundaries, queue one A2V per segment, stitch with ffmpeg concat.

## The anchor

The anchor image IS the identity lock — sheet-derived, front-facing, ≥512²,
mouth unobstructed, no burned-in text. Never drive identity from prompt alone.

## Performance facts (measured on M5 16GB, Q4, 512×512)

- ~16 s/frame on MPS with low_ram block-streaming (Q4). 2 s clip ≈ 13 min.
- 5 s ≈ 32 min, 8 s ≈ 51 min, 22 s ≈ 2.3 h single-pass → use segmented mode.
- Q8@512×768 swaps (5.5 GB swap) — do not use on 16 GB. Q4 + 512×512 + low_ram
  is the reliable envelope.

## Pitfalls already climbed (do not re-climb)

- LTX-MLX-A2V node install: ltx-2-mlx@v0.14.15 pyproject has a readme-path bug
  on subdir installs; clone repo, remove the `readme` line from both subpackage
  pyprojects, pip install from local clone.
- Needs `transformers < 5.10` (mlx-lm 0.31 conflict).
- ltx-core-mlx requires ffmpeg on PATH: symlink `ffmpeg`/`ffprobe` into the
  ComfyUI venv bin or export PATH (user-local brew `~/homebrew/opt/ffmpeg/bin`).
- ComfyUI must launch with `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`.
- Flat/calm TTS → near-static mouth (node README). Expressive takes articulate.
- First A2V run downloads the Q8/Q4 model (~8–10 GB) — subsequent runs cached.
- kokoro_tts.py writes long audio with `array('h')`, NOT `struct.pack("%dh",*s)`
  (unpacking ~500k args breaks on long scripts); ensure output dir exists.

## Env gate before running

- M5 ComfyUI headless: `curl -s http://M5:8188/system_stats`
- Anchor staged in M5 `ComfyUI-Shared/input/`
- Kokoro model dir present; venv `~/.venvs/kokoro/bin/python` has sherpa_onnx
- LM Studio / llama-server off (frees ~5 GB)
