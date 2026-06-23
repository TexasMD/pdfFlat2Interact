import cv2
import pytesseract
from PIL import Image
import numpy as np

def extract_text_and_boxes(image_path: str, source_file: str = "unknown", page_num: int = 0) -> list[dict]:
    """
    Extract text and bounding boxes from an image using pytesseract.
    Returns a list of dictionaries, where each dict represents a detected word or block
    and contains traceability metadata ('source_file', 'page_num', 'image_path')
    alongside 'text', 'x', 'y', 'w', 'h', and 'conf'.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")

    # Convert to RGB (pytesseract expects RGB)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Use pytesseract to get data
    # Output is a dictionary with lists for each column
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)

    extracted = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        try:
            conf = float(data['conf'][i])
        except ValueError:
            conf = -1.0

        # Filter out empty text and low-confidence results
        if text and conf > 0:
            extracted.append({
                "source_file": source_file,
                "page_num": page_num,
                "image_path": image_path,
                "text": text,
                "x": data['left'][i],
                "y": data['top'][i],
                "w": data['width'][i],
                "h": data['height'][i],
                "conf": conf
            })

    return extracted
