# Convocation name slide generator

This repository provides a unified command-line utility to generate student
name slides for convocation — student cards, PowerPoint decks, and final
print-ready PDFs with photos pasted onto templates.

## Which scenario are you in?

This tool can be used in two very different ways depending on whether you
have **Canva Pro** available. Figuring out which scenario applies to you
first will save you time, since it determines which subcommands you
actually need.

### Scenario A — You have Canva Pro (recommended if available)

Canva Pro includes a **Bulk Create** feature that can take a CSV of student
data (name, program, branch, specialization, etc.) and auto-generate one
designed slide per row, with all the text already laid out using your
template/brand kit. This means Canva handles all the *text rendering* for
you — you don't need this script's `cards` or `slides` commands at all.

What Canva Pro **cannot** do is pull in a different *photo* per student from
a folder of files named by roll number. That's the one gap this script
fills.

**Your workflow:**
1. In Canva, design your slide template with placeholder text fields
   (Student Name, Program Name, Branch, Specialization) and a blank/empty
   image placeholder where the photo should go.
2. Use **Bulk Create** with a CSV containing your student data to generate
   one slide per student, with all text fields populated.
3. Export the result as a single **PDF** (File → Download → PDF, "All
   pages"). Each page will be one student's slide, in the same order as
   your CSV.
4. Prepare a second, simpler CSV containing just the `Roll No` column, in
   the **same order as your Canva export**, so this script knows which
   photo belongs on which page.
5. Run this script's `pdf-pages` command to paste each student's photo
   into the blank placeholder on their corresponding PDF page, and compile
   everything into a final print-ready PDF.

```bash
python main.py pdf-pages --csv canva.csv --pdf template.pdf --output-pdf final_output.pdf
```

That's it — no `--template`, no font setup, no text positioning. Canva did
that part; this script only pastes photos.

> **Tip:** If instead of a PDF you exported your Bulk Create batch as a
> folder of sequential images (e.g. `1.png`, `2.png`, ...), use
> `pdf-templates` instead of `pdf-pages` — see the
> [full subcommand reference](#3-generate-pdf-from-pre-rendered-templates)
> below. Most users exporting from Canva will want the PDF route above.

### Scenario B — You don't have Canva Pro

Without Bulk Create, there's no tool generating the text-rendered slides
for you — so this script needs to do that part itself, in addition to
pasting photos. You'll use the `cards` or `slides` commands, which draw
the student's name, program, branch, and specialization directly onto a
blank base template image using Pillow, then paste in the student's photo.

**Your workflow:**
1. Design (or obtain) a single blank base template image — no per-student
   text needed, since this script draws it for you.
2. Prepare a CSV with the full student detail columns (see
   [CSV File Formats](#csv-file-formats) below).
3. Run `cards` to generate individual card PNGs, or `slides` to generate
   a ready-to-present PowerPoint deck with one slide per student.

```bash
python main.py slides --csv data.csv --template template.png --logo logo.jpg --output-pptx all_students.pptx
```

---

## Installation

This project uses `uv` for python dependency management, but can also be run with standard Python.

Ensure you have the required dependencies installed:
```bash
uv pip install -r pyproject.toml
# Or using pip:
pip install openpyxl pandas pdf2image pillow python-pptx reportlab
```

### PDF page processing dependency (Optional, required for Scenario A)
The `pdf-pages` command converts PDF templates into images using `pdf2image`. This requires **Poppler** to be installed on your system:
- **macOS**: `brew install poppler`
- **Windows**: Download Poppler, extract it, and specify the bin folder via `--poppler-path` argument if it's not in your system environment variable path.

## CSV File Formats

Depending on the subcommand you run, your input CSV must contain specific columns:

### For `cards` and `slides` Subcommands (Scenario B — no Canva Pro)
These commands dynamically render text and overlays, requiring the following headers in your CSV:
- `Roll No`: The student's unique identifier (e.g., `S20210010029`). Also used to locate the photo image named `{RollNo}.(jpg|png|jpeg)`.
- `Student Name`: The student's full name.
- `Program Name`: The degree program name.
- `Branch`: The academic branch/department.
- `Specialization`: (Optional) The area of specialization (wrapped automatically if long).

*Example:*
```csv
Roll No,Student Name,Program Name,Branch,Specialization
S20160990002,RAVI GORRIPATI,Doctor of Philosophy,Computer Science and Engineering,ENABLING PARTICIPATORY DECISION MAKING...
```

This is also the same CSV format you'd feed into Canva's Bulk Create if you're following Scenario A — Canva needs these same fields to populate the text. The difference is only in step 4 of Scenario A, where you prepare a *second*, simpler CSV (below) just for the photo-pasting step.

### For `pdf-templates` and `pdf-pages` Subcommands (Scenario A — with Canva Pro)
These commands paste photo files onto pre-rendered templates/pages where student details are already printed, requiring only:
- `Roll No`: The student's roll number to load their photo and match the sequential template or PDF page order.

*Example:*
```csv
Roll No
S20210010029
S20210010030
```

**Important:** The order of rows in this CSV must match the order of pages/images in your Canva export exactly, since this script matches them positionally (row 1 → page 1, row 2 → page 2, etc.), not by reading any text off the page.

---

## Full Subcommand Reference

All workflows are unified under the `main.py` entrypoint.

### 1. Generate Student Card Images (Scenario B)
Renders student cards to PNG images from a student information CSV and a base image.

```bash
python main.py cards --csv test.csv --template template.png --logo logo.jpg --output-dir output
```

**Options:**
- `--csv`: Path to student information CSV (default: `test.csv`).
- `--template`: Path to base template image (default: `template.png`).
- `--logo`: Path to institution logo image (default: `logo.jpg`).
- `--image-dir`: Directory containing student photos named `{RollNo}.(jpg|png|jpeg)` (default: `images`).
- `--output-dir`: Directory to save generated card PNGs (default: `output`).
- `--font`: Font file name or path (default: `arial.ttf`).
- `--no-batch`: Do not print the Batch number on cards.
- `--batch-text`: Batch number string to render (default: `BATCH - 2025`).
- `--single-roll`: Process and generate card for only a single roll number (useful for testing).

---

### 2. Generate PowerPoint Slide Presentation (Scenario B)
Creates a widescreen PowerPoint slide presentation (`.pptx`) with student cards, one slide per student.

```bash
python main.py slides --csv data.csv --template template.png --logo logo.jpg --output-pptx all_students.pptx
```

**Options:**
- `--csv`: Path to student information CSV (default: `data.csv`).
- `--template`: Path to base template image (default: `template.png`).
- `--logo`: Path to institution logo image (default: `logo.jpg`).
- `--image-dir`: Directory containing student photos (default: `images`).
- `--output-dir`: Directory to save/load card PNGs (default: `output`).
- `--output-pptx`: Path to output PPTX file (default: `all_students.pptx`).
- `--font`: Font file name or path (default: `arial.ttf`).
- `--no-batch`: Do not print the Batch number on cards.
- `--batch-text`: Batch number string to render (default: `BATCH - 2025`).
- `--overwrite`: Force overwrite of existing card PNGs inside the output directory instead of reusing them.

---

### 3. Generate PDF from Pre-rendered Templates (Scenario A — sequential images)
Pastes student photos onto sequential Canva-generated template images (e.g. `template/1.png`, `template/2.png`, etc.) and compiles them into a single PDF. Use this if you exported your Canva Bulk Create batch as individual image files rather than a single PDF.

```bash
python main.py pdf-templates --csv canva.csv --template-dir template --output-pdf final_output.pdf
```

**Options:**
- `--csv`: Path to CSV containing roll numbers (default: `canva.csv`).
- `--template-dir`: Directory containing sequential template images (default: `template`).
- `--image-dir`: Directory containing student photo files (default: `images`).
- `--output-dir`: Directory to save intermediate output images (default: `output`).
- `--output-pdf`: Path to save output PDF (default: `final_output.pdf`).

---

### 4. Generate PDF from Template PDF Pages (Scenario A — PDF export, most common)
Converts a template PDF page-by-page, pastes student photos onto each page, and compiles them back into a single PDF. This is the command most Canva Pro users will reach for, since Canva's Bulk Create exports cleanly as a multi-page PDF.

```bash
python main.py pdf-pages --csv canva.csv --pdf template.pdf --output-pdf final_output.pdf
```

**Options:**
- `--csv`: Path to CSV containing roll numbers (default: `canva.csv`).
- `--pdf`: Path to template PDF file (default: `template.pdf`).
- `--image-dir`: Directory containing student photo files (default: `images`).
- `--output-dir`: Directory to save modified page images (default: `processed_pages`).
- `--output-pdf`: Path to save final PDF (default: `final_output.pdf`).
- `--poppler-path`: Path to Poppler bin directory (required on Windows if not in environment PATH).

---

## Customizing Layout (Editing `config.py`)

If text or photos land in the wrong spot on your template — or you just want
to redesign the layout — you don't need to touch the rendering code in
`card.py` or `pdf.py`. All pixel positions, font sizes, and box dimensions
live in `convocation/config.py` as plain dataclass fields, so adjusting the
layout is just a matter of editing numbers there and re-running.

There are two config classes, and which one matters depends on your scenario:

### `CardLayoutConfig` — for `cards` and `slides` (Scenario B)

This controls every coordinate used when the script draws text and photos
onto a blank template from scratch. Relevant fields if your layout needs
tweaking:

- **`photo_box`** — `(x, y, width, height)` of the box the student photo is
  resized and centered into.
- **`logo_position`** / **`logo_max_size`** — where the institution logo is
  placed and its maximum dimensions.
- **`text_x_start`** / **`text_max_width`** — the left edge and width of the
  column all text fields are aligned within (defaults assume text sits on
  the right half of the card, starting at `x=850`).
- **`program_y`**, **`branch_y`**, **`spec_y_center`**, **`name_y_center`**,
  **`roll_y`**, **`batch_y`** — vertical position for each text field.
- **`*_font_size`** fields — fixed font sizes for branch, name, roll number,
  and batch text. `program_max_font_size` / `program_min_font_size` instead
  define a shrink-to-fit range, since program names vary a lot in length.
- **`*_max_height`** / **`*_line_spacing`** — for the name and
  specialization fields, which can wrap onto multiple lines.
- **`font_path`** — overridden by the `--font` CLI flag if passed, but this
  is the fallback default.

If text is overlapping, clipped, or sitting too high/low for your specific
template image, this is the file to edit — just update the relevant `_y`,
`_x`, or `font_size` value and re-run `cards` or `slides`.

### `PreRenderedTemplateConfig` — for `pdf-templates` and `pdf-pages` (Scenario A)

Since Canva already draws the text in this scenario, this config only
controls where the **photo** gets pasted into the placeholder Canva left
for it:

- **`paste_position`** — `(x, y)` top-left corner where the photo is pasted.
- **`max_size`** — max `(width, height)` for photos pasted onto image
  templates (used by `pdf-templates`).
- **`max_size_pdf`** — a separate, typically smaller max size used by
  `pdf-pages`, since PDF-rasterized pages are handled at a different
  resolution than direct image templates.
- **`special_rolls`** — a list of roll numbers that need different/special
  handling than the rest (e.g. a different photo position or size for a
  retake photo, a re-issued ID, or a layout exception). Add or remove roll
  numbers here as needed; check `pdf.py` to see exactly how entries in this
  list are treated differently.

If a student's photo is landing in the wrong spot or the wrong size on your
Canva-exported template, `paste_position` and `max_size`/`max_size_pdf` are
the values to adjust here — make sure the position matches the placeholder
location in your actual Canva design, in pixels at your export resolution.

---

## Directory Structure

```
.
├── convocation/             # Python package containing unified core logic
│   ├── __init__.py
│   ├── config.py            # Dataclasses defining coordinates, fonts and positions
│   ├── utils.py             # Image helpers (resizing, center-pasting, wrapping text)
│   ├── card.py              # Card rendering logic (drawing text/photos/logo)
│   ├── presentation.py      # PowerPoint presentation generator logic
│   └── pdf.py               # PDF template/pages photo pasting logic
├── main.py                  # Single entrypoint CLI script
├── README.md                # Documentation (this file)
└── pyproject.toml           # Project dependencies and settings
```
