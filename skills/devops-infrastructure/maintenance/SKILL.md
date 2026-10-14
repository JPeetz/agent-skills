---
name: maintenance
description: >-
  Use this skill when operating a self-hosted customer web stack (Cal.diy /
  Typebot / n8n / Postgres / Stripe) that a maintenance agent must keep
  available, patched, and backed up automatically. JEV-first decisions, sparse
  LLM generation, health probes, weekly backups, JEV-gated updates, rollback.
version: 1.0.0
platforms: [hermes, openclaw, claude, codex]
author:
  name: Custodian (AgentForge)
  source: Joerg Peetz / Fluffy — Custodian customer-maintenance agent
license: MIT
risk_tier: L2
tags: [maintenance, backup, update, health, ops, self-hosted, jev, runbook]
requires:
  binaries: []
---

# Custodian Maintenance Runbook

Operates a client's self-hosted stack — booking engine (Cal.diy), automation
(n8n), chat (Typebot), Postgres, web/TLS, Stripe webhook. **Purpose: availability
+ recoverability + currency, at the lowest possible inference cost.**

## When to Use This Skill

Use this skill when:
- A customer stack must be monitored, backed up, and updated automatically.
- You need a repeatable, guardrailed maintenance loop (health → backup →
  update → rollback) that never breaks a live booking flow.
- Cost matters: the loop should run decisions on a cheap model and only summon
  a generation model for genuine language work.

## COST DISCIPLINE (first rule)
- Use **JEV** (`typesafe/jev-1.13`, endpoint `/api/alpha/decisions`) for EVERY decision
  (gate an update, classify an incident, pick retention).
- Use a cheap **flash model** ONLY for unavoidable language work: writing the human
  incident text, parsing an error JEV can't classify, composing an escalation, reading
  a release note for breaking-change judgment.
- A cycle that completes JEV-only is a WIN. Do not summon a generation model for
  anything a command, grep, or JEV resolves.

## JEV call shape (verified)
POST `https://openrouter.ai/api/alpha/decisions`
Headers: `Authorization: Bearer $OPENROUTER_API_KEY`, `Content-Type: application/json`
Body:
```json
{"model":"typesafe/jev-1.13",
 "state":"<short context>",
 "questions":{"q1":{"type":"choice","instructions":"...","criteria":{"A":"...","B":"..."}},
              "q2":{"type":"score","instructions":"...","criteria":["0: ...","1: ...","2: ..."]},
              "q3":{"type":"noul","instructions":"..."}}}
```
Read `answers[qid].choice|score|noul` + `.confidence`. Threshold `< 0.6` confidence → escalate.
`score` runs 0..(len(criteria)-1); normalise / (len-1). Use `noul`, not `bool`. Batch all
questions for a decision into ONE call. try/catch every JEV call → safe neutral default.

## 1. HEALTH PROBE (every 15 min)
Probe each service; record ok/fail:
```
systemctl is-active <cal-diy|n8n|typebot|postgres|caddy/nginx> 2>/dev/null
curl -fsS -o /dev/null -w "%{http_code}" http://localhost:PORT/health   # per service
curl -fsS -o /dev/null -w "%{http_code}" https://<domain>/            # web + TLS via HTTPS
openssl x509 -noout -enddate -in <crt> 2>/dev/null                     # TLS expiry
df -h / | tail -1; free -m | awk 'NR==2{print $3"/"$2"MB"}'            # disk + RAM
```
If all ok → emit nothing (quiet). If any fail:
1. JEV `noul` "Is this an incident requiring action?" (threshold 0.6).
2. JEV `choice` classify: transient / service-down / disk-full / tls-expiring / unknown.
3. If covered by a rule (one known-good service dead, TLS < 7d) → repair per that
   service's rollback+restart rule; verify health after.
4. If unknown/breaking/ambiguous → do NOT mutate → queue, alert once.

## 2. WEEKLY BACKUP (Sunday 03:00 UTC)
1. `pg_dump` the DB to a timestamped file.
2. Back up config + env (vault labels, docker-compose, Caddyfile).
3. Rotate by retention: daily×7 + weekly×4 (from config).
4. Copy off-box to the backup destination (S3/syncthing/second VPS).
5. VERIFY restorable (`pg_restore --list` or load into scratch schema + SELECT count).
6. Alert: `Backup <ts> OK (n MB, verified restorable)` or `BACKUP FAILED: <why>`.
- Never run a mutation without a fresh verified backup first.

## 3. WEEKLY UPDATE CHECK (Monday 02:00 UTC)
1. Query upstream releases: Cal.diy (`calcom/cal.diy`), Typebot (`baptisteArno/typebot.io`),
   n8n (`n8n-io/n8n`). Note current pinned vs available.
2. For each pending update: JEV `noul` "Is this a safe non-breaking update?"
   (fresh backup + supported path + not a major jump = lower; breaking/major/unknown = higher).
3. Non-breaking → apply → verify service health → record.
4. Breaking/major/ambiguous → STALL, escalate with the specific release + JEV reasoning.
   Do NOT auto-install a breaking change on a live booking system.
5. Report briefly: applied / stalled / nothing.
- Core stays upstream-compatible: customisation is additive overlay; never a destructive
  rewrite that breaks a clean upstream merge.

## 4. DISK HEADROOM (daily)
- `df -h /System/Volumes/Data 2>/dev/null || df -h /` — take the DATA volume. If < 15%
  free → warn. If < 5% → escalate immediately (a full disk kills cron first).
- Flag transient big-writer patterns from shared hosts if present (WAL/snapshots can
  spike a volume and starve unrelated cron).

## 5. ROLLBACK (always have a story before a mutation)
Keep the previous pinned version/image + its verified backup. To rollback: stop service,
restore previous image, restart, verify health. The rollback path exists BEFORE any apply.

## 6. REPORTING
- Quiet unless it matters. Speak up on: incident fired, update applied, backup
  verified/FAILED, escalation needed, disk low.
- Reports are verified on the output side — never claim success without reading back proof.
- Escalation format: what happened · tradeoff · recommendation · exact decision needed.

## PITFALLS
- A full disk kills cron first — check disk first, cheaply, often.
- `score` needs normalising; use `noul` not `bool`; confidence-gate before any action.
- Never blind-`latest` on a live system; pin and verify.
- Never state an update/backup succeeded without output-side verification.
- Secrets by label from the vault; split-headers so keys never verbatim in output.
- DeepSeek/flash is for language work only — don't summon it to "decide".
