#!/usr/bin/env python3
"""Word-synced PressStart2P karaoke captions burned onto a video with ffmpeg (no libass).
Captions render to auto-sized transparent PNGs, centered in-frame, using the
HERMES-AGENT wordmark font (PressStart2P) with a yellow->orange gradient for the
active word and dim gray for the rest. All words share one baseline.
Usage: karaoke_burn.py <video> <out>
- word timings come from ASR of the video's own (clean) audio track.
"""
import sys, os, json, subprocess
from PIL import Image, ImageDraw, ImageFont

VIDEO = sys.argv[1]
OUT   = sys.argv[2]
# Optional 3rd arg: the TRUE script the voice reads. Used to keep on-screen
# captions verbatim (not the ASR mishearing). Falls back to the baked default.
_SCRIPT_ARG = sys.argv[3] if len(sys.argv) > 3 else None
WORD_SYNC = (_SCRIPT_ARG if _SCRIPT_ARG else
"""Hermes researches with receipts now. Every claim is matched to a real source, cited, and
fact-checked before it reaches you. Hand it any document, it shows what checks out,
and what doesn't. That's trust you can see.""")
# Align these true script words onto ASR timings so captions show the real script,
# not the transcriber's mishearings (Whisper renders "cited" as "sided", etc.).

FONT    = "/Users/joergpeetz/.hermes/fonts/pressstart2p/PressStart2P-Regular.ttf"
# HERMES-AGENT wordmark gradient: yellow top -> orange bottom
YELLOW  = (255, 215, 30)
ORANGE  = (235, 140, 20)
DIM     = (150, 158, 175)
SHADOW  = (0, 0, 0)
FS      = 46
WORK    = os.path.dirname(OUT)

def render_text(img, x, y, text, font, palette, sw=4):
    """Draw text with a vertical gradient palette (list of colors top->bottom),
    black outline, pasted with its top-left at (x, y). All words share the same
    font metrics so tops/baselines align across a line."""
    from PIL import Image, ImageDraw
    d = ImageDraw.Draw(img)
    tb = d.textbbox((0, 0), text, font=font, stroke_width=sw)
    tw = max(int(tb[2] - tb[0]), 1); th = max(int(tb[3] - tb[1]), 1)
    # glyph mask WITHOUT stroke -> for the color fill
    fill_mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(fill_mask).text((-int(tb[0]), -int(tb[1])), text, font=font,
                                   fill=255, stroke_width=0, stroke_fill=0)
    # glyph mask WITH stroke -> black outline underneath
    stroke_mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(stroke_mask).text((-int(tb[0]), -int(tb[1])), text, font=font,
                                     fill=255, stroke_width=sw, stroke_fill=255)
    # vertical gradient overlay
    grad = Image.new("RGB", (tw, th))
    gd = ImageDraw.Draw(grad)
    n = len(palette)
    for gy in range(th):
        t = (gy / max(1, th - 1)) * (n - 1)
        i = min(int(t), n - 2); f = t - i
        col = tuple(int(palette[i][c] + (palette[i + 1][c] - palette[i][c]) * f)
                    for c in range(3))
        gd.line([(0, gy), (tw, gy)], fill=col)
    px = int(x) - int(tb[0]); py = int(y) - int(tb[1])
    img.paste((0, 0, 0, 255), (px, py), stroke_mask)
    img.paste(grad, (px, py), fill_mask)

# ---- 1) ASR word timings from the video audio ----
def word_times(video):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(video, word_timestamps=True)
    words = []
    for s in segs:
        for w in (s.words or []):
            t = w.word.strip()
            if t:
                words.append((round(w.start, 2), round(w.end, 2), t))
    return words

WORD_SYNC = (_SCRIPT_ARG if _SCRIPT_ARG else
"""Hermes researches with receipts now. Every claim is matched to a real source, cited, and
fact-checked before it reaches you. Hand it any document, it shows what checks out,
and what doesn't. That's trust you can see.""")
# Align these true script words onto ASR timings so captions show the real script,
# not the transcriber's mishearings (Whisper renders "cited" as "sided", etc.).

words = word_times(VIDEO)      # ASR gives (start, end, text) per spoken token
if not words:
    sys.exit("no words from ASR")
