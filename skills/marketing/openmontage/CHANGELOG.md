# Changelog

## [1.0.0] — 2026-10-28

### Added
- Initial release of the openmontage skill (video production via the OpenMontage repo).
- Safety rules: work only inside OM repo, read AGENT_GUIDE.md, never bypass pipelines, approval gates for paid/batch generation.
- Workflow: classify request -> find pipeline manifest -> preflight -> proposal -> workspace -> stage-by-stage execution -> ffprobe verification.
- Blocker protocol and reactive troubleshooting (VIDEO_GEN_LOCAL_ENABLED, diffusers install, talking-head over lip-sync-first).
- 5 eval cases with should-trigger/not-trigger scenarios.
