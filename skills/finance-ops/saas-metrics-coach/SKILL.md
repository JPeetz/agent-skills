---
name: saas-metrics-coach
description: >-
  Use this skill when analyzing SaaS business metrics, building financial
  models, or preparing investor metrics. Activates on "SaaS metrics", "ARR",
  "MRR", "churn", "LTV", "CAC", "unit economics", "recurring revenue",
  "financial model", "runway", "burn rate", "net revenue retention", "NRR",
  "quick ratio", or "investor metrics". Covers revenue metrics (ARR/MRR/NRR),
  churn and retention, LTV/CAC ratio, unit economics, cash flow and runway,
  cohort analysis, benchmark comparisons, and board/investor metric packs.
version: 1.0.0
author: Skill Foundry
license: MIT
category: finance-ops
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - finance
  - saas
  - metrics
  - revenue
  - churn
  - LTV
  - CAC
  - MRR
  - ARR
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
    - saas-metrics
    - revenue
    - churn
    - LTV-CAC
    - unit-economics
    - benchmarking
  related_skills:
    - pricing-strategist
    - go-to-market-launch
    - unit-economics-and-financial-model
---

# SaaS Metrics Coach

Turn a pile of subscription data into a defensible, consistent metric set — and say what the numbers mean, not just what they are.

Every metric here has one agreed definition, one formula, and one stated input. Ambiguity is the failure mode: two teams that "report 110% NRR" are usually computing three different things.

## Overview

The skill is organized as a metrics stack. Each layer depends on the one below it, so compute upward and never quote a higher-layer number built on a broken lower layer.

| Layer | Metrics | Depends on |
|-------|---------|-----------|
| 0 — Instrumentation | contract start/end, MRR per account, expansion/contraction events, S&M spend, cash balance | billing + CRM + GL |
| 1 — Revenue base | MRR, ARR, ARPA, new/expansion/contraction/churn MRR | Layer 0 |
| 2 — Retention | gross revenue churn, logo churn, GRR, NRR, quick ratio | Layer 1 |
| 3 — Unit economics | CAC, LTV, LTV/CAC, CAC payback, gross margin, contribution margin | Layers 1–2 + S&M spend |
| 4 — Efficiency & cash | burn multiple, magic number, Rule of 40, runway | Layers 1–4 + cash |
| 5 — Narrative | cohort tables, benchmark position, board pack | Layers 1–4 |

Deliverables are always a **table plus a read**: the number, the definition used, the trend, the benchmark band, and the decision it implies.

## When to Use

- Building or auditing a monthly/quarterly SaaS metric pack
- Preparing a board deck, investor update, or fundraise data room
- Answering "is our growth efficient?" / "how long is our runway?"
- Diagnosing a metric that moved and nobody can explain why
- Sanity-checking a metrics spreadsheet before it reaches an investor
- Setting targets: what NRR, CAC payback, or burn multiple should be next quarter
- Cohort work: is retention improving for newer cohorts or only in aggregate?

### Do Not Use For

| Need | Use instead |
|------|-------------|
| Choosing a price or packaging model | `pricing-strategist` |
| GTM launch plan and channel mix | `go-to-market-launch` |
| Full three-statement model / cap table / valuation | finance team + `unit-economics-and-financial-model` |
| Bookkeeping, revenue recognition policy, audit | controller / CPA — this skill consumes recognized revenue, it does not set policy |
| Fundraising narrative and deck design | founder + investor-relations workflow |

## Non-Negotiable Definitions

State these in the output. Half of all metric disputes are definition disputes.

- **MRR** — the normalised monthly value of active recurring subscriptions at a point in time. Annual contracts divided by 12; quarterly by 3. Usage revenue counts only if it is recurring and predictable (use trailing 3-month average, not the peak month).
- **ARR** — `MRR × 12`. ARR is a *snapshot annualisation*, never a sum of bookings and never "revenue we hope to get".
- **Excluded from MRR/ARR**: one-off implementation and onboarding fees, professional services, hardware, pass-through taxes, refunds/credits, trial users not yet converted, contractually committed but not-started revenue.
- **Customers vs accounts vs seats** — pick one unit and hold it for the whole pack. Enterprise accounts with sub-accounts are one logo, many accounts; say which you are counting.
- **Period** — state start date, end date, and whether values are point-in-time (MRR, ARR, customers) or period flows (churn, S&M spend, cash burn). Mixing the two is the most common reporting bug.

