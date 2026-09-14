# Changelog

## [1.0.0] — 2025-05-15

### Added
- Initial release as combined meta-skill package
- 15 enterprise consulting methodology patterns from github.com/sruthir28/enterprise-ai-skills

### Included Skills

**Framing (3 skills):**
- SCPR Framework — Situation-Complication-Problem-Recommendation argument structure
- Issue Tree Builder — MECE problem decomposition
- Hypothesis Tree — Day-1 hypothesis commitment and testing

**Analysis (4 skills):**
- Synthesis — Insight extraction from raw data
- Prioritization — RICE, Impact/Effort, Value/Complexity, Weighted Scoring
- AI Use-Case Scorer — Value × Feasibility × Safety scoring
- Data Insights — Plain-English dataset analysis

**Writing (3 skills):**
- Decision Memo Builder — 1-page yes/no decision artifact
- Top-Down Memo (Minto Pyramid) — Answer-first writing
- Storyline Builder — Slide narrative construction

**Meetings & People (3 skills):**
- Meeting Prep Kit — Pre-read, agenda, talking points, objections
- Stakeholder Map — Power/Interest grid with stance mapping
- Workshop Designer — Half-day/full-day workshop agendas

**Decks (2 skills):**
- McKinsey Charts — Native python-pptx chart objects (bar+callout, stacked over time, waterfall)
- Deck Pipeline — 4-agent pipeline (Strategist → Builder → Critic → Fixer)

**Quality (1 skill):**
- McKinsey Critic — EM-level review framework

### Improvements over source material
- All 15 skills consolidated into one SKILL.md with cross-referencing and composition patterns
- Added full YAML frontmatter with hermes tags and related_skills
- Added comprehensive "Common Pitfalls" section with per-skill mistake catalog
- Added "Verification" section with per-skills acceptance criteria
- Added "Composition Patterns" table mapping real needs to skill stacks
- Added canonical full strategic engagement workflow (6 phases)
- Added eval test cases (evals/evals.json)
- Added reference implementation (references/charts.py — the full python-pptx chart code)
- Added CHANGELOG with proper versioning
- Added MIT LICENSE with attribution to original author
- Organized by consulting category (Framing, Analysis, Writing, Meetings, Decks, Quality)
- Standardized SKILL.md format per Hermes skill packaging conventions