json.dump(words, open(os.path.join(WORK, "karaoke_words.json"), "w"), indent=1)
print(f"[ok] {len(words)} words timed")

# ---- align the true script words onto ASR timings (display script, not ASR) ----
# Monotonic ratcheted alignment: script words that EXACTLY match an asr token anchor
# to that token's real timing (consumed in order, never going backward). The few that
# don't match (misheard words, the "fact-checked" split, stray dash) get evenly
# interpolated between the surrounding matched anchors. Guarantees no collapse and no
# dead zone, while keeping true script text on screen.
import re as _re

def _tok(s):
    return [_re.sub(r"[^a-z']", "", t.lower()) for t in s.split()]

script_tok = _tok(WORD_SYNC)
asr_tok = [t for _, _, t in words]
# Normalize the ASR side to the SAME cleaned/lowercased form as the script tokens,
# otherwise capitals ("Browser", "CLI", "Hermes") never match and the ratchet
# cascades into a collapsed tail. (Bug found 2026-08-11: `_tok` lowercases+strips
# the script but raw ASR was compared against it.)
asr_clean = [_re.sub(r"[^a-z']", "", t.lower()) for t in asr_tok]
print(f"[ok] script tokens={len(script_tok)} asr tokens={len(asr_tok)}")

anchor = [None] * len(script_tok)   # script idx -> asr idx (real time)
cursor = 0
for i, stok in enumerate(script_tok):
    if not stok:                     # empty token (the stray '-')
        continue
    for k in range(cursor, len(asr_tok)):
        if not asr_clean[k]:              # empty cleaned token ("%" or ".") — skip, can't anchor
            continue
        if asr_clean[k] == stok or asr_clean[k].startswith(stok) or stok.startswith(asr_clean[k]):
            anchor[i] = k
            cursor = k + 1
            break
# greedily fill unmatched script slots by interpolation between nearest anchors
anchored_idx = [i for i in range(len(script_tok)) if anchor[i] is not None]
for i in range(len(script_tok)):
    if anchor[i] is not None:
        continue
    prev = None; last = None
    for a in anchored_idx:
        if a < i: prev = a
        elif a > i:
            last = a; break
    if prev is None and last is not None:
        anchor[i] = anchor[last] - (last - i)         # extrapolate before first anchor
    elif prev is not None and last is not None:
        f = (i - prev) / max(1, (last - prev))        # linear interp in index space
        anchor[i] = int(anchor[prev] + f * (anchor[last] - anchor[prev]))
    elif prev is not None:
        anchor[i] = anchor[prev]
# convert any remaining None to 0, clamp, then ratchet strictly monotonic
anchor = [0 if a is None else max(0, min(a, len(words) - 1)) for a in anchor]
for i in range(1, len(anchor)):
    if anchor[i] < anchor[i-1]:
        anchor[i] = anchor[i-1]

script_words = [(words[anchor[i]][0], words[anchor[i]][1], WORD_SYNC.split()[i])
                for i in range(len(script_tok))]
words = script_words

# ---- anti-collapse pass: re-spread zero-width runs ----
# ASR sometimes emits a burst of tokens all sharing one tiny timestamp (e.g. a
# phrase it snapped to a single token). Every matched word then inherits that
# identical window, so 5-6 words flash on screen at once and vanish instantly.
# Detect any run of consecutive words with near-zero span and re-distribute it
# evenly across the audible gap between the distinct words that bound it.
MIN_SPAN = 0.12
runs = []                      # (start_idx, end_idx)
i = 0
while i < len(words):
    if (words[i][1] - words[i][0]) < MIN_SPAN:
        j = i
        while j + 1 < len(words) and (words[j+1][1] - words[j+1][0]) < MIN_SPAN \
              and abs(words[j+1][0] - words[i][0]) < 0.25:
            j += 1
        runs.append((i, j))
        i = j + 1
    else:
        i += 1
for a, b in runs:
    # left boundary: end of the last distinct word before this run (or run start)
    left_end = words[a-1][1] if a > 0 else words[a][0]
    # right boundary: start of the first distinct word after this run (or run end)
    right_start = words[b+1][0] if b + 1 < len(words) else max(words[b][1], left_end + 0.25)
    span = max(0.25, right_start - left_end)
    n = (b - a + 1)
    step = span / n
    for k in range(n):
        idx = a + k
        words[idx] = (left_end + step * k, left_end + step * (k + 1), words[idx][2])

