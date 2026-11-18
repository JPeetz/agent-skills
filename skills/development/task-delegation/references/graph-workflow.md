# Graph workflow

Use a small execution graph for work with meaningful dependencies or concurrent lanes. Store it in the existing task or harness records; no graph database, retrieval service, or extra planner agent is required. Keep instructions and operational authority in their canonical owners.

## Record and dispatch

For each node, record `id`, outcome, `depends_on`, owner/job reference, write scope, `input_ref`, acceptance checks, state, and evidence references. Let `input_ref` identify the artifact revision and relevant contract or policy inputs. Use existing fields rather than requiring a new schema.

- Keep prerequisites acyclic; record a repair as a new attempt of an affected node.
- Mark ready only when required prerequisites are accepted and inputs are available. Claim and launch it before marking running. A plan or receipt alone is not completion.
- Dispatch independent ready nodes concurrently within capacity and ownership limits. Checks and a selected fresh-eyes review can run together on a stable artifact when neither needs the other's output.
- Finish by accepting the required nodes with current evidence. Omit an unnecessary optional review, or record a skipped reason; do not mark an unperformed review as passed.

## Reuse evidence and repair selectively

Bind each check or review to its input reference, covered scope, result, and source. Reuse it while those inputs and its applicable policy remain valid. A passing worker check proves its slice, not the integrated artifact.

When inputs change, reopen affected nodes and follow the dependencies to identify evidence that no longer applies. Preserve unrelated accepted work. Recheck a repaired finding and newly affected risks rather than restarting the whole review sequence. Run any broader check or fresh attestation required by repository policy; dependency analysis does not authorize CI pruning or approval reuse across revisions.

Notify affected owners of scope changes and confirm amendments before relying on them. Follow the main workflow's waiting and continuation rules for externally blocked nodes.

## Choose verification

A requested or workflow-required Critique stage, and fresh-eyes review selected by the parent or required by policy, use a fresh-context agent that did not author the work; follow the [lane protocol](lane-protocol.md#review-the-complete-lane). Otherwise separate verification is a judgment call based on complexity, uncertainty and failure cost: tiny work with no critique or fresh-eyes-review requirement can stay local. Pick the pattern that fits:

- **Adversarial cross-review:** independent agents try to refute each other's findings before any are reported.
- **Per-unit review, one summary:** one reviewer per file or risk area, feeding one agent that ranks and deduplicates the findings.
- **Fix until checks pass:** inspect failures and attempt evidence-supported repairs; if an approach stalls, investigate and change strategy, reassign, or report the blocker and next action.
- **Plan stress-test:** agents that did not write the plan try to refute it; reconcile their evidence rather than vote.

Scope one review to the change; add another only for unresolved findings, materially changed inputs, missing evidence, or an explicit policy requirement. Keep advisors and subplanners conditional. Apply the [Verifier](../prompts/verifier.md) stopping rule: stop when acceptance holds, not when confidence feels high enough.

Assess time and available cost per accepted outcome, including dispatch, waiting, integration, model calls, and rework. Add agents only when their useful concurrency or independent judgment repays that overhead.
