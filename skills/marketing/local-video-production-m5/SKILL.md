---
name: local-video-production-m5
description: Use this skill when producing local videos on the 16GB M5 executor.
version: 0.1.0
---

# Local Video Production on M5 (16 GB Unified, Apple Silicon)

Hard rule: video on the M5 stays local-first, GGUF/MLX, short clips, modest
resolutions, aggressive memory management. Cloud only with explicit approval.
This is the executor doctrine; primary Mac delegates video work to M5.

## The goal is a "character presents a message" video, NOT a lip-sync exercise

The user wants a finished message video (e.g. Agent N addresses the camera with
scripted narration + karaoke captions + music + QA), judged against their own
**on-disk reference videos**. Before building anything: find and study the
existing reference pipeline and its finished renders — the user has already done
this well and its parts are the indicator of "perfect". For the Hermes Herald
line the canonical blueprint is `~/workspace/scripts/hermes_build/`:
`herald_pipeline.sh` + `build_final_video.py` (+ `qa_review.py`, `karaoke_burn.py`,
`x_caption.py`, and a `*.spec.json` holding script/prompt/out/duration as the
single source of truth). Translate that pipe to local models leg by leg — keep
every local stage (karaoke burn, trim, QA, caption) verbatim and swap only the
cloud generation legs for a local A2V model. Deliverable shape: 9:16, ~720×1280,
speech-length, word-synced captions aligned to the TRUE script, deterministic QA.

ComfyUI famously wants a `{"prompt": {...}}` top-level key — POST a bare node
dict and it returns `no_prompt` with no node errors.

## Non-negotiable memory discipline (16 GB unified)

- Prefer quantized models: GGUF Q4/Q5, INT8, or MLX ports. FP8 on Mac can break —
  stick to FP16/BF16 or GGUF.
- Before launching ComfyUI set:
  `export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` (raise MPS upper limit).
- Shut down LM Studio / llama-server before heavy renders (~5 GB freed).
- Use lowvram/block-offload/teacache-offload flags, sequential loading, tiling;
  generate low-res (480p–720p or ~740×480) then spatial upscale.
- Keep clips 3–5 s; document peak RAM per model in the skill so nothing is retried
  blind.
- MPS is NOT CUDA and never can be. CUDA is NVIDIA-only; Apple Silicon has no
  NVIDIA GPU. Unified memory (CPU+GPU sharing the 16 GB pool) is a real
  advantage but NOT CUDA. Code that calls `torch.cuda.*` throws
  `AssertionError: Torch not compiled with CUDA enabled` and cannot be made to
  run by "trying harder" — the API physically does not exist. If the user asks
  "can't this use CUDA with shared memory?", explain that distinction once and
  move on to the MLX/MPS path. Patch any node that hardcodes `device="cuda"` to
  runtime-detect: `"cuda" if torch.cuda.is_available() else "mps" if
  torch.backends.mps.is_available() else "cpu"`. Research models built by NVIDIA
  users (EchoMimic and its mmgp offload lib) are CUDA-first end to end — prefer
  an MLX-native model (LTX, Wan FastMetal) over patching each torch.cuda call.

## Model priority (character-consistent video + lip sync, late 2026)

1. **LTX-2.x (distilled + GGUF Q4 or MLX)** — native audio-to-video lip sync.
   Best on 16 GB M4/M5 with Gemma INT8 text encoder + GGUF transformer, tiling
   (~740×480), then upscale. Prefer the ComfyUI-LTX-MLX-A2V node (or MLX path)
   for Apple Silicon speed. Verified install + API workflow + pyproject packaging
   fix: `references/ltx-mlx-a2v-setup.md`.
2. **Wan 2.2 TI2V-5B (GGUF Q4_K_M or FastMetal-5B-QAD MLX)** — best
   quality/speed balance for T2V/I2V. ~9–11 GB peak; 5 s 720p feasible.
   FastMetal (Hao AI Lab / FastVideo) is MLX-native, very efficient on MPS.
3. **Wan 2.1 T2V 1.3B / FastMetal-1.3B** — lighter fallback for drafts/tests.
4. Supporting: AnimateDiff (light motion), MuseTalk/SadTalker/V-Express
   (post-process lip-sync) only when pure generative A2V is too heavy.

EchoMimic V3-Flash works but is CUDA-oriented: expect device/path/config walls.
Use LTX A2V for talking videos before EchoMimic. The full wall-by-wall path for
making ANY CUDA-written custom node run on MPS: `references/comfyui-mps-custom-node-pitfalls.md`.

## Character consistency (paramount)

- Generate a clean **multi-view character sheet** first (front, 3/4, side,
  expressions) from 1–3 references — Qwen Image 2.1 quantized, or Flux GGUF,
  with IP-Adapter / PuLID / FaceID / native reference conditioning + face
  detailer pass.
- The sheet is the identity lock. Always I2V/first-frame from the sheet or a
  neutral keyframe, never pure T2V for faces.
- Re-anchor (start/end neutral keyframe) between chunks of longer talking
  videos. Fixed seeds where useful. Re-lock identity after any scene/costume
  change.
- Prompts: "preserve the exact eye shape, nose, jawline, hair color and style
  from the character sheet" + motion + camera + lighting + expression + audio
  behavior. Negatives: face drift, sticky lips, artifacts, inconsistent
  proportions.
