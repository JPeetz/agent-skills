---
name: month-end-close
description: >-
  Use this skill when managing month-end financial close, running account
  reconciliations, preparing close checklists, or analyzing close efficiency.
  Activates on "month-end close", "close the books", "reconciliation", "bank
  reconciliation", "accrual", "prepaid", "deferred revenue", "close checklist",
  "trial balance", "variance analysis", "flux analysis", "journal entry",
  "close calendar", or "financial close". Covers close calendars and checklists,
  bank and balance-sheet reconciliations, accrual and prepaid schedules, deferred
  revenue roll-forward, journal entry drafting, trial balance and flux review,
  and close-cycle time reduction.
version: 1.0.0
author: Skill Foundry
license: MIT
category: finance-ops
compatibility: >-
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - finance
  - close
  - reconciliation
  - month-end
  - accounting
  - accruals
  - prepaids
  - deferred-revenue
  - journal-entries
  - trial-balance
  - variance-analysis
  - flux
  - close-checklist
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
    - finance-ops
    - month-end-close
    - reconciliation
    - accruals
    - flux-analysis
    - close-management
  related_skills:
    - saas-metrics-coach
    - accountant
    - fp-and-a-analyst
---

# Month-End Close

Close the books on a schedule, with evidence behind every number, so the P&L and
balance sheet are defensible the moment they land — not three weeks later after
someone asks "what is this $48k in 6410?"

The output of this skill is never "the close is done." It is a **close package**:
a checklist with completion state, reconciliation sign-offs with residual amounts,
a journal entry log, a trial balance that balances, and a flux narrative that
explains every movement over threshold.

## Operating principles

1. **Materiality first.** Set the threshold before you look at the numbers, not
   after you find an unexplained $3k. Every review procedure below has a
   threshold parameter and every exception is either cleared or disclosed.
2. **Reconcile to source, not to expectation.** A bank rec that agrees with the
   GL is not proof; it is proof only when the statement balance plus uncleared
   items ties to the GL balance. Agreeing two internal systems to each other
   proves nothing.
3. **Every journal entry has a why.** A JE without a support reference, a
   preparer, an approver, and a business reason is a plug with paperwork.
4. **Cutoff is a date, not an opinion.** Period cutoff, invoice date, receipt
   date, and service period are four different facts. Record which one you used
   on every accrual and every revenue line.
5. **Reversals are booked at entry time, not remembered at close time.** If an
   accrual should reverse, the reversing entry exists in the same batch as the
   accrual. Accruals that reverse "when we get the invoice" become permanent
   accruals.
6. **Hard lock at the end.** After lock, corrections go through a documented
   post-close adjustment, not a silent edit to a closed period.
7. **Same procedure every month.** A close that is reinvented monthly is not a
   close, it is a project. Standard templates beat heroic effort.

## Close calendar structure

Three phases, defined relative to period end (D0). Negative offsets are business
days before month end, positive offsets are business days after.

| Phase | Window | Purpose | Exit criterion |
|---|---|---|---|
| **Pre-close** | D-5 → D-1 | Freeze inputs, collect uncoded items, snapshot subledgers | All source data present and complete through D0 |
| **Core close** | D+1 → D+5 | Post entries, reconcile every balance-sheet account, build the TB | TB balances; every rec has a residual under threshold |
| **Review** | D+6 → D+8 | Flux narrative, package build, management sign-off, lock | Signed package, period locked, retrospective captured |

Two calendar models, and you must pick one explicitly:

- **Business-day model** — offsets are business days. Correct for companies with
  weekend transaction flow (e-commerce, SaaS with automated billing).
- **Calendar-day model** — offsets are calendar days, with hard dates. Correct
  when filing deadlines drive the schedule (statutory reporting, listed entities).

Mixing them silently is how a "D+3" task lands on a Sunday and the close slips
two days without anyone noticing.

## Close checklist by day

A checklist is a set of tasks with **owner, day, dependency, and evidence
artifact**. Status without an artifact is a claim, not a completion.

### Pre-close (D-5 → D-1)

