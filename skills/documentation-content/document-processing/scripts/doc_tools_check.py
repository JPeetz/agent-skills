#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Document Processing Tool Validator
==================================
Validates the availability of all document-processing tools required by the
document-processing agent skill. Reports missing dependencies with exact
installation commands.

Usage:
    python3 doc_tools_check.py          # Check all tools
    python3 doc_tools_check.py --json   # Machine-readable output
    python3 doc_tools_check.py --pdf    # Check PDF tools only
    python3 doc_tools_check.py --office # Check Office tools only
    python3 doc_tools_check.py --conv   # Check conversion tools only

Exit codes:
    0 — All tools available
    1 — Some tools missing
    2 — Fatal error (Python version, etc.)
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(Enum):
    AVAILABLE = "available"
    MISSING = "missing"
    DEGRADED = "degraded"


@dataclass
class ToolCheck:
    name: str
    category: str
    import_name: Optional[str] = None
    cli_command: Optional[str] = None
    install_pip: Optional[str] = None
    install_brew: Optional[str] = None
    install_apt: Optional[str] = None
    min_version: Optional[str] = None
    notes: str = ""
    status: Status = Status.AVAILABLE
    version_installed: Optional[str] = None


# ── Tool Registry ──────────────────────────────────────────────────────────

TOOLS: list[ToolCheck] = [
    # PDF tools
    ToolCheck(
        name="pypdf",
        category="pdf",
        import_name="pypdf",
        install_pip="pypdf",
        install_brew="",
        install_apt="python3-pypdf",
        min_version="3.0",
        notes="PDF merge, split, rotate, metadata, form filling",
    ),
    ToolCheck(
        name="pdfplumber",
        category="pdf",
        import_name="pdfplumber",
        install_pip="pdfplumber",
        install_brew="",
        install_apt="",
        min_version="0.7",
        notes="Layout-aware text/table extraction from PDFs",
    ),
    ToolCheck(
        name="pytesseract",
        category="pdf",
        import_name="pytesseract",
        install_pip="pytesseract",
        install_brew="tesseract",
        install_apt="tesseract-ocr",
        min_version="0.3",
        notes="OCR engine for scanned PDFs. Also requires system tesseract.",
    ),
    ToolCheck(
        name="pdf2image",
        category="pdf",
        import_name="pdf2image",
        install_pip="pdf2image",
        install_brew="poppler",
        install_apt="poppler-utils",
        min_version="1.16",
        notes="Convert PDF pages to images for OCR. Requires poppler system lib.",
    ),

    # Office tools
    ToolCheck(
        name="python-docx",
        category="office",
        import_name="docx",
        install_pip="python-docx",
        install_brew="",
        install_apt="python3-docx",
        min_version="0.8",
        notes="DOCX creation, editing, template filling, mail merge",
    ),
    ToolCheck(
        name="openpyxl",
        category="office",
        import_name="openpyxl",
        install_pip="openpyxl",
        install_brew="",
        install_apt="python3-openpyxl",
        min_version="3.0",
        notes="XLSX read/write, formulas, charts, pivot tables, styling",
    ),
    ToolCheck(
        name="python-pptx",
        category="office",
        import_name="pptx",
        install_pip="python-pptx",
        install_brew="",
        install_apt="",
        min_version="0.6",
        notes="PPTX creation, editing, charts, speaker notes",
    ),
    ToolCheck(
        name="pandas",
        category="office",
        import_name="pandas",
        install_pip="pandas",
        install_brew="",
        install_apt="python3-pandas",
        min_version="1.3",
        notes="Data manipulation, XLSX↔CSV↔JSON conversion",
    ),

    # Conversion tools
    ToolCheck(
        name="pandoc",
        category="conversion",
        cli_command="pandoc",
        install_pip="",
        install_brew="pandoc",
        install_apt="pandoc",
        min_version="2.14",
        notes="Universal document converter (DOCX, MD, HTML, LaTeX, PDF, etc.)",
    ),
    ToolCheck(
        name="pdf2docx",
        category="conversion",
        import_name="pdf2docx",
        install_pip="pdf2docx",
        install_brew="",
        install_apt="",
        notes="PDF to DOCX conversion with layout preservation",
    ),
    ToolCheck(
        name="LibreOffice",
        category="conversion",
        cli_command="soffice",
        install_pip="",
        install_brew="--cask libreoffice",
        install_apt="libreoffice",
        notes="Headless conversion for DOCX↔PDF, XLSX↔PDF, PPTX↔PDF. Best fidelity.",
    ),
    ToolCheck(
        name="markdown",
        category="conversion",
        import_name="markdown",
        install_pip="markdown",
        install_brew="",
        install_apt="python3-markdown",
        notes="Markdown↔HTML processing for conversion pipelines",
    ),
]


