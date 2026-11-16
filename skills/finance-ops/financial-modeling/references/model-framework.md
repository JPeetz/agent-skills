# Model Framework — Choosing and Building the Right Model

A financial model is an argument in numbers. The *type* of model determines what the argument can and cannot prove. Pick the wrong type and the model is not "roughly right" — it is answering a different question. This reference maps model types to decisions and company stages, and gives the build sequence for each.

## 1. The Four Model Types

| Type | Question it answers | Granularity | Fails when |
|---|---|---|---|
| **Three-statement** | "Do we run out of cash, and when?" | monthly, 12–60 months | drivers are hardcoded; balance sheet is plugged |
| **Bottoms-up operating (P&L only)** | "What does the plan produce, and what does it cost?" | monthly, 12–36 months | used for a liquidity decision (no balance sheet → no cash truth) |
| **Top-down market** | "Is the opportunity big enough to be worth the plan?" | annual, 3–5 years | used as the *forecast* rather than as a ceiling check |
| **Cohort / vintage** | "Does each cohort of customers pay back, and how fast does it decay?" | monthly cohorts, 24–60 months | aggregate-only data is fed in; cohorts are too young to read |

Most production models are a **bottoms-up engine inside a three-statement shell, with a cohort module for retention and a top-down module only as a sanity ceiling.** Say which module a given tab is; do not let a top-down number leak into a bottoms-up cell.

### 1.1 Three-statement model

The full accounting system: P&L, balance sheet, cash flow, wired together. This is the only model type that can answer liquidity questions, because it is the only one where cash is a calculated output rather than an assumption.

**Use it when:** raising debt or equity, testing covenant compliance, planning a hiring ramp that could exhaust cash, preparing a board pack that must reconcile to the actuals, or whenever someone will ask "how much cash is left in month 14?"

**Do not use it when:** you need a quick price/volume sensitivity — a P&L-only model gets there in a tenth of the time.

**Build sequence:**

1. **Assumptions tab.** One row per driver: value, unit, source, owner, range. Nothing else in the model may contain a number that is not referenced from here (or from the actuals tab).
2. **Actuals tab.** Last 12–24 months of the real P&L and balance sheet, untouched. History and forecast are visually separated; the forecast formulas must not overwrite actuals.
3. **Revenue build.** Channel by channel, bottoms-up, with ramp and seasonality. See §3.
4. **COGS.** Variable (hosting, payment fees), headcount-driven (support, services), and fixed. Never a single "% of revenue."
5. **Headcount plan.** Department, start count, additions by month, fully loaded monthly cost. Hiring is the largest controllable cost line for most companies under $50M revenue — model it explicitly or the OPEX is fiction.
6. **OPEX.** Department totals = headcount × cost + non-headcount. Non-headcount is either % of revenue or a discrete line (office, audit, insurance).
7. **Capex and depreciation.** Capex by month; depreciation straight-line per vintage over the useful life. Per-vintage matters: a single rate on closing PP&E will not tie while capex ramps.
8. **Working capital.** DSO on revenue → AR; DPO on COGS → AP; deferred revenue as a % of revenue (or derived from billing terms); prepaid as a % of OPEX. Set opening balances from the last close.
9. **Debt and interest.** Draw/repay schedule; interest on the opening balance (iterative calculation only if interest-on-average is genuinely needed — and then document the circularity).
10. **Tax with NOL carry-forward.** A loss-making year produces a deferred tax asset, not negative cash tax. Getting this wrong overstates cash by the tax rate × the loss.
11. **Cash flow, indirect method.** Start at net income, add back D&A, adjust for working capital, subtract capex, add financing. Ending cash flows *to* the balance sheet.
12. **Balance sheet, derived.** Cash from the cash flow; retained earnings = prior + net income; PP&E = prior + capex − depreciation. Check: assets − (liabilities + equity) = 0, every month.
13. **Checks tab.** Balance residual, cash tie, ARR tie, headcount tie to payroll, revenue tie to billings + deferred movement.
14. **Scenarios.** One switch, one driver table. Not three copies.

### 1.2 Bottoms-up operating model

Revenue and cost built from operational units: reps × productivity, traffic × conversion, accounts × ARPU, engineers × cost, tickets × cost per ticket. Output is a P&L plus a lightweight cash view (EBITDA − capex − ΔNWC).

**Use it when:** the question is about the *plan* rather than the *balance sheet* — pricing changes, GTM capacity, gross margin trajectory, hiring affordability over 12–24 months, sales-comp design.

