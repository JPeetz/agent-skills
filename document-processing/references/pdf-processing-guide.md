# PDF Processing Guide

Comprehensive reference for PDF manipulation techniques used by the
document-processing agent skill.

---

## Table of Contents

1. [Reading & Inspecting PDFs](#1-reading--inspecting-pdfs)
2. [Text Extraction](#2-text-extraction)
3. [Table Extraction](#3-table-extraction)
4. [Merging PDFs](#4-merging-pdfs)
5. [Splitting PDFs](#5-splitting-pdfs)
6. [Rotation & Page Manipulation](#6-rotation--page-manipulation)
7. [Watermarking & Overlays](#7-watermarking--overlays)
8. [Form Filling](#8-form-filling)
9. [OCR (Optical Character Recognition)](#9-ocr-optical-character-recognition)
10. [Metadata & Annotations](#10-metadata--annotations)
11. [Image Extraction](#11-image-extraction)
12. [Encryption & Password Handling](#12-encryption--password-handling)
13. [Performance & Large Files](#13-performance--large-files)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Reading & Inspecting PDFs

### Basic Inspection

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")
print(f"Encrypted: {reader.is_encrypted}")
print(f"PDF Version: {reader.pdf_header}")

# Metadata
meta = reader.metadata
if meta:
    print(f"Title: {meta.title}")
    print(f"Author: {meta.author}")
    print(f"Subject: {meta.subject}")
    print(f"Creator: {meta.creator}")
    print(f"Producer: {meta.producer}")
    print(f"Created: {meta.creation_date}")
    print(f"Modified: {meta.modification_date}")
```

### Page-by-Page Inspection

```python
for i, page in enumerate(reader.pages):
    print(f"\nPage {i+1}:")
    print(f"  Size: {page.mediabox.width} x {page.mediabox.height}")
    print(f"  Rotation: {page.get('/Rotate', 0)}°")
    print(f"  Contents: {len(page['/Contents'])} objects")

    # Check for images
    if '/XObject' in page['/Resources']:
        xobjects = page['/Resources']['/XObject']
        images = [k for k, v in xobjects.items()
                  if v['/Subtype'] == '/Image']
        if images:
            print(f"  Images: {len(images)}")
```

### Detecting Scanned vs. Text PDFs

```python
def is_scanned_pdf(reader: PdfReader) -> bool:
    """Heuristic: check if first page has extractable text."""
    if len(reader.pages) == 0:
        return False
    text = reader.pages[0].extract_text()
    return not text or len(text.strip()) < 20
```

---

## 2. Text Extraction

### Simple Extraction (pypdf)

Best for simple, single-column PDFs with standard fonts.

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
all_text = []
for page in reader.pages:
    text = page.extract_text()
    if text:
        all_text.append(text)

full_text = "\n\n".join(all_text)
```

### Layout-Aware Extraction (pdfplumber)

Best for multi-column layouts, complex positioning, and precise text
coordinates. Use this as the default for text extraction.

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        # Full page text
        text = page.extract_text()

        # Text with layout info
        for char in page.chars:
            print(f"'{char['text']}' at "
                  f"x={char['x0']:.1f}, y={char['top']:.1f}, "
                  f"font={char['fontname']}, size={char['size']}")

        # Extract by bounding box
        cropped = page.within_bbox((0, 0, 300, 800))
        header_text = cropped.extract_text()
```

### Extraction Strategies

pdfplumber supports multiple strategies for text extraction:

```python
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Default strategy (best for most docs)
    text = page.extract_text()

    # Word-based extraction
    words = page.extract_words()

    # Preserve more whitespace
    text = page.extract_text(x_tolerance=3, y_tolerance=3)

    # Horizontal/vertical layout hints
    text = page.extract_text(keep_blank_chars=True)
```

### Handling Extraction Failures

```python
import pdfplumber

with pdfplumber.open("problematic.pdf") as pdf:
    for page in pdf.pages:
        try:
            text = page.extract_text()
        except Exception as e:
            print(f"Warning: failed on page {page.page_number}: {e}")
            # Fallback: try pypdf
            text = page.extract_text_simple()
        if text:
            print(text)
```

---

## 3. Table Extraction

pdfplumber provides the best table extraction in the Python ecosystem.

### Basic Table Extraction

```python
import pdfplumber

with pdfplumber.open("financial_report.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table_idx, table in enumerate(tables):
            print(f"--- Table {table_idx + 1} on Page {page.page_number} ---")
            for row in table:
                print(" | ".join(str(cell) if cell else "" for cell in row))
```

### Tuning Table Detection

```python
# Adjust table detection parameters
tables = page.extract_tables({
    "vertical_strategy": "lines",      # "lines", "lines_strict", "text"
    "horizontal_strategy": "lines",    # "lines", "lines_strict", "text"
    "intersection_x_tolerance": 3,     # Tolerance for line intersections
    "intersection_y_tolerance": 3,
    "snap_tolerance": 3,               # Snap nearby elements together
    "edge_min_length": 3,              # Min line length to consider
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
})

# Visual debugging
import pdfplumber
img = page.to_image(resolution=150)
img.reset().debug_tablefinder()
img.save("table_debug.png")
```

### Merging Split Rows

PDFs often have cells split across rows. A common heuristic:

```python
def merge_split_rows(table: list[list]) -> list[list]:
    """Merge rows where the first cell is empty (continuation row)."""
    merged = []
    for row in table:
        if merged and not row[0] and row[1:]:
            # Append to last row
            for i, cell in enumerate(row[1:], 1):
                if cell:
                    merged[-1][i] = (merged[-1][i] or "") + " " + cell
        else:
            merged.append(row)
    return merged
```

---

## 4. Merging PDFs

### Simple Merge

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for path in ["chapter1.pdf", "chapter2.pdf", "chapter3.pdf"]:
    writer.append(path)

writer.write("complete_book.pdf")

# Validate
merged = PdfReader("complete_book.pdf")
print(f"Merged PDF: {len(merged.pages)} pages")
```

### Merge with Page Selection

```python
writer = PdfWriter()

# Append first 3 pages from doc1
reader1 = PdfReader("doc1.pdf")
for page in reader1.pages[:3]:
    writer.add_page(page)

# Append pages 5-10 from doc2
reader2 = PdfReader("doc2.pdf")
for page in reader2.pages[4:10]:
    writer.add_page(page)

writer.write("selected_pages.pdf")
```

### Insert Pages at Specific Positions

```python
writer = PdfWriter(clone_from="base.pdf")

# Insert doc2 after page 2 (0-indexed)
reader2 = PdfReader("insert.pdf")
for i, page in enumerate(reader2.pages):
    writer.insert_page(page, index=2 + i)

writer.write("base_with_insert.pdf")
```

### Merge with Metadata Preservation

```python
writer = PdfWriter()
writer.append("doc1.pdf")
writer.append("doc2.pdf")

# Set merged document metadata
writer.add_metadata({
    '/Title': 'Combined Quarterly Reports',
    '/Author': 'Finance Department',
    '/Subject': 'Q1-Q4 2026 Financial Reports',
    '/Creator': 'document-processing skill v1.0.0',
})

writer.write("combined.pdf")
```

---

## 5. Splitting PDFs

### Split by Page Ranges

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("large_document.pdf")

def extract_pages(reader, start, end, output_path):
    """Extract pages [start, end] (0-indexed, inclusive)."""
    writer = PdfWriter()
    for page in reader.pages[start:end + 1]:
        writer.add_page(page)
    writer.write(output_path)
    print(f"Extracted pages {start+1}-{end+1} → {output_path}")

# Split into chapters
extract_pages(reader, 0, 14, "chapter_1.pdf")   # Pages 1-15
extract_pages(reader, 15, 29, "chapter_2.pdf")  # Pages 16-30
extract_pages(reader, 30, 44, "chapter_3.pdf")  # Pages 31-45
```

### Split Every N Pages

```python
def split_every_n(reader: PdfReader, n: int, prefix: str):
    """Split into chunks of n pages each."""
    for chunk_start in range(0, len(reader.pages), n):
        chunk_end = min(chunk_start + n, len(reader.pages))
        writer = PdfWriter()
        for page in reader.pages[chunk_start:chunk_end]:
            writer.add_page(page)
        writer.write(f"{prefix}_{chunk_start//n + 1:03d}.pdf")

split_every_n(reader, 5, "chunk")
```

### Split by Bookmark / Outline

```python
reader = PdfReader("book_with_outline.pdf")

def get_outline_structure(outline, level=0):
    """Recursively extract bookmark titles and page numbers."""
    items = []
    for item in outline:
        if isinstance(item, list):
            items.extend(get_outline_structure(item, level + 1))
        else:
            items.append({
                "title": item.title,
                "page": reader.get_destination_page_number(item),
                "level": level,
            })
    return items

structure = get_outline_structure(reader.outline)
for item in structure:
    print(f"{'  ' * item['level']}{item['title']} → page {item['page'] + 1}")
```

---

## 6. Rotation & Page Manipulation

### Rotate Pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.rotate(90)           # Clockwise 90°
    # page.rotate(-90)        # Counter-clockwise 90°
    # page.rotate(180)        # Upside down
    writer.add_page(page)

writer.write("rotated.pdf")
```

### Scale / Resize Pages

```python
from pypdf import PdfReader, PdfWriter, Transformation

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Scale to A4 (595.28 x 841.89 points) while preserving content
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)
    scale_x = 595.28 / w
    scale_y = 841.89 / h
    scale = min(scale_x, scale_y)

    op = Transformation().scale(scale, scale)
    page.add_transformation(op)
    page.mediabox.width = 595.28
    page.mediabox.height = 841.89
    writer.add_page(page)

writer.write("scaled.pdf")
```

### Crop Pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Crop to half-page (left side)
    page.mediabox.right = page.mediabox.right / 2
    writer.add_page(page)

writer.write("cropped.pdf")
```

---

## 7. Watermarking & Overlays

### Text Watermark

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

def create_text_watermark(text: str, opacity: float = 0.1) -> PdfReader:
    """Create a watermark PDF page with diagonal text."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(612, 792))  # Letter size

    c.saveState()
    c.setFillAlpha(opacity)
    c.setFont("Helvetica", 60)
    c.translate(306, 396)     # Center of page
    c.rotate(45)               # Diagonal
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()

    packet.seek(0)
    return PdfReader(packet)

# Apply watermark
reader = PdfReader("document.pdf")
watermark = create_text_watermark("CONFIDENTIAL", opacity=0.08)
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark.pages[0])
    writer.add_page(page)

writer.write("watermarked.pdf")
```

### Image Watermark (Logo Overlay)

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
logo = PdfReader("logo.pdf")    # Single-page PDF with transparent logo
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(logo.pages[0], over=True)  # over=True for top layer
    writer.add_page(page)

writer.write("with_logo.pdf")
```

### Page Number Stamping

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io

def create_page_number_page(page_num: int, total: int) -> PdfReader:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(612, 792))
    c.setFont("Helvetica", 10)
    c.drawCentredString(306, 20, f"Page {page_num} of {total}")
    c.save()
    packet.seek(0)
    return PdfReader(packet)

reader = PdfReader("document.pdf")
writer = PdfWriter()

for i, page in enumerate(reader.pages):
    pn_overlay = create_page_number_page(i + 1, len(reader.pages))
    page.merge_page(pn_overlay.pages[0])
    writer.add_page(page)

writer.write("numbered.pdf")
```

---

## 8. Form Filling

### Read Form Fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()

if fields is None:
    print("No form fields found. This may be a flat PDF or use XFA forms.")
else:
    for field_name, field_info in fields.items():
        print(f"Field: {field_name}")
        print(f"  Type:  {field_info.get('/FT', 'Unknown')}")
        print(f"  Value: {field_info.get('/V', '(empty)')}")
        print(f"  Flags: {field_info.get('/Ff', 0)}")
        if '/Opt' in field_info:
            print(f"  Options: {field_info['/Opt']}")
```

### Fill Form Fields

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("tax_form.pdf")
writer = PdfWriter()
writer.append(reader)

# Fill fields on specific pages
writer.update_page_form_field_values(writer.pages[0], {
    "Name": "Alice Brown",
    "TaxID": "IE1234567X",
    "TaxYear": "2025",
    "Amount": "45200.00",
    "Date": "2026-05-28",
}, auto_regenerate=False)

# Handle checkboxes and radio buttons
# Checkbox: '/V' → '/Yes' (checked) or '/Off' (unchecked)
writer.update_page_form_field_values(writer.pages[0], {
    "MarriedCheckbox": "/Yes",
    "SelfEmployedRadio": "/Yes",
})

# Flatten form fields (make them permanent, non-editable)
# writer.set_need_appearances_writer(True)
writer.write("tax_form_filled.pdf")
```

### Auto-Detect and Fill All Fields

```python
def auto_fill_form(input_path: str, output_path: str,
                   field_values: dict[str, str]) -> dict[str, str]:
    """Fill a PDF form and report which fields were matched."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)

    fields = reader.get_fields()
    if not fields:
        return {"error": "No form fields found"}

    matched = {}
    unmatched = {}

    for field_name in fields:
        page = writer.pages[0]  # Assume fields on first page; adjust as needed
        if field_name in field_values:
            writer.update_page_form_field_values(page, {
                field_name: field_values[field_name]
            })
            matched[field_name] = field_values[field_name]
        else:
            unmatched[field_name] = "not provided"

    writer.write(output_path)
    return {"matched": matched, "unmatched": unmatched}

result = auto_fill_form("form.pdf", "form_filled.pdf", {
    "Name": "Bob Smith",
    "Email": "bob@example.com",
})
print(f"Filled {len(result['matched'])} fields")
if result.get("unmatched"):
    print(f"Unfilled fields: {list(result['unmatched'].keys())}")
```

### XFA Forms (Limitation)

pypdf does **not** support XFA (XML Forms Architecture) forms. If
`reader.get_fields()` returns `None` and the PDF was created with Adobe
LiveCycle, the form likely uses XFA. Options:

1. Use Adobe Acrobat (proprietary) to fill.
2. Convert to AcroForm with an external tool.
3. Extract the XFA XML, modify it manually, repackage.

---

## 9. OCR (Optical Character Recognition)

### Full Pipeline for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
import io

def ocr_pdf(input_path: str, output_path: str, dpi: int = 300,
            language: str = "eng") -> str:
    """
    OCR a scanned PDF and produce a searchable PDF.
    Returns the extracted text as a string.
    """
    # Step 1: Convert PDF pages to images
    images = convert_from_path(input_path, dpi=dpi)

    # Step 2: OCR each page
    all_text = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang=language)
        all_text.append(f"--- Page {i+1} ---\n{text}")

    full_text = "\n\n".join(all_text)

    # Step 3: Optionally create searchable PDF
    # (Requires reportlab or pikepdf for proper searchable PDF creation)
    # This is a simplified approach; for production, use ocrmypdf

    with open(output_path.replace(".pdf", ".txt"), "w") as f:
        f.write(full_text)

    return full_text

text = ocr_pdf("scanned_document.pdf", "scanned_output.pdf")
```

### Using ocrmypdf (Recommended for Production)

```bash
# Install: pip install ocrmypdf
# Also requires: brew install tesseract tesseract-lang  (macOS)
#                apt install ocrmypdf tesseract-ocr     (Linux)

# Basic OCR
ocrmypdf scanned.pdf searchable.pdf

# With language and deskew
ocrmypdf --language eng+deu --deskew --clean scanned.pdf searchable.pdf

# Force OCR even if text exists
ocrmypdf --force-ocr scanned.pdf searchable.pdf

# Optimize output size
ocrmypdf --optimize 3 scanned.pdf searchable.pdf
```

### Extracting Text from Specific Regions

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("form.pdf", dpi=300)
page_img = images[0]

# Crop to a specific region (left, top, right, bottom in pixels)
# Typical form field: name at top-left
name_region = page_img.crop((100, 200, 600, 250))
name_text = pytesseract.image_to_string(name_region).strip()
print(f"Name field: {name_text}")

# Multiple regions
regions = {
    "Name": (100, 200, 600, 250),
    "Date": (100, 300, 600, 350),
    "Amount": (100, 400, 600, 450),
}
for field, bbox in regions.items():
    cropped = page_img.crop(bbox)
    value = pytesseract.image_to_string(cropped).strip()
    print(f"{field}: {value}")
```

---

## 10. Metadata & Annotations

### Read and Modify Metadata

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.append(reader)

writer.add_metadata({
    '/Title': 'Updated Report Title',
    '/Author': 'Jane Doe',
    '/Subject': 'Q1 2026 Financial Analysis',
    '/Keywords': 'finance, quarterly, 2026',
    '/Creator': 'document-processing skill',
})

writer.write("document_with_metadata.pdf")
```

### Add Text Annotations

```python
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText

reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.append(reader)

# Add a sticky-note annotation
annotation = FreeText(
    text="Reviewed by Legal — approved.",
    rect=(50, 700, 300, 750),
    font="Helvetica",
    font_size="12pt",
    font_color="000000",
    border_color="000000",
    background_color="ffff00",
)
writer.add_annotation(page_number=0, annotation=annotation)
writer.write("annotated.pdf")
```

### Add Hyperlinks

```python
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.append(reader)

# External URL link
link = Link(
    rect=(50, 750, 200, 770),
    url="https://example.com/reference",
)
writer.add_annotation(page_number=0, annotation=link)
writer.write("with_links.pdf")
```

---

## 11. Image Extraction

```python
from pypdf import PdfReader
import os

reader = PdfReader("document.pdf")
os.makedirs("extracted_images", exist_ok=True)

image_count = 0
for page_num, page in enumerate(reader.pages):
    if '/XObject' not in page['/Resources']:
        continue

    for obj_name, obj in page['/Resources']['/XObject'].items():
        if obj['/Subtype'] != '/Image':
            continue

        image_count += 1
        data = obj.get_data()

        # Determine format
        fmt = obj['/Filter']
        if isinstance(fmt, list):
            fmt = fmt[0]

        ext_map = {
            '/DCTDecode': 'jpg',
            '/JPXDecode': 'jp2',
            '/FlateDecode': 'png',
            '/CCITTFaxDecode': 'tiff',
        }
        ext = ext_map.get(fmt, 'png')

        filename = f"extracted_images/page{page_num+1}_{obj_name[1:]}.{ext}"
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"Extracted: {filename} ({len(data)} bytes)")

print(f"Total images extracted: {image_count}")
```

---

## 12. Encryption & Password Handling

```python
from pypdf import PdfReader, PdfWriter

# Detection
reader = PdfReader("document.pdf")
if reader.is_encrypted:
    print("PDF is encrypted.")

    # Try decrypting
    success = reader.decrypt("user_password")
    if success == 0:
        print("Wrong password.")
    elif success == 1:
        print("User password accepted.")
    elif success == 2:
        print("Owner password accepted — full access.")
    else:
        print(f"Decryption returned: {success}")

# Add password protection
writer = PdfWriter(clone_from="document.pdf")
writer.encrypt(
    user_password="user123",    # Required to open
    owner_password="owner456",  # Full permissions
    permissions_flag=0b0100_1100_0000,  # Allow printing + copying
    # Or use predefined permissions:
    # permissions_flag=PasswordType.PRINT | PasswordType.COPY
)
writer.write("protected.pdf")
```

### Remove Password (with Owner Credentials)

```python
reader = PdfReader("protected.pdf")
if reader.is_encrypted:
    reader.decrypt("owner456")

writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.write("unprotected.pdf")
```

---

## 13. Performance & Large Files

### Handling Large PDFs (>100 MB, >1000 pages)

```python
from pypdf import PdfReader, PdfWriter

# Use lazy reading for large files
reader = PdfReader("huge_document.pdf")  # Does NOT load all pages into memory

# Process one page at a time
for page in reader.pages:
    # Process page individually
    text = page.extract_text()
    # Write immediately, don't accumulate
```

### Stream-Writing for Large Merges

```python
# For very large merges, write incrementally
writer = PdfWriter()
for i, path in enumerate(large_pdf_list):
    writer.append(path)
    if (i + 1) % 10 == 0:  # Flush every 10 files
        writer.write(f"partial_{i//10}.pdf")
        writer = PdfWriter()
```

### Memory Profiling

```python
import tracemalloc

tracemalloc.start()
# ... PDF operation ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
```

---

## 14. Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| `PdfReadError: EOF marker not found` | Truncated or corrupt PDF | Try `PdfReader(path, strict=False)`, or repair with `mutool clean input.pdf output.pdf` |
| `PdfReadError: Could not find object` | Cross-reference table corrupted | Use `strict=False`, or try `qpdf --replace-input input.pdf` |
| `extract_text()` returns empty string | Scanned/image PDF, or custom font encoding | Use OCR path; check if text is selectable in a viewer |
| Encrypted PDF, no password prompt | PDF has empty password string | Try `reader.decrypt("")` |
| Text order is wrong | PDF internally stores text in non-visual order | Use `pdfplumber` which sorts by visual position |
| Table cells merged incorrectly | Vertical/horizontal line detection failed | Tune `extract_tables()` parameters; try visual debug mode |
| `ModuleNotFoundError: pdf2image` | Missing system dependency (poppler) | `brew install poppler` (macOS) or `apt install poppler-utils` (Linux) |
| OCR returns gibberish | Wrong language model | Specify `lang='eng+deu'` etc.; install language packs |
| Form fields not writable | Fields are flattened or XFA | Check `reader.get_fields()`; XFA forms need different approach |
| MemoryError on large PDF | Loading entire PDF into RAM | Process page-by-page; don't accumulate results in memory |