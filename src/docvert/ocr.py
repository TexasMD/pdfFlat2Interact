from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _parse_confidence(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return -1.0


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _id_part(value: str | None, fallback: str) -> str:
    raw = value or fallback
    stem = Path(raw).stem
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower()
    return normalized or fallback


def _page_part(page_num: int | None) -> str:
    return f"p{page_num:03d}" if page_num is not None else "punknown"


def _read_rgb_image(image_path: str):
    import cv2

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _image_to_data(rgb_image):
    import pytesseract

    return pytesseract.image_to_data(rgb_image, output_type=pytesseract.Output.DICT)


def extract_text_and_boxes(
    image_path: str,
    *,
    source_file: str | None = None,
    page_num: int | None = None,
    run_id: str | None = None,
) -> list[dict]:
    """
    Extract text and bounding boxes from an image using pytesseract.
    Returns one traceable OCR-word hypothesis per detected word.
    """
    rgb = _read_rgb_image(image_path)
    data = _image_to_data(rgb)

    extracted = []
    n_boxes = len(data['text'])
    source_part = _id_part(source_file, _id_part(image_path, "image"))
    page_part = _page_part(page_num)

    for i in range(n_boxes):
        text = data['text'][i].strip()
        conf = _parse_confidence(data['conf'][i])

        # Filter out empty text and low-confidence results
        if text and conf > 0:
            word = {
                "id": f"ocr-{source_part}-{page_part}-w{i:04d}",
                "text": text,
                "x": _safe_int(data['left'][i]),
                "y": _safe_int(data['top'][i]),
                "w": _safe_int(data['width'][i]),
                "h": _safe_int(data['height'][i]),
                "conf": conf,
                "source_file": source_file,
                "page_num": page_num,
                "image_path": image_path,
                "rendered_image_path": image_path,
                "run_id": run_id,
                "status": "ocr_hypothesis",
                "warnings": [],
            }
            extracted.append(word)

    return extracted