- Lip-sync: clear audio + high-quality starting portrait; higher CFG on audio;
  request natural head movement, blinks, expression matching audio.

## Learning-to-learn loop (mandatory after every run)

1. Build minimal workflows in order: (a) multi-view sheet from 1–3 refs,
   (b) I2V with locked character, (c) A2V lip sync (LTX), (d) full OpenMontage
   pipeline calling ComfyUI for assets then composing.
2. After every success/failure: save a reusable skill entry — exact workflow
   JSON path, model filenames + download links + folder placement, sampler
   settings, memory peaks, failure modes.
3. Measure: face consistency, lip-sync accuracy, motion coherence. Iterate on
   quantization/tiling/steps; stay under ~12–13 GB peak.
4. Produce editable artifacts (sheets, scene plans, workflow JSONs, rendered
   clips) so the human can review and direct.

## OpenMontage integration

- Run OpenMontage with `VIDEO_GEN_LOCAL_ENABLED=true` and
  `COMFYUI_SERVER_URL` pointing at the local ComfyUI server.
- Use OpenMontage pipelines (avatar-spokesperson, talking-head, cinematic,
  animation), its comfyui_image/comfyui_video tools, skills, and approval
  gates. Prefer zero-key local paths. Script-first: use storytelling.md beats
  before generating anything.

## M5-local "Agent N presents a message" pipeline (Herald blueprint, ported 2026-10-21)

The cloud Herald pipeline (`herald_pipeline.sh` + `build_final_video.py`, grok-imagine
i2v + volcengine lip-sync) ported to fully local M5. Run:

    ~/workspace/scripts/hermes_build/herald_pipeline_m5.sh --spec <spec.json> --anchor agentn_anchor_v1.png

Stages (single spec JSON = source of truth, same schema as cloud version):
1. TTS: Kokoro sid 10 = mature voice, local via `kokoro_tts.py` (model dir
   `~/.hermes/kokoro/kokoro-multi-lang-v1_0/`, re-downloadable from k2-fsa
   sherpa-onnx tts-models release if purged). Default script = research-receipts.
2. Talking render + lip sync in ONE leg: LTX-2.3 MLX A2V on M5. **Memory-safe
   config is Q4 quant at 512×512, low_ram; the Q8@512×768 config SWAP-THRASHES
   on 16 GB (5.5 GB swap used, ~97M swapouts, 53 min no completion).**
3. Karaoke burn (PressStart2P, word-synced to TRUE script) — `karaoke_burn.py`,
   unchanged from cloud version.
4. Trim to speech+2.5s (ffmpeg).
5. QA gate (qa_review.py) and 6. X caption (x_caption.py) — unchanged.

**Measured speed (Q4, 512×512, 49 frames, low_ram on M5): 13 min render for
2.04 s = 16 s per frame.** Projections: 5 s ≈ 32 min, 8 s ≈ 51 min, 22 s ≈
2.3 h. That is the honest cost of 16 GB block-streaming; on a 64+ GB M-series
the same engine is ~2 s/frame. Do not silently promise faster — quote these
numbers when asked for an ETA.

**Longer messages = segmented renders (user's chosen approach).** Do NOT run one
big A2V job; split the narration at sentence boundaries, render each sentence
as its own A2V chunk (each re-anchors on the identity image — no drift across
the take), then concat (each segment carries its own synced audio, so lossless
concat works). Sentence-split timing: Kokoro reads ~continuously with few
silence gaps, so cut proportional to character count of each sentence with
~0.15 s pre-roll / 0.25 s tail, frames = ceil(dur×24)+padding. Stitch,
trim, karaoke burn, and QA run after concat.

Pitfalls learned:
- LTX-MLX-A2V node install: ltx-2-mlx@v0.14.15 pyproject has readme-path bug on
  subdir install; clone repo, remove `readme` line from both subpackage
  pyprojects, pip install from local clone.
- The takeover node needs `transformers < 5.10` (mlx-lm 0.31 conflict).
- ltx-core-mlx does video I/O through ffmpeg and fails at the END of a render
  with `RuntimeError: ffmpeg not found on PATH` if ffmpeg is not visible to the
  ComfyUI process. Symlink `~/homebrew/opt/ffmpeg/bin/{ffmpeg,ffprobe}` into the
  Comfy venv `bin/` AND export PATH in the launch command.
- First A2V run downloads the model (Q8 ~8-10G, Q4 smaller) then two-stage
  inference: 30 guided steps half-res + 3 refine full-res. Slow but normal.
- Flat/calm TTS → near-static mouth per node README; expressive take articulates.
- A loaded node may still fail at the encode step — progress bar to 100%
  does NOT mean the file was written; always check the output dir.
- Model output audio is trimmed/padded to frames/frame_rate exactly.

Full install, API workflow, quantization/memory decision, and speed bench:
`references/ltx-mlx-a2v-setup.md`. Mature-voice TTS leg: `references/kokoro-tts-mature-voice.md`.

## Env check before starting

- ComfyUI headless up? `curl -s http://127.0.0.1:8188/system_stats`
- Models present in `~/ComfyUI-Shared/models/**`? (diffusion_models,
  text_encoders, vae, loras, checkpoints)
- MPS available? `torch.backends.mps.is_available()`
- LM Studio off? `pgrep -fl llama-server`
