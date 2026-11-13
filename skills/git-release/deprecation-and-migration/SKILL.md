---
name: deprecation-and-migration
description: "Use this skill when deprecating APIs or migrating users."
version: "1.0.0"
author: "@artisan"
license: MIT
category: git-release
platforms:
  - claude-code
  - openclaw
  - cursor
  - codex
  - opencode
  - gemini-cli
permissions:
  files.read: true
  files.write: true
  network: false
  shell.execute: false
  dangerous: false
metadata:
  tags:
    - deprecation
    - migration
    - expand-contract
    - codemod
    - semver
    - sunsets
    - api-lifecycle
  related_skills:
    - safe-refactor
    - code-simplification
    - changelog-generator
    - release-management
---

# Deprecation and Migration

## Overview

Code is a liability. Every line carries maintenance cost — tests to keep green, dependencies to patch, security advisories to answer, and context every future reader must rebuild. Deprecation is the discipline of removing code that no longer earns its keep; migration is moving its consumers somewhere safe before you do.

Most teams are good at building. Few are good at removing. This skill covers the removal half: deciding whether to deprecate, announcing it honestly, migrating consumers without downtime, and proving the old path is actually gone before deleting it.

## When to Use

- Removing a public API, endpoint, exported symbol, CLI flag, or config key
- Replacing an implementation and moving callers onto the new one
- Renaming or dropping a database column in production without downtime
- Sunsetting a whole service, hostname, or credential set
- Deciding whether to keep maintaining a legacy system or invest in migration

**When not to use:** a behavior-preserving internal restructure with green tests belongs to `safe-refactor`; trimming readability complexity inside one file belongs to `code-simplification`. This skill is for changes that cross a boundary — a version, a package, a contract, or a running production system — where someone outside your diff depends on you.

## The Deprecation Decision Tree

Answer in order. Stop at the first answer that decides.

```
1. Does this still provide unique value?
   → Yes: maintain it. No unique value means nothing else matters.
   → No: continue.

2. Is there a replacement?
   → No: build it first. Never deprecate without an alternative that
     covers the critical use cases. "We'll figure it out" is not a plan.

3. How many consumers depend on it?
   → Count them, don't estimate: callers in-repo, packages importing it,
     HTTP clients by user-agent, rows referencing it, cron jobs, docs.
   → Zero consumers: skip deprecation, go straight to removal.

4. What does migration cost per consumer?
   → Automatable by codemod: do it, and ship the codemod.
   → Manual and expensive: compare against maintenance cost (5).

5. What is the cost of NOT deprecating, over 2–3 years?
   → Security surface, dependency pins, engineer hours, onboarding drag,
     and the opportunity cost of every change having two paths.
   → If maintenance is cheaper than migration, maintain it honestly —
     and stop calling it deprecated. A permanent "deprecated" label with
     no removal is worse than no label: it tells consumers the code is
     dead while you keep paying for it.
```

Two failure modes to name explicitly: deprecating something with **no replacement**, and deprecating something with **zero measured usage** instead of just deleting it.

## Hyrum's Law: Announcement Is Not Migration

With enough consumers, every observable behavior becomes a dependency — including bugs, error message text, field ordering, timing, retry counts, and undocumented side effects. That is Hyrum's Law, and it is the reason a deprecation announcement reliably fails to produce migration.

Practical consequences:

- **Assume behavior-level dependencies exist even when the signature is identical.** A consumer pinned to "returns 500 on bad input" breaks when the replacement returns 400, even though both are "errors".
- **Enumerate behavior, not just symbols.** For each entry point, list: status codes, error strings, ordering guarantees, nullability, default values, side effects, and rate limits. Diff old against new. Every difference is a migration item.
- **Defaults are the API.** A changed default silently migrates nobody and breaks everybody.
- **Announcement alone migrates ~0% of consumers.** The Churn Rule: if you own the infrastructure, you own the migration — either you move the callers, or you ship compatibility that makes moving free.
- **Measure behavior, not intent.** A dashboard showing "consumers notified" is not evidence; a metric showing old-path request count going to zero is.

