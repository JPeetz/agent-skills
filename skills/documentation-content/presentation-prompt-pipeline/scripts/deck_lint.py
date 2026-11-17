#!/usr/bin/env python3
# /// script
# dependencies = ["python-pptx"]
# ///
"""Lint a .pptx deck against the presentation rules this skill prescribes.

Checks the mechanically verifiable half of a deck review, so the reviewer can
spend attention on story and visuals instead of counting words:

  * slide title length (default: 6 words max)
  * bullets per slide (default: 5 max)
  * words per bullet (default: 10 max)
  * speaker notes present on every slide
  * distinct heading/body font families (default: 2 max)
  * distinct explicit text colours (default: 3 max)

Findings are printed as JSON. Exit code 0 = clean, 1 = findings, 2 = the file
could not be read.

Usage:
  uv run --with python-pptx scripts/deck_lint.py deck.pptx
  uv run --with python-pptx scripts/deck_lint.py deck.pptx --max-title-words 8 --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# Layout body placeholders that carry bullet text rather than titles.
_BULLET_PLACEHOLDER_TYPES = {"BODY", "OBJECT", "SUBTITLE", "TEXT_PLACEHOLDER"}
_WORD = re.compile(r"[^\s]+")


def _words(text: str) -> int:
    return len(_WORD.findall(text.strip()))


def _shape_paragraphs(shape):
    """Yield (paragraph, text) for a shape that has a text frame."""
    if not getattr(shape, "has_text_frame", False):
        return
    for paragraph in shape.text_frame.paragraphs:
        text = paragraph.text.strip()
        if text:
            yield paragraph, text


def _is_bullet_container(shape) -> bool:
    if not getattr(shape, "is_placeholder", False):
        return False
    try:
        kind = shape.placeholder_format.type
    except (AttributeError, ValueError):
        return False
    return getattr(kind, "name", "") in _BULLET_PLACEHOLDER_TYPES


def _slide_title(slide) -> str:
    title_shape = slide.shapes.title
    if title_shape is not None and title_shape.has_text_frame:
        return title_shape.text_frame.text.strip()
    # Blank-layout slides: fall back to the first non-empty text shape.
    for shape in slide.shapes:
        for _, text in _shape_paragraphs(shape):
            return text
    return ""


def _bullets(slide) -> list[str]:
    found: list[str] = []
    for shape in slide.shapes:
        if not _is_bullet_container(shape):
            continue
        for paragraph, text in _shape_paragraphs(shape):
            level = getattr(paragraph, "level", 0) or 0
            if text and level >= 0:
                found.append(text)
    return found


def _notes_text(slide) -> str:
    if not slide.has_notes_slide:
        return ""
    frame = slide.notes_slide.notes_text_frame
    return frame.text.strip() if frame is not None else ""


def _fonts_and_colours(prs):
    fonts: set[str] = set()
    colours: set[str] = set()
    for slide in prs.slides:
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    name = run.font.name
                    if name:
                        fonts.add(name)
                    try:
                        rgb = run.font.color.rgb
                    except (AttributeError, TypeError, ValueError):
                        rgb = None
                    if rgb is not None:
                        colours.add(str(rgb))
    return fonts, colours


def lint(path: str, args) -> dict:
    from pptx import Presentation

    prs = Presentation(path)
    findings: list[dict] = []
    slides_report: list[dict] = []

    for index, slide in enumerate(prs.slides, start=1):
        title = _slide_title(slide)
        bullets = _bullets(slide)
        notes = _notes_text(slide)
        title_words = _words(title)

        slides_report.append(
            {
                "slide": index,
                "title": title,
                "title_words": title_words,
                "bullets": len(bullets),
                "notes": bool(notes),
            }
        )

        if title_words > args.max_title_words:
            findings.append(
                {
                    "rule": "title_words",
                    "slide": index,
                    "message": f"title has {title_words} words (max {args.max_title_words}): {title!r}",
                }
            )
        if not title:
            findings.append(
                {"rule": "missing_title", "slide": index, "message": "slide has no title text"}
            )
        if len(bullets) > args.max_bullets:
            findings.append(
                {
                    "rule": "bullet_count",
                    "slide": index,
                    "message": f"{len(bullets)} bullets (max {args.max_bullets})",
                }
            )
        for bullet in bullets:
            count = _words(bullet)
            if count > args.max_bullet_words:
                findings.append(
                    {
                        "rule": "bullet_words",
                        "slide": index,
                        "message": f"bullet has {count} words (max {args.max_bullet_words}): {bullet[:70]!r}",
                    }
                )
        if args.require_notes and not notes:
            findings.append(
                {"rule": "missing_notes", "slide": index, "message": "no speaker notes"}
            )

    fonts, colours = _fonts_and_colours(prs)
    if len(fonts) > args.max_fonts:
        findings.append(
            {
                "rule": "font_families",
                "message": f"{len(fonts)} font families (max {args.max_fonts}): {sorted(fonts)}",
            }
        )
    if len(colours) > args.max_colors:
        findings.append(
            {
                "rule": "text_colours",
                "message": f"{len(colours)} explicit text colours (max {args.max_colors}): {sorted(colours)}",
            }
        )

    return {
        "path": path,
        "slides": len(prs.slides),
        "fonts": sorted(fonts),
        "text_colours": sorted(colours),
        "ok": not findings,
        "finding_count": len(findings),
        "findings": findings,
        "per_slide": slides_report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("deck", help="path to a .pptx file")
    parser.add_argument("--max-title-words", type=int, default=6)
    parser.add_argument("--max-bullets", type=int, default=5)
    parser.add_argument("--max-bullet-words", type=int, default=10)
    parser.add_argument("--max-fonts", type=int, default=2)
    parser.add_argument("--max-colors", type=int, default=3, dest="max_colors")
    parser.add_argument("--no-notes-check", action="store_true", help="skip the speaker-notes rule")
    parser.add_argument("--json", action="store_true", help="print only the JSON report")
    args = parser.parse_args(argv)
    args.require_notes = not args.no_notes_check

    try:
        report = lint(args.deck, args)
    except Exception as exc:  # unreadable deck is a hard failure, not a finding
        print(json.dumps({"ok": False, "error": str(exc), "path": args.deck}), file=sys.stdout)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        print(f"{status} {report['path']} — {report['slides']} slides, {report['finding_count']} finding(s)")
        for finding in report["findings"]:
            where = f"slide {finding['slide']}: " if "slide" in finding else ""
            print(f"  [{finding['rule']}] {where}{finding['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