| Day | Task | Owner | Evidence |
|---|---|---|---|
| D-5 | Confirm close calendar; publish dates and dependencies | Controller | Calendar doc, versioned |
| D-5 | Change freeze on ERP config, chart of accounts, and billing rules | Controller | Freeze notice |
| D-5 | Send data request to department heads (receipts, approvals, commitments) | Close lead | Request thread |
| D-4 | AP cutoff communication to vendors and internal requesters | AP clerk | Notice |
| D-4 | Confirm all bank/card feeds are connected and current | Accountant | Feed status screenshot |
| D-3 | Preliminary trial balance snapshot; archive it | Accountant | Snapshot file |
| D-3 | Subledger cutoff confirmation (AR, AP, inventory) | Accountant | Cutoff memo |
| D-2 | Payroll register received and reconciled to HR headcount | Payroll | Register + headcount tie-out |
| D-2 | Confirm no unposted batches older than 5 days | Accountant | Aging query |
| D-1 | Revenue subledger frozen; no invoicing without controller approval | Billing | Freeze confirmation |
| D-1 | Pre-close stand-up: known issues, expected accruals, staffing gaps | Controller | Meeting notes |

### Core close (D+1 → D+5)

| Day | Task | Owner | Evidence |
|---|---|---|---|
| D+1 | Post payroll journal (gross wages, taxes, benefits, employer cost) | Payroll | JE + register |
| D+1 | Import all bank and corporate card transactions through D0 | Accountant | Import count vs statement count |
| D+1 | Post recurring JEs (rent, subscriptions, depreciation, loan interest) | Accountant | Recurring JE batch |
| D+2 | Bank reconciliations — every operating and reserve account | Accountant | Signed rec per account |
| D+2 | Corporate card reconciliations and expense coding | Accountant | Rec + uncoded item list |
| D+2 | AR reconciliation, aging review, allowance assessment | AR analyst | Aging + allowance memo |
| D+3 | AP reconciliation and accrual completeness test (search for unrecorded liabilities) | AP clerk | Rec + search memo |
| D+3 | Post accrual JEs with reversing entries in the same batch | Accountant | JE batch |
| D+3 | Prepaid amortization schedule run and post | Accountant | Schedule + JE |
| D+3 | Inventory valuation and COGS reconciliation *(if inventory module active)* | Cost accountant | Valuation report |
| D+4 | Fixed asset roll-forward, depreciation, disposals, CWIP review | Accountant | Roll-forward |
| D+4 | Revenue recognition run; deferred revenue roll-forward tie-out | Revenue accountant | Waterfall + roll-forward |
| D+4 | Intercompany matching and elimination entries | Consolidation | IC matrix, zero residual |
| D+4 | Accrual true-up vs prior month actuals | Accountant | True-up memo |
| D+5 | FX revaluation of monetary balances; CTA where applicable | Treasury | Revaluation report |
| D+5 | Sales tax / VAT reconciliation and filing prep | Tax | Return vs GL |
| D+5 | Trial balance review: out-of-balance check, unusual movements | Controller | TB review sign-off |
| D+5 | Flux analysis above threshold with commentary | FP&A | Flux schedule |

### Review (D+6 → D+8)

| Day | Task | Owner | Evidence |
|---|---|---|---|
| D+6 | Journal entry review: all manual JEs approved, none missing support | Controller | JE log with approvals |
| D+6 | Variance commentary completed for every account over threshold | FP&A | Flux schedule, complete |
| D+7 | Financial statement package: P&L, BS, CF, supporting schedules | Controller | Package |
| D+7 | Management review and sign-off | CFO | Signature |
| D+8 | Lock period; close subledgers | Controller | Lock confirmation |
| D+8 | Retrospective: days consumed per task, blockers, checklist changes | Close lead | Metrics file |

## Bank reconciliation

The single most over-trusted procedure in accounting. Do it in a fixed order:

```
statement ending balance
  + deposits in transit (recorded in GL, not yet on statement)
  - outstanding checks (recorded in GL, not yet cleared)
  ± bank errors (rare; require statement evidence)
  = GL adjusted balance        -> must equal GL book balance
```

and independently:

```
GL book balance
  ± unrecorded bank items (fees, interest, direct debits)  -> post JEs
  = GL adjusted balance
```

### Matching rules

Match in this priority order; stop at the first match, do not let a loose rule
pre-empt a tight one.

1. **Exact amount + exact date + exact reference** — auto-match, no review.
2. **Exact amount + date within ±3 business days** — auto-match, log as
   date-tolerance match.
3. **Exact amount + fuzzy reference** (normalized: strip punctuation, case,
   leading zeros, vendor prefixes) — auto-match if unique; if multiple
   candidates, route to exception.
4. **Amount within tolerance + same counterparty** — candidate match, requires
   human confirmation.
