# Sources, Formula Canon, and Benchmark Provenance

## How to use this file

Every number in `SKILL.md`'s benchmark tables is a **directional band**, not a surveyed constant. Bands are drawn from the public reports below, rounded to the nearest sensible increment, and then cross-checked against each other. When a pack cites a benchmark, it should name the population (ARR band, segment, ACV motion, survey year), because the reports disagree — sometimes by 10+ points — for exactly those reasons.

## Primary benchmark sources

| Source | What it is good for | Caveats |
|--------|--------------------|---------|
| **ChartMogul — SaaS Retention Reports** (annual) | NRR/GRR by segment, churn by pricing model, cohort retention curves | Skewed toward companies on ChartMogul billing; strong on retention mechanics, weaker on growth |
| **OpenView — SaaS Benchmarks Report** (through 2022) | Growth by ARR band, CAC payback, NRR by segment, magic number | Venture-backed, PLG-weighted sample; the series stopped after 2022, so treat later years as historical |
| **SaaS Capital — annual SaaS retention and spending surveys** | Retention by ACV, S&M/G&A/R&D spend as % of revenue, growth by ARR band | Survey self-report; mid-market and bootstrapped skew relative to OpenView |
| **KeyBanc Capital Markets — SaaS Survey (Private SaaS Company Survey)** | Growth, churn, gross margin, S&M efficiency by ACV band | Annual, private-company sample, enterprise-weighted |
| **Bessemer Venture Partners — State of the Cloud** | Cloud growth rates, Rule of 40 distribution, efficiency benchmarks for public + private | Narrative report; figures are medians of a broad population and shift year to year |
| **ICONIQ — State of Software** | Growth and efficiency by stage; burn multiple and NRR distributions | Late-stage and growth-stage weighted |
| **Benchmarkit — SaaS Performance Metrics** | Operating metrics by ARR band and segment; NRR, growth efficiency, CAC ratios | Smaller sample; useful as a cross-check on OpenView-era numbers |
| **Paddle — SaaS Benchmarks** | SMB and self-serve pricing, churn, conversion | SMB/self-serve heavy; not representative of enterprise ACV |
| **Battery Ventures — Cloud Software benchmarks** | Public cloud comps: growth, margin, Rule of 40 | Public-market data, not private SaaS |

Rule of thumb: use two sources, and if they disagree by more than 10 points, quote a range rather than a single median.

## Metric definitions and where they come from

| Metric | Canonical reference | Note |
|--------|--------------------|------|
| MRR/ARR, expansion vs new | Standard SaaS finance practice; see Bessemer and SaaS Capital glossaries | No single authority — the contract base is the ground truth, not a blog post |
| NRR / GRR | ChartMogul and SaaS Capital both publish explicit formulas | Variants differ on reactivation and on whether services revenue is included; always state which |
| Quick ratio (growth efficiency) | Mamoon Hamid (Social Capital), popularised 2015–2016 | `(new + expansion) / (churn + contraction)`; the 2.0 "good" line is convention, not survey output |
| LTV and LTV/CAC 3x | David Skok, *SaaS Metrics 2.0* (forentrepreneurs.com) | The 3x figure assumes a specific churn/margin regime; Skok himself frames it as a heuristic |
| CAC payback | SaaS Capital, OpenView, KeyBanc all report it | Segment norms (6/12/18 months) are convention derived from those samples |
| Magic number | Lars Leckie / Scale Venture Partners | Defined on **prior-period** S&M spend; comparing same-period spend understates it |
| Burn multiple | David Sacks, Craft Ventures — "The Burn Multiple" (2020) | Quarterly or annual only; monthly net new ARR is too lumpy |
| Rule of 40 | Widely attributed to Brad Feld and Fred Wilson; standard VC heuristic | Growth % + profit margin %; state whether margin is FCF, EBITDA or operating |
| Cohort retention triangle | Standard subscription analytics practice (ChartMogul, Amplitude, Mixpanel docs) | Revenue-weighted triangles are more decision-relevant than logo-weighted |

## Deliberate omissions

- **No single "correct" NRR.** Whether reactivation counts is a policy choice; this skill reports both and defaults to excluding it.
- **No universal gross-margin target.** AI inference and infrastructure-heavy products legitimately run 50–70%; the 70–85% band is a traditional-software figure.
- **No fixed LTV lifetime.** 36–60 months for SMB, longer for enterprise, but the assumption must be stated per pack. Deriving lifetime as `1 / monthly churn` is the defensible default because it is traceable to the observed churn rate.

## Handling internal data

Where a company has its own historical distribution (its own quartiles across cohorts, segments or vintages), prefer **internal benchmarks over external ones**. External bands exist to sanity-check, not to set targets — a target set from someone else's median is a target with no owner.

## Reading list

- David Skok, *SaaS Metrics 2.0 — A Guide to Measuring and Improving What Matters*
- ChartMogul, *SaaS Retention Report* (latest edition)
- OpenView Partners, *SaaS Benchmarks Report* (2021, 2022)
- SaaS Capital, *Retention Benchmarks* and *Spending Benchmarks* (latest editions)
- KeyBanc Capital Markets, *Private SaaS Company Survey* (latest edition)
- Bessemer Venture Partners, *State of the Cloud* (latest edition)
- ICONIQ Growth, *State of Software* (latest edition)
- Benchmarkit, *SaaS Performance Metrics* (latest edition)
- David Sacks, *The Burn Multiple* (Craft Ventures, 2020)
- Mamoon Hamid, *The SaaS Quick Ratio* (Social Capital)
