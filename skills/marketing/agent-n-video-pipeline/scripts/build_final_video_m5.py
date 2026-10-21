#!/usr/bin/env python3
"""Build a Hermes Herald video — FULLY LOCAL on the M5 executor.
Translation of build_final_video.py (grok-imagine + volcengine cloud legs) to
local models: LTX-2.3 MLX A2V (talking render + native lip-sync in one leg),
Piper TTS (mature voice), then the SAME local caption/trim/QA stages.

Usage:
  python3 build_final_video_m5.py --script "<speech>" [--out NAME] [--duration 22] [--voice PATH] [--anchor PATH]
  or --spec spec.json  (same schema as the cloud version: script/prompt/out/duration/voice)

Stages:
  1. TTS (Piper, mature voice) -> audio.wav
  2. LTX-2.3 MLX A2V on M5 (anchor + audio -> talking video with lip sync)
  3. karaoke_burn.py (same as cloud version, PressStart2P word-synced)
  4. trim to speech+2.5s
  5. qa_review.py (same deterministic gate)
  6. x_caption.py
"""
import re, json, time, os, sys, subprocess, argparse, urllib.request

AP = argparse.ArgumentParser()
AP.add_argument("--script", default=None)
AP.add_argument("--spec", default=None)
AP.add_argument("--out", default="hermes-herald-m5-FINAL.mp4")
AP.add_argument("--duration", type=int, default=22)
AP.add_argument("--voice", default="/tmp/m5_images/audio/hn_mature.wav")
AP.add_argument("--anchor", default="agentn_anchor_v1.png")
AP.add_argument("--m5", default="192.168.212.46")
args = AP.parse_args()

BASE = "/Users/joergpeetz/workspace/scripts/hermes_build"
M5 = f"http://{args.m5}:8188"
WORK = "/tmp/m5_herald"
os.makedirs(WORK, exist_ok=True)
KARAOKE = "/Users/joergpeetz/workspace/scripts/karaoke_burn.py"
KOKORO_PY = "/Users/joergpeetz/.venvs/kokoro/bin/python"
PY = "/usr/local/bin/python3"

# ---------------------------------------------------------------- spec resolve
if args.spec:
    spec = json.load(open(args.spec))
    SCRIPT = spec["script"]
    args.out = spec.get("out", args.out)
    args.duration = int(spec.get("duration", args.duration))
    if spec.get("voice"):
        args.voice = spec.get("voice")
else:
    SCRIPT = args.script or ("Hermes researches with receipts now. Every claim is matched to a "
              "real source, cited, and fact-checked before it reaches you. Hand it any document "
              "\u2014 it shows what checks out, and what doesn't. That's trust you can see.")

# ---------------------------------------------------------------- 1. TTS (Kokoro sid 10 = mature voice)
print("── 1/6 TTS (Kokoro sid 10, mature) ──")
tts_py = "/Users/joergpeetz/workspace/scripts/kokoro_tts.py"
tts_out = os.path.join(WORK, "voice.wav")
if os.path.exists(args.voice) and os.path.getsize(args.voice) > 10000:
    subprocess.run(["cp", args.voice, tts_out], check=True)
    print(f"   using supplied voice: {args.voice}")
else:
    subprocess.run([KOKORO_PY, tts_py, "10", "1.0", tts_out, SCRIPT], check=True, timeout=300)
    print(f"   Kokoro synth done: {tts_out}")
print(f"   voice: {tts_out} ({os.path.getsize(tts_out)} bytes)")

# ---------------------------------------------------------------- 2. LTX A2V on M5
print("── 2/6 LTX-2.3 MLX A2V on M5 ──")
# stage anchor + audio into M5 ComfyUI input dir
subprocess.run(["sshpass", "-p", "Buddy-2019", "scp", "-o", "StrictHostKeyChecking=no",
                os.path.join(WORK, "voice.wav"),
                f"joergpeetz@{args.m5}:/Users/joergpeetz/ComfyUI-Shared/input/agentn_speech.wav"], check=True)

a2v_prompt = (
    "Anime girl with short black bob hair and black over-ear headphones with orange accents "
    "speaks directly to the camera, natural facial expressions and lip movement, subtle "
    "head movement, gentle confident tone, semi-realistic anime illustration, sharp focus, "
    "clean dark studio backdrop with violet grade."
)
frames = int(args.duration * 24)
wf = {
    "img": {"class_type": "LoadImage", "inputs": {"image": args.anchor}},
    "aud": {"class_type": "LoadAudio", "inputs": {"audio": "agentn_speech.wav"}},
    "a2v": {"class_type": "LTXMLXA2V", "inputs": {
        "image": ["img", 0], "audio": ["aud", 0], "prompt": a2v_prompt,
        "width": 512, "height": 768, "frames": min(frames, 200), "frame_rate": 24,
        "seed": 42, "cfg_scale": 3.0, "low_ram": True,
        "model_dir": "dgrauet/ltx-2.3-mlx-q8"}},
    "video": {"class_type": "CreateVideo", "inputs": {
        "images": ["a2v", 0], "fps": 24.0, "audio": ["a2v", 1]}},
    "save": {"class_type": "SaveVideo", "inputs": {
        "video": ["video", 0], "filename_prefix": "agentn_herald_a2v", "format": "mp4", "codec": "h264"}},
}
r = subprocess.run(["sshpass", "-p", "Buddy-2019", "ssh", "-o", "StrictHostKeyChecking=no",
                    f"joergpeetz@{args.m5}",
                    f"curl -s --max-time 20 -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' -d @/tmp/m5_herald_wf.json"],
                   capture_output=True, text=True)
print("   queued response:", r.stdout.strip()[:120])

# ---------------------------------------------------------------- 3-6 local stages (unchanged from cloud pipeline)
print("─ local stages 3-6 (karaoke/trim/QA/caption) run in full pipeline after A2V output is pulled ─")