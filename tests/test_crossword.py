import os
import json
import tempfile
import pytest
from pathlib import Path
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.crossword import digitize_crossword_image, find_grid, process_grid, assign_clues, render_template
from jinja2.exceptions import TemplateNotFound

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

from docvert.crossword import validate_grid

def test_validate_grid_symmetry():
    # 5x5 grid, asymmetric
    grid_data = [[{"blocked": False} for _ in range(5)] for _ in range(5)]
    grid_data[0][0]["blocked"] = True
    # If symmetric, grid_data[4][4] should be True. Leave it False.

    issues, _ = validate_grid(grid_data, 5, 5)

    # 5x5 is non-standard
    assert any("non-standard" in issue["message"] for issue in issues)
    # Lacks symmetry
    assert any("rotational symmetry" in issue["message"] for issue in issues)

def test_validate_grid_orphans():
    # 5x5 grid
    grid_data = [[{"blocked": False} for _ in range(5)] for _ in range(5)]
    # Create an orphan at (1,1) by blocking (0,1), (2,1), (1,0), (1,2)
    grid_data[0][1]["blocked"] = True
    grid_data[2][1]["blocked"] = True
    grid_data[1][0]["blocked"] = True
    grid_data[1][2]["blocked"] = True

    # Block its symmetric counterparts so it doesn't fail symmetry, just to test orphans independently
    grid_data[4][3]["blocked"] = True
    grid_data[2][3]["blocked"] = True
    grid_data[3][4]["blocked"] = True
    grid_data[3][2]["blocked"] = True

    issues, _ = validate_grid(grid_data, 5, 5)
    assert any("orphaned" in issue["message"] for issue in issues)

def test_digitize_review_targets(temp_dir):
    img_path = temp_dir / "test_cw_review.png"
    generate_synthetic_crossword(img_path, 3, 3, [(1, 1)])

    out_dir = temp_dir / "out_review"
    digitize_crossword_image(str(img_path), str(out_dir), title="Test Review Targets")

    with open(out_dir / "crossword.json") as f:
        data = json.load(f)

    targets = data.get("review_targets", [])
    assert len(targets) > 0

    # Verify cells are targeted
    cell_targets = [t for t in targets if t["type"] == "cell"]
    assert len(cell_targets) == 9 # 3x3
    assert cell_targets[0]["id"] == "cell-r0-c0"

    # Verify clues are targeted
    across_targets = [t for t in targets if t["type"] == "across_clue"]
    assert len(across_targets) == 2
    assert across_targets[0]["id"].startswith("clue-across-")

    # Verify issues are targeted (should have non-standard size issue)
    issue_targets = [t for t in targets if t["type"] == "issue"]
    assert len(issue_targets) > 0
    assert issue_targets[0]["id"].startswith("issue-")

    # Verify review.html contains expected DOM elements
    with open(out_dir / "review.html") as f:
        html = f.read()
        assert 'id="review-panel"' in html
        assert 'id="export-btn"' in html
        assert 'id="import-file"' in html
        assert 'data-id="cell-r0-c0"' in html

def test_render_template_success(tmp_path):
    template_file = tmp_path / "test.html"
    template_file.write_text("Hello {{ name }}!")
    rendered = render_template(str(template_file), {"name": "World"})
    assert rendered == "Hello World!"

def test_render_template_not_found(tmp_path):
    template_file = tmp_path / "nonexistent.html"
    with pytest.raises(TemplateNotFound):
        render_template(str(template_file), {"name": "World"})
