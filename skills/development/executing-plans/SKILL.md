---
name: executing-plans
description: Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available
---

# Executing Plans

Execute the plan yourself, task by task, in this session: no implementer
subagent per task, no reviewer per task — one fresh-context review of
the whole branch at the end. Inline execution gives up a fresh context
and a second pair of eyes per task; this skill replaces them: the brief
is the spec, the ledger is your memory, TDD is the per-task gate, and
the final reviewer is the second pair of eyes.

**Core principle:** the plan already did the thinking. Execute it
exactly, prove each step with a test you watched fail and then pass,
and leave a record that survives your own forgetting.

**Narration:** at most one short line between tool calls — the ledger
and the tool results carry the record.

**Continuous execution:** execute every task in the plan without
pausing to check in between them. Four things stop you, and only these:
an irreversible or destructive operation; a security-sensitive action;
a side effect outside this worktree that norms gate (a merge, a push to
a shared branch, a publish); and a plan so broken that every path
forward is a guess.

**Rulings, not stalls.** Conflicts, ambiguities, plan defects — decide
them. The spec is the binding authority, the plan is its argument, and
your judgment settles what neither answers. Record every decision in
the ledger as `Ruling: <what you decided> — <why> — <what it costs if
wrong>` and keep going. Deviating from the plan without a ledgered
ruling is a decision made in secret.

## When to use

- You have a plan from writing-plans and inline execution was chosen at
  the handoff.
- Your harness has no subagent tool (see the per-platform references in
  `../subagent-driven-development/references/`). Never fabricate a
  dispatch; run the plan here.
- Tasks are mostly independent — the same precondition as
  subagent-driven-development.

A fully specified plan makes inline execution transcription plus
testing: it runs well on a mid-tier session model, and the one place
the most capable model earns its cost is the final review, which this
skill dispatches separately. Prefer subagent-driven-development when a
review gate per task is wanted, or when the plan is long enough that
its last tasks would run on a compacted context — the ledger keeps a
long inline run recoverable, but the last tasks get the least of you.

## Setup

Create or verify the isolated worktree under the repository's worktree
procedure. Never start implementation on the default branch.

Conversation memory does not survive compaction. An inline executor
that loses its place re-implements tasks whose commits already exist.
Track progress in a ledger file, not only in todos — todos are a live
view; the ledger is the record. The workspace and ledger are shared
with subagent-driven-development (same directory, same format), so a
plan can change executors mid-flight and the new one resumes from the
same ledger.

- Each plan owns a workspace: at skill start, run
  `../subagent-driven-development/scripts/sdd-workspace PLAN_FILE` — it
  prints the plan's git-ignored directory, home to every artifact for
  THIS plan: ledger, briefs, review packages. Another plan's directory
  is never yours to read or write.
- The ledger is `<workspace>/progress.md`, created with the identity
  line `# SDD ledger — plan: <plan file path>`. Tasks with a
  `Task <N>: complete` line are DONE — their commits exist in git even
  when your context forgot making them; after compaction, trust the
  ledger and `git log` over recollection. A ledger whose first line
  names a different plan is another plan's progress: leave it and start
  your own. `git clean -fdx` destroys the workspace (it is git-ignored
  scratch); recover from `git log`.

Read the plan once, note its context and Global Constraints, and create
a todo per task. If the plan names a spec, read it too — the spec is
the authority the plan argues from, and conflicts inside the plan
resolve against it. A plan with no reachable spec gets a ledger note
saying so; rulings made without one are provisional.

**REQUIRED SUB-SKILL:** load engineering-skills:tdd now, before Task 1.
It governs every step of every task; a plan whose steps already say
"write the failing test first" does not exempt you.

Before Task 1, scan the plan's Interfaces blocks for conflicts between
tasks: for every task that consumes what an earlier task produces, one
ledger row — the two tasks, what one produces against what the other
consumes, and what you found. A plan whose tasks share nothing gets the
single line `Pre-flight: no shared interfaces`. Rule on each conflict a
row surfaces with the spec as the binding authority, record the ruling
beside its row, and start Task 1. Each task's own text is checked when
you read its brief, not here.

## The task loop

Everything you print, and every tool result, stays resident in context
for the rest of the session. Redirect long test output to a file in the
workspace and read its tail; read a brief, not the whole plan.
Bookkeeping rides along with work — a ledger append in the same call as
the commit, never in a call of its own.

### 1. Take the task

