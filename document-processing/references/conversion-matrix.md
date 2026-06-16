# Document Format Conversion Matrix

Complete cross-reference for converting between document formats. Each cell
specifies the recommended tool, a quality rating (1–5 ⭐), and any important
considerations.

---

## Quick Reference

```
          TO →
FROM ↓    PDF      DOCX     XLSX     PPTX     MD       HTML     TXT      CSV      JSON
─────────────────────────────────────────────────────────────────────────────────────────
PDF       —        pdf2docx —        —        pandoc   pandoc   pypdf    —        —
                   3⭐                                      4⭐
DOCX      LO soff. —        —        —        pandoc   pandoc   docx     —        —
          5⭐                                      4⭐       4⭐
XLSX      LO soff. —        —        —        —        —        —        pandas   pandas
          4⭐                                                               5⭐       5⭐
PPTX      LO soff. —        —        —        —        —        pptx     —        —
          4⭐                                                    3⭐
MD        pandoc   pandoc   —        markdown —        —        —        —        —
          5⭐       4⭐               4⭐
HTML      pandoc   pandoc   —        —        pandoc   —        —        —        —
          5⭐       4⭐                         4⭐
TXT       —        docx     —        —        —        —        —        —        —
           —       3⭐
CSV       —        —        pandas   —        —        —        —        —        pandas
                            5⭐                                                     5⭐
JSON      —        —        pandas   —        —        —        —        pandas   —
                            4⭐                                              5⭐

⭐ Rating: 5=lossless/high-fidelity, 4=very good, 3=moderate/review needed,
2=poor/lossy, 1=barely usable
```

---

## Detailed Conversion Recipes

### PDF → * (Source: PDF)

#### PDF → DOCX ⭐⭐⭐
**Tool:** `pdf2docx` (Python) or LibreOffice headless
```bash
# Method A: pdf2docx (best for text-heavy PDFs)
pip install pdf2docx
```
```python
from pdf2docx import Converter
cv = Converter("input.pdf")
cv.convert("output.docx")
cv.close()
```

```bash
# Method B: LibreOffice (better for mixed content)
soffice --headless --convert-to docx input.pdf
```

**Considerations:**
- Layout preservation is imperfect — text reflows at page boundaries
- Tables often need manual adjustment
- Images usually survive but positioning may shift
- Scanned/image PDFs will produce a DOCX with embedded images (no text)

#### PDF → Markdown ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.pdf -t markdown -o output.md
```

**Considerations:**
- Works well for text-heavy, simple-layout PDFs
- Multi-column layouts may produce garbled output
- Use `pdfplumber` as fallback for complex layouts:
  ```python
  import pdfplumber
  with pdfplumber.open("input.pdf") as pdf:
      text = "\n\n".join(p.extract_text() or "" for p in pdf.pages)
  with open("output.md", "w") as f:
      f.write(text)
  ```

#### PDF → Text ⭐⭐⭐⭐
**Tool:** `pdfplumber` (primary) or `pypdf` (simple)
```python
import pdfplumber
with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
```

#### PDF → HTML ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.pdf -t html5 -o output.html
```

---

### DOCX → * (Source: Word Document)

#### DOCX → PDF ⭐⭐⭐⭐⭐
**Tool:** LibreOffice headless (best fidelity)
```bash
soffice --headless --convert-to pdf input.docx
```

```bash
# Alternative: pandoc + LaTeX (better typography, requires tex install)
pandoc input.docx -o output.pdf --pdf-engine=xelatex
```

**Considerations:**
- LibreOffice preserves exact layout, fonts, and pagination
- pandoc+LaTeX gives better typography but may alter layout
- Always verify page count matches

#### DOCX → Markdown ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.docx -t markdown -o output.md
```

```bash
# With GitHub-Flavored Markdown
pandoc input.docx -t gfm -o output.md

# Extract images
pandoc input.docx -t markdown --extract-media=./media -o output.md
```

#### DOCX → HTML ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.docx -t html5 -o output.html --standalone
```

#### DOCX → Text ⭐⭐⭐
**Tool:** `python-docx` (programmatic) or `pandoc`
```python
from docx import Document
doc = Document("input.docx")
text = "\n".join(p.text for p in doc.paragraphs)
with open("output.txt", "w") as f:
    f.write(text)
```

---

### XLSX → * (Source: Excel Spreadsheet)

#### XLSX → PDF ⭐⭐⭐⭐
**Tool:** LibreOffice headless
```bash
soffice --headless --convert-to pdf input.xlsx
```

**Considerations:**
- Wide sheets may be split across multiple pages
- Set print area and page breaks in Excel before conversion for best results

