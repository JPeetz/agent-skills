# Scrutiny Corrections Log

_Real-world failures that shaped this skill. AgentForge test runs 2026-05-24._

## Correction 1: CLI Dev Tools Mistaken for Mobile Apps

**Problem:** First test run picked Forge (CLI guardrail framework, 676 HN points) as winner. Joerg: "And that's a mobile app?"

**Root cause:** Platform-agnostic scoring. HN Show HN overweights dev tools.

**Fix applied:** Added hard scope gate — mobile apps only. Auto-reject: CLI tools, SDKs, libraries, desktop-only, Chrome extensions without mobile companion, infrastructure/dev tools. Added scoring note: "Mobile apps only. If a candidate isn't clearly a mobile app, eliminate before scoring."

## Correction 2: Kill-Floor Kills Mobile Apps on SEO

**Problem:** ShadowCat (QR file transfer) and Pablo (Chrome extension) killed on SEO even though their real discovery channel was Chrome Web Store / direct virality.

**Fix applied:** SEO → "SEO/ASO Opportunity." Score the HIGHER of ASO (for mobile apps) or SEO (for web apps). Never kill a mobile app on web SEO when App Store optimization is its real channel.

## Correction 3: Research-Without-Verification

**Problem:** First reports used inference-based competitor data because SearXNG was offline. Data was plausible but unverified.

**Fix applied:** Tavily web_search is now primary. Research phase must use live web_search/web_fetch. If research fails, flag it explicitly rather than inferring silently. "No winner today" is valid if data quality prevents scoring.