- Run `scripts/task-start PLAN_FILE N`. It prints the brief path and
  BASE (the commit the task's review range is cut from) in one call.
- Read the brief for every task, including ones you remember from
  setup: memory holds a summary; the brief has the exact values,
  signatures, and test cases.
- Mark the task's todo in_progress.

### 2. Work the steps

The plan's steps are already in RED-GREEN order; follow them in that
order under engineering-skills:tdd, loaded at setup. A test step's code
is written first and run first. Watching it fail is a step, not a
formality — a test that passes before the implementation exists is a
finding about the test.

Every step that runs a command has an `Expected:` line. Run the
command, read its output, and compare. Three outcomes:

- **Matches.** Next step.
- **The code is wrong.** Use engineering-skills:diagnosing-bugs. Find
  the cause; never patch the symptom to make the step's output match.
- **The plan is wrong** — a step contradicts the spec, an earlier
  task's interface does not match what this task consumes, a command
  that cannot work. Rule on the smallest change that satisfies the
  spec, ledger it as `Task <N>: Ruling: <finding> — <what you decided
  and why>`, and continue. The ruling is carried, not remembered: later
  tasks that touch the same interface read it from the ledger.

Commit as the plan's commit steps say. A task that spans several
commits is fine; BASE is what the review range is cut from, never
`HEAD~1`.

### 3. The completion contract

Before a task's ledger line, all of the following are true, with
evidence in this session — not inferred from the diff looking right:

- Every test the brief names exists and ran in this task, and you read
  the output.
- The final test run for the task passed — `task-done` is that run, and
  it writes the command and result into the ledger line.
- Every `Expected:` line in the brief was compared against real output.
- Every deviation from the brief has a `Ruling:` line in the ledger.

If any item is missing, the task is not complete: finish it.

### 4. Complete the task

Run `scripts/task-done PLAN_FILE N BASE -- <test command>` with the
test command the brief names for the whole task. It runs the tests,
keeps the full output in the workspace, prints the tail, and — only if
they pass — appends the completion line to the ledger:

`Task <N>: complete (commits <base7>..<head7>, tests: <command> → <result>)`

A failing run records nothing; the task is not complete. When it
records, mark the todo complete and take the next task.

## Final review

Run `../subagent-driven-development/scripts/review-package PLAN_FILE
MERGE_BASE HEAD` (MERGE_BASE = the commit the branch started from, e.g.
`git merge-base main HEAD`) and review from the file it prints.

**With a subagent tool:** dispatch the reviewer on the most capable
available model — the whole-branch review is a judgment task — using
engineering-skills:code-review's
[code-reviewer.md](../subagent-driven-development/references/code-reviewer.md),
with the package path, the plan and spec paths, the plan's Review Focus
section verbatim if it has one (the input classes and failure modes the
plan's tests do not exercise — the reviewer checks each deliberately),
and a pointer to the ledger's `Ruling:` lines so it can weigh the calls
you made. Specify the model explicitly; an omitted model inherits the
session's, which may not be the most capable. This is the one fresh
context the whole run buys; do not replace it with your own read of the
diff.

**Without a subagent tool:** read code-reviewer.md and perform that
review yourself against the package, as a separate pass after the last
task's ledger line. Write `Final review: self-review (no subagent
tool)` to the ledger, and say so in your final message: a self-review
by the author is weaker than a fresh reviewer, and your human partner
decides whether that is enough before merge.

Sort the findings before acting on any. The reviewer's severity labels
are advice; the gate is yours, and so is its "Declined to judge" list —
every line there is a ruling you make and ledger: `Final: Ruling:
<behavior the reviewer set aside> — <what a reasonable person using
this software gets, and why that stands or is now a finding> — <cost if
wrong>`. Re-grade first, by effect: a finding's grade is what a
reasonable person using this software gets if it ships, not whether the
spec names the triggering input — a reviewer who set a finding at Minor
because the spec was silent has graded the spec, not the effect. Then:

- **Critical and Important** enter the fix pass.
- **Minor** goes to the ledger as `Final: minor (deferred): <one-liner>`
  and to your final message under "Deferred minors". Minors never enter
  the fix pass, and never become rulings — a ruling is a decision about
  a conflict, not a note that you declined a polish suggestion.

Fix the Critical and Important findings yourself in ONE pass, each
verified by TDD: write the test that reproduces the finding, watch it
fail, make it pass, then run the whole suite. Record each in the ledger
as `Final: fixed <finding> — <test name> RED→GREEN, suite <N>/<N>`. A
fix without a test that failed first is not verified; a suite that is
not green after the pass means the pass is not over. Do not dispatch a
re-review: the covering tests already answer "addressed" and the suite
run already answers "broke nothing". A finding you decide not to fix is
a ruling — `Final: Ruling: <finding> — <why the code stands> — <cost if
wrong>` — reported in the rulings list. There is no second fix pass.

## Finish

Collect every `Ruling:` ledger line into your final message under
"Rulings I made", in the order made, each with what it costs if wrong,
and every `minor (deferred)` line under "Deferred minors". Both lists
are exhaustive — the final message is the only place decisions taken on
your partner's behalf reach them.

When the final review is clean and its fixes are committed, delete this
plan's workspace directory — the git history is the record now. Sibling
directories belong to other plans; leave them alone. Then use pr-land.

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "I remember what Task N says" | You remember a summary. The brief has the exact values. Read it. |
| "The plan's code is right, skip watching the test fail" | A test you never saw fail proves nothing. It is one step. Run it. |
| "The plan is wrong here, I'll just do the right thing" | Do the right thing and ledger the ruling. Unledgered deviation is a decision made in secret. |
| "I'll write the ledger lines after a few tasks" | Compaction does not wait for a convenient moment. One line per task, in the same message as the commit. |
| "Let me check in before the next task" | Inline execution was chosen to spend less. Only the four stops stop you. |
| "I read my own diff carefully; the final reviewer is redundant" | Same author, same blind spots. The reviewer is the only fresh context this run buys. |
| "The reviewer said Minor, so it's Minor" | The label graded the spec's silence. Grade what the person gets. Re-grade, then gate. |
| "The fix is obvious, no need for a failing test first" | The failing test is the only proof the finding was real and is now gone. Without it you have a diff and a hope. |
| "I'll fix the minors too while I'm in there" | Every minor you fix is a test, a fix, and a suite run your partner did not ask for. Ledger them; your partner decides. |