## Advisory vs Compulsory

| Type | When | Mechanism |
|---|---|---|
| Advisory | Replacement is stable, old path is safe | Warnings, docs, deprecation headers. Consumers migrate on their timeline. |
| Compulsory | Security issue, blocking constraint, unsustainable cost | Hard date. You supply tooling, docs, and support. |

Default to advisory. Compulsory is a promise you must resource: a deadline without a codemod, a guide, and a support channel is an outage you scheduled for someone else.

## Deprecation Notice Template

Ship this in three places at once — the CHANGELOG, the docs page, and the runtime signal (header, warning log, or compile-time annotation). A notice that lives only in a wiki is not a notice.

```markdown
## Deprecation: <symbol / endpoint / service>

- **Status:** Deprecated as of <version> (<YYYY-MM-DD>)
- **Replacement:** <name> — <one-line why it is better>
- **Removal:** <version> at earliest, not before <YYYY-MM-DD>
- **Support window:** <N minor releases / M months> (see policy below)
- **Reason:** <concrete cost being removed — security, scaling, dual maintenance>

### What changed for you
| Old | New |
|---|---|
| `oldCall(x)` | `newCall({ value: x })` |
| header `X-Old` | header `X-New` |
| column `name` | column `full_name` |

### Migration steps
1. <mechanical step, exact command>
2. <config change, with before/after>
3. Verify: `<command>` — expect <output>

### Getting help
<issue link, channel, owner handle>
```

Rules for the notice: it states a **date and a version**, names a **replacement**, gives **runnable steps**, and names an **owner**. Undated deprecations rot indefinitely; that is how "advisory for four years" happens.

## Expand / Contract (Parallel Change)

Never change a contract in place across a version boundary. Migrate in additive phases so **old and new consumers are both valid at every deploy**. Each phase is independently deployable and reversible.

```
EXPAND ───────────────→ MIGRATE ───────────────→ CONTRACT
add new alongside old,  dual-write + backfill,   stop writing old,
both accepted           switch readers           drop old alone
```

### 1. Renames

Worked example — API field `name` → `full_name`:

1. **Expand.** Add `full_name` (nullable) and accept it in requests. Old `name` still works. Deploy.
2. **Dual-write.** Writes populate both; reads still use `name`. Deploy.
3. **Backfill.** Copy `name → full_name` for existing rows in throttled batches, off the hot path.
4. **Switch reads.** Point readers at `full_name`; keep dual-writing. Deploy, then bake — watch error rates and dashboards for longer than one release cycle.
5. **Contract.** Stop writing `name`. Deploy. Then, in a *separate, later* deploy with old code no longer running, drop it.

### 2. Drops

- **Expand:** emit a deprecation warning from the read path and add a metric counting remaining consumers. Make the deprecation visible in the response (header, log line), not just in docs.
- **Migrate:** move every caller to the replacement. Track the count down to zero in a dashboard you actually look at.
- **Contract:** drop after the support window closes and the metric has read zero through at least one full traffic cycle (include weekly and monthly batch jobs — they are the ones that break on day 31).

### 3. Type changes

Postgres example — `id integer` → `id text`:

```sql
-- Expand (safe, additive)
ALTER TABLE orders ADD COLUMN id_text text;
CREATE UNIQUE INDEX CONCURRENTLY orders_id_text_idx ON orders (id_text);

-- Backfill in batches, never one UPDATE over the table
UPDATE orders SET id_text = id::text
WHERE id_text IS NULL AND id IN (SELECT id FROM orders WHERE id_text IS NULL LIMIT 5000);
```

Then dual-write both columns with the cast applied in the app, switch reads to `id_text`, and only then drop `id`. Ship the drop in its own deploy.

**Rules that apply to every expand/contract:**

