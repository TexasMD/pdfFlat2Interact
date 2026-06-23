import cv2
import re
from pathlib import Path


def _id_part(value: str | None, fallback: str) -> str:
    raw = value or fallback
    stem = Path(raw).stem
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower()
    return normalized or fallback


def _page_part(page_num: int | None) -> str:
    return f"p{page_num:03d}" if page_num is not None else "punknown"


def detect_layout_blocks(
    image_path: str,
    *,
    source_file: str | None = None,
    page_num: int | None = None,
    run_id: str | None = None,
) -> list[dict]:
    """
    Detect layout blocks in an image using morphological operations and contour detection.
    Returns traceable layout block hypotheses with bounding boxes.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")
    page_height, page_width = img.shape[:2]

    # Binarize image (invert so text is white on black background)
    # Using Otsu's thresholding
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Use a rectangular structuring element to merge text into lines/blocks
    # Wide kernel merges characters into words/lines.
    # Tall kernel merges lines into paragraphs/blocks.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 15))

    # Apply dilation to connect components
    dilation = cv2.dilate(thresh, rect_kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter out very small noise blocks
        area = w * h
        if area > 400: # Arbitrary small threshold, can be tuned
            boxes.append((x, y, w, h))

    # Sort blocks top-to-bottom, then left-to-right
    boxes.sort(key=lambda b: (b[1], b[0]))

    source_part = _id_part(source_file, _id_part(image_path, "image"))
    page_part = _page_part(page_num)
    blocks = []
    for idx, (x, y, w, h) in enumerate(boxes, start=1):
        block = {
            "id": f"layout-{source_part}-{page_part}-b{idx:04d}",
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "text": "",
            "page_width": int(page_width),
            "page_height": int(page_height),
            "source_file": source_file,
            "page_num": page_num,
            "image_path": image_path,
            "rendered_image_path": image_path,
            "run_id": run_id,
            "status": "layout_hypothesis",
            "warnings": [],
        }
        block["role"] = classify_block_role(block)
        blocks.append(block)

    return blocks

def classify_block_role(block_dict: dict) -> str:
    """
    Classify a block into a durable role based on its features.
    Expected block_dict keys: 'x', 'y', 'w', 'h', 'text' (optional), 'page_width', 'page_height'.

    Roles: 'instruction', 'factoid_sidebar', 'visual_reference', 'exercise_items', 'footer', 'unknown'
    """
    x = block_dict.get('x', 0)
    y = block_dict.get('y', 0)
    w = block_dict.get('w', 0)
    h = block_dict.get('h', 0)
    page_w = block_dict.get('page_width', 1000)
    page_h = block_dict.get('page_height', 1000)
    text = block_dict.get('text', "")

    text_normalized = text.strip().lower()
    area_ratio = (w * h) / (page_w * page_h) if page_w and page_h else 0
    margin_block = (x > page_w * 0.65 or x + w < page_w * 0.35) and w < page_w * 0.45
    visual_keywords = (
        "number line", "map", "graph", "chart", "table", "diagram",
        "picture", "grid", "crossword", "shown", "above", "below",
    )
    explicit_visual_hint = (
        bool(block_dict.get("visual_type"))
        or bool(block_dict.get("contains_number_line"))
    )
    visual_keyword_shape_hint = any(keyword in text_normalized for keyword in visual_keywords) and area_ratio > 0.08
    wide_thin_low_text = (
        w > page_w * 0.45
        and h < page_h * 0.08
        and len(text_normalized) < 20
        and area_ratio > 0.01
    )

    # 1. Footer check
    # If it's very low on the page and relatively thin
    if y > page_h * 0.9 and h < page_h * 0.1:
        return "footer"

    # 2. Factoid/Sidebar check
    # If it's pushed far to one margin and relatively narrow, including top-corner callouts.
    if margin_block and y < page_h * 0.75:
        return "factoid_sidebar"

    # 3. Visual Reference check
    # If it occupies a significant area but has very little text (or specific visual keywords)
    # Note: text density check would be ideal here if text is populated
    if explicit_visual_hint or visual_keyword_shape_hint or (area_ratio > 0.15 and len(text_normalized) < 50) or wide_thin_low_text:
        return "visual_reference"

    # 4. Instruction check
    # Typically near the top or immediately preceding a large exercise block, spanning most of the width
    if y < page_h * 0.3 and w > page_w * 0.6:
        # Simple heuristic: starts with a number or action verb, or is bold (if font data existed)
        return "instruction"

    # 5. Exercise items
    # Typically central, containing lists or multiple lines
    if x > page_w * 0.1 and x < page_w * 0.3 and w > page_w * 0.4:
        return "exercise_items"

    return "unknown"
