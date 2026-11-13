---
name: skill-portability-and-packaging
description: Use this skill when packaging or porting agent skills.
version: "1.0.0"
author: "@artisan"
license: MIT
platforms:
  - claude-code
  - openclaw
  - cursor
  - codex
  - opencode
  - gemini-cli
permissions:
  - files.read
  - files.write
metadata:
  category: skill-development
  tags:
    - agent-skills
    - packaging
    - portability
    - cross-platform
    - marketplace
    - skill-distribution
    - install-verification
  related_skills:
    - agent-skills-creator
    - skill-lifecycle-foundry
    - skill-miner
  spec_version: "1.0"
---

# Skill Portability and Packaging

A `SKILL.md` that works on your machine is a document. A `SKILL.md` that loads,
triggers, and behaves identically on Claude Code, Codex, Cursor, OpenCode, Gemini
CLI, Copilot, Windsurf, and OpenClaw is a *product*. This skill covers the last mile:
conforming to the spec's hard rules, choosing the right install root per host,
budgeting the description for routers that truncate it, packaging as a plugin or a
CLI-installable repo, removing the hazards that break on someone else's machine, and
proving that the copy the host loaded is the copy you edited.

It is deliberately mechanical. Packaging failures are almost never creative
failures — they are a name that does not match its folder, a description whose
trigger words fall past a truncation boundary, an absolute path, a tool name only
one host understands, or a stale duplicate in a higher-precedence directory.

## When to Use

Use this skill when you are:

- Shipping a finished skill from a private workspace into a public repo, registry,
  or marketplace.
- Porting one skill to a second or third host and need to know where the files go
  and what silently changes.
- Converting loose skills into a Claude Code plugin, a `marketplace.json`
  collection, or an `npx skills add`-able repo.
- Debugging "I installed it and it does nothing", "it triggers on the wrong
  things", or "my edit didn't take effect".
- Reviewing a third-party skill before installing it on a machine you care about.

**Don't use for:** authoring the content of a skill from scratch (use
`agent-skills-creator`), deciding whether a workflow deserves to be a skill
(`skill-lifecycle-foundry`), or writing plugin logic (hooks, MCP servers, agents)
beyond the packaging shell that carries skills.

## Canonical Layout and the Spec's Hard Rules

One skill = one directory whose basename is the skill name. Everything else is
optional and sits beside `SKILL.md`, never inside a hidden subfolder:

```
skill-name/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # optional: executable code
├── references/       # optional: docs loaded on demand
├── assets/           # optional: templates, data files
├── evals/evals.json  # repo convention (not spec): grading scenarios
├── LICENSE
└── CHANGELOG.md
```

Hard rules — a violation is a load failure, not a style nit:

| Rule | Constraint | Failure mode |
|---|---|---|
| `name` length | 1–64 characters | Rejected by strict loaders |
| `name` charset | `a-z`, `0-9`, `-` only | Uppercase or `_` breaks discovery |
| `name` edges | no leading/trailing `-`, no `--` | Rejected |
| `name` vs. folder | must equal the parent directory name | Skill loads under the wrong key or not at all |
| `description` | 1–1024 characters, non-empty | Missing = no routing at all |
| `metadata` | map of string → string | Nested objects/lists get dropped by some parsers |
| `compatibility` | ≤500 characters, only if needed | Over-budget text is ignored |

Soft rules that matter in practice: body under 500 lines and under ~5000 tokens
(the whole body loads on activation), frontmatter under ~100 tokens (it loads for
*every* skill at startup), and file references one level deep from `SKILL.md`.
Deep reference chains cost context on every hop.

Quoting `version: "1.0.0"` matters: unquoted `1.0.0` is a valid string but
unquoted `1.0` parses as a float and `0.10` becomes `0.1` — a silent downgrade in
any tool that compares versions.

## Prerequisites

- Read access to the skill source directory and to each target host's skills root.
- Write access to the skill directory (this skill edits files; that is the whole
  `files.write` permission).
- A shell for `sha256sum`/`shasum`, `find`, and host CLIs (`npx skills`,
  `claude plugin`, `openclaw skills`).
