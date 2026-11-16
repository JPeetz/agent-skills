# The Month-End Close Framework

Reference material for `month-end-close`. Covers the phase model, the task
inventory per phase, role definitions, the close-calendar concept, and the
levers that actually shorten a close.

---

## 1. Why the close has a shape

A close is not a list of reconciliations. It is a **dependency graph** with a
hard deadline, where the constraint is almost always reviewer capacity and
data completeness rather than posting effort.

Every close decomposes into the same four questions, and the phases exist to
answer them in order:

1. **Is the data complete?** (pre-close) — nothing else matters until it is.
2. **Is every balance correct?** (core close) — post, reconcile, tie.
3. **Does the story make sense?** (review) — flux, variance, challenge.
4. **Is it frozen?** (lock) — after which change requires a log.

Skipping to question 2 with incomplete data is the single most common reason a
close slips: the bank rec looks clean because half the transactions never
arrived.

---

## 2. Phase model

### Pre-close — D-5 to D-1

**Goal:** arrive at D0 with complete data, frozen systems, and known problems
already named.

| Offset | What happens | Who |
|---|---|---|
| D-5 | Calendar published; change freeze on ERP config, COA and billing rules; data request sent | Controller, Close lead |
| D-4 | AP cutoff communication; bank/card feed verification; vendor statement requests | AP clerk, Accountant |
| D-3 | Preliminary TB snapshot (archived); subledger cutoff confirmation | Accountant |
| D-2 | Payroll register received and tied to headcount; aged unposted batches cleared | Payroll, Accountant |
| D-1 | Revenue subledger frozen; pre-close stand-up with known issues and expected accruals | Billing, Controller |

**Exit criteria:** all feeds current through D0; no unposted batch older than
5 days; known accruals listed with amounts; no open question about what will
arrive late.

**Design notes**

- The change freeze matters more than it looks. A chart-of-accounts edit on D+2
  invalidates every mapping in the flux schedule and usually goes unnoticed
  until next month's comparison is nonsense.
- Subledger cutoff must be enforced by the system, not by asking people not to
  post. "We told them" is not a control.
- The preliminary TB snapshot is what lets you prove, after lock, exactly what
  changed and when. Without it, a post-close adjustment is indistinguishable
  from a mistake.

### Core close — D+1 to D+5

**Goal:** every balance-sheet account reconciled, every manual entry posted,
trial balance balanced, flux drafted.

| Offset | What happens | Who |
|---|---|---|
| D+1 | Payroll journal; full transaction import; recurring JEs | Payroll, Accountant |
| D+2 | Bank recs (all accounts); card recs; AR rec + aging + allowance | Accountant, AR analyst |
| D+3 | AP rec + unrecorded liability search; accruals with reversals; prepaid amortization; inventory valuation; commission accrual | AP, Accountant, Cost accountant, RevOps |
| D+4 | Fixed asset roll-forward; revenue recognition + deferred revenue roll-forward; intercompany matching and eliminations; accrual true-ups | Accountant, Revenue accountant, Consolidation |
| D+5 | FX revaluation; sales tax/VAT reconciliation; TB review; flux analysis | Treasury, Tax, Controller, FP&A |

**Exit criteria:** debits = credits; balance sheet balances; every subledger ties
to GL at zero; every rec has a residual under threshold or a logged disposition;
flux drafted for every account over threshold.

**Design notes**

- D+2 to D+4 is where parallelization pays. Bank recs, prepaids, fixed assets
  and revenue recognition have no dependency on each other. Running them serially
  is habit, not logic.
- Accrual reversals belong in the same batch as the accrual. Any process that
  relies on remembering to reverse later will eventually double-count.
- The unrecorded-liability search is a *sample*, and it should be documented as
  a sample: population, selection basis, items tested, conclusion. "We looked"
  is not evidence.

### Review — D+6 to D+8

**Goal:** turn a correct trial balance into a reviewed, signed, locked package.

| Offset | What happens | Who |
|---|---|---|
| D+6 | Manual JE review and approval; variance commentary completed | Controller, FP&A |
| D+7 | Financial statement package built; management review and sign-off | Controller, CFO |
| D+8 | Period locked; retrospective and efficiency metrics captured | Controller, Close lead |

**Exit criteria:** every manual JE has support and a non-preparer approver; every
variance over threshold has a driver-classified narrative; package signed; period
locked; metrics recorded.

**Design notes**

- Review at D+6 rather than D+8 is deliberate: by D+8 the preparer has moved on
  and the fix costs twice as much.
- The retrospective is not optional overhead. Close duration, stale-item count
  and rework rate are the only inputs to next month's improvement, and memory
  at quarter end is unreliable.

---

## 3. Roles and responsibilities

| Role | Owns | Does not own |
|---|---|---|
| **Controller** | Calendar, change freeze, TB review, JE approval, lock | Preparing recs (segregation) |
| **Close lead** | Checklist state, task assignment, retrospective, escalation | Accounting judgments |
| **Staff/senior accountant** | Bank/card recs, accruals, prepaids, fixed assets, recurring JEs | Approving own entries |
| **Revenue accountant** | Revenue recognition run, deferred revenue waterfall, contract modifications | Billing operations |
| **AP clerk** | AP rec, cutoff communication, unrecorded liability sample | Accrual estimation for non-AP costs |
| **AR analyst** | AR rec, aging, allowance assessment | Collections execution |
| **Payroll** | Register, payroll journal, headcount tie-out, employer taxes | Benefit plan accounting |
| **Cost accountant** | Inventory valuation, COGS, standard-cost variances | Purchasing |
| **Consolidation** | IC matching, eliminations, top-side entries | Entity-level closes |
| **Treasury** | FX revaluation, CTA, bank relationship items | Operating recs |
| **Tax** | Sales tax/VAT reconciliation, filing prep, provision inputs | Revenue recognition |
| **FP&A** | Flux narrative, budget-vs-actual, variance commentary | Posting entries |
| **CFO** | Management review, sign-off, escalation decisions | Preparing or approving at preparer level |

