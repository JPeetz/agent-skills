# Incident Response Guide

Incident classification, Incident Commander roles, communication templates, and postmortem structure for production incidents.

---

## Table of Contents

1. [Incident Classification](#1-incident-classification)
2. [Incident Command System](#2-incident-command-system)
3. [Communication Templates](#3-communication-templates)
4. [Timeline Reconstruction](#4-timeline-reconstruction)
5. [Postmortem Structure](#5-postmortem-structure)
6. [Incident Response Playbooks by Scenario](#6-incident-response-playbooks-by-scenario)
7. [Post-Incident Review Cadence](#7-post-incident-review-cadence)

---

## 1. Incident Classification

### 1.1 Severity Levels

| Level | Label | Definition | Response | Communication | Example |
|-------|-------|-----------|----------|---------------|---------|
| **SEV0** | Critical | Complete system outage, data loss, security breach, or active exploit affecting all users | Immediate. On-call paged. Company-wide comms. | Status page update every 30 minutes. Executive notified. | Payment service down for all users, database corruption, active DDoS |
| **SEV1** | High | Major feature broken, >50% error rate on critical path, SLO budget burning at >10x rate | Page within 5 minutes. Full team mobilized. | Status page update every 1 hour. Engineering manager notified. | Checkout flow returning 500s for 60% of users, search completely broken |
| **SEV2** | Medium | Partial degradation affecting subset of users, single endpoint or region impacted | Page within 30 minutes. Small response team. | Status page update every 4 hours. Team lead notified. | Reports page slow (>5s load), EU region has elevated error rate |
| **SEV3** | Low | Minor issue, no immediate user impact, cosmetic bugs | Ticket created. SLA 24-hour response. | No status page update. Create ticket in tracking system. | Dashboard stats are 15 minutes behind, typo in welcome email |
| **SEV4** | Info | Non-urgent observability, upcoming deprecations, capacity warnings | No response needed. | Document and monitor. | SSL certificate expires in 30 days, disk usage at 75% |

### 1.2 Escalation Matrix

```
Detected Issue
       │
       ├── User-facing? ──── No ──→ SEV3/SEV4
       │
       ├── Yes
       │
       ├── All users? ────── Yes ──→ SEV0
       │
       ├── Some users (>10%)? ── Yes ──→ SEV1
       │
       ├── Single feature? ── Yes ──→ SEV2
       │
       └── Single user? ──── Yes ──→ SEV3
```

### 1.3 Incident Triggers (When to Declare)

| Trigger | Severity | Example |
|---------|----------|---------|
| SLO budget exhaustion imminent (<1h) | SEV0 | Burn rate 720x, 1 hour to exhaustion |
| Complete service outage | SEV0 | Homepage returns 503, all routes down |
| >50% error rate on critical endpoint | SEV1 | Checkout 62% error rate |
| Data loss detected | SEV0 | Database table truncated, S3 bucket deleted |
| Security breach/exploit | SEV0 | Unauthorized DB access, API key leaked |
| sLO burn rate at 14.4x | SEV1 | Fast burn alert firing, not yet critical |
| Single endpoint degraded | SEV2 | Reports page loading 5x slower |
| Capacity warning | SEV3 | DB connection pool at 85% |
| Certificate expiring <14 days | SEV3 | SSL cert expires in 10 days |

---

## 2. Incident Command System

### 2.1 Roles and Responsibilities

#### Incident Commander (IC)

**Primary responsibility: Coordination, not resolution.**

- Declares the incident and assigns severity
- Creates and manages the incident channel
- Assigns roles: Ops Lead, Comms Lead, Scribe
- Ensures the team is working on the right things
- Decides when to escalate (severity bump)
- Tracks timeline and decisions
- Decides when incident is resolved
- Schedules the postmortem

**The IC should NOT:**
- Debug the issue (leave that to Ops Lead)
- Code fixes
- Multi-task — IC is a single-threaded role

#### Ops Lead

- Investigates the root cause
- Implements mitigation / fix
- Runs diagnostic queries
- Has authority to rollback, feature-flag, restart
- Reports findings to IC for comms

#### Comms Lead

- Drafts and sends status updates in the incident channel
- Updates status page (e.g., Statuspage.io)
- Notifies stakeholders (engineering managers, product, executives for SEV0/SEV1)
- Handles external communication for SEV0

#### Scribe

- Records every action, finding, and decision with timestamps
- Maintains the incident timeline document
- Tracks which commands were run (for reproducibility)
- Archives logs, screenshots, and relevant observability data

### 2.2 Incident Channel Setup

When an incident is declared, create a dedicated Slack channel (or equivalent):

```
#inc-{yyyymmdd}-{short-description}
#inc-20260618-payment-timeout
```

**Channel Topic:**
```
SEV1 | IC: @jane | Ops: @bob | Comms: @alice | Status: investigating
SLO: 14.4% budget consumed | TTR so far: 12m
```

**Pinned items:**
1. Link to runbook
2. Zoom/facetime link
3. Link to live dashboard
4. Current runbook/checklist

### 2.3 Role Handoff Protocol

When a shift change or handoff is needed:

```
**HANDOFF: IC from @jane → @mike**
Time: 2026-06-18T14:30:00Z

Status: Service recovered (14:22 UTC), monitoring
SLO budget consumed: 14.4%

What we know:
  - Cause: v2.4.1 deploy introduced memory leak in payment worker
  - Fix: Rolled back to v2.4.0
  - False: Observability dashboard showing pre-rollback edge

What's left:
  - Wait 1h to confirm no secondary effects
  - Update the runbook with this incident
  - Ensure incident channel summary posted to #engineering

Handoff complete: @jane → @mike
```

---

## 3. Communication Templates

### 3.1 Incident Declaration

```
🚨 INCIDENT DECLARED
─────────────────────
Title:       {Payment service timeout}
Severity:    SEV1 (High)
Status:      Investigating
Incident:    #inc-20260618-payment-timeout
IC:          @jane
Ops Lead:    @bob
Comms Lead:  @alice
Scribe:      @carol

Description:
  Payment API is returning 503 errors for ~60% of requests.
  Latency spiked from 200ms to >30s at 14:03 UTC.

Customer Impact:
  Users cannot complete checkout.
  Cart and catalog pages are unaffected.

Detection:
  Grafana Alert: SLOErrorBudgetBurnCritical fired at 14:04 UTC.
  Monitor: payment-error-rate (threshold: 1%, actual: 18%).

Timeline (so far):
  14:00 UTC - Deploy v2.4.1 initiated
  14:03 UTC - Latency spike detected
  14:04 UTC - Burn rate alert fired
  14:07 UTC - Incident declared

Go-to Channel: #inc-20260618-payment-timeout
```

### 3.2 Status Update Template

```
📊 INCIDENT UPDATE
───────────────────
Title:       {Payment service timeout}
Update:      #{1}

Status:      [Investigating | Mitigating | Resolved | Monitoring]
Duration:    {14:07 UTC → ongoing, elapsed: 23m}

Current Understanding:
  • Performance regression isolated to payment-worker v2.4.1
  • Newrelic query shows memory leak in payment-gateway-http module
  • Rollback of payment-worker started

Actions Taken:
  • Deployed payment-worker v2.4.0 (previous stable) at 14:25 UTC
  • Metrics beginning to stabilize — error rate dropping from 18% → 5% → 2%

Next Steps:
  • Wait for full completion of rollback to all pods (~5 min)
  • Verify error rate returns to <0.1% baseline
  • Root cause investigation of memory leak in v2.4.1

ETA:
  Estimated resolution: 14:35 UTC

Need Help?
  • If you have relevant context, post in the incident channel
  • This is your only source of truth — do not disseminate outside this channel
```

### 3.3 Incident Resolution

```
✅ INCIDENT RESOLVED
─────────────────────
Title:       {Payment service timeout}
Severity:    SEV1 (High)
Start:       14:03 UTC
Resolved:    14:30 UTC
Duration:    27 minutes

Customer Impact:
  • 60% of checkout requests failed (estimated 2,100 failed transactions)
  • Users saw "payment processing error" messages
  • No data loss — all failed requests logged and queued for retry
  • Error budget consumed: 14.4% of monthly budget

Root Cause:
  Introduction of connection pool leak in payment-worker v2.4.1:
  - Commit `a3b21c9` added a new HTTP client that wasn't closed after requests
  - Caused connection pool exhaustion after ~3 minutes of production traffic
  - All subsequent connections timed out → cascading failure

Fix:
  Rolled back payment-worker from v2.4.1 → v2.4.0 (14:25 UTC)
  Metrics recovered by 14:30 UTC.

Postmortem:
  Scheduled: 2026-06-19 15:00 UTC
  Channel:   #inc-20260618-payment-timeout
  Ticket:    INC-20260618

Thank you to the response team: @jane (IC), @bob (Ops), @alice (Comms), @carol (Scribe)
```

### 3.4 Stakeholder Notification (SEV0/SEV1)

```
⚠️ INCIDENT NOTIFICATION — {title}
─────────────────────────────────────
Audience:  Engineering Managers / Executives
Severity:  SEV1

What happened:
  {2-3 sentence summary — no technical jargon}

Customer Impact:
  • {who is affected and how}

Current Status:
  {investigating / mitigated / resolved}

Response Team:
  {IC name} leading, {N} engineers engaged

Next Update:
  {time of next update or "No further updates expected"}
```

### 3.5 External / Customer Communication (SEV0 only)

```
STATUS PAGE UPDATE
───────────────────
Date: {2026-06-18}
Time: {14:30 UTC}

We are currently investigating reports of degraded performance
affecting our payment processing. Some users may experience
errors during checkout. We are working to restore full service
and will provide an update within 30 minutes.

— {Company} Status
```

---

## 4. Timeline Reconstruction

### 4.1 Timeline Template

```markdown
## Incident Timeline: {Payment service timeout}
**Date:** 2026-06-18
**Severity:** SEV1

| Time (UTC) | Event | Source | Actor | Evidence |
|------------|-------|--------|-------|----------|
| 14:00:00 | Deploy v2.4.1 started | CI/CD pipeline | @engineer | [link to pipeline run] |
| 14:02:15 | deploy completed | CI/CD pipeline | @engineer | [link to deploy log] |
| 14:03:02 | Latency spike: p99 >30s (baseline 200ms) | Grafana alert | System | [grafana link] |
| 14:03:45 | Error rate >15% | Grafana alert | System | [grafana link] |
| 14:04:12 | SLOErrorBudgetBurnCritical alert fired | Alertmanager | System | [alert link] |
| 14:05:00 | @bob checks Grafana → sees payment-worker latency | Manual | @bob | - |
| 14:07:00 | @jane declares SEV1, creates #inc-20260618-payment-timeout | Slack | @jane | [link] |
| 14:08:00 | Ops Lead @bob begins investigating payment-worker | Manual | @bob | - |
| 14:10:00 | @alice sets up status page | Statuspage | @alice | [status link] |
| 14:12:00 | @bob finds v2.4.1 added new HTTP client (not closed) | Code review | @bob | [commit link] |
| 14:14:00 | Decision: roll back to v2.4.0 | Slack | @jane | [decision post] |
| 14:15:00 | Rollback initiated | CI/CD | @ops-lead | [pipeline link] |
| 14:18:00 | Error rate dropping: 15% → 5% → 2% | Grafana | System | [grafana link] |
| 14:22:00 | Error rate <0.1%, latency back to baseline | Grafana | System | [grafana link] |
| 14:25:00 | Rollback completed — all pods on v2.4.0 | CI/CD | System | [deploy log] |
| 14:30:00 | @jane declares resolved, posts resolution | Slack | @jane | [resolution post] |
| 14:35:00 | Status page updated to "Resolved" | Statuspage | @alice | [status link] |
```

### 4.2 Key Metrics

```
Detection Metrics:
  Time to Detect (TTD):  = 14:03 - 14:00 = 3 minutes
  Time to Acknowledge:   = 14:07 - 14:04 = 3 minutes (alert → declare)
  Time to Respond (TTRD): = 14:07 - 14:00 = 7 minutes (cause → IC assigned)

Resolution Metrics:
  Time to Mitigate:      = 14:02 - 14:15 = 13 minutes (deploy → rollback start)
  Time to Resolve (TTR): = 14:30 - 14:00 = 30 minutes (total incident duration)
  Time to Recover:       = 14:22 - 14:02 = 20 minutes (deploy → metrics recovered)

Impact Metrics:
  Errors served:        ~2,100 failed requests
  Error budget used:    14.4%
  Users affected:       ~1,800
  Revenue impact:       12 min× (680 transactions/min × $45 avg order) × 60% error rate
                       = loss estimate
```

### 4.3 Automated Timeline Collection

**Enhance timeline collection with automation:**

```bash
# Gather data points for timeline reconstruction

# 1. Pull deploy events from CI/CD
# 2. Pull alert firings from Alertmanager API
# 3. Pull dashboard snapshots (Grafana API)
# 4. Pull Slack messages from incident channel
# 5. Extract timestamps from logs for key events

# Example: query Alertmanager for alert firings
curl -s "http://alertmanager:9093/api/v2/alerts?silenced=false&inhibited=false" \
  | jq '[.[] | {name: .labels.alertname, start: .startsAt, end: .endsAt, severity: .labels.severity}]'
```

---

## 5. Postmortem Structure

### 5.1 Postmortem Template

```markdown
---
title: "Postmortem: {incident_title}"
date: {YYYY-MM-DD}
authors: [{names}]
severity: {SEV0/SEV1/SEV2}
status: draft # Publish after approved
---

# Postmortem: {incident_title}

**Date:** {YYYY-MM-DD}
**Authors:** {names}
**Severity:** {SEV0/SEV1/SEV2}
**Incident Duration:** {start_datetime} → {end_datetime}
**Detection:** {manual / automated alert}
**TTD (Time to Detect):** {X minutes}
**TTR (Time to Resolve):** {X minutes}

## Summary

{2-3 sentences. What happened? What was the impact?}

## Customer Impact

- **Affected users:** {estimated count or percentage}
- **Affected functionality:** {specific features/components impacted}
- **Degradation type:** {latency / errors / complete outage / data loss}
- **Error budget impact:** {X% of monthly budget consumed}
- **Revenue impact:** {estimated loss, if applicable}

## Timeline

| Time (UTC) | Event | Source |
|------------|-------|--------|
| {HH:MM} | {description} | {system/person} |

*Full timeline in Appendix A if it exceeds 15 rows.*

## Root Cause Analysis

### Direct Cause
{The technical failure that triggered the incident. One paragraph.}

### Triggering Event
{What started the chain of events. E.g., a deploy, config change, upstream failure.}

### Contributing Factors

| Factor | Description | Classification |
|--------|-------------|----------------|
| {Factor 1} | {Why this contributed} | Process / Technology / People |
| {Factor 2} | {Why this contributed} | Process / Technology / People |

### Why Chain (5 Whys)

```
Why 1: Users saw 503 errors during checkout.
Why 2: Payment-worker could not handle requests.
Why 3: Worker ran out of database connections.
Why 4: Connection pool was exhausted by connections that were never closed.
Why 5: New HTTP client in v2.4.1 was not configured with a connection timeout
       or close-after-use pattern.

Root Cause: Missing connection lifetime management in the new HTTP client.
```

## Detection

| Metric | Value |
|--------|-------|
| First alert fired at | {HH:MM} |
| Incident declared at | {HH:MM} |
| Time to detect | {X minutes} |
| How was it detected? | {Grafana alert / customer report / automated health check} |
| Could detection be faster? | {Yes/No} — {How: e.g., add synthetic monitoring, tune thresholds} |

## Resolution

| Metric | Value |
|--------|-------|
| Mitigation started at | {HH:MM} |
| Service recovered at | {HH:MM} |
| Time to resolve | {X minutes} |
| What action resolved it? | {Rollback, feature flag, config change, restart} |
| Was any data lost? | {Yes/No — details if yes} |
| Was a hotfix required? | {Yes/No} |

## Lessons Learned

### What Went Well
- {The alert fired within 3 minutes of the deploy — fast detection}
- {Rollback pipeline completed in 13 minutes — excellent automation}
- {Team communication in the incident channel was clear}
- {Runbook for payment degradation was up-to-date}

### What Went Poorly
- {No canary deploy to catch the issue before production}
- {The memory leak was not caught in staging because request volume was too low}
- {Incident channel wasn't created until 4 minutes after the first alert}
- {Runbook didn't cover connection pool exhaustion symptoms}

### Where We Got Lucky
- {The leak only affected one worker type — could have been worse}
- {Incident happened during business hours with full team available}
- {No data loss — all failed requests were safely queued for retry}

## Action Items

| ID | Priority | Action | Owner | Due | Tracker |
|----|----------|--------|-------|-----|---------|
| INC-001 | P0 | Add connection timeout and close-after-use to all HTTP clients | @bob | 7 days | [JIRA-123] |
| INC-002 | P1 | Implement canary deploys (5% traffic before full rollout) | @jane | 14 days | [JIRA-124] |
| INC-003 | P1 | Add connection pool exhaustion dashboard panel | @carol | 7 days | [JIRA-125] |
| INC-004 | P2 | Write runbook section for connection pool symptoms | @alice | 14 days | [JIRA-126] |
| INC-005 | P0 | Enable automated rollback on SLO burn rate > 10x | @bob | 21 days | [JIRA-127] |

## Appendices

### Appendix A: Full Timeline
{Complete timeline from the incident channel, chronologically ordered}

### Appendix B: Relevant Dashboards
- [ ] Dashboard links with time ranges set to incident window
- {Grafana: payment-service-overview?from=14:00&to=14:35}

### Appendix C: Affected Systems
- {List all affected services, versions, and hostnames}

### Appendix D: Related Changes
- {PR links for the deploy that caused the incident}
- {PR links for the fix}
- {Link to incident channel archive}
```

### 5.2 Postmortem Best Practices

| Do ✅ | Don't ❌ |
|------|---------|
| Focus on the system, not the person | Assign blame or use accusatory language |
| Include evidence: logs, dashboards, screenshots | Make claims without data |
| Distinguish between cause and symptom | Mix timeline with analysis |
| Assign owners AND due dates to action items | Leave action items vague or ownerless |
| File action items at multiple levels (fast fix + systemic improvement) | Only fix the immediate cause |
| Publish promptly (within 1 week), even if rough | Wait for "perfect" analysis |
| Review action items at the next postmortem's follow-up | Write and abandon |

### 5.3 Postmortem Review Checklist

```
☐ Blameless language reviewed
☐ Timeline verified against Slack + monitoring data
☐ Customer impact quantified
☐ Action items have owners and due dates
☐ P0 items are already in progress
☐ Dashboard links point to specific time ranges
☐ Incident channel logs archived
☐ Stakeholders notified of postmortem publication
```

---

## 6. Incident Response Playbooks by Scenario

### 6.1 Service Degraded (High Latency / Errors)

```
1. IC: Declare incident (SEV1/SEV2 based on impact)
2. Ops: Check SLO dashboards → identify affected service
3. Ops: Check recent deploys (last 1 hour)
   - If recent deploy → rollback immediately
   - If no deploy → check upstream dependencies
4. Ops: Check infrastructure alerts (CPU, memory, connections)
5. Ops: Check external dependencies (cloud provider status, 3rd party APIs)
6. Comms: Post "investigating" status update
7. IC: Escalate if not mitigated within SLO response time
```

### 6.2 Complete Outage

```
1. IC: Declare SEV0 immediately
2. Ops: Verify from multiple sources (not a false alarm)
3. Comms: Update status page to "Major Outage"
4. Ops: Check infrastructure → are servers reachable?
   - DNS resolves? Load balancers healthy? Database accessible?
5. Ops: Check cloud provider status for region-level issues
6. Ops: If cloud issue → no fix, wait for provider
7. Ops: If code/infra issue → rollback or failover
8. IC: Every 30 min: "Is this still an active issue?"
9. Ops: Confirm recovery → IC declares resolved
```

### 6.3 Data Loss

```
1. IC: Declare SEV0 — highest priority
2. Ops: IMMEDIATELY: Stop all writes to affected storage
3. Ops: Take snapshot / backup of current state
4. Ops: Determine scope — what data, how many records, time window
5. Ops: Check backup status — can we restore?
6. Ops: Determine restore method + estimated time
7. IC: Coordinate restore window with business (may need read-only mode)
8. IC: Exec + Product comms: what was lost, what's the recovery plan
9. Ops: Execute restore, verify data integrity
10. Postmortem: MUST include root cause of data loss + redundancy gap
```

### 6.4 Security Breach

```
1. IC: Declare SEV0, notify security team
2. Security: Determine scope — what data/system was accessed
3. Security: Contain — rotate keys, block IPs, isolate systems
4. IC: NOTIFY LEGAL immediately — regulatory obligations may apply
5. IC: Coordinate with Comms for any public statement
6. Security: Collect evidence — logs, access records, timelines
7. Security: Root cause — how did the breach occur?
8. Postmortem: MUST include external disclosure timeline if applicable
```

### 6.5 Dependency / Upstream Failure

```
1. IC: Declare SEV2 initially, escalate if critical
2. Ops: Confirm upstream is the issue (not us)
3. Ops: Enable fallback/cached response if available
4. Ops: Set up degraded experience — communicate to users
5. Ops: Monitor upstream status page for resolution
6. Comms: Update status page — "Degraded due to upstream provider issue"
7. Postmortem: Can we add a fallback? Degraded UX?
```

---

## 7. Post-Incident Review Cadence

### 7.1 After Incident: Immediate

| Action | Owner | Deadline |
|--------|-------|----------|
| Post resolution to incident channel | IC | Within 15 min of resolution |
| Archive incident channel | Scribe | Within 1 hour |
| File action items from what was learned during incident | IC | Within 24 hours |
| Schedule postmortem (within 5 days) | IC | Within 24 hours |

### 7.2 Postmortem Preparation

| Action | Owner | Deadline |
|--------|-------|----------|
| Reconstruct timeline from incident channel | Scribe | 48 hours before PM |
| Gather dashboard screenshots / links | Ops | 48 hours before PM |
| Draft root cause analysis | Ops | 24 hours before PM |
| Pre-read postmortem draft to IC | Scribe | 24 hours before PM |

### 7.3 Postmortem Meeting Agenda (30-60 min)

```
1. Summary (5 min)
   - What happened? What was the impact?

2. Timeline Walkthrough (10 min)
   - Key events, decisions, timing

3. Root Cause + Contributing Factors (10 min)
   - Direct cause, contributing factors, 5 whys

4. Lessons Learned (10 min)
   - What went well, what went poorly

5. Action Items (10 min)
   - Review, assign owners and due dates

6. Follow-up Schedule (5 min)
   - When do we check P0/P1 action items?
```

### 7.4 Follow-Up Cadence

| Interval | Activity |
|----------|----------|
| Postmortem + 2 weeks | Check P0 action items due. IC follows up. |
| Postmortem + 1 month | All action items review. Close or escalate overdue items. |
| Quarterly | Review action item completion rate by team. |
| Quarterly | Review incident trends — are SLO improvements translating to fewer incidents? |

---

## References

- [Google SRE Workbook — Incident Response](https://sre.google/workbook/incident-response/)
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)
- [Atlassian Incident Management Handbook](https://www.atlassian.com/incident-management/handbook)
- [The Incident Command System for Ops](https://www.pagerduty.com/blog/incident-command-system-at-pagerduty/)