print("=== after anti-collapse re-spread ===")
for x in words:
    print("   ", round(x[0],2), "-", round(x[1],2), x[2])

# ---- 2) chunk into caption lines (<=4 words) ----
lines = [words[i:i+4] for i in range(0, len(words), 4)]

# ---- 3) render cumulative per-word highlight states for each line ----
# Real karaoke: as each word is spoken it lights up and STAYS lit. For a 4-word
# line we emit up to 4 state PNGs: state j has words 0..j in the yellow->orange
# gradient, words j+1.. dim. State j is enabled from word[j].start onward, so the
# highlight advances word-by-word. All states share identical geometry so they
# stack cleanly (later states sit on top and win).
font = ImageFont.truetype(FONT, FS)
scratch = ImageDraw.Draw(Image.new("RGBA", (5, 5), (0, 0, 0, 0)))
states = []                      # (on_start, on_end, png_path)
# Each line's states must hold until the START of the next line, else ASR pauses
# between sentences create holes with no caption. Last line holds to video end.
line_starts = [ln[0][0] for ln in lines]          # absolute start time of each line
for idx, ln in enumerate(lines):
    # per-word widths + phrase geometry (all states in a line share this)
    widths = [scratch.textbbox((0, 0), t, font=font, stroke_width=4)[2] - scratch.textbbox((0, 0), t, font=font, stroke_width=4)[0]
              for _, _, t in ln]
    gap = 24
    tw = sum(widths) + gap * (len(ln) - 1)
    BIG = 120
    base = Image.new("RGBA", (int(tw + 200), int(BIG * 2 + FS * 2)), (0, 0, 0, 0))
    xs = [100]
    for wd in widths[:-1]:
        xs.append(xs[-1] + wd + gap)
    # end of this line = start of the next line (or full video duration for the last)
    if idx + 1 < len(lines):
        hold_until = line_starts[idx + 1]
    else:
        hold_until = 30.0                          # overlays are clipped by -shortest anyway
    for j in range(len(ln)):     # state j: words 0..j lit
        state = base.copy()
        for wpos, (_, _, txt) in enumerate(ln):
            pal = [YELLOW, ORANGE] if wpos <= j else [DIM, DIM]
            render_text(state, xs[wpos], BIG, txt, font, pal, sw=4)
        alpha = state.split()[3]
        bb = alpha.getbbox()
        if not bb:
            continue
        m = 12
        l = max(0, bb[0] - m); t = max(0, bb[1] - m); r = min(state.size[0], bb[2] + m); b = min(state.size[1], bb[3] + m)
        crop = state.crop((l, t, r, b))
        MAXW = 600
        if crop.width > MAXW:
            sc = MAXW / crop.width
            crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
        p = os.path.join(WORK, f"cap_{idx:03d}_s{j}.png")
        crop.save(p)
        on = ln[j][0]            # light up when this word starts; hold to next line start
        states.append((on, hold_until, p))
print(f"[ok] {len(states)} karaoke states")

# ---- 4) ffmpeg: overlay each state enabled on its window, keep audio ----
N = len(states)
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", VIDEO]
for s, e, p in states:
    cmd += ["-loop", "1", "-i", p]
fc = ""
prev = "0:v"
WIDTH = 720
for i in range(N):
    s, e, _ = states[i]
    nxt = f"v{i}"
    lx = "(main_w-overlay_w)/2"
    ly = "main_h-overlay_h-110"
    win = f"between(t\\,{round(s,2)}\\,{round(e,2)})"
    fc += f"[{prev}][{i+1}:v]overlay=x={lx}:y={ly}:enable='{win}'[{nxt}];"
    prev = nxt
fc += f"[v{N-1}]scale={WIDTH}:1280,format=yuv420p[vout]"
cmd += ["-filter_complex", fc, "-map", "[vout]", "-map", "0:a", "-c:v", "libx264",
        "-preset", "fast", "-crf", "21", "-c:a", "copy", "-shortest",
        "-movflags", "+faststart", OUT]
print("running ffmpeg...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ffmpeg err:", r.stderr[-900:]); sys.exit(2)
print(f"[done] karaoke -> {OUT}")
