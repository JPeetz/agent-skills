---
name: git-workflow-automation
description: >
  Expert Git workflow automation for commit message generation, branch naming,
  PR description writing, changelog generation, merge conflict resolution,
  and release management. Activates when users say "write a commit message",
  "create a PR", "generate changelog", "branch name for", "resolve merge
  conflict", "cut a release", "bump version", "semantic version", or
  "conventional commits". Enforces Conventional Commits, semantic versioning,
  and reproducible Git workflows across teams.
version: 1.0.0
author: Skill Foundry
license: MIT
compatibility: >
  Cross-platform: Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Windsurf,
  Gemini CLI, OpenClaw, Hermes Agent, and any SKILL.md-compatible agent.
tags:
  - git
  - version-control
  - conventional-commits
  - changelog
  - release-management
  - semantic-versioning
  - automation
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
---

# Git Workflow Automation

Automate Git operations with battle-tested conventions. Every commit, PR, changelog,
and release follows reproducible standards that scale across teams and enable full
CI/CD automation.

## Role

You are a Git workflow expert. You enforce consistency through Convention over
Configuration, enabling teams to automate changelogs, versioning, and releases.

## Core Conventions

### Conventional Commits (Strict Enforcement)

```
<type>[optional-scope]: <description>

[optional body]

[optional footer]
```

**Types and their effects:**

| Type | SemVer Bump | Changelog Section | When to Use |
|------|-------------|-------------------|-------------|
| `feat` | MINOR | Added | New feature |
| `fix` | PATCH | Fixed | Bug fix |
| `docs` | NONE | — | Documentation only |
| `style` | NONE | — | Formatting, whitespace |
| `refactor` | NONE | — | Code change, no feature/fix |
| `perf` | PATCH | Performance | Performance improvement |
| `test` | NONE | — | Adding/updating tests |
| `build` | PATCH* | — | Build system, dependencies |
| `ci` | NONE | — | CI configuration |
| `chore` | NONE | — | Maintenance tasks |
| `revert` | PATCH | — | Reverting a commit |

\* `build` bumps PATCH only if dependency change is user-facing.

**Breaking changes:** Add `!` after type/scope and `BREAKING CHANGE:` footer.
- `feat!: drop support for Node 16` → MAJOR bump
- `feat(api)!: remove deprecated /v1 endpoint` → MAJOR bump

### Commit Message Quality Rules

1. **Imperative mood:** "Add feature" not "Added feature" or "Adds feature"
2. **No period at end** of subject line
3. **Subject ≤ 72 characters**
4. **Body explains WHAT and WHY**, not HOW
5. **Every commit is atomic** — one logical change
6. **Reference issues:** `Closes #123` or `Refs #456` in footer
7. **Co-authored-by** for pair/mob programming

### Branch Naming Convention

```
<type>/<ticket>-<short-description>
```

| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Feature | `feat/TICKET-123-add-oauth` | `feat/PROJ-42-user-auth` |
| Bug fix | `fix/TICKET-456-null-check` | `fix/PROJ-99-login-redirect` |
| Chore | `chore/update-deps` | `chore/eslint-v9-migration` |
| Release | `release/v1.2.0` | `release/v2.0.0` |
| Hotfix | `hotfix/v1.1.1-crash` | `hotfix/v1.2.1-memory-leak` |

### PR Description Template

Generate PR descriptions with this structure:

```markdown
## Summary
[One sentence explaining what this PR does]

## Motivation
[Why this change is needed — link to issue/discussion]

## Changes
- [List of key changes, one per bullet]
- [Breaking changes highlighted with ⚠️]

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing steps performed

## Screenshots (if UI)
[Before/After screenshots]

## Checklist
- [ ] Code follows project conventions
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

Closes #[ISSUE_NUMBER]
```

## Changelog Generation

Generate changelogs from commit history following Keep a Changelog format:

```markdown
# Changelog
All notable changes to this project will be documented in this file.

## [VERSION] — YYYY-MM-DD

### Added
- [feat commits with descriptions]

### Changed
- [breaking changes, deprecations]

### Fixed
- [fix commits with descriptions]

### Security
- [security-related fixes]

### Performance
- [perf commits with descriptions]
```

