# Model Pricing Reference

Illustrative per-million-token prices for common models, grouped by the tier
they belong to in this skill. **These change frequently — always check provider
docs before trusting a number.** The tier bands are the durable part; the exact
prices are snapshots, not commitments.

## Tier 1: Cheap (~$0.10-0.50/M input tokens)

| Model | Input | Output | Notes |
|---|---|---|---|
| DeepSeek V3 | ~$0.14 | ~$0.28 | General routine work |
| GPT-4o-mini | ~$0.15 | ~$0.60 | Quick responses |
| Claude Haiku | ~$0.25 | ~$1.25 | Fast tool use |
| Gemini Flash | ~$0.075 | ~$0.30 | High volume |
| GLM 5 (Zhipu / OpenRouter Z.AI) | * | * | **text-only** — do not use for vision |
| Kimi K2.5 (Moonshot) | ~$0.45 | ~$2.25 | multimodal (text + image + video); 262K context |

### Tier 2: Mid (~$1-5/M input tokens)

| Model | Input | Output | Notes |
|---|---|---|---|
| Claude Sonnet | ~$3.00 | ~$15.00 | Balanced performance |
| GPT-4o | ~$2.50 | ~$10.00 | Multimodal tasks |
| Gemini Pro | ~$1.25 | ~$5.00 | Long context |

### Tier 3: Premium (~$10-75/M input tokens)

| Model | Input | Output | Notes |
|---|---|---|---|
| Claude Opus | ~$15.00 | ~$75.00 | Complex reasoning |
| GPT-4.5 | ~$75.00 | ~$150.00 | Frontier tasks |
| o1 | ~$15.00 | ~$60.00 | Multi-step reasoning |
| o3-mini | ~$1.10 | ~$4.40 | Reasoning on a budget |

> Requested input/output values are the ones in the seed table and served as the
> basis for the bands. **Prices change — check provider docs for current rates.**

## Vision guidance

- **Text-only models** (for example GLM 5) must never receive image input — no
  photo analysis, screenshots, image-generation tools, or chart/document vision.
  Route those to a vision-capable model (Kimi K2.5, GPT-4o, Gemini, Claude with
  vision, or a GLM vision variant).
- **Vision-capable Tier 1/2 models** (for example Kimi K2.5) handle routine and
  moderate image work without dragging the premium models into it.