- Knowledge of which hosts the skill must actually support. Do not package for
  eight hosts when the user runs two — every extra root is another stale copy to
  chase later.
- Upstream specs and host docs are collected in
  [references/sources.md](references/sources.md); re-check exact paths and CLI
  flags there before relying on one.

## How to Run

Name the packaging operation, for example:

```
Package this skill for the repo and make it installable with npx skills add.
```
```
Port this Claude Code skill to Codex and Cursor without forking the content.
```
```
I copied the skill into ~/.claude/skills and it still triggers the old text. Fix it.
```

Then follow the procedure below. The run is: validate the shape, place it, budget
the description, pick the packaging route, sweep hazards, verify the loaded copy.

## Quick Reference

| Need | Command / fact |
|---|---|
| Validate shape | `python3 scripts/validate_skill.py <skills-dir>` (repo) or `skills-ref validate <dir>` |
| Pre-flight package | `python3 scripts/check_package.py <skill-dir>` — name/folder, budget, secret and absolute-path sweep |
| Install from repo | `npx skills add owner/repo` (`-g` global, `-a claude-code`, `-s name`, `--copy`) |
| List what is installed | `npx skills list` · `claude plugin list` · `openclaw skills list` |
| Update installed | `npx skills update` |
| Plugin manifest | `<plugin>/.claude-plugin/plugin.json` — *only* that file in the hidden dir |
| Marketplace index | `.claude-plugin/marketplace.json` at repo root (`name`, `owner`, `plugins[]`) |
| Plugin skill invocation | `/plugin-name:skill-name` |
| Canonical cross-host root | `~/.agents/skills/` (Codex, Antigravity, OpenClaw personal) |
| Prove loaded == edited | `sha256sum` source vs. resolved host path |

## Host Matrix

Project-relative root for a checked-in skill, global root for a per-user install.
Where two roots exist, the project copy usually wins — which is exactly how a
stale project copy shadows a fresh global one.

| Host | Project root | Global root |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` (older setups: `.codex/skills/`) | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| OpenClaw | `<workspace>/skills/`, `.agents/skills/` | `~/.agents/skills/`, `~/.openclaw/skills/` |
| Hermes | profile `skills/` dir | `~/.hermes/profiles/<name>/skills/` |

OpenClaw has the deepest root list and a defined precedence: workspace `skills/`
(highest) → project `.agents/skills` → personal `~/.agents/skills` → managed
`~/.openclaw/skills` → workshop skills → bundled → `skills.load.extraDirs`
(lowest). OpenClaw also skips a symlinked skill that resolves outside its root
unless the target is declared in `skills.load.allowSymlinkTargets` — the single
most common reason a symlinked skill "installs" but never appears.

Two layout notes that break nervous readers' assumptions:

- **Hosts name by frontmatter, not path.** OpenClaw keeps the skill name from
  `SKILL.md` even when the folder is nested (`skills/personal/hello-world/`).
  Most other hosts key on the directory basename, which is why `name` must equal
  the folder. Nesting is therefore safe on OpenClaw and risky elsewhere.
- **Symlink vs. copy.** Symlink keeps one source of truth and makes edits
  instant; copy survives hosts that resolve symlinks badly or sandboxes that
  cannot follow them. If the user edits the *installed* copy, a symlink layout
  means they just edited the source — say so explicitly.

## Description Budgeting

The description is a routing table entry, not marketing copy. It is the only text
present before activation, so every character must earn a trigger.

1. **Write the triggers first.** List the phrases a user actually types ("port
   this skill", "marketplace.json", "install fails", "nothing happens").
2. **Open with the trigger clause.** `Use when …` as the first words survives
   truncation; a value proposition first ("A comprehensive framework for…") dies
   mid-word in every list view.
3. **Budget by host.** The spec allows 1024 characters, but several hosts and
   registry UIs truncate far earlier for display and some routers only embed the
   first sentence. Target ≤60 characters for a repo-quality description, ≤160 for
   a keyword-rich one, and never *depend* on text past ~200 characters.
4. **Trim the tail, not the head.** If a description must shrink, delete
   synonyms and qualifiers from the end; never move the trigger verb out of
   position one.
5. **One skill, one job.** A description with two "and also"s is two skills. Split
   it, because overlapping triggers mean the router picks arbitrarily.

Smell test: if you cannot name three user sentences the description matches, it
is not a routing trigger yet.

## Plugin and Manifest Packaging

Three distribution routes, in increasing ceremony:

**1. Loose skill in a repo** — `skills/<category>/<name>/SKILL.md` plus LICENSE,
CHANGELOG, evals, references. Installable with
`npx skills add owner/repo --skill name`, or by copying into any host root from
the matrix. Lowest ceremony, widest compatibility, no invocation prefix.

**2. Plugin** — a directory with a manifest at `.claude-plugin/plugin.json` and
sibling component dirs at the root:

```
my-plugin/
├── .claude-plugin/plugin.json   # name, version, description — ONLY this file here
├── skills/<name>/SKILL.md
├── agents/
├── hooks/hooks.json
└── .mcp.json
```

Putting `skills/` or `hooks/` *inside* `.claude-plugin/` is the classic structural
error: components then fail to load silently. Plugin skills invoke as
`/plugin-name:skill-name`, which is the correct choice when two plugins might ship
the same skill name, and a needless namespace for a single personal skill.

**3. Marketplace** — `.claude-plugin/marketplace.json` at the repo root:

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Joerg Peetz" },
  "plugins": [
    { "name": "skill-pack", "source": "./plugins/skill-pack", "version": "1.0.0" }
  ]
}
```

