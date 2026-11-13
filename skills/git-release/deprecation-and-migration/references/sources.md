# Sources

Reference material behind this skill. Prioritise the primary sources (specs and vendor docs) over secondary write-ups.

## Upstream skill

- Addy Osmani, `agent-skills` — `deprecation-and-migration`
  https://github.com/addyosmani/agent-skills/blob/main/skills/deprecation-and-migration/SKILL.md
  Source for the decision tree, Hyrum's Law framing, advisory/compulsory split, migration patterns, expand/contract worked example, and the rationalizations table. This skill extends it with the codemod workflow, the semver-tied support window, the explicit evidence gate, and the service sunset checklist.

## Versioning and changelog policy

- Semantic Versioning 2.0.0 — https://semver.org/
  Authoritative definition of MAJOR/MINOR/PATCH and why removal is a major bump.
- Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/
  The `Deprecated` and `Removed` sections; the two-entry announcement-then-removal discipline.
- Node.js Release Working Group, deprecation policy — https://github.com/nodejs/Release/blob/main/GOVERNANCE.md
  A real-world example of a documented support window tied to release lines.

## Hyrum's Law and API evolution

- Hyrum Wright, "Hyrum's Law" — https://www.hyrumslaw.com/
  Original statement: with enough users, all observable behaviors become depended on.
- Google SRE Book, "Managing Load" / graceful degradation chapters — https://sre.google/sre-book/table-of-contents/
  Background on running two paths in parallel and draining traffic.
- `sunset` HTTP response header (RFC 8594) — https://www.rfc-editor.org/rfc/rfc8594
  Machine-readable deprecation signalling: `Sunset` and `Deprecation` headers.

## Expand / contract and zero-downtime schema changes

- Martin Fowler, "Parallel Change" — https://martinfowler.com/bliki/ParallelChange.html
  The expand/migrate/contract pattern this skill applies to schemas and APIs.
- PostgreSQL docs, `CREATE INDEX CONCURRENTLY` — https://www.postgresql.org/docs/current/sql-createindex.html
  Non-blocking index builds; the lock behaviour that makes a plain `UPDATE` backfill dangerous.
- PostgreSQL docs, `ALTER TABLE` — https://www.postgresql.org/docs/current/sql-altertable.html
  Which alterations take `ACCESS EXCLUSIVE` locks, and why add-column is cheap while rewrite is not.
- GitHub Engineering, "Online schema migrations for GitHub's MySQL databases" — https://github.blog/engineering/architecture-optimization/online-schema-migrations-for-githubs-mysql-databases/
  Production account of batched, throttled, resumable backfills.

## Codemods and large-scale change

- `jscodeshift` — https://github.com/facebook/jscodeshift
  AST-based JS/TS codemods; the `--dry`/`--print` review loop.
- `ast-grep` — https://ast-grep.github.io/
  Structural search and rewrite across many languages; better than regex once call shapes vary.
- `comby` — https://comby.dev/
  Lightweight structural matching and rewriting, including non-code files.
- `libcst` — https://libcst.readthedocs.io/
  Python codemods that preserve formatting, which keeps review diffs honest.
- OpenRewrite — https://docs.openrewrite.org/
  Recipe-based Java/Kotlin migrations with test harnesses.
- Google Testing Blog, "Codemod" / large-scale change posts — https://testing.googleblog.com/
  Practice notes on landing codemods in reviewable batches.

## Service sunset and decommissioning

- RFC 9110, HTTP Semantics — `410 Gone` — https://www.rfc-editor.org/rfc/rfc9110#name-410-gone
  Why 410 communicates intentional removal where 404 reads as a fault.
- AWS Well-Architected, Sustainability Pillar — https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/
  Decommissioning guidance, including orphaned resources and right-sizing after shutdown.
- NIST SP 800-88 Rev. 1, Guidelines for Media Sanitization — https://csrc.nist.gov/pubs/sp/800/88/r1/final
  Data destruction expectations behind the retention and PII deletion items.

## Adjacent skills in this repo

- `skills/development/safe-refactor` — behavior-preserving internal restructuring with green tests. Boundary: no public contract, no consumers to migrate.
- `skills/code-quality/code-simplification` — reducing readability complexity within a file. Boundary: nothing is removed from the public surface.
- `skills/git-release/release-management` — version arithmetic, tagging, release notes.
- `skills/git-release/changelog-generator` — generating the `Deprecated` and `Removed` entries from commits.
