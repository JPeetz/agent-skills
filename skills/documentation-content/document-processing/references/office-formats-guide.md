# Office Formats Guide

Comprehensive reference for creating and manipulating DOCX, XLSX, and PPTX
files using Python libraries. Part of the document-processing agent skill.

---

## Table of Contents

1. [DOCX: Word Documents](#1-docx-word-documents)
2. [XLSX: Excel Spreadsheets](#2-xlsx-excel-spreadsheets)
3. [PPTX: PowerPoint Presentations](#3-pptx-powerpoint-presentations)
4. [Cross-Format Style Consistency](#4-cross-format-style-consistency)
5. [Performance & Best Practices](#5-performance--best-practices)

---

## 1. DOCX: Word Documents

### Library: python-docx

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
```

### Document Structure

```
Document
├── Sections
│   ├── Header
│   ├── Body
│   │   ├── Paragraphs
│   │   │   └── Runs
│   │   └── Tables
│   │       ├── Rows
│   │       │   └── Cells
│   │       │       └── Paragraphs
│   │       └── Columns
│   └── Footer
└── Styles
    ├── Paragraph styles
    ├── Character styles
    └── Table styles
```

### Template Patterns

#### Pattern 1: Placeholder Replacement

The most common and reliable approach. Use `{{PLACEHOLDER}}` syntax in
templates and replace before saving.

```python
from docx import Document
import re

def fill_template(template_path: str, output_path: str,
                  data: dict[str, str]) -> Document:
    """Replace {{KEY}} placeholders throughout a DOCX template."""
    doc = Document(template_path)

    def replace_in_runs(paragraphs):
        for para in paragraphs:
            for run in para.runs:
                for key, value in data.items():
                    placeholder = f"{{{{{key}}}}}"
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, value)

    # Body paragraphs
    replace_in_runs(doc.paragraphs)

    # Table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_in_runs(cell.paragraphs)

    # Headers and footers
    for section in doc.sections:
        replace_in_runs(section.header.paragraphs)
        replace_in_runs(section.footer.paragraphs)

    doc.save(output_path)
    return doc
```

**Important caveat:** python-docx can split a placeholder across multiple
runs. If `{{NAME}}` becomes `"{{NAM"` in one run and `"E}}"` in another,
direct replacement fails. Use this more robust approach:

```python
def fill_template_robust(template_path: str, output_path: str,
                         data: dict[str, str]):
    """Robust placeholder replacement handling split runs."""
    doc = Document(template_path)

    def replace_in_paragraph(para):
        # Concatenate all runs, replace, then rewrite
        full_text = "".join(run.text for run in para.runs)
        for key, value in data.items():
            full_text = full_text.replace(f"{{{{{key}}}}}", value)

        if full_text == "".join(run.text for run in para.runs):
            return  # No changes

        # Rewrite: clear all runs, set text on the first run
        for i, run in enumerate(para.runs):
            if i == 0:
                run.text = full_text
            else:
                run.text = ""

    for para in doc.paragraphs:
        replace_in_paragraph(para)

    doc.save(output_path)
```

#### Pattern 2: Table as Data Region

For tabular data in templates, use a marker row pattern:

```python
def fill_table_template(doc: Document, table_index: int,
                        headers: list[str], rows: list[list[str]]):
    """Fill a template table with headers and data rows."""
    table = doc.tables[table_index]

    # Assume first row is a header template row
    header_row = table.rows[0]
    for i, header in enumerate(headers):
        if i < len(header_row.cells):
            header_row.cells[i].text = header

    # Add data rows (copying style from header row)
    for row_data in rows:
        row = table.add_row()
        for i, cell_text in enumerate(row_data):
            if i < len(row.cells):
                row.cells[i].text = str(cell_text)
                # Copy formatting from header row
                _copy_paragraph_format(
                    header_row.cells[i].paragraphs[0],
                    row.cells[i].paragraphs[0]
                )
```

#### Pattern 3: Conditional Sections

Insert or remove entire paragraphs/tables based on data:

```python
def insert_conditional_content(doc: Document, marker: str,
                               content_func, data: dict):
    """Insert content at a {{MARKER}} paragraph, removing the marker."""
    for i, para in enumerate(doc.paragraphs):
        if marker in para.text:
            # Remove marker paragraph
            p = para._element
            p.getparent().remove(p)

            # Insert generated content before the element's old position
            content_func(doc, data)
            break
```

### Styles & Formatting

#### Defining Styles Programmatically

```python
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Modify built-in style
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

# Create a custom paragraph style
custom_style = doc.styles.add_style('CustomQuote', 1)  # 1 = paragraph
custom_style.font.name = 'Georgia'
custom_style.font.size = Pt(12)
custom_style.font.italic = True
custom_style.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
custom_style.paragraph_format.left_indent = Cm(1.5)
custom_style.paragraph_format.space_before = Pt(12)
custom_style.paragraph_format.space_after = Pt(12)

# Apply custom style
doc.add_paragraph('This is wisdom.', style='CustomQuote')
```

#### Table Styling

```python
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

def style_table(table, header_rows=1):
    """Apply professional table styling."""
    # Set table style
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row formatting
    for cell in table.rows[0].cells:
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # Header background
        shading = parse_xml(
            f'<w:shd {nsdecls("w")} w:fill="2F5496"/>'
        )
        cell._tc.get_or_add_tcPr().append(shading)

    # Data rows
    for row in table.rows[1:]:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(10)

def set_column_widths(table, widths_cm: list[float]):
    """Set exact column widths."""
    for row in table.rows:
        for i, width in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(width)
```

#### Adding Images with Positioning

```python
from docx.shared import Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_image_centered(doc, image_path: str, width_inches: float = 5.5,
                       caption: str = None):
    """Add a centered image with optional caption."""
    # Empty paragraph for spacing
    doc.add_paragraph()

    # Image paragraph — centered
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    run.add_picture(image_path, width=Inches(width_inches))

    # Caption
    if caption:
        cap_para = doc.add_paragraph()
        cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_run = cap_para.add_run(caption)
        cap_run.font.size = Pt(9)
        cap_run.font.italic = True
        cap_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
```

### Sections & Page Setup

```python
from docx.shared import Cm, Inches
from docx.enum.section import WD_ORIENT

# Default section (applies to first section)
section = doc.sections[0]
section.page_width = Cm(21.0)   # A4
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# Add a landscape section in the middle
doc.add_section()
landscape_section = doc.sections[-1]
landscape_section.orientation = WD_ORIENT.LANDSCAPE
landscape_section.page_width = Cm(29.7)
landscape_section.page_height = Cm(21.0)

# Back to portrait
doc.add_section()
portrait_section = doc.sections[-1]
portrait_section.orientation = WD_ORIENT.PORTRAIT
```

### Headers & Footers

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

section = doc.sections[0]

# Header with left-aligned text and right-aligned page number
header = section.header
header.is_linked_to_previous = False

# Left text
left_para = header.paragraphs[0]
left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
left_para.add_run("Q1 2026 Report").bold = True

# Right-aligned page number (use tab stop)
left_para.add_run("\t\t")
left_para.add_run("Confidential").italic = True

# Footer with centered page number
footer = section.footer
footer.is_linked_to_previous = False

# Add page number field
footer_para = footer.paragraphs[0]
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Page number field code
from docx.oxml.ns import qn
run = footer_para.add_run()
fld_char_begin = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
run._r.append(fld_char_begin)

run2 = footer_para.add_run("Page ")
run3 = footer_para.add_run()
instr_text = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
run3._r.append(instr_text)

run4 = footer_para.add_run()
fld_char_end = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
run4._r.append(fld_char_end)
```

### Mail Merge

```python
import csv
from docx import Document

def mail_merge(template_path: str, recipients_csv: str,
               output_pattern: str = "letter_{:03d}.docx"):
    """Perform mail merge: one document per recipient."""
    with open(recipients_csv, newline='', encoding='utf-8') as f:
        recipients = list(csv.DictReader(f))

    for i, recipient in enumerate(recipients):
        doc = Document(template_path)

        # Replace in all paragraphs
        for para in doc.paragraphs:
            full_text = "".join(r.text for r in para.runs)
            original = full_text
            for key, val in recipient.items():
                full_text = full_text.replace(f"{{{{{key}}}}}", val)

            if full_text != original:
                for j, run in enumerate(para.runs):
                    run.text = full_text if j == 0 else ""

        output_path = output_pattern.format(i)
        doc.save(output_path)
        print(f"Generated: {output_path}")
```

### DOCX → PDF (Best Methods)

```bash
# LibreOffice headless — best fidelity
soffice --headless --convert-to pdf report.docx --outdir output/

# Pandoc with reference doc for styling
pandoc report.docx -o report.pdf --pdf-engine=xelatex

# Using python-docx to read + reportlab to write PDF (complex, custom)
```

---

## 2. XLSX: Excel Spreadsheets

### Library: openpyxl

```python
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              NamedStyle, numbers)
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import (DataBarRule, ColorScaleRule,
                                       IconSetRule, FormulaRule)
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.pivot import PivotTable
```

### Workbook Structure

```
Workbook
└── Worksheets
    ├── Cells (value, formula, style)
    ├── Merged cells
    ├── Charts
    ├── Tables
    ├── Pivot tables
    ├── Conditional formatting
    ├── Data validation
    ├── Filters / AutoFilter
    ├── Freeze panes
    ├── Print settings
    └── Named ranges
```

### Template Patterns

#### Pattern 1: Header → Data → Totals → Chart

The most common business report pattern.

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

def create_business_report(output_path: str, title: str,
                           headers: list[str], data: list[list],
                           chart_cols: list[int] = None):
    """Create a formatted business report with chart."""
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]  # Sheet name max 31 chars

    # ── Styling ──
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496",
                              fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center",
                             wrap_text=True)
    data_font = Font(name="Calibri", size=10)
    total_font = Font(name="Calibri", size=11, bold=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # ── Title Row ──
    ws.merge_cells(start_row=1, start_column=1,
                   end_row=1, end_column=len(headers))
    title_cell = ws.cell(row=1, column=1, value=title)
    title_cell.font = Font(name="Calibri", size=14, bold=True,
                           color="2F5496")
    title_cell.alignment = Alignment(horizontal="center")

    # ── Headers ──
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # ── Data ──
    for row_idx, row_data in enumerate(data, 4):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = data_font
            cell.border = thin_border
            if isinstance(value, (int, float)):
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal="right")

    # ── Totals Row ──
    data_end = 3 + len(data)
    total_row = data_end + 1
    ws.cell(row=total_row, column=1, value="TOTAL").font = total_font
    ws.cell(row=total_row, column=1).border = thin_border

    if chart_cols is None:
        chart_cols = list(range(2, len(headers) + 1))

    for col in chart_cols:
        col_letter = get_column_letter(col)
        formula = f"=SUM({col_letter}4:{col_letter}{data_end})"
        cell = ws.cell(row=total_row, column=col, value=formula)
        cell.font = total_font
        cell.border = thin_border
        cell.number_format = '#,##0.00'

    # ── Chart ──
    if len(data) > 0:
        chart = BarChart()
        chart.title = title
        chart.style = 10
        chart.width = 22
        chart.height = 14

        chart_data = Reference(ws, min_col=chart_cols[0],
                               min_row=3, max_row=data_end,
                               max_col=chart_cols[-1])
        cats = Reference(ws, min_col=1, min_row=4, max_row=data_end)
        chart.add_data(chart_data, titles_from_data=True)
        chart.set_categories(cats)

        ws.add_chart(chart, f"A{total_row + 3}")

    # ── Column widths ──
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    # ── Freeze panes ──
    ws.freeze_panes = "A4"

    # ── Print settings ──
    ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True)
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    wb.save(output_path)
```

#### Pattern 2: Multiple Sheets with Summary

```python
def create_multi_sheet_report(output_path: str,
                              sheets_data: dict[str, list[list]]):
    """Create workbook with multiple data sheets and a summary."""
    wb = Workbook()

    # Remove default sheet
    wb.remove(wb.active)

    for sheet_name, data in sheets_data.items():
        ws = wb.create_sheet(title=sheet_name[:31])

        for row_idx, row in enumerate(data, 1):
            for col_idx, value in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)

    # Summary sheet with references
    summary = wb.create_sheet(title="Summary", index=0)
    summary.cell(row=1, column=1, value="Sheet").font = Font(bold=True)
    summary.cell(row=1, column=2, value="Row Count").font = Font(bold=True)

    for i, name in enumerate(sheets_data.keys(), 2):
        safe_name = name[:31]
        summary.cell(row=i, column=1, value=name)
        summary.cell(row=i, column=2,
                     value=f"=COUNTA('{safe_name}'!A:A)")

    wb.save(output_path)
