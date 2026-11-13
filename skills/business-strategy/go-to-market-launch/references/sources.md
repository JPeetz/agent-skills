# Sources & Reading

## Primary sources this skill was adapted from

### coreyhaines31/marketingskills — `skills/launch`
- Repo: https://github.com/coreyhaines31/marketingskills
- Skill: https://github.com/coreyhaines31/marketingskills/blob/main/skills/launch/SKILL.md

What was taken:
- **ORB framework** (Owned / Rented / Borrowed) and the "everything routes back to owned" rule
- Five-phase progression (internal → alpha → beta → early access → full launch) — here compressed into a tier decision, because the phases were implicit about *when* to escalate
- Product Hunt preparation model and the SavvyCal / Reform case notes
- Post-launch actions: onboarding sequence, roundup inclusion, comparison pages, interactive demo
- The major/medium/minor update triage matrix

What was changed:
- The readiness gate (SLC) was promoted from a preamble to a numbered step with hard blockers
- Checklist-only closing replaced with measurable verification criteria
- Ad-creative and video execution removed and delegated to dedicated skills

### phuryn/pm-skills — `pm-go-to-market`
- Repo: https://github.com/phuryn/pm-skills
- Plugin: https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market
- Skills used:
  - `gtm-strategy` — channel selection, messaging, success metrics, phased launch plan
  - `gtm-motions` — the seven motions (inbound, outbound, paid, community, partners, ABM, PLG) as a cross-check on channel choice
  - `beachhead-segment` — four criteria (burning pain, willingness to pay, winnable share, referral potential) for choosing the first audience
- Commands referenced: `/pm-go-to-market:plan-launch`, `/pm-go-to-market:battlecard`

What was taken: the metrics taxonomy (awareness → engagement → conversion → revenue → market), the audience-specific messaging discipline, and the go/no-go cadence.

What was changed: motion taxonomy is folded into the ORB classes rather than presented as seven parallel options, because ORB answers the only question that matters at launch — *who controls the distribution*.

## Frameworks named in the body

- **SLC — Simple, Lovable, Complete** — Jason Cohen (A Smart Bear). https://longform.asmartbear.com/slc/
  The antidote to both MVP-itis (minimal but unlovable) and stealth mode.
- **Positioning statement shape** — April Dunford, *Obviously Awesome* (2019). The For/who/is a/that/Unlike/because construction, plus the insistence that the category must be recognizable to the buyer.
- **Activation metric** — the "aha moment" framing common to PLG practice; see Wes Bush, *Product-Led Growth* (2019), and Reforge's activation material. Rule applied here: activation must be an action the user takes for their own benefit within a fixed window.
- **Rollback / kill-switch criteria** — borrowed from incident-management practice (Google SRE Workbook, "Canarying Releases"); a launch is a canary with a marketing budget.

## Boundaries — skills that own adjacent work

| Skill | Path | Why it is not this skill |
|-------|------|--------------------------|
| `astra-campaign` | `skills/marketing/astra-campaign` | Produces ad creative — hooks, scripts, image/video prompts, A/B test plans for X/TikTok/IG. This skill decides *when* to run ads and *to what destination*, then hands off. |
| `agent-n-video-pipeline` | `skills/marketing/agent-n-video-pipeline` | Renders the launch video (TTS, talking-head render, captions) on local hardware. This skill writes the demo brief it is given. |
| `pricing-strategist` | `skills/business-strategy/pricing-strategist` | Sets the model and range. This skill only needs the *shape* of pricing for objection handling. |
| `app-discovery-scrutiny` | `skills/business-strategy/app-discovery-scrutiny` | Runs before this one: is the thing worth building at all. |
| `linear-project-management` | `skills/business-strategy/linear-project-management` | Tracks the tasks this plan generates, once they exist. |

## Verification notes

- Claims about Product Hunt and HN mechanics (timing, rules, comment dynamics) are operational norms, not published guarantees; platform rules change and should be re-checked before a Tier 2 push.
- The case examples (Superhuman, Notion, TRMNL, SavvyCal, Reform) come from the marketing skills source and are illustrative, not benchmarks.
- No traffic, conversion, or revenue figures are asserted anywhere in this skill as expected outcomes. If a plan needs a projection, it must be labeled as one.

## Further reading

- April Dunford — *Obviously Awesome* (positioning) and *Sales Pitch* (narrative)
- Jason Cohen — SLC and "just one more feature" essays on A Smart Bear
- Gabriel Weinberg & Justin Mares — *Traction* (nineteen channels; the ORB classes are a coarser cut of the same idea)
- Google SRE Workbook — canarying and rollback discipline, applied here to public launches
- Hacker News `showhn` guidelines — https://news.ycombinator.com/showhn.html
