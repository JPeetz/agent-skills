# Changelog

## [1.0.0] — 2026-10-28

### Added
- Initial release of the local-video-production-m5 skill (16 GB Apple Silicon executor doctrine).
- Memory discipline: GGUF Q4/Q5 or MLX ports, PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0, LM Studio off, lowvram/tiling, 3-5 s clips.
- Model priority: LTX-2.x A2V > Wan 2.2 TI2V-5B > Wan 1.3B; CUDA-is-not-MPS guidance with runtime device detection.
- Character consistency via multi-view sheet + I2V first-frame + re-anchoring; measured speed facts (16 s/frame) and segmented renders.
- 5 eval cases with should-trigger/not-trigger scenarios.
