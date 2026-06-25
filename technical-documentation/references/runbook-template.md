# Runbook Template

Use this template for every operational runbook. Copy the structure, fill in
the details, and review after every incident.

---

```markdown
# Runbook: [Service Name] — [Incident / Procedure Name]

- **Owner**: [team or individual]
- **Last tested**: YYYY-MM-DD
- **Next review**: YYYY-MM-DD (quarterly, or after next incident)
- **Linked alerts**: [Alert names and sources]

---

## Overview

[One paragraph describing what this runbook covers. What kind of incident?
What's the typical trigger? When should someone reach for this runbook?]

---

## Symptoms

### Alert Triggers

- **Alert**: `[alert name]` from [monitoring system]
  - Threshold: [metric] > [value] for [duration]
  - Severity: [SEV1 / SEV2 / SEV3]

### User Reports

- "I see [error message] when I try to [action]"
- "[Feature] is slow / not responding"
- "[Specific error code or behavior]"

### Metrics Dashboard

- Dashboard: [link]
- Key metric 1: [name] — normal range: [min-max]
- Key metric 2: [name] — normal range: [min-max]

---

## Impact

- **What breaks?** [Description of affected functionality]
- **Who is affected?** [Internal teams / external users / specific regions]
- **Blast radius:** [What else could cascade?]

---

## Severity Classification

- **SEV1** (Critical): [conditions] — **Page on-call immediately**
  - Example: Complete service outage, data loss, security breach
- **SEV2** (Major): [conditions] — **Page during business hours**
  - Example: Partial outage, degraded performance, non-critical feature broken
- **SEV3** (Minor): [conditions] — **Create ticket, no page**
  - Example: Cosmetic issue, non-blocking bug, performance within SLA

---

## Prerequisites

Before executing this runbook, you need:

- **Access to**: [list of dashboards, tools, SSH hosts]
- **Permissions**: [required IAM roles, AWS/GCP accounts, admin access]
- **Tools installed**: [CLI tools, scripts needed]

---

## Diagnostic Steps

Perform these steps in order. At each step, document your findings.

### Step 1: Check [Dashboard / Metric]

1. Open [dashboard link]
1. Check [metric name]
   - **Normal**: [expected value or range]
   - **Abnormal**: [what to look for]
1. If abnormal: note the value and proceed to Step 2.
   - If normal: this may not be the right runbook. Check [alternative].

### Step 2: Run Diagnostic Command

```bash
[command to run] [--flags]
```

- **Expected output**: [what normal looks like]
- **Red flags**: [what an issue looks like]
- **If the output shows [X]**: proceed to Mitigation → [section].

### Step 3: Check Logs

1. Open [log aggregation tool] at [link]
1. Search for: `[search query]`
1. Look for: [error patterns, stack traces, timing anomalies]
1. Time range: [last N minutes / since incident start]

---

## Mitigation

### ⚠️ First Response (≤ 5 minutes)

Goal: Stop the bleeding. Restore service, even with reduced functionality.

1. [Immediate action — e.g., restart service, fail over, scale up]
   ```bash
   [command]
   ```
1. Verify: [how to confirm the action worked]
1. If unsuccessful after [N] minutes: escalate to [person/team].

### Short-Term Fix

Goal: Restore full functionality with a workaround.

1. [Workaround step]
1. [Verification step]
1. Document the workaround in [ticket/issue tracker].

### Long-Term Fix

Goal: Permanent resolution.

- Issue: [link to ticket]
- Owner: [person/team]
- Target date: YYYY-MM-DD

---

## Verification

After mitigation, confirm the incident is resolved:

- [ ] [Metric] has returned to normal range ([min-max])
- [ ] [Health check endpoint] returns `200 OK`
- [ ] Users can [perform critical action]
- [ ] [Downstream service] is receiving traffic normally
- [ ] No new errors in logs for [N] minutes

---

## Escalation

If mitigation fails or the situation worsens:

| After | If | Escalate to |
|-------|----|------------|
| 15 minutes | Issue unresolved | [Secondary on-call] |
| 30 minutes | Issue unresolved | [Engineering manager] |
| 60 minutes | SEV1 with user impact | [VP Engineering / Director] |
| Anytime | Data loss suspected | [Security team] |
| Anytime | Legal/compliance risk | [Legal team] |

### Escalation Contacts

| Name | Role | Phone | Email | PagerDuty |
|------|------|-------|-------|-----------|
| [Name] | [Role] | [Phone] | [Email] | [PagerDuty] |
| [Name] | [Role] | [Phone] | [Email] | [PagerDuty] |

---

## Post-Incident

After the incident is resolved:

1. **Create a postmortem** in [postmortem tool/location]
   - Link: [postmortem template]
1. **File follow-up issues**:
   - [ ] [Issue 1 description] → [link]
   - [ ] [Issue 2 description] → [link]
1. **Update this runbook** with lessons learned
   - What diagnostic step would have been faster?
   - What information was missing during the incident?
   - Did escalation contacts respond as expected?

---

## Appendix

### Useful Commands

```bash
# Check service status
[command]

# View recent logs
[command]

# Check database connections
[command]

# Verify configuration
[command]
```

### Common Error Messages

| Error | Meaning | Action |
|-------|---------|--------|
| `[error 1]` | [explanation] | [what to do] |
| `[error 2]` | [explanation] | [what to do] |

### Related Runbooks

- [Runbook: Related Incident A](link)
- [Runbook: Related Incident B](link)
```

---

## Usage Notes

1. **Copy the template** — don't modify it. Fill in a copy.
2. **Replace ALL bracketed placeholders** `[like this]`. An incomplete runbook
   is worse than no runbook — it wastes time during an incident.
3. **Test the diagnostic commands** before publishing. If a command doesn't
   work or returns different output, fix it before the incident.
4. **Review after every incident**. Add what you learned. Remove what was
   wrong. Runbooks improve through use, not through planning.
5. **Never include credentials, API keys, or internal IPs** in runbooks. Use
   references to secret managers or env vars.
6. **Precede destructive commands with a ⚠️ warning**. If someone running this
   runbook at 3 AM can accidentally delete production data, the runbook is
   dangerous.

---

*Template version: 1.0.0 — Last updated: 2026-06-23*