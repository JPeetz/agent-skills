---
name: financial-modeling
description: >-
  Use this skill when building financial models — three-statement models,
  bottoms-up P&L, scenario planning, forecasting, or valuation. Activates on
  "financial model", "three-statement model", "P&L", "balance sheet", "cash flow
  forecast", "scenario planning", "pro forma", "unit economics", "bottoms-up",
  "top-down forecast", "sensitivity analysis", "SaaS model", "fundraising
  model", "cap table", "DCF", or "runway model". Covers driver-based revenue
  builds, COGS and OPEX structure, P&L → balance sheet → cash flow links,
  best/base/worst scenarios, tornado sensitivity, DCF and terminal value,
  dilution and liquidation waterfalls, and the checks that catch a model that
  does not foot.
version: 1.0.0
author: Skill Foundry
license: MIT
category: finance-ops
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - finance
  - financial-modeling
  - forecasting
  - unit-economics
  - P&L
  - balance-sheet
  - cash-flow
  - scenario-planning
  - fundraising
  - valuation
  - DCF
  - three-statement
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
permissions:
  files.read: true
  files.write: true
  network: false
  shell.execute: true
  dangerous: false
metadata:
  tags:
    - finance
    - financial-modeling
    - forecasting
    - unit-economics
    - three-statement
    - scenario-analysis
    - valuation
  related_skills:
    - saas-metrics-coach
---

# Financial Modeling

Build a model that answers one question, foots to the penny, and survives an investor's second pass. The output of this skill is a driver tree, a three-statement model, a scenario switch, and a written set of assumptions — not a spreadsheet-shaped guess.

## The One Rule

**Every number in the model must trace to a driver the reader can argue with.** A revenue line that says "$4.2M in 2028" is an opinion. A revenue line that says "480 customers × $9k ACV, from 12 sales reps at 4 ramped deals/rep/quarter" is a model — the reader can disagree with the rep productivity, and that disagreement is the conversation worth having. If you cannot name the driver, you do not have a forecast; you have a target.

## Workflow

0. **Frame the decision.** Ask what the model is *for*: fundraise, board pack, hiring plan, pricing change, acquisition, covenant test. The purpose sets the horizon, the granularity, and which line must be right. A fundraising model is a growth and burn story over 24–36 months; a covenant model is a liquidity story over 12; a pricing model is a cohort and elasticity story. Never build one model to serve all three.
1. **Choose the model type.** Three-statement, bottoms-up P&L, top-down market model, or cohort/vintage model — see `references/model-framework.md` for fit by company stage. Most real models are a bottoms-up engine wrapped in a three-statement shell.
2. **Build the driver tree** before any arithmetic. Revenue drivers, cost drivers, working-capital drivers, financing drivers. Each driver gets: a value, a source, a range, and an owner.
3. **Build revenue bottoms-up**, then COGS, then OPEX, then headcount (headcount drives most of OPEX and is the most common place models drift from reality).
4. **Wire the three statements** through the link table below. Build the balance sheet from the cash flow, never independently.
5. **Add scenarios** as a single switch that flips named driver sets — not three copies of the model.
6. **Run sensitivity** on the 3–5 drivers that actually move the answer, and show it as a tornado, not a paragraph.
7. **Check the model.** Balance sheet balances, cash ties, ARR ties to the MRR roll-forward, headcount ties to payroll, no hardcoded numbers inside formulas.
8. **Present** the summary tab, the assumptions page, and the sensitivity — in that order — and state the falsifiable claim.

## Bottoms-Up P&L Construction

Bottoms-up means building from the unit that generates revenue and the person who costs money, then aggregating. Top-down means starting from a market size and asserting a share. Use bottoms-up for anything you will be held to; use top-down only as a cross-check.

### Revenue by channel

Build each channel separately, because they have different economics, different ramp, and different ceilings:

