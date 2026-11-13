# Changelog

## [0.1.0] - 2026-11-13

### Added
- Initial release: changelog-generator skill
- `scripts/generate_changelog.py` — Conventional Commit parser with Keep a Changelog rendering, semver bump detection, and JSON output
- `scripts/commit_linter.py` — commit message linter with strict mode and JSON output
- Support for breaking changes via both `type(scope)!:` and `BREAKING CHANGE:` footers
- `--update` mode that prepends to an existing CHANGELOG.md without touching history
- `references/ci-integration.md` with GitHub Actions, pre-commit, and release-job wiring
- Eval cases covering version selection, breaking-change migration notes, and linter behavior
