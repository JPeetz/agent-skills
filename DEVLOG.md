# DevLog — Agent Skills Repository Development History

_Narrative development log. Maintained by Skill Foundry. Every run adds an entry. Searchable by skill name, domain, keyword, and date._

---

## 2026-05-24 — Repository Inception

### Discovery
Initial launch — not a discovery run, but a foundation ship. Three skills built from AgentForge's internal department development, extracted as standalone Agent Skills per the agentskills.io specification.

### Selection
Three skills selected as v1.0.0 foundation:
1. **app-discovery-scrutiny** — Scored highest on Business Value (enables VC-grade analysis for any mobile app), Platform Portability (pure SKILL.md, no platform-specific tools), and Distinctiveness (no public equivalent at this quality level).
2. **app-scaffolding** — Fills a clear quality gap: existing scaffolding skills are generic PRDs, not 12-section production blueprints with exact hex colors, animation timing, and DB schemas.
3. **astra-campaign** — Covers the underserved marketing/campaign niche. Existing marketing skills repos (hyperfx-ai, coreyhaines31) focus on individual tactics. This skill runs the full agency pipeline.

### Improvements
All three built from AgentForge's real-world usage data:
- Corrections logs capture actual failures (Forge was a CLI tool, Runway/Luma didn't have API keys, SEO kill-floor killed mobile apps)
- Eval suites include near-miss negatives (CLI tools, SaaS products, Chrome extensions, Facebook ads)
- Scripts provide deterministic computation (scoring engine, claims checker, skill validator)
- Descriptions optimized per agentskills.io best practices (imperative, user-intent, near-miss protection)

### Challenges
- **GitHub repo naming:** Chose `agent-skills` (not `agentforge-skills` or `awesome-agent-skills`). Rationale: highest-SEO match for "agent skills," no company lock-in, clean `gh skill install` path. Tradeoff: requires the name to be available on GitHub — it was.
- **gh skill publish:** Discovered mid-build that GitHub launched `gh skill` in April 2026. Added official CLI install instructions. Validated repository compatibility.
- **Platform scope:** Decided Universal as default for all v1.0.0 skills. No platform-specific adapters needed yet — all three use standard SKILL.md + Python scripts with inline deps.

### Next Targets
- Broaden domain coverage beyond Business/Development/Marketing
- Source skills from community repos (anthropics/skills, hyperfx-ai/marketing-skills, coreyhaines31/marketingskills)
- Identify pain-point gaps: debugging, testing, security, documentation, CI/CD
- First autonomous run: Tuesday May 26 02:00 Dublin