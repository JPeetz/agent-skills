# CHANGELOG — git-workflow-automation

## v1.0.0 — 2026-06-04

### Added
- Initial release of Git Workflow Automation agent skill
- Conventional Commits enforcement with complete type-to-SemVer mapping
- Breaking change detection (feat! and BREAKING CHANGE footer)
- Automated commit message generation from staged changes
- Branch naming convention patterns (feat, fix, chore, release, hotfix)
- PR description template generation with structured sections
- Changelog generation following Keep a Changelog format
- User-facing prose rewrite: technical commits → human-readable release notes
- Semantic versioning engine: determines MAJOR/MINOR/PATCH bumps from commit history
- Release flow documentation (branch, version bump, changelog, tag, push, GitHub Release)
- Merge conflict resolution priority rules and best practices
- Merge strategy table (squash, merge commit, rebase per branch type)
- Security rules: commit signing, secret detection, protected branches, signed tags
- Edge case handling (empty commits, WIP, detached HEAD, diverged branches, monorepo scoping)
- CI/CD integration files: commitlint config, semantic-release config, changelog format
- Helper scripts: generate-changelog.sh, next-version.sh, validate-commits.sh
- 6 eval cases with near-miss negatives
- Reference docs: Conventional Commits spec, Keep a Changelog guide, SemVer cheatsheet

### Why
Git workflow skills are among the highest-demand agent skill categories
(Agensi 2026 report). Existing skills focus on single operations (commit message
OR PR description OR changelog). This skill unifies the full Git workflow
lifecycle — commit → branch → PR → merge → changelog → release — with strict
convention enforcement for reproducible CI/CD automation.