import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert import ocr


def test_extract_text_and_boxes_parses_decimal_confidence(monkeypatch):
    monkeypatch.setattr(ocr, "_read_rgb_image", lambda image_path: object())
    monkeypatch.setattr(
        ocr,
        "_image_to_data",
        lambda rgb_image: {
            "text": ["Hello", "ignored", "bad"],
            "conf": ["95.5", "-1", "not-a-number"],
            "left": ["10", 20, 30],
            "top": ["11", 21, 31],
            "width": ["12", 22, 32],
            "height": ["13", 23, 33],
        },
    )

    results = ocr.extract_text_and_boxes(
        "rendered/sumbridge2_p001.png",
        source_file="sumbridge2.pdf",
        page_num=1,
        run_id="pilot-run",
    )

    assert len(results) == 1
    word = results[0]
    assert word["id"] == "ocr-sumbridge2-p001-w0000"
    assert word["text"] == "Hello"
    assert word["conf"] == 95.5
    assert word["x"] == 10
    assert word["y"] == 11
    assert word["w"] == 12
    assert word["h"] == 13
    assert word["source_file"] == "sumbridge2.pdf"
    assert word["page_num"] == 1
    assert word["rendered_image_path"] == "rendered/sumbridge2_p001.png"
    assert word["run_id"] == "pilot-run"
    assert word["status"] == "ocr_hypothesis"
    assert word["warnings"] == []


def test_extract_text_and_boxes_filters_invalid_and_low_confidence(monkeypatch):
    monkeypatch.setattr(ocr, "_read_rgb_image", lambda image_path: object())
    monkeypatch.setattr(
        ocr,
        "_image_to_data",
        lambda rgb_image: {
            "text": ["", "Low", "Invalid"],
            "conf": ["90.0", "0", "not-a-number"],
            "left": [1, 2, 3],
            "top": [1, 2, 3],
            "width": [1, 2, 3],
            "height": [1, 2, 3],
        },
    )

    assert ocr.extract_text_and_boxes("rendered/page.png") == []
