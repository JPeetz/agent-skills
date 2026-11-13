---
name: "go-to-market-launch"
description: "Use this skill when planning a launch, beta, or GTM push."
version: "1.0.0"
author: "@artisan"
license: "MIT"
platforms:
  - claude-code
  - openclaw
  - cursor
  - codex
  - opencode
  - gemini-cli
permissions:
  files:
    read: true
    write: false
  network: false
  shell: false
metadata:
  hermes:
    tags:
      - go-to-market
      - launch
      - gtm
      - product-hunt
      - hacker-news
      - positioning
      - activation
      - owned-channels
      - launch-runbook
      - business-strategy
    related_skills:
      - "pricing-strategist"
      - "enterprise-consulting-methods"
      - "linear-project-management"
      - "app-discovery-scrutiny"
---

# Go-to-Market Launch

A launch is a **decision about scope and channel**, not a press release. This skill produces a launch plan a team can execute on a calendar: a go/no-go verdict, a tier, a channel map that ends in owned assets, a narrative, a runbook with rollback criteria, and an activation target that survives week two.

Output is a **plan document**, not copy. Ad creative and video assets are produced by other skills (see boundaries).

## When to Use

- Shipping a new product, a paid tier, or a feature that changes what the product *is*
- Choosing how loud to be: quiet ship vs private beta vs full public push
- Planning Product Hunt, Hacker News, or a directory/registry listing
- A launch date is fixed and you need a day-of runbook with abort conditions
- Post-launch: signups arrived and activation did not, and you need to find out why
- Converting a shipped repo or internal tool into a public release with an audience

## Do Not Use For

| Need | Use instead |
|------|-------------|
| Ad copy, hooks, scripts, A/B test plans for X/TikTok/IG | `astra-campaign` |
| Rendering a launch video (TTS, talking head, captions) | `agent-n-video-pipeline` |
| Setting the price itself | `pricing-strategist` |
| Ongoing content calendar after launch week | content strategy skill |
| Deciding whether the idea is worth building | `app-discovery-scrutiny` |
| Deal desk, discounting, sales compensation | revenue ops |

If the ask is "write my launch tweets," that is creative production. This skill decides *who to tell, in what order, with what proof, and when to stop.*

---

## Step 1 — Readiness Gate

Run this before any channel work. A loud launch of an unready product burns the one attention window you get with a channel; the second attempt is always weaker than the first.

### The SLC test (Simple, Lovable, Complete)

Launchable ≠ feature-complete. It means one job, done as a whole experience.

| Criterion | Passes when | Fails when |
|-----------|-------------|------------|
| **Simple** | It does one clearly stated thing | The pitch needs "and" three times |
| **Lovable** | A target user would *choose* it over their workaround | Users tolerate it to "give feedback" |
| **Complete** | No visible stub inside that one scope | "Coming soon" sits in the main flow |

Two opposite failure modes both kill launches:

- **Stealth mode** — polishing in private, waiting for perfect. Procrastination in a nice suit. Nothing ships, nobody learns you exist.
- **Just one more feature** — every date slips for one more thing. The launch becomes a permanent internal project.

Middle path: cut scope until one thing is lovable and complete, ship *that*, then launch the rest as updates. A launch you can repeat beats a launch you never do.

### Launch blockers (hard stops)

Any one of these true → do not run Tier 2:

- [ ] Core flow breaks for a new user on a clean account (no demo data, no hand-holding)
- [ ] Signup, payment, or email delivery has no one on call
- [ ] No way to measure activation (see Step 7) — you would be launching blind
- [ ] Support route is undefined (no inbox, no docs, no owner)
- [ ] Terms, privacy policy, or data-handling claim is missing where required
- [ ] Rollback is undefined: you cannot name how to turn the launch off

### Readiness verdict

Write one line: **SHIP / SHIP SMALL / HOLD**, plus the single biggest risk. If you cannot name the biggest risk, you have not looked.

---

## Step 2 — Launch Tiering

Pick the tier from *readiness × consequence of being wrong*, never from how excited the team is.