```

### Advanced Formatting

#### Conditional Formatting

```python
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule

# Data bars (in-cell visualization)
rule = DataBarRule(
    start_type='min', end_type='max',
    color='2F5496', showValue=True
)
ws.conditional_formatting.add('C4:C50', rule)

# Color scale (3-color gradient)
ws.conditional_formatting.add('D4:D50', ColorScaleRule(
    start_type='min', start_color='FF4444',   # Red = low
    mid_type='percentile', mid_value=50, mid_color='FFFF44',  # Yellow = mid
    end_type='max', end_color='44FF44'          # Green = high
))

# Highlight negative values
from openpyxl.formatting.rule import FormulaRule
ws.conditional_formatting.add('E4:E50', FormulaRule(
    formula=['$E4<0'],
    font=Font(color='FF0000', bold=True),
    fill=PatternFill(start_color='FFCCCC', end_color='FFCCCC',
                     fill_type='solid')
))
```

#### Data Validation (Dropdown Lists)

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(
    type="list",
    formula1='"Option A,Option B,Option C"',
    allow_blank=True,
    showDropDown=False
)
dv.error = "Please select from the dropdown."
dv.errorTitle = "Invalid Selection"
ws.add_data_validation(dv)
dv.add("B4:B100")
```

#### Number Formatting Reference

