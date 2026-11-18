# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two invocation policies, with runtime-specific discovery behavior:

- A **model-invoked** skill has a description that helps the runtime or agent select it automatically. It remains available for explicit invocation where the runtime supports that. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill opts out of automatic invocation where the runtime honors `disable-model-invocation: true`. Keep a short human-facing description. Do not assume zero context load or absence from every skill roster: discovery, injected metadata, and explicit invocation differ across runtimes.

Pick model invocation when the agent should select the skill on its own. Use explicit-only policy when selection should stay with the user, and verify actual discovery in each target runtime.

Skill rosters may truncate or omit descriptions; limits vary by runtime and version. Put routing information in the first clause, including any boundary needed to prevent misrouting. Keep the discoverable set focused and verify which skills the target runtime actually exposes.

Shared instructions that do not need independent invocation belong in ordinary Markdown references. A router can read a referenced procedure regardless of whether that procedure is a skill; it need not invoke a member skill by name.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when it needs independent discovery. If only a router selects the procedure, keep it as an ordinary Markdown reference under the router and link to it.

## Router skills

When related procedures multiply, use one **router skill** to choose among them. Keep only the router's `SKILL.md` and `agents/openai.yaml` discoverable; put each member's instructions in an ordinary Markdown file such as `member/PROCEDURE.md`. The router links to the selected file and reads it after routing. Use another `SKILL.md` only when that operation needs independent invocation.
