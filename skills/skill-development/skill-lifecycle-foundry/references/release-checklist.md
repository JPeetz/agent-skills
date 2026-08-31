# Skill Release Checklist

Use this checklist before publishing a skill to a public repo, marketplace, or team.
Every item must be satisfied before a skill leaves a private tree.

## Content & Structure
- [ ] `SKILL.md` frontmatter: `name` equals the folder slug; `description` is ≤60
      characters and ends in a period.
- [ ] Body sections in canonical order: When to Use, Prerequisites, How to Run,
      Quick Reference, Procedure, Pitfalls, Verification.
- [ ] Every auto state path in `references/sources.md` has a URL.
- [ ] Body stays under ~500 lines; heavy detail lives in `references/`.

## Security & Privacy

- [ ] No hardcoded API keys, tokens, or credentials anywhere (sweep for `sk-` +
      24+ chars, `lin_api_`, and env placeholders).
- [ ] No private hostnames, account names, org facts, or internal repo paths.
- [ ] All examples are portable; no machine-local absolute paths.

## Packaging

- [ ] `LICENSE` (MIT) present with the current year.
- [ ] `CHANGELOG.md` version section present.
- [ ] `evals/evals.json` present with ≥6 cases (should-trigger and not-trigger).
- [ ] `references/` present and referenced by the body.

## Validation

- [ ] `scripts/validate_skill.py <skills-dir>` reports `"valid": true` and an empty
      `issues` list.