| | **Tier 0 — Quiet ship** | **Tier 1 — Beta** | **Tier 2 — Full push** |
|---|---|---|---|
| **Trigger** | Feature inside an existing product; reversible; low blast radius | New surface, real users, still-shifting scope | New product/category, or a moment competitors cannot copy quickly |
| **Audience** | Existing users, changelog readers | Named waitlist, 20–100 invited accounts | Everyone, all channels, one date |
| **Channels** | Changelog + in-app note + one owned post | Email to list, 1–2 rented posts, docs | ORB full set + PH/HN + borrowed placements |
| **Assets** | Screenshot, 5-line note | Landing page, demo GIF, onboarding email | Landing page, demo, 60–90s video, press kit, comparison page |
| **Success metric** | Adoption among exposed users | Activated invited cohorts | Activation rate + qualified pipeline |
| **Cost of failure** | Low — retry next week | Medium — invitees remember | High — channel credibility is spent once |
| **Reversibility** | Instant | Feature-flag off | Public; only mitigable |

Rules:

- **Default down.** Tier 2 is earned by a passing gate, not requested by enthusiasm.
- **One Tier 2 per quarter, per channel.** Channels remember. Two PH launches inside eight weeks splits your own vote.
- **A Tier 0 that goes well is the argument for Tier 1** — use the adoption data as the proof point.
- **Never tier up mid-launch.** Escalating on day one because signups spiked is how rollback criteria get ignored.

---

## Step 3 — ORB Channel Framework

Three channel classes, distinguished by who controls distribution.

### Owned — you control access
Email list, blog, docs site, changelog, branded community (Discord/Slack), the product itself.

- Compounds; no algorithm, no pay-to-play, no platform risk.
- Start with **one or two** matched to the audience: writers → blog; operators → email; developers → docs + community.
- An owned channel is only owned if you can export the list.

### Rented — visibility without control
X, LinkedIn, YouTube, Reddit, app stores, marketplaces, directories.

- Algorithms change, reach decays, rules are enforced unevenly.
- Use 1–2 where the audience already is; each post must have a path back to owned.
- Rented reach is a spike, not a base. A launch that lives only here ends on day three.

### Borrowed — someone else's audience
Guest posts, podcasts, newsletter features, co-webinars, creator reviews, speaking slots.

- Fastest credibility shortcut; also the least controllable timing.
- Ask for a specific slot tied to your date, not "sometime soon."
- A borrowed placement without an owned capture step is a vanity metric.

### The rule: everything routes to owned

Every rented post, borrowed mention, PH listing, and directory entry must terminate in an owned asset — email capture, waitlist, docs signup, or account creation.

```
Rented/Borrowed attention → landing page (single CTA) → owned list/account → onboarding → activation
```

If a channel cannot route anywhere owned, treat it as brand spend, not launch spend, and say so in the plan.

### Channel map (fill before launch)

| Channel | Class | Audience fit | Owned destination | Owner | Date |
|---------|-------|--------------|-------------------|-------|------|
| Changelog post | Owned | existing users | in-app | | T-1 |
| Email to list | Owned | warm | product | | T-0 |
| X thread | Rented | | landing page | | T-0 |

A map with twelve rented entries and no owned destination is a red flag.

---

## Step 4 — Launch Narrative

The narrative is four sentences and one demo. If it needs a deck to be understood, it is not ready.

### Positioning statement

> For **[specific user]** who **[situation/pain]**, **[product]** is a **[category]** that **[single outcome]**. Unlike **[alternative]**, it **[one defensible difference]**.

Keep the category recognizable. Inventing a category on launch day forces the audience to do work they will not do.

### Proof points

Three, ranked. Each must be checkable by a skeptic in under two minutes:

1. **Demo-able** — they can see it work (best)
2. **Measured** — a number you can source and defend (`N` runs, `X`% faster, `$Y` saved)
3. **Testimonial** — a named or clearly-described user with a specific before/after

