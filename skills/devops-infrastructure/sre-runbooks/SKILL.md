---
name: sre-runbooks
description: >-
  Safe-by-default DevOps/SRE runbook automation for incident response,
  postmortems, on-call handovers, and operational troubleshooting.
  Implements Google SRE principles with agent-safe execution patterns
  including dry-run modes, human approval gates, and blast-radius limits.
version: 1.0.0
platforms: [openclaw, claude, codex, cursor, gemini, copilot, opencode, windsurf]
author:
  name: Skill Foundry (Forge)
  source: Google SRE Book, bregman-arie/devops-sre-skills, Pulumi DevOps Skills
license: MIT
risk_tier: L2
tags: [devops, sre, incident-response, runbook, postmortem, on-call, troubleshooting]
requires:
  binaries: []
---

# SRE Runbooks

Production-safe DevOps and SRE runbook automation. Execute incident response
procedures, draft postmortems, generate on-call handovers, and troubleshoot
production issues — all with built-in safety gates that prevent the agent
from making destructive changes without human approval.

## When to Use This Skill

Use this skill when:
- Responding to a production incident (alert fired, service degraded)
- Writing or updating a runbook for a service
- Drafting a postmortem after an incident
- Preparing on-call handover notes
- Troubleshooting a deployment failure or pipeline issue
- Performing a root cause analysis (RCA)
- Any request like "investigate this alert", "write a postmortem",
  "create runbook for X", "prepare handover notes"

## Safety Model

This skill is **risk tier L2 (elevated)**. Every automated action follows
these safety rules:

### Execution Gates

| Gate | Description |
|------|-------------|
| **Read-only first** | All investigations start read-only; writes require explicit escalation |
| **Dry-run by default** | Destructive commands print what they *would* do before execution |
| **Blast-radius check** | Before acting, compute and report the scope of impact |
| **Human approval** | Any change to production state requires human confirmation |
| **Rollback plan** | Every change proposal includes a verified rollback path |
| **Audit log** | Every action is logged with timestamp, identity, and justification |

### Never-Automate List

These actions require a human in the loop, no exceptions:
- `kubectl delete` on running workloads
- `terraform destroy` or `terraform apply -auto-approve`
- Database DROP, TRUNCATE, or schema-destructive migrations
- DNS record deletion or apex domain changes
- IAM policy or RBAC role removal
- Secrets rotation without backup verification
- Firewall rule removal on production traffic paths

## Incident Response Workflow

### Phase 1: Triage (Read-Only)

When an alert fires, the agent:

1. **Acknowledges the alert** in the incident management system
2. **Gathers context** — recent deployments, config changes, metrics
3. **Identifies the blast radius** — affected services, users, regions
4. **Checks for known patterns** in the incident database
5. **Declares severity** based on SLO impact

```
SEVERITY ASSESSMENT:
├── SEV0: User-visible outage, SLO breached → Page on-call
├── SEV1: Degraded but available, SLO at risk → Alert on-call
├── SEV2: Non-critical, SLO not threatened → Ticket
└── SEV3: Informational, no user impact → Log only
```

### Phase 2: Investigation

The agent systematically works through:

1. **The Four Golden Signals** (Google SRE):
   - Latency: Is response time elevated?
   - Traffic: Is request rate anomalous?
   - Errors: Is error rate above threshold?
   - Saturation: Is any resource exhausted?

2. **The Five Whys** — progressive root cause drilling:
   - Why did the alert fire? → Error rate spiked
   - Why did errors spike? → Timeouts from auth service
   - Why auth service timing out? → Connection pool exhausted
   - Why pool exhausted? → New deployment changed pool size
   - Why was pool size changed? → Config drift in deployment template

3. **The Differential Diagnosis** — rule out common causes:
   - Recent deployment? Check deploy log
   - Config change? Check config history
   - Dependency issue? Check upstream health
   - Capacity issue? Check resource metrics
   - Network issue? Check connectivity between services

### Phase 3: Mitigation

Execute mitigation steps with **human approval at each gate**:

1. **Contain** — Stop the bleeding (rate-limit, circuit-break, shed load)
2. **Mitigate** — Restore service (rollback, scale up, failover)
3. **Verify** — Confirm recovery (check SLOs, run health checks)
4. **Communicate** — Update status page and stakeholders

