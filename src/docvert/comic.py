import cv2
import numpy as np
import pytesseract
import json
from pathlib import Path
import shutil
from datetime import datetime, timezone

from .html import render_template

def detect_text_regions(img):
    """
    Heuristic text region detector for POC.
    Note: As defined in specs, simple cv2 contouring is brittle and often masks artwork.
    This POC tightens the bounding boxes to mitigate artwork destruction before an ML model is introduced.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding to be more precise about what constitutes "text"
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Use a smaller dilation kernel to prevent the mask from bleeding into panel borders
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    region_id = 1
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        # Stricter filtering to avoid masking non-text material
        # The synthetic test text creates a bounding box area roughly 110x25 = 2750.
        if 20 < area < (img.shape[0] * img.shape[1] * 0.5) and w > 8 and h > 8:

            # Simple heuristic classification
            text_type = "speech" if w/h < 3 else "narrative"

            regions.append({
                "id": f"comic-text-{region_id}",
                "bbox": [x, y, w, h],
                "type": text_type,
                "text": ""
            })
            region_id += 1

    return regions

def process_comic_page(image_path: str, output_dir: str):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    img_name = Path(image_path).name

    # 1. Detect text regions
    regions = detect_text_regions(img)

    # Create mask for inpainting
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    # 2. Extract OCR and build mask
    for region in regions:
        x, y, w, h = region["bbox"]

        # Tightly constrain ROI to prevent masking artwork
        padding = 2
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.shape[1], x + w + padding)
        y2 = min(img.shape[0], y + h + padding)

        roi = img[y1:y2, x1:x2]

        # OCR
        text = pytesseract.image_to_string(roi, config='--psm 6').strip()
        region["text"] = text

        # Mask strictly the detected text pixels within the ROI to avoid destroying backgrounds
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, text_mask_roi = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY_INV)

        # Combine the precise text pixel mask into the global mask
        mask[y1:y2, x1:x2] = cv2.bitwise_or(mask[y1:y2, x1:x2], text_mask_roi)

    # 3. Inpaint to erase text
    clean_img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

    clean_img_name = "clean_" + img_name
    clean_img_path = out_dir / clean_img_name
    cv2.imwrite(str(clean_img_path), clean_img)

    # 4. Generate JSON
    comic_data = {
        "metadata": {
            "source_image": img_name,
            "clean_image": clean_img_name,
            "width": img.shape[1],
            "height": img.shape[0],
            "generated_at": datetime.now(timezone.utc).isoformat()
        },
        "regions": regions
    }

    with open(out_dir / "comic.json", "w") as f:
        json.dump(comic_data, f, indent=2)

    # 5. Generate interactive HTML
    template_dir = Path(__file__).parent / "templates"
    context = {
        "title": "Comic Interactive View",
        "data": comic_data
    }
    html = render_template(template_dir / "comic.html", context)
    with open(out_dir / "index.html", "w") as f:
        f.write(html)
