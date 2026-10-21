# Kokoro TTS (mature voice) — local narration leg

Kokoro via sherpa-onnx is the proven local TTS for message videos. Venv:
`~/.venvs/kokoro/bin/python`; script: `~/workspace/scripts/kokoro_tts.py`.
Usage: `kokoro_tts.py <sid> <speed> <out.wav> "<script text>"`.

**sid 10 = the mature Hermes voice** (what produced `tts_hermes_final.wav`).

## Model files

- Dir: `~/.hermes/kokoro/kokoro-multi-lang-v1_0/` (model.onnx ~325 MB,
  voices.bin, tokens.txt, lexicon-us-en.txt, lexicon-zh.txt, espeak-ng-data/).
- **Download as ONE tar.bz2 asset, not individual files.** The k2-fsa
  /sherpa-onnx `tts-models` release publishes `kokoro-multi-lang-v1_0.tar.bz2`
  (~336 MB) and the individual-file URLs (`.../tts-models/kokoro-multi-lang-v1_0/model.onnx`)
  ɢ return 404. Enumerate real assets from the GitHub releases API
  (`repos/k2-fsa/sherpa-onnx/releases/tags/tts-models`) before guessing URLs.
- Config objects (model/voices/tokens/data_dir/lexicon) must match the dir.

## Long-audio write pitfall

`kokoro_tts.py` originally wrote WAV with
`struct.pack("<%dh" % len(s), *s)`. On a full narration (~530k samples) the
unpacking explodes and `wave.close()` then throws
`AttributeError: 'Wave_write' object has no attribute '_file'` — a misleading
cascade; the real error is the giant `struct.pack`. Fix: build an
`array('h', s)` (byteswap on big-endian hosts) and `writeframes(a.tobytes())`.
Also confirm the output directory EXISTS before calling — a missing dir
produces the same `_file`-attribute cascade from `wave.open` failure.
Short test clips (8 s) can pass even when a full narration fails, so always
test with the actual script length.

## Sentence-splitting for segmented renders

Kokoro reads nearly continuously (often a single silence gap for the whole
pass), so `silencedetect` alone won't find sentence boundaries. Cut by
proportional character count per sentence with ~0.15 s pre-roll and ~0.25 s
tail: total_duration × sentence_chars / total_chars gives per-sentence dur;
use `ffmpeg -ss L -to R -c copy` per segment. Render EACH sentence as its own
A2V chunk (identity re-anchor per chunk), then concat.