def check_python_version() -> bool:
    """Check minimum Python version."""
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 9):
        print(f"❌ Python 3.9+ required, found {major}.{minor}")
        return False
    return True


def check_import(tool: ToolCheck) -> None:
    """Check if a Python package is importable."""
    try:
        mod = __import__(tool.import_name)
        version = getattr(mod, "__version__", None)
        if version is None:
            # Try common version attributes
            for attr in ("VERSION", "version", "__VERSION__"):
                version = getattr(mod, attr, None)
                if version:
                    break
        if version is None:
            version = "installed"
        tool.version_installed = str(version)
        tool.status = Status.AVAILABLE
    except ImportError:
        tool.status = Status.MISSING


def check_cli(tool: ToolCheck) -> None:
    """Check if a CLI tool is on PATH and get its version."""
    path = shutil.which(tool.cli_command)
    if path is None:
        tool.status = Status.MISSING
        return

    tool.version_installed = path

    # Try to extract version
    version_flags = ["--version", "-v", "-V", "version"]
    for flag in version_flags:
        try:
            result = subprocess.run(
                [tool.cli_command, flag],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                out = result.stdout.strip() or result.stderr.strip()
                if out:
                    tool.version_installed = out.split("\n")[0][:120]
                    break
        except (OSError, subprocess.TimeoutExpired):
            continue

    tool.status = Status.AVAILABLE

    # Special: check tesseract system binary for pytesseract
    if tool.name == "pytesseract" and tool.status == Status.AVAILABLE:
        tesseract_path = shutil.which("tesseract")
        if tesseract_path is None:
            tool.status = Status.DEGRADED
            tool.notes = (
                "Python package installed but 'tesseract' system binary not found. "
                "OCR will not work. Install: brew install tesseract"
            )

    # Special: check poppler for pdf2image
    if tool.name == "pdf2image" and tool.status == Status.AVAILABLE:
        pdftoppm_path = shutil.which("pdftoppm")
        if pdftoppm_path is None:
            tool.status = Status.DEGRADED
            tool.notes = (
                "Python package installed but 'pdftoppm' (poppler) not found. "
                "PDF-to-image conversion will not work. Install: brew install poppler"
            )


def check_tool(tool: ToolCheck) -> None:
    """Run the appropriate check for a tool."""
    if tool.import_name:
        check_import(tool)
    elif tool.cli_command:
        check_cli(tool)
    else:
        tool.status = Status.MISSING
        tool.notes = "No check method defined for this tool"


def get_install_commands(tool: ToolCheck, platform: str) -> list[str]:
    """Get platform-appropriate install commands."""
    commands = []

    if platform == "darwin" and tool.install_brew:
        commands.append(f"brew install {tool.install_brew}")
    elif platform in ("linux", "linux2") and tool.install_apt:
        commands.append(f"sudo apt-get install -y {tool.install_apt}")

    if tool.install_pip:
        commands.append(f"pip install {tool.install_pip}")

    if not commands:
        if tool.name == "pytesseract":
            commands.append("# Requires both pip and system packages:")
            commands.append("brew install tesseract  # macOS")
            commands.append("pip install pytesseract")
        elif tool.name == "pdf2image":
            commands.append("# Requires both pip and system packages:")
            commands.append("brew install poppler  # macOS")
            commands.append("pip install pdf2image")
        else:
            commands.append(f"# Manual install required for: {tool.name}")

    return commands


def generate_report(tools: list[ToolCheck], platform: str, json_output: bool) -> dict:
    """Generate a human or JSON report."""
    available = [t for t in tools if t.status == Status.AVAILABLE]
    degraded = [t for t in tools if t.status == Status.DEGRADED]
    missing = [t for t in tools if t.status == Status.MISSING]

    report = {
        "platform": platform,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "summary": {
            "total": len(tools),
            "available": len(available),
            "degraded": len(degraded),
            "missing": len(missing),
            "ok": len(missing) == 0 and len(degraded) == 0,
        },
        "categories": {},
    }

    for category in sorted(set(t.category for t in tools)):
        cat_tools = [t for t in tools if t.category == category]
        cat_missing = [t for t in cat_tools if t.status != Status.AVAILABLE]
        report["categories"][category] = {
            "tools": {
                t.name: {
                    "status": t.status.value,
                    "version": t.version_installed,
                }
                for t in cat_tools
            },
            "ok": len(cat_missing) == 0,
        }

    if json_output:
        return report

    # ── Human-readable output ───────────────────────────────────────────

    print("=" * 65)
    print("  Document Processing — Tool Availability Report")
    print("=" * 65)
    print(f"  Platform:    {platform}")
    print(f"  Python:      {report['python_version']}")
    print(f"  Available:   {len(available)}/{len(tools)}")
    if degraded:
        print(f"  Degraded:    {len(degraded)}")
    if missing:
        print(f"  Missing:     {len(missing)}")
    print("=" * 65)

    status_icon = {
        Status.AVAILABLE: "✅",
        Status.DEGRADED: "⚠️",
        Status.MISSING: "❌",
    }

    for category in sorted(set(t.category for t in tools)):
        cat_tools = [t for t in tools if t.category == category]
        cat_missing = [t for t in cat_tools if t.status != Status.AVAILABLE]
        symbol = "✅" if not cat_missing else "❌"
        print(f"\n  [{symbol}] {category.upper()} TOOLS")

        for tool in cat_tools:
            icon = status_icon[tool.status]
            ver = tool.version_installed or "—"
            print(f"      {icon} {tool.name:<18} {ver:<50}")
            if tool.notes and tool.status != Status.AVAILABLE:
                print(f"         {tool.notes}")
            if tool.status == Status.DEGRADED:
                print(f"         {tool.notes}")

    if missing or degraded:
        print("\n" + "=" * 65)
        print("  INSTALLATION COMMANDS")
        print("=" * 65)
        needs_install = degraded + missing
        seen = set()
        for tool in needs_install:
            cmds = get_install_commands(tool, platform)
            for cmd in cmds:
                if cmd not in seen:
                    print(f"  {cmd}")
                    seen.add(cmd)

    if missing:
        print(f"\n  ❌ {len(missing)} tool(s) missing. Install them to proceed.")
        return report
    elif degraded:
        print(f"\n  ⚠️  All Python packages installed but {len(degraded)} tool(s)"
              f" have degraded functionality.")
        print("  Core workflow should work; advanced features may be limited.")
        return report
    else:
        print("\n  ✅ All tools available. Ready for document processing.")
        return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate document processing tooling availability"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output machine-readable JSON report"
    )
    parser.add_argument(
        "--pdf", action="store_true",
        help="Check PDF tools only"
    )
    parser.add_argument(
        "--office", action="store_true",
        help="Check Office format tools only"
    )
    parser.add_argument(
        "--conv", "--conversion", action="store_true",
        help="Check conversion tools only",
    )

    args = parser.parse_args()

    if not check_python_version():
        sys.exit(2)

    # Determine platform
    platform = sys.platform
    if platform == "darwin":
        platform_label = "macOS"
    elif platform.startswith("linux"):
        platform_label = "Linux"
    elif platform == "win32":
        platform_label = "Windows"
    else:
        platform_label = platform

    # Filter tools
    if args.pdf:
        tools = [t for t in TOOLS if t.category == "pdf"]
    elif args.office:
        tools = [t for t in TOOLS if t.category == "office"]
    elif args.conv:
        tools = [t for t in TOOLS if t.category == "conversion"]
    else:
        tools = list(TOOLS)

    # Run all checks
    for tool in tools:
        check_tool(tool)

    report = generate_report(tools, platform_label, args.json)

    if args.json:
        print(json.dumps(report, indent=2))

    missing = [t for t in tools if t.status == Status.MISSING]
    degraded = [t for t in tools if t.status == Status.DEGRADED]

    if missing:
        sys.exit(1)
    elif degraded:
        sys.exit(0)  # Degraded is not a fatal condition
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()