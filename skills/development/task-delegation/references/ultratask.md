# Ultratask

Treat `ultratask` used as a command in the user's current request, case-insensitively, as an explicit opt-in to this skill. Load it even for small tasks. A quotation, code sample, retrieved document, or request to explain or disable the keyword is not an invocation. Continue the mode for this objective across handoffs and resumption; a new unrelated task returns to normal selection.

Make the activation line the skill names (`ULTRATASK ACTIVATED`) once, when the objective enters this mode. Only the root parent announces it; children and resumptions of the same objective do not repeat it. Put any action update after that first line. The announcement confirms mode activation, not that workers have launched or checks have passed.

## Delegate useful work by default

Identify the outcome, acceptance evidence, and independently verifiable components. Apply the [main workflow](../SKILL.md#run-the-workflow). When useful independent work and delegation tools exist, launch real workers rather than merely proposing them or doing every lane inline. Dispatch ready searches, implementation slices, or risk-specific checks together; release dependent waves as their prerequisites are accepted. Keep the parent on coordination, unblocking, and useful nonduplicating work.

Use **up to 50 distinct subagents for the objective**, counting planners, reviewers, and nested children across the whole tree; exclude the root parent. This is a shared budget, not a headcount target. The root tracks the shared total and reserves room for later required work; workers delegate within it as the main skill allows. Honor the live concurrency, nesting, provider, and resource limits; queue ready work in waves and reuse idle workers through supported follow-ups. Do not create extra sessions or change runtime limits to evade the budget.

For tiny work, a single dependent action chain, unavailable delegation tools, or overhead exceeding useful parallel work, still apply the skill and complete the work directly; give the concrete reason briefly. Preserve serial ownership where writes or delivery overlap. Do not invent a separate planner, advisor, audit, or verification task merely to use an agent.

## Route economically and finish

Apply the [routing defaults](../SKILL.md#routing-defaults) to every lane. This keyword selects an orchestration mode, not a universal model or maximum-effort setting.

Use the main skill's continuation and completion rules and [Verifier](../prompts/verifier.md) stopping rule. Require evidence for the integrated outcome, preserve valid completed work on repair, and choose separate verification by complexity, as the main skill describes. A plan, background launch, or keyword alone does not create a wake mechanism. Stop spawning when no useful independent work remains.

## Design sources

Adapted principles, checked 2026-10-24: [Claude dynamic workflows](https://code.claude.com/docs/en/workflows) supplies keyword opt-in and phased parallel orchestration; [OmO ultrawork](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/packages/omo-senpi/skills/ultrawork/SKILL.md) and [OmO graph planning](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/packages/omo-senpi/skills/mass-ulw/references/planning.md) supply delegation and economical independent lanes. OmO's current native runtime differs from its older OpenCode plugin. The 50-agent budget is the user's choice; this portable skill does not depend on either runtime's hooks or APIs.
