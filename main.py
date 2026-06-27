import os
import argparse
import pandas as pd
from PIL import Image

from convocation.config import CardLayoutConfig, PreRenderedTemplateConfig
from convocation.card import generate_student_card
from convocation.presentation import create_presentation_from_cards
from convocation.pdf import create_pdf_from_image_templates, create_pdf_from_pdf_pages
from convocation.utils import find_photo

def run_cards(args):
    """Executes the card generation workflow."""
    layout_config = CardLayoutConfig(
        font_path=args.font,
        logo_path=args.logo,
        batch_text="" if args.no_batch else args.batch_text
    )
    
    if not os.path.exists(args.csv):
        print(f"Error: CSV file '{args.csv}' not found.")
        return
        
    df = pd.read_csv(args.csv)
    
    if args.single_roll:
        roll_val = args.single_roll.strip()
        df = df[df['Roll No'].astype(str).str.strip() == roll_val]
        if df.empty:
            print(f"Error: Roll number '{roll_val}' not found in '{args.csv}'.")
            return
            
    if not os.path.exists(args.template):
        print(f"Error: Template image '{args.template}' not found.")
        return
        
    template_base = Image.open(args.template)
    
    logo_image = None
    if layout_config.logo_path and os.path.exists(layout_config.logo_path):
        logo_image = Image.open(layout_config.logo_path).convert("RGB")
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    success_count = 0
    for _, row in df.iterrows():
        roll_no = str(row.get('Roll No', '')).strip()
        if not roll_no:
            continue
            
        photo = find_photo(roll_no, args.image_dir)
        if not photo:
            print(f"Photo not found for Roll No: {roll_no}, skipping card generation...")
            continue
            
        try:
            card = generate_student_card(
                row=row,
                template_base=template_base,
                layout_config=layout_config,
                photo_image=photo,
                logo_image=logo_image,
                draw_batch=not args.no_batch
            )
            output_path = os.path.join(args.output_dir, f"{roll_no}.png")
            card.save(output_path)
            print(f"Saved Card - {roll_no}")
            success_count += 1
        except Exception as e:
            print(f"Error generating card for Roll No {roll_no}: {e}")
            
    print(f"Completed card generation. Successfully created {success_count} cards.")


def run_slides(args):
    """Executes the PowerPoint slide generation workflow."""
    layout_config = CardLayoutConfig(
        font_path=args.font,
        logo_path=args.logo,
        batch_text="" if args.no_batch else args.batch_text
    )
    
    if not os.path.exists(args.csv):
        print(f"Error: CSV file '{args.csv}' not found.")
        return
        
    df = pd.read_csv(args.csv)
    
    create_presentation_from_cards(
        student_data=df,
        template_path=args.template,
        image_folder=args.image_dir,
        output_folder=args.output_dir,
        output_pptx=args.output_pptx,
        layout_config=layout_config,
        logo_path=args.logo,
        draw_batch=not args.no_batch,
        overwrite_cards=args.overwrite
    )


def run_pdf_templates(args):
    """Executes Canva template image sequential pasting workflow."""
    layout_config = PreRenderedTemplateConfig()
    
    if not os.path.exists(args.csv):
        print(f"Error: CSV file '{args.csv}' not found.")
        return
        
    df = pd.read_csv(args.csv)
    
    if not os.path.exists(args.template_dir):
        print(f"Error: Template directory '{args.template_dir}' not found.")
        return
        
    create_pdf_from_image_templates(
        student_data=df,
        template_folder=args.template_dir,
        image_folder=args.image_dir,
        output_folder=args.output_dir,
        output_pdf=args.output_pdf,
        layout_config=layout_config
    )