**Generation process:**
1. `git log --oneline <last-tag>..HEAD`
2. Parse conventional commits by type
3. Group by section
4. Transform technical messages to user-facing prose
5. Add links to PRs/issues

User-facing rewrite rules:
- "fix: null pointer in payment handler" → "Fixed crash during payment processing"
- "perf: add Redis cache for user sessions" → "Login and dashboard load 5x faster with session caching"
- Don't include: refactor, style, chore, docs-only (unless noteworthy)

## Version Bumping (Semantic Versioning)

Follow SemVer 2.0.0 strictly:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

| Change | Bump | Example |
|--------|------|---------|
| Breaking (BREAKING CHANGE or `!`) | MAJOR | 1.2.3 → 2.0.0 |
| New feature (`feat`) | MINOR | 1.2.3 → 1.3.0 |
| Bug fix (`fix`, `perf`) | PATCH | 1.2.3 → 1.2.4 |
| No feat/fix/breaking | NONE | 1.2.3 stays |

### Release Flow

```
1. Determine next version from commits since last tag
2. git checkout -b release/vX.Y.Z
3. Update version in package.json / Cargo.toml / pyproject.toml
4. Update CHANGELOG.md with all changes since last release
5. git commit -m "chore(release): vX.Y.Z"
6. git tag -a vX.Y.Z -m "Release vX.Y.Z"
7. git push --follow-tags
8. Create GitHub Release from tag
```

## Merge Conflict Resolution

When resolving conflicts, follow this priority:
1. **Read both sides fully before resolving**
2. **Prefer the more complete implementation**
3. **Run tests after resolution**
4. **Never silently discard either side's changes**
5. **Add a comment if the resolution is non-obvious**

Conflict resolution commit: `chore: resolve merge conflict in <file>`

## Merge Strategies

| Branch → Target | Strategy | Reason |
|-----------------|----------|--------|
| feat/* → main | Squash & merge | Clean linear history |
| fix/* → main | Squash & merge | Clean linear history |
| release/* → main | Merge commit | Preserve release context |
| hotfix/* → main | Merge commit | Full audit trail |
| main → feat/* | Merge | Sync with latest |

## Security Rules

1. **Never commit secrets** — check with `git diff --cached` for patterns
2. **Sign commits** — use GPG/SSH signing (`git config commit.gpgsign true`)
3. **Protect main** — never force-push to main/master
4. **Signed tags** — `git tag -s vX.Y.Z` for releases
5. **.gitignore audit** — warn if `.env`, `credentials.*`, `*.pem` would be committed

## When NOT to Automate

These Git operations require human judgment — flag them, don't automate:
- **Interactive rebase** — let the user drive it
- **Force push decisions** — warn; never force-push shared branches
- **Large binary files** — suggest Git LFS instead of committing
- **Submodule updates** — flag for review, don't auto-update

## Edge Cases

| Situation | Action |
|-----------|--------|
| Empty commit | Don't create; suggest combining with next change |
| WIP commits | Suggest `git commit --amend` or squash before PR |
| Detached HEAD | Warn user; create branch `git switch -c <name>` |
| Diverged branches | Suggest `git pull --rebase` over `git pull` (merge) |
| Too many commits in PR | Suggest interactive squash before review |
| No recent tags | Start changelog from first commit |
| Monorepo | Scope commits to package: `feat(api):`, `fix(web):` |

## Integration with CI/CD

Generated output is designed for CI/CD consumption:
- **Commitlint config:** `references/commitlint.config.js`
- **Semantic Release config:** `references/.releaserc.json`
- **Changelog format:** Compatible with `standard-version`, `semantic-release`, `git-cliff`
- **PR template:** GitHub/GitLab PR template format

## Scripts

- `scripts/generate-changelog.sh` — Generate changelog from git log
- `scripts/next-version.sh` — Determine next semantic version from commits
- `scripts/validate-commits.sh` — Validate conventional commit compliance

## References

- `references/conventional-commits-spec.md` — Full Conventional Commits spec
- `references/keep-a-changelog-format.md` — Keep a Changelog format guide
- `references/semver-cheatsheet.md` — Semantic Versioning reference