# Codex: model control and prompting

Start with [routing defaults](../SKILL.md#routing-defaults) and the
[lane contract](../SKILL.md#lane-contract). Consult [Model routing](model-routing.md)
for substitution, escalation, review, or policy ambiguity. Inspect the live
spawn and wait schema: Codex clients and ChatGPT-hosted agents can expose
different controls; API parameter names are not automatically spawn parameters.

## Select the model and effort

- Codex can set reasoning effort separately from the model when the host
  exposes it: use the spawn tool's accepted effort field or native custom-agent
  `model_reasoning_effort`. Start from the documented baseline and adjust for
  the work within supported levels and applicable policy.
- Use the live model catalog and accepted override fields. In native Codex,
  custom-agent `model` and `model_reasoning_effort` values take precedence over
  the resolved spawn/default settings. Inspect a selected role before claiming
  a spawn override changed it; `worker` and `explorer` are role names. Preserve
  fixed-role restrictions even when another model is available in the catalog.
- With no model or effort configured, a child can inherit the parent's route.
  A newly selected model without an explicit/configured effort can use its own
  default. Confirm the effective values when the host exposes them.
- When the live schema requires `fork_turns: "none"` for model/effort overrides,
  use it and supply a self-contained brief. A full-history fork may keep the
  parent's route. Use neither field nor behavior on a host that lacks it.
- Use only effort levels supported by that model and host. An API effort,
  composer intelligence level, service tier and delegation mode are distinct
  controls.
- Children inherit parent permissions. A read-only brief does not create a
  sandbox, and a custom-agent file cannot grant broader permissions, a different
  provider, or MCP access the parent lacks. Keep configuration changes outside
  an ordinary delegation task.

## Prompt for an outcome

Use the shared [lane contract](../SKILL.md#lane-contract). State the requested
artifact or decision, relevant repository facts, scope, and checks. Make
"implement and verify" explicit when action is authorized; use "inspect and
report" for read-only work. Give the worker room to choose implementation
steps within those bounds.

For bounded cheap-model work, supply the exact inputs and observable result.
For judgment work, describe the uncertainty, invariants and evidence that
would settle it. Ask for findings and verification evidence, rather than
a transcript of private reasoning or repeated "think harder" instructions.
Add a compact example only when a format or edge case is otherwise ambiguous.

## Coordinate natively

Launch independent slices within the host's capacity. Keep the parent active
on useful work and collect required reports using native notifications or
waits. Follow-up/start tools may be required to run an idle agent again.
Verify the live state after an interruption or resume.

A shell-launched CLI process is a separate execution route, not a native
subagent. Use it only when needed and permitted, with a tracked process and
retrievable result. A shell session ID alone does not guarantee a later turn
will resume. Apply the main skill's continuation rule without installing a
watchdog or changing environment variables.

Reviewed 2026-10-28 against [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
and [OpenAI prompting guidance](https://developers.openai.com/api/docs/guides/prompt-engineering).
Live schema and applicable host instructions govern actual invocation.
