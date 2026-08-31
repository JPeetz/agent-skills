# Changelog — Document Processing Agent Skill

All notable changes to this skill package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.1.0 — 2026-06-09 (Run 003)

### Added
- SEO-optimized description with primary keyword clusters for AI engine discovery
- QUICK REFERENCE table at top of SKILL.md — task → library/tool → key command
- COMMON PITFALLS & ANTI-PATTERNS section (10 anti-patterns with fixes)
- Decision matrix table: which library for each operation across PDF/DOCX/XLSX/PPTX
- GEO metadata block for structured AI engine summarization
- Windsurf and OpenCode platform compatibility notes

### Changed
- Expanded platforms list to all 8: claude-code, codex, cursor, gemini-cli, openclaw, copilot, windsurf, opencode
- Version bumped to 1.1.0
- Clarified non-trigger boundaries with additional negative examples
- SKILL.md line count: 758 → 872 (+114 lines)

---

## v1.0.0 — 2026-05-28

### Added
- Initial release by Skill Foundry
- **PDF Processing:** text extraction (pypdf + pdfplumber), merge, split,
  rotate, watermark, form filling, OCR (pytesseract), annotations, image
  extraction, metadata manipulation, encryption handling
- **DOCX Processing:** template-based generation with placeholder
  replacement, build-from-scratch with python-docx, mail merge, style
  management, headers/footers, DOCX→PDF conversion
- **XLSX Processing:** spreadsheet creation with formatting, formulas,
  charts (bar, line, pie, combo), pivot tables, conditional formatting,
  data validation, multi-sheet workbooks, XLSX↔CSV↔JSON conversion
- **PPTX Processing:** slide generation from markdown, template-driven
  decks, chart embedding, tables, shapes, speaker notes, image slides
- **Format Conversion:** full cross-reference matrix for PDF, DOCX, XLSX,
  PPTX, Markdown, HTML, TXT, CSV, JSON conversions via pandoc and native
  libraries
- **Pre-flight validation:** PEP 723 `doc_tools_check.py` script checking
  availability of all required tools with platform-specific install
  instructions
- **Safety rules:** never overwrite source files, always validate output,
  warn on destructive operations, handle missing dependencies gracefully
- **Platform support:** Claude Code, Codex, Cursor, Gemini CLI, OpenClaw,
  GitHub Copilot with platform-specific compatibility notes
- **8 eval cases:** 5 positive (PDF extraction, DOCX report, XLSX with
  charts, PPTX from markdown, PDF form filling) + 3 near-miss negatives
  (read-only PDF viewing, general text editing, image editing)
- **Reference guides:**
  - `pdf-processing-guide.md` — 14-section deep dive on all PDF operations
  - `office-formats-guide.md` — DOCX, XLSX, PPTX patterns, templates, and
    cross-format style management
  - `conversion-matrix.md` — complete format conversion pair matrix with
    quality ratings and tool recommendations
