# Security Scan Notes — Documented False Positives

The repo-scanner flags several patterns in this skill's reference files. All are **intentional false positives** — the flagged text appears in security check criteria descriptions, not in executable code.

| File | Line | Pattern Flagged | Explanation |
|------|------|----------------|-------------|
| `references/infra-hardening-gate.md` | 22 | `curl | sh` in a Dockerfile | This is a security **check rule** describing what to detect during infra review, NOT an actual command to execute. |
| `references/infra-hardening-gate.md` | 39 | `curl | sh` in a build? | This is a **check question** for reviewers, not executable code. |
| `references/security-review-gate.md` | 12 | `dangerouslySetInnerHTML` | This describes a security check item ("Never dangerouslySetInnerHTML"), NOT actual usage. |
| `references/security-review-gate.md` | 38 | remote `curl | sh` | This is a security rule describing what to flag in code review, not an executable command. |

**Verdict:** ✅ All flagged items are descriptive security criteria, not executable code. Safe to publish.
