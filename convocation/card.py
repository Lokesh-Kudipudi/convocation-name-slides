import os
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw

from convocation.config import CardLayoutConfig
from convocation.utils import (
    load_font,
    get_scaled_font,
    center_paste,
    resize_keep_aspect,
    draw_centered_text,
    draw_wrapped_text
)

def clean_field(val: Any) -> str:
    """Helper to clean string values from CSV/DataFrame rows, handling NaNs."""
    if val is None:
        return ""
    # Check for pandas/numpy NaN without importing pandas/numpy
    if isinstance(val, float) and val != val:  # NaN is not equal to itself
        return ""
    s = str(val).strip()
    if s.lower() in ('nan', '<na>', 'nat'):
        return ""
    return s


def generate_student_card(
    row: Dict[str, Any],
    template_base: Image.Image,
    layout_config: CardLayoutConfig,
    photo_image: Optional[Image.Image] = None,
    logo_image: Optional[Image.Image] = None,
    draw_batch: bool = True
) -> Image.Image:
    """
    Renders a single student card PIL Image using student details, photo, and logo.
    """
    # Extract and clean row data
    roll_no = clean_field(row.get('Roll No', ''))
    student_name = clean_field(row.get('Student Name', ''))
    program_name = clean_field(row.get('Program Name', ''))
    branch = clean_field(row.get('Branch', ''))
    specialization = clean_field(row.get('Specialization', ''))
    
    # Copy the template base
    card = template_base.copy()
    draw = ImageDraw.Draw(card)
    
    # 1. Paste Photo if provided
    if photo_image:
        center_paste(card, photo_image, *layout_config.photo_box)
        
    # 2. Paste Logo if provided
    if logo_image:
        logo_resized = resize_keep_aspect(logo_image, *layout_config.logo_max_size)
        card.paste(logo_resized, layout_config.logo_position)
        
    # 3. Draw Program Name (with dynamic font scaling to fit max width)
    if program_name:
        font_program = get_scaled_font(
            layout_config.font_path,
            program_name,
            layout_config.text_max_width,
            layout_config.program_max_font_size,
            layout_config.program_min_font_size
        )
        draw_centered_text(
            draw, program_name, font_program,
            layout_config.program_y, card.width, layout_config.text_x_start
        )
        
    # 4. Draw Branch Name
    if branch:
        font_branch = load_font(layout_config.font_path, layout_config.branch_font_size)
        draw_centered_text(
            draw, branch, font_branch,
            layout_config.branch_y, card.width, layout_config.text_x_start
        )
        
    # 5. Draw Specialization (wrapped to fit max width and height)
    if specialization:
        font_spec = load_font(layout_config.font_path, layout_config.spec_font_size)
        draw_wrapped_text(
            draw, specialization, font_spec,
            layout_config.spec_y_center,
            layout_config.text_max_width,
            layout_config.spec_max_height,
            layout_config.spec_line_spacing,
            card.width,
            layout_config.text_x_start
        )
        
    # 6. Draw Student Name (wrapped to fit max width and height)
    if student_name:
        font_name = load_font(layout_config.font_path, layout_config.name_font_size)
        draw_wrapped_text(
            draw, student_name, font_name,
            layout_config.name_y_center,
            layout_config.text_max_width,
            layout_config.name_max_height,
            layout_config.name_line_spacing,
            card.width,
            layout_config.text_x_start
        )
        
    # 7. Draw Roll Number
    if roll_no:
        font_roll = load_font(layout_config.font_path, layout_config.roll_font_size)
        draw_centered_text(
            draw, roll_no, font_roll,
            layout_config.roll_y, card.width, layout_config.text_x_start
        )
        
    # 8. Draw Batch Number (Optional)
    if draw_batch and layout_config.batch_text:
        font_batch = load_font(layout_config.font_path, layout_config.batch_font_size)
        batch_x_start = layout_config.text_x_start + layout_config.batch_x_offset
        draw_centered_text(
            draw, layout_config.batch_text, font_batch,
            layout_config.batch_y, card.width, batch_x_start
        )
        
    return card
