---
name: "pricing-strategist"
description: "Use this skill when choosing or revisiting SaaS pricing: seat, usage, value-based, freemium or hybrid models, Van Westendorp willingness-to-pay analysis, or Good/Better/Best tier packaging. Runs pricing_model_picker.py, wtp_analyzer.py and packaging_designer.py to return a recommended model, a price range and a tier design — never a single number."
version: "0.1.0"
author: "Alireza Rezvani (alirezarezvani), Skill Foundry"
license: "MIT"
platforms:
  - linux
  - macos
  - windows
metadata:
  hermes:
    tags:
      - pricing
      - packaging
      - saas-pricing
      - van-westendorp
      - willingness-to-pay
      - value-based-pricing
      - freemium
      - tiers
      - business-strategy
      - commercial
    related_skills:
      - "enterprise-consulting-methods"
      - "linear-project-management"
---

# Pricing Strategist

Structured answer to the pricing-design question: **which model, which range, which packaging.**

The skill recommends a model and a price *range*. A human picks the number, owns the trade-off, and runs the GTM.

## When to Use

- Launching a SaaS / API / AI product and choosing a first pricing model
- Revisiting pricing after 18+ months of GTM data (model shift, not just a price bump)
- Designing or redesigning tier packaging (Good/Better/Best, Bronze/Silver/Gold)
- You have Van Westendorp survey responses and want the acceptable price range
- An exec or board asks "what should we charge?" and you need the structured answer
- You suspect packaging anti-patterns: decoy tier, feature dump, no upgrade trigger

## Do Not Use For

| Need | Use instead |
|------|-------------|
| Per-deal discount approval | deal-desk workflow |
| Brand, category creation, CMO positioning | CMO advisory |
| Whole-company revenue strategy | CRO advisory |
| Technical-sale enablement / POC scoping | sales-engineer workflow |

## Workflow

### Step 1 — Assess customer context (~20 min)

Capture, in a JSON brief:

- industry and buyer (SMB / mid-market / enterprise)
- average deal size and current customer count
- value drivers — what the customer measurably gains
- consumption pattern: seat, usage, value, or hybrid
- adoption curve (viral / sales-led / bottom-up-then-top-down)
- competitor models and their published price points

Missing fields are not fatal — the picker degrades gracefully and marks lower confidence.

### Step 2 — Pick the pricing model

```bash
python3 scripts/pricing_model_picker.py --input brief.json --profile saas --output markdown
```

Ranks five models (seat, usage, value-based, freemium, hybrid) by fit score 0–100, each with a rationale and a trade-off. Read the top two, not just the top one — the runner-up is usually the answer for the next 24 months.

### Step 3 — Validate willingness to pay

```bash
python3 scripts/wtp_analyzer.py --input survey.json --output markdown
```

Van Westendorp Price Sensitivity Meter over four questions per respondent:

1. At what price would this be **so cheap you'd doubt the quality**? (`too_cheap`)
2. At what price is it **a bargain — clearly good value**? (`bargain`)
3. At what price does it start to feel **expensive but still worth considering**? (`expensive`)
4. At what price is it **too expensive — you would not buy**? (`too_expensive`)

Output: the four intersection points (OPP, IDP, PMC, PME) and the Range of Acceptable Prices (PMC → PME).

**Minimum N = 30.** Below that the curves are noise; the script warns and still runs so you can sanity-check direction.

### Step 4 — Design packaging

```bash
python3 scripts/packaging_designer.py --input features.json --profile saas --output markdown
```

Assigns features to Good / Better / Best by value-to-segment and cost-to-serve, then flags anti-patterns:

- **Feature dump** — Best tier carrying more than ~60% of total feature value
- **Decoy tier** — a tier no segment would rationally choose
- **No upgrade trigger** — adjacent tiers separated only by limits nobody hits
- **Price ladder gap** — step ratios that break the 2–3× rule of thumb
- **Orphan feature** — feature with no segment that values it above its cost

### Step 5 — Decide

Take model + range + packaging to the pricing committee. The skill does not commit the number and should not be asked to.

## Scripts

All three are stdlib-only Python 3.8+, no install step, no network calls.

| Script | Purpose | Input |
|--------|---------|-------|
| `scripts/pricing_model_picker.py` | 5-model fit scorer | `brief.json` |
| `scripts/wtp_analyzer.py` | Van Westendorp PSM | `survey.json` |
| `scripts/packaging_designer.py` | Good/Better/Best designer + anti-pattern detection | `features.json` |

Common flags: `--input PATH`, `--output markdown|json`, `--profile saas|api|marketplace`. Run any script with `--help` for the full schema, and see `references/pricing_canon.md` for worked input examples.

### Minimal inputs

`brief.json`

```json
{
  "product": "AI support triage",
  "buyer": "mid-market",
  "avg_deal_size": 18000,
  "customer_count": 140,
  "consumption_pattern": "hybrid",
  "value_measurable": true,
  "value_metric": "tickets deflected per month",
  "adoption": "bottom-up-then-top-down",
  "competitor_models": ["seat", "usage"]
}
```

`survey.json`

```json
{
  "currency": "USD",
  "respondents": [
    {"too_cheap": 50, "bargain": 150, "expensive": 400, "too_expensive": 900}
  ]
}
```

`features.json`

```json
{
  "segments": ["smb", "mid", "enterprise"],
  "features": [
    {"name": "Core dashboard", "cost": 1, "value": {"smb": 8, "mid": 6, "enterprise": 4}, "table_stakes": true}
  ]
}
```

## Reading the Output

- **Model score** is a fit score, not a probability. 70+ means "defensible", not "certain".
- **OPP is not the price.** It is the point where equal shares call you too cheap and too expensive. Real prices cluster between IDP and OPP.
- **PMC → PME is the negotiation envelope**, not the list price. List at or just under IDP; discount down toward PMC.
- **Tier count** — three is the default because it maps to a reference effect. Two is fine for API pricing; five is almost always a mistake at the SMB end.

## Anti-Patterns

- Recommending a specific number — this skill emits a range
- Running PSM with N < 30 and treating the result as evidence
- Treating the OPP as "the price" rather than the centre of a range
- Choosing value-based pricing without a value metric you can actually meter
- Designing tiers before the model is chosen — packaging is downstream of the model
- Packaging feature dumps into Best to justify the price
- Copying a competitor's published price as a proxy for willingness to pay

## Verification

Before presenting results, confirm:

1. The brief's `consumption_pattern` matches the winning model's assumptions
2. Survey N ≥ 30 and the four thresholds are monotonically ordered per respondent (`too_cheap < bargain < expensive < too_expensive`) — the analyzer reports violations
3. Every tier has at least one feature a named segment is willing to pay for
4. The recommended range has a stated currency and billing period

## References

- `references/pricing_canon.md` — model selection heuristics, PSM mechanics, tier design rules, and source reading list

## License

MIT — see `LICENSE`.
