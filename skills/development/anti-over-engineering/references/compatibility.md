# Compatibility Reference

## Western Agent Integration

- **Claude Code**: Install via `gh skill install JPeetz/agent-skills anti-over-engineering --agent claude-code`. Activates from natural-language triggers like "this is too much" or over-engineering patterns.
- **Hermes Agent**: Add `external_dirs` in config.yaml or `hermes skills install JPeetz/agent-skills/anti-over-engineering`. Available as `/anti-over-engineering` slash command.
- **Codex**: Copy to `~/.codex/skills/` or `~/.agents/skills/`. Activates on scope-creep signals.
- **Cursor**: Copy to `~/.cursor/skills/`. Activates via description matching.

## Complementary Skills

- **PUA (Push-Up Agent)**: When the AI is too passive or gives up easily — push it forward. Install alongside this skill for balanced behavior.
- **finding-unknowns-context-audit**: When the AI's context itself needs pruning to reduce over-engineering impulses.
- **code-review**: When you need structured review that also gates on scope.

## Pairing with PUA

Moyu and PUA solve opposite problems. They are complementary:

- **PUA**: When the AI is too passive or gives up easily — push it forward
- **Anti-Over-Engineering**: When the AI is too aggressive or over-engineers — pull it back

Install both for the best results. PUA sets the floor (don't slack), this skill sets the ceiling (don't over-do).

## Avoiding Over-Correction

Some engineering cultures value proactive architecture suggestions. If the user explicitly says "use your judgment" or "suggest the best approach," calibrate scope accordingly. This skill's default is conservative; override with user preference.

## Original Work

All techniques in this skill originate from [uucz/moyu](https://github.com/uucz/moyu). The English port maintains the full 4-level intervention system, anti-pattern tables, and detection signals from the original while adapting trigger descriptions for Western agent platforms.