| Channel | Driver | Unit | Typical build |
|---|---|---|---|
| Inbound / self-serve | Traffic × conversion × ACV | visitors | traffic from content/SEO growth curve, 1.5–3% visitor→trial, 20–30% trial→paid |
| Outbound | Reps × ramped productivity × win rate | reps | 3-month ramp to quota, 60–80% attainment, quota ÷ ACV = deals |
| Partner / channel | Partners × attach × ACV | partners | 1–2 quarter lag from signing to first revenue |
| Expansion | Base × expansion rate | installed base | applied to beginning-of-period base, never to new logos in the same month |
| Enterprise | Pipeline coverage × win rate | pipeline | 3× coverage of target, 6–9 month cycles, revenue lands 2 quarters after pipeline |

Rules that keep the build honest:

- **New logos carry a ramp.** A rep hired in month 1 does not produce at quota until month 4. Model `productivity ramp = [0.0, 0.25, 0.6, 1.0]` by tenure, and apply it per rep cohort, not to the average.
- **Seasonality is real.** Q4 enterprise close, August European holiday, January self-serve spike. If the model is flat, it is wrong before it is optimistic.
- **Expansion applies to the base only.** Applying expansion to the same month's new business double-counts.
- **Cap the growth rate.** A 15%/month compounding new-business line implies 435% annual growth by year three. Set a terminal growth rate and glide to it.

### COGS

Three components, and keep them separate because each scales differently:

1. **Variable hosting/infrastructure** — % of revenue, declines with scale (12% → 8%) if there is real architecture leverage; do not assume that decline without an engineering reason.
2. **Support / services delivery** — headcount-driven. Tickets per customer × tickets per agent per month. Ratio-based (1 support agent per 150 accounts) is defensible; "% of revenue" hides the step function.
3. **Third-party / payment fees** — 2.5–3.5% of collected revenue, plus per-transaction costs. Easy to forget; material at scale.
4. **Amortization of capitalized implementation** — if you capitalize, the amortization belongs here, not in D&A of company capex.

Gross margin target ranges by model: pure SaaS 75–85%, SaaS + usage 65–78%, marketplace 60–75% (take rate dependent), hardware-enabled 35–55%, services-heavy 25–45%. If your model shows 90% at $1M ARR and 70% at $20M, you have assumed the opposite of scale economics — justify it or fix it.

### OPEX

Structure by department, and drive every department by headcount plus a non-headcount line:

| Department | Headcount driver | Non-headcount driver |
|---|---|---|
| Engineering | roadmap: squads × engineers per squad | tooling, cloud dev, contractors (10–15% of eng cost) |
| Product & Design | ratio to engineering (1:6–1:8) | research, design tools |
| Sales | quota-carrying reps + 1:4 management + 1:8 SDR | commissions (8–12% of new ARR), travel, events |
| Marketing | ratio to sales (1:3–1:5) | program spend = % of target new ARR, 40–60% of S&M |
| Customer Success | accounts per CSM (1:100 SMB, 1:25 enterprise) | CS tooling, training |
| G&A | % of revenue, glides 12% → 7% with scale | audit, legal, insurance, rent |

Two structural rules:

