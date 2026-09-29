# Security Policy for Agent Skills

## Reporting a Vulnerability

If you discover a security vulnerability in any skill — including malicious, unsafe, or prompt-injection-prone instructions in a `SKILL.md`, or a harmful `scripts/` file — please **do not open a public GitHub issue**.

Report it privately via **GitHub's private vulnerability reporting**:

1. Go to the repository's **Security** tab
2. Click **Report a vulnerability**
3. Provide a clear, reproducible description of the issue

We aim to acknowledge reports within **48 hours** and will work with you to assess, fix, and disclose responsibly.

## Scope

This policy covers:

- `SKILL.md` files containing instructions that could cause harm (prompt injection, credential exfiltration, data destruction)
- Scripts under any skill's `scripts/` directory
- Incorrect or unsafe tool usage guidance that could damage a user's system
- Any other security-relevant defect in the repository

## Responsible Disclosure

We ask reporters to follow standard responsible disclosure: allow time to fix and release before public disclosure. We credit reporters in release notes when they request it.

## Note on Skill Safety

Skills are arbitrary instructions run with the agent's tools and privileges, so treat unknown skills with caution. The repository's [agentic-security-scanner](/skills/security/agentic-security-scanner) skill exists precisely to help audit skills of unknown provenance before use.