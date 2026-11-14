# Sources

Reference material behind this skill. Primary sources (papers, specs, vendor engineering docs) take precedence over secondary write-ups; where a claim is contested, the paper is the authority.

## Upstream skill collections

- GitHub, `awesome-copilot` (MIT) — https://github.com/github/awesome-copilot
  Community collection of Copilot instructions, prompts, and skills. Source for the packaging conventions this skill follows (SKILL.md frontmatter, description-as-trigger, eval cases alongside the skill) rather than for the eval methodology itself.
- Addy Osmani, `agent-skills` (MIT) — https://github.com/addyosmani/agent-skills
  Structural reference for the section layout, anti-pattern table, red flags, and verification checklist used across this repo.

## Evaluator-optimizer and agent architecture

- Anthropic, "Building Effective Agents" — https://www.anthropic.com/engineering/building-effective-agents
  Names the evaluator-optimizer workflow and states the precondition this skill repeats: iteration must measurably improve the artifact, and the evaluator must give specific, actionable feedback.
- Anthropic, "Effective harnesses for long-running agents" — https://www.anthropic.com/engineering
  Practical notes on bounded loops, progress artifacts, and why agents need external checks rather than self-assessment.
- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023) — https://arxiv.org/abs/2303.11366
  Self-reflection with an external signal (test pass/fail) improves agents; reflection without an external signal mostly reinforces existing behavior. The basis for "self-critique needs a check it cannot talk its way out of."
- Yao et al., "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (2024) — https://arxiv.org/abs/2406.12045
  Task-success measurement for tool-using agents with a simulated user; the pass^k reliability metric is the reason single-run success rates overstate agent quality.

## Self-critique and self-refinement

- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" (2023) — https://arxiv.org/abs/2303.17651
  The canonical self-refine loop, plus the finding that gains vary sharply by task and model — the empirical basis for treating self-critique as a partial tool, not a correctness guarantee.
- Panickssery et al., "LLM Evaluators Recognize and Favor Their Own Generations" (2024) — https://arxiv.org/abs/2404.13076
  Measures self-preference and links it to self-recognition; the reason this skill insists the judge differ from the model under test, or be offset-calibrated.
- Lightman et al., "Let's Verify Step by Step" (2023) — https://arxiv.org/abs/2305.20050
  Process supervision beats outcome supervision for reasoning: score the trajectory, not only the final answer.

## LLM-as-judge and rubric design

- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023) — https://arxiv.org/abs/2306.05685
  Establishes strong judge–human agreement on open-ended tasks, and documents the three biases this skill tells you to probe: position, verbosity, and self-enhancement.
- Liu et al., "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment" (2023) — https://arxiv.org/abs/2303.16634
  Chain-of-thought evaluation with form-filling and probability-weighted scoring; the source for "reason before you label" and for criteria expressed as explicit evaluation steps.
- Kim et al., "Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models" (2024) — https://arxiv.org/abs/2405.01535
  Shows a small judge trained on rubrics can track a proprietary judge closely — relevant when you need a cheap, stable, self-hosted evaluator.
- Tan et al., "JudgeBench: A Benchmark for Evaluating LLM-based Judges" (2024) — https://arxiv.org/abs/2410.12784
  Judges that look strong on preference data degrade on hard correctness judgments; argues for difficulty-stratified calibration sets rather than a single agreement number.
- Chan et al., "ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate" (2023) — https://arxiv.org/abs/2308.07201
  Multi-agent critique as an alternative to single-judge scoring, with the cost trade-off made explicit.

## Position bias, pairwise comparison, and ranking

- Wang et al., "Large Language Models are not Fair Evaluators" (2023) — https://arxiv.org/abs/2305.17926
  Quantifies position bias in LLM judges and proposes order-swapping with agreement required — the default control in this skill's pairwise section.
- Bradley & Terry, "Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons", Biometrika 39(3/4), 1952 — https://doi.org/10.2307/2334029
  The model behind Bradley–Terry ranking, including why confidence intervals matter when comparisons are incomplete.
- Elo, *The Rating of Chessplayers, Past and Present* (1978)
  Online rating approximation; used here only for live leaderboards, with the caveat that results depend on presentation order.

## Calibration, agreement, and measurement validity

- Cohen, "A Coefficient of Agreement for Nominal Scales", *Educational and Psychological Measurement* 20(1), 1960 — https://doi.org/10.1177/001316446002000104
  Cohen's κ, and the chance-correction that makes raw agreement misleading on imbalanced label sets.
- Shankar et al., "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences" (2024) — https://arxiv.org/abs/2404.12272
  EvalGen: criteria drift, criteria-implementation mismatch, and why human preference data must anchor any judge-based metric.
- Shankar et al., "Operationalizing Machine Learning: An Interview Study" (2022) — https://arxiv.org/abs/2209.15174
  Practitioner accounts of evaluation debt — metrics that stopped matching the product and nobody noticed.
- Liang et al., "Holistic Evaluation of Language Models" (HELM, 2022) — https://arxiv.org/abs/2211.09110
  Multi-metric, scenario-stratified evaluation; the argument against collapsing quality into one headline number.
- Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation" (2023) — https://arxiv.org/abs/2309.15217
  Reference-free faithfulness/answer-relevance metrics for retrieval systems — the component-level (level 2–3) scores this skill recommends before end-to-end judging.

## Agent and coding benchmarks

- Liu et al., "AgentBench: Evaluating LLMs as Agents" (2023) — https://arxiv.org/abs/2308.03688
  Multi-environment agent evaluation; shows how much scores move with environment and harness details, which is why the runner must pin configuration.
- Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (2023) — https://arxiv.org/abs/2310.06770
  Executable end-to-end evaluation (tests as the oracle) — the model for level-4 checks that cannot be argued with.
- Mialon et al., "GAIA: A Benchmark for General AI Assistants" (2023) — https://arxiv.org/abs/2311.12983
  Real-world assistant tasks with unambiguous answers, designed so simple string matching can score them.

## Tooling and harness references

- OpenAI Evals — https://github.com/openai/evals
  Dataset/registry format and the "eval as a yaml + runner" convention.
- OpenAI simple-evals — https://github.com/openai/simple-evals
  Minimal, readable harness implementations; useful as a template for keeping the runner boring.
- Hamel Husain, "Your AI Product Needs Evals" — https://hamel.dev/blog/posts/evals/
  Practitioner guidance on unit tests, LLM-as-judge, and human review in a layered system; the closest public articulation of the pyramid used here.
- LangSmith / Braintrust / promptfoo docs — https://promptfoo.dev/docs/configuration/guide/
  Promptfoo's declarative assertion model (deterministic asserts plus `llm-rubric` graders) is a good reference implementation of the gate-then-judge scorer.

## Adjacent skills in this repo

- `skills/qa-testing/playwright-e2e` — deterministic end-to-end browser assertions; level 1–4 checks that need no judge.
- `skills/development/prompt-engineering` — prompt structure and iteration; this skill tells you whether the iteration worked.
- `skills/code-quality/code-review` — human/agent review of code diffs; the human-review tier of the pyramid for code artifacts.
- `skills/ai-agent-engineering/ai-agent-architecture` — topology, tool design, and state management for agents whose behavior this skill measures.