### Segregation rules that are non-negotiable

1. Preparer ≠ approver, for every manual JE and every reconciliation.
2. The person who owns the budget does not unilaterally write the variance
   explanation for their own line without review.
3. Bank rec preparer has no ability to create vendors or change bank details.
4. Whoever can post to a closed period is a named, logged role — not "finance
   admins".

---

## 4. The close calendar concept

A close calendar is not a date list. It is a **contract** with four properties:

1. **Offsets, not dates.** Every task is defined as D±n so the calendar survives
   a period-end that lands on a weekend. Publish dates derived from offsets.
2. **A declared day model.** Business-day or calendar-day, stated explicitly and
   used consistently. Mixing them silently is how a D+3 task lands on a Sunday.
3. **A named owner per task.** Unowned tasks do not get done; they get absorbed
   by whoever is most anxious, which is not a staffing strategy.
4. **A dependency map.** What must finish before what. In practice 60–70% of
   assumed sequencing is convention, and removing it is free speed.

### Typical failure modes of a calendar

| Symptom | Underlying cause |
|---|---|
| Close consistently finishes D+9/D+10 | Reviewer bottleneck at D+6–D+7, or data arriving late at D+2 |
| Some months fast, some slow | Tasks are date-anchored; weekend/holiday collisions |
| Same three tasks always late | Those tasks depend on an external party with no SLA (payroll provider, bank, landlord) |
| Checklist complete but errors found at review | Completion is being declared without evidence artifacts |
| Nobody can say who owns a step | Calendar was never written down, or was written once and drifted |

---

## 5. Acceleration strategies

Ordered roughly by return on effort. Most companies attempt #5 first, which is
the only one that reliably fails.

1. **Instrument first.** You cannot shorten what you cannot measure. Capture
   close duration, hours per task, and queue time between prepared and reviewed
   for two months before changing anything. The queue time is usually the answer.
2. **De-serialize.** Rebuild the task list as a dependency graph. Run bank recs,
   prepaid amortization, fixed assets and revenue recognition concurrently from
   D+2.
3. **Pre-close the knowables.** Bonuses, commissions, known large invoices,
   signed contracts, depreciation. Anything determinable before D0 should not
   consume core-close days.
4. **Standardize templates.** One rec template, one accrual schedule, one flux
   format. Preparer variation is the largest hidden cost in a close and the
   hardest to see.
5. **Automate the deterministic 60%.** Bank feeds, recurring JEs, amortization
   schedules, depreciation runs, deferred revenue waterfalls. These have no
   judgment in them; every manual hour is an hour unavailable for the 40% that
   does.
6. **Add reviewer capacity before preparer capacity.** If work waits two days
   between prepared and reviewed, adding preparers increases the queue.
7. **Move review into the flow.** Review the bank rec at D+2 rather than the
   package at D+7. Same reviewer hours, earlier defect detection, cheaper fixes.
8. **Cut scope honestly.** Some reconciliations exist because they always have.
   Test each against materiality and risk, document the rationale for any
   downgrade to quarterly, and get it approved. Do not simply stop doing them.
9. **Set an SLA with external dependencies.** Payroll provider, bank statements,
   landlord, key vendors. A close cannot beat its slowest external input, and an
   unstated dependency is always late.

### What acceleration is not

- **Not a shorter checklist.** Removing tasks shortens the close and lengthens
  the audit.
- **Not working weekends.** Overtime hides the constraint; the constraint
  returns the following month.
- **Not a bigger team.** More preparers on a reviewer-bound close produces more
  work in progress and the same lock date.
- **Not a new ERP.** The system is rarely the bottleneck; the process around it
  is. Migrating during close season is how a company discovers that in
  production.

---

## 6. Soft close vs hard close

Some organizations run a **soft close** (management numbers, no lock, adjustments
allowed) followed by a **hard close** (locked, reported). If you use this model:

- Soft close has a declared cutoff and a declared set of accounts in scope. It is
  not "the numbers as they stand".
- Every adjustment between soft and hard close is logged with a reason. The size
  of that log measures how much the soft close is guessing.
- The hard close is the only one with a sign-off.
- Reporting soft-close numbers externally without labelling them as preliminary
  is a disclosure problem, not a process preference.

A soft close that routinely moves 10%+ between versions is not a soft close, it
is an early draft being presented as a result.

---

## 7. Interactions with adjacent processes

| Process | Interaction |
|---|---|
| **Financial audit** | The close evidence set (recs, JE log, flux) is the audit PBC list. Build it during close, not from memory in February |
| **Budgeting / reforecast** | Close produces actuals; it must not also silently revise the forecast, or forecast accuracy becomes unmeasurable |
| **Revenue operations** | Contract modifications after the subledger freeze are the usual cause of a revenue restatement |
| **AP / procurement** | Cutoff discipline lives in AP; a close cannot compensate for an AP team that codes late |
| **Payroll** | Payroll calendar rarely aligns to month end; the accrual for the straddle days is a permanent, frequently-missed item |
| **Tax** | Sales tax reconciliation needs the revenue split by jurisdiction, which is a revenue-recognition output, not a tax input |
