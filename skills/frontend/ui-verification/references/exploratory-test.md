# Exploratory browser testing

The probes in `SKILL.md` decide rules someone already wrote down. This pass
finds the cases the contract never listed: a fresh tester starts from a finished
feature and uses it the way an impatient, curious person would.

Use it when acceptance checks already pass and the user asks to "try to break
this", or when a feature is about to ship and nobody has driven it end to end.

## Preconditions

- **A test environment, not production.** You will submit garbage, double-click,
  and interrupt requests. Point at staging, a preview deployment, or a local
  build with a seeded database.
- **A fresh context.** New browser context, no reused cookies, no warm service
  worker. A tester with the developer's session is not a fresh tester.
- **The contract, in hand.** Read the acceptance criteria first, so what you
  report as "unlisted" is genuinely unlisted and not something the spec covered.
- **A place to write findings as you go.** Notes taken after the session are
  reconstructed, and reconstructed findings lose their reproduction steps.

## The pass

Work in this order. Each stage assumes the previous one passed; when a stage
strands you, that is already a finding.

### 1. Cold arrival

Land on the feature with no context: direct URL, not a link from inside the app.

- Does the page render anything useful before data arrives?
- Does the back button behave after three navigations into the flow?
- Reload mid-flow. Does it resume, reset cleanly, or half-restore?

### 2. The happy path, slowly

Do the intended thing, once, without hurrying. Note anything that makes you
pause: a label you had to re-read, a state you could not tell apart from
another, a button whose result was not where you looked.

### 3. The happy path, fast

Repeat it with speed: double-click submit, press Enter twice, Tab-and-Enter a
form in under a second. Look for duplicate submissions, races, and stale
renders.

### 4. Hostile input

For every text field: empty, one space, 5000 characters, emoji, RTL text, a
leading `=`, `<script>`, a newline, a pasted number with separators, an email
with a trailing dot. For every numeric field: `0`, `-1`, `1e9`, `0.000001`, and
a value at the documented maximum plus one.

Judge the response, not just the acceptance: a rejection with no explanation is
as much a defect as an acceptance of nonsense.

### 5. Boundaries and interruption

- Leave the flow and come back: is state preserved, discarded, or duplicated?
- Open the feature in two tabs and act in both.
- Kill the network mid-request (DevTools offline), then restore it. Does the UI
  recover without a reload?
- Navigate away during a save, then return.

### 6. Assistive and alternative input

- Tab through the whole flow without touching the mouse. Can you finish it?
- Zoom to 200% and 400%. Does the flow survive?
- Turn on reduced motion. Do transitions still land in a usable end state?
- Force a dark theme if the feature claims support.

### 7. Recovery

After each failure you caused, ask: how does a user who does not know the
system recover? If the answer is "reload", that is a finding.

## Writing it up

- One finding per observation, with numbered reproduction steps that a second
  person can follow without asking you anything.
- Include the state you were in when it happened (route, viewport, theme,
  signed-in account, data seeded).
- Classify the source explicitly: `explore:` for this pass, `runtime:` for a
  console/network observation, `axe:` for a tool-reported violation. Never
  present an exploratory finding as if a rule predicted it.
- Separate "broken" from "surprising". Surprising goes in a short notes section;
  a notes section that grows into a second findings list is a sign the contract
  is underspecified, which is itself worth reporting.

## What this pass is not

- Not a regression suite. Nothing here gets committed as a test; durable tests
  belong in the repo's test directory.
- Not a redesign review. If a finding needs a new layout or type scale, name the
  design mode to run next instead of proposing the redesign here.
- Not a substitute for the probes. If an exploratory finding maps to a probe
  (`target-size`, `failure-injection`), run the probe so the finding arrives
  with a measurement rather than an impression.

## Recording template

```text
explore:
  feature: checkout / payment step
  route: /checkout/payment
  session: seeded user, 360px, dark, production build
  finding: retry after a failed card charge re-submits the whole order
  steps:
    1. Add one item, continue to payment
    2. Enter a card that declines once (test fixture 4000000000000002)
    3. Click "Try again", submit a valid card
  observed: two orders created; order list shows duplicates
  expected: one order, retry only re-attempts the charge
  source: explore
  severity_hint: blocking (duplicate charge)
```
