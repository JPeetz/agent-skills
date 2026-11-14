# Sources — Product Manager Toolkit

Provenance for the frameworks in `SKILL.md`, plus the reading they are condensed from.
Thresholds marked **(heuristic)** are defaults from practice, not published constants — argue with them.

---

## RICE

- **Origin:** Sean McBride, Intercom, 2016 — "RICE: Simple prioritization for product managers". Publicly documented; the four factors and the canonical impact multipliers (3 / 2 / 1 / 0.5 / 0.25) come from that post.
- **Confidence scale** (100 / 80 / 50 / 20) is from the same post; this skill adds the rule that unsupported items are capped at 50% rather than excluded.
- **Extensions:** `Reach × Impact × Confidence / Effort` variants (RICE+, weighted RICE, VAN) exist; all of them exist to separate evidence quality from value size. The skill keeps the base formula because it is the one a team can argue about in one meeting.
- **Known criticisms:** reach and effort are not commensurable, the score hides dependencies, and the confident team wins. The SKILL.md "Rules that keep RICE honest" subsection is derived from those critiques.

## Jobs to be Done / Interview synthesis

- Clayton Christensen, Taddy Hall, Karen Dillon, David Duncan — *Competing Against Luck* (2016). Job as progress-in-a-situation; "workaround = real competitor" follows directly.
- Bob Moesta & Chris Spiek — the Switch interview / forces diagram (push, pull, anxiety, habit). Underpins "ask about the last time, not hypotheticals".
- Rob Fitzpatrick — *The Mom Test* (2013). Three rules: talk about their life not your idea, ask about specifics in the past, talk less. The "never pitch" and "ask past behavior" guidance is this book.
- Teresa Torres — *Continuous Discovery Habits* (2021). Interview snapshots and opportunity solution trees; the participant-count discipline is adapted from her opportunity mapping.
- Affinity mapping: standard UX-research practice (KJ method, Jiro Kawakita, 1960s). The "cluster by behavior, not noun" rule is a practitioner convention, not from the original method.

## Opportunity Scoring

- Anthony Ulwick — *What Customers Want* (2005) and the Outcome-Driven Innovation method (Strategyn). Formula: `Importance + max(Importance − Satisfaction, 0)`.
- The scoring is only valid on *outcome statements* ("minimize the time to…"), not on features. Scoring features with it produces a wishlist.

## PRD practice

- Marty Cagan — *Inspired* (2nd ed., 2017): the product-discovery framing, problem before solution, and why a spec-style PRD fails.
- Atlassian / Aha! / Productboard public PRD templates contributed the artifacts-not-features structure and the must/should/won't split. The MoSCoW mnemonic is Dai Clegg, Oracle, 1994.
- Kill criteria and "revisit if" are adapted from Amazon's working-backwards habit and from Bezos's Type 1 / Type 2 decision framing (1997 shareholder letter, formalized 2015).

## OKRs

- John Doerr — *Measure What Matters* (2018); Andy Grove at Intel (1975) is the origin of the practice.
- Christina Wodtke — *Radical Focus* (2nd ed., 2021). The "grade the bet, not the execution" retro and the 0.7-is-good scoring norm come from here.
- Google's re:Work OKR guide for the 0–1 scoring convention and the "OKRs are not performance reviews" caveat.
- Leading vs lagging indicators: the distinction is standard in the 4 Disciplines of Execution (McChesney, Covey, Huling, 2012). The requirement that each objective carry at least one lagging KR is this skill's own guard against teams optimizing only the inputs.

## Decision frameworks

- **DACI:** developed at Intuit; widely taught at Atlassian. The "exactly one approver" rule is the whole point — consensus is a different, slower decision mode.
- **DARE:** Decision, Alternatives, Reasoning, Evidence — a decision-record convention (a lightweight cousin of ADRs, Michael Nygard, 2011). The added `Revisit if` line is this skill's contribution.
- **Type 1 / Type 2 decisions:** Jeff Bezos, 2015 Amazon shareholder letter — reversible decisions should be made fast by a small group; this is why the skill tells you to *skip* the framework when the call is cheap and reversible.

## Roadmap and stakeholder communication

- Cagan's four risks (value, usability, feasibility, business viability) — used implicitly in the PRD "Risks" table.
- Teresa Torres and Petra Wille on stakeholder alignment; the "bad news first, with a plan and a date" rule is standard crisis-communication practice applied to product updates.
- Patrick Lencioni — *The Five Dysfunctions of a Team* (2002), for the observation that trust dies on surprises rather than on misses.

---

## Reading list (order matters)

1. *The Mom Test* — Fitzpatrick. Two hours. Fixes interviews immediately.
2. *Inspired* — Cagan. The frame for everything else.
3. *Continuous Discovery Habits* — Torres. Turns discovery into a weekly habit.
4. *Measure What Matters* — Doerr. Skim; take the cadence, not the religion.
5. *Radical Focus* — Wodtke. The honest version of OKRs.
6. *Escaping the Build Trap* — Melissa Perri (2018). On outcomes vs outputs at org level.

## Source quality note

RICE and opportunity scoring are published formulas — cite them as such. OKR guidance is practice-derived and varies by organization; treat every threshold in this skill (0.7 is a good score, 8–12 interviews saturate, ≤50% confidence means research) as a heuristic to be tuned against your own data, not a standard to be enforced.