Rules: no unlabeled projections, no "up to," no borrowed logos you have not earned. One overstated claim converts a technical audience into a hostile one.

### Objection table

Write the six objections you would raise if you were the buyer. This is the highest-leverage page in the plan — it becomes the FAQ, the PH comment replies, and the HN answers.

| Objection | What it really means | Response (proof point + link) |
|-----------|----------------------|-------------------------------|
| "This is a toy / demo" | needs to see durability | |
| "I can build this in a weekend" | needs the cost of the hard part | |
| "Why not <incumbent>?" | needs the specific trade-off | |
| "Is my data safe?" | needs the data path, plainly | |
| "What does it cost me later?" | needs the pricing shape, not a number | |
| "Who else uses it?" | needs one credible peer | |

### Demo

- 60–90 seconds, no voiceover intro, outcome visible in the first 5 seconds
- Recorded, not live, for the launch page; shows the *job*, not an interface tour
- Works on a fresh browser profile with no cached session — test this literally

---

## Step 5 — Channel Playbooks

### Product Hunt

Prep beats luck. The listing is a landing page with a vote counter.

**T-14 to T-7**
- Confirm the hunter or self-hunt; pick a launch date with no obvious giant shipping
- Write the tagline as the positioning statement's outcome clause, ≤60 chars
- Assets: gallery of 4–6 frames (outcome first, settings last), 30–60s demo, thumbnail legible at 100px
- Seed 15–30 people who will genuinely try it; ask for *feedback*, never for votes
- Verify the first-comment draft: what it is, who it's for, what's different, one link

**T-0**
- Launch 12:01am PT; the day runs on US waking hours
- Reply to every comment within 30 minutes, all day; answers, not thanks
- Do not link-drop in unrelated communities — that is the fastest way to get delisted
- Route every visitor to a page with email capture, not straight to signup

**T+1 to T+7**
- Thank-you note with the outcome; convert the listing traffic into the owned list
- Publish the "what we learned" post — it outperforms the launch post most of the time

Realistic expectations: a #1 day is a spike of low-intent traffic. Judge it on activated signups, not upvotes.

### Hacker News

The only channel where the comment section *is* the launch. Technical credibility or nothing.

- **Show HN** only for something people can try immediately; title = "Show HN: <what it does> (<how>)", no adjectives
- Post 6–9am ET on a weekday; be present for the first two hours
- Expect the harshest objection first ("this already exists", "what's the catch"); answer with mechanism, not marketing
- Never ask for upvotes, never use alt accounts, never argue with a hostile top comment — one calm technical reply and move on
- If it does not take, do not repost the same thing within weeks; ship something and try again later

### Directories and registries

Low effort, long tail, compounding SEO — roughly an afternoon total.

- Pick directories your audience actually browses (AI tool lists, dev registries, niche industry indexes), not the 200-site spray lists
- Reuse one asset set: 60-char tagline, 160-char and 300-word descriptions, logo, 3 screenshots, pricing shape
- Every listing links to an owned landing page with a UTM; revisit quarterly, since stale entries decay but still send traffic

---

## Step 6 — Launch-Day Runbook

One page, times in one timezone, named owners. Unnamed tasks do not happen.

| Time | Action | Owner | Done when |
|------|--------|-------|-----------|
| T-7 | Assets frozen; landing page and onboarding QA'd on a clean profile | | no P0 bugs open |
| T-3 | Email drafted and test-sent to 3 addresses incl. one external | | inbox + mobile render OK |
| T-1 | Staging → prod deploy; smoke test signup, payment, email, docs links | | all four pass |
| T-1 | Status page / support inbox monitored; on-call named for 48h | | rota posted |
| T-0 08:00 | Publish post + changelog; flip any flags | | URLs live |
| T-0 09:00 | Email send | | delivery rate > 97% |
| T-0 09:30 | Rented posts; PH listing live if used | | links resolve |
| T-0 hourly | Metrics check: signups, activation, errors, support queue | | dashboard open |
| T-0 18:00 | Day-one retro note: what broke, what converted | | written, not verbal |
| T+1 | Onboarding email sequence live; reply to every inbound | | queue empty |
| T+7 | Activation review against target; decide iterate vs expand | | decision recorded |

