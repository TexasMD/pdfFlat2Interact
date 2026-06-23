import cv2
import pytesseract
from PIL import Image
import numpy as np

def extract_text_and_boxes(image_path: str) -> list[dict]:
    """
    Extract text and bounding boxes from an image using pytesseract.
    Returns a list of dictionaries, where each dict represents a detected word or block
    and contains 'text', 'x', 'y', 'w', 'h', and 'conf'.
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
        conf = int(data['conf'][i])

        # Filter out empty text and low-confidence results
        if text and conf > 0:
            extracted.append({
                "text": text,
                "x": data['left'][i],
                "y": data['top'][i],
                "w": data['width'][i],
                "h": data['height'][i],
                "conf": conf
            })

    return extracted