`name`, `owner`, and `plugins[]` are required; each entry needs `name` and a
`source` path relative to the marketplace root, with no `..` segments. Install is
`plugin-name@marketplace-name`. The entry `name` is the install id; the manifest
`name` is the skill prefix. Keep them equal unless you have a reason.

For skill collections, prefer route 1 and let `npx skills add` handle host
placement (it symlinks a canonical copy into each agent dir, or `--copy` when
symlinks are unavailable). Reserve plugins for skills that need hooks, agents, or
MCP servers to work.

## Portability Hazards

Sweep for these before publishing; each one is invisible on the author's machine.

- **Absolute paths.** `/Users/<user>/...`, `/home/<user>/...`, `C:\Users\...` break
  everywhere. Use paths relative to the skill root, `$HOME`/`~`, `$PROJECT_ROOT`,
  or OpenClaw's `{baseDir}` placeholder.
- **Host-specific tool names.** Claude Code says `Read`/`Write`/`Bash`; Hermes says
  `read_file`/`write_file`/`terminal`; OpenClaw says `exec`. Describe the *action*
  ("read the file", "run the validator") and let the host map it, or list names as
  examples with "or your host's equivalent".
- **Script interpreters.** `python` is absent on many macOS/Linux images where
  only `python3` exists; `bash` is not `zsh`; Windows has no `sh` guarantee. Use
  `#!/usr/bin/env python3`, stdlib only, and no `uv`/`pip install` at run time
  unless `compatibility` says so.
- **Frontmatter dialects.** OpenClaw-specific keys (`user-invocable`,
  `command-dispatch`, `requires.bins`) are inert elsewhere — harmless but
  misleading if you imply portability. Everything non-standard belongs under
  `metadata`.
- **Permissions and modes.** Executable bits, symlinks, and CRLF line endings
  survive git but not zip/archive round-trips. Ship `scripts/` with documented
  invocations (`python3 scripts/x.py`) rather than relying on `./x.py`.
- **Case sensitivity.** macOS is case-insensitive; Linux CI is not. `Scripts/` vs
  `scripts/` works locally and 404s in CI.
- **Name collisions and precedence.** A same-named skill in a higher-precedence
  root wins. Before debugging content, confirm which copy actually loaded.
- **Size limits.** Download/extract caps (e.g. 10 MiB download, 25 MiB extracted,
  1000 files in `npx skills`) reject vendored datasets and model weights. Ship a
  fetch step, not a blob.

## Install Verification Loop

Installing is not verifying. Close the loop every time:

1. **Hash the source.** `shasum -a 256 <source>/SKILL.md`.
2. **Resolve the loaded path.** Ask the host, don't assume: `npx skills list`,
   `claude plugin list`, `openclaw skills list`, or the host's skills inventory.
3. **Hash the loaded file.** If it is a symlink, hash the resolved target
   (`shasum -a 256 -L`). Identical hash = the loaded copy *is* the edited copy.
4. **Check for shadowing.** `find <each root> -name SKILL.md -path '*<name>*'` —
   more than one hit is a precedence bug waiting to happen.
5. **Restart the session.** Most hosts cache the skill list at startup; a gateway
   restart or `/new` is required before new frontmatter is visible.
6. **Fire a real trigger.** Phrase the request the way a user would and confirm
   the skill activates — not the name, the *trigger sentence*.
7. **Run the payload.** Execute one script or one reference read to prove paths
   inside the skill resolve from the installed location.

If step 3 mismatches, stop: you are debugging the wrong file. If step 6 fails
while step 3 passes, the problem is the description, not the install.

## Security Packaging Rules

- **No secrets in the package.** No tokens, keys, cookies, internal hostnames, or
  customer data — including in examples and `references/`. Sweep before publish;
  a leaked key cannot be unpublished.
- **Minimum permissions.** Declare only the file/network access the skill needs.
  Blanket tool grants (`allowed-tools: *`, equivalent to shell-everything) turn a
  helpful skill into a remote code execution surface.
- **No install-time execution.** Skills should not need `postinstall` hooks or
  download-and-run bootstrap scripts. If a setup step is unavoidable, make it
  explicit, reviewed, and version-pinned.
- **Pin and checksum third-party sources.** Reference commits or tags, not
  branches, and record archive hashes. A skill that silently pulls `main`
  changes behavior without a version bump.
- **Review before installing someone else's skill.** Skills are instructions the
  agent will follow — treat a downloaded skill as untrusted code, read the body
  and every `scripts/` file, and check for prompt-injection and exfiltration
  patterns before it lands in a root the agent trusts.
- **Keep attribution and license.** Preserve upstream `LICENSE` and author
  metadata when forking; `license` in frontmatter plus a bundled `LICENSE` file.

## Pitfalls

- **`name` ≠ folder.** Works until the host keys on the directory and the skill
  never appears. Rename one or the other; never leave them divergent.
- **Description written as a summary.** "A framework for portable skills" routes
  nothing; "Use when packaging or porting skills across agent hosts" routes.
- **Publishing from the working copy.** Uncommitted edits, stray `.DS_Store`,
  `__pycache__`, and local scratch files ride along. Package from a clean tree.
- **Assuming one root.** Installing into `~/.claude/skills` and also `.claude/skills`
  produces two divergent copies and an unreproducible bug report.
- **Symlink surprises.** A symlinked skill outside the OpenClaw root is skipped
  silently; a copied skill stops tracking source edits. Choose deliberately.
- **Editing the installed copy.** Fine on purpose, fatal by accident — the next
  `npx skills update` overwrites it. Edit the source, then reinstall.
- **Plugin components inside `.claude-plugin/`.** Only `plugin.json` lives there;
  everything else is a root-level sibling.
- **Testing on the author's host only.** Trigger phrasing and path handling differ
  per host; portability claims need at least two hosts exercised.

## Verification

Before calling a package shipped:

- `name` matches the directory, is ≤64 chars, lowercase-hyphenated, no `--`.
- `description` ≤60 chars in repo convention (hard cap 1024), opens with a trigger
  clause, and the top three user phrases appear in the first 160 characters.
- Frontmatter parses as YAML; `metadata` values are scalars; `version` is quoted.
- Body is under 500 lines and contains no absolute user paths, no secret patterns,
  and no host-only tool names presented as universal.
- `LICENSE`, `CHANGELOG.md`, `evals/evals.json`, and `references/` sit beside
  `SKILL.md`; every `references/` file is linked from the body.
- The repo validator prints `"valid": true` with an empty `issues` list.
- Evidence exists for the install loop: source hash, resolved loaded path, matching
  hash, single copy found across roots, and one real trigger fired post-restart.
