---
name: document-processing
description: >
  End-to-end document processing agent skill covering PDF manipulation
  (extract, merge, split, rotate, watermark, form-fill, OCR), DOCX
  creation and editing (templates, mail-merge, style management), XLSX
  spreadsheet handling (formulas, charts, pivot tables, data analysis),
  PPTX presentation generation (layouts, charts, media, speaker notes),
  and cross-format document conversion via pandoc and native libraries.
  Primary keyword clusters: PDF manipulation automation, DOCX generation
  Python, Excel spreadsheet automation openpyxl, PowerPoint generation
  python-pptx, document format conversion pandoc, mail merge automation,
  PDF OCR extraction, batch document processing, office automation Python,
  template-driven document generation. Designed for agentic platforms —
  Claude Code, Codex, Cursor, Gemini CLI, OpenClaw, GitHub Copilot,
  Windsurf, and OpenCode.
version: 1.1.0
author: Skill Foundry
platforms:
  - claude-code
  - codex
  - cursor
  - gemini-cli
  - openclaw
  - copilot
  - windsurf
  - opencode
tags:
  - document
  - pdf
  - docx
  - xlsx
  - pptx
  - conversion
  - office
  - automation
  - form-filling
  - ocr
  - report-generation
geo:
  primary_workflows:
    - pdf_manipulation
    - document_generation
    - spreadsheet_automation
    - presentation_creation
    - format_conversion
    - batch_document_processing
  target_roles:
    - business_analyst
    - data_analyst
    - operations_manager
    - report_writer
    - legal_professional
  complexity_level: intermediate
  prerequisite_knowledge:
    - python_basics
    - file_io
    - document_structure_concepts
---

# Document Processing — Agent Skill

End-to-end document processing for agentic workflows. Create, read, edit,
convert, and analyze documents across the five major office formats: PDF,
DOCX, XLSX, PPTX, and cross-format conversion.

---

## Quick Reference

| Task | Library/Tool | Key Command/Pattern |
|---|---|---|
| Extract text (simple) | `pypdf` | `PdfReader("f.pdf").pages[0].extract_text()` |
| Extract text (layout) | `pdfplumber` | `pdf.pages[i].extract_text()` |
| Extract tables | `pdfplumber` | `pdf.pages[i].extract_tables()` |
| Merge PDFs | `pypdf` | `PdfWriter().append(…).write("out.pdf")` |
| Split PDFs | `pypdf` | Write page slices to separate files |
| Rotate pages | `pypdf` | `page.rotate(90)` |
| Add watermark | `pypdf` | Overlay PDF onto target |
| Fill form fields | `pypdf` | `update_page_form_field_values(page, data)` |
| OCR scanned PDF | `pytesseract + pdf2image` | Convert to images → Tesseract |
| Create DOCX from scratch | `python-docx` | `Document().add_heading(…)` |
| Mail merge (template) | `python-docx` + CSV | Replace `{{PLACEHOLDER}}` in runs |
| DOCX → PDF | LibreOffice headless | `soffice --headless --convert-to pdf` |
| Create XLSX with charts | `openpyxl` | `Workbook()` → add `BarChart()` |
| Pivot table | `openpyxl` | `PivotTable()` on new sheet |
| XLSX → CSV | `pandas` | `read_excel().to_csv()` |
| Create PPTX | `python-pptx` | `Presentation().slides.add_slide(…)` |
| Speaker notes | `python-pptx` | `slide.notes_slide.notes_text_frame.text` |
| Cross-format convert | `pandoc` | `pandoc input.docx -o output.md` |
| Validate tools | `doc_tools_check.py` | Run at start of every session |

---

## When to Activate

Activate this skill when the user needs to **do something with a document**
as opposed to merely viewing it. Activation triggers include:

| Trigger | Example phrasing |
|---------|-----------------|
| PDF manipulation | "extract pages from this PDF", "merge these PDFs", "fill out this form", "rotate page 3", "add a watermark", "OCR this scanned document", "split this PDF into chapters" |
| DOCX creation / editing | "write a report as a Word doc", "update the template", "mail-merge these names", "convert my markdown to DOCX", "generate an invoice as .docx" |
| XLSX spreadsheet work | "create a budget spreadsheet", "add a chart to the Excel file", "calculate column totals", "generate a pivot table", "format this data as a table" |
| PPTX presentation | "make a slide deck from these notes", "add speaker notes", "generate charts in PowerPoint", "create a presentation from this outline" |
| Format conversion | "convert PDF to DOCX", "turn this Word doc into Markdown", "XLSX to CSV", "DOCX to PDF", "PPTX to images" |

**Non-triggers** (do NOT activate):
- "Read this PDF to me" (pure text extraction for viewing — use a simpler read/extract path, not this full skill)
- "Edit this paragraph" (general text editing, not document-format editing)
- "What does this image look like?" (image analysis, not document processing)
- "Summarise this article" (content summarisation, not document manipulation)
- "Can you crop this photo?" (image editing, not document processing)

---

## Common Pitfalls & Anti-Patterns

### ❌ NEVER do these

1. **Overwriting the source file — you'll lose the original**
   - Always write to `{original}_processed.{ext}` or `{original}_{operation}.{ext}`
   - If the user insists on overwrite, show both paths and confirm first

2. **Forgetting to run `doc_tools_check.py` before operations**
   - Missing libraries cause obscure errors. Run the checker first in every session.

3. **Using `pypdf` for table extraction — it'll give you garbage**
   - `pypdf` extracts raw text with no layout awareness. Use `pdfplumber` for tables and columnar text.

4. **Loading a 500MB file entirely into memory**
   - For large files (>100MB): use streaming/chunking. For PDFs >1,000 pages: extract page ranges.

5. **Assuming `cell.value` returns a formatted string when it returns `None`**
   - XLSX formulas return `None` unless you load with `data_only=True`. Even then, cached values may be stale.

6. **Using hardcoded slide layout indices (`prs.slide_layouts[0]`)**
   - Layout order differs between templates. List dynamically: `[ly.name for ly in prs.slide_layouts]`

7. **Running Pandoc without checking it's installed**
   - Pandoc is a system dependency, not a Python package. `brew install pandoc` / `apt install pandoc`.

8. **Trying to fill XFA (XML Forms Architecture) forms with pypdf**
   - `pypdf` only handles AcroForm fields. XFA forms require different tools — check `reader.get_fields()` first.

9. **Embedding 4000px images into DOCX files**
   - Resize images before embedding: `img.thumbnail((1920, 1080))`. Unscaled images balloon file sizes.

10. **Mixing document formats without checking conversion quality**
    - PDF → DOCX conversion loses structure. DOCX → PDF via LibreOffice preserves it. Check `references/conversion-matrix.md` for quality ratings.

### ✅ Decision Matrix: Which Library When?

| Outcome | PDF | DOCX | XLSX | PPTX |
|---|---|---|---|---|
| Simple text extraction | `pypdf` | N/A | N/A | N/A |
| Layout-aware text | `pdfplumber` | `python-docx` | `openpyxl` | `python-pptx` |
| Table extraction | `pdfplumber` | `python-docx` | `openpyxl` | N/A |
| Create from scratch | N/A | `python-docx` | `openpyxl` | `python-pptx` |
| Template filling | `pypdf` (forms) | `python-docx` | `openpyxl` | `python-pptx` |
| Charts | N/A | N/A | `openpyxl` | `python-pptx` |
| Images/OCR | `pytesseract` | `python-docx` | `openpyxl` | `python-pptx` |
| Conversion to other | LibreOffice | pandoc/LibreOffice | pandas/LibreOffice | LibreOffice |

---

## Safety Rules (Mandatory)

1. **Never overwrite the source file.** Always write output to a new path.
   Default naming: `{original_name}_processed.{ext}` or
   `{original_name}_{operation}.{ext}`.

2. **Validate output integrity.** After every write operation, read back the
   output file and confirm:
   - The file exists and is non-empty.
   - Page / row / slide counts are correct.
   - Critical content (text, data, images) survived the operation.

3. **Warn on destructive operations.** If a user explicitly asks to overwrite
   the source, confirm before proceeding. Show both paths and ask.