5. **One-to-many / many-to-one** (batch settlement vs individual invoices) —
   sum-group matching, requires human confirmation.
6. **Everything else** — exception queue.

### Tolerance thresholds

Set these per account type, in writing, before the run:

| Account type | Amount tolerance | Date tolerance | Rule |
|---|---|---|---|
| Operating bank | 0.00 | ±3 business days | Zero amount tolerance; any cent difference is an exception |
| Corporate card | 1.00 | ±5 business days | FX and tip adjustments |
| Merchant/payout clearing | 5.00 | ±2 business days | Processor fee netting |
| Intercompany | 0.00 | 0 | Must match exactly or eliminate through the IC account |
| Suspense/clearing | 0.00 | n/a | Must be zero at lock |

The point of a tolerance is to route items to review, not to write them off.
A tolerance that is never touched is a tolerance that is too tight; a tolerance
that absorbs 40 items a month is a broken process.

### Exception handling

Every exception gets exactly one disposition, logged:

- **Timing** — will clear next period. Requires expected clearing date. Goes on
  the stale-item report with a clock.
- **Error** — needs a correcting JE. Amount, account, support, approver.
- **Unidentified** — no support found. If under materiality, reclass to a named
  suspense account with an owner and an investigation deadline. If over, do not
  close without escalation.
- **Bank error** — requires statement-side evidence (bank letter, corrected
  statement). Never adjust the GL for an unconfirmed bank error.

### Stale items

An item that survives more than two closes is not a timing difference, it is an
unrecorded error. Track:

- Age in periods, not days. "Cleared on the fourth close" is the number that
  matters.
- Anything older than **2 periods** escalates to the controller.
- Anything older than **3 periods** must be written off, corrected, or
  explicitly disclosed with a remediation plan.
- The stale-item count is a close-quality metric (see below). It should trend
  toward zero, not plateau.

## Accruals

### Standard accrual schedule

Maintain a standing schedule, one row per accrual, refreshed monthly rather than
rebuilt. Columns: accrual ID, GL account, counterparty, basis (contract /
estimate / run-rate), calculation, prior month actual, current accrual, reversal
date, owner, support reference.

| Accrual type | Basis | Common error |
|---|---|---|
| Unbilled professional services | Days worked × rate, or % complete | Accruing to budget instead of to actual delivery |
| Utilities | Prior month actual, seasonally adjusted | Forgetting the true-up when the invoice lands |
| Rent / opex fixed costs | Contract, straight-line | Double-counting when the invoice posts in the same period |
| Bonus / commissions | Plan attainment × rate, pro-rated | Missing the payroll tax and employer burden on top |
| Legal / professional fees | Engagement letter or estimate | Letting it run flat for six months with no true-up |
| Interest | Amortized cost × effective rate × days/365 | Using nominal instead of effective rate |
| Vendor goods/services received not invoiced (GR/IR) | Three-way match exceptions | Accruing at PO price when the invoice differs |

**Reverse at entry time.** For every accrual expected to be invoiced next period,
post the reversing entry in the same batch with the same date. Accruals that
"reverse later" are the number one cause of double-counted expenses.

**True-up discipline.** When the actual invoice arrives, the variance between
accrual and actual is itself a signal: a consistently large true-up means the
accrual basis is wrong, not that the month was unusual. Report the true-up amount
per accrual each month; a stable small true-up is the goal.

### Prepaid amortization

1. Every prepaid has: total amount, service start, service end, amortization
   method (straight-line by default), GL account, expense account, owner.
2. Amortize by **day count within the period**, not by whole months, whenever the
   service period does not align to month boundaries. Twelve equal twelfths of a
   mid-month-starting annual policy overstates the first and last month.
3. Short-term vs long-term split: the portion amortizing beyond 12 months sits in
   a long-term prepaid account. Reclassify monthly; do not let the split drift.
4. Roll-forward must tie: opening + additions − amortization − disposals =
   closing, per prepaid, and in total to the GL.
5. A prepaid fully amortized with a non-zero balance means the schedule and the
   GL have diverged. Find it in the month it happens.

### Deferred revenue recognition

Under ASC 606 / IFRS 15, revenue is recognized as performance obligations are
satisfied — not when cash arrives.

1. Maintain a contract-level waterfall: contract ID, total transaction price,
   term, start, end, recognition method (ratable / milestone / usage), deferred
   opening balance, billings, recognized, deferred closing.
