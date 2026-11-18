---
name: writing-portable-scripts
description: Use when writing or editing automation that runs unchanged from any checkout — repo scripts, setup and bootstrap scripts, CI helpers, hook handlers, skill-bundled scripts, and CLI utilities — or when a script breaks in a worktree, plugin cache, CI runner, or fresh clone. Not for one-off commands.
---

# Writing portable scripts

A **portable** script runs unchanged from every place it gets packaged into:
the primary checkout, a linked worktree, a runtime projection
(`.claude/skills/<name>` symlink), a plugin cache, a CI runner, a fresh clone
on another machine. It is also **idempotent** (safe to run twice),
**non-interactive** (zero prompts, pagers, or interactive input), and
**isolated** (project dependencies never land globally). Every rule below
serves one of those four words.

## Steps

1. **Decide script or instructions.** A script earns its place only for
   reusable, deterministic, machine-checkable automation with at least one
   real caller (`package.json`, task runner, CI workflow, hook registry,
   Makefile, another script). A procedure the agent can execute directly
   belongs in docs or a skill.
2. **Load the target repo's guidance.** Root and scoped `AGENTS.md` /
   `CLAUDE.md`, `CONTRIBUTING*`, script-directory docs, and the neighbouring
   scripts outrank this skill on placement, headers, shells, and validation
   commands. Discover the repo's own commands: a command from another repo
   (`pnpm gate`, `make ci`) exists only where this repo documents it.
   For packaged lifecycle hooks, read the [hook contract](../../hooks/AGENTS.md)
   and use its native verification procedure; script tests alone do not prove
   installed discovery, trust, or execution.
3. **Anchor every path** per the table below; derive locations, assume none.
4. **Write to the portable baseline.**

   ```bash
   #!/usr/bin/env bash
   # <what this script does and who calls it>
   # usage: <script> [--dry-run] <args>
   set -euo pipefail
   ```

   - Target bash 3.2 (macOS `/bin/bash`): arrays and `[[ ]]` yes; `mapfile`,
     `declare -A`, `${var,,}`, `&>>` no.
   - Quote every expansion: `"${var}"`, `"${dir}/file"`.
   - `${HOME}` not `~`; `python3` not `python`; `command -v` not `which`;
     `printf` not `echo -e`.
   - Flags both BSD and GNU accept: no `grep -P`, `sed -i` without a suffix,
     `date -d`, `find -printf`, `readlink -f`, `cp --parents`.
   - `tmp=$(mktemp -d "${TMPDIR:-/tmp}/<name>.XXXXXX")` with
     `trap 'rm -rf "${tmp}"' EXIT`.
   - Python: `#!/usr/bin/env python3`, standard library only unless the repo
     supplies an isolated environment. Node: `#!/usr/bin/env node`, `.mjs`,
     `node:` built-ins only.
   - Secrets arrive as environment variables the caller injects; the script
     reads them once and keeps them out of arguments, output, and logs.
5. **Run non-interactively and isolated** per the tables below.
6. **Make effects idempotent and visible.** Check tools before use
   (`command -v`), create-if-missing, upsert rather than append, and gate
   destructive actions behind `--yes` with `--dry-run` printing the plan. One
   line per effect to stderr; stdout carries only output another program
   consumes. Exit `0` done, `1` failure, `2` usage.
7. **Run it from a foreign directory.** Run the script once from a temporary
   directory outside the repo with `HOOK_CWD`, `CLAUDE_*`, and `GIT_DIR`
   unset, and once from inside a linked worktree (`git worktree add`). A
   colocated test (`<script>.test.sh`) is optional; add one only when the
   logic is easy to break silently.
8. **Validate.** `bash -n` and `/bin/bash -n` (bash 3.2), `shellcheck -s bash`
   when installed, `node --check` or `python3 -m py_compile` for other
   languages, then the repo's documented gate.

## Anchors

| Need | Derive from | Never from |
|------|-------------|------------|
| The script's own directory (sibling files, `lib/`) | bash `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)`; Python `Path(__file__).resolve().parent`; Node `fileURLToPath(new URL(".", import.meta.url))` | `$PWD`, `$0` under `sh`, a literal repo path |
| The repository being operated on | `git -C "${target}" rev-parse --show-toplevel` with `target` = payload `cwd`, `HOOK_CWD`, or an argument, defaulting to `$PWD` | The script's own directory: a packaged copy may live in `~/.claude/plugins/cache/…` or another repo |
| The skill or plugin bundle | `${CLAUDE_SKILL_DIR:-}`, `${AGENT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}`, falling back to the script's own directory | Assuming the variable is set: tests, other runtimes, and bare shells run the script without it |
| Persistent state | `${AGENT_PLUGIN_DATA}` or `${AGENT_CONFIG_DIR}` for a hook; `git config branch.<name>.<key>` for per-branch state (Git renames and deletes it with the branch, across worktrees) | Files under the worktree or `.git/` by literal path |
| A scratch directory | `mktemp -d "${TMPDIR:-/tmp}/<name>.XXXXXX"` plus `trap … EXIT` | `/tmp/<fixed-name>`: two runs collide |
| The user's home | `${HOME}` | `~` inside quotes, `/Users/<name>` |

### Worktree facts