```python
formats = {
    'integer': '#,##0',
    'decimal_1': '#,##0.0',
    'decimal_2': '#,##0.00',
    'currency': '€#,##0.00',
    'currency_neg': '€#,##0.00;[Red]-€#,##0.00',
    'percentage': '0.0%',
    'percentage_2': '0.00%',
    'date_short': 'DD/MM/YYYY',
    'date_long': 'DD MMM YYYY',
    'datetime': 'DD/MM/YYYY HH:MM',
    'text': '@',
    'fraction': '# ?/?',
    'scientific': '0.00E+00',
    'accounting': '_("€"* #,##0.00_);_("€"* (#,##0.00);_("€"* "-"??_);_(@_)',
}
```

### Charts

```python
from openpyxl.chart import (BarChart, LineChart, PieChart, AreaChart,
                             ScatterChart, Reference, Series)
from openpyxl.chart.label import DataLabelList

# ── Bar Chart ──
bar = BarChart()
bar.type = "col"            # "col" = vertical, "bar" = horizontal
bar.grouping = "clustered"  # "clustered", "stacked", "percentStacked"
bar.title = "Revenue by Quarter"
bar.y_axis.title = "Revenue (€)"
bar.x_axis.title = "Quarter"
bar.style = 10

# ── Line Chart ──
line = LineChart()
line.title = "Monthly Trend"
line.y_axis.title = "Units Sold"
line.y_axis.scaling.min = 0

# ── Pie Chart with Labels ──
pie = PieChart()
pie.title = "Market Share"
data = Reference(ws, min_col=2, min_row=1, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
pie.add_data(data, titles_from_data=True)
pie.set_categories(cats)
pie.dataLabels = DataLabelList()
pie.dataLabels.showPercent = True
pie.dataLabels.showCatName = True

# ── Combo Chart (Bar + Line) ──
bar = BarChart()
line = LineChart()

data1 = Reference(ws, min_col=2, min_row=1, max_row=6)
data2 = Reference(ws, min_col=3, min_row=1, max_row=6)
cats = Reference(ws, min_col=1, min_row=2, max_row=6)

bar.add_data(data1, titles_from_data=True)
bar.set_categories(cats)
line.add_data(data2, titles_from_data=True)
line.set_categories(cats)
line.y_axis.axId = 200  # Secondary axis

bar.y_axis.crosses = "min"
bar += line

ws.add_chart(bar, "A10")
```

