#!/usr/bin/env python3
"""Kokoro TTS via sherpa-onnx for Hermes script. Usage: kokoro_tts.py [sid] [speed] [out.wav]"""
import sys, os, wave, struct
import sherpa_onnx

BASE = os.path.dirname(os.path.abspath(__file__))
M = "/Users/joergpeetz/.hermes/kokoro/kokoro-multi-lang-v1_0"
sid = int(sys.argv[1]) if len(sys.argv) > 1 else 10
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(BASE, f"tts_kokoro_s{sid}.wav")
# Optional 4th arg overrides the speech text (single source of truth), else the default.
SCRIPT = (sys.argv[4] if len(sys.argv) > 4 else
          "Hermes researches with receipts now. Every claim is matched to a real source, cited, and "
          "fact-checked before it reaches you. Hand it any document - it shows what checks out, "
          "and what doesn't. That's trust you can see.")

kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
    model=os.path.join(M, "model.onnx"),
    voices=os.path.join(M, "voices.bin"),
    tokens=os.path.join(M, "tokens.txt"),
    data_dir=os.path.join(M, "espeak-ng-data"),
    lexicon=",".join([os.path.join(M, "lexicon-us-en.txt"), os.path.join(M, "lexicon-zh.txt")]),
)
tts_config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro, num_threads=4, debug=False),
)
if not tts_config.validate():
    raise ValueError("bad config")
tts = sherpa_onnx.OfflineTts(tts_config)

gen = sherpa_onnx.GenerationConfig()
gen.sid = sid
gen.speed = speed
audio = tts.generate(SCRIPT, gen)
if len(audio.samples) == 0:
    sys.exit("no audio generated")
sr = audio.sample_rate
s = list(audio.samples)
# detect scale: floats in [-1,1] vs already-int
mx = max((abs(x) for x in s), default=0)
if mx <= 1.0 and any(abs(x) < 0.1 and x != 0 for x in s[:50]):
    s = [int(x * 32767) for x in s]
s = [max(-32768, min(32767, int(x))) for x in s]
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    import array as _arr
    a = _arr.array("h", s)
    if sys.byteorder != "little":
        a.byteswap()
    w.writeframes(a.tobytes())
print(f"saved {os.path.basename(out)} sid={sid} speed={speed} sr={sr} dur={len(s)/sr:.2f}s", flush=True)
