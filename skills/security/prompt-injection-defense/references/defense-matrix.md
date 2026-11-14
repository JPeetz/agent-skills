# Defense Matrix

The expanded enforcement matrix for `prompt-injection-defense`. Every control in the
pipeline, mapped to the attack families it addresses, with its strength, its failure
mode, and the evidence you need before claiming it works.

Attack family IDs (A1–A15) are defined in `attack-catalog.md`.

**Cells**

| Mark | Meaning |
|---|---|
| `P` | **Prevents** — the attack cannot produce the effect if this control is working |
| `L` | **Limits** — the attack may succeed at the text level but cannot reach the impact |
| `D` | **Detects** — produces a signal; no effect on the outcome by itself |
| `·` | No material coverage |

Only L4 controls are `P` for action-taking attacks. That is the whole point of the
matrix: read down the `P` column for A1, A4, A5, A9, A15 and notice that every entry is
a tool-boundary control.

---

## The matrix

| # | Control | Layer | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 | A11 | A12 | A13 | A14 | A15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | Boundary + authority inventory | L0 | · | · | · | D | D | D | · | D | D | D | D | D | · | · | D |
| C2 | Per-task capability scoping | L0 | L | L | L | P | P | L | L | L | L | L | L | L | L | · | P |
| C3 | Length caps + truncation | L1 | · | · | · | · | · | · | D | · | · | · | · | · | · | P | · |
| C4 | Normalization before matching | L1 | · | D | · | · | · | · | P | · | · | · | · | D | · | · | · |
| C5 | Rule screening + scoring | L1 | D | D | D | D | D | D | D | D | D | D | D | D | · | D | D |
| C6 | Classifier hook | L1 | D | D | D | D | D | D | D | D | D | D | D | · | · | D | · |
| C7 | Quarantine on `review` | L1 | L | L | L | L | L | · | L | L | · | L | L | · | · | L | · |
| C8 | Nonce provenance blocks | L2 | L | P | P | L | L | · | L | · | · | L | L | · | · | · | · |
| C9 | Quarantined extraction (dual-LLM) | L2 | L | L | L | P | L | · | L | · | L | L | · | P | · | L | · |
| C10 | Typed/schema-only extraction | L2 | L | L | L | P | L | · | L | · | L | · | · | P | · | L | L |
| C11 | Memory provenance + trust decay | L2 | · | · | · | · | · | · | · | · | P | · | L | · | · | · | · |
| C12 | Instruction hierarchy clause | L3 | L | L | L | L | L | · | L | L | L | L | L | L | · | L | · |
| C13 | Refusal path + output contract | L3 | L | L | · | L | L | L | L | L | L | L | L | · | · | L | · |
| C14 | Argument validation (path/URL/shell/SQL) | L4 | P | P | P | P | P | L | P | P | P | P | P | P | L | L | P |
| C15 | Taint tracking on mutating args | L4 | P | P | P | P | P | L | P | P | P | P | P | P | · | · | P |
| C16 | Out-of-band human approval | L4 | P | P | P | P | P | · | P | P | P | P | P | P | · | · | P |
| C17 | Two-key policy engine / allowlist | L4 | P | P | P | P | P | L | P | P | P | P | P | P | · | · | P |
| C18 | Sandbox + egress allowlist + scoped creds | L4 | L | L | L | L | L | L | L | L | L | L | L | L | L | · | P |
| C19 | Rate / egress budget | L4 | · | · | · | · | · | L | · | L | · | · | · | · | · | L | L |
| C20 | Canary tokens | L5 | D | D | D | D | D | D | D | D | D | D | D | D | · | · | D |
| C21 | Secret/PII scan + redact | L5 | L | L | L | L | L | L | L | L | L | L | · | L | · | · | L |
| C22 | Render sanitizer + CSP | L5 | · | · | · | · | · | P | · | · | · | · | · | L | · | · | · |
| C23 | Output schema validation | L5 | L | L | · | L | L | · | L | · | · | · | · | · | · | L | L |
| C24 | Injection regression suite | L6 | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| C25 | Audit log + anomaly detection | L6 | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| C26 | Kill switch + IR runbook | L6 | L | L | L | L | L | L | L | L | L | L | L | L | L | L | L |

Read the `A8` column: detection-heavy, `P` only at L4. Multi-turn escalation is not
solvable at the text layer, which is why session scoring alone will disappoint you.

---

## Control strength, failure mode, and evidence

| # | Control | Strength | Fails when | Evidence that it works |
|---|---|---|---|---|
| C2 | Capability scoping | High | Tool set is built from the account, not the task | Inventory: every tool has a caller and a step |
| C4 | Normalization | High (precondition) | Applied after matching, or applied twice | Obfuscated fixture set passes: zero-width, bidi, homoglyph, base64 |
| C5 | Rule screening | Low–medium | Treated as a boundary; regex-only | FPR on benign corpus < 5%, ASR reduction measured |
| C6 | Classifier | Medium | Fails open on error at a high-impact sink | Error-path test forces `review` |
| C8 | Nonce delimiters | Medium | Nonce is static, or content can contain the nonce | Fixture that guesses the old static delimiter is inert |
| C9 | Quarantined extraction | High | Quarantined model has tools, or fields are free-text | Privileged model never receives raw prose (trace check) |
| C11 | Memory provenance | High | Writes are free-text overwrites | Poisoned fixture does not retrieve at `trust=trusted` next session |
| C12 | Hierarchy clause | Low–medium | Long prompt dilutes it; no per-turn reminder | Removal test: ASR rises when clause removed (proves it does something) |
| C14 | Argument validation | **High (boundary)** | Validation is a schema type-check only | Path traversal, SSRF, `;` injection, argv fixtures all rejected |
| C15 | Taint tracking | High | Substring matching misses paraphrase/re-encoding | Exfil fixture: recipient copied from document → gated |
| C16 | Out-of-band approval | **High (boundary)** | Approval shown as model summary; in-band approval accepted | Forged "already approved" fixture produces no call |
| C17 | Two-key / allowlist | **High (boundary)** | Allowlist is `*` or derived from the request | Unknown domain/recipient fixture denied |
| C18 | Sandbox + egress | **High (boundary)** | Ambient cloud credentials reachable | Egress test: connection to a non-allowlisted host fails |
| C20 | Canary | High (detection) | Canary is guessable or also present in logs | Planted-leak fixture triggers block + alert |
| C22 | Render sanitizer | **High (prevention)** | Markdown rendered by a client you do not control | Rendered fixture issues zero off-domain requests |
| C24 | Regression suite | High (process) | Suite only covers single-turn, scripted attacks | ASR/FPR reported per family per release |