2. Roll-forward must tie to the GL deferred revenue account:
   `opening + billings − recognized ± adjustments = closing`.
3. Ratable recognition uses day-count over the service period, same rule as
   prepaids — the mirror image of the same calculation.
4. Watch three specific failure modes:
   - **Billings recognized as revenue on cash receipt.** The classic. Cash is
     not revenue.
   - **Deferred revenue going negative** on a contract — always an error, either
     double-recognition or a missing billing record.
   - **Contract modifications** silently resetting the waterfall without a
     cumulative catch-up adjustment.
5. Every deferred revenue balance should be traceable to a specific contract.
   An unexplained pool balance is not a deferred revenue account, it is a
   suspense account wearing a costume.

## Trial balance review

Run these checks in order; each one gates the next.

### 1. Out-of-balance detection

- Sum of all debits equals sum of all credits. If not, the TB is corrupt — stop,
  do not "investigate the difference," find the unposted or one-sided batch.
- Balance sheet balances: assets = liabilities + equity. If not, and debits =
  credits, the issue is a mapping/classification problem, not a posting problem.
- Subledger-to-GL tie for AR, AP, fixed assets, inventory, deferred revenue. Each
  must be zero variance at lock.

### 2. Unusual account movements

Flag any account where any of these is true:

- Balance changed by more than the materiality threshold **and** more than 20% vs
  prior period.
- Sign flipped (asset became a credit balance, liability became a debit balance)
  — with an explicit whitelist for accounts where this is legitimate
  (accumulated depreciation, contra accounts, overdrafts).
- Activity in an account with zero activity for the prior 3 months (dormant
  account waking up is usually a miscoding).
- Balance is exactly round ($50,000.00) — often a plug.
- Account has a single entry comprising more than 80% of the period movement.

### 3. Flux vs prior period

Compare current to prior period, and current to same period last year where the
business is seasonal. Both comparisons, because MoM hides seasonality and YoY
hides a new problem.

Threshold: greater than max(materiality, 10% of the account balance) or any
movement over the hard floor. Everything above threshold needs a written
explanation from the account owner — not from the person who prepared the entry.

A flux explanation is one of exactly four things:

1. **Volume/price** — more units, different rate. Quantify both.
2. **Timing** — moved between periods. Name both periods and the reason.
3. **One-off** — non-recurring event. Name the event and confirm no recurrence.
4. **Error** — a mistake, now corrected or accruing. Name the correction.

"Variance due to higher spend" is not one of the four. It is a restatement of
the number.

## Variance analysis (budget vs actual)

For each account group, produce: actual, budget, variance in currency, variance
in percent, favorable/unfavorable flag (respecting the sign convention per
account — higher revenue is favorable, higher opex is not), and a narrative.

Structure the narrative in three layers:

- **Headline** — one sentence: what moved, by how much, why.
- **Driver decomposition** — the 2–3 components that sum to the variance.
- **Forward look** — does this repeat next month, and what is the revised
  expectation.

Rules that keep variance analysis honest:

- Compute variance on the same basis as budget (if budget excludes a
  reclass, compare like to like or explain the bridge).
- Never net an unfavorable variance against a favorable one in the same account
  group without showing both — that is how a missed cost target disappears.
- Percentages on small bases are noise: if the budget line is under the
  materiality floor, report currency only, and say the percentage is not
  meaningful.
- Reforecast only on request. A close is a reporting exercise; silently changing
  the forecast during close destroys the ability to measure forecast accuracy.

## Journal entries

### Anatomy of an acceptable JE

Every entry carries: JE number, date, period, entity, preparer, approver,
description that states the business reason, support reference (invoice number,
schedule tab, contract ID), line items (account, cost center, debit, credit), and
reversal flag with reversal date.

Missing any one of those makes it a **plug**, and plugs are the mechanism by
which material errors survive close.

### Entry types

| Type | Purpose | Rules |
|---|---|---|
| **Recurring** | Same amount/pattern each period (rent, depreciation, subscriptions) | Template with defined start/end; review annually; auto-reverse only if the underlying is an accrual |
| **Adjusting** | Bring accounts to correct balance at period end (accruals, true-ups, rev rec) | Must reverse or be superseded; never netted against another adjusting entry |
| **Correcting** | Fix a posted error from this or a prior period | Reference the original entry; if prior period and material, route to the restatement decision, do not bury it in current period |
| **Reclass** | Move amounts between accounts/cost centers with no P&L impact | Must net to zero; used for coding errors, never to change a reported total |
| **Reversal** | Undo a prior accrual | Posted at accrual time; if manual, must reference the original JE |

