---
name: linear-project-management
description: Use when driving Linear projects and issues from an agent.
version: 1.0.0
license: MIT
author: Skill Foundry
platforms:
  - linux
  - macos
  - windows
metadata:
  tags:
    - linear
    - project-management
    - issue-tracking
    - graphql
    - mcp
    - ticketing
  complexity_priority: intermediate
  managed_workflows:
    - creating_issue
    - updating_project
    - discovering_before_create
    - bulk_sync
    - label_taxonomy
---

# Linear Project Management

Drive Linear (linear.app) from an agent: create and update issues, projects,
and teams; route work with a label taxonomy; and keep workflows aligned with
code changes. It is designed for agents using the official Linear MCP server
for simple operations and the Linear GraphQL API for anything more advanced.

Two ground rules save most of the pain: **always discover before you create**
(Linear accumulates duplicates fast) and **know the difference between
`description` and `content`** on a project. This skill encodes both.

## When to Use

Use this skill when you want to:

- Create or update a Linear issue, project, or initiative.
- Check for an existing issue/project before making a duplicate.
- Classify and label issues consistently across a team.
- Move issues through workflow states, or bulk-sync a sprint to Done.
- Attach a resource link or milestone to a project.

**Don't use for:** non-Linear ticketing, or when the data model difference
(`description` vs `content`) does not matter — that is exactly when you should
use it, but if you are only reading one status value, a quick GraphQL query is
enough.

## Prerequisites

- **Linear access token** (starts `lin_api_`... ) exposed as the environment
  variable `LINEAR_ACCESS_TOKEN`. Generate at Linear → Settings → Security &
  access → Personal API keys. Never hardcode it in files or commits.
- **Official Linear MCP server** (recommended for simple ops) wired with the
  same token:
  ```json
  {"mcpServers": {"linear": {"command": "npx", "args": ["mcp-remote", "https://mcp.linear.app/sse"], "env": {"LINEAR_API_KEY": "{token}"}}}}
  ```
  Prefer `mcp.linear.app`; avoid deprecated community servers.
- Node.js >= 20 only if you use the `@linear/sdk`/scripts path (optional).

## How to Run

Simple operation via MCP:

```
Create a high priority bug titled "Fix auth timeout" in the ENG team.
```

Discovery before create (mandatory):

```
Search Linear for any existing project matching "checkout-redesign" before creating one.
```

GraphQL for advanced/authoritative access — run the query through your agent's
GraphQL tool with the Linear endpoint (`https://api.linear.app/graphql`) and
`Authorization: {LINEAR_ACCESS_TOKEN}` header.

## Quick Reference

| Operation | Approach |
|-----------|----------|
| Create/update issue | MCP, or GraphQL `issueCreate`/`issueUpdate` |
| Create project | GraphQL `projectCreate` (set both description + content) |
| Find duplicates first | GraphQL `issues`/`projects` search by title/keyword |
| List statuses | GraphQL `projectStatuses { nodes { id name } }` |
| Milestone | `projectMilestoneCreate` |
| Resource link | `entityExternalLinkCreate` |
| Bulk state change | `issueUpdate` loop, or `@linear/sdk` script |

## Procedure

1. **Discover before create.** Before any new issue/project, search Linear by
   title keywords and fail fast if a match exists, then propose an update
   instead. Completion criterion: a search ran and returned either an existing
   match (handled) or a confirmed empty result.
2. **Pick the write path.** Simple = MCP. Authoritative/multi-field = GraphQL.
   Completion criterion: one path is chosen and the payload is mapped to the
   chosen shape's fields.
3. **Set both content fields on projects.** `description` (≤255 chars, shows in
   list views) and `content` (unlimited, shows in the main detail panel). If you
   set only one, half the interface is blank. Stop and fill both.
   Completion criterion: both fields populated for projects/initiatives.
4. **Assign labels by taxonomy.** Choose exactly one Type (`feature`, `bug`,
   `refactor`, `chore`, `spike`); 1-2 Domain tags (e.g. `security`, `backend`,
   `frontend`, `testing`, `infrastructure`); 0-2 Scope tags (`blocked`,
   `breaking-change`, `tech-debt`, `needs-split`, `good-first-issue`).
   Completion criterion: the issue carries one Type and at most 2+1 domain/scope.
5. **Resolve states against workspace statuses.** Status UUIDs are
   workspace-specific — query `projectStatuses` first, never hardcode an ID.
   Completion criterion: status IDs were fetched, not assumed.
6. **If bulk-syncing a sprint:** batch `issueUpdate` to Done and update the
   project, then verify a sample. Completion criterion: at least 2 issues
   verified as Done after the run.

## Pitfalls

- **Duplicate issues.** The number-one failure. Always search before create.
- **`description` vs `content`.** Set both; one without the other renders blank.
- **Hardcoded status UUIDs.** They are workspace-specific. Always query.
- **Hardcoded API token.** Keep it in `LINEAR_ACCESS_TOKEN`, never in the skill,
  an issue body, or a repo.
- **Unchecked codebase scope.** Issue text describing "missing" features may
  already be implemented — verify the codebase before re-implementing.

## Verification

- [ ] Creating an issue returns its ID and the matching label Type.
- [ ] A project create carries non-empty `description` AND `content`.
- [ ] A "find duplicates" query returns the pre-existing issue when it exists.
- [ ] Status IDs come from `projectStatuses`, not a constant.
- [ ] No call in the transcript echoes or writes the raw token.