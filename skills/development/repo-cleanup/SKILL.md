---
name: repo-cleanup
description: Use when cleaning up dead code, obsolete tests, and stale documentation across a repository — legacy cleanup or evidence-backed simplification. Not for unrelated feature development, branch-scope tidy (code-simplifier), AI-slop removal (remove-ai-slops), or retiring a feature (deprecation-and-migration).
---

# Repository cleanup

Leave one maintained implementation of each supported behavior, with evidence for every removal. Adapt to the repository's stack: a web production graph alone cannot establish whether native, server, worker, or tooling code is unused.

## Establish the scope

Read repository instructions, ownership boundaries, manifests, build/test configuration, and relevant behavior contracts. Inspect the checkout and preserve other work. Identify authored source, generated artifacts, vendored/copied files, supported platforms, and external consumers. Upstream ownership determines where a repair belongs.

A broad cleanup request authorizes investigation and ordinary reversible cleanup within existing permissions. Follow the repository's actual approval and delivery rules; this skill adds no new approval gate or publishing authority. Keep behavior-changing discoveries separate from behavior-preserving cleanup, and finish independent authorized work while a consequential decision is pending.

Read affected implementations and callers before editing. If the user requests a full-source read, complete it before implementation: inventory tracked source at a named revision, retain file hashes and actual read ranges, and reconcile the union of worker records against the entire inventory. Counts scoped to one directory cannot prove repository coverage. Truncated output and search results are not full reads; inspect binary assets with suitable tools and label that evidence separately. When sources change, identify which reading/review evidence needs refreshing. Use a task-local ledger with revision, path, SHA-256, inclusive line ranges, and completion status; ranges must cover through EOF before marking a text file fully read. Keep this evidence outside tracked source unless the repo requests a checked-in audit. Otherwise, scope reading to the affected graph rather than imposing a full-repo pass.

## Prove a candidate is dead

Use the installed analyzer and repository search to generate candidates, then trace the loading path. For each accepted removal, retain a concise record of the candidate, caller/contract evidence, dependent edits, and verification. Group records by coherent change; a separate document per symbol is unnecessary.

Check these sources of false positives:

- Platform resolution and conditional exports: native/web suffixes, package exports, Metro/Expo or other route conventions, server/client entrypoints, workers, dynamic imports, path strings, and code generation.
- Non-product consumers: scripts, CI, migrations, deployment bundles, fixtures, agent tooling, and published package APIs. Search hidden tracked files too.
- Test-only reachability: a production analyzer can reveal code kept alive only by tests. Determine whether the implementation is obsolete or a required contract lacks a live caller. Move valid assertions to the surviving implementation when removing a duplicate path.
- Dependencies: inspect every owning workspace manifest, scripts, configuration, peer/optional requirements, and platform consumers before removing a package. Update the lockfile using the repo's package manager.

Delete confirmed dead code together with its obsolete exports, callers, fixtures, configuration, and documentation references. Preserve a convention-loaded entrypoint with a narrowly explained analyzer exception when needed. Edit authored source and regenerate required output through its owner; reading a generated or vendored file does not make it locally owned.

## Retire tests by requirement

A test's age, filename, or runtime cost does not establish obsolescence. For duplicate cases, identify the retained assertions that cover the same inputs, side effects, errors, and guards. Keep unique authorization, financial, data-integrity, accessibility, and regression coverage. Replace tests coupled to a removed wrapper with tests of the live behavior when the requirement survives.

For static migration or incident-repair pins, verify rollout/application evidence and the surviving regression owner before retirement. An old SQL file can still be required for replay or fresh installs. Keep uncertainty explicit rather than declaring historical repairs complete from filenames.

Optimize repeated setup, filesystem scans, and compilation when they dominate tests. Preserve test isolation and stable provider/cache lifetimes. Files read dynamically from disk may be absent from affected-test graphs: register real dependencies using the repository's supported approach and prove selection with a related/changed-test run. A slow maintained test belongs in the repo's supported lane, not silently outside execution.

Tests normally affect development and CI time. Claim UI speed improvements only when bundle or runtime evidence demonstrates an effect on shipped code.

## Reconcile docs and modernize selectively

Follow documentation owners and verify claims against live source, scripts, schema, and tests. Correct stale paths, commands, API names, instruction discovery, ownership claims, and rollout prose; link to executable owners instead of copying their catalogs. Retire redundant guidance while preserving contracts and useful decisions.

When current framework/provider guidance matters, fetch official documentation for the installed version and the proposed migration. Treat “latest recommendations” as a request for applicable improvements, not blanket dependency upgrades or provider/protocol switches. Update every affected consumer of an accepted migration. Keep recommendations specific to the actual web/native/backend toolchain; do not carry one repo's stack into another.

## Verify and deliver

Use focused checks during edits, then the repository's required gates. Inspect the combined diff, including untracked files, and obtain a fresh-eyes review when breadth or risk warrants it. If delegating, give workers disjoint write ownership; the lead reconciles their evidence and reviews the integrated result.

Measure claims: compare emitted chunks and entry dependencies for bundler changes, run real supported platform builds for resolution changes, and use browser/device evidence when rendered behavior changes. Byte-identical JavaScript supports preserved output, not faster UI. Tests using Git's tracked-file list may need reviewed deletions staged before scans can run correctly.

Tie checks and review to the delivered revision. Reuse unaffected evidence and rerun checks when integration changes the relevant inputs. Report merged, open, or local-only state accurately.

Finish with what changed and why, verification, remaining findings and their next action, and material limits. Report line/test reductions as maintenance results, not proof of correctness or performance. Leave the repo with no half-removed implementation or unexplained analyzer suppressions.