### Validation rules before posting

- Debits equal credits, per entry and per batch.
- No entry to a locked period.
- No entry to a control account (AR, AP, inventory, fixed assets) that bypasses
  the subledger — control accounts are posted to by the system, not by hand.
- Account requires a cost center/dimension and does not have one → reject.
- Amount exceeds the preparer's approval limit → route to approver, do not post.
- Same preparer is not the approver. Ever. This is the control, not a formality.

### Approval matrix (typical)

| Amount band | Preparer | Approver |
|---|---|---|
| < materiality / 10 | Staff accountant | Senior accountant |
| materiality / 10 → materiality | Senior accountant | Controller |
| > materiality | Controller | CFO |
| Any top-side / consolidation entry | Consolidation lead | CFO |
| Any entry affecting reported revenue | Revenue accountant | Controller + CFO |

## Close efficiency metrics

Track five numbers monthly. Without them, "the close feels slow" is the only
available diagnosis.

| Metric | Definition | Healthy signal |
|---|---|---|
| **Close duration** | Business days from D0 to period lock | Trend down or flat; absolute value is secondary |
| **Reconciliation coverage** | Balance-sheet accounts reconciled on schedule ÷ total accounts requiring rec | 100%; below 100% is a control gap, not a resourcing issue |
| **Items per person per day** | Completed checklist tasks ÷ accountant-days consumed | Rising = standardization working; falling = tasks got harder or bigger |
| **Stale item count** | Reconciliation exceptions older than 2 periods | Trending to zero |
| **Post-close adjustments** | JEs posted to a closed period after lock | Zero; any non-zero value needs a root cause |
| **Rework rate** | Tasks reopened after being marked complete | Under 5%; higher means completion is being declared, not verified |

Capture these at the retrospective (D+8), not from memory at quarter end. The
trend matters more than any single month, and a metric that improves for three
months then regresses usually means the person who built the process left.

## Workflow optimization

1. **Parallelize by account, not by day.** Most closes are serialized because
   tasks are sequenced by habit. Bank recs, prepaids, and fixed assets have no
   dependency on each other — run them concurrently from D+2.
2. **Map the real dependencies.** Build a DAG: what genuinely must finish before
   what. Usually 70% of the "sequence" is convention. The true critical path is
   normally: subledger cutoff → revenue recognition → TB → flux → package.
3. **Standardize templates.** One rec template, one accrual schedule, one flux
   template. Variation between preparers is the largest hidden cost in a close.
4. **Automate the mechanical 60%.** Bank feeds, recurring JEs, amortization
   schedules, depreciation, deferred revenue waterfalls. These are deterministic;
   every hour spent on them manually is an hour not spent on the 40% that needs
   judgment.
5. **Move review earlier.** Reviewing at D+7 means the error is three days old
   and the fixer has moved to another task. Review the bank rec at D+2 while the
   preparer still has context.
6. **Separate prep from review in staffing.** The person who prepared a rec
   should not be the reviewer, for control reasons and because self-review finds
   nothing.
7. **Pre-close the known items.** Bonus, commissions, known large invoices, and
   contract modifications can be prepared before D0. Anything knowable in advance
   should not consume core-close days.
8. **Measure the queue, not the effort.** If tasks wait 2 days between "prepared"
   and "reviewed," the constraint is reviewer capacity, and adding preparers
   makes it worse.

## Using the checklist script

`scripts/close_checklist.py` generates the checklist above for a specific entity
and period, scoped to the modules that are actually active, and marks status
against the current close day.

```bash
# Demo: run the built-in self-test (no input file needed)
python3 scripts/close_checklist.py --self-test

# Generate a markdown checklist
python3 scripts/close_checklist.py --input close-config.json

# JSON output for tooling, with two tasks already completed
python3 scripts/close_checklist.py --input close-config.json \
    --format json --done PC-02 --done CC-01

# Mark status as of a specific close day
python3 scripts/close_checklist.py --input close-config.json --day D+3
```

Config schema:

```json
{
  "entity": "Acme Inc.",
  "period": "2026-10",
  "close_model": "business_day",
  "modules": ["bank", "accruals", "prepaids", "deferred_revenue",
              "fixed_assets", "payroll", "ar", "ap", "tax"],
  "materiality": 25000,
  "team": {"controller": "A. Chen", "accountant": "M. Ortiz"}
}
```

