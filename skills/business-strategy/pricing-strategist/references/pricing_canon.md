# Pricing Canon — Working Reference

Condensed reference for the three decisions this skill supports: **model**, **range**, **packaging**.
Everything here is a heuristic or a documented method — treat thresholds as defaults to argue with, not laws.

---

## 1. Choosing the Model

### The five models and their one-line test

| Model | Charge for | Works when | Breaks when |
|-------|-----------|------------|-------------|
| **Seat** | Access per user | The product's value grows with each additional human in the loop | One seat can serve a whole team (automation, shared inbox, API) — then you are undercharging for delivery |
| **Usage** | Consumed units | Consumption is meterable and correlates with value received | Buyers throttle usage out of cost anxiety, which kills habit formation |
| **Value-based** | A share of measured value | There is a metric both sides accept and you can meter | The metric is unattributable, or you cannot explain it at purchase time |
| **Freemium** | Nothing, until a limit | Self-serve onboarding and near-zero marginal cost per free user | Free users carry real cost-to-serve, or the gate is so weak that free is the product |
| **Hybrid** | Platform fee + a variable dimension | You need forecastability *and* upside; mid-market and above | Two dimensions raise sales friction more than they raise revenue |

### Selection rules of thumb

1. **Value metric beats buyer type.** Choose the model whose unit best tracks the value the customer receives, then adapt the contract to the buyer. Reversing this produces pricing that procurement likes and customers ignore.
2. **Match the model to the shape of consumption, not to the competitor.** Competitor pricing tells you what buyers will *benchmark* against, not what they will pay.
3. **Seat pricing is a headcount proxy.** It is correct only while headcount is a good proxy for value. AI features that let one person do the work of five break that proxy — this is the single most common model-shift trigger today.
4. **Usage pricing needs a floor.** Without a committed minimum, usage pricing makes your revenue as volatile as the customer's business and invites procurement to treat your bill as a cost centre.
5. **Freemium is a distribution decision, not a pricing decision.** If the product needs a sales rep to land, a free tier is a content marketing expense with a login.
6. **Hybrid is the default end-state for mid-market B2B.** A modest platform fee covers cost-to-serve; the usage component preserves expansion. Expect to explain it twice.
7. **Model migrations take 2–3 quarters and a cohort-by-cohort rollout.** Never reprice the whole base at once — grandfather, then migrate on renewal.
8. **One dimension at a time.** Adding a second pricing dimension while raising the price is two changes and one attribution problem.

### Signals it is time to revisit the model

- Net revenue retention is flat or negative while product usage grows
- Win rate is high and price is never the stated objection (you are underpriced)
- Customers routinely ask for a discount before scope is discussed
- A meaningful share of revenue comes from a segment the model was not built for
- Support cost per account grows faster than revenue per account

---

## 2. Van Westendorp Price Sensitivity Meter

### The four questions

Ask each respondent, in this order, for the same product description and currency:

1. At what price would this product be **so inexpensive that you would question its quality**? (`too_cheap`)
2. At what price would this product be **a bargain — clearly good value for the money**? (`bargain`)
3. At what price does this product start to become **expensive, though you would still consider it**? (`expensive`)
4. At what price is this product **too expensive — you would not consider it**? (`too_expensive`)

Order matters: asking for the upper bound first anchors the lower answers.

### Curves

Plot all four cumulative distributions against price:

- **Too cheap** — share of respondents whose `too_cheap` threshold is at or above the price. Descending: as price rises, fewer people call it cheap.
- **Bargain** — share whose `bargain` threshold is at or above the price. Descending.
- **Expensive** — share whose `expensive` threshold is at or below the price. Ascending.
- **Too expensive** — share whose `too_expensive` threshold is at or below the price. Ascending.

### The four intersections

| Point | Curves that cross | Reading |
|-------|-------------------|---------|
| **PMC** — Point of Marginal Cheapness | too cheap × expensive | Floor of the acceptable range. Below it, buyers suspect the product. |
| **PME** — Point of Marginal Expensiveness | bargain × too expensive | Ceiling. Above it, buyers stop considering you. |
| **OPP** — Optimal Price Point | too cheap × too expensive | Equal shares call you too cheap and too expensive. A centre, not a target. |
| **IDP** — Indifference Price Point | bargain × expensive | Equal shares call you a bargain and call you expensive. Usually the best anchor for list price. |

**Range of Acceptable Prices = PMC → PME.** List at or just under IDP; discount toward PMC; never settle below PMC.

### Pitfalls

