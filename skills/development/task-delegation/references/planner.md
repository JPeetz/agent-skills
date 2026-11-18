# Planner

## Select the shape

Choose the smallest arrangement likely to finish sooner at the required quality:

| Work | Arrangement |
| --- | --- |
| Small edit, one decision chain, or one external dependency | Work directly |
| Distinct searches, hypotheses, components, or review areas | Independent parallel lanes |
| More uniform items than one context can coordinate, per-item verification the plan must enforce, or an orchestration worth re-running | Host script workflow (the `Workflow` tool on Claude Code) when the host provides one |
| Workers need sustained discussion to settle an interface or evidence | Collaborating team, when supported |
| A large workstream has its own independent integration problem | Subplanner within the shared budget |

Prefer complete, bounded slices over many microtasks. A numbered list does not make independent tasks sequential. Parallel work should save elapsed time after briefing, contention, and integration are counted; it may consume more tokens. A script workflow moves the plan from context into code: verification runs because the script sequences it and only the final result returns to the parent, at a materially higher token cost than turn-by-turn dispatch.

## Brief each lane

Use the canonical [lane contract](../SKILL.md#lane-contract). Pass the minimum context needed to work independently; give reviewers original artifacts rather than an author's conclusion disguised as fact. Give collaborators relevant sibling contracts, and keep the parent as the user's contact. A bounded worker needs enough context to finish; a judgment-heavy worker needs the goal and constraints without scripted reasoning. An example helps with a subtle format or edge case.

## Track and adapt

Use [Graph workflow](graph-workflow.md) for task records, readiness, acceptance evidence, and review gates. Keep tiny or serial tasks direct. Avoid a new ledger unless it serves a real resumption need.

Use [Teams](teams.md) to coordinate shared writes and task claims. Confirm an uncertain writer has stopped and reconcile its partial edits before reassigning its scope. A worktree isolates writes but does not eliminate integration conflicts or active operation ownership.
