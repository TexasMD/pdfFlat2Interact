import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.layout import detect_layout_blocks, classify_block_role

def generate_blocks_image(filepath):
    """Generate an image with distinct dark rectangles simulating text blocks."""
    img = Image.new('L', (1000, 1000), color=255) # White background
    draw = ImageDraw.Draw(img)

    # Draw block 1 (Instruction like)
    draw.rectangle([100, 100, 900, 150], fill=0)

    # Draw block 2 (Exercise items like)
    draw.rectangle([150, 300, 450, 600], fill=0)

    # Draw block 3 (Factoid/Sidebar like)
    draw.rectangle([750, 200, 950, 500], fill=0)

    img.save(filepath)
    return filepath

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)

def test_detect_layout_blocks(temp_dir):
    img_path = temp_dir / "test_layout.png"
    generate_blocks_image(img_path)

    blocks = detect_layout_blocks(
        str(img_path),
        source_file="sumbridge2.pdf",
        page_num=1,
        run_id="pilot-run",
    )

    # We drew 3 distinct blocks, dilation might merge things if they were close,
    # but here they are far apart.
    assert len(blocks) == 3
    for block in blocks:
        assert block["id"].startswith("layout-sumbridge2-p001-b")
        assert block["source_file"] == "sumbridge2.pdf"
        assert block["page_num"] == 1
        assert block["rendered_image_path"] == str(img_path)
        assert block["run_id"] == "pilot-run"
        assert block["status"] == "layout_hypothesis"

def test_classify_block_role():
    # Test Instruction
    inst_block = {
        'x': 100,
        'y': 100,
        'w': 800,
        'h': 50,
        'text': 'Draw lines between these words and their abbreviations.',
        'page_width': 1000,
        'page_height': 1000,
    }
    assert classify_block_role(inst_block) == "instruction"

    # Test Factoid
    factoid_block = {'x': 800, 'y': 200, 'w': 150, 'h': 300, 'page_width': 1000, 'page_height': 1000}
    assert classify_block_role(factoid_block) == "factoid_sidebar"

    # Test top-corner factoid from the first hard gate.
    top_factoid_block = {'x': 780, 'y': 40, 'w': 170, 'h': 220, 'page_width': 1000, 'page_height': 1000}
    assert classify_block_role(top_factoid_block) == "factoid_sidebar"

    # Test Footer
    footer_block = {'x': 100, 'y': 950, 'w': 800, 'h': 20, 'page_width': 1000, 'page_height': 1000}
    assert classify_block_role(footer_block) == "footer"

    # Test Number Line / visual reference near top of page.
    number_line_block = {'x': 100, 'y': 120, 'w': 800, 'h': 40, 'page_width': 1000, 'page_height': 1000}
    assert classify_block_role(number_line_block) == "visual_reference"

    # Test Exercise Items
    exercise_block = {'x': 200, 'y': 400, 'w': 500, 'h': 200, 'text': '1. first item 2. second item', 'page_width': 1000, 'page_height': 1000}
    assert classify_block_role(exercise_block) == "exercise_items"