- **N < 30 is not evidence.** Curves from small samples are step functions that produce spurious intersections. The analyzer warns; believe the warning.
- **The OPP is not the price.** It is the point of maximum indecision, not maximum revenue. Revenue is usually maximised above the OPP, because demand is inelastic in the upper half of the range.
- **PSM measures perception of price, not willingness to pay.** It says nothing about conversion at a given price. Pair it with a demand curve or a Van Westendorp-adjacent conjoint before committing.
- **Aggregate samples hide segments.** A bimodal sample (SMB and enterprise in one file) produces a wide, meaningless range. Split by segment and run twice.
- **Out-of-order thresholds signal careless respondents.** `too_cheap ≤ bargain ≤ expensive ≤ too_expensive` should hold. A few violations are noise; more than ~10% means the questionnaire or the sample is broken.
- **Currency and billing period must be fixed in the prompt.** Mixing monthly and annual answers corrupts the curves.

### Newton-Miller-Smith extension

Newton, Miller and Smith (1993) extend PSM by weighting each respondent's curves by stated purchase intent, producing a demand-adjusted version of the same four points. Useful for testing a downside scenario — the adjusted points sit below the raw ones. It does not fix a bad sample, and it is not a substitute for a real demand test.

---

## 3. Tier Packaging

### The default shape

Three tiers, cumulative: **Good ⊂ Better ⊂ Best**. Every feature in Good appears in Better and Best. Differentiation comes from features *added* up the ladder plus limits (seats, volume, retention, SLA, support).

| Tier | Job | Typical content |
|------|-----|-----------------|
| **Good** | Land the deal. Must be complete enough to be useful alone. | Table stakes, core workflow, single-team use |
| **Better** | Carry the volume. Target segment's actual job. | Collaboration, integrations, admin controls, higher limits |
| **Best** | Extract surplus from the few who need it. | Governance, SSO/SCIM, audit, dedicated support, custom terms |

### Ladder rules of thumb

- **Price steps of roughly 2–3×** between adjacent tiers read as intentional. Steps under ~1.5× look like a mistake; steps over ~5× make the middle tier decorative.
- **Value should rise faster than price.** Aim for value index ≈ price index ^ (1/0.85) — i.e. higher tiers are better deals per unit, which is what makes upgrading feel rational.
- **Two tiers are fine for API/usage pricing.** Five tiers at the SMB end is almost always a segmentation failure expressed as a product page.
- **Every tier needs a named buyer.** If you cannot say "this tier is for X", it is a discount mechanism wearing a feature list.

### Anti-patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **Feature dump** | Best carries the majority of total feature value | Push value down until Best is under ~60%; sell Best on governance and support instead |
| **Decoy tier** | Middle tier adds under ~15% value over entry | Widen the middle or collapse to two tiers |
| **No upgrade trigger** | Adjacent tiers ship identical features | Gate on a limit the target segment actually hits |
| **Top-heavy list** | Best lists 1.5×+ the features of Good | Prune features nobody pays for; a shorter list sells better |
| **Orphan feature** | A feature whose value never exceeds its cost-to-serve | Drop it, or fold it into a tier where it is free to serve |
| **Ladder gap** | Entry→mid step far larger than mid→top | Rebalance; the middle tier is absorbing demand and capping expansion |

### Sequencing

Model → range → packaging. Packaging designed before the model is chosen encodes the wrong unit, and packaging designed before the range exists encodes a price you invented. Both are expensive to unwind.

---

## 4. Reading List

- Van Westendorp, P. (1976). *NSS-Price Sensitivity Meter (PSM) — A New Approach to Study Consumer Perception of Price.* ESOMAR Congress.
- Newton, D., Miller, J., & Smith, P. (1993). *A Market Acceptance Extension to Traditional Price Sensitivity Measurement.* American Marketing Association.
- Monroe, K. B. *Pricing: Making Profitable Decisions.* McGraw-Hill.
- Nagle, T. T., & Müller, G. *The Strategy and Tactics of Pricing.* Routledge.
- Anderson, J. C., Narus, J. A., & van Rossum, W. (2006). *Customer Value Propositions in Business Markets.* Harvard Business Review, March 2006.
- Ramanujam, M., & Tacke, G. (2016). *Monetizing Innovation.* Wiley.
- Reichheld, F. F., & Sasser, W. E. (1990). *Zero Defections: Quality Comes to Services.* Harvard Business Review — the origin of the retention-economics argument for pricing below the ceiling.

### Caveats on the literature

- PSM predates SaaS. Its mechanics transfer; its assumptions about discrete purchases and known substitutes transfer less well. Re-interpret the four points for subscription contexts rather than quoting them as-is.
- Most published "optimal price" case studies are survivorship-biased. Use them to calibrate direction, never as a benchmark for your own number.
- Any pricing benchmark older than about five years should be treated as a hypothesis, especially in categories where AI has changed the cost-to-serve.
