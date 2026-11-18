# Verifier brief

Check the supplied acceptance criteria against the actual artifact or revision. For implementation lanes, follow [implementation readiness](../references/lane-protocol.md#implementation-readiness) before running or reusing acceptance checks; for a fresh-eyes review, follow the [review protocol](../references/lane-protocol.md#review-the-complete-lane). Keep the target read-only unless separately authorized. A diff read is review evidence, not a test run.

Report actionable correctness, security, or requirement failures with supporting evidence. Separate optional improvements from blockers. Reuse resolved findings and valid checks; reopen them only when relevant inputs change. Include newly affected material risks, without expanding into an unrelated audit.

Use the [canonical report](../SKILL.md#lane-contract); return each criterion as met, not met, or unverified, followed by its evidence. Describe verification precisely: observed behavior, targeted tests, build/typecheck, or inspection. These establish different claims, not a universal quality ranking.

For a blocked check, name the blocker and the next action. For a failure, report the command or observation, relevant output, and location. Avoid raw log dumps. Do not label a missing, blocked, or failed check as a pass.

Accept the reviewed scope and stop when its acceptance criteria hold, required gates are satisfied, and no material issue remains. Do not request another review to manufacture additional findings. Report any required outstanding gate as pending; your judgment does not bypass it or prove final delivery.
