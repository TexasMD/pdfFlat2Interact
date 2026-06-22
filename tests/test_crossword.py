import os
import json
import tempfile
import pytest
from pathlib import Path
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.crossword import digitize_crossword_image, find_grid, process_grid, assign_clues

def generate_synthetic_crossword(filepath, rows, cols, blocked_cells):
    """
    Generate a clean synthetic crossword image for testing.
    """
    cell_size = 30
    margin = 20
    img_w = cols * cell_size + 2 * margin
    img_h = rows * cell_size + 2 * margin

    img = Image.new('RGB', (img_w, img_h), color='white')
    draw = ImageDraw.Draw(img)

    # Draw grid
    for r in range(rows):
        for c in range(cols):
            x1 = margin + c * cell_size
            y1 = margin + r * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            fill = 'black' if (r, c) in blocked_cells else 'white'
            draw.rectangle([x1, y1, x2, y2], fill=fill, outline='black', width=2)

    img.save(filepath)
    return filepath

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)

def test_find_process_grid(temp_dir):
    img_path = temp_dir / "test_cw.png"
    # 3x3 grid with center blocked
    generate_synthetic_crossword(img_path, 3, 3, [(1, 1)])

    res = find_grid(str(img_path))
    assert res is not None
    rect, img_gray = res

    rows, cols, grid_data = process_grid(img_gray, rect)
    assert rows == 3
    assert cols == 3

    assert grid_data[1][1]["blocked"] is True
    assert grid_data[0][0]["blocked"] is False

def test_assign_clues():
    grid_data = [
        [{"blocked": False}, {"blocked": False}, {"blocked": False}],
        [{"blocked": False}, {"blocked": True}, {"blocked": False}],
        [{"blocked": False}, {"blocked": False}, {"blocked": False}]
    ]

    across, down = assign_clues(grid_data, 3, 3)

    # 1 across (len 3), 1 down (len 3)
    # 2 down (len 1, invalid), 3 down (len 3)
    # 4 across (len 1, invalid) - wait, r=1, c=0 left is bounds, right is blocked. length 1. Invalid.
    # r=1, c=2. left is blocked. right is bounds. length 1. Invalid.
    # 4 across (r=2, c=0, len 3)

    # Let's trace it exactly.
    # (0,0): Across(len 3) -> 1, Down(len 3) -> 1
    # (0,1): Across(no, left is open), Down(len 1 - valid? no, wait. down len is 1 because next is blocked. Invalid)
    # (0,2): Across(no), Down(len 3) -> 2
    # (1,0): Across(len 1, invalid), Down(no)
    # (1,2): Across(len 1, invalid), Down(no)
    # (2,0): Across(len 3) -> 3, Down(no)

    assert "1" in across
    assert across["1"]["length"] == 3
    assert across["1"]["cell"] == [0, 0]

    assert "1" in down
    assert down["1"]["length"] == 3
    assert down["1"]["cell"] == [0, 0]

    assert "2" in down
    assert down["2"]["length"] == 3
    assert down["2"]["cell"] == [0, 2]

    # 3x3 grid with center block gives us clue #3 at (2,0)
    assert "3" in across
    assert across["3"]["length"] == 3
    assert across["3"]["cell"] == [2, 0]

def test_digitize_full_flow(temp_dir):
    img_path = temp_dir / "test_cw2.png"
    generate_synthetic_crossword(img_path, 3, 3, [(1, 1)])

    out_dir = temp_dir / "out"
    digitize_crossword_image(str(img_path), str(out_dir), title="Test CW")

    assert (out_dir / "crossword.json").exists()
    assert (out_dir / "index.html").exists()
    assert (out_dir / "review.html").exists()
    assert (out_dir / "test_cw2.png").exists()

    with open(out_dir / "crossword.json") as f:
        data = json.load(f)

    assert data["metadata"]["rows"] == 3
    assert data["metadata"]["columns"] == 3
    assert len(data["clues"]["across"]) == 2
    assert len(data["clues"]["down"]) == 2

    with open(out_dir / "index.html") as f:
        html = f.read()
        assert "Test CW" in html
        assert "across-clues" in html
        assert "crossword_json" not in html # template variable replaced

    with open(out_dir / "review.html") as f:
        html = f.read()
        assert "test_cw2.png" in html
