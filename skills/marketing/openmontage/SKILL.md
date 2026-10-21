---
name: openmontage
description: Use this skill when producing or editing video via OpenMontage.
version: 0.1.0
author: Joerg Peetz
license: MIT
platforms: [linux, macos]

metadata:
  hermes:
    tags: [video, openmontage, ffmpeg, remotion, hyperframes, production]
    config:
      - key: openmontage.path
        description: Absolute path to the OpenMontage repository
        default: "~/workspace/OpenMontage"
        prompt: "Where is your OpenMontage repository?"
      - key: openmontage.projects_path
        description: Directory where OpenMontage project workspaces are stored
        default: "~/workspace/OpenMontage/projects"
        prompt: "Where should OpenMontage project workspaces be created?"
---

# OpenMontage Video Production

Use this skill whenever the user asks to create, produce, edit, render,
localize, repurpose, animate, or compose video using the locally installed
OpenMontage repository.

The OpenMontage repository is the authoritative source for: available
pipelines, pipeline stages, required tools, provider availability, stage
quality rules, checkpoint requirements, and review procedures.

## Safety and execution rules

- Work only inside the configured OpenMontage repository.
- Read `AGENT_GUIDE.md` before production.
- Never bypass the pipeline system with an ad-hoc Python production script.
- Never call a generation tool before reading its referenced Layer 3 skill.
- Never silently change provider, model, composition runtime, or deliverable type.
- Ask for approval before paid generation, batch generation, or major creative changes.
- Stop and report blockers instead of silently substituting a lower-quality path.
- Keep generated files inside `projects/<project-name>/`.
- Do not modify source code unless the user explicitly asks for a code change.

## Required paths

Set `OM_ROOT="${OPENMONTAGE_PATH}"`. Resolve these relative to OM_ROOT:
`AGENT_GUIDE.md`, `PROJECT_CONTEXT.md`, `pipeline_defs/`, `skills/`,
`.agents/skills/`, `tools/`, `schemas/`, `projects/`.

If OM_ROOT does not exist, stop and ask the user for the correct path.

## Helper script

Run the bundled preflight helper when a concise capability report is needed:

```
python "${HERMES_SKILL_DIR}/scripts/preflight.py"
```

Use the OpenMontage repository's own registry output as the source of truth.

## Workflow

### 1. Classify the request
Determine whether the request is: a new topic-to-video production, a
source-footage edit, a podcast repurpose, a screen-demo video, a cinematic
trailer/teaser, an animation/motion-graphics project, a talking-head or avatar
video, a localization/dubbing job, a batch clip-generation job, or a
render/review/repair request. If vague, read `skills/meta/onboarding.md`. If a
reference video/URL is supplied, read `skills/meta/video-reference-analyst.md`.

### 2. Identify the pipeline
List manifests: `find "$OM_ROOT/pipeline_defs" -maxdepth 1 -type f -name '*.yaml'`
and read the candidate with `cat`. Common pipelines: `animated-explainer`,
`screen-demo`, `clip-factory`, `podcast-repurpose`, `cinematic`, `animation`,
`hybrid`, `localization-dub`. If ambiguous, explain the difference and ask the
user to choose — do not proceed until resolved.

**Pipeline names mislead about MOTION TYPE — read the manifest description before
committing.** `character-animation` renders **deterministic local motion**
(SVG/Canvas/Remotion/HyperFrames rigs) and its own description says it is *not*
a remote video-gen replacement — picking it for a request that wants a real
image turned into a *flowing* video clip is the wrong call. For genuinely
generative image-to-video, use `cinematic` (or `hybrid`) and drive the local
diffusers tool `ltx_video_local` (or wan/hunyuan/cogvideo) — the registry tool
is a first-class path and often means ComfyUI is NOT needed for the video leg.
Verify the chosen manifest's `description` and `stages` name a video-generation
tool before treating it as the motion pipeline.

### 3. Run mandatory preflight
From the repo root run the capability summary (see helper / registry output).
Present: available capabilities, configured vs total providers, local tools,
unavailable tools, quick setup options, runtime warnings, and whether the
selected pipeline is passed, degraded, or blocked. Do not hardcode provider or
API-key names; read them from registry output.

### 4. Present the production proposal
Before generation present: selected pipeline and reason, creative direction,
available + alternative tool paths, estimated cost, local vs cloud execution,
music source/plan, composition runtime options, production stages, approval
points, known limitations. If both Remotion and HyperFrames are available,
present both with tradeoffs and a recommendation, plus FFmpeg where relevant.
Do not lock the render runtime silently. Wait for explicit approval before
generation.

### 5. Initialize the project workspace
Use kebab-case. `mkdir -p "projects/<project-name>"` and follow the repo
convention (`artifacts/`, `assets/{images,video,audio,music}/`, `renders/`).
Do not write assets to the repository root.

### 6. Execute stage by stage
For each stage in the manifest: read the stage director skill, read referenced
meta skills, discover/validate required tools, read each tool's `agent_skills`
refs, execute only the current stage, validate the canonical artifact against
its schema, run the reviewer protocol, write/verify the checkpoint, and pause
for human approval where required. Typical director paths:
`skills/pipelines/<pipeline>/{idea,script,scene_plan,assets,edit,compose}-director.md`.
The manifest is authoritative — do not assume every pipeline has every stage.

### 7. Verify the final render
Run `ffprobe` (duration, size, streams, dimensions, frame rate) on
`projects/<project-name>/renders/final.mp4`. Check: file exists/non-empty,
expected duration, resolution/aspect, video+audio streams, subtitles if
required, no missing assets, render report, checkpoint status, reviewer
findings. Report the exact final path and classify the outcome (rendered /
rendered with warnings / blocked / failed).

