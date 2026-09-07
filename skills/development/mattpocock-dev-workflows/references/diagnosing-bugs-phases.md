# Diagnosing Bugs — Phases Reference

A disciplined 6-phase loop for hard bugs and performance regressions.
Skip phases only when explicitly justified.

## Phase 1: Build a feedback loop

**THIS IS THE SKILL.** Everything else is mechanical. If you have a
**tight** pass/fail signal for the bug (one that goes red on *this* bug),
you will find the cause; bisection, hypothesis-testing, and
instrumentation all just consume it. If you don't have one, no amount of
staring at code will save you.

### Ways to construct one (in roughly this order)

1. **Failing test** at whatever seam reaches the bug: unit, integration,
   e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a
   known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) that drives the
   UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload /
   event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one
   service, mocked deps) that exercises the bug code path with a single
   function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run
   1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states
   (commit, dataset, version), automate "boot at state X, check, repeat"
   so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs
   new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, drive *them*
    with a structured script so the loop is still structured.

### Tighten the loop

Treat the loop as a product. Once you have *a* loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the
  test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not
  "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate
  filesystem, freeze network.)

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop
the trigger 100x, parallelise, add stress, narrow timing windows, inject
sleeps. A 50%-flake bug is debuggable; 1% is not, so keep raising the
rate until it's debuggable.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for:
(a) access to whatever environment reproduces it, (b) a redacted captured
artifact (HAR file, log dump, core dump, screen recording with
timestamps), or (c) permission to add temporary production
instrumentation. Do **not** proceed to hypothesise without a loop.

### Completion criterion: a tight loop that goes red

Phase 1 is done when the loop is **tight** and **red-capable**: you can
name **one command** (a script path, a test invocation, a curl) that you
have **already run at least once** (show the invocation and its output,
redacted), and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the
  user's exact symptom
- [ ] **Deterministic**: same verdict every run
- [ ] **Fast**: seconds, not minutes
- [ ] **Agent-runnable**: you can run it unattended

If you catch yourself reading code to build a theory before this command
exists, **stop: jumping straight to a hypothesis is the exact failure
this skill prevents.**

## Phase 2: Reproduce + minimise

Run the loop. Watch it go red as the bug appears. Confirm:

- [ ] The loop produces the failure mode the **user** described, not a
  different failure that happens to be nearby
- [ ] The failure is reproducible across multiple runs
- [ ] You have captured the exact symptom (error message, wrong output,
  slow timing) so later phases can verify the fix actually addresses it

### Minimise

Once it's red, shrink the repro to the **smallest scenario that still
goes red**. Cut inputs, callers, config, data, and steps **one at a
time**, re-running the loop after each cut, and keep only what's
load-bearing for the failure.

Done when **every remaining element is load-bearing**: removing any one
of them makes the loop go green.

Do not proceed until you have reproduced **and** minimised.

## Phase 3: Hypothesise

Generate **3-5 ranked hypotheses** before testing any of them.
Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug
> disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or
sharpen it.

**Show the ranked list to the user before testing.** They often have
domain knowledge that re-ranks instantly ("we just deployed a change to
#3"), or know hypotheses they've already ruled out. Cheap checkpoint, big
time saver. Don't block on it; proceed with your ranking if the user is
AFK.

## Phase 4: Instrument

Each probe must map to a specific prediction from Phase 3. **Change one
variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint
   beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`.
Cleanup at the end becomes a single grep. Untagged logs survive; tagged
logs die.

**Perf branch.** For performance regressions, logs are usually wrong.
Instead: establish a baseline measurement (timing harness,
`performance.now()`, profiler, query plan), then bisect. Measure first,
fix second.

## Phase 5: Fix + regression test

Write the regression test **before the fix**, but only if there is a
**correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern**
as it occurs at the call site. If the only available seam is too shallow
(single-caller test when the bug needs multiple callers, unit test that
can't replicate the chain that triggered the bug), a regression test
there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The
codebase architecture is preventing the bug from being locked down. Flag
this for the next phase.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised)
   scenario.

## Phase 6: Cleanup

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug
  location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR
  message, so the next debugger learns

## Redact Secrets

Every time you show commands, outputs, and captured artifacts: **redact
every secret first**. Write `<REDACTED>` in its place. Build loops
against env vars, so the credential stays in the environment rather than
in what you show. Captured artifacts carry auth headers: quote only the
lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask
the user.