### Rollback criteria

Decide these *before* launch, in writing. A rollback call made under pressure defaults to doing nothing.

Abort the public push (delist / pause posts / pull the banner) when **any** of:

- Error rate on the core flow exceeds 5% for 15 minutes
- Signup or payment fails for a whole provider (not a single user)
- A data-exposure or auth issue appears — this is immediate, no debate
- Support queue exceeds 2× the on-call's capacity to answer within 4 hours
- The demo makes a claim the product cannot do; a wrong claim in public is worse than a missing launch

**Roll back quietly, communicate loudly.** Fix first, then a short factual note: what happened, who was affected, what changed. Silence after a public failure costs more than the failure.

---

## Step 7 — Post-Launch Measurement

Signups measure the channel. Activation measures the product. Only one of them predicts revenue.

### Define activation before launch

> A user is activated when they **[single observable action]** within **[window]**.

Good activation events are actions the user takes for their own benefit, and that a non-activated user cannot fake:

- Good: "created and shared one report within 7 days", "ran 3 analyses in first session"
- Bad: "completed onboarding", "invited a teammate" (proxy for intent, not value), "logged in twice"

### The report that matters

| Cohort | Signups | Activated | Activation % | Day-7 return % | Source |
|--------|---------|-----------|--------------|-----------------|--------|
| PH day | | | | | producthunt |
| HN | | | | | hn |
| Email list | | | | | owned-email |
| Directory | | | | | listing |

Read it by channel, not in aggregate. A 40% aggregate that hides 3% from PH and 55% from email tells you where to spend next time.

### Cadence

- **T+1**: funnel drop-off — where do new accounts die?
- **T+7**: activation by channel; kill the channel that produced noise, not the one that produced fewer, better users
- **T+30**: retention of the launch cohort vs pre-launch baseline. Did the launch attract a *different* user than the product is built for?

### Signals worth more than signups

- Activated accounts that returned without a reminder
- Inbound support questions that are about *use*, not *access*
- Pre-launch list converting at a materially higher rate than cold traffic — proof the narrative lands

---

## Anti-Patterns

- **Launching everything at once.** One push, then silence for a quarter. Stagger: launch the product, then ship the second act while attention lasts.
- **Big launch, no owned capture.** Traffic lands on a signup wall, bounces, and is gone forever.
- **Signups as the headline metric.** A spike with 4% activation is a paid lesson in vanity.
- **Tier inflation.** Calling it a "beta" while running a full public push — you get the scrutiny of a launch without the forgiveness of a beta.
- **Launching a stub** because the date was announced internally. Cut scope, keep the date.
- **Rollback criteria invented mid-incident.** Written in advance or it will not be used.
- **Borrowed mentions with no ask.** "Let us know if you'd like to cover it" converts to nothing; propose a date and an asset.
- **Claiming traction you do not have.** Numbers get checked. One fabricated metric ends the relationship with the exact audience you wanted.
- **Ignoring the comments.** On PH and HN the reply *is* the marketing; a silent launch reads as an abandoned one.
- **Post-launch silence.** The week after is where the launch either becomes a habit or a memory.

---

## Verification

Before handing the plan over, confirm:

1. A named readiness verdict (SHIP / SHIP SMALL / HOLD) with one stated biggest risk
2. The tier is justified by the gate, not by ambition, and is internally consistent (assets, channels, metric)
3. Every channel in the ORB map has an owned destination; no orphan rented channels
4. The narrative contains a positioning statement, exactly three proof points, and ≥5 objections with responses
5. The runbook has owners and times, and rollback criteria are numeric and written *before* T-0
6. Activation is defined as one observable action with a window, and the measurement table is per-channel
7. Nothing in the plan depends on a metric you cannot measure on T+7

## References

- `references/sources.md` — source skills, frameworks, and reading list behind this one

## License

MIT — see `LICENSE`.