4. **Handle missing dependencies gracefully.** Run `scripts/doc_tools_check.py`
   before any document operation. If a required library is missing, install it
   (with user approval) or suggest the command.

5. **Preserve metadata when possible.** Author, creation date, and custom
   properties should survive transformations unless the user explicitly asks
   to strip them.

6. **Respect file size limits.** For files >100 MB, warn the user and suggest
   streaming / chunking approaches. For PDFs >1,000 pages, use page-range
   extraction instead of loading the entire document.

---

## Pre-Flight: Tool Validation

Before any document operation, validate the tooling:

```bash
python3 scripts/doc_tools_check.py
```

The script checks for:
- `pypdf` — PDF manipulation (merge, split, rotate, metadata)
- `pdfplumber` — PDF text/table extraction with layout awareness
- `python-docx` — DOCX read/write
- `openpyxl` — XLSX read/write, formulas, charts
- `python-pptx` — PPTX read/write, slide generation
- `pandoc` — universal format conversion (CLI)

If a tool is missing, the script outputs the exact `pip install` or `brew
install` command. Run it first in every document-processing session.

---

## Workflow: PDF Manipulation

### 1. Assess the Document

```python
from pypdf import PdfReader
reader = PdfReader("input.pdf")
print(f"Pages: {len(reader.pages)}")
print(f"Metadata: {reader.metadata}")
print(f"Encrypted: {reader.is_encrypted}")
```

If encrypted and the user provides a password:

```python
reader.decrypt("the_password")
```

### 2. Choose the Right Tool

| Operation | Tool | Why |
|-----------|------|-----|
| Extract text (simple) | `pypdf` | Fast, lightweight |
| Extract text (layout-aware) | `pdfplumber` | Preserves columns, tables, positioning |
| Extract tables | `pdfplumber` | Direct `.extract_tables()` |
| Merge PDFs | `pypdf` | `PdfWriter.append()` |
| Split PDFs | `pypdf` | Write page ranges to separate files |
| Rotate pages | `pypdf` | `page.rotate(90)` |
| Add watermark | `pypdf` | Overlay one PDF onto another |
| Fill form fields | `pypdf` | `reader.get_fields()` → `writer.update_page_form_field_values()` |
| OCR scanned docs | `pytesseract` + `pdf2image` | Tesseract OCR pipeline |
| Add annotations | `pypdf` | Free-text, highlight, link annotations |
| Extract images | `pypdf` | Iterate `/XObject` resources |

### 3. Execute with Validation

**Text extraction example:**
```python
import pdfplumber
with pdfplumber.open("input.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        tables = page.extract_tables()
        print(f"--- Page {i+1} ---")
        print(text)
```

**Merge example:**
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for path in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    writer.append(path)

writer.write("merged_output.pdf")
# Validate
assert len(PdfReader("merged_output.pdf").pages) == expected_pages
```

**Form filling example:**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

writer.append(reader)
fields = reader.get_fields()
# Show user available fields, collect values
writer.update_page_form_field_values(writer.pages[0], {
    "Name": "Jane Doe",
    "Date": "2026-05-28",
    "Amount": "150.00"
})
writer.write("form_filled.pdf")
```

**OCR example:**
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf", dpi=300)
text = "\n\n".join(pytesseract.image_to_string(img) for img in images)
with open("scanned_ocr.txt", "w") as f:
    f.write(text)
```

### 4. Common Issues & Remedies

| Issue | Remedy |
|-------|--------|
| Encrypted PDF without password | Ask user for password; if unavailable, report and stop |
| Scanned PDF (image-only) | Use OCR path (pdf2image + pytesseract) |
| Corrupt PDF | Try `pypdf.PdfReader(strict=False)`, or use `mutool` repair |
| Extracted text is garbled | Use `pdfplumber` instead of `pypdf` for layout-aware extraction |
| Form fields not found | Check `reader.get_fields()` — some PDFs use XFA forms (unsupported) |

---

## Workflow: DOCX Creation & Editing

### 1. Decide: Template or Blank

- **Template approach:** Start from an existing `.docx` with placeholders like
  `{{NAME}}`, `{{DATE}}`, `{{AMOUNT}}`. Best for reports, invoices, letters.
- **Blank approach:** Build from `Document()` using `python-docx`. Best for
  simple documents or when no template exists.

### 2. Template Pattern

```python
from docx import Document