#### XLSX → CSV ⭐⭐⭐⭐⭐
**Tool:** `pandas` or `openpyxl`
```python
import pandas as pd

# Single sheet
df = pd.read_excel("input.xlsx")
df.to_csv("output.csv", index=False)

# All sheets
xls = pd.ExcelFile("input.xlsx")
for sheet in xls.sheet_names:
    df = pd.read_excel("input.xlsx", sheet_name=sheet)
    df.to_csv(f"output_{sheet}.csv", index=False)
```

```python
# openpyxl (no pandas dependency)
import csv
from openpyxl import load_workbook
wb = load_workbook("input.xlsx", read_only=True)
ws = wb.active
with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        writer.writerow(row)
```

#### XLSX → JSON ⭐⭐⭐⭐⭐
**Tool:** `pandas`
```python
import pandas as pd
df = pd.read_excel("input.xlsx")
df.to_json("output.json", orient="records", indent=2)

# Multiple sheets → nested JSON
xls = pd.ExcelFile("input.xlsx")
result = {}
for sheet in xls.sheet_names:
    result[sheet] = pd.read_excel("input.xlsx",
                                   sheet_name=sheet).to_dict(orient="records")
import json
with open("output.json", "w") as f:
    json.dump(result, f, indent=2)
```

#### XLSX → Markdown ⭐⭐⭐
**Tool:** `pandas` + manual formatting
```python
import pandas as pd
df = pd.read_excel("input.xlsx")
with open("output.md", "w") as f:
    f.write(df.to_markdown(index=False))
```

---

### PPTX → * (Source: PowerPoint)

#### PPTX → PDF ⭐⭐⭐⭐
**Tool:** LibreOffice headless
```bash
soffice --headless --convert-to pdf input.pptx
```

**Considerations:**
- Animations and transitions are lost (static export)
- Embedded videos become static thumbnails
- Speaker notes not included by default

#### PPTX → Images (per slide) ⭐⭐⭐
**Tool:** Convert to PDF first, then to images

```bash
# Convert PPTX → PDF → images
soffice --headless --convert-to pdf input.pptx
```

```python
from pdf2image import convert_from_path
images = convert_from_path("input.pdf", dpi=200)
for i, img in enumerate(images):
    img.save(f"slide_{i+1:02d}.png")
```

#### PPTX → Text (extract content) ⭐⭐⭐
**Tool:** `python-pptx`
```python
from pptx import Presentation
prs = Presentation("input.pptx")
for i, slide in enumerate(prs.slides):
    print(f"\n=== Slide {i+1} ===")
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text)
```

---

### Markdown → * (Source: Markdown)

#### Markdown → PDF ⭐⭐⭐⭐⭐
**Tool:** `pandoc` + LaTeX engine
```bash
# Best quality
pandoc input.md -o output.pdf --pdf-engine=xelatex

# With template
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --template=eisvogel \
  --metadata title="My Document" \
  --metadata author="Jane Doe"

# With table of contents
pandoc input.md -o output.pdf --pdf-engine=xelatex --toc --toc-depth=3
```

**Common PDF engines:**
| Engine | Best for | Install |
|--------|----------|---------|
| `xelatex` | Unicode, custom fonts | `texlive-xetex` |
| `pdflatex` | Standard LaTeX | `texlive-latex-base` |
| `wkhtmltopdf` | HTML-like styling | `brew install wkhtmltopdf` |
| `weasyprint` | CSS-styled PDFs | `pip install weasyprint` |

#### Markdown → DOCX ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.md -o output.docx

# With style reference document
pandoc input.md --reference-doc=corporate-style.docx -o output.docx
```

**Creating a reference document:**
1. Create a DOCX with desired styles in Word/LibreOffice
2. Save as `corporate-style.docx`
3. Use `--reference-doc` to apply those styles

#### Markdown → PPTX ⭐⭐⭐⭐
**Tool:** `pandoc` or `python-pptx` (custom)
```bash
pandoc input.md -o output.pptx
```

For more control, use the markdown-to-PPTX pattern from `office-formats-guide.md`.

#### Markdown → HTML ⭐⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.md -t html5 -o output.html --standalone \
  --css=style.css --metadata title="My Page"
```

---

### HTML → * (Source: HTML)

#### HTML → DOCX ⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.html -o output.docx
```

#### HTML → PDF ⭐⭐⭐⭐⭐
**Tool:** `pandoc` or `wkhtmltopdf`
```bash
# pandoc with wkhtmltopdf engine
pandoc input.html -o output.pdf --pdf-engine=wkhtmltopdf

# Direct wkhtmltopdf (better for complex HTML/CSS)
wkhtmltopdf input.html output.pdf
```

#### HTML → Markdown ⭐⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.html -t markdown -o output.md
```

---

