---
name: agent-cli-harness
description: Use when explicitly dispatching parallel or isolated work across agent CLIs, or requesting an independent CLI review. Not for ordinary native delegation.
disable-model-invocation: true
---

# Agent CLI harness

Run caller-configured lanes with Node.js 24 or later. A lane is a task, mode and ordered candidate list. Confirm the selected providers and costs are authorized before dispatch. Read mode is advisory, not an OS sandbox: use an OS sandbox when the repository or worker is untrusted. Worktrees isolate files, not shared Git storage, credentials or network access. OpenCode is excluded because detached descendants can escape process groups.

1. **Brief.** Provide each lane a task, scope and verification criteria. Write lanes start from committed `HEAD`; uncommitted caller edits are not copied. Set a finite timeout. Select only transports installed locally.
2. **Configure.** Create a JSON file outside the worktree. Example:

   ```json
   {"lanes":[{"name":"review","mode":"read","prompt":"Review the changes for correctness.","timeoutMs":120000,"candidates":[{"transport":"codex","model":"YOUR_MODEL"}]}]}
   ```

   Supported CLI transports are `codex`, `claude` and `omp`. Omit `model` to use the CLI's default. Read mode uses Codex's read-only sandbox, Claude's restricted read tools, or OMP's read/search tools with extensions disabled. Tool restrictions are not an OS sandbox.

   Granola is explicit opt-in: prepare an evidence file containing the diff, source excerpts, requirements and verification results. Supply a `read` lane with `evidenceFile` and a candidate `{"transport":"granola","model":"YOUR_MODEL","baseUrlEnv":"REVIEW_BASE_URL","apiKeyEnv":"REVIEW_API_KEY"}`. The base URL ends in `/v1`. The harness sends evidence to that endpoint without tools, with bounded output and timeout. Env fields are variable names, not values; the JSON file and receipt must not contain credentials. Inspect the evidence for sensitive data before sending it.
3. **Dispatch.** Run `node <skill-dir>/scripts/harness.mjs <repository> <lanes.json>`. Lanes run concurrently. Only parsed errors or nonzero-exit stderr identifying quota/rate limits advance a candidate chain. Each write lane gets a new worktree; a fallback resets only that invocation's worktree after checking its branch and HEAD. Workers must not alter Git history. The receipt records attempts, fingerprints, changed paths, output and worktree identity.
4. **Finish.** Inspect every receipt, diff and report; run the task's verification and independent review before integration. Read fingerprints cover Git-tracked diffs and nonignored untracked files, not ignored files or external state. The harness retains write worktrees even on failure; after integrating or abandoning the work, remove only the worktree and branch named in its receipt. If an attempt changed history, investigate its worktree before any cleanup.