doc = Document("template.docx")

# Replace placeholders across all paragraphs, tables, headers, footers
placeholders = {
    "{{NAME}}": "Jane Doe",
    "{{DATE}}": "28 May 2026",
    "{{AMOUNT}}": "€1,500.00"
}

def replace_in_paragraphs(paragraphs):
    for para in paragraphs:
        for key, val in placeholders.items():
            if key in para.text:
                for run in para.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, val)

replace_in_paragraphs(doc.paragraphs)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            replace_in_paragraphs(cell.paragraphs)
for section in doc.sections:
    replace_in_paragraphs(section.header.paragraphs)
    replace_in_paragraphs(section.footer.paragraphs)

doc.save("output.docx")
```

### 3. Building from Scratch

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# Styles
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# Heading
doc.add_heading('Quarterly Report', level=1)

# Paragraph
p = doc.add_paragraph('Executive summary of Q1 2026 results.')
p.alignment = WD_ALIGN_PARAGRAPH.LEFT

# Bold run
run = p.add_run(' Key highlights:')
run.bold = True

# Bullet list
for item in ['Revenue up 12%', 'Costs down 4%', '3 new markets entered']:
    doc.add_paragraph(item, style='List Bullet')

# Table
table = doc.add_table(rows=3, cols=3, style='Light Grid Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
data = [['Metric', 'Q4 2025', 'Q1 2026'],
        ['Revenue', '€2.1M', '€2.35M'],
        ['Profit', '€420K', '€510K']]
for i, row_data in enumerate(data):
    for j, cell_val in enumerate(row_data):
        table.rows[i].cells[j].text = cell_val

# Image
doc.add_picture('chart.png', width=Inches(5.5))

doc.save('report.docx')
```

### 4. Mail Merge for Bulk Documents

```python
from docx import Document
import csv

doc = Document("letter_template.docx")

with open("recipients.csv") as f:
    recipients = list(csv.DictReader(f))

for i, recipient in enumerate(recipients):
    doc_copy = Document("letter_template.docx")
    for para in doc_copy.paragraphs:
        for key, val in recipient.items():
            if f"{{{{{key}}}}}" in para.text:
                for run in para.runs:
                    run.text = run.text.replace(f"{{{{{key}}}}}", val)
    doc_copy.save(f"letter_{i+1:03d}.docx")
```

### 5. DOCX → PDF Conversion

```python
# Option A: LibreOffice headless (best fidelity)
# soffice --headless --convert-to pdf report.docx

# Option B: python-docx + reportlab (programmatic)
# Option C: pandoc + wkhtmltopdf (Markdown intermediary)
```

---

## Workflow: XLSX Spreadsheet Handling

### 1. Read & Analyse Existing Data

```python
import openpyxl
from openpyxl.utils import get_column_letter

wb = openpyxl.load_workbook("data.xlsx", data_only=True)
ws = wb.active

print(f"Sheet: {ws.title}, Rows: {ws.max_row}, Cols: {ws.max_column}")

# Read headers
headers = [cell.value for cell in ws[1]]
print(f"Columns: {headers}")

# Read all data as list of dicts
data = []
for row in ws.iter_rows(min_row=2, values_only=True):
    data.append(dict(zip(headers, row)))
```

### 2. Create from Scratch with Formatting

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import DataBarRule

wb = Workbook()
ws = wb.active
ws.title = "Q1 Budget"

# Header styling
header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
header_align = Alignment(horizontal="center", vertical="center")
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

