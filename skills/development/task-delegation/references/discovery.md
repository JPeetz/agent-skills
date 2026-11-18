# Discovery and adoption

## Check availability first

Confirm `task-delegation` appears in the active host's skill catalog. A ZIP, another client's installation, or a file on disk does not establish that this session loaded it. Keep one canonical skill and expose it through each host's supported discovery or plugin mechanism; remove duplicate-name ambiguity only within authorized scope.

Inspect the loaded description, parsing, invocation policy, and listing budget before making the description broader. Codex can shorten descriptions or omit entries when the catalog exceeds its budget. Claude also limits skill listing context. Front-load concrete trigger phrases; keep automatic invocation available for this orchestration skill. Explicit invocation remains a useful diagnostic.

For Codex metadata, keep `policy.allow_implicit_invocation: true` in `agents/openai.yaml`. For Claude, check that overrides or `disable-model-invocation` do not suppress automatic use. Preserve a portable `SKILL.md` with only `name` and `description`; keep host-specific settings in their supported configuration owners.

## Optional durable routing pointer

Propose this single line in the relevant durable instructions when delegation is repeatedly missed:

> Route an explicit `ultratask` invocation to `$task-delegation`; otherwise use the skill to assess substantial multi-lane work.

Do not apply it uninvited — it edits durable user config outside the task's scope. Do not copy this skill's procedures into AGENTS.md. On native Claude Code, make the pointer reachable through its actual loaded instruction entry point; do not assume AGENTS.md is read without the user's configured integration.

## Check behavior

Try natural prompts for multi-part implementation, PR batches, broad diagnosis, and fresh-eyes review. Include negative cases such as a typo, one exact lookup, and a purely serial change. Compare whether the skill is selected, whether useful lanes actually launch, and whether completion is evidenced. A better description improves eligibility; it cannot guarantee invocation or override runtime restrictions.

For repeatable comparisons after changing this skill, use the conditional [evaluation scenarios](evaluation.md).

Official sources, checked 2026-10-24: [Build skills](https://learn.chatgpt.com/docs/build-skills), [Concise skills and progressive disclosure](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [Claude skills](https://code.claude.com/docs/en/skills). Keep detailed host behavior in the adapters.