def run_pdf_pages(args):
    """Executes PDF template conversion and photo pasting workflow."""
    layout_config = PreRenderedTemplateConfig()
    
    if not os.path.exists(args.csv):
        print(f"Error: CSV file '{args.csv}' not found.")
        return
        
    df = pd.read_csv(args.csv)
    
    if not os.path.exists(args.pdf):
        print(f"Error: Template PDF file '{args.pdf}' not found.")
        return
        
    # Windows fallback path if not custom provided, or None for macOS/Linux
    poppler_path = args.poppler_path
    if not poppler_path and os.name == 'nt':
        poppler_path = r"C:\poppler-24.08.0\Library\bin"
        
    create_pdf_from_pdf_pages(
        student_data=df,
        pdf_template_path=args.pdf,
        image_folder=args.image_dir,
        output_folder=args.output_dir,
        output_pdf=args.output_pdf,
        layout_config=layout_config,
        poppler_path=poppler_path
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convocation Card, Slide, and PDF Generator CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # 1. Cards command
    parser_cards = subparsers.add_parser("cards", help="Generate PNG student cards from CSV and base template")
    parser_cards.add_argument("--csv", default="test.csv", help="Path to student information CSV (default: test.csv)")
    parser_cards.add_argument("--template", default="template.png", help="Path to base template image (default: template.png)")
    parser_cards.add_argument("--logo", default="logo.jpg", help="Path to institution logo image (default: logo.jpg)")
    parser_cards.add_argument("--image-dir", default="images", help="Directory containing student photo files (default: images)")
    parser_cards.add_argument("--output-dir", default="output", help="Directory to save generated card PNGs (default: output)")
    parser_cards.add_argument("--font", default="arial.ttf", help="Font file name or absolute path (default: arial.ttf)")
    parser_cards.add_argument("--no-batch", action="store_true", help="Do not print the Batch number on cards")
    parser_cards.add_argument("--batch-text", default="BATCH - 2025", help="Batch number string to render (default: BATCH - 2025)")
    parser_cards.add_argument("--single-roll", help="Generate card for only a single roll number")
    parser_cards.set_defaults(func=run_cards)
    
    # 2. Slides command
    parser_slides = subparsers.add_parser("slides", help="Generate widescreen PPTX slides with student cards")
    parser_slides.add_argument("--csv", default="data.csv", help="Path to student information CSV (default: data.csv)")
    parser_slides.add_argument("--template", default="template.png", help="Path to base template image (default: template.png)")
    parser_slides.add_argument("--logo", default="logo.jpg", help="Path to institution logo image (default: logo.jpg)")
    parser_slides.add_argument("--image-dir", default="images", help="Directory containing student photo files (default: images)")
    parser_slides.add_argument("--output-dir", default="output", help="Directory to save/load card PNGs (default: output)")
    parser_slides.add_argument("--output-pptx", default="all_students.pptx", help="Path to output PPTX file (default: all_students.pptx)")
    parser_slides.add_argument("--font", default="arial.ttf", help="Font file name or absolute path (default: arial.ttf)")
    parser_slides.add_argument("--no-batch", action="store_true", help="Do not print the Batch number on cards")
    parser_slides.add_argument("--batch-text", default="BATCH - 2025", help="Batch number string to render (default: BATCH - 2025)")
    parser_slides.add_argument("--overwrite", action="store_true", help="Force overwrite of existing card PNGs inside output directory")
    parser_slides.set_defaults(func=run_slides)
    
    # 3. PDF Templates command (Sequential Canva images)
    parser_pdf_tmpl = subparsers.add_parser("pdf-templates", help="Paste photos on sequential template images and compile to PDF")
    parser_pdf_tmpl.add_argument("--csv", default="canva.csv", help="Path to CSV containing roll numbers (default: canva.csv)")
    parser_pdf_tmpl.add_argument("--template-dir", default="template", help="Directory containing sequential template images (default: template)")
    parser_pdf_tmpl.add_argument("--image-dir", default="images", help="Directory containing student photo files (default: images)")
    parser_pdf_tmpl.add_argument("--output-dir", default="output", help="Directory to save intermediate output images (default: output)")
    parser_pdf_tmpl.add_argument("--output-pdf", default="final_output.pdf", help="Path to save output PDF (default: final_output.pdf)")
    parser_pdf_tmpl.set_defaults(func=run_pdf_templates)
    
    # 4. PDF Pages command (Convert template PDF)
    parser_pdf_pages = subparsers.add_parser("pdf-pages", help="Convert template PDF, paste photos page-by-page, and save to PDF")
    parser_pdf_pages.add_argument("--csv", default="canva.csv", help="Path to CSV containing roll numbers (default: canva.csv)")
    parser_pdf_pages.add_argument("--pdf", default="template.pdf", help="Path to template PDF file (default: template.pdf)")
    parser_pdf_pages.add_argument("--image-dir", default="images", help="Directory containing student photo files (default: images)")
    parser_pdf_pages.add_argument("--output-dir", default="processed_pages", help="Directory to save modified page images (default: processed_pages)")
    parser_pdf_pages.add_argument("--output-pdf", default="final_output.pdf", help="Path to save final PDF (default: final_output.pdf)")
    parser_pdf_pages.add_argument("--poppler-path", help="Path to Poppler bin directory (required on Windows if not in environment PATH)")
    parser_pdf_pages.set_defaults(func=run_pdf_pages)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