- **Additive first, destructive last and alone.** Adds are safe in any deploy; drops and renames get their own deploy *after* no code references the old shape.
- **Every migration has a tested `down` path.** A migration you cannot reverse is a deploy you cannot roll back. Run the down before merging the up.
- **Backfill in batches and throttle.** A single `UPDATE` over millions of rows takes a lock that takes your service with it.
- **Build large indexes without blocking writes** — `CREATE INDEX CONCURRENTLY` in Postgres.
- **Decouple risky cutover with a feature flag**, then remove the flag branch once the new path is the only path.
- **Deploy-time reality:** during any rollout, old and new code run simultaneously. If the schema change and the code change ship in the same deploy, one of them is querying a column that does not exist.

## Codemod Workflow

For in-repo migrations and published packages, migration *is* automation — otherwise you have outsourced the work to your consumers.

**1. Inventory callers.** Produce a list, not a feeling.

```bash
rg -n --stats -g '!**/CHANGELOG.md' '\boldCall\(' src/ packages/ examples/
rg -l 'from ["'\'']old-package["'\'']' . | wc -l
# Structural queries beat regex once shapes vary:
ast-grep --pattern 'oldCall($ARG)' --lang ts
comby 'oldCall(:[arg])' 'newCall({ value: :[arg] })' .ts
```

Record: file count, repo count, distinct call shapes. Distinct shapes decide whether a mechanical rewrite is feasible; if there are 40 shapes, fix the API or write 40 rules — do not hand-edit 400 files.

**2. Mechanical rewrite.** Use a syntax-aware tool (`jscodeshift`, `ast-grep`, `comby`, `libcst`, OpenRewrite) — never `sed`. Requirements: idempotent (running twice changes nothing), dry-run first, and a diff you can review.

```bash
npx jscodeshift -t codemods/rename-call.ts src/ --dry --print
```

**3. Human review.** Land in small batches, one package or directory per PR. Typecheck and tests must pass per batch so a failure points at one codemod rule, not 400 files. Review the diff for semantic drift: the codemod that "worked" on 398 files and silently reordered arguments on the other 2 is the normal case.

**4. Delete the old path.** Only after the shim has zero callers: remove the deprecated export, the adapter, the warning, and the compatibility branch. A shim left behind becomes permanent — it is the only artifact in the repo whose cost never appears in a ticket.

## Support Window Policy (tied to semver)

| Change | Announced in | Earliest removal | Notes |
|---|---|---|---|
| Deprecate a public API | MINOR | Next MAJOR | Mark `@deprecated`, emit runtime warning, add to docs |
| Remove a deprecated API | MAJOR | — | Major bump is the removal license; list it under `Removed` |
| Add optional field / param | MINOR or PATCH | — | Additive, no window needed |
| Change a default | MAJOR | — | Defaults are behavior; treat as breaking |
| Security removal | PATCH (expedited) | Same or next release | Allowed to break semver — document the CVE and mitigation |
| Internal-only symbol | PATCH | Any release | No public window required, still needs the evidence gate |

Minimum window: **one full minor release or 90 days, whichever is longer**, for anything public. Consumers on a slower release cadence are the ones a 30-day window silently breaks. Record the deprecation in `CHANGELOG.md` under `Deprecated` when announced and under `Removed` when deleted — two entries, two releases, so the history shows the promise was kept.

`changelog-generator` and `release-management` own the version arithmetic; this skill owns the promise the version number makes.

## Evidence Gate

Deletion is a claim that nobody depends on this. Prove it, per item, before merging the removal PR.

- [ ] **Grep returns zero callers** — excluding `CHANGELOG.md`, migration docs, and the deprecated definition itself:
      `rg -n 'oldSymbol' --glob '!CHANGELOG.md' --glob '!docs/migrations/**'` → no hits