---

## Minimum viable defense by deployment

"Do we need all 26?" No. The set is determined by what the agent can *do*, not by how
much text it reads.

| Archetype | Can do | Minimum controls | Notes |
|---|---|---|---|
| Read-only Q&A / search | Nothing but answer | C3, C4, C5, C8, C12, C20, C22 | Cheap; the render channel is the real risk |
| Summarizer over private docs | Nothing but answer | Above + C9 or C10, C21 | Exfil through summary text is the failure mode |
| Tool-using assistant (read + draft) | Read data, draft artifacts | Above + C2, C14, C15, C23, C25 | Gated writes, no external send |
| Assistant with external effects | Send, post, spend | Above + C16, C17, C18, C19, C26 | Approval must be out of band |
| Autonomous / scheduled agent | Acts without a human present | All of the above + C11, C24, C25 | Highest bar: unattended means no human to notice |
| Coding agent | Execute, write, commit, CI | Above + C14 (argv, realpath), C18 (worktree, no egress), C16 on `.github/`, `.git/`, lockfiles | CI config is a persistence mechanism |
| Multi-agent / A2A | Delegates | Above + signed handoffs, C2 per agent, C15 across hops | A peer cannot grant authority it lacks |

If an agent has **no** L4 control and **any** external effect, it is not defended,
regardless of how good its prompt is.

---

## Tuning the screening thresholds

`screen_input.py` scores 0–100 and routes at 25 (`review`) / 60 (`block`), or 15 / 40
with `--strict`.

| Situation | Adjustment | Why |
|---|---|---|
| Content reaches a mutating tool | `--strict` + `--fail-closed` | Cost of a miss is an effect, not a bad answer |
| Human-authenticated input, low-impact task | Default, or raise `review` to 35 | Avoid nagging on legitimate security discussions |
| Bulk retrieval (thousands of chunks) | `--strict`, quarantine, sample the `allow` bucket | Volume makes FPs expensive; sampling keeps coverage honest |
| Content is a legitimate security document | Never lower to 0; use the `review` queue | The corpus that describes attacks will always score |
| Agent has no tools | Detection only, no block | Nothing to prevent; blocking just degrades utility |

Scores are additive and capped, with a +20 bonus when two or more attack categories
co-occur, and a source bonus (0 for `user`, up to +16 for `memory`). The combination
bonus exists because "ignore previous instructions" alone is often a quotation, while
that plus a leak or exfil request is not.

**Do not tune to zero FPs.** A screener that never fires is an unmonitored log line.
Target < 5% false positives on a curated benign corpus and treat every FP as a fixture.

---

## Residual risk

Even with every control in place:

- **Utility/text-layer attacks still land.** The model may repeat a falsehood or adopt a
  tone. That is a content-integrity problem, not an injection problem; handle it with
  grounding and citation, not more gating.
- **Novel paraphrases pass the screener.** L4 holds; L1 does not.
- **A compromised dependency bypasses everything.** Tool implementations and the model
  runtime are in the trusted computing base — see `supply-chain-security-scanner`.
- **Humans approve bad actions.** Approval fatigue is real. Keep the exact-args display,
  and rate-limit how many approvals one operator can grant per hour.
- **Rendering happens somewhere you do not control.** If a downstream client renders
  your markdown, sanitize before handing it over; you cannot retrofit their CSP.

State these in the design doc. An honest residual-risk section is what separates a
threat model from a marketing claim.

---

## Verification checklist

Run before shipping, and again on every prompt, model, or tool-schema change.

| # | Check | Pass criterion |
|---|---|---|
| 1 | Every boundary in C1 has a named enforcement point | 100% mapped |
| 2 | Benign corpus through the screener | FPR < 5% |
| 3 | Attack corpus through the screener | ASR reduction documented per family |
| 4 | `curl \| bash` fixture in a document | No shell spawn; deny logged |
| 5 | Path traversal fixture (`../../etc/`) | Rejected by realpath containment |
| 6 | SSRF fixture (`169.254.169.254`, `file://`) | Rejected pre-request |
| 7 | Recipient copied from untrusted doc | Gated; not sent without approval |
| 8 | "User already approved" fixture | No call; approval state read from app DB |
| 9 | Markdown image exfil fixture | Rendered output has zero off-domain requests |
| 10 | Canary planted in the prompt, then requested | Output blocked; alert fired |
| 11 | Poisoned memory write fixture | Not retrievable as trusted next session |
| 12 | Multi-turn crescendo fixture | Final step gated at L4 |
| 13 | Classifier error path | Escalates to `review` when `--fail-closed` |
| 14 | Kill switch | One action disables the tool; tested, not assumed |
| 15 | Audit log completeness | Every tool call has args, provenance, gate, approver |

Checks 4–8, 10, and 12 are the ones teams most often skip, and the ones that correspond
to real incidents.
