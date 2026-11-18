---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Each slice respects the repo's PR limits — read them (`AGENTS.md`, `docs/conventions/`, or equivalent) and split any slice whose change would exceed the cap
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

Write every acceptance criterion as **verifiable evidence**: a command that passes, an endpoint that responds, a rendered screen, a query result. "The API works" is not a criterion; "`POST /x` returns 201 with the new field" is.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?
- Does every acceptance criterion read as checkable evidence?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets **in dependency order, blockers first**, so every blocking edge can reference a real identifier.

Publishing is **idempotent**: before creating anything, search existing tickets and tracking issues (or files) for this feature, including completed ones. A matching title is only a candidate: confirm the same parent or feature scope and intended acceptance criteria before reusing or updating it. Preserve completed work; a partial publish resumes from the remaining tickets.

**How** tickets land depends on the tracker `/setup-matt-pocock-skills` configured; the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket.
  - **Parent**: use the source issue when one exists. Otherwise reuse or create a tracking issue when the ticket set needs shared progress tracking or the repository requires one; a small plan can publish standalone tickets.
  - When there is a parent, make each ticket its **sub-issue** (tracker doc's operation). Attaching sub-issues is the **one allowed change to the parent** — otherwise do not close or modify it.
  - Set each ticket's blocking edges as the platform's **native blocking relationship** where it has one; otherwise set each ticket's "Blocked by" body section to the blocking issues.
  - **Labels**: resolve the ready-for-agent role through the configured label mapping (`docs/agents/triage-labels.md`); do not hardcode the label string. Apply it **only to frontier tickets** — those with no open blockers. Blocked tickets are promoted when their last blocker closes.
  - **Assignees**: leave every ticket unassigned. Unassigned + ready means any agent or human may claim it; claiming is assigning yourself, and it is the session's first write.

The **frontier** is the set of tickets that are open, unblocked, and unassigned: the feature's open tickets (the parent's sub-issues when grouped) with zero open blockers (the native `blocked_by` count, or an open entry in the `Blocked by` line) and no assignee. Use the tracker doc's frontier query where it defines one.

A ticket is **done only when it is closed with evidence** — a comment recording what was verified, then the close. Anything less stalls the graph: an open-but-implemented ticket blocks its dependents forever, and a silently closed one cannot be trusted. Whoever works a ticket owns closing it with evidence and promoting its newly-unblocked dependents to ready-for-agent.

Publishing the tickets is this skill's deliverable. Working the frontier belongs to `/implement` (one ticket) and `/implement-spec` (the whole graph).

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the source or tracking issue when tickets are grouped; omit this section for standalone tickets.

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