- [ ] **Runtime metric reads zero** for at least one full traffic cycle, including weekly/monthly batch jobs
- [ ] **Tests updated, suite green** — deleted tests for the old path, added tests for the replacement, no `skip`/`xfail` used to make it pass
- [ ] **Docs and CHANGELOG record the removal** with version, date, and the replacement (`Removed` section, linked to the original `Deprecated` entry)
- [ ] **Deprecation notices removed** — the `@deprecated` tag, the warning log, the `Deprecation`/`Sunset` response headers
- [ ] **Down path exists** for any migration shipped in the same PR

If any box is unchecked, the removal is not ready — it is a hope with a diff attached.

## Sunset Checklist for Services

Removing a service is deprecation plus infrastructure. The code is the easy part.

**Traffic**
- [ ] Serve a machine-readable sunset response before shutdown: `410 Gone` with a body pointing at the replacement, or `301` if there is a true 1:1 successor. Never `404` — it reads as a bug and generates support tickets instead of migrations.
- [ ] Keep the tombstone endpoint alive for the full support window; it costs near-zero and converts failures into instructions.
- [ ] Verify client retry behavior: a 410 that clients retry forever is a self-inflicted DDoS.

**Data**
- [ ] Retention decision made and written down: export window, format, who can request it, retention period after shutdown.
- [ ] Backup verified by *restoring* it once — an untested backup is a rumor.
- [ ] PII deleted on schedule, not "eventually"; record the deletion.

**Access**
- [ ] Credentials and API keys revoked; tokens invalidated, not just rotated away from.
- [ ] IAM roles, service accounts, and OAuth clients deleted.
- [ ] DNS records removed and certificates allowed to lapse — after the tombstone window, not before.
- [ ] Webhooks and outbound integrations deregistered at the third party, so they stop calling a dead host.

**Operations**
- [ ] Alerts, dashboards, and synthetics removed — a monitor for a dead service pages someone at 3am for nothing.
- [ ] Runbooks deleted, on-call rotation updated, ownership transferred for anything still referenced.
- [ ] Cost confirmed at zero in the billing console; orphaned resources (buckets, snapshots, IPs, log groups) are the usual survivors.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It still works, why remove it?" | Working but unmaintained code accrues security debt and blocks change. The cost is silent, not zero. |
| "Someone might need it later" | Then it can be rebuilt against a current codebase. Keeping it costs more than rebuilding it. |
| "Migration is too expensive" | Compare against 2–3 years of dual maintenance, testing, docs, and onboarding. Migration usually wins. |
| "Users will migrate on their own" | They will not. Ship the codemod, the guide, and the deadline — or do the migration yourself. |
| "Just rename the column, it's one line" | During rollout, old and new code coexist; one queries a column that is gone. Expand/contract. |
| "We'll write the rollback if we need it" | You will need it at the worst moment, without it. Run the `down` before merging the `up`. |
| "We deprecated it, that's the hard part" | Announcement migrates nobody. The hard part is the codemod and the evidence gate. |

## Red Flags

- Deprecation with no replacement, or no date
- "Advisory" for multiple years with zero migration progress
- Removal PR with no grep evidence and no metric
- Schema change and dependent code change in the same deploy
- Consumers discovered *after* the removal — means usage was never measured
- New features still landing on the deprecated path
- A compatibility shim with no owner and no removal ticket

## Verification

Before declaring the deprecation complete:

- [ ] Replacement is production-proven and covers the documented use cases
- [ ] Notice shipped to CHANGELOG + docs + runtime signal, with version and date
- [ ] Every consumer migrated, proven by metric or grep — not by notice sent
- [ ] Old code, tests, docs, config, and notices removed
- [ ] Removed entry in `CHANGELOG.md` links back to the `Deprecated` entry
- [ ] `rg` over the tree finds no surviving references

Before declaring a schema migration complete:

- [ ] Shipped in additive phases, never an in-place edit
- [ ] Old and new code both valid against the schema at every deploy step
- [ ] `down` path written, run, and merged alongside `up`
- [ ] Backfills batched and throttled; large indexes built concurrently
- [ ] Destructive step shipped in its own deploy, after zero readers
