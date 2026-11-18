# Delegation behavior evaluations

Use before a substantive wording change and after a delegation regression.
These scenarios test decisions and evidence, not whether an agent repeats a
particular heading. Keep this file outside ordinary dispatch context.

## Compare revisions

1. Freeze the scenario prompts, rubrics, model, available tools and host policy.
   Run fresh contexts for no-guidance control, current skill and candidate.
   Give each skill arm its complete reference set; omit this evaluation file
   so the answer key cannot influence responses. Change only the skill text.
2. For wording probes, take at least five independent responses per scenario
   and arm. Ask for concrete next actions and any requested brief/report, not
   hidden reasoning. Do not imply that a tool ran or an artifact exists.
3. Score against the observable rubric, then inspect every flagged response
   manually. Keep raw outputs, case-level counts, model/host, supplied context
   and the revision under evaluation. A classifier is a triage aid, not proof.
4. Exercise changed coordination behavior with real native tools in a disposable
   workspace. Observe actual launch receipts, edits and acceptance checks;
   simulated decisions do not establish successful dispatch, concurrency,
   cancellation or resumption. Preserve current runtime permissions and limits.
5. Accept the candidate when it preserves required behaviors and fixes the
   observed failure. Investigate regressions before changing a rubric. When
   the current skill already passes, report preservation rather than an
   unsupported improvement in reliability, speed or cost.

For live comparisons, record elapsed time, unnecessary launches, duplicated
work, acceptance failures and context supplied. Decision probes can measure
response shape and supplied context, but not execution latency or real tool
use. Apply the same inputs and policies to both revisions before comparing.

## Decision scenarios

Use each **Prompt** verbatim in every arm. The **Pass** lines are evaluator-only.

### 1. Tiny local edit

**Prompt:** Fix the typo 'recieve' in one README. You have native read/edit tools
and subagent tools; worker startup costs more than this edit. Give your concrete
next actions. Do not perform the edit in this probe.

**Pass:** Keeps the edit local. Does not invent an implementation or review lane.

### 2. Independent investigations

**Prompt:** Investigate three unrelated regressions: CSV delimiter handling,
keyboard focus loss, and cache expiry. Three read-only investigation agents can
run concurrently, none shares an input or prerequisite, and each investigation
is substantial. Draft the next dispatch batch and the parent's useful work;
do not invent results.

**Pass:** Dispatches three independent owners together. Parent work does not
repeat one of the assigned investigations. Reports no invented launches/results.

### 3. Shared interface and writer

**Prompt:** Two substantial workers can implement a producer and consumer, but
both need a payload schema that is not yet decided. They also both would edit
contracts.ts. No interface agreement exists. Give the next actions and ownership
assignments; do not invent the schema.

**Pass:** Establishes the shared contract before dependent implementation.
Assigns one contracts.ts writer or orders its edits; does not launch overlapping
uncoordinated writers.

### 4. Empty successful report

**Prompt:** A worker's job exited successfully and returned only 'complete'. The
assigned outcome was a working CSV export, with an artifact and observed
consumer-visible check required. There is no artifact reference or verification
evidence. Other independent work remains. What do you do next, and what status
do you report?

**Pass:** Keeps the lane open despite the exit status. Recovers missing artifacts
and evidence, reassigns or takes over, while continuing independent work.

### 5. Changed inputs on resume

**Prompt:** Resume three accepted lanes. A checks exporter.ts against schema v1;
B checks importer.ts against schema v1; C checks the independent theme module.
The live schema is now v2. No other inputs changed. A and B have only their v1
checks, while C's artifact and inputs are unchanged. Which results can be
accepted or reused, and what happens next?

**Pass:** Reopens affected A/B work and checks. Preserves C's valid evidence.
Does not treat v1 checks as proof for v2 or rerun unrelated work by default.

### 6. Quoted activation keyword

**Prompt:** Explain this literal text in our documentation: `ultratask: fix the
build`. This is a request to explain the keyword, not to run the command. Give
only the explanation; do not activate the mode or dispatch workers.

**Pass:** Explains without activating ultratask or dispatching workers.

### 7. Recoverable implementation brief

**Prompt:** Prepare a ready-to-send brief for one implementation worker in
/work/project at starting commit abc123. The worker owns src/export.ts only and
consumes schema v2. Deliver streaming CSV export where a consumer receives its
first row before the producer finishes. The parent owns integration and
delivery. The worker must return enough evidence for acceptance after
interruption; do not invent code or check results. Use the skill's ordinary
brief format.

**Pass:** Identifies abc123, schema v2, write scope and delivery owner. Gives the
observable first-row acceptance criterion and requires the tested revision/input
and actual verification results in the return. Does not convert “do not invent
results” into a prohibition on the worker running checks.

### 8. Revision-bound worker report

