---
name: release-management
description: Use this skill when preparing a new software release — version bumping, changelog generation, git tag workflows, release notes drafting, semantic versioning decisions, and CI release pipeline management. Covers the full release lifecycle from version selection to distribution.
---

# Release Management

## Overview

Structured release management workflow covering versioning, changelogs, git tagging, release notes, CI/CD release automation, and rollback procedures. Ensures every release is traceable, documented, and recoverable.

## When to Use

- Cutting a new version before deployment
- Deciding the next version number (major/minor/patch)
- Writing or updating a changelog
- Tagging a git release
- Drafting release notes for stakeholders
- Reviewing or troubleshooting a CI release pipeline
- Planning a hotfix or security release
- Preparing rollback procedures

## Semantic Versioning (SemVer)

### Version Format: `MAJOR.MINOR.PATCH`

| Bump | When | Example |
|------|------|---------|
| **MAJOR** | Breaking API changes, incompatible changes | 1.x → 2.0.0 |
| **MINOR** | New features, backward-compatible | 1.1.0 → 1.2.0 |
| **PATCH** | Bug fixes, backward-compatible | 1.1.1 → 1.1.2 |

### Additional Labels

| Label | Meaning | Example |
|-------|---------|---------|
| -alpha.N | Early testing, incomplete | 2.0.0-alpha.1 |
| -beta.N | Feature-complete, testing | 2.0.0-beta.1 |
| -rc.N | Release candidate | 2.0.0-rc.1 |
| +build.N | Build metadata | 1.0.0+build.42 |

### Versioning Rules

1. Once a version is published, never modify that version's tag or release
2. If a breaking change is discovered between rc and release, bump major
3. Security hotfixes increment patch on the affected major version line
4. Pre-release versions have lower precedence than the normal version

## Changelog Management

### Keep a Changelog Format

Every release entry should follow this structure:

```
## [1.2.0] - 2026-10-26

### Added
- New feature descriptions

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be-removed features

### Removed
- Features removed in this release

### Fixed
- Bug fixes

### Security
- Vulnerability fixes
```

### Changelog Discipline

- Every PR should include a changelog entry as part of the PR description
- Changelog is maintained in `CHANGELOG.md` at the repo root
- Unreleased changes go under `## [Unreleased]` section
- When cutting a release, promote `[Unreleased]` to the new version header
- Link each version header to the tag comparison on GitHub/GitLab

## Release Workflow

### Step 1: Determine the Version Bump

Check each merged change since the last release and apply the highest severity bump:

```
[PATCH]  Bug fixes, hotfixes, documentation
[MINOR]  New features, deprecations, non-breaking improvements
[MAJOR]  Breaking API changes, major rewrites, migrations
```

**Tiebreaker:** If changes span multiple categories, bump by the highest category. A single breaking change means a major bump even if everything else is patches.

### Step 2: Prepare the Release Branch

```bash
# From main branch, ensure it's up to date
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v1.2.0
```

### Step 3: Update Changelog

- Move `[Unreleased]` entries to the new version header
- Add the release date
- Verify every change in this release has a changelog entry
- Update the diff link at the bottom of CHANGELOG.md

### Step 4: Update Version in Manifest

Update the version in all manifest files:

| Platform | File | Field |
|----------|------|-------|
| Node/Python | `package.json` / `pyproject.toml` | `version` |
| Rust | `Cargo.toml` | `version` |
| Go | `build.gradle` / `Cargo.toml` | `version` |
| Generic | `VERSION` file or `__init__.py` `__version__` | — |

```bash
# Example: Python
sed -i 's/version = "1.1.0"/version = "1.2.0"/' pyproject.toml
# Example: Node
npm version 1.2.0
```

### Step 5: Commit and Tag

```bash
# Commit the version and changelog changes
git add CHANGELOG.md pyproject.toml
git commit -m "chore(release): v1.2.0"

# Create signed tag
git tag -s v1.2.0 -m "Release v1.2.0"

# Push tag and branch
git push origin v1.2.0
git push origin release/v1.2.0
```

### Step 6: Merge Release Branch

```bash
# Open PR for release branch
gh pr create --base main --head release/v1.2.0 --title "Release v1.2.0" --body "See CHANGELOG.md"

# After approval, merge with --no-ff
git checkout main
git merge --no-ff release/v1.2.0
git push origin main

# Delete release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### Step 7: Create GitHub/GitLab Release

```bash
# GitHub release
gh release create v1.2.0 --title "v1.2.0" --notes-file CHANGELOG.md --verify