headers = ["Category", "Budget", "Actual", "Variance", "Variance %"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border

# Data
data = [
    ["Marketing", 50000, 48500],
    ["R&D", 120000, 118000],
    ["Sales", 75000, 72000],
    ["Operations", 90000, 93500],
    ["Support", 45000, 44200],
]

for row_idx, (cat, budget, actual) in enumerate(data, 2):
    ws.cell(row=row_idx, column=1, value=cat).border = thin_border
    ws.cell(row=row_idx, column=2, value=budget).border = thin_border
    ws.cell(row=row_idx, column=3, value=actual).border = thin_border
    # Variance = Actual - Budget
    ws.cell(row=row_idx, column=4,
            value=actual - budget).border = thin_border
    ws.cell(row=row_idx, column=4).number_format = '#,##0'
    # Variance %
    if budget != 0:
        ws.cell(row=row_idx, column=5,
                value=(actual - budget) / budget).border = thin_border
        ws.cell(row=row_idx, column=5).number_format = '0.0%'

# Auto-width columns
for col in range(1, len(headers) + 1):
    ws.column_dimensions[get_column_letter(col)].width = 16

# Totals row
total_row = len(data) + 2
ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
for col in [2, 3, 4]:
    col_letter = get_column_letter(col)
    ws.cell(row=total_row, column=col,
            value=f"=SUM({col_letter}2:{col_letter}{total_row-1})")
    ws.cell(row=total_row, column=col).font = Font(bold=True)

# Bar chart
chart = BarChart()
chart.title = "Budget vs Actual"
chart.x_axis.title = "Category"
chart.y_axis.title = "Amount (€)"
chart.style = 10
cats = Reference(ws, min_col=1, min_row=2, max_row=total_row-1)
budget_data = Reference(ws, min_col=2, min_row=1, max_row=total_row-1)
actual_data = Reference(ws, min_col=3, min_row=1, max_row=total_row-1)
chart.add_data(budget_data, titles_from_data=True)
chart.add_data(actual_data, titles_from_data=True)
chart.set_categories(cats)
chart.width = 20
chart.height = 12
ws.add_chart(chart, f"A{total_row + 2}")

# Conditional formatting — data bars on Actual
rule = DataBarRule(start_type='min', end_type='max',
                   color='2F5496', showValue=True)
ws.conditional_formatting.add(f"C2:C{total_row-1}", rule)

# Freeze header row
ws.freeze_panes = 'A2'

wb.save("budget_report.xlsx")
```

### 3. Pivot Tables

```python
from openpyxl import load_workbook
from openpyxl.pivot import PivotTable

wb = load_workbook("sales_data.xlsx")
ws = wb.active

# Create pivot on a new sheet
pivot_sheet = wb.create_sheet("Pivot")

pivot = PivotTable()
pivot.add_field("Region")
pivot.add_field("Product")
pivot.add_field("Revenue")
pivot_sheet.add_pivot(pivot, "A3")
wb.save("sales_with_pivot.xlsx")
```

### 4. Common XLSX Pitfalls

| Pitfall | Fix |
|---------|-----|
| Formula results return `None` | Use `data_only=True` when loading, or compute values manually |
| Large file (>50MB) | Use `read_only=True` mode or chunk with `iter_rows()` |
| Merged cells lose data | Read from top-left cell; `ws.merged_cells.ranges` to detect |
| Date values appear as numbers | Apply date number format: `cell.number_format = 'YYYY-MM-DD'` |

---

## Workflow: PPTX Presentation Generation

### 1. Read & Analyse Existing Deck

```python
from pptx import Presentation

prs = Presentation("deck.pptx")
print(f"Slides: {len(prs.slides)}")
print(f"Slide width: {prs.slide_width}, height: {prs.slide_height}")

for i, slide in enumerate(prs.slides):
    print(f"\n--- Slide {i+1} ({slide.slide_layout.name}) ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(f"  [{shape.shape_type}] {shape.text[:100]}")
        if shape.has_table:
            print(f"  [TABLE] {shape.table.rows.__len__()} rows")
```

### 2. Build from Scratch

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)

# --- Title Slide ---
slide = prs.slides.add_slide(prs.slide_layouts[0])  # Title layout
slide.shapes.title.text = "Q1 2026 Business Review"
if slide.placeholders[1].has_text_frame:
    slide.placeholders[1].text = "Strategy & Operations\n28 May 2026"

# --- Content Slide ---
slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title + Content
slide.shapes.title.text = "Key Highlights"

tf = slide.placeholders[1].text_frame
tf.clear()
for highlight in [
    "Revenue up 12% YoY to €2.35M",
    "Operating margin improved to 21.7%",
    "3 new markets: Spain, Portugal, Italy",
    "Customer NPS score: 72 (up from 64)"
]:
    p = tf.add_paragraph()
    p.text = highlight
    p.level = 0
    p.font.size = Pt(18)
    p.space_after = Pt(8)

# --- Chart Slide ---
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank
slide.shapes.title.text = "Revenue Trend"

chart_data = CategoryChartData()
chart_data.categories = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
chart_data.add_series('Revenue (€K)', [680, 710, 750, 770, 790, 810])

chart_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE_MARKERS, Inches(1), Inches(1.5),
    Inches(11), Inches(5.5), chart_data
)
chart = chart_frame.chart
chart.has_legend = True
chart.has_title = False

# --- Image Slide ---
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Market Expansion Map"
slide.shapes.add_picture("map.png", Inches(2), Inches(1.5),
                         Inches(9), Inches(5))

# --- Speaker Notes ---
for slide in prs.slides:
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = (
        f"Speaker notes for: {slide.shapes.title.text}"
    )

prs.save("quarterly_review.pptx")
```

### 3. Template-Driven Slides

```python
from pptx import Presentation
import json

prs = Presentation("template.pptx")
with open("slide_content.json") as f:
    content = json.load(f)

for slide_data in content["slides"]:
    slide = prs.slides.add_slide(
        prs.slide_layouts[slide_data["layout_index"]]
    )
    slide.shapes.title.text = slide_data["title"]
    if "body" in slide_data:
        slide.placeholders[1].text = slide_data["body"]

prs.save("generated_deck.pptx")
```

### 4. PPTX Common Issues

| Issue | Fix |
|-------|-----|
| Layout index not found | List available: `[ly.name for ly in prs.slide_layouts]` |
| Placeholder missing | Check `slide.placeholders`; not all layouts have placeholder[1] |
| Images too large | Resize with PIL first, or use `Inches()` to set exact dimensions |
| Font not available on system | Use common fonts (Calibri, Arial) or embed fonts |

---

## Workflow: Format Conversion

### The Conversion Matrix

See `references/conversion-matrix.md` for the full cross-reference. Quick
reference for the most common paths:

| From | To | Tool | Quality |
|------|----|------|---------|
| DOCX | PDF | LibreOffice headless | ⭐⭐⭐⭐⭐ Best |
| DOCX | Markdown | `pandoc -i input.docx -o output.md` | ⭐⭐⭐⭐ Good |
| Markdown | DOCX | `pandoc -i input.md -o output.docx` | ⭐⭐⭐⭐ Good |
| Markdown | PDF | `pandoc --pdf-engine=xelatex` | ⭐⭐⭐⭐⭐ Best |
| PDF | DOCX | `pdf2docx` library or LibreOffice | ⭐⭐⭐ Moderate |
| PDF | Text | `pdfplumber` or `pandoc` | ⭐⭐⭐⭐ Good |
| XLSX | CSV | `pandas.read_excel().to_csv()` | ⭐⭐⭐⭐⭐ Lossless |
| XLSX | PDF | LibreOffice headless | ⭐⭐⭐⭐ Good |
| PPTX | PDF | LibreOffice headless | ⭐⭐⭐⭐ Good |
| PPTX | Images | `pptx → PDF → pdf2image` | ⭐⭐⭐ Moderate |
| HTML | DOCX | `pandoc -i input.html -o output.docx` | ⭐⭐⭐ Moderate |

### Generic Pandoc Pattern

```bash
# Basic conversion
pandoc input.docx -o output.md

# With template and metadata
pandoc input.md \
  --template=corporate.latex \
  --metadata title="Q1 Report" \
  --metadata author="Jane Doe" \
  --pdf-engine=xelatex \
  -o output.pdf

# Convert with reference document for styling
pandoc input.md --reference-doc=styles.docx -o output.docx

# Batch conversion
for file in *.md; do
  pandoc "$file" -o "${file%.md}.docx"
done
```

### PDF → DOCX (Best Available)

```python
# Using pdf2docx (best fidelity for text-heavy PDFs)
from pdf2docx import Converter
cv = Converter("input.pdf")
cv.convert("output.docx", start=0, end=None)
cv.close()

# Fallback: extract text, rebuild in python-docx
import pdfplumber
from docx import Document

doc = Document()
with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            doc.add_paragraph(text)
doc.save("output.docx")
```

### XLSX → CSV / JSON

```python
import pandas as pd

df = pd.read_excel("data.xlsx", sheet_name=None)  # All sheets
for sheet_name, sheet_df in df.items():
    sheet_df.to_csv(f"data_{sheet_name}.csv", index=False)
    sheet_df.to_json(f"data_{sheet_name}.json", orient="records")
```

---

## Platform Compatibility Notes

### Claude Code / Codex
- Full Python scripting capability — all libraries available.
- Use `subprocess` for pandoc and LibreOffice calls.
- Recommend `pip install` for missing packages.

### Cursor
- Works identically; execute scripts via integrated terminal.
- Use the `doc_tools_check.py` script as a pre-commit or task runner.

### Gemini CLI
- Can execute Python but may have restricted subprocess access.
- Prefer pure-Python libraries (pypdf, pdfplumber, python-docx, openpyxl,
  python-pptx) over CLI tools when possible.
- Pandoc may not be available; fall back to Python-only conversion paths.

### OpenClaw
- Full tool access. Can install packages and run both Python scripts and
  external CLI tools.
- Recommended: run `doc_tools_check.py` on first invocation to set up the
  environment.

### GitHub Copilot
- Chat context; provide complete, self-contained Python snippets.
- Include dependency installation comments.
- Tip: reference `scripts/doc_tools_check.py` for the install list.

### Windsurf
- Full Python execution in IDE terminal; all libraries supported.
- Use `doc_tools_check.py` for environment validation.
- Store reusable template files in project workspace.

### OpenCode
- Execute scripts via terminal with full Python access.
- Prefer pure-Python libraries for portability.
- Run `doc_tools_check.py` to validate environment before any operation.

---

## Integration Pattern

A typical document-processing session follows this sequence:

```
1. User Request
   ↓
2. Trigger Detection (match phrases → activate skill)
   ↓
3. Tool Validation   →  scripts/doc_tools_check.py
   ↓
4. Document Assessment →  Inspect input file(s)
   ↓
5. Operation Execution →  Follow workflow above
   ↓
6. Output Validation →  Read back, verify integrity
   ↓
7. Deliver Output    →  Present result path + summary
```

---

## Reference Files

| File | Contents |
|------|----------|
| `references/pdf-processing-guide.md` | Deep dive: extraction, merging, splitting, rotation, watermarking, form filling, OCR |
| `references/office-formats-guide.md` | DOCX templates, XLSX formatting, PPTX layouts, style consistency |
| `references/conversion-matrix.md` | Full conversion pair matrix with tool recommendations and quality ratings |
| `scripts/doc_tools_check.py` | PEP 723 pre-flight validation of all required tooling |
| `evals/eval_cases.json` | 5 positive + 3 near-miss negative test cases |

---

## Troubleshooting Quick Reference

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `ModuleNotFoundError` | Missing Python package | Run `doc_tools_check.py`, install missing packages |
| `pandoc: command not found` | pandoc not installed | `brew install pandoc` (macOS) or `apt install pandoc` (Linux) |
| PDF text extraction empty | Scanned/image PDF | Use OCR path: pdf2image + pytesseract |
| DOCX styles look wrong | Template mismatch | Use `--reference-doc` with pandoc or LibreOffice conversion |
| XLSX formula error `#REF!` | Sheet/cell references broken | Check sheet names and cell ranges after row insertion |
| PPTX layout index changes | Template differs from code assumption | List layouts dynamically with `[ly.name for ly in prs.slide_layouts]` |
| File size ballooning | Embedded high-res images | Resize images before embedding: `img.thumbnail((1920, 1080))` |
| Character encoding issues | Non-UTF-8 content | Specify encoding: `encoding='utf-8'` in all file operations |
