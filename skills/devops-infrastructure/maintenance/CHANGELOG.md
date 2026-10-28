# Changelog

All notable changes to the maintenance skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 (2026-10-28)

### Added
- Initial release: Custodian maintenance runbook for self-hosted customer stacks (Cal.diy / Typebot / n8n / Postgres / Stripe).
- JEV-first decision loop (health probe -> backup -> update -> rollback) with flash-model cost discipline.
- 15-minute health probes, weekly verified backups, JEV-gated weekly updates, and rollback-first mutation policy.
- Eval suite (evals/evals.json, 7 cases).