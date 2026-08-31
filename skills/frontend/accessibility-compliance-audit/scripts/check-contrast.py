#!/usr/bin/env python3
# accessibility-compliance-audit — compute WCAG contrast ratios
# Usage: python3 check-contrast.py "#FFFFFF" "#333333"
# PEP 723 inline dependencies
# /// script
# requires-python = ">=3.8"
# ///

import sys
import re

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb: tuple) -> float:
    """Calculate relative luminance per WCAG 2.2."""
    vals = []
    for c in rgb:
        s = c / 255.0
        vals.append(s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]

def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(hex_to_rgb(fg_hex))
    l2 = relative_luminance(hex_to_rgb(bg_hex))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def wcag_grade(ratio: float, is_large_text: bool = False) -> str:
    """Return WCAG compliance grade."""
    threshold = 3.0 if is_large_text else 4.5
    aaa_threshold = 4.5 if is_large_text else 7.0

    if ratio >= aaa_threshold:
        return "✅ AAA (enhanced)"
    elif ratio >= threshold:
        return "✅ AA (pass)"
    else:
        return "❌ FAIL"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 check-contrast.py <foreground> <background>")
        print("Example: python3 check-contrast.py '#FFFFFF' '#333333'")
        sys.exit(1)

    fg = sys.argv[1]
    bg = sys.argv[2]

    if not re.match(r'^#?[0-9a-fA-F]{6}$', fg) or not re.match(r'^#?[0-9a-fA-F]{6}$', bg):
        print("❌ Colors must be hex format: #RRGGBB or RRGGBB")
        sys.exit(1)

    ratio = contrast_ratio(fg, bg)
    print(f"Foreground: {fg}")
    print(f"Background: {bg}")
    print(f"Contrast Ratio: {ratio:.2f}:1")
    print(f"Normal Text: {wcag_grade(ratio, is_large_text=False)}")
    print(f"Large Text:  {wcag_grade(ratio, is_large_text=True)}")
    print(f"UI Component: {'✅ AA (pass)' if ratio >= 3.0 else '❌ FAIL'} (WCAG 1.4.11)")