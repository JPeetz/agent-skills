---
name: manual-qa
description: Use when manually testing or dogfooding a working app, service, API, or CLI; reviewing rendered appearance or supplied screenshots; or verifying user-facing implementation changes. Not for automated test authoring, security audits, performance benchmarks, or implementation craft alone.
---

# Manual QA

One entry point for functional checks and visual review. Completion
includes inspected, user-viewable evidence tied to the claims it
supports.

## Select the lane

| Scope | Lane |
| --- | --- |
| Behavior | Functional (sections 1–4) |
| Appearance, including terminal rendering | Visual lane (section 5) |
| Behavior and appearance | Both lanes |
| Supplied screenshots | Visual lane limited to the supplied states |
| Implementation craft alone | Separate `emil-design-eng` skill |
| Unrelated work | No manual QA pass |

A screenshot review works without a runnable target but establishes no
live behavior or uncaptured state. Behavioral defects found during
visual review enter the functional lane when in scope; otherwise report
them uncovered.

## 1. Scope the pass

Identify the target, access, intended behavior, changed surfaces, and
requested stop point from the task and authoritative sources. For a
live target, verify the running version. For supplied captures,
disclose their provenance and unknown capture details, and keep claims
within what the evidence shows.

State scope and observable expectations before execution. Keep design
judgments distinguishable from functional requirements. Review-only
work produces recommendations; the task's authorization governs fixes
and production mutations. Preserve existing user resources and register
task-created resources under section 6.

## 2. Exercise the functional lane

Define happy-path, meaningful-edge, and adjacent-regression scenarios.
Each needs concrete inputs, exact actions, a binary pass condition, and
its real interface; explain inapplicable scenarios. Execute the
scenarios and record reproducible steps and side effects: requests,
persistence, logs, adjacent state. Vary applicable empty/oversized
inputs, special characters, repeated submissions, refresh/navigation,
offline conditions, and permission denial.

Run the required checks for implementation changes and applicable
focused diagnostics; record commands, exit status, and unavailable
checks. These complement real-interface execution.

## 3. Evaluate and recheck

Evaluate declared criteria against evidence. After authorized fixes,
repeat the original reproduction and recapture changed states. Broaden
rechecks only for affected behavior or failures. Label hypotheses
separately from observations.

Use one severity scale:

- **Blocker:** unusable purpose, crash/data loss, unreadable essential
  content, or unreachable controls.
- **Major:** incorrect results, broken handling/state, misleading
  hierarchy, repeated component drift, or severe
  contrast/accessibility barriers.
- **Minor:** nonblocking spacing, rhythm, copy, or rough edges.

## 4. Deliver and close

Present proof, then finish cleanup under section 6. Report:

- Target/version/environment; lanes, screens, states, and breakpoints
  reviewed.
- Each criterion: expected result, actual result, PASS/FAIL/BLOCKED,
  and user-viewable evidence.
- Findings: severity, precise location, expected versus actual,
  reproduction where applicable, suggested fix, and evidence.
- Checks and outcomes; uncovered criteria; evidence-delivery
  limitations; cleanup receipts and retained resources.
- Overall verdict: PASS, PASS WITH FINDINGS, FAIL, or BLOCKED.
  Required untested criteria, unverified proof delivery, or unresolved
  cleanup preclude PASS.

Example criterion: `Invalid email → HTTP 422 | BLOCKED: target
unavailable | Evidence: none` — records a gap without turning an
expectation into an observed result.

## 5. Visual lane

List screens, states, themes, and breakpoints before reviewing. Obtain
at least one full-screen contextual capture per scoped state, recording
method and dimensions; prefer desktop and mobile widths, with
supplementary crops for details. For supplied captures, review the
available states and disclose missing coverage; a missing live target
does not block critique of visible evidence.

Record a brief first impression per state, then inspect:

- Structure, hierarchy, alignment, spacing, and rhythm.
- Brand references, design tokens, and component consistency.
- Typography, readability, color, and contrast.
- Interaction affordances, visible focus, and reachable controls.
- Responsive layouts, themes, clipping, and overlap.
- Content clarity and visible accessibility issues.
- Motion and state transitions when relevant and evidenced.

Report each finding by screen/state and precise element with evidence
and a concrete suggested fix. After authorized fixes, recapture the
changed states and recheck the original findings; improvement claims
follow section 6.

## 6. Evidence contract

Prove each criterion through its actual interface:

| Criterion | Evidence channel |
| --- | --- |
| HTTP contract | HTTP client: status, relevant headers, safe response fields |
| Browser behavior | Real browser: reproducible actions and screenshots |
| Desktop behavior | Running app: supported computer-use tools, actions and screenshots |
| Terminal interaction | Real PTY: transcript and observed result |
| Terminal appearance | Real terminal renderer or browser-rendered xterm.js: screenshots |
| CLI or data state | Command result or state comparison |

Plain terminal output cannot prove color, layout, or wide-glyph
rendering. A dry run proves only dry-run behavior. A still image cannot
prove motion or completion of an interactive workflow.

Record actual results, PASS/FAIL/BLOCKED, capture method, dimensions
where relevant, target version, environment, and evidence location in
the task evidence directory. Visual proof shows real product chrome and
the surface being assessed with enough surrounding UI for context;
captions, white-canvas mocks, source code, and successful builds are
not visual proof. Do not capture credentials or private data; use
isolated test state for storage resets or setting changes. Production
mutations and destructive actions require the task's explicit
authorization.

For improvement claims, capture before and after at matching viewport,
theme, data, UI state, and capture method, and present the paired
artifacts. An after-only capture proves current appearance, not
improvement; disclose absent baselines.

Present artifacts through the runtime's supported attachment, embed, or
accessible-link mechanism; a bare filesystem path or description is not
delivery. Inspect the artifact at the delivered destination, not merely
its source: open the exact delivered URL for hosted files, and verify
actual playback and `video/mp4` delivery for video. Publishing private
evidence publicly requires authorization, and agent access does not
establish access for the user's account — disclose audience
restrictions. If access, rendering, delivery, or playback cannot be
verified, mark the affected proof BLOCKED.

Register task-created processes, ports, browser sessions, simulators,
containers, temporary files, and test data. Clean up only those within
authorized scope and record a receipt for each; deleting user or shared
data needs explicit approval. Preserve delivered evidence separately
from disposable test resources. Report retained resources and reasons,
pending cleanup, and untested criteria — unresolved cleanup prevents
completion.
