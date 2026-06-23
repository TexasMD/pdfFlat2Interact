import cv2
import numpy as np
import pytesseract
import re

def extract_clue_text_from_image(img, grid_rect):
    """
    Find text regions outside the grid_rect, run OCR, and parse clues.
    Returns (across_clues_text, down_clues_text) as dictionaries mapping number to string.
    """
    x, y, w, h = grid_rect
    h_img, w_img = img.shape[:2]

    # Create a mask covering everything EXCEPT the grid
    mask = np.ones((h_img, w_img), dtype=np.uint8) * 255
    cv2.rectangle(mask, (x, y), (x+w, y+h), 0, -1)

    # Apply mask
    img_outside = cv2.bitwise_and(img, mask)

    text = pytesseract.image_to_string(img_outside, config='--psm 3')
    return parse_clues_from_text(text)

def parse_clues_from_text(text):
    """
    Parse OCR text to extract Across and Down clues.
    """
    across_clues = {}
    down_clues = {}
    current_section = None

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        if re.match(r"(?i)^Across\s*$", line):
            current_section = across_clues
            continue
        elif re.match(r"(?i)^Down\s*$", line):
            current_section = down_clues
            continue

        if current_section is not None:
            match = re.match(r"^(\d+)[.)]?\s*(.*)", line)
            if match:
                num = match.group(1)
                clue_text = match.group(2)
                if num in current_section:
                    current_section[num] += " " + clue_text
                else:
                    current_section[num] = clue_text
            else:
                if current_section:
                    keys = list(current_section.keys())
                    if keys:
                        last_key = keys[-1]
                        current_section[last_key] += " " + line

    return across_clues, down_clues