### Phase 4: Resolution

After the incident is resolved:

1. **Verify full recovery** — all SLOs green for 15+ minutes
2. **Document timeline** — timestamped actions and decisions
3. **Create follow-up tickets** — prevent recurrence
4. **Archive incident artifacts** — logs, graphs, chat transcripts

## Postmortem Template

Generate blameless postmortems following Google's template:

```markdown
# Postmortem: [Incident Title]

**Date:** YYYY-MM-DD
**Severity:** SEV0/1/2
**Duration:** Xh Ym (HH:MM UTC to HH:MM UTC)
**Authors:** [Names]
**Status:** Draft / Review / Final

## Summary
[One paragraph — what happened, impact, duration]

## Timeline (UTC)
| Time | Event |
|------|-------|
| 14:32 | Alert fired: error rate >5% on api-gateway |
| 14:33 | On-call acknowledged |
| 14:38 | Identified: connection pool exhaustion |
| 14:42 | Rolled back deployment v2.4.1 → v2.4.0 |
| 14:47 | Error rate normalized; SLO recovered |

## Root Cause
[Technical explanation — what failed and why]

## Impact
- Users affected: [count or %]
- Revenue impact: [$ or N/A]
- SLO impact: [which SLO, how much burned]

## Detection
- How was it detected? (alert, user report, partner)
- Time to detect: X minutes
- Could detection have been faster?

## Resolution
[Steps taken to resolve — be specific]

## Action Items
| # | Action | Owner | Priority | Due |
|---|--------|-------|----------|-----|
| 1 | Fix connection pool default | @engineer | P0 | EOW |
| 2 | Add alert on pool saturation | @sre | P1 | Sprint |
| 3 | Update deployment checklist | @team | P2 | Month |

## Lessons Learned
- What went well?
- What went poorly?
- Where did we get lucky?
```

## Runbook Template

```markdown
# Runbook: [Service Name] — [Failure Mode]

**Owner:** [Team]
**Last Updated:** YYYY-MM-DD
**Severity:** [Expected severity when this runbook is needed]

## Symptoms
- [Alert name(s) that fire]
- [Observable symptoms — metrics, logs, user reports]

## Prerequisites
- [Access needed: VPN, jump host, cluster, dashboard URLs]
- [Credentials: which tokens/roles, NOT actual values]

## Investigation Steps
1. [Check dashboard X for metric Y]
2. [Run query: SELECT ... FROM ... WHERE ...]
3. [Check recent deployments: kubectl rollout history ...]
4. [...]

## Mitigation Steps
### Quick Fix (stop the bleeding)
1. [Action] → Expected result: [what you should see]
2. [Action] → Expected result: [...]

### Full Resolution
1. [Action with rollback command]
2. [...]

## Verification
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [SLO dashboard shows recovery]

## Escalation
- If [condition]: escalate to [team/on-call rotation]
- If unresolved after [N] minutes: page [escalation contact]
```

## On-Call Handover Template

```markdown
# On-Call Handover — YYYY-MM-DD

**From:** [Outgoing]
**To:** [Incoming]
**Shift:** [Hours covered]

## Active Incidents
| ID | Title | Severity | Status | Action needed |
|----|-------|----------|--------|---------------|
| INC-123 | API latency | SEV2 | Mitigating | Monitor for 24h |

## Known Issues (Watch List)
- [Service X] has been flapping on deploys — may need rollback
- [Alert Y] is noisy — ticket filed to tune threshold

## Upcoming Changes
- [Service A] deployment scheduled Tue 10:00 UTC
- [Infra B] maintenance window Thu 02:00-04:00 UTC

## Open Questions
- [Question that needs follow-up]
```

## Platform Notes

- **All platforms:** This skill provides procedural knowledge — no binary
  dependencies required. The agent applies the patterns using its existing
  tools (shell, kubectl, terraform, monitoring APIs).
- **Safety:** The risk-tier L2 designation ensures agents pause for human
  approval before any destructive action. Platform runtimes should enforce
  this through their native approval mechanisms.
- **OpenClaw:** Compatible with native approval gates and elevated-tool controls.