- **Fully loaded headcount cost** = base × (1 + burden). Burden is 1.25–1.35 in the US (payroll tax, benefits, workers' comp), higher with equity and 401k match. Understating burden by 25% is a 25% miss on the largest cost line.
- **Hiring is lumpy and lags.** An approved req closes in 45–90 days; salary starts the month after close. Model the close lag, or your opex will be optimistic in exactly the quarter you present.

## The Three-Statement Model

The three statements are one system with three views. Build in this order and never break the links:

| From | To | Link | Sign |
|---|---|---|---|
| Revenue | P&L | accrued revenue for the period | + |
| Revenue | Balance sheet | accounts receivable = revenue ÷ 30 × DSO | + asset |
| Deferred revenue | Balance sheet | billings collected in advance of recognition | + liability |
| COGS | Balance sheet | accounts payable = COGS ÷ 30 × DPO | + liability |
| EBITDA | Cash flow | starting point, after adding back non-cash | + |
| D&A | P&L / Cash flow | capex ÷ useful life, added back in CFO | − P&L, + CF |
| Net income | Balance sheet | retained earnings roll-forward | + equity |
| Capex | Balance sheet | gross PP&E; accumulates, depreciates | + asset |
| Ending cash | Balance sheet | **must equal** cash flow ending balance | + asset |
| Debt draw / repay | Cash flow | financing section | ± |
| Equity raised | Cash flow | financing section; also option pool | + |

**Build order:** P&L → cash flow → balance sheet, with cash as the plug from cash flow. If you build the balance sheet independently and plug with a "balancing" row, you have hidden an error, not fixed one.

**The balance check is non-negotiable.** `Assets − (Liabilities + Equity) = 0` every month, to the cent. A residual means: a P&L line is not flowing to retained earnings, a capex/depreciation mismatch, or a working-capital line is being computed on the wrong base. `scripts/financial_model_builder.py` reports the residual per month and flags any month where it exceeds tolerance.

**Opening balances.** A model with no opening AR/AP/deferred revenue shows a large artificial cash inflow in month 1. Set opening balances from the last actual close, or state explicitly that month 1 is a fresh start with zero working capital.

## Scenario Planning

Scenarios are **named driver sets**, not duplicate models. Implement as one switch (`scenario = base`) that selects a value per driver from a scenario table. A duplicated model guarantees that the models diverge the first time someone edits one.

| Driver | Worst | Base | Best | Rationale |
|---|---|---|---|---|
| New logo adds / month | −40% vs base | plan | +20% vs base | pipeline coverage assumption |
| Net revenue churn | 2.5%/mo | 1.5%/mo | 1.0%/mo | last 4 cohorts |
| ACV | −10% | plan | +10% | discounting pressure |
| Hiring | freeze non-critical | plan | +2 reps/quarter | plan approval |
| Gross margin | −4 pts | plan | +2 pts | infra renegotiation |
| Collections (DSO) | 55 days | 40 days | 30 days | customer mix |

Three rules:

- **Worst case must be survivable, not theatrical.** A worst case where the company dies in month 8 is not a scenario, it is a fundraising argument. Show the management action that extends runway (hiring freeze, program spend cut) and the resulting runway.
- **Scenarios differ in drivers, not in the terminal multiple.** Changing the exit multiple is not a scenario, it is a valuation assumption.
- **Report the trigger.** For each scenario, state the observable that tells you which one you are in ("NRR < 100% for two consecutive quarters") and the decision it triggers ("freeze S&M hiring").

## Sensitivity Analysis

Sensitivity answers "what actually matters." Two forms, both required in a serious model:

**One-way sensitivity / tornado.** For each of the top 5 drivers, flex ±20% (or a defensible range), hold everything else at base, and record the change in the outcome (Year-3 revenue, ending cash, enterprise value, IRR). Rank by swing magnitude — that ranking *is* the tornado chart, and it is the single most useful slide in a board deck.

**Two-way table.** Pick the two largest drivers and show the outcome across a 5×5 grid. The most valuable cell is the one where the outcome crosses a threshold — the month runway falls below 12, or the year EBITDA turns negative.

**Breakeven.** Compute the value of each driver at which the outcome flips sign (e.g. "churn above 2.2%/month and we never reach breakeven inside 36 months"). Breakevens are more persuasive than forecasts because they are falsifiable.

**Correlation is the trap.** Revenue growth and hiring are positively correlated; flexing them independently produces scenarios that cannot happen. In multi-way sensitivity, constrain correlated drivers to move together, or state that the table is a mechanical bound rather than a joint distribution.

## Unit Economics

Unit economics is the test of whether growth creates or destroys value. Compute at the **cohort** level, on **gross-margin dollars**, with the **payback period** stated:

- **CAC** = fully loaded S&M (including salaries, tools, programs, commissions) ÷ new customers acquired in the period. Blended CAC hides channel failure; compute paid CAC separately.
- **LTV** = ARPA × gross margin ÷ monthly churn (or a defined-lifetime variant: ARPA × GM × expected lifetime months). State the variant; they differ by 30%+.
- **LTV/CAC** healthy band 3–5×. Above 5× usually means underinvestment in growth, not excellence.
- **CAC payback** = CAC ÷ (ARPA × GM). Under 12 months is strong for SMB, 18–24 acceptable for mid-market, 24–36 for enterprise. Payback is the metric that governs cash, so it belongs in the model's cash section.
- **Contribution margin** = revenue − variable COGS − variable S&M − variable success. Must be positive per account before scale means anything.
- **Marginal unit economics** differ from average. The next 100 customers usually cost more to acquire than the last 100. If the model's growth assumes flat CAC while the market is getting harder, it is optimistic by construction.

**Negative unit economics with a plan to fix them is a legitimate early-stage position. Negative unit economics with no stated fix is a business that loses money faster as it grows.** Say which one you have.

## SaaS-Specific Modeling

A SaaS model is a **stock-and-flow** on recurring revenue, not a revenue line with a growth rate.

```
begin_mrr
  + new business MRR        (logos × ACV ÷ 12)
  + expansion MRR           (begin_mrr × expansion rate)
  − contraction MRR         (begin_mrr × contraction rate)
  − churned MRR             (begin_mrr × churn rate)
= end_mrr
```

Things that separate a real SaaS model from a fake one:

- **Cohort decay.** Retention is not constant: month 1 churn is 3× month 12 churn. Model a decay curve or a cohort triangle, and let the aggregate fall out. A single blended churn rate applied to a growing base overstates long-run revenue.
- **Expansion is a function of base and time.** NRR above 100% comes from seat growth and upsell; it decays as the base matures and as the mix shifts to smaller accounts. Model NRR gliding toward 100–105%, not staying at 130% for five years.
- **Virality is a loop, not a rate.** If the model claims a viral coefficient, define it (`new users per existing user per month`), constrain k < 1 for paid-independent growth, and show the loop's cost (referral credits are COGS or S&M, not free).
- **Contraction and churn are different lines.** Contraction (downgrade) is often larger than churn in SMB; collapsing them hides the rescue motion's effectiveness.
- **Annual vs monthly contracts change cash, not revenue.** Annual-upfront improves cash and deferred revenue; it does not change recognized revenue. Model billing terms as a separate driver, or the cash flow will be wrong by a full year of prepayments.

## DCF Valuation

For a venture-stage company, DCF is a discipline for testing assumptions, not an oracle. Run it anyway — it forces terminal-value honesty.

1. **Project unlevered free cash flow** for 5–10 years: `EBIT × (1 − tax) + D&A − capex − ΔNWC`. Use EBIT, not EBITDA — taxes and capex are real.
2. **Terminal value**, one of two ways, and state which:
   - **Gordon growth:** `FCF_terminal × (1 + g) ÷ (WACC − g)`, with `g` = 2–3% (never above long-run GDP).
   - **Exit multiple:** `terminal EBITDA × multiple`, with the multiple sourced from current public comparables and *cross-checked* against the Gordon value. A 12× exit multiple implies a specific growth and margin profile — check that the model actually has it.
3. **WACC** = `E/V × Ke + D/V × Kd × (1 − tax)`. For a venture-stage company, Ke from CAPM plus a size/illiquidity premium lands at 12–20%; a seed-stage company discounting at 10% is flattering itself. Use a range, and show the value at both ends.
4. **Discount** at mid-year convention if cash flows arrive through the year (multiply the discount factor by `(1 + WACC)^0.5`).
5. **Bridge to equity value**: enterprise value + cash − debt − preferred liquidation preference (if valuing common) − option pool on an as-converted basis.
6. **Sensitivity is mandatory**: enterprise value across WACC ±2 pts × terminal growth ±1 pt. The spreadsheet cell is worth less than the shape of the grid. When 80% of the value sits in the terminal value, say so out loud — it means the model is a bet on the terminal assumption, not on the forecast.

## Fundraising Model

The fundraising model answers three questions: how much, at what price, and what does everyone own afterwards.

- **Pre-money / post-money.** `post = pre + new money`. Price per share = `pre-money ÷ fully diluted pre-money shares`. Investors' ownership = `new money ÷ post-money`. Founders often conflate pre-money valuation with the post-money number they will read in the press release; state both.
- **Fully diluted shares** = issued common + all preferred on an as-converted basis + all outstanding options + **unallocated option pool**. The pool is included *before* the round in the pre-money, which is why the pool top-up dilutes founders, not investors.
- **Option pool shuffle.** Investors typically require the post-close unallocated pool to be 10–15% of fully diluted. Model the top-up explicitly: `pool_shares_needed = target_pct × post_shares − existing_unallocated`, and show the founder dilution it causes. This single line routinely costs founders 3–5 points and is omitted from most founder-built models.
- **SAFE notes.** Post-money SAFEs convert at `valuation_cap ÷ (cap ÷ price)` and their ownership is fixed at signing (`purchase amount ÷ post-money cap`). Stacking multiple SAFEs with different caps dilutes founders multiplicatively — model each note separately, then convert at the priced round. Pre-money SAFEs dilute founders against each other; the post-money SAFE does not. Know which one you signed.
- **Dilution waterfall.** For each round: pre-money, new money, post-money, price per share, shares issued, founder %, employee %, prior investor %, new investor %. Carry it forward so Series B dilution is computed on the Series A post-close cap table, not on today's.
- **Liquidation waterfall** (for exits): return preference (1× non-participating is standard), participation caps, and the conversion decision at each exit value. A $30M exit on a $40M post-money Series A can pay the common nothing — show that crossover explicitly.
- **Runway and round size.** `round size = monthly net burn × months of runway + buffer`. 18–24 months is the standard ask because it reaches the next milestone without a bridge. Show the post-raise runway and the hiring the round funds; a round that funds 36 months of the same plan is a round that under-raises the ambition.

## Metrics the Model Must Emit

| Metric | Definition | Why the model needs it |
|---|---|---|
| ARR | end MRR × 12 | the headline; must tie to the roll-forward |
| MRR growth | MoM and annualized | separates trajectory from level |
| NRR | (begin + expansion − contraction − churn) ÷ begin | expansion engine health |
| GRR | (begin − contraction − churn) ÷ begin | retention floor; caps everything |
| Gross margin | (revenue − COGS) ÷ revenue | scaling quality |
| CAC payback | CAC ÷ (ARPA × GM) | cash intensity of growth |
| LTV/CAC | margin-based LTV ÷ fully loaded CAC | growth efficiency |
| Burn multiple | net burn ÷ net new ARR | capital efficiency of the growth plan |
| Rule of 40 | revenue growth % + EBITDA margin % | balance of growth and profit |
| Magic number | ΔARR ÷ prior-period S&M | S&M payback speed |
| Runway | cash ÷ trailing 3-month average net burn | the survival number |
| Quick ratio | (new + expansion) ÷ (churn + contraction) | growth vs. leakage |

`scripts/financial_model_builder.py` emits all of these per month plus an annual roll-up, and runs the balance and cash reconciliation checks on every period.

## Using the Script

```bash
python3 scripts/financial_model_builder.py --input model.json --format markdown
python3 scripts/financial_model_builder.py model.json --format json --pretty
cat model.json | python3 scripts/financial_model_builder.py --self-test
python3 scripts/financial_model_builder.py --self-test      # built-in demo, verifies invariants
```

Minimal input:

```json
{
  "company": "Acme",
  "currency": "USD",
  "start_month": "2026-01",
  "months": 36,
  "revenue": {
    "starting_mrr": 180000,
    "new_mrr_start": 22000,
    "new_mrr_growth": 0.03,
    "churn_rate": 0.014,
    "expansion_rate": 0.011,
    "contraction_rate": 0.004
  },
  "cogs": {"hosting_pct": 0.09, "support_pct": 0.05, "payment_pct": 0.028, "fixed_monthly": 4000},
  "headcount": {
    "departments": [
      {"name": "engineering", "start": 9, "cost_per_head": 16500, "additions": {"6": 2, "15": 2}},
      {"name": "sales", "start": 4, "cost_per_head": 14500, "additions": {"4": 1, "10": 2}, "variable_pct_revenue": 0.05},
      {"name": "marketing", "start": 2, "cost_per_head": 12000, "additions": {"3": 1}, "non_headcount_pct_revenue": 0.08},
      {"name": "cs", "start": 3, "cost_per_head": 9500},
      {"name": "ga", "start": 2, "cost_per_head": 11000, "non_headcount_monthly": 9000}
    ]
  },
  "capex": {"pct_revenue": 0.02, "useful_life_months": 36},
  "working_capital": {"dso_days": 38, "dpo_days": 25, "deferred_revenue_pct": 0.14},
  "cash": {"starting_cash": 3400000, "debt": 0, "interest_rate_annual": 0.0, "tax_rate": 0.21},
  "scenario": "base"
}
```

The script validates types and ranges, never invents a value for a missing driver, and exits non-zero with a message naming the offending field. Feed its `flags` array into the narrative — do not re-derive runway or burn by hand.

## Data Quality Checklist

Run this before anyone sees the model:

- [ ] Every input carries a **source, a date, and an owner**. "Management estimate" is a source; blank is not.
- [ ] No hardcoded numbers inside formulas — every value lives on an assumptions tab and is referenced.
- [ ] Units are labelled everywhere: monthly vs annual, thousands vs units, $ vs %.
- [ ] Currency is single and stated; FX assumptions (if any) are on the assumptions page.
- [ ] Balance sheet balances every period, to zero, not "close enough."
- [ ] Ending cash on the cash flow equals cash on the balance sheet.
- [ ] ARR ties to the MRR roll-forward; headcount ties to payroll; revenue ties to billings plus deferred movement.
- [ ] The revenue build ties to the sales capacity plan (reps × productivity ≥ revenue), or the gap is explained.
- [ ] History and forecast are visually separated; the model does not silently overwrite actuals.
- [ ] No circular references except an intentional, documented interest-on-average-debt loop with iterative calculation on.
- [ ] Rounding is consistent — display to the unit, never round inputs.
- [ ] The model opens, calculates, and recalculates in under 5 seconds (a slow model is a stale model).
- [ ] Every scenario is reachable by flipping one switch.
- [ ] Version, author, and change date on the cover.

## Anti-Patterns

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| Top-down TAM × share as the revenue forecast | The share number is the answer restated as an input; it contains no evidence | Bottoms-up build; use TAM only as a ceiling check |
| Flat growth rate to the horizon | Compounds into absurdity (15%/mo ≈ 435%/yr) and reads as naive | Glide to a terminal rate; tie early growth to capacity |
| Single blended churn rate on a growing base | Overstates long-run revenue; hides cohort decay | Cohort triangle or time-decayed churn curve |
| Balance sheet with a "plug" row | Hides a real error and guarantees a restatement | Derive cash from the cash flow; fix the residual |
| Revenue recognized when billed | Overstates revenue and understates deferred liability | Accrual recognition; track deferred revenue separately |
| Headcount cost = base salary | Misses 25–35% burden and start-date lag; the largest cost line is wrong | Fully loaded cost × (1 + burden), hire month + 45–90 day lag |
| Hiring plan not tied to revenue capacity | The plan says 12 reps but revenue requires 20 | Derive required reps from revenue ÷ per-rep productivity |
| Opex as a flat % of revenue | Hides step functions (a new office, a SOC 2 audit, a CFO) | Headcount-led opex plus discrete event lines |
| LTV without gross margin | Overstates unit value by the margin gap | Margin-based LTV always |
| CAC excluding salaries and programs | Flatters CAC 2–3× and the LTV/CAC with it | Fully loaded CAC; state the variant |
| Terminal value = 80%+ of DCF value, unremarked | The valuation is one assumption wearing a spreadsheet | Say so, cross-check Gordon vs exit multiple, show the grid |
| Exit multiple pulled from a hotter market | Implies a growth/margin profile the model does not have | Source comparables as of the model date; test the implied profile |
| Option pool top-up omitted | Understates founder dilution by 3–5 points | Model pool shuffle explicitly before the round |
| Three copies of the model for three scenarios | They diverge on the first edit; nobody knows which is live | One model, one scenario switch, one driver table |
| Hardcoded actuals mixed into forecast formulas | The model silently double-counts or drops a month on refresh | Separate actuals tab, formula-driven forecast only |
| Runway quoted on the current burn | Ignores planned hiring — the actual plan | Planned net burn including the hires the round funds |
| Sensitivity as a paragraph of adjectives | Unfalsifiable and unranked | Tornado ranked by swing, plus breakeven values |

## Presenting to Investors

Order matters more than polish.

1. **The claim first.** One sentence: what the business becomes and what it needs. "We reach $40M ARR in 2029 at 78% gross margin and positive EBITDA in Q3 2028, on a $12M round."
2. **The driver page, not the output page.** Show MRR build, rep productivity, retention curve, gross margin path. Investors trust what they can reconstruct.
3. **The assumptions page with sources.** Every driver, its value, its basis, its range. Putting this forward is a credibility move; burying it is the opposite.
4. **The scenario page** with best/base/worst and the trigger for each. Include the worst case honestly — an investor who finds an unshown downside stops believing the rest.
5. **The sensitivity/tornado.** Show which three drivers decide the outcome and what you would do if they break.
6. **The cash page.** Runway, burn multiple, the month the raise is consumed, and the milestone it buys.
7. **The asks and uses.** Where the money goes, by category and by quarter, tied to the hiring plan in the model.

What not to do: 60 tabs, colour-coded everything, a summary that does not tie to the detail, hockey sticks with no driver, or a model that cannot answer "what if churn is 2% instead of 1.4%" inside 60 seconds. Bring the live model to the meeting and change an assumption in front of them — that is the demonstration that the model is real.

## Verification Checklist

- [ ] The model answers the specific decision it was built for; horizon and granularity match
- [ ] Revenue is bottoms-up, per channel, with ramp and seasonality, and ties to sales capacity
- [ ] COGS separated into variable, headcount-driven, and transaction fees; margin path justified
- [ ] OPEX is headcount-led with fully loaded cost, burden, and hire lag
- [ ] Three statements wired per the link table; cash from cash flow; balance residual zero every period
- [ ] Opening working-capital balances set or the fresh-start assumption stated
- [ ] Scenarios are one switch over named driver sets; worst case survivable with management action
- [ ] Sensitivity ranked by swing, with breakevens, and correlated drivers moved together
- [ ] Unit economics on gross-margin dollars, cohort-level, with payback stated
- [ ] If DCF: FCF on EBIT, terminal value cross-checked, WACC range shown, TV share of value disclosed
- [ ] If fundraising: pre/post stated, pool top-up modelled, SAFEs converted individually, waterfall shown
- [ ] All twelve metrics emitted and internally consistent
- [ ] Data quality checklist passed; every input has a source, date, and owner
- [ ] The three numbers that decide the outcome are named, with their breakevens
