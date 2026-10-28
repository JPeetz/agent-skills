# Changelog

## [1.0.0] — 2026-10-28

### Added
- Initial release of the agent-n-video-pipeline skill (fully-local 'Agent N presents a message' on M5).
- Port of the cloud Herald pipeline: Kokoro mature TTS -> LTX-2.3 MLX A2V talking render -> karaoke -> trim -> QA -> X caption.
- One-command usage (herald_pipeline_m5.sh --spec --anchor), spec JSON as single source of truth.
- Segmented mode for >10 s messages; measured performance facts; env gate checklist.
- 5 eval cases with should-trigger/not-trigger scenarios.
