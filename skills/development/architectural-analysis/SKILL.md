---
name: architectural-analysis
description: >-
  Use when auditing a requested codebase scope for structural risks such as unclear ownership, duplication, cycles, dead code, or costly change patterns. Not for security audits, performance profiling, routine feature review, or executing the cleanup — repo-cleanup owns removal.
disable-model-invocation: true
argument-hint: "[scope] [--out <file>]"
---

# Architectural Analysis

Use this workflow when the user asks for an architecture or maintainability
audit. First identify the repository's boundaries and the requested scope. A
narrow request can be answered directly; for a broad audit, save a report under
`.audits/architecture/<UTC timestamp>/` unless the user names another path.

Look for concrete evidence of unclear ownership, overlapping responsibilities,
dependency cycles, unused code, unsafe type boundaries, or patterns that make
changes unnecessarily broad. Trace references before calling code unused, and
account for public APIs, dynamic loading, tests, and framework conventions.
Treat counts and thresholds as prompts for inspection, not proof of a defect.

For each finding, state the observed behavior or maintenance cost, cite the
source location, describe impact and confidence, and propose the smallest
useful correction. Separate confirmed findings from possibilities and name
areas you did not inspect. Keep the audit read-only unless the user also asks
for remediation; use the relevant implementation and review workflows for
changes.