### Pivot Tables

```python
from openpyxl import load_workbook
from openpyxl.pivot import PivotTable

wb = load_workbook("sales.xlsx")
ws = wb["RawData"]

# Data must be in a contiguous range with headers
pivot_sheet = wb.create_sheet("Pivot")

pivot = PivotTable()
pivot.add_column("Region")
pivot.add_column("Product")
pivot.add_data("Revenue")
pivot.add_data("Units", "Units Sold")

pivot_sheet.add_pivot(pivot, "A3")
wb.save("sales_with_pivot.xlsx")
```

### Reading Large Files

```python
# Memory-efficient reading
wb = load_workbook("huge_data.xlsx", read_only=True)
ws = wb.active

# Stream row-by-row
for row in ws.iter_rows(min_row=2, values_only=True):
    # Process each row without loading entire sheet
    process_row(row)

wb.close()

# Reading with data_only (ignore formulas, get cached values)
wb = load_workbook("with_formulas.xlsx", data_only=True)
```

---

## 3. PPTX: PowerPoint Presentations

### Library: python-pptx

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTOSIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData, ChartData
```

### Slide Layouts

```python
prs = Presentation()

# Inspect available layouts
for i, layout in enumerate(prs.slide_layouts):
    print(f"{i}: {layout.name}")

