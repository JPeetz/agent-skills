---
name: clonedeps
description: "Not for ordinary API or docs questions (use librarian). Clone dependency source repos into an ignored local workspace so agents can inspect library internals from source."
---

# Clonedeps Skill

You help users make a small set of important dependency source repositories
locally readable to agents.

This is a workflow skill, not a command wrapper. Do not use a helper script for
dependency detection, ref validation, cloning, status, or cleanup. The main
session (the `orchestrator`) and the `librarian` do the repo-specific thinking;
the main session performs the approved filesystem and git operations directly.

## Workflow

### Step 1: Check Existing State

First check whether `.slim/clonedeps.json` exists.

If it exists:

1. Read it before asking librarian for a new plan.
2. Check whether each listed `path` exists under `.slim/clonedeps/repos/`.
3. Reuse existing cloned repos when they already satisfy the user's task.
4. Only ask librarian for new recommendations if the existing manifest is
   missing, stale, or insufficient for the current task.

### Step 2: Ask Librarian for the Clone Plan

Gather the repository facts yourself, or through `explorer` for an unfamiliar
tree: what the project does, its main architecture and integration points, and
the dependency manifests with declared versions. The `librarian` researches
remote sources only, so hand it those facts.

Use this prompt, with the facts filled in:

```md
Here is a project a developer needs to debug and extend:

<what it does, main architecture, integration points>
<dependency manifest excerpts with declared versions>

Which remote source repositories, if cloned locally, would help most? Recommend
a repo only when its source would be more useful than its docs or this project
alone. Most dependencies are not worth cloning; recommend 0–3, and say so if
none clearly helps.

For each recommendation, give:
- dependency name and the version or range in use
- official source repository URL (HTTPS)
- tag, commit, or ref matching that version
- package subdirectory when the source is a monorepo
- why local source helps, and when
- caveats: huge repo, missing tag, uncertain version mapping

Also list the dependencies you considered and would not clone.
```

Include user-mentioned dependencies and central frameworks, SDKs, ORMs,
runtime or plugin APIs, and build tools. Leave out tiny utilities, transitive
dependencies, and dev-only tools unless the active task needs them.

### Step 3: Verify and Confirm the Plan

The main session owns final approval. Before cloning:

1. Prefer pinned tags or commit SHAs. If no exact tag exists, ask librarian to
   find the correct module-specific tag/commit or explain the fallback.
2. Only use HTTPS GitHub/GitLab-style repository URLs by default. Flag
   `file://` URLs, SSH URLs, local paths, URLs with embedded credentials, and
   private or auth-required repositories for explicit user approval.
3. Present the plan to the user with dependency, repo URL, ref, reason, and
   caveats. Plain public HTTPS clones proceed under this invocation's
   authority; only the flagged cases wait for approval before cloning.

### Step 4: Update `.gitignore`

Before cloning artifacts, inspect `.gitignore`. Update the managed block in
place when present; otherwise append it. Add only the missing exact lines
below, never duplicate entries or modify unrelated rules. The block keeps
cloned artifacts git-local.

```gitignore
# BEGIN oh-my-opencode-slim clonedeps
.slim/clonedeps/repos/
# END oh-my-opencode-slim clonedeps
```

Do not write `.ignore` allowlist blocks; remove a legacy clonedeps block from
`.ignore` when one is present.

### Step 5: Clone Sources Manually

Create one folder per source repository under:

```text
.slim/clonedeps/repos/<safe-repo-name>/
```

Derive the safe name from the repository owner/name, not the package name —
`https://github.com/opencode-ai/opencode.git` becomes `opencode-ai__opencode`:
join owner and name with `__`, strip any `.git` suffix, and replace remaining
unsafe path characters with `_`.

If multiple packages come from the same monorepo, clone the repository once and
point each manifest entry at the same repo path with different `packagePath`
values as needed. Do not create ecosystem folders, per-package clone folders, or
per-version folders. If two different source repositories normalize to the same
safe name, disambiguate manually and record the chosen path in
`.slim/clonedeps.json`.

Clone/fetch with normal git commands. For an existing clone, first verify that
`git remote get-url origin` matches the approved repo URL. If it does not match,
stop and ask whether to clean/reclone.

Safe manual git pattern:

1. `git ls-remote <repoUrl> <ref>` to verify the ref where practical.
2. Clone without submodules/recursive behavior.
3. Prefer shallow fetch/clone where practical.
4. Clone into a temporary directory under `.slim/clonedeps/repos/`, then move it
   into the final safe-name path after checkout succeeds.
5. Remove failed temporary clones.

Do not run dependency install/build/test scripts from cloned repositories.

### Step 6: Write Local State

Write `.slim/clonedeps.json` so future agents know what exists:

```json
{
  "version": "1.0.0",
  "updatedAt": "2026-05-12T00:00:00.000Z",
  "dependencies": [
    {
      "name": "@opencode-ai/plugin",
      "resolvedVersion": "1.3.17",
      "repoUrl": "https://github.com/opencode-ai/opencode.git",
      "ref": "v1.3.17",
      "path": ".slim/clonedeps/repos/opencode-ai__opencode",
      "packagePath": "packages/plugin",
      "reason": "Plugin API source used by the project"
    },
    {
      "name": "@opencode-ai/sdk",
      "resolvedVersion": "1.3.17",
      "repoUrl": "https://github.com/opencode-ai/opencode.git",
      "ref": "v1.3.17",
      "path": ".slim/clonedeps/repos/opencode-ai__opencode",
      "packagePath": "packages/sdk/js",
      "reason": "Core SDK source used to inspect runtime behavior"
    }
  ]
}
```

If a clone fails after earlier clones succeeded, still write state for the
successful clones so future inspection is not misleading.

Do not add `.slim/clonedeps.json` to `.gitignore`. It is small, reviewable
project metadata that can be committed. Only the cloned repository contents
under `.slim/clonedeps/repos/` should be ignored.

### Step 7: Register Dependency Source in AGENTS.md

After successful cloning, update the repository root `AGENTS.md` so future
agents know why the dependency source exists and where to look.

If `AGENTS.md` already has a `## Cloned Dependency Source` section, update that
section. Otherwise append this section:

Use this format and list the actual repos directly. Keep each item to one short
sentence so future agents do not need an extra read just to know what is there:

```markdown
## Cloned Dependency Source

Read-only dependency source repositories are available under
`.slim/clonedeps/repos/` for inspection. Do not edit these clones.

- `.slim/clonedeps/repos/<safe-name>/` - `<repo>` at `<ref>`; <one sentence on
  why this source is useful>.
- `.slim/clonedeps/repos/<safe-name-2>/` - `<repo>` at `<ref>`; <one sentence on
  why this source is useful>.
```

Also keep `.slim/clonedeps.json` updated as the structured manifest, but do not
make agents read it for the basic repo list.

## Cleanup

When the user asks to clean cloned dependencies, remove:

- `.slim/clonedeps/repos/`
- the managed clonedeps marker block from `.gitignore`, plus any legacy block
  in `.ignore`

Ask before removing `.slim/clonedeps.json` or the `AGENTS.md` section because
they may be intentional project metadata.