# For pre-release
gh release create v1.2.0-rc.1 --title "v1.2.0-rc.1" --prerelease --notes-file CHANGELOG.md
```

### Step 8: Deploy

- Trigger the CI/CD pipeline for the release tag
- Deploy to staging first, verify, then production
- Monitor for errors for 30 minutes after production deploy

## CI/CD Release Pipeline

### Recommended Pipeline Stages

```
lint → test → build → integration → security → publish → deploy
```

### Release Job Example (GitHub Actions)

```yaml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: make build
      - name: Publish
        run: make publish
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
      - name: Deploy
        run: make deploy
```

### Artifact Signing

- Sign release artifacts with GPG or Sigstore (cosign)
- Publish checksums (SHA256SUMS)
- Verify signatures in the deployment step

## Hotfix Release Workflow

For urgent fixes that cannot wait for the next regular release:

```bash
# Branch from the release tag, not from main
git checkout -b hotfix/v1.2.1 v1.2.0

# Apply the fix
git cherry-pick <commit-hash>  # or make the fix directly

# Version bump (patch increment)
# Update version: 1.2.0 → 1.2.1

# Add changelog entry under [Fixed]

# Commit, tag, PR, and release following the standard workflow

# Cherry-pick the fix back to main after hotfix release
git checkout main
git cherry-pick <hotfix-commit-hash>
```

## Rollback Procedures

### Before Deployment

Document the rollback plan:

| Item | Details |
|------|---------|
| Rollback trigger | What metric or signal triggers a rollback? |
| Rollback command | Exact command to revert |
| Data migration | Is there a reversible migration? |
| Verification | How to verify rollback succeeded? |
| Communication | Who needs to be notified? |

### Rollback Strategies

| Strategy | When | How |
|----------|------|-----|
| **Git revert** | Code-only change | `git revert <tag>` + new PR |
| **Feature flags** | Gradual rollout | Disable flag, users see old behavior |
| **Database migration revert** | Schema change | `sequelize db:migrate:undo` or equivalent |
| **Infrastructure rollback** | Deployment failure | Redeploy previous container/image version |
| **Version pin** | Dependency issue | Pin to previous version in requirements |

## Release Checklist

```markdown
## Release: v1.2.0

### Pre-Release
- [ ] All changes since last release are documented in CHANGELOG.md
- [ ] Version bumped in all manifest files
- [ ] Version bump follows SemVer rules
- [ ] All tests pass (local and CI)
- [ ] Integration tests pass
- [ ] No known critical bugs in the milestone
- [ ] Security scan completed (zero critical/high issues)
- [ ] Release branch created and CI pipeline green

### Release
- [ ] Changelog finalized with date
- [ ] Git tag created (signed)
- [ ] PR merged to main with --no-ff
- [ ] GitHub/GitLab release created
- [ ] Release notes published
- [ ] Artifacts built and signed
- [ ] Checksums published

### Post-Release
- [ ] Deployed to production
- [ ] Monitored for 30 minutes post-deploy
- [ ] Smoke tests passed in production
- [ ] Rollback plan documented (ready if needed)
- [ ] Stakeholders notified
- [ ] [Unreleased] section started in CHANGELOG.md for next cycle
```

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Merging to main before tagging | Loses the release boundary | Always tag before merging the release branch |
| Bumping version in PR body instead of manifest | Version never actually changes | Automate version bumps in CI or pre-commit hook |
| Changelog entries that just say "Bug fixes" | Useless for debugging | Require specific descriptions in PR templates |
| Forgetting to pull tags before releasing | Duplicate tag or wrong base | Add `git fetch --tags --force` to release script |
| No pre-release validation | Breaking changes in production | Gate releases through staging environment |
| Manual release steps | Human error, forgotten steps | Automate everything except the git tag and deploy trigger |
| No rollback test | Post-deploy panic | Test rollback in staging before every major release |
| Releasing on Friday afternoon | Weekend incident response | No deploys after Thursday EOD |

## Red Flags

- Releases happening without a changelog update
- Versions bumped without following SemVer
- No signed tags for release commits
- Release process not documented in CONTRIBUTING.md
- Hotfixes applied without cherry-picking back to main
- Release branch diverging significantly from main
- No testing between version bump and tag creation
- Rollback plan not documented before deployment