# Common layout indices (0-based, varies by template):
# 0 — Title Slide
# 1 — Title and Content
# 2 — Section Header
# 3 — Two Content
# 4 — Comparison
# 5 — Title Only
# 6 — Blank
# 7 — Content with Caption
# 8 — Picture with Caption
```

### Template Patterns

#### Pattern 1: Title + Bullet Slides

The most common presentation pattern.

```python
def create_bullet_slide(prs: Presentation, title: str,
                        bullets: list[str],
                        layout_index: int = 1):
    """Create a title + bullet-point slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[layout_index])
    slide.shapes.title.text = title

    # Body text frame
    body = slide.placeholders[1].text_frame
    body.clear()

    for i, bullet in enumerate(bullets):
        p = body.paragraphs[0] if i == 0 else body.add_paragraph()
        p.text = bullet
        p.level = 0
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        p.space_after = Pt(8)

    return slide
```

#### Pattern 2: Image + Caption Slide

```python
def create_image_slide(prs: Presentation, title: str,
                       image_path: str, caption: str = "",
                       layout_index: int = 5):
    """Create a slide with a large image and optional caption."""
    slide = prs.slides.add_slide(prs.slide_layouts[layout_index])
    slide.shapes.title.text = title

    # Image centered in available space
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    img_left = Inches(1.5)
    img_top = Inches(1.5)
    img_width = slide_width - Inches(3)
    img_height = slide_height - Inches(3.5)

    slide.shapes.add_picture(image_path, img_left, img_top,
                             img_width, img_height)

    if caption:
        txBox = slide.shapes.add_textbox(
            Inches(1.5), slide_height - Inches(1),
            slide_width - Inches(3), Inches(0.5)
        )
        tf = txBox.text_frame
        tf.text = caption
        tf.paragraphs[0].font.size = Pt(10)
        tf.paragraphs[0].font.italic = True
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide
```

#### Pattern 3: Full Presentation from Markdown

```python
import re
from pptx import Presentation
from pptx.util import Pt

def markdown_to_pptx(md_path: str, pptx_path: str):
    """Convert a markdown file to a PPTX presentation.
    
    Markdown conventions:
    - `# title` → Slide title (new slide)
    - `## subtitle` → Slide subtitle
    - `- bullet` → Bullet point
    - `---` → New section/divider
    - `![alt](path)` → Image on its own slide
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    with open(md_path, 'r') as f:
        content = f.read()

    # Split into slides by headings
    sections = re.split(r'\n(?=# )', content)

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        title_line = lines[0].lstrip('# ').strip()

        # Title slide for first section, content slides for rest
        layout_idx = 0 if len(prs.slides) == 0 else 1
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        slide.shapes.title.text = title_line

        # Process body content
        if len(lines) > 1 and layout_idx == 1:
            body = slide.placeholders[1].text_frame
            body.clear()
            first = True
            for line in lines[1:]:
                if line.strip().startswith('- '):
                    text = line.strip()[2:]
                    p = body.paragraphs[0] if first else body.add_paragraph()
                    p.text = text
                    p.font.size = Pt(20)
                    first = False
                elif line.strip().startswith('## '):
                    subtitle = line.strip()[3:]
                    if slide.placeholders[1].has_text_frame:
                        slide.placeholders[1].text = subtitle

    prs.save(pptx_path)
    return prs
