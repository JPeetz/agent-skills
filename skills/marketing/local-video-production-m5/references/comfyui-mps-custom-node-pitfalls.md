# ComfyUI custom-node pitfalls on Apple Silicon (MPS)

Debugging walls when a CUDA-written custom node refuses to run on the M5's
MPS build. Order they tend to appear, roughly top to bottom:

## 1. Node fails to import (custom nodes never show in /object_info)

Check "IMPORT FAILED" / traceback in the headless server log, not just GUI.
Common causes, each fixed by a small patch (back up the file first):

- **Legacy mediapipe `solutions`** — mediapipe >=1.0 removed `mp.solutions.*`.
  Nodes still do `from mediapipe import solutions` or `mp.solutions.face_mesh`
  at module level. Patch options: (a) comment out a truly dead import; (b)
  install a `.pth` shim in site-packages that installs a permissive dummy on
  `mp.solutions` whose `__getattr__` returns nested dummies, `__iter__` yields
  empty, and `__call__` raises a clear error — module-level references load,
  only actual calls fail.
- **`torchaudio.save` → torchcodec wall** — torchcodec's dylib links
  `libavcodec.58` (FFmpeg 4), which the M5 lacks (FFmpeg 9 provides
  `libavcodec.63`), and installing FFmpeg@4 needs Xcode CLT 27. The clean fix is
  the same as cozui Wav2Lip: patch `torchaudio.save(...)` to write with
  `soundfile` or the stdlib `wave` module (mono int16 PCM). See
  `creative/comfyui` references/local-lip-sync-wav2lip.md for the model.
- **Missing vendored module** (e.g. a custom node that `from .dist import`
  xFuser shims that the git clone didn't include) — obtain it from the
  upstream/main repo and copy the file into the node's src tree. The module
  degrades gracefully (None fallbacks) once present.
- **`pip install` of a git subpackage + pyproject `readme`** fails with
  `Readme path must be within the project directory` when `readme` points
  outside the subdir and the PEP 517 hook can't find it. Fix: clone at the
  pinned tag, delete the `readme = ...` line from each subpackage's pyproject,
  pip install the local clones.
- Missing pip deps surface one at a time (`pyloudnorm`, `decord` has no py3.13
  wheel — comment out its import if only used by an unused code path). Iterate:
  install → restart → read next error.

## 2. Loads but model files "not found" / empty dropdowns

Custom nodes often resolve model paths relative to the install tree
(`ComfyUI/models/...`) instead of the shared dir that `extra_model_paths.yaml`
maps. Fix: `ln -sfn` the shared model dirs into the install tree
(remove any pre-existing real dir first, or the symlink lands INSIDE it). Also
add missing keys to extra_model_paths.yaml (e.g. `clip_vision:`) or the
loader's option list comes back empty.

## 3. Runs, then a config / device wall during inference

- Omegaconf `Missing key` for a field the node reads from its own config.yaml —
  append the missing key with a sensible default (`quantize_transformer: false`).
- mmgp offload profiler calls `torch.cuda` → on MPS set the node's `use_mmgp`
  to `None`/`"off"` and rely on block_offload + lowvram + teacache_offload
  instead of the CUDA memory profiler.
- Any `torch.cuda.*` call → hard `AssertionError`. Runtime-detect the device in
  the node's constructors/defaults.

## Watch the shared flag through every restart

Any rebuild of headless ComfyUI must re-export `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`
(and keep the mediapipe `.pth` shim in site-packages). Env like DYLD_LIBRARY_PATH
often doesn't survive the launch + macOS strips it for spawned processes — set
it inline on the launch command (`env DLL=... nohup ... main.py`).