`modules` drives scope: an entity without inventory does not get inventory tasks,
and the script warns when a module is active but has no assigned owner. Invalid
periods, unknown modules, and malformed configs exit non-zero rather than
producing a plausible-looking but wrong checklist.

## Anti-patterns

| # | Anti-pattern | Description | Impact | Fix |
|---|---|---|---|---|
| 1 | **Plug to close** | A balancing entry posted to "make it tie" with a vague description and no support | Hides errors that compound monthly; the plug grows silently until it is material | Ban unlabeled entries; every JE needs a support reference and a stated business reason |
| 2 | **Recurring accrual, no true-up** | An accrual posted at the same amount every month and never compared to actual invoices | Systematic over/understatement that reverses only at year-end audit; forecast becomes meaningless | True-up every accrual monthly; report the accrual-to-actual delta per line |
| 3 | **Reverse-when-invoiced** | Accrual booked without a reversing entry, "we'll reverse it when the bill comes" | Double-counted expense; forgotten reversals are the top cause of overstated liabilities | Post the reversal entry in the same batch as the accrual |
| 4 | **Cash-received revenue** | Recognizing revenue when the invoice is paid or the cash lands | Violates ASC 606; overstates revenue in strong collection months | Recognize on performance obligation satisfaction; deferred revenue roll-forward per contract |
| 5 | **Zero-tolerance-everywhere rec** | Applying 0.00 tolerance to every account including card and clearing accounts | Hundreds of trivial exceptions bury the three that matter | Tiered tolerances by account type, documented and reviewed quarterly |
| 6 | **Reconciling GL to GL** | "Reconciled" means two internal systems agree, with no tie to the bank or counterparty statement | Proves internal consistency, not correctness; catches nothing | Every rec anchors to an external source: statement, invoice, confirmation |
| 7 | **Immortal stale items** | Timing differences older than three closes, still listed as "will clear" | Unrecorded errors carried forward indefinitely; audit finding | Age by periods; escalate at 2, write off or disclose at 3 |
| 8 | **Self-approved JEs** | Same person prepares and approves, or approval is a checkbox applied in bulk at month end | Removes the only detective control on manual entries | Segregation enforced by system approval limits, not policy documents |
| 9 | **Silent post-close edits** | Adjustments posted to a locked period without disclosure or a documented adjustment log | Reported numbers change after distribution; destroys trust in the close | Hard lock plus a post-close adjustment log reviewed at the next close |
| 10 | **Variance without a driver** | "Higher than budget due to increased spend" or "timing" with no quantification | Commentary that restates the number instead of explaining it; reviewers cannot act | Require one of volume/price, timing (both periods named), one-off, or error — with quantification |
| 11 | **Checklist theater** | Tasks marked complete because the day arrived, no evidence artifact attached | The checklist reports progress that does not exist; failures surface at the review stage | Completion requires an artifact link; rework rate tracked as a metric |
| 12 | **Serialized close by habit** | Tasks run one after another because "that's the order we've always done it" | Close takes 12 days when 5 are available; everyone works weekends at month end | Map true dependencies as a DAG; parallelize independent recs from D+2 |
| 13 | **Materiality set after the fact** | Threshold chosen once the exceptions are visible, to make the list shorter | Exceptions are suppressed by redefining significance; nothing gets investigated | Set and document materiality before the first procedure runs, per entity |
| 14 | **Unreconciled suspense growth** | Suspense/clearing accounts allowed to carry a balance at lock | Errors accumulate in a place nobody reviews; balance becomes unexplainable | Suspense must be zero at lock or have a named owner and clearing deadline |

## Output contract

When this skill is used to run or support a close, the deliverable includes:

- **Checklist state** — tasks, owners, days, status, evidence reference per
  completed task.
- **Reconciliation summary** — per account: source balance, GL balance, residual,
  exceptions count, stale items count, preparer/reviewer.
- **Journal entry log** — every manual JE with type, support reference, preparer,
  approver.
- **Trial balance status** — debits = credits (yes/no), BS balances (yes/no),
  subledger ties at zero (per subledger).
- **Flux schedule** — every account over threshold with a driver-classified
  narrative.
- **Open items** — anything unresolved at lock, with owner, amount, and target
  date. An empty open-items list at lock on a first close is a red flag, not a
  success.

If any of those cannot be produced, say which and why. A close reported as
complete without a balancing trial balance is not a close.
