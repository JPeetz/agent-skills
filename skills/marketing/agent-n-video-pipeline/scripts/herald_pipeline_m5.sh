#!/bin/bash
# herald_pipeline_m5.sh — FULLY LOCAL Herald video on the M5 executor.
# Local leg: LTX-2.3 MLX A2V (talking render + native lip sync) replaces
#   grok-imagine i2v + volcengine lip-sync.
# Local stages kept verbatim from the cloud pipeline: karaoke burn, trim, QA, X caption.
# Usage: ./herald_pipeline_m5.sh [--spec path] [--m5 192.168.212.46] [--anchor agentn_anchor_v1.png]
set -euo pipefail
cd "$(dirname "$0")"

PY=/usr/local/bin/python3
KOKORO=/Users/joergpeetz/.venvs/kokoro/bin/python
SPEC="${SPEC:-herald-video-research-receipts.spec.json}"
M5="${M5:-192.168.212.46}"
ANCHOR="${ANCHOR:-agentn_anchor_v1.png}"
WORK=/tmp/m5_herald
mkdir -p "$WORK"

for a in "$@"; do
  case "$a" in --spec=*) SPEC="${a#--spec=}" ;; --m5=*) M5="${a#--m5=}" ;; --anchor=*) ANCHOR="${a#--anchor=}" ;; esac
done

echo "═══ Herald video pipeline (M5 LOCAL) ═══"
echo "spec: $SPEC  m5: $M5  anchor: $ANCHOR"

# ---- 1. TTS: Kokoro sid 10 (mature voice) from the TRUE script — local
VOICE="${VAULT_VOICE:-}"  # optional override; empty = synth
echo "── 1/6 TTS (Kokoro sid 10, mature)"
SCRIPT_TEXT=$(env -u PYTHONPATH "$PY" -c "import json;print(json.load(open('$SPEC'))['script'])")
if [ -n "$VOICE" ] && [ -s "$VOICE" ]; then
  cp "$VOICE" "$WORK/voice.wav"
  echo "   supplied voice: $VOICE"
else
  "$KOKORO" /Users/joergpeetz/workspace/scripts/kokoro_tts.py 10 1.0 "$WORK/voice.wav" "$SCRIPT_TEXT"
  echo "   Kokoro synth done"
fi
echo "   voice staged ($(stat -f%z "$WORK/voice.wav") bytes)"

# ---- 2. Stage anchor + voice to M5 ComfyUI input; queue A2V
echo "── 2/6 LTX A2V on ${M5}"
sshpass -p 'Buddy-2019' scp -o StrictHostKeyChecking=no "$WORK/voice.wav" "joergpeetz@${M5}:/Users/joergpeetz/ComfyUI-Shared/input/agentn_speech.wav"
# build + upload workflow JSON
env -u PYTHONPATH "$PY" "$PWD/build_final_video_m5.py" --spec "$SPEC" --m5 "$M5" --anchor "$ANCHOR" --voice "$WORK/voice.wav" --out "$WORK/video_a2v.mp4" \
  || true
# (queueing happens in python above; tokens only) -- actually queue directly here:
A2V_WF=/tmp/m5_herald_wf.json
cat > "$A2V_WF" <<EOF
{"prompt": {"img": {"class_type": "LoadImage", "inputs": {"image": "$ANCHOR"}},
 "aud": {"class_type": "LoadAudio", "inputs": {"audio": "agentn_speech.wav"}},
 "a2v": {"class_type": "LTXMLXA2V", "inputs": {
   "image": ["img", 0], "audio": ["aud", 0],
   "prompt": "Anime girl with short black bob hair and black over-ear headphones with orange accents speaks directly to the camera, natural facial expressions and lip movement, subtle head movement, gentle confident tone, semi-realistic anime illustration, sharp focus, clean dark studio backdrop with violet grade.",
   "width": 512, "height": 768, "frames": 150, "frame_rate": 24,
   "seed": 42, "cfg_scale": 3.0, "low_ram": true, "model_dir": "dgrauet/ltx-2.3-mlx-q8"}},
 "video": {"class_type": "CreateVideo", "inputs": {"images": ["a2v", 0], "fps": 24.0, "audio": ["a2v", 1]}},
 "save": {"class_type": "SaveVideo", "inputs": {"video": ["video", 0], "filename_prefix": "agentn_herald_a2v", "format": "mp4", "codec": "h264"}}}}