### Plain Text → * (Source: TXT)

#### TXT → DOCX ⭐⭐⭐
**Tool:** `python-docx` or `pandoc`
```python
from docx import Document
doc = Document()
with open("input.txt") as f:
    for line in f:
        doc.add_paragraph(line.strip())
doc.save("output.docx")
```

#### TXT → PDF ⭐⭐⭐
**Tool:** `pandoc`
```bash
pandoc input.txt -o output.pdf --pdf-engine=xelatex
```

---

### CSV/JSON → * (Source: Tabular Data)

#### CSV → XLSX ⭐⭐⭐⭐⭐
**Tool:** `pandas` or `openpyxl`
```python
import pandas as pd
df = pd.read_csv("input.csv")
df.to_excel("output.xlsx", index=False, sheet_name="Data")
```

#### CSV → JSON ⭐⭐⭐⭐⭐
```python
import pandas as pd
df = pd.read_csv("input.csv")
df.to_json("output.json", orient="records", indent=2)
```

#### JSON → XLSX ⭐⭐⭐⭐
```python
import pandas as pd
df = pd.read_json("input.json", orient="records")
df.to_excel("output.xlsx", index=False)
```

#### JSON → CSV ⭐⭐⭐⭐⭐
```python
import pandas as pd
df = pd.read_json("input.json", orient="records")
df.to_csv("output.csv", index=False)
```

---

## Quality Considerations

### When Fidelity Matters Most

For **legal, compliance, or archival documents**, always use:

```
Source → PDF:      LibreOffice headless (⭐⭐⭐⭐⭐)
Source → PDF/A:    soffice + PDF/A export filter
Source → DOCX:     Native application preferred; LibreOffice as fallback
```

### Lossy Conversions (Expect Data/Style Loss)

```
PDF → DOCX:        Layout changes at page boundaries, tables drift
PPTX → Images:     Animations, transitions, videos lost
XLSX → CSV:        Formulas, formatting, multiple sheets lost (single-sheet only)
DOCX → TXT:        All formatting, images, tables lost
PPTX → TXT:        Only text content preserved
```

### Round-Trip Conversions (Avoid)

```
DOCX → PDF → DOCX:  Significant degradation (⭐⭐) — don't do this
XLSX → CSV → XLSX:  Formulas lost, formatting lost (⭐⭐⭐) — restore manually
PPTX → PDF → PPTX:  Near-total loss (⭐) — each slide becomes one image
```

---

## Batch Conversion Patterns

### Convert All Files in Directory

```bash
# All DOCX → PDF
for f in *.docx; do
  soffice --headless --convert-to pdf "$f"
done

# All MD → DOCX
for f in *.md; do
  pandoc "$f" -o "${f%.md}.docx"
done

# All XLSX → CSV
for f in *.xlsx; do
  python3 -c "
import pandas as pd
df = pd.read_excel('$f')
df.to_csv('${f%.xlsx}.csv', index=False)
"
done
```

### Python Batch Converter

```python
#!/usr/bin/env python3
"""Batch document converter using pandoc."""
import subprocess
import sys
from pathlib import Path

FORMAT_MAP = {
    ".md": {".docx", ".pdf", ".html", ".pptx", ".txt"},
    ".docx": {".pdf", ".md", ".html", ".txt"},
    ".html": {".pdf", ".md", ".docx"},
    ".txt": {".pdf", ".md", ".docx"},
}

def convert_files(input_dir: str, output_dir: str,
                  from_fmt: str, to_fmt: str) -> int:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    count = 0
    for file in input_path.glob(f"*{from_fmt}"):
        out_file = output_path / f"{file.stem}{to_fmt}"
        subprocess.run(
            ["pandoc", str(file), "-o", str(out_file)],
            check=True
        )
        print(f"  ✓ {file.name} → {out_file.name}")
        count += 1

    return count
```

---

## Tool Installation Summary

| Tool | macOS | Linux (apt) | pip |
|------|-------|-------------|-----|
| pandoc | `brew install pandoc` | `apt install pandoc` | — |
| LibreOffice | `brew install --cask libreoffice` | `apt install libreoffice` | — |
| pypdf | — | — | `pip install pypdf` |
| pdfplumber | — | — | `pip install pdfplumber` |
| pdf2docx | — | — | `pip install pdf2docx` |
| python-docx | — | — | `pip install python-docx` |
| openpyxl | — | — | `pip install openpyxl` |
| python-pptx | — | — | `pip install python-pptx` |
| pandas | — | — | `pip install pandas` |
| pdf2image | `brew install poppler` | `apt install poppler-utils` | `pip install pdf2image` |
| pytesseract | `brew install tesseract` | `apt install tesseract-ocr` | `pip install pytesseract` |