**Do not use it when:** the answer must survive an accountant, a lender, or a diligence process.

**Build sequence:** driver tree → revenue by channel → COGS by component → headcount → OPEX → EBITDA → a one-line cash bridge (EBITDA − capex − ΔNWC) → sensitivity. The discipline is identical to the three-statement; only the linking is skipped. Keep the driver tree identical to the three-statement version so the two can be reconciled.

### 1.3 Top-down market model

TAM → SAM → SOM, with share assumptions. Market size from a credible source (bottom-up TAM from customer counts × ACV is far more defensible than an analyst's "$40B market"), then a share ramp.

**Use it when:** sizing an opportunity for a pitch, choosing between markets, or sanity-checking a bottoms-up plan that implies an implausible share.

**Do not use it when:** producing a revenue forecast you will be held to. `TAM × 2% share` is the answer written as an input. The failure mode is diagnostic: if your bottoms-up plan implies 35% of SAM in year three, either the SAM is wrong or the plan is.

**Build sequence:** define the customer unit precisely (a "developer" and a "seatable enterprise employee" are different markets) → count addressable units from the bottom (company registries, developer surveys, seat counts) → apply a realistic ACV per unit → apply a share ramp justified by win rates and sales capacity → reconcile against the bottoms-up plan and explain any gap above 2×.

### 1.4 Cohort / vintage model

Customers grouped by acquisition month, with each cohort's revenue tracked forward: retention curve, expansion, contraction, and payback per cohort.

**Use it when:** retention is the crux (SaaS, subscriptions, marketplaces), when aggregate NRR is masking a deteriorating recent cohort, or when you need to prove CAC payback rather than assert it.

**Do not use it when:** cohorts are younger than 6–12 months — the right tail is unobserved and any fit is an extrapolation.

**Build sequence:** build the cohort triangle (rows = acquisition month, columns = months since acquisition, cells = retained revenue or logos) → fit a decay curve (power law `retention = a × t^(−b)` fits SaaS better than exponential; exponential is acceptable for short horizons if stated) → apply the fitted curve to the forecast, letting recent cohorts carry their own (usually worse) curve → derive aggregate NRR as an *output*, never an input → compute payback per cohort on gross-margin dollars.

## 2. Fit by Company Stage

| Stage | Primary model | Secondary | Horizon | Fatal mistake to avoid |
|---|---|---|---|---|
| **Pre-seed / idea** | Bottoms-up unit economics | Top-down TAM for framing | 18–24 months | Building a 60-tab model on zero data; the model is a hypothesis, keep it one page |
| **Seed** | Bottoms-up P&L + cash bridge | Cohort (if 6+ months of data) | 24 months | Ignoring CAC payback; growth that consumes cash is the whole risk |
| **Series A** | Three-statement | Cohort, scenario | 24–36 months | No capacity tie between revenue and reps; the plan is unfunded by month 15 |
| **Series B** | Three-statement + cohort | Segment P&L | 36 months | Segment P&L missing — blended numbers hide a broken motion |
| **Growth / late** | Three-statement, quarterly | Driver-based by product line, debt/covenant module | 36–60 months | Working capital and deferred revenue treated as noise; at $50M+ they move cash by millions |
| **Profitable / PE-owned** | Three-statement + covenant + DCF | Working-capital cycle model | 36–60 months, quarterly | Cash conversion assumed, not modelled; DSO drift breaks the covenant before the P&L shows anything |
| **Pre-IPO** | Three-statement, quarterly, auditable | Cohort, segment, sensitivity | 8 quarters | Model that cannot be re-derived by an auditor: hardcodes, circular refs, undocumented drivers |

The pattern: **the earlier the stage, the more the model is about unit economics and the less about accounting; the later the stage, the more it is about cash conversion and control.** A seed company needs a one-page driver model with a payback calculation. A $200M company needs a model that a lender's analyst can rebuild from the assumptions page.

## 3. The Revenue Build, in Detail

Revenue is where models are most often wrong and most often dishonest. The build below applies to all four model types.

**Step 1 — decompose to units.** Every revenue line must reduce to `units × price per unit per period`. Units are logos, seats, transactions, GB stored, API calls, or stores. Price is ACV, ARPA, take rate, or per-unit fee. If a line cannot be decomposed, it is a target, not a forecast.

**Step 2 — separate new from existing.** `revenue_t = existing_base_t + new_business_t`. Existing base rolls forward with expansion, contraction, churn. New business comes from a capacity model.

**Step 3 — build the capacity model.** For sales-led: `reps × ramped productivity × attainment`. Productivity is deals per rep per month × ACV, and it ramps (0 → 100% over 3–6 months). Then check the arithmetic: if the revenue target needs 20 reps and the hiring plan funds 12, the model is inconsistent and an investor will find it in ten minutes.

**Step 4 — apply seasonality.** Monthly multipliers by calendar month, sourced from the prior year or from the segment's known pattern. Q4-heavy enterprise, summer-light Europe, January-heavy self-serve.

**Step 5 — cap and glide.** Set a terminal growth rate (typically 2–5× market growth, decaying to market growth by year 5–7) and glide toward it. A constant 8%/month new-business growth implies 152% annual growth of the *add* line, which compounds into nonsense by year four.

**Step 6 — reconcile to a ceiling.** Compare the implied market share against the top-down SAM. Above ~10–15% share within five years, the plan needs a stated reason (new market, category creation, geographic expansion) — not a shrug.

## 4. Choosing Between Scenarios, Sensitivity, and Stress Tests

They are different tools and are often conflated:

- **Scenario** = a coherent, internally consistent alternative world (base/best/worst), with correlated drivers moving together. Answers "what happens if the market turns."
- **Sensitivity** = one driver at a time, holding others fixed. Answers "which assumption matters most." Its output is a ranking, not a range.
- **Stress test** = an extreme, single-factor shock applied to a surviving plan. Answers "at what point does this break, and what do we do." Used for covenants and liquidity.

A serious model ships all three: scenarios for the plan, sensitivity for the ranking, stress for the covenant or runway floor.

## 5. Model Architecture Rules

These apply regardless of type and are what separate a model that survives diligence from one that does not.

1. **One number, one home.** Every input lives once, on the assumptions tab, and is referenced everywhere else. Duplicated inputs drift.
2. **Colour convention.** Blue = hardcoded input, black = formula, green = link to another sheet. Anyone opening the model can then see what is assumed versus what is computed.
3. **Time flows left to right, one column per period, never one sheet per month.** Row-consistent, column-periodic is the only layout that can be audited or extended.
4. **Uniform rows.** Every block has the same rows in the same order on every tab; every statement has total, growth, and margin rows directly beneath it.
5. **No circular references** except a documented interest-on-average-debt loop with iterative calc on, and a note saying so.
6. **History is locked.** Forecast formulas must not overwrite actuals; a model that silently rewrites history cannot be reconciled to the ledger.
7. **Checks are visible on the cover.** Balance residual, cash tie, and a traffic-light summary. A model without checks is a model nobody has verified.
8. **One scenario switch, one driver table.** Duplicated scenarios diverge on the first edit, and nobody knows which is live.
9. **Every output has a "so what."** A tab that produces numbers nobody acts on is a tab that will not be maintained.
10. **Version, date, and author on the cover.** Models circulate; an unversioned model is an unowned model.

## 6. Common Structural Errors by Type

| Type | Error | Symptom | Fix |
|---|---|---|---|
| Three-statement | Balance sheet plugged with a "balancing" row | Residual hidden, not zero | Derive cash from CF; find the real break |
| Three-statement | Depreciation on closing PP&E | Balance drifts while capex ramps | Per-vintage straight line |
| Three-statement | No opening working capital | Large artificial cash inflow in month 1 | Set opening AR/AP/deferred from the last close |
| Three-statement | Tax benefit on losses | Cash overstated | NOL carry-forward, DTA on the balance sheet |
| Bottoms-up | OPEX as % of revenue | Hides hiring step functions | Headcount-led OPEX + discrete events |
| Bottoms-up | Reps without ramp | Revenue front-loaded and unfunded | Ramp curve applied to hire cohorts |
| Top-down | Share assumption as the forecast | Unfalsifiable | Share as ceiling only |
| Cohort | Aggregate churn applied to a growing base | Overstates long-run revenue | Fit the curve, roll each cohort |
| Cohort | Cohorts younger than the fit window | Extrapolation dressed as data | Cap the horizon, state the extrapolation |
| Any | Scenario copies instead of a switch | Divergence on first edit | One model, driver table, switch |
| Any | Hardcodes inside formulas | Untraceable, unchangeable, wrong on refresh | Assumptions tab, single source |
| Any | Rounding inputs to look clean | Silent 1–3% bias, compounds | Round display, never inputs |
