import os
from typing import Tuple, List, Optional
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

def resize_keep_aspect(photo: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Resize photo maintaining aspect ratio using LANCZOS filter."""
    original_width, original_height = photo.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return photo.resize((new_width, new_height), Image.Resampling.LANCZOS)


def center_paste(template: Image.Image, photo: Image.Image, 
                 box_x: int, box_y: int, box_w: int, box_h: int) -> None:
    """Resize photo and paste it in the center of the bounding box on the template."""
    resized = resize_keep_aspect(photo, box_w, box_h)
    rw, rh = resized.size
    paste_x = box_x + (box_w - rw) // 2
    paste_y = box_y + (box_h - rh) // 2
    template.paste(resized, (paste_x, paste_y))


def find_photo(roll_no: str, image_folder: str) -> Optional[Image.Image]:
    """Search for student photo matching roll_no with standard extensions."""
    for ext in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
        photo_path = os.path.join(image_folder, f"{roll_no}.{ext}")
        if os.path.exists(photo_path):
            try:
                return Image.open(photo_path).convert("RGB")
            except Exception as e:
                print(f"Error opening photo {photo_path}: {e}")
    return None


@lru_cache(maxsize=128)
def load_font(font_path: str, size: int) -> ImageFont.ImageFont:
    """Load a truetype font with fallback logic for macOS/Linux/Windows."""
    try:
        return ImageFont.truetype(font_path, size=size)
    except IOError:
        # Common system fallbacks
        fallbacks = [
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            font_path
        ]
        for path in fallbacks:
            try:
                return ImageFont.truetype(path, size=size)
            except IOError:
                continue
        # Fallback to default PIL font if nothing else works
        return ImageFont.load_default()


@lru_cache(maxsize=128)
def get_scaled_font(font_path: str, text: str, max_width: int, 
                    max_size: int, min_size: int = 24) -> ImageFont.ImageFont:
    """Iterate font size downwards from max_size to fit text within max_width."""
    # Create a dummy image/draw to measure text bounding box
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    
    for size in range(max_size, min_size - 1, -2):
        font = load_font(font_path, size)
        # Note: If it fell back to load_default, we can't scale it, just return it
        if isinstance(font, ImageFont.ImageFont) and font.path is None:
            return font
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return font
            
    return load_font(font_path, min_size)


def wrap_text_to_lines(draw: ImageDraw.Draw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    """Greedily wrap text into a list of lines that fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = test_bbox[2] - test_bbox[0]
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_centered_text(draw: ImageDraw.Draw, text: str, font: ImageFont.ImageFont,
                       y: float, template_width: int, text_x_start: int, fill: str = "black") -> None:
    """Draw a single line of text centered in the text block area."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (template_width - text_width + text_x_start) // 2
    draw.text((x, int(y)), text, font=font, fill=fill)


def draw_wrapped_text(draw: ImageDraw.Draw, text: str, font: ImageFont.ImageFont,
                      y_center: int, max_width: int, max_height: int, line_spacing: int,
                      template_width: int, text_x_start: int, fill: str = "black") -> None:
    """Wrap text to fit max_width and draw centered vertically around y_center."""
    lines = wrap_text_to_lines(draw, text, font, max_width)
    
    # Calculate line height based on font metrics
    line_bbox = font.getbbox("Ay")
    line_height = line_bbox[3] - line_bbox[1]
    
    max_lines = max(1, max_height // (line_height + line_spacing))
    lines = lines[:max_lines]
    
    total_text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
    start_y = y_center - total_text_height // 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (template_width - text_width + text_x_start) // 2
        y = start_y + i * (line_height + line_spacing)
        draw.text((x, y), line, font=font, fill=fill)