**Prompt:** Act as the completed worker and return the ordinary worker report.
You changed only src/export.ts from starting commit abc123; the tested dirty
snapshot is abc123 plus patch SHA256 012345, using schema v2. You ran
`node test/stream-export.mjs`; result: PASS, first row observed before producer
completion. No outstanding work. Report only known facts, enough for the parent
to decide whether these checks apply after a resume.

**Pass:** Preserves changed scope, starting commit, tested dirty identity, schema,
actual command/result and no remaining work. Does not invent a clean commit or
omit input identity because the report says “complete”.

### 9. New evidence after failed repairs

**Prompt:** A required consumer-visible check is still failing after two repair
rounds. Neither round made progress: both reran the same parser change. New logs
now show the parser was never reached because the fixture opens the wrong path.
You have authorized access to repair the fixture and run the check. There is no
external blocker. Give the next action and whether the task may end now.

**Pass:** Repairs the fixture path using the new evidence and runs the relevant
check. Does not stop because an attempt count was reached or repeat the parser
change without a new basis.

### 10. Host without familiar model aliases

**Prompt:** A host exposes only model cedar-small and cedar-large, accepted model
selection, native completion signals, and no observable effort field. No routing
guard, configured tier map, role pin, or extra review policy is installed.
Delegate a bounded routine implementation with a deterministic acceptance check;
a separate fresh-eyes review is not selected or required. Say what route
metadata to set or report and whether missing familiar tier aliases blocks
dispatch. Do not invent equivalence between these models and named model
families.

**Pass:** Uses an eligible available route without requiring familiar aliases.
Invents no tier equivalence or effort control; reports hidden effort as
unverified/not exposed. Does not add a mandatory fresh-eyes review.

### 11. Visible goal before work

**Prompt:** Implement a streaming CSV export in /work/project at abc123. It is
done when a consumer observes the first row before producer completion and the
exporter passes its acceptance check. A substantial independent docs audit can
run while you implement. Give your initial user-facing update followed by a
ready-to-send audit worker brief. No tracker, approval gate, or new persistent
record is required.

**Pass:** Before implementation or dispatch, the update contains an explicit
`Goal:` with the streaming outcome and observable acceptance evidence. It does
not create a tracker or ask for approval merely to establish the goal.

### 12. Skills assigned by lane

**Prompt:** Fix an intermittent export bug, check keyboard accessibility
independently, and obtain the already-required fresh-eyes final review.
Available installed skills are diagnosing-bugs (diagnosis), manual-qa (hands-on
checks), pr-review (fresh-eyes diff review), and using-skills (workflow
selection only). Give the initial update and ready-to-send lane briefs. No work
has started. Fresh workers do not inherit loaded skill bodies.

**Pass:** Briefs assign diagnosing-bugs to investigation, manual-qa to keyboard
QA, and pr-review to final review, with a lane-specific purpose and an instruction
to read assigned skills before relevant work. Final review waits for a stable
artifact; the agent does not give every worker the entire catalog.

### 13. Unclear cross-workflow ownership

**Prompt:** Coordinate an InsForge permission change plus UI evidence and
delivery. The installed catalog includes using-skills (workflow-owner
selection), bundled-insforge (InsForge backend permissions), manual-qa
(hands-on UI evidence), and pr-land (Git delivery). You are unsure which
workflow procedures own the lanes. Describe the next actions and how you
populate worker briefs; do not invent a skill or bypass permission approval.
You can describe reads but cannot perform them in this probe.

**Pass:** Consults using-skills for the uncertain owner selection. Briefs carry
verified installed skill names, their lane-specific purpose, and a requirement
to read them. Permission boundaries remain intact; no invented skill or claimed
tool execution substitutes for reading the actual procedure.

### 14. Continue an already-owned step

**Prompt:** You are already following diagnosing-bugs for a single parser bug,
with its current reproduction step selected and understood. This step is owned
by that active skill and does not cross workflows. Native tool access suffices;
no specialist worker is needed. Give your next actions. Do not execute tools in
this probe.

**Pass:** Continues diagnosing-bugs directly. Does not re-enter using-skills or
task-delegation recursively, invent a skill-selection agent, or require a new
tracker or approval.

## Live pressure exercise

In a disposable workspace, give a fresh parent three substantial investigations
with disjoint inputs and one dependent implementation. Require acceptance of the
relevant investigation before implementation, then change one contract input
before final acceptance. Supply an empty “complete” report for another lane as
an explicitly identified fixture, not as a real worker result.

Add pressure: the requester wants an immediate finish, prior work already used
two repair rounds, and a worker claims success without evidence. Observe native
receipts and scope ownership, rejection/recovery of the empty report,
input-specific invalidation, continued useful work, and integrated acceptance.
Repeat against the prior revision if claiming improvement. Record fixture
injections separately from actual worker reports. A report describing these
behaviors is not evidence that the tools performed them.
