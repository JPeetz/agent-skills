# Implementation lanes and resumption

Use for implementation readiness, requested or selected fresh-eyes review, or resumption.
Keep delivery with the existing repository workflow; this protocol grants no additional authority.

## Brief and recovery records

Use the canonical [lane contract](../SKILL.md#lane-contract). Keep ownership,
status, input revisions, and evidence in existing host records. Add compact
brief and report files when recovery, handoff, or a long run makes them useful;
put their absolute paths in the dispatch. Existing recoverable records need no
second ledger or fixed workspace layout.

## Implementation readiness

For every implementation lane, even when no fresh-eyes reviewer is selected,
inspect the current repository before running or reusing acceptance checks:

1. Inspect `git status --short --untracked-files=all`, the complete `BASE..HEAD`
   commit diff, and `git diff HEAD` (the integrated staged and unstaged tracked
   state).
2. Enumerate `git ls-files --others --exclude-standard` and inspect the contents
   of in-scope untracked files. Separate unrelated edits and other owners' work
   from the lane; reconcile unclear base, scope, or ownership.
3. Bind each check to the actual current inputs and covered scope. The actual
   diffs and artifacts, not an agent's summary, determine what changed and what
   evidence applies. Reuse unaffected valid evidence; rerun missing or affected
   checks and any broader checks or fresh attestations required by policy.

Repeat readiness when inputs change before accepting or reusing evidence. Do not
rerun every test merely because another input changed.

## Review the complete lane

A requested or workflow-required Critique stage requires a fresh-eyes review: a
fresh-context agent that did not author the change, even if no separate review
lane was selected beforehand. The same applies when the parent selects a
fresh-eyes review or policy requires it. Supply the original requirements,
binding constraints, and the complete actual change package, not the author's
transcript or correctness argument.
The implementer's self-check can supplement but cannot satisfy this critique.
Keep the target read-only unless separately authorized. Apply
[Model routing](model-routing.md#reviews).

- Cover `BASE..HEAD` plus authorized staged, unstaged, and untracked lane changes.
  Use the full commit range, the tracked working diff from `HEAD`, and the
  authorized untracked artifacts; reviewing only the latest commit loses prior
  lane work. Separate unrelated edits and other owners' work from the package.
- Include the commit log, diff summary, relevant full diff/artifacts, and the
  revision/input references behind checks. If the base, scope, or ownership is
  unclear, reconcile it before accepting the lane.
- Require two explicit verdicts: spec compliance and code quality, each with
  evidence and unresolved findings. A review missing either verdict stays open.
  A successful exit, a green suite, or an author's conclusion is insufficient.

## Repair, reuse, and acceptance

Before reuse or resumption, verify the live revision and relevant inputs against the
recorded evidence.
Reopen affected work when inputs changed; preserve unaffected accepted work.
Use [Graph workflow](graph-workflow.md) to bind checks and reviews to their
scope and inputs. Run required broader checks and fresh attestations even
when a scoped check can be reused.

Return material findings to the implementer, then re-review the fix and newly
affected scope. Investigate failed approaches before repeating or escalating;
choose recovery from the evidence rather than a fixed round count.
Unresolved spec failures or material findings keep the lane open; resolve them,
remove the affected change with proof, or report the owner, blocker, and next
action. Record any authorized deferral with its impact and follow-up trigger.

Accept only when the brief's outcome, required verdicts, and current checks are
satisfied. Partial, empty, or blocked reports remain open under the main
workflow's recovery rule. The parent verifies the integrated result and any
whole-branch review required by the repository before its delivery workflow
can declare completion.
