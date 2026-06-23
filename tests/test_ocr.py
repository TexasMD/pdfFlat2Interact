import pytest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.ocr import extract_text_and_boxes

def generate_text_image(filepath, text):
    """Generate a clean synthetic image with text for OCR testing."""
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    # Using default font. It might be small but tesseract usually handles simple text.
    draw.text((10, 10), text, fill='black')
    img.save(filepath)
    return filepath

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)

def test_extract_text_and_boxes(temp_dir):
    img_path = temp_dir / "test_ocr.png"
    test_string = "Hello OCR"
    generate_text_image(img_path, test_string)

    results = extract_text_and_boxes(str(img_path))

    # Check if we got results
    assert len(results) > 0

    # Check if our test string is in the extracted text (case insensitive, might be split into words)
    combined_text = " ".join([r["text"] for r in results]).lower()
    assert "hello" in combined_text or "ocr" in combined_text

    # Check bounding box structure
    for r in results:
        assert "x" in r
        assert "y" in r
        assert "w" in r
        assert "h" in r
        assert "conf" in r
