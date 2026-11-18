# Model guidance sources

Official sources reviewed 2026-11-11 with Prompt Current live preparation and
page reads. The preparation fetches references; it is not an independent model
evaluation, and a successful routing test is not a quality comparison.

- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model)
- [Claude model configuration](https://code.claude.com/docs/en/model-config)
- [Claude dynamic workflows](https://code.claude.com/docs/en/workflows) and the
  [Agent SDK dynamic workflows cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows)
- [Haiku 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5),
  [Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5),
  [Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5),
  [Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2) prompting guides
- [Claude Fable and Mythos 5.2](https://www.anthropic.com/news/claude-fable-and-mythos-5-2)

The current host's exposed schema establishes permitted dispatch controls and
role restrictions; the live catalog settles which named route exists.

Route names checked 2026-11-17 against the Codex 0.169.0 model catalog and the
GPT-6.2 guide above: `gpt-6.2-sol` and `gpt-6.2-astra` are current, and the
catalog marks `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-sol` and the 5.6 family
previous or legacy. The delegation guard's `policy.json` carries the exact IDs
and efforts; this skill names none, so a new release changes that file only.
