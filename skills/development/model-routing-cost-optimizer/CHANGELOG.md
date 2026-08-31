# Changelog

## [1.0.0] - 2026-08-24

- Initial release of the model-routing cost optimizer.
- Establishes a three-tier model hierarchy (Tier 1 cheap ~$0.10-0.50/M in, Tier 2
  mid ~$1-5/M in, Tier 3 premium ~$10-75/M in).
- Ships a task classifier (`scripts/classify_task.py`, stdlib only) plus decision
  rules including the vision-capable vs text-only override.
- Documents anti-patterns such as heartbeats/cron on premium models.
- Prices live in `references/model-pricing.md` with a "prices change, check
  provider docs" caveat rather than inline in the body.