## Revenue Metrics

### ARR / MRR construction

Build MRR from the contract table, then reconcile:

```
MRR_end = MRR_begin
        + new business MRR
        + expansion MRR (upsell, cross-sell, seat growth, usage overage)
        + reactivation MRR (churned logo returning)
        - contraction MRR (downgrade, seat loss, usage drop)
        - churned MRR (full cancellation / non-renewal)
```

The bridge must close to the observed ending MRR. A gap larger than rounding means a categorization error, a mid-month start, or a discount/credit that was never booked. Report the residual explicitly rather than plugging it.

Rules that keep the series clean:

1. **Normalise before you add.** Convert every contract to its monthly equivalent at the same date basis (month-end). Do not mix month-start and month-end snapshots in one series.
2. **Mid-month starts** — either prorate the first month or start recognition the following month. Document the choice; do not switch mid-series.
3. **Annual prepay** is not MRR uplift. Cash collected ≠ MRR. Show deferred revenue separately.
4. **Price increases** on existing customers are expansion MRR, not new business.
5. **Currency** — report in one currency, at a stated FX rate, and keep the FX assumption in the pack.
6. **Annualised ≠ ARR.** `last month revenue × 12` overstates ARR if that month contained a one-off. Use `MRR × 12` from the normalised base.

### Revenue growth

- **MoM growth** = `(MRR_end − MRR_begin) / MRR_begin`
- **YoY growth** = `(MRR_this_month − MRR_same_month_last_year) / MRR_same_month_last_year`
- **CMGR** (compound monthly growth rate) over n months = `(MRR_end / MRR_begin)^(1/n) − 1`
- **Annualised run-rate growth** = `(ARR_end − ARR_begin) / ARR_begin` — usable only when the period is a year.

Report growth on a **trailing 3-month average** when a single month is noisy; say that you did.

### Churn and retention

Define each of these once and never let them drift:

| Metric | Formula | Reads as |
|--------|---------|----------|
| Gross revenue churn rate | `(contraction MRR + churned MRR) / MRR_begin` | how much of the base leaks, ignoring gains |
| Logo churn rate | `customers_churned / customers_begin` | how many accounts leave |
| Gross Revenue Retention (GRR) | `(MRR_begin − contraction − churn) / MRR_begin` | ceiling on retention with zero expansion; **always ≤ 100%** |
| Net Revenue Retention (NRR) | `(MRR_begin + expansion + reactivation − contraction − churn) / MRR_begin` | base growth from existing customers alone |
| Net dollar retention (NDR) | same as NRR; use one name in the pack | — |
| Quick ratio | `(new MRR + expansion MRR) / (churned MRR + contraction MRR)` | growth efficiency of the revenue engine |

Two rules people get wrong constantly:

- **NRR excludes new business.** If new logos are in the numerator it is a growth rate, not retention.
- **Whether reactivation counts in NRR is a policy choice.** Standard (and this skill's default) is to exclude reactivation from NRR and report it in the bridge; if you include it, label it "NRR incl. reactivation". Never compare the two variants against the same benchmark.

**Logo churn vs revenue churn diverge** when you lose many small accounts (high logo churn, low revenue churn) or one large one (the reverse). Report both, and report the customer-size mix alongside.

**Annualised churn trap:** don't multiply a monthly churn rate by 12. `1 − (1 − m)^12` is the correct annualisation, and at 3%/month the difference is 36% vs 30.6%.

## LTV / CAC Framework

### CAC

| Variant | Formula | Use for |
|---------|---------|---------|
| Blended CAC | `total S&M spend / new customers` | company-level efficiency, board reporting |
| Paid CAC | `paid acquisition spend / new customers from paid` | channel-level decisions |
| Fully-loaded CAC | `(S&M comp + programs + tools + allocated overhead) / new customers` | true payback and pricing decisions |
| New-business CAC | excludes expansion-attributable S&M | separating land from expand |

Rules:

- **Match the numerator to the denominator's period.** S&M spend in month M acquires customers who may only close in M+1 or M+2. For fast cycles use same-month; for enterprise (>60 day cycles) use a **lagged CAC** — spend shifted forward by the observed sales cycle — and say so.
- **Include the people.** S&M salaries, commissions, marketing programs, tools, agencies, and event costs. Excluding headcount is the single most common way CAC gets flattered by 2–3×.
- **Never divide by gross new logos when trials/self-serve are mixed** with sales-led. Split the segments, compute CAC per segment, then blend.
- **Expansion spend** is not acquisition spend; if you cannot separate it, say the CAC is blended and overstated.

### LTV

```
ARPA (monthly)      = MRR / paying customers
Gross margin %      = (revenue − COGS) / revenue     # COGS = hosting, support, third-party fees
Monthly churn       = gross revenue churn rate (decimal)
Average lifetime    = 1 / monthly churn             # simple; months
LTV (margin-based)  = ARPA × gross margin % × average lifetime
```

Choice of churn in the denominator matters enormously: using **logo churn** gives a customer-value estimate, using **revenue churn** gives a revenue-weighted one. For LTV/CAC against a revenue-based CAC, use **revenue churn** consistently. Document it.

Alternative when retention is stable: `LTV = ARPA × gross margin % × assumed_lifetime_months`. Use 36–60 months for SMB, longer for enterprise — but justify it, don't default silently.

### LTV/CAC ratio

```
LTV/CAC = LTV / CAC
```

| LTV/CAC | Read |
|---------|------|
| < 1.0 | Losing money on every customer. Stop scaling spend. |
| 1.0 – 2.0 | Under-monetised or over-spending. Fix pricing, retention or channel mix before scaling. |
| 3.0 | The conventional healthy target — a *floor* for efficient SMB SaaS, not a universal goal. |
| 3.0 – 5.0 | Healthy. Scale what works. |
| > 5.0 | Usually under-investing in growth, or LTV is inflated by an optimistic lifetime assumption. Verify the inputs before celebrating. |

LTV/CAC is a **ratio of assumptions**. Always ship it with the churn rate and gross margin used, and a sensitivity line (`if churn rises 25%, ratio falls to X`).

### CAC payback period

```
CAC payback (months) = CAC / (ARPA × gross margin %)
```

This is the cash-relevant sibling of LTV/CAC and the better operating metric for a capital-constrained company.

| Segment | Good | Acceptable | Concerning |
|---------|------|-----------|------------|
| SMB / self-serve | < 6 months | 6–12 | > 12 |
| Mid-market | < 12 months | 12–18 | > 18 |
| Enterprise | < 18 months | 18–24 | > 24 |

Payback uses **gross-margin dollars**, not revenue dollars. A 12-month payback on 80% margin is 15 months on a revenue basis.

## Unit Economics

The per-customer P&L is the honest test of whether the business works before scale.

```
Per customer, per month
  Revenue (ARPA)                    100.00
  − COGS (hosting, support, 3rd party)  −20.00
  = Gross profit                      80.00   (80% gross margin)
  − Direct service costs (CSM, onboarding)  −10.00
  = Contribution margin               70.00
  − Allocated S&M (CAC amortised over payback)  −12.00
  − Allocated R&D / G&A (at scale)     −20.00
  = Operating profit per customer     38.00
```

- **Gross margin** = `(revenue − COGS) / revenue`. COGS is *cost to serve*, not "everything except sales". For SaaS, hosting + support + third-party API/data costs. Target 70–85%; infrastructure-heavy or AI-inference products legitimately run 50–70% — say so rather than hiding it.
- **Contribution margin** = gross profit − variable customer-facing costs (CSMs, onboarding, payment fees). Target > 60% for SaaS at scale.
- **Segment the unit economics.** SMB, mid-market and enterprise usually have different ARPA, gross margin, churn and CAC. A blended number hides the fact that one segment funds the others. Show a table per segment.
- **Marginal vs average.** Average CAC includes legacy inefficiency. For "should we spend the next $100k?", use marginal CAC and marginal payback.

### Magic number

```
Magic number = (ΔARR over the period × 4 for a quarter) / S&M spend in the prior period
            ≈ net new ARR annualised / S&M spend
```

| Magic number | Read |
|--------------|------|
| > 1.5 | Under-investing in sales & marketing; pour it on |
| 0.75 – 1.5 | Efficient; scale steadily |
| 0.5 – 0.75 | Fix conversion or pricing before adding spend |
| < 0.5 | Spend is not converting; stop and diagnose |

## Cash Flow

### Burn rate

- **Gross burn** = total monthly cash out.
- **Net burn** = `cash out − cash in` (the number that matters for runway).
- Use a **trailing 3-month average** for planning; a single month is noise. Report both the month and the 3-month average when they diverge sharply.

### Runway

```
Runway (months) = current cash / trailing-3-month average net burn
```

Rules:

- Include **committed** outflows (annual contract renewals, hiring plan, debt service). A runway number that ignores signed obligations is fiction.
- Exclude restricted cash and undrawn facilities unless you state them separately as "runway including undrawn revolver".
- State the assumed **growth in burn**. Flat-burn runway is a lower bound for a company that is hiring.
- Below 12 months is a fundraising trigger, not a planning detail. Below 6 months is triage.

### Burn multiple

```
Burn multiple = net burn / net new ARR
```

The single best one-number efficiency test: how many dollars of cash you burned per dollar of new ARR.

| Burn multiple | Read |
|---------------|------|
| < 1.0 | Exceptional (rare, usually capital-efficient PLG) |
| 1.0 – 1.5 | Excellent |
| 1.5 – 2.0 | Good |
| 2.0 – 3.0 | Acceptable but needs a reason |
| > 3.0 | Inefficient; growth is being bought |

Compute over a quarter or a year, never a single month (net new ARR is lumpy).

### Rule of 40

```
Rule of 40 = revenue growth % (YoY) + profit margin % (FCF margin, or EBITDA margin if stated)
```

Above 40 is healthy; the mix matters more than the sum. A 60% growth / −25% margin company is in a different risk class from 15% growth / 30% margin — describe which one you are.

## Cohort Analysis

Aggregate churn hides cohort drift: a company can show flat 3% monthly churn while every recent cohort is at 5% and older, stickier cohorts mask it.

Build the **retention triangle**:

```
Cohort      M0     M1     M2     M3     M4     M5
2026-01   100%    92%    88%    85%    83%    82%
2026-02   100%    90%    85%    82%    80%      —
2026-03   100%    88%    82%    78%      —      —
2026-04   100%    86%    79%      —      —      —
```

Read it three ways:

1. **Down the diagonal** — is each newer cohort retaining worse at the same age? If yes, you have a product, onboarding or ICP problem, not a churn-number problem.
2. **Across a row** — flattening curve = a stable retained core. A curve still falling at M6 means you have not found product-market fit for that segment.
3. **By revenue, not just logos** — a revenue-weighted triangle shows whether the accounts staying are the valuable ones.

Also compute **cohort NRR** (revenue at month N / revenue at M0 for the same cohort) and **payback by cohort** (months until cumulative gross profit covers CAC). Newer cohorts paying back slower is an early warning that shows up in LTV/CAC a year later.

Cohort rules: fixed cohort definition (signup month, or first-paid month — pick one), at least 6 months of history before drawing conclusions, and never compare cohorts of different segment mixes without segmenting.

## Benchmark Tables

Bands below are directional medians for venture-backed B2B SaaS; treat them as a starting reference, not a verdict. Sources and caveats in `references/sources.md`.

### Growth (ARR, YoY)

| ARR band | Median | Top quartile |
|----------|--------|--------------|
| < $1M | 100%+ | 200%+ |
| $1M – $3M | 70–80% | 120%+ |
| $3M – $10M | 50–60% | 90%+ |
| $10M – $25M | 40–50% | 70%+ |
| $25M – $50M | 30–40% | 55%+ |
| $50M+ | 20–25% | 40%+ |

### Retention

| Segment | GRR good | NRR good | NRR excellent |
|---------|----------|----------|---------------|
| SMB | 80–85% | 90–100% | 105%+ |
| Mid-market | 85–90% | 100–110% | 115%+ |
| Enterprise | 90–95% | 110–120% | 130%+ |

Monthly gross revenue churn: SMB 3–5%, mid-market 1.5–2.5%, enterprise < 1%.

### Efficiency

| Metric | Good | Great | Notes |
|--------|------|-------|-------|
| LTV/CAC | 3.0 | 4.0–5.0 | > 5 usually means under-investment |
| CAC payback | ≤ 12 mo (SMB), ≤ 18 (MM), ≤ 24 (ENT) | 6–9 mo | gross-margin basis |
| Burn multiple | ≤ 2.0 | ≤ 1.0 | quarterly/annual |
| Quick ratio | ≥ 2.0 | ≥ 4.0 | new+expansion ÷ churn+contraction |
| Magic number | ≥ 0.75 | ≥ 1.0 | prior-period S&M |
| Rule of 40 | ≥ 40 | ≥ 60 | growth% + margin% |
| Gross margin | 70–85% | 80%+ | AI/infra products lower, legitimately |

**Benchmark discipline:** compare only same-ARR-band, same-segment, same-ACV-motion companies. A $2M ARR self-serve product and a $2M ARR enterprise product share almost no healthy metric values. When you cite a band, name the population it came from.

## Running the Calculator

`scripts/metrics_calculator.py` takes a JSON input and emits the full computed set as JSON or a markdown pack. Stdlib only, no network.

```bash
python3 scripts/metrics_calculator.py --input metrics.json --output markdown
python3 scripts/metrics_calculator.py --input metrics.json --output json
```

Minimal input:

```json
{
  "company": "Acme",
  "currency": "USD",
  "period": {"start": "2026-01", "end": "2026-06"},
  "mrr": {"begin": 100000, "end": 128000},
  "movement": {"new": 30000, "expansion": 9000, "reactivation": 2000,
               "contraction": 4000, "churn": 9000},
  "customers": {"begin": 200, "end": 214, "new": 30, "churned": 16},
  "pnl": {"revenue": 660000, "cogs": 132000, "sales_marketing": 180000},
  "cash": {"balance": 4200000, "net_burn_monthly": 100000},
  "assumptions": {"segment": "mid-market"}
}
```

The script reports every derived metric, checks that the MRR bridge closes, and raises `flags` for the conditions that matter (NRR < 100, burn multiple > 2, runway < 12 months, LTV/CAC outside 3–5, payback > segment norm). Feed its `flags` straight into the narrative — do not re-derive numbers by hand for a board pack.

## Anti-Patterns and Pitfalls

| Anti-pattern | Why it is wrong | Do instead |
|--------------|-----------------|------------|
| ARR = last month's revenue × 12 | One-off revenue inflates it; annualised ≠ recurring | Normalised `MRR × 12` from the contract base |
| Calling bookings ARR | Cash/commit ≠ recognized recurring revenue | Keep bookings, billings, revenue and ARR as separate lines |
| NRR with new logos in the numerator | Becomes a growth rate and overstates retention | Exclude new; label any variant that includes reactivation |
| Monthly churn × 12 for annual churn | Compounds; overstates by 3–6 pts at typical rates | `1 − (1 − m)^12` |
| CAC without S&M headcount | Flatters CAC 2–3× | Fully-loaded CAC; state which variant |
| LTV without gross margin | Overstates by the margin gap; a 60%-margin business overstates LTV by 67% | Margin-based LTV always |
| LTV/CAC with no assumptions attached | The ratio is a function of churn and margin, not a fact | Ship churn, margin, lifetime and a sensitivity line |
| Runway on flat burn | Ignores hiring and renewals — the actual plan | Use planned burn; state assumptions |
| Aggregate churn only | Masks cohort decay and segment mix | Cohort triangle + segment table |
| Mixing point-in-time and flow metrics | Numerator/denominator mismatch produces nonsense | Label every metric PIT or period |
| Blended CAC for a channel decision | Hides which channel is broken | Paid/marginal CAC per channel |
| Benchmarking across ARR bands and motions | Comparisons are meaningless | Match band, segment, ACV |
| Switching definitions mid-series to look better | Destroys trend integrity and credibility | Version the definition; restate history if you must change |
| Rounding cash runway to a comfortable number | Removes the urgency the number exists to create | Report exact months and the sensitivity |

## Verification Checklist

Before delivering a metrics pack:

- [ ] Definitions stated: MRR rules, churn basis (logo vs revenue), NRR variant, CAC variant, LTV churn and lifetime assumption
- [ ] MRR bridge closes to observed MRR; residual reported if not
- [ ] Period and currency stated; PIT vs flow labelled per metric
- [ ] ARR = MRR × 12 from the normalised base (not revenue × 12)
- [ ] Churn annualised correctly, not multiplied by 12
- [ ] LTV computed on gross-margin dollars
- [ ] CAC fully loaded for the variant claimed
- [ ] Runway includes committed outflows and planned burn
- [ ] Cohort drift checked, not just aggregate churn
- [ ] Each benchmark comparison names its population
- [ ] Every metric carries a "so what": trend direction and the decision it implies
