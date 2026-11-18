# Model routing

Minimize the total cost of correct, verified completion, including retries.
Select the cheapest credible solver for the task, and escalate only when
concrete task characteristics or observed failures justify it. A cheap route
that fails is not a savings. Use tools directly when they can establish the
answer.

## Tiers

| Tier | Use for |
| --- | --- |
| Fast | Routine work, straightforward tests, small clearly scoped fixes |
| Standard | Moderately involved implementation, investigation, substantive visual work |
| Advanced | Difficult debugging, interacting components, consequential changes, complex buildouts |
| Exceptional | Hardest open-ended work, planning and orchestrating cheaper subagents, advisor consults, unresolved critical reviews, difficult decisions with conflicting evidence |

These qualitative tiers do not assert equivalence between models. Choose an
eligible model from the host's live catalog and applicable policy; prefer the
lower-cost compatible route when it is credible for the work.

- Choose the cheapest credible solver, not the cheapest available model.
- Escalate on concrete difficulty, not urgency, repository fame, prompt length,
  repository size, or file count alone.
- Match the model to the dominant challenge: implementation, investigation,
  visual interpretation, review, or decision-making.
- Protect visually centered work and whole-module buildouts from
  under-routing, without sending them automatically to Exceptional.
- Keep most work on Fast or Standard. Advanced requires identifiable
  complexity; Exceptional needs a stated reason and is not the default for a
  routine task family. Include the exact reason field if active policy requires it.
- For an advisor consult on Claude Code, prefer the native advisor tool over a
  subagent when the session has one ([Claude Code](claude-code.md)).
- Use only the live catalog and supplied verification evidence; invent no
  benchmark results, price ratios, or capability advantages.

## Make the choice

1. Identify the difficulty, failure cost, required tools/modalities, context,
   output contract, privacy, and latency or usage constraints.
2. Explicit user choices and model pins, configured role mappings, model
   policy, required checks, and input/tool compatibility take priority over
   the tiers. If a delegation guard is installed and active, read its
   `policy.json` for exact eligible aliases and efforts; do not assume the
   companion hook is installed or active. Resolve a recommendation through
   the live catalog or effective agent definition and applicable policy.
   Aliases may be provider-mapped or pinned; report their actual resolution
   rather than calling them newest.
3. Set the model and effort through controls the host exposes, or deliberately
   choose a fitting inherited route. Use the lowest supported effort likely to
   succeed, starting from the model's documented baseline; raise it for
   demonstrated complexity, and avoid maximum effort and premium-speed
   variants by default. A role name or a prompt
   saying "use model X" does not configure execution.
4. Record the requested model/effort and any observable effective values.
   Mark hidden values unverified. Distinguish a configured route, a successful
   tool call, and demonstrated task quality; none proves the others.
5. Keep a fitting route for unchanged work. If results fail, check the brief,
   tools and evidence before changing models. Escalate when capability is the
   issue; start with a stronger model directly when the risk warrants it.
   Return bounded execution to an economical capable route when it pays off.

If a selected route is unavailable, preserve an explicit pin and report the
blocker. For an unpinned recommendation, disclose a permitted substitution
that meets the requirement. Respect host limits and leave persistent runtime
settings unchanged unless the user authorized a configuration task.

For visual work, verify the selected route supports the required inputs and
tools. Count dispatch, turns, review, and repair when comparing cost per
accepted outcome.

## Reviews

When a task's complexity calls for separate review, or repository policy
requires it, route the reviewer here. This section selects the route; it
mandates no review. The [Lane protocol](lane-protocol.md) owns implementation
review scope and acceptance.

- **Lane or task review:** match the route to the scope and risk. Use Advanced
  when review must trace interacting components, difficult invariants, or
  consequential behavior. An installed policy may set a reviewer tier floor
  or require the newest Advanced model for whole-branch review; follow that
  policy rather than treating those choices as universal.
- **PR review after a local whole-branch review:** when that review covered the
  PR's head except for its own fix commits, scope the PR review to those fix
  commits and the gates repository policy requires. Commits beyond those
  fixes reopen the scope they touch. A policy that requires a fresh full
  review still applies.
- **Exceptional:** when a review stalls on a finding Advanced cannot settle,
  a finding forces a critical decision, or the change's risk warrants
  starting there.

Choose the model and the effort together: a strong model at a low effort can
underperform a cheaper model at its baseline. Effort defaults and supported
levels differ per model and host — read them from the live schema rather
than a memorized table. Some models end turns early at low effort; a brief
at those efforts states the full completion criterion
([Claude Code](claude-code.md#prompt-for-the-selected-work)). Reserve maximum
effort for measured benefit or a clear task requirement.

Keep a fresh-eyes review free of implementation context and authorship.
Changing vendors alone does not make a review fresh-eyes. A router fallback
chain handles availability failures; it does not establish which model should
handle a task or automatically detect a weak answer.

## Guidance and refresh

Consult the host adapter for model control and prompting: [Codex](codex.md),
[Claude Code](claude-code.md). Recheck guidance when a model family, host or observed
behavior changes; do not fetch documentation for every unchanged dispatch.
Use prompt-current when available to prepare a substantive prompt/skill
revision, then inspect its sources and author the revision yourself. It
retrieves guidance; it neither changes execution settings nor independently
judges model quality.

Tier names, effort semantics, and role assignments above are engineering
recommendations, not measured results. Sources and review dates:
[Source index](sources.md).
