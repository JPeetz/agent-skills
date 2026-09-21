# Error-Specific Debugging Strategies

Supplement to the main SKILL.md — deeper patterns for common failure modes.

## Test Failure Deep Dive

### When Tests Pass in Isolation but Fail in Suite

```
Tests fail in suite but pass alone:
├── Shared state pollution
│   ├── Tests modify global/module-level state without cleanup
│   ├── Database/test fixtures are not isolated between tests
│   └── Singletons cache stale data from a previous test
├── Test ordering dependency
│   ├── Test B depends on state set by Test A
│   └── Tests assume alphabetical or insertion-order execution
└── Resource contention
    ├── Port already in use from a previous test
    ├── File locks not released
    └── Thread pool exhausted
```

**Fix pattern:** Use `pytest --random-order` or `jest --randomize` to surface order dependencies. Each test must `setUp` its own world and `tearDown` completely.

### When Tests Fail Only in CI

```
Fails in CI, passes locally:
├── Environment mismatch
│   ├── Different dependency versions (check lockfile vs installed)
│   ├── Different OS or language runtime
│   └── Different timezone, locale, or encoding
├── Resource differences
│   ├── CI has less memory/CPU → timeouts or OOM
│   ├── CI has no network access → external API calls fail
│   └── CI has different filesystem permissions
└── Secret/configuration differences
    ├── Missing environment variables
    ├── Different database credentials or empty database
    └── Feature flags toggled differently
```

**Fix pattern:** Run the test exactly as CI runs it — same command, same env. Use `act` (GitHub Actions locally) or replicate the CI Docker image.

## Build Failure Deep Dive

### Type Errors

```
Type error:
├── Missing type stub or declaration file
│   └── Install or generate the type definition
├── Function signature changed but callers not updated
│   └── Check all call sites (use your language's find-references)
├── Conditional type not narrowed properly
│   └── Add explicit type guard or assertion
└── Generic type parameter mismatch
    └── Verify the concrete type satisfies the generic constraint
```

### Import/Module Errors

```
Module not found:
├── File doesn't exist
│   └── Check filename case (case-sensitive filesystems!)
├── File exists but not in module search path
│   └── Add __init__.py, fix tsconfig paths, update PYTHONPATH
├── Circular import
│   └── Break the cycle: extract shared dependency into a new module
├── Named export doesn't exist
│   └── Check the actual export name from the source module
└── Package not installed
    └── Run package manager install, check lockfile
```

## Runtime Error Deep Dive

### Null/Undefined Reference

```
Cannot read property 'x' of undefined:
├── The value is never set
│   └── Trace back: where should this value be initialized?
├── The value is set asynchronously but read synchronously
│   └── Add await, callback, or reactive subscription
├── The value is conditionally set and the condition failed
│   └── Check all branches that should set this value
└── The value was set but later deleted/overwritten
    └── Check for mutations, reassignments, or cache evictions after the set
```

### Network Errors

```
Network request failed:
├── Host unreachable
│   └── Check DNS, VPN, firewall, proxy settings
├── Connection refused
│   └── Is the server running? Is the port correct?
├── TLS/SSL error
│   └── Check certificate expiry, hostname mismatch, CA bundle
├── Timeout
│   └── Server overloaded, request too slow, timeout too short
└── CORS error (browser only)
    └── Server must send Access-Control-Allow-Origin header matching the request origin
```

## Production Incident Deep Dive

### Monitoring Before Action

Before touching production, check:
1. **Dashboards:** Latency, error rate, throughput, saturation
2. **Logs:** Recent errors at the affected service
3. **Alerts:** What triggered? What's the threshold?
4. **Recent changes:** Deploys, config changes, dependency updates, data migrations

### The Rollback Decision

```
Should we roll back?
├── Is the issue caused by a recent deploy (last 1 hour)?
│   └── → Roll back immediately. Diagnose post-rollback.
├── Is the issue data corruption that a rollback won't fix?
│   └── → Restore from backup instead.
├── Is the issue a gradual degradation (no single deploy)?
│   └── → Diagnose in-place; rollback won't help.
└── Is the fix obvious and safe to push directly?
    └── → Hotfix, but with expedited review.
```

### Post-Incident Activities

1. **Document the timeline:** When did it start? When was it detected? When was it mitigated?
2. **Write the postmortem:** What happened? Why? What prevented detection? What prevented mitigation?
3. **Add monitoring:** If a similar issue would go unnoticed again, add an alert.
4. **Run a recurrence drill:** Can you reproduce the incident scenario in staging?

## Instrumentation Guidelines

Add logging only when it helps. Remove it when done.

**When to add instrumentation:**
- You can't localize the failure to a specific line
- The issue is intermittent and needs monitoring
- The fix involves multiple interacting components

**When to remove it:**
- The bug is fixed and tests guard against recurrence
- The log is only useful during development (not in production)
- It contains sensitive data (always remove sensitive data)

**Permanent instrumentation (keep):**
- Error boundaries with error reporting
- API error logging with request context
- Performance metrics at key user flows