A linked worktree (`git worktree add`, `wt switch --create`) is a full
checkout sharing one object store with the primary checkout. What changes:

- **`.git` is a file**, not a directory. Test membership with
  `git rev-parse --is-inside-work-tree`, never `[ -d .git ]`.
- **Two git directories.** `git rev-parse --git-dir` is per-worktree (`HEAD`,
  index, `logs/HEAD`); `git rev-parse --git-common-dir` is shared (`config`,
  `hooks/`, `refs/`, stash, objects). Hook paths and repo config come from
  the common dir; HEAD and the index from the git dir.
- **Branch ≠ directory name.** Read it with `git rev-parse --abbrev-ref
  HEAD`; a worktree can be renamed or detached.
- **Default branch ≠ `main`.** Read `git symbolic-ref --short
  refs/remotes/origin/HEAD`, falling back to `git config
  init.defaultBranch`, before comparing against it.
- **Stale `GIT_*` environment leaks across directories.** Before running git
  against a directory other than the caller's, clear `GIT_DIR`,
  `GIT_WORK_TREE`, `GIT_COMMON_DIR`, and `GIT_INDEX_FILE`
  (`env -u GIT_DIR -u GIT_WORK_TREE … git -C "${target}" …`); an inherited
  value silently targets the wrong worktree.
- **Ignored files stay behind.** `node_modules/`, `.venv/`, `.env`, and build
  output do not follow a branch into a new worktree. A bootstrap script is
  safe to run once per worktree and installs into the current worktree,
  never the primary checkout.
- **One primary checkout.** Where `--git-dir` equals `--git-common-dir` the
  checkout is primary; a script that mutates files treats it as protected
  unless the repo says otherwise.
- **Symlink projections.** Runtime directories (`.claude/skills/<name>`)
  link into the canonical owner (`plugins/xan-skills/skills/<name>`);
  `pwd -P` resolves the link so sibling-file reads and edits land in one
  place.

A hook handler receives `cwd` in its JSON payload and `HOOK_CWD` from the
adapter; that is the repository to act on. The handler itself launches from
the session working directory, which may be a different worktree than the one
being edited. The target repository's hook contract names the adapter's
exact variables.

## Non-interactive execution

Assume no TTY: no `read -p` or other stdin read, any "confirm?" variable
defaults to yes, and a missing answer is a non-zero exit, not a question.
Input comes from arguments, environment, files, or a documented runtime
payload such as hook JSON on stdin; a step that genuinely needs a human
(`gcloud auth login`) is handed to the user, not driven.

| Tool | Non-interactive form |
|------|----------------------|
| apt | `DEBIAN_FRONTEND=noninteractive apt-get install -y foo` |
| pip | `pip install --no-input` |
| npm | `npm init -y`, `npm ci` |
| npx | `npx --yes create-foo` |
| git | `git --no-pager <cmd>`, `git commit -m "..."`, `git merge --no-edit`, `git rebase --no-edit` |
| cloud CLIs | JSON output and file or env inputs (`--format=json`, `--quiet`); authentication happens before the script, never inside it |
| terraform | `terraform init -input=false`, `terraform apply -auto-approve` |
| pulumi | `pulumi up --yes`, `pulumi destroy --yes` |
| docker | `docker system prune -f` |
| kubectl | `kubectl delete --wait=false` when blocking is undesirable; `--edit` is never used |
| gh / glab | `--yes` on confirm prompts; body via `--body-file` or `--body` |
| ssh | `-o BatchMode=yes -o StrictHostKeyChecking=accept-new` |

Pagers break agent output and stay off: `git --no-pager`, `GIT_PAGER=cat`;
force `| cat` where a wrapper pages.

## Dependency isolation

Project dependencies install into the language's isolation mechanism, never
globally.

| Language | Isolation | Version pinning | Lock file |
|----------|-----------|-----------------|-----------|
| Python | `python3 -m venv .venv` + `. .venv/bin/activate` (or `uv venv`) | `pyproject.toml` or `requirements.txt` | `requirements.txt` / `uv.lock` / `poetry.lock` |
| JS/TS | Local `node_modules/` (default) | `.nvmrc` + `corepack enable` | `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` |
| Rust | Cargo per-project (default) | `rust-toolchain.toml` | `Cargo.lock` (binaries) |
| Go | `go mod` (default) | go directive in `go.mod` | `go.mod` + `go.sum` |
| Java/JVM | Maven/Gradle per-project | `.sdkmanrc` + `mvnw` / `gradlew` wrappers | `pom.xml` / `build.gradle` lock |
| Ruby | `bundle config set --local path 'vendor/bundle'` | `.ruby-version` | `Gemfile.lock` |

Pin language, package manager, and dependency versions; commit lock files;
gitignore isolation dirs (`.venv/`, `node_modules/`, `vendor/bundle/`,
`target/`); match the same strategy and pins in CI. A `pipx`-installed CLI is
separate tooling, not a project dependency, and still pinned where possible.

## Guardrails

- Tests, CI, scanners, and cleanup gates stay at full strength; the script
  changes to pass them.
- Generated manifests and indexes come from their generator.
- One owner per script: edit the canonical file (`plugins/xan-skills/…`,
  `.codex/…`); a projected symlink is read-only.
