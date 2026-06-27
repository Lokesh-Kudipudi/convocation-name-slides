# Convocation name slide generator.

This repository provides a unified command-line utility to generate student 
name slides for convocation.

## Installation

This project uses `uv` for python dependency management, but can also be run with standard Python.

Ensure you have the required dependencies installed:
```bash
uv pip install -r pyproject.toml
# Or using pip:
pip install openpyxl pandas pdf2image pillow python-pptx reportlab
```

### PDF page processing dependency (Optional)
The `pdf-pages` command converts PDF templates into images using `pdf2image`. This requires **Poppler** to be installed on your system:
- **macOS**: `brew install poppler`
- **Windows**: Download Poppler, extract it, and specify the bin folder via `--poppler-path` argument if it's not in your system environment variable path.

## CSV File Formats

Depending on the subcommand you run, your input CSV must contain specific columns:

### For `cards` and `slides` Subcommands
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

### For `pdf-templates` and `pdf-pages` Subcommands
These commands paste photo files onto pre-rendered templates/pages where student details are already printed, requiring only:
- `Roll No`: The student's roll number to load their photo and match the sequential template or PDF page order.

*Example:*
```csv
Roll No
S20210010029
S20210010030
```

---

## Usage


All workflows are unified under the `main.py` entrypoint.

### 1. Generate Student Card Images
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

### 2. Generate PowerPoint Slide Presentation
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

### 3. Generate PDF from Pre-rendered Templates
Pastes student photos onto sequential Canva-generated template images (e.g. `template/1.png`, `template/2.png`, etc.) and compiles them into a single PDF.

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

### 4. Generate PDF from Template PDF Pages
Converts a template PDF page-by-page, pastes student photos onto each page, and compiles them back into a single PDF.

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
