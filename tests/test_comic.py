import pytest
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import cv2
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.comic import process_comic_page

def generate_synthetic_comic(filepath):
    """
    Generate a simple comic panel with a character and a speech balloon.
    """
    img_w, img_h = 400, 400
    img = Image.new('RGB', (img_w, img_h), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a stick figure (the art)
    draw.line((200, 300, 200, 200), fill='blue', width=5) # body
    draw.ellipse((175, 150, 225, 200), outline='blue', width=3) # head
    draw.line((200, 225, 150, 250), fill='blue', width=5) # arm
    draw.line((200, 225, 250, 250), fill='blue', width=5) # arm

    # Draw a speech balloon (ellipse)
    draw.ellipse((50, 20, 300, 100), fill='white', outline='black', width=2)
    # Draw balloon tail pointing to the stick figure
    draw.polygon([(150, 95), (170, 95), (190, 150)], fill='white', outline='black')

    # Add text to the balloon
    # Use default font for wide compatibility in CI, but scale it up
    try:
        font = ImageFont.truetype("LiberationSans-Regular.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    draw.text((100, 40), "Hello World!", fill='black', font=font)

    img.save(filepath)
    return filepath

def test_process_comic_page(tmp_path):
    img_path = tmp_path / "test_comic.png"
    out_dir = tmp_path / "comic_out"

    generate_synthetic_comic(img_path)

    # Mock Tesseract to avoid dependency issues in the test runner
    import pytesseract
    original_to_string = pytesseract.image_to_string
    try:
        def mock_to_string(image, config=''):
            return "Hello World!"
        pytesseract.image_to_string = mock_to_string

        process_comic_page(str(img_path), str(out_dir))

        # Verify outputs
        assert (out_dir / "clean_test_comic.png").exists()
        assert (out_dir / "index.html").exists()
        assert (out_dir / "comic.json").exists()

        with open(out_dir / "comic.json") as f:
            data = json.load(f)

        assert data["metadata"]["width"] == 400
        assert data["metadata"]["height"] == 400
        assert len(data["regions"]) > 0

        # Check that one of the regions has our mocked text
        found_text = False
        for region in data["regions"]:
            if "Hello" in region["text"]:
                found_text = True
                break
        assert found_text, "Failed to find extracted text in JSON output"

    finally:
        pytesseract.image_to_string = original_to_string
