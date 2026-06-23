import cv2
import numpy as np

def detect_layout_blocks(image_path: str) -> list[tuple[int, int, int, int]]:
    """
    Detect layout blocks in an image using morphological operations and contour detection.
    Returns a list of bounding boxes (x, y, w, h) for detected blocks.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")

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

    blocks = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter out very small noise blocks
        area = w * h
        if area > 400: # Arbitrary small threshold, can be tuned
            blocks.append((x, y, w, h))

    # Sort blocks top-to-bottom, then left-to-right
    blocks.sort(key=lambda b: (b[1], b[0]))

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

    area_ratio = (w * h) / (page_w * page_h) if page_w and page_h else 0

    # 1. Footer check
    # If it's very low on the page and relatively thin
    if y > page_h * 0.9 and h < page_h * 0.1:
        return "footer"

    # 2. Factoid/Sidebar check
    # If it's pushed far to one margin, relatively narrow, and not at the very top
    if (x > page_w * 0.7 or x + w < page_w * 0.3) and w < page_w * 0.4 and y > page_h * 0.1:
        return "factoid_sidebar"

    # 3. Visual Reference check
    # If it occupies a significant area but has very little text (or specific visual keywords)
    # Note: text density check would be ideal here if text is populated
    if area_ratio > 0.15 and len(text.strip()) < 50:
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