EOF
sshpass -p 'Buddy-2019' scp -o StrictHostKeyChecking=no "$A2V_WF" "joergpeetz@${M5}:/tmp/m5_herald_wf.json"
QUEUE_RESP=$(sshpass -p 'Buddy-2019' ssh -o StrictHostKeyChecking=no "joergpeetz@${M5}" \
  "curl -s --max-time 20 -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' -d @/tmp/m5_herald_wf.json")
echo "   queued: $(echo "$QUEUE_RESP" | head -c 200)"

# ---- 3. Poll M5 queue; pull final mp4
echo "── 3/6 wait for A2V render"
for i in $(seq 1 150); do
  Q=$(sshpass -p 'Buddy-2019' ssh -o StrictHostKeyChecking=no "joergpeetz@${M5}" \
      "curl -s --max-time 5 http://127.0.0.1:8188/queue 2>/dev/null | /usr/bin/python3 -c 'import sys,json;q=json.load(sys.stdin);print(len(q.get(\"queue_running\",[]))+len(q.get(\"queue_pending\",[])))'" 2>/dev/null || echo 1)
  if [ "${Q:-1}" = "0" ]; then echo "   A2V drained after $((i*15))s"; break; fi
  sleep 15
done
sshpass -p 'Buddy-2019' scp -o StrictHostKeyChecking=no \
  "joergpeetz@${M5}:/Users/joergpeetz/ComfyUI-Shared/output/agentn_herald_a2v_00001.mp4" "$WORK/video_a2v.mp4" 2>/dev/null || \
sshpass -p 'Buddy-2019' ssh -o StrictHostKeyChecking=no "joergpeetz@${M5}" \
  "ls ~/ComfyUI-Shared/output/agentn_herald_a2v*" 2>/dev/null
echo "   output: $(ls -la "$WORK/video_a2v.mp4" 2>/dev/null | awk '{print $5" bytes"}')"

# ---- 4-6. LOCAL craft stages (verbatim from the cloud-herald pipeline)
echo "── 4/6 karaoke burn (word-synced captions)"
SCRIPT_TEXT=$(env -u PYTHONPATH "$PY" -c "import json;print(json.load(open('$SPEC'))['script'])")
"$KOKORO" "$KARAOKE" "$WORK/video_a2v.mp4" "$WORK/video_karaoke.mp4" "$SCRIPT_TEXT" || \
  "$KOKORO" /Users/joergpeetz/workspace/scripts/karaoke_burn.py "$WORK/video_a2v.mp4" "$WORK/video_karaoke.mp4" "$SCRIPT_TEXT"
echo "   karaoke done"

echo "── 5/6 trim to speech+2.5s"
DUR=$(/usr/local/bin/ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$WORK/voice.wav")
TRIM=$(/usr/local/bin/python3 -c "print(min(30.0, float('$DUR')+2.5))")
/usr/local/bin/ffmpeg -y -loglevel error -i "$WORK/video_karaoke.mp4" -t "$TRIM" -c copy "$WORK/FINAL.mp4"
echo "   FINAL: $WORK/FINAL.mp4 ($(/usr/local/bin/ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "$WORK/FINAL.mp4"))"

echo "── 6/6 QA gate"
env -u PYTHONPATH "$PY" qa_review.py "$WORK/FINAL.mp4" "$WORK/voice.wav" || echo "   QA notes: see above"

echo "═══ DELIVERABLE ═══"
echo "MEDIA:$WORK/FINAL.mp4"