```

### Charts in PowerPoint

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

def add_chart_slide(prs: Presentation, title: str, chart_type,
                    categories: list, series_data: dict[str, list[float]]):
    """Add a slide with an embedded chart."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank layout
    slide.shapes.title.text = title

    chart_data = CategoryChartData()
    chart_data.categories = categories
    for name, values in series_data.items():
        chart_data.add_series(name, values)

    chart_frame = slide.shapes.add_chart(
        chart_type,
        Inches(1), Inches(1.5),
        Inches(11), Inches(5.5),
        chart_data
    )

    # Style the chart
    chart = chart_frame.chart
    chart.has_legend = True
    chart.has_title = False     # We use the slide title instead

    # Format axes
    if hasattr(chart, 'value_axis'):
        chart.value_axis.has_major_gridlines = True
        chart.value_axis.major_gridlines.format.line.color.rgb = (
            RGBColor(0xDD, 0xDD, 0xDD)
        )

    return slide

# Usage
add_chart_slide(prs, "Quarterly Revenue", XL_CHART_TYPE.COLUMN_CLUSTERED,
    categories=["Q1", "Q2", "Q3", "Q4"],
    series_data={
        "2025": [210, 230, 250, 270],
        "2026": [235, 255, 275, 295],
    }
)
```

### Tables in PowerPoint

```python
def add_table_slide(prs: Presentation, title: str,
                    headers: list[str], rows: list[list],
                    col_widths: list = None):
    """Add a slide with a formatted table."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title

    num_rows = len(rows) + 1  # +1 for header
    num_cols = len(headers)

    table_shape = slide.shapes.add_table(
        num_rows, num_cols,
        Inches(1), Inches(1.5),
        Inches(11), Inches(5)
    )
    table = table_shape.table

    # Apply column widths
    if col_widths:
        for i, width in enumerate(col_widths):
            table.columns[i].width = Inches(width)

    # Header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        for para in cell.text_frame.paragraphs:
            para.font.bold = True
            para.font.size = Pt(14)
            para.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            para.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2F, 0x54, 0x96)

    # Data rows
    for r, row_data in enumerate(rows):
        for c, value in enumerate(row_data):
            cell = table.cell(r + 1, c)
            cell.text = str(value) if value is not None else ""
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(12)
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xF2, 0xF2, 0xF2)

    return slide
```

### Shapes & SmartArt Replacements

PPTX doesn't have a native SmartArt API. Use shapes as alternatives:

```python
from pptx.enum.shapes import MSO_SHAPE

# Add a shape
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1), Inches(2), Inches(4), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x2F, 0x54, 0x96)
shape.line.fill.background()

# Add text to shape
tf = shape.text_frame
tf.word_wrap = True
tf.auto_size = MSO_AUTOSIZE.SHAPE_TO_FIT_TEXT
p = tf.paragraphs[0]
p.text = "Key Result"
p.font.size = Pt(16)
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.alignment = PP_ALIGN.CENTER
```

### Speaker Notes

```python
def add_speaker_notes(prs: Presentation, notes_map: dict[int, str]):
    """Add speaker notes to slides by index."""
    for slide_idx, notes_text in notes_map.items():
        if slide_idx < len(prs.slides):
            slide = prs.slides[slide_idx]
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = notes_text

# Alternatively, add notes when building slides:
slide = prs.slides[0]
notes = slide.notes_slide
notes.notes_text_frame.text = "Welcome everyone. Today we'll review Q1 results."
```

---

## 4. Cross-Format Style Consistency

### Color Palette

Define a consistent palette across all document types:

```python
# Corporate palette
PALETTE = {
    'primary':    RGBColor(0x2F, 0x54, 0x96),  # Dark blue
    'secondary':  RGBColor(0x44, 0x72, 0xC4),  # Medium blue
    'accent':     RGBColor(0xFF, 0xC0, 0x00),  # Amber/gold
    'text':       RGBColor(0x33, 0x33, 0x33),  # Dark gray
    'text_light': RGBColor(0x66, 0x66, 0x66),  # Medium gray
    'background': RGBColor(0xF5, 0xF5, 0xF5),  # Light gray
    'white':      RGBColor(0xFF, 0xFF, 0xFF),
    'success':    RGBColor(0x2E, 0x7D, 0x32),  # Green
    'warning':    RGBColor(0xED, 0x6C, 0x02),  # Orange
    'error':      RGBColor(0xD3, 0x2F, 0x2F),  # Red
}

# Font stack per platform:
FONTS = {
    'heading': 'Calibri',
    'body': 'Calibri',
    'mono': 'Consolas',
}
```

### Style Mapping Between Formats

| Element | DOCX (python-docx) | XLSX (openpyxl) | PPTX (python-pptx) |
|---------|--------------------|-----------------|--------------------|
| Title/H1 | Heading 1 style, Pt(16) | Merged cell, Font(size=14, bold=True) | `slide.shapes.title`, Pt(36) |
| Subtitle/H2 | Heading 2 style, Pt(13) | Row below title, Font(size=12, bold=True) | Subtitle placeholder, Pt(24) |
| Body text | Normal style, Pt(11) | Data cells, Font(size=10) | Body text frame, Pt(18-24) |
| Bullet | List Bullet style | Bullet char in cell `"• " + text` | Bullet paragraphs (level 0-4) |
| Table | Table object | Worksheet range | Table shape |
| Chart | Inline picture | Chart object | Chart shape |

---

## 5. Performance & Best Practices

### Memory Management

```python
# DOCX: Always close/save. Large docs can use streaming.
# python-docx has no streaming read; for huge files, consider lxml directly.

# XLSX: Use read_only and write_only modes for large files.
wb = load_workbook("huge.xlsx", read_only=True)
wb.close()

# Write-only mode
wb = Workbook(write_only=True)
ws = wb.create_sheet()
ws.append(["Header1", "Header2"])
ws.append(["Value1", "Value2"])
wb.save("output.xlsx")
```

### Batch Operations

```python
# Generate multiple DOCX from CSV data
import csv
from docx import Document

def batch_generate_docx(template_path: str, csv_path: str,
                        output_dir: str, filename_col: str = "Filename"):
    """Generate one DOCX per CSV row."""
    os.makedirs(output_dir, exist_ok=True)
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            doc = Document(template_path)
            # ... fill template ...
            doc.save(os.path.join(output_dir, row[filename_col]))
```

### Style Inheritance

```python
# When building documents programmatically, reuse style objects
# Don't create new Font/Style objects for every cell

# BAD
for row in data:
    for val in row:
        cell.font = Font(name="Calibri", size=10)  # New object each time

# GOOD
data_font = Font(name="Calibri", size=10)
for row in data:
    for val in row:
        cell.font = data_font  # Reuse same object
```

### Common Pitfalls

| Pitfall | Explanation | Fix |
|---------|------------|-----|
| Placeholder split across runs | python-docx may split `{{NAME}}` into multiple runs | Use robust replacement method (concatenate, replace, rewrite) |
| XLSX formula returns None | `data_only=True` reads cached values, not computed results | Open in Excel first to compute, or use `openpyxl`'s formula engine |
| PPTX layout mismatch | Layout indices vary between template files | Inspect layouts dynamically: `[l.name for l in prs.slide_layouts]` |
| Missing chart data | Chart References must point to populated cells | Ensure data exists before creating chart |
| Image size in PPTX | Large images bloat file size | Resize to target dimensions before embedding |
| Corrupted DOCX after save | Multiple saves or manual XML manipulation | Clone from original, modify once, save once |
| XLSX date stored as number | Dates are Excel serial numbers | Set number_format='YYYY-MM-DD' or convert with `from_excel()` |