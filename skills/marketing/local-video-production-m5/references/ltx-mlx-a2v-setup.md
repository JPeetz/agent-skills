# LTX-2.x MLX Audio-to-Video (talking head) — M5 setup and usage

Primary talking-video path on 16 GB Apple Silicon: one image + one audio in →
lip-synced talking video out, MLX-native (≈2× faster than PyTorch-on-MPS), no
CUDA anywhere. Node: `noreff/ComfyUI-LTX-MLX-A2V` ("🍎 LTX MLX Audio-to-Video"
under Lightricks/MLX). Model auto-downloads on first run from
`dgrauet/ltx-2.3-mlx-q8` (Q8 quant). **On 16 GB use `dgrauet/ltx-2.3-mlx-q4`
instead** — see Memory decision below.

## Memory decision (measured on M5 16 GB, late 2026)

- Q8 @ 512×768 × 97 frames + low_ram = SWAP THRASH. 5.5 GB of 7.2 GB swap used,
  ~97M swapouts, ~53 min elapsed with no completion, engine at 22.5% MEM.
- Q4 @ 512×512 × 49 frames + low_ram = clean. Engine at 3.1% MEM, completes.
  Measured 13:04 for 2.04 s of video = **16 s per frame**.
- Projected (at 16 s/frame): 5 s ≈ 32 min, 8 s ≈ 51 min, 22 s ≈ 2.3 h.
- The two-stage recipe is fixed: 30 guided steps at half res + 3 refine full res.

Rule: default A2V jobs on 16 GB to Q4 + 512×512 + low_ram; only consider Q8 or
taller latents on a 64+ GB machine. Interrupting dev ops: `pkill -f ltx-2-mlx`
and restart headless ComfyUI to clear stuck model state — the REST /interrupt
alone does not kill the CLI subprocess.

## ffmpeg PATH (end-of-render failure)

ltx-core-mlx encodes through a system ffmpeg. If it is not visible to the
ComfyUI process, the render runs to 100% then dies with
`RuntimeError: ffmpeg not found on PATH. Install it with: brew install ffmpeg`.
The progress bar to 100% does NOT mean the file exists — always check output.
Fix: symlink `~/homebrew/opt/ffmpeg/bin/{ffmpeg,ffprobe}` into the Comfy venv
`bin/` and export PATH in the headless launch command.

## Install (verified working)

1. Clone node into ComfyUI custom_nodes; install `requirements.txt` into the
   Comfy venv (imageio, av, ltx-core-mlx, ltx-pipelines-mlx).
2. The `ltx-2-mlx` subpackage install FAILS with
   `ValueError: Readme path must be within the project directory: ../../README.md`
   — pyproject `readme` points outside the subdirectory and pip's PEP 517
   metadata hook rejects it. A symlink into the subpackage does NOT fix it
   (hatchling resolves the path before finding the local file). The fix:
   clone `dgrauet/ltx-2-mlx` at the pinned tag, DELETE the `readme = ...` line
   from `packages/ltx-core-mlx/pyproject.toml` AND
   `packages/ltx-pipelines-mlx/pyproject.toml`, then
   `pip install <clone>/packages/ltx-core-mlx` and `.../ltx-pipelines-mlx` from
   the local clones.
3. `pip install imageio av "mlx-lm<0.31"` — mlx-lm 0.31.x fails to import
   against transformers >=5.10, so keep transformers below 5.10.
4. Restart headless ComfyUI; verify `GET /object_info/LTXMLXA2V` returns the node.

## API workflow (from the node's own example_workflows/a2v_talking_head.json)

```
LoadImage(image) -> LTXMLXA2V(prompt, width, height, frames, frame_rate, seed,
            cfg_scale=3.0, low_ram=true, model_dir="dgrauet/ltx-2.3-mlx-q8") <- LoadAudio(audio)
-> CreateVideo(images=[a2v,0], fps, audio=[a2v,1]) -> SaveVideo
```

- Audio is trimmed/zero-padded to exactly `frames / frame_rate` seconds.
- `low_ram: true` uses block streaming — mandatory on 16 GB.
- Pipeline is two-stage: 30 guided steps at half resolution, then 3 refine
  steps at full resolution.

## Quality levers

- **Expressive audio drives expressive faces.** A flat/quiet track gets a
  near-static mouth; the same portrait with an energetic take articulates well.
  If the mouth barely moves, fix the audio before anything else.
- A start image with burned-in caption text makes the model hallucinate
  gibberish captions across the whole clip — never feed a text-bearing sheet or
  render as the start frame.
- >257 frames: render chunks, feeding the last frame of one chunk into the next.
- Still need a clean front-facing anchor: see the character-anchor requirements
  in `creative/comfyui` references/echo-mimic-v3-flash.md.
