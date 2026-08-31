# Campaign Corrections Log

_Real-world failures that shaped this skill. AgentForge 2026-05-24._

## Correction 1: Tool Honesty — The Runway/Luma Lie

**Problem:** Initial AGENTS.md claimed Runway Gen-4.5 was primary video tool, Luma Dream Machine was secondary. Joerg called it instantly: "Sorry, how can you create videos and music?"

**Root cause:** Accepted the spec's tool stack as aspirational reality. Didn't verify API access before listing.

**Fix applied:** Ran `video_generate action=list` and `music_generate action=list` to inventory all providers. Found 14 video providers (2 configured: openrouter/veo-3.1-fast ✅, runway/gen4.5 🔑 needs key) and 5 music providers (1 configured: openrouter/lyria-3-pro ✅). Updated tool section to reality. Runway is now "future upgrade once key is set" — never listed as primary until verified.

## Correction 2: Over-Instruction — Platform Character Limits

**Problem:** Listed "Headline max 70 characters" and "Caption max 150 characters" — agents already know platform limits. This is context waste per best practices.

**Fix applied:** Trimmed platform rules to what the agent WOULDN'T know: X requires contrarian framing, TikTok needs creator voice not ad voice, Instagram needs caption hierarchy. Platform character limits are universal knowledge — removed.

## Correction 3: Generic "Use X tool" → Engine-Specific Routing

**Problem:** Original spec said "Use tools optimized for photorealism" — vague, agent picks wrong tool.

**Fix applied:** Explicit routing rule: Still → fal.ai FLUX (schnell/dev/pro-ultra). Video → openrouter/veo-3.1-fast. Music → openrouter/lyria-3-pro. Per-asset: exact model, settings, seed, and engine-aware prompt. No generic "use a video tool" — always "use video_generate with openrouter/google/veo-3.1-fast, 9:16, 8s, seed 42."

## Correction 4: Skills From Spec vs Skills From Experience

**Problem:** The first AGENTS.md was essentially the spec rephrased — a LLM-synthesized skill from generic knowledge.

**Fix applied per best practices:** Extracted from the real hands-on task of building this department. The corrections above are more valuable than the original instructions — they capture what went wrong and why. Future campaigns should reference this log before creative output to avoid repeating the same mistakes.