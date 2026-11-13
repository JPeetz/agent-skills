# Changelog

All notable changes to this skill are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-13

### Added
- Initial release by @artisan, adapted from `coreyhaines31/marketingskills` (`skills/launch`) and `phuryn/pm-skills` (`pm-go-to-market`), reworked to this repo's conventions.
- `SKILL.md` — seven-step workflow: readiness gate → launch tiering → ORB channel map → narrative → channel playbooks → launch-day runbook → post-launch activation measurement.
- Readiness gate built on the SLC (Simple, Lovable, Complete) test, with the two opposing failure modes (stealth mode, just-one-more-feature) and six hard launch blockers.
- Launch tiering matrix (Tier 0 quiet ship / Tier 1 beta / Tier 2 full push) keyed to readiness and blast radius, with default-down and no-mid-launch-escalation rules.
- ORB framework (Owned / Rented / Borrowed) with the "everything routes to owned" rule and a channel-map table that forces an owned destination per channel.
- Launch narrative kit: positioning statement template, ranked proof-point types, a six-row objection table that becomes the FAQ and the comment replies, and demo rules.
- Product Hunt, Hacker News, and directory playbooks with realistic expectations (activated signups, not upvotes).
- Launch-day runbook with named owners and times, plus numeric rollback criteria written before T-0.
- Activation-first measurement: activation defined as one observable action with a window, per-channel cohort table, T+1/T+7/T+30 cadence.
- `references/sources.md` — source skills, frameworks, boundaries, and reading list.
- `evals/evals.json` — three evaluation scenarios: quiet launch, full launch, and launch with issues.
- `LICENSE` (MIT) and this changelog.

### Changed from source
- Frontmatter extended to repo conventions: `version`, `author`, `license`, `platforms`, and read-only `permissions` (planning skill: no network, no shell, no writes).
- Description cut to 54 characters so routing does not depend on a paragraph.
- Merged the sources' phases into an explicit tier decision, which the originals left implicit, and added the boundary table separating this skill from ad-creative and video-production skills.
- Replaced the sources' checklist-only close with a verification section tied to measurable output.
