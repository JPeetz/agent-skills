# Scaffolding Corrections Log

_Real-world failures that shaped this skill. AgentForge test runs 2026-05-24._

## Correction 1: Scaffolded a Non-Mobile App (Forge)

**Problem:** Phase 6 generated a full scaffold for Forge before the mobile-only scope gate was added. The scaffold was technically correct but for the wrong platform.

**Fix applied:** Scaffolding now only triggers if scrutiny verdict is BUILD AND the candidate passes the Mobile-First Fit scoring dimension (6/10 minimum). CLI/SaaS scaffolds waste production time.

## Correction 2: Tool Honesty — Video & Music Claims

**Problem:** Initial tool section claimed Runway Gen-4.5 and Luma Dream Machine as primary/secondary video tools. Joerg: "Sorry, how can you create videos and music?" Neither API key existed.

**Fix applied:** Verified what's actually available:
- Images: fal.ai FLUX (✅ tested)
- Video: video_generate via openrouter/google/veo-3.1-fast (✅ available, 4-8s)
- Video: runway/gen4.5 (🔑 provider exists, needs RUNWAY_API_KEY)
- Music: music_generate via openrouter/google/lyria-3-pro-preview (✅ available, 180s)
- Removed all aspirational tool claims. Only verified tools listed.

## Correction 3: Local AI — Added After External Input

**Problem:** Original scaffold used Firebase/CloudKit for all AI. Joerg linked ai-agents-from-scratch repo.

**Fix applied:** Added Section 8.4 — Local-First AI Agent Architecture using llama.cpp/MediaPipe/MLX Swift with Phi-4-mini on-device. Mapping repo examples (intro/translation/react-agent/coding/scaling) directly onto app features. Competitive moat: zero cloud inference costs, offline capability, privacy nutrition label advantage.