## Blocker protocol
Report: (1) attempted, (2) what failed, (3) the class (auth, provider, install,
tool, runtime, design), (4) available options, (5) recommended option. Do not
switch providers/models/runtimes/deliverable types without user approval.

## Useful commands
- Pipelines: `find "$OM_ROOT/pipeline_defs" -maxdepth 1 -type f -name '*.yaml'`
- Project state: `find "$OM_ROOT/projects/<name>" -maxdepth 3 -type f | sort`
- Runtimes: registry `_tools["video_compose"].get_info()["render_engines"]`
- Tools: registry `capability_catalog()`

## Local video generation (`ltx_video_local` / difftransducers)

OpenMontage's local LTX path (`tools/video/ltx_video_local.py` →
`generate_local_video` in `tools/video/_shared.py`) is a genuine **local GPU
tool** usable without any paid provider — it runs LTX-2 image-to-video via
diffusers on the machine's GPU (resource profile ≈ 12 GB VRAM / 16 GB RAM,
`i2v: true`, 121 frames @ 30 fps). Getting it to register as AVAILABLE has two
gates that are easy to miss:

- **The tool reads `VIDEO_GEN_LOCAL_ENABLED` and only returns AVAILABLE when it
  is set `true`/`1`/`yes`** — plus it needs `diffusers` AND `torch` importable in
  the venv used to run the tool. Set it persistently in `$OM_ROOT/.env`
  (`VIDEO_GEN_LOCAL_ENABLED=true`) since `tools/base_tool.py` auto-loads `.env`.
- **`diffusers` is NOT declared in `requirements-gpu.txt`** — that file ships
  only torch/torchaudio/torchvision, yet the tool does
  `import diffusers; from diffusers.utils import export_to_video`. A fresh venv
  built from the declared requirements gets the LTX path stuck at UNAVAILABLE
  with no clear `ImportError` surfaced. Install it explicitly after the gpu
  stack: `uv pip install --python .venv/bin/python diffusers accelerate safetensors`.
- **If the venv is broken, rebuild it with `uv` at the pinned Python**: the
  repo pins python in `.python-version` (e.g. 3.10) and `uv` can fetch it. A
dead symlink in `.venv/bin` (e.g. a `python3.14 → /usr/local/opt/...` target
that no longer exists) makes every tool call fail — move the broken venv aside,
then `uv venv --python 3.10` in `$OM_ROOT` and reinstall core + gpu + diffusers.
Warm up and verify in the rebuilt venv: `torch.backends.mps.is_available()==True` + `diffusers` imports, then `local_generation_status()` returns AVAILABLE.


## Talking character videos — the correct pipeline

**FIRST: study the user's existing on-disk reference videos + their build
scripts before proposing anything.** The user already has finished
"character presents a message" videos (e.g. in `~/workspace/scripts/hermes_build/`
and `~/workspace/artifacts/video/`) whose parts were produced with OpenMontage
on this machine — those are the indicator of what "perfect" means, and the
canonical blueprint is the `herald_pipeline.sh` + `build_final_video.py` pair
with its `*.spec.json` single-source-of-truth. Translate that proven pipe to
local models leg by leg; keep every local stage (karaoke burn, trim, QA,
caption) verbatim and swap only the cloud generation legs.

When the ask is "a character talking" (avatar/spokesperson/anime host), do NOT reach
for lip-sync-first. The repo's own `skills/creative/talking-head-gen-usage.md` is
emphatic: **`talking_head` (SadTalker/MuseTalk/EchoMimic from a still + audio) is the
PRIMARY avatar path; Wav2Lip-lip_sync is the FALLBACK** when talking_head is
unavailable. Wav2Lip patches a 96×96 mouth region over existing video — it looks
awful as a primary pipeline.

Correct production order:
1. **Script first** — use `skills/creative/storytelling.md` beats (hook/tension/concept/proof/reframe),
   the But-Therefore method, misconception-first (Derek Muller), 30-second rule, and the
   anti-subjective rule (describe the visual cause of emotion, not the emotion).
2. **Audio before motion** — generate clean TTS first (Piper for free local, ElevenLabs
   for quality voice), then drive the talking_head with it. Audio duration = video duration.
3. **Image-quality gate** — front-facing, neutral expression, 512×512+, no hair covering
   the mouth; use the sheet/anchor render. Preview a 5s clip before full generation;
   expression_scale 0.7–1.0, still_mode false for conversational, crop preprocess.
4. **Model choice (16 GB M5)** — LTX-2.x GGUF/MLX A2V (native lip sync) > Wan 2.2
   TI2V-5B (GGUF Q4_K_M or FastMetal-5B-QAD) > Wan 1.3B draft > EchoMimic/MuseTalk/
   SadTalker. EchoMimic V3-Flash works but is CUDA-oriented and hits device/path/
   config walls on MPS. Shut the local LLM down (LM Studio) before renders;
   PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0. Full doctrine: `local-video-production-m5` skill.
5. **Compose like a professional** — enhancement chain (face → eyes → color → audio),
   subtitle burn, B-roll/overlay cuts, background music with ducking, silence cuts
   (remove for Shorts, speed-up for longform), output per platform profile.

Use the `avatar-spokesperson` (production, presenter-led) or `talking-head`
(footage-led) pipeline manifests with their director skills and human gates instead
of ad-hoc generation.

## Design principle
Three layers, no duplication: Hermes SKILL.md = orchestration/safety/approvals;
OpenMontage AGENT_GUIDE + manifests = production state machine; OpenMontage
stage + Layer 3 skills = creative quality and tool execution. Hermes chooses
and coordinates; OpenMontage defines how production executes.
