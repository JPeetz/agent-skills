# Claude Code: model control and prompting

Start with [routing defaults](../SKILL.md#routing-defaults) and the
[lane contract](../SKILL.md#lane-contract). Consult [Model routing](model-routing.md)
for substitution, escalation, review, or policy ambiguity. Inspect the live
`Agent` schema and selected definition: aliases, effort levels, and accepted
fields change between versions. Native Claude Code supports background
subagents and per-agent routing; a wrapper or older client may expose less.

## Select the model and effort

- Prefer an explicit selection for a bounded assignment: model precedence is
  invocation, then agent definition, then subagent default, then parent.
  An alias can resolve to a provider mapping or the parent's same-family
  model — it does not guarantee the newest public version. Preserve pins and
  check observable task metadata for substitutions.
- A conversation fork retains the parent's route. For an independently routed
  assignment, dispatch a fresh subagent when the host supports it.
- A subagent on the session's own model inherits the session effort; on any
  other model it runs at that model's default — set effort on the call when
  the default does not fit the task.
- For an advisor consult, prefer the native advisor tool when the session
  has one: it reads the full conversation, toggling it keeps the prompt
  cache, and subagents inherit it. A separately routed subagent suits a whole
  delegated subtask. **Enabling the advisor is a persistent setting that bills the
  advisor model — leave that to the user.**

If the observed route differs, inspect existing overrides without printing
secrets: `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`,
and `CLAUDE_CODE_EFFORT_LEVEL` can alter selection, as can provider alias
maps, managed restrictions and installed mods. These are troubleshooting
facts, not variables to set for delegation. Report an unresolved
restriction; do not alter settings or bypass it with another CLI.

## Prompt for the selected work

Use the shared [lane contract](../SKILL.md#lane-contract). Explain the outcome,
scope and completion evidence. Separate instructions from source material;
use clear headings or XML tags when a prompt mixes documents and examples.
Include context that explains a non-obvious constraint.

Give a cheap model a bounded coding or lookup assignment with an explicit
check and a requirement to finish it. Give a mid-tier model the relevant
interfaces and invariants, allowing implementation choices inside the scope.
For a top-tier model, describe the larger end state and meaningful limits;
let it investigate and plan instead of prescribing every tool call. At low
effort, strong models end turns early more often: tell them to work through
ordinary obstacles (errors, timeouts, failing tools) and to stop only for a
deliberate blocker or a decision that is the user's. Keep required
repository checks and approval boundaries in force for every model.

Use a small example for a difficult output contract. Ask for concise evidence,
remaining uncertainty and actual changes, rather than private reasoning —
reasoning-extraction prompts can be refused.

## Coordinate natively

Native background subagents run concurrently and return completion
notifications. Foreground waiting, available tools and fork behavior depend
on the installed client and current mode. Use the returned handle and native
wait/resume facilities; collect the report before accepting the assignment.
Pass relevant skills/context explicitly to a fresh agent rather than assuming
it received the parent's conversation and loaded skill bodies.

No custom completion ledger, watchdog or environment change is a prerequisite.
Honor host controls already in force. External CI/deployment waits and
shell-launched processes have separate completion contracts; follow the main
skill's continuation rule instead of assuming a native agent notification
supervises them. Use teams only for useful sustained peer coordination when
the host already supports them.

## Orchestrate with a script workflow

Claude Code 2.1.154+ adds a third dispatch mechanism besides foreground and
background subagents: the `Workflow` tool. The model writes a JavaScript
orchestration script and the runtime executes it in the background, holding
intermediate results in script variables and returning only the script's
final result to the session. Prefer it over turn-by-turn dispatch when the
item count outgrows one context window, per-item verification must be
enforced rather than remembered, or the orchestration is worth re-running.
Keep adaptive dispatch when the parent must react to each result.

- Trigger it with a plain request ("use a workflow"), the `ultracode`
  keyword in a typed prompt, or `/effort ultracode` for every substantive
  task in a session. The keyword does not fire from `-p` or agent-composed
  input. A `disableWorkflows` setting or `CLAUDE_CODE_DISABLE_WORKFLOWS`
  removes the tool.
- Describe the harness in the prompt: phases, one worker per item, the
  verification pass, and the returned result. Script primitives:
  `agent(prompt, {label, phase, schema, model, stallMs})` spawns a
  clean-context worker that sees only its prompt — `schema` forces a
  structured verdict, `model` routes a stage, `stallMs` sizes the
  silent-output window before an auto-restart. `parallel()` is a barrier;
  `pipeline(items, ...stages)` streams items through stages independently;
  `phase(name)` groups agents; plain JavaScript between calls filters and
  routes at no token cost. `Date.now()` and `Math.random()` throw so a
  relaunch replays deterministically; pass such inputs through `args`.
- Runtime facts: up to 16 concurrent agents and 1,000 per run. A stopped or
  unrecoverable `agent()` resolves `null` inside `parallel`/`pipeline`, so
  scripts filter those results; a stalled agent restarts up to five times
  before the call fails. A relaunched run replays completed agents from
  cache positionally — reordering the script reruns the shifted agents.
  Resumption works within the same session; a stopped session needs
  `claude --resume` and a fresh `Workflow` call.
- Workflow agents run under the session's permission mode and tool
  allowlist on the ordinary subagent model order; a script-named model
  counts as the per-invocation model. They return findings as their result,
  not as report files.
- Cost and scale control: many agents mean many tokens. Set the amount of
  verification in the prompt, route cheap stages to cheaper models, and
  pilot a small slice first. `/workflows` shows per-agent usage and allows
  stop, restart and save; a run past 25 agents or a 1.5M-token projection
  raises a `Large workflow` warning; `workflowSizeGuideline` steers the
  default scale.
- The generated script persists under `~/.claude/projects/`; save a
  reusable orchestration into `.claude/workflows/` to re-run it as
  `/<name>`. Edit saved scripts through the bundled `/workflow-authoring`
  skill (2.1.248+).

Reviewed 2026-11-15 against
[Claude subagents](https://code.claude.com/docs/en/sub-agents),
[dynamic workflows](https://code.claude.com/docs/en/workflows),
the [Agent SDK dynamic workflows cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows),
[model configuration](https://code.claude.com/docs/en/model-config),
[advisor tool](https://code.claude.com/docs/en/advisor),
[prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices);
verify the live schema for the installed version.
