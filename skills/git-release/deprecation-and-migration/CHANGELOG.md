# Changelog

## [1.0.0] - 2026-11-13

### Added
- Initial release: deprecation-and-migration skill
- Deprecation decision tree covering unique value, replacement readiness, consumer count, migration cost, and cost of non-removal
- Hyrum's Law framing: behavior-level dependencies, the Churn Rule, and why announcement migrates nobody
- Advisory vs compulsory deprecation with the resourcing each implies
- Deprecation notice template with support window, old/new mapping table, and migration steps
- Expand/contract (parallel change) for renames, drops, and type changes, including a Postgres `integer → text` worked example
- Codemod workflow: caller inventory with `rg`/`ast-grep`/`comby`, syntax-aware rewrite, batched review, delete the old path
- Support-window policy tied to semver, with a two-entry `Deprecated` → `Removed` changelog discipline
- Evidence gate before deletion: grep zero, metric zero, tests updated, docs and CHANGELOG record the removal
- Service sunset checklist: tombstone/redirect responses, data retention and export, credential and DNS revocation, orphaned resources
- Eval cases covering deprecation notice quality, expand/contract migration, and full service sunset
- `references/sources.md` with upstream and primary sources
