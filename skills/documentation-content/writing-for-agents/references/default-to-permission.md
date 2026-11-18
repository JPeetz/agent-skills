# Default to permission

Standing preference for `AGENTS.md`, `CLAUDE.md`, READMEs, runbooks, and any instruction file.

- **Default to permission.** Write what the agent can do and how; add a restriction only when you can name the specific, present-day harm it prevents. If you can't name it, don't write it.
- **Gate only the irreversible.** "Ask a human before X" belongs only where X is irreversible, touches auth, billing, data deletion, or migrations, or is customer-visible. Everything else: do it, then report.
- **Guardrails follow incidents.** A rule earns its place after an actual incident, not before — cite the incident as the rule's reason.
- **Prefer "do → verify → report"** over "propose → wait → do".
- **Keep it short.** Target under 60 lines. Facts the agent can discover itself — file layout, commands, test runners — don't belong in docs; the agent can read the repo.
- **Every rule has an expiry.** Tag restrictions with date and reason (`# 2026-11: added after prod outage #412`); a rule without a reason is removed on the next edit.
- **Replace blanket hedges with concrete conditions.** "Always confirm", "be careful", "double-check with the team", "consider asking" — each becomes the specific condition that actually warrants a pause.
- **Optimize for the agent's speed and ownership**, not the reader's comfort. If a rule mainly reduces human anxiety rather than real risk, cut it.
