---
name: spec-peer-review
description: >-
  Use when running one requested fresh-eyes review of a saved specification, design, RFC, or detailed PRD and reporting findings for the user to disposition. Not for implementation reviews, automatic approval loops, or adversarial decision review (doubt-driven-development).
disable-model-invocation: true
argument-hint: "[spec path] [--context <paths>] [--out <directory>]"
---

# Spec Peer Review

Review a saved design only when the user requests a fresh-eyes review. Use
the stated scope and any approval already given to review the document as-is.
Resolve the document and relevant context from the request; ask only when
missing information prevents a useful review.

Use one available fresh-eyes reviewer for the requested round. Follow the
repository's review tooling and privacy boundaries, and give the reviewer a
specific findings path and the relevant source material. If no fresh-eyes
reviewer is available, explain the limitation instead of presenting a
self-review as a fresh-eyes review.

Check applicable scope, interfaces, ownership, data changes, safety
invariants, and verification expectations. Report concrete findings with
severity, evidence, and consequence; mark uncertain claims. Save one findings
artifact per round under the requested location or a timestamped
`.peer-reviews/` directory beside the spec. Report verdict and limitations
without calling a draft approved by default. The round ends at the findings
report: applying selected findings or running another round is separate,
explicitly requested work.
