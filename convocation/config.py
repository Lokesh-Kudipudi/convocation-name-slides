from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class CardLayoutConfig:
    # Font path
    font_path: str = "arial.ttf"
    
    # Photo box parameters: (x, y, width, height)
    photo_box: Tuple[int, int, int, int] = (50, 165, 750, 750)
    
    # Logo config
    logo_path: str = "logo.jpg"
    logo_position: Tuple[int, int] = (1700, 860)
    logo_max_size: Tuple[int, int] = (200, 200)
    
    # Text horizontal alignment bounds (usually right side of card starts at x=850)
    text_x_start: int = 850
    text_max_width: int = 1020
    
    # Program Name text
    program_y: int = 185
    program_max_font_size: int = 96
    program_min_font_size: int = 24
    
    # Branch text
    branch_y: int = 325
    branch_font_size: int = 48
    
    # Specialization text
    spec_y_center: int = 465
    spec_font_size: int = 24
    spec_max_height: int = 200
    spec_line_spacing: int = 8
    
    # Student Name text
    name_y_center: int = 615
    name_font_size: int = 52
    name_max_height: int = 200
    name_line_spacing: int = 10
    
    # Roll Number text
    roll_y: int = 765
    roll_font_size: int = 52
    
    # Batch text
    batch_y: float = 929.5
    batch_font_size: int = 96
    batch_x_offset: int = -200
    batch_text: str = "BATCH - 2025"


@dataclass
class PreRenderedTemplateConfig:
    # Configuration for inserting photos on pre-rendered templates (imgeditor / pdfeditor)
    paste_position: Tuple[int, int] = (165, 232)
    max_size: Tuple[int, int] = (750, 750)
    max_size_pdf: Tuple[int, int] = (600, 600)
    special_rolls: list[str] = field(default_factory=lambda: [
        "S20210010011", "S20210010095", "S20210010125", "S20210020285"
    ])
