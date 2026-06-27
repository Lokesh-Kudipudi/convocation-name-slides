import os
from typing import Optional, Union, List, Dict, Any
import pandas as pd
from PIL import Image

from convocation.config import PreRenderedTemplateConfig
from convocation.utils import find_photo, resize_keep_aspect

def create_pdf_from_image_templates(
    student_data: Union[pd.DataFrame, List[Dict[str, Any]]],
    template_folder: str,
    image_folder: str,
    output_folder: str,
    output_pdf: str,
    layout_config: PreRenderedTemplateConfig
) -> None:
    """
    Pastes student photos onto sequential Canva template images (template/1.png, template/2.png, etc.)
    and compiles them into a single PDF file.
    """
    rows = student_data.to_dict(orient="records") if isinstance(student_data, pd.DataFrame) else student_data
    i = 1
    final_images = []
    os.makedirs(output_folder, exist_ok=True)
    
    for row in rows:
        roll = str(row.get('Roll No', '')).strip()
        if not roll:
            continue
            
        template_path = os.path.join(template_folder, f"{i}.png")
        if not os.path.exists(template_path):
            print(f"Warning: Template image not found at {template_path}. Skipping row {roll}...")
            continue
            
        # Check special rolls where no photo is pasted
        if roll in layout_config.special_rolls:
            try:
                template = Image.open(template_path).convert("RGB")
                output_path = os.path.join(output_folder, f"{roll}.png")
                template.save(output_path)
                print(f"{roll} Saved (Special Roll, keeping template template/{i}.png as is)")
                final_images.append(template)
                i += 1
            except Exception as e:
                print(f"Error processing special roll {roll} at index {i}: {e}")
            continue
            
        photo = find_photo(roll, image_folder)
        if not photo:
            print(f"Photo not found for Roll Number: {roll}, skipping template/{i}.png insertion...")
            # Note: Do not increment index i, matching legacy behavior
            continue
            
        try:
            template = Image.open(template_path).convert("RGB")
            photo_resized = resize_keep_aspect(photo, *layout_config.max_size)
            template.paste(photo_resized, layout_config.paste_position)
            
            output_path = os.path.join(output_folder, f"{roll}.png")
            template.save(output_path)
            print(f"{roll} Saved (Photo pasted on template/{i}.png)")
            final_images.append(template)
            i += 1
        except Exception as e:
            print(f"Error processing roll {roll} at index {i}: {e}")
            
    if final_images:
        final_images[0].save(
            output_pdf,
            save_all=True,
            append_images=final_images[1:],
            resolution=100
        )
        print(f"Saved final PDF: {output_pdf}")
    else:
        print("No images were processed. PDF not created.")


def create_pdf_from_pdf_pages(
    student_data: Union[pd.DataFrame, List[Dict[str, Any]]],
    pdf_template_path: str,
    image_folder: str,
    output_folder: str,
    output_pdf: str,
    layout_config: PreRenderedTemplateConfig,
    poppler_path: Optional[str] = None
) -> None:
    """
    Converts pages from a template PDF into images, pastes student photos onto them,
    and compiles them back into a single PDF.
    """
    from pdf2image import convert_from_path
    
    rows = student_data.to_dict(orient="records") if isinstance(student_data, pd.DataFrame) else student_data
    roll_numbers = [str(r.get('Roll No', '')).strip() for r in rows if str(r.get('Roll No', '')).strip()]
    
    print(f"Converting PDF template {pdf_template_path} to images...")
    convert_kwargs = {}
    if poppler_path:
        convert_kwargs['poppler_path'] = poppler_path
        
    try:
        pages = convert_from_path(pdf_template_path, **convert_kwargs)
    except Exception as e:
        print(f"Error converting PDF pages: {e}")
        print("Please verify that poppler is installed and configured on your system.")
        return
        
    os.makedirs(output_folder, exist_ok=True)
    output_images = []
    
    # Process each page paired with a roll number
    for page, roll_no in zip(pages, roll_numbers):
        print(f"Processing page for student {roll_no}...")
        photo = find_photo(roll_no, image_folder)
        if not photo:
            print(f"❌ Photo not found for {roll_no}, skipping page...")
            continue
            
        try:
            # Resize and paste the photo
            photo_resized = resize_keep_aspect(photo, *layout_config.max_size_pdf)
            page_rgb = page.convert("RGB")
            page_rgb.paste(photo_resized, layout_config.paste_position)
            
            output_path = os.path.join(output_folder, f"{roll_no}.jpg")
            page_rgb.save(output_path)
            output_images.append(page_rgb)
        except Exception as e:
            print(f"Error processing page for {roll_no}: {e}")
            
    if output_images:
        output_images[0].save(
            output_pdf,
            save_all=True,
            append_images=output_images[1:]
        )
        print(f"✅ PDF created: {output_pdf}")
    else:
        print("⚠️ No output PDF created. Check image paths and CSV.")
