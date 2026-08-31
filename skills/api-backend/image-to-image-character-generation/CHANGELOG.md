# Changelog

All notable changes to the `image-to-image-character-generation` skill.

## [1.0.0] - 2026-08-17
- Initial release.
- Core capability: generate consistent character images across scenes using
  kie.ai grok-imagine/image-to-image from Supabase S3 or Google Drive reference
  photos.
- Reference selection with mandatory face anchors + keyword-scored pose refs,
  model-aware ref key/count, dynamic prompt composition with anti-repeat deque,
  strength calibration, fallback model, and post-generation workflow.