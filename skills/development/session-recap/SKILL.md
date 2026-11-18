---
name: session-recap
description: Use when reorienting in a long or resumed session with an evidence-backed map of its goal, pivots, outcomes, current step, and open decisions. Not a planner or task tracker.
disable-model-invocation: true
argument-hint: "[short]"
---

# Session recap

Rebuild how this conversation actually unfolded so the user can regain their bearings after a long run, a context compaction, or a switch back to this session. The map is advisory: it plans nothing, executes nothing, and writes no state, so it works the same in Claude and Codex.

## Modes

- No argument: render the full map.
- `short`: render only the goal, current stage, and what needs the user.

## Steps

1. **Collect evidence** from this conversation's user messages, tool results, and artifacts it names (files, commands, URLs, PRs). Repository state alone does not show a stage happened. Done when the original goal, each explicit goal change, completed outcomes, dropped paths, and pending user decisions are each listed with their source.
2. **Cut stages.** Use 4 to 8 when the history supports them and fewer for a sparse one; never pad. Mark each with one outcome:
   - `done`: finished, with an outcome the conversation supports
   - `now`: the current unfinished stage
   - `planned`: explicitly agreed, not started
   - `dropped`: abandoned, with the stated reason
   - `pivot`: old direction and the evidenced new one
3. **Attach one evidence pointer per stage**: a real path or URL from the conversation, else a short distinctive quote from a user message or tool result. Never invent a link. Mark anything rebuilt from a compacted summary as `inferred`.
4. **Render** in at most 15 lines using the shape below. `Needs you` lists open decisions, or `none`. `Next` names a concrete action only when the conversation supports one, else `none`. Done when every line traces to a source from step 1.

## Output

```text
Goal: <goal, plus any evidenced change>
S1 done: <stage> -> <outcome> (evidence: <pointer>)
S2 pivot: <old> -> <new> (evidence: <pointer>)
S3 now: <current stage> (evidence: <pointer>)
S4 dropped: <path> - <reason> (evidence: <pointer>)
Needs you: <decision or none>
Next: <action or none>
```

Omit rows that do not apply. Keep stage order and numbers stable across repeated calls unless new evidence corrects them, and say what changed.
