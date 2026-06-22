import os
import json
from pathlib import Path
from datetime import datetime, timezone
import cv2
import numpy as np
import shutil

import math

def deskew_image(img):
    """Detect skew and rotate image to straighten it."""
    # Use Canny edge detection
    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    # Find lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return img

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        # We only care about lines that are roughly horizontal or vertical
        # Normalize angle to -45 to 45 degrees
        if -45 <= angle <= 45:
            angles.append(angle)
        elif angle > 45:
            angles.append(angle - 90)
        elif angle < -45:
            angles.append(angle + 90)

    if not angles:
        return img

    median_angle = np.median(angles)

    # If the skew is very small, don't bother rotating
    if abs(median_angle) < 0.5:
        return img

    # Rotate image
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def find_grid(image_path: str):
    """
    Detect the outer bounding box of the crossword grid.
    Returns (x, y, w, h) of the outer grid, or None if not confidently found.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    # Deskew
    img = deskew_image(img)

    # Noise reduction and binarize
    blurred = cv2.medianBlur(img, 3)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Morphology to close small gaps
    kernel = np.ones((5,5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Assume largest contour that's roughly square/rectangular is the grid
    max_area = 0
    best_rect = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        # Crosswords have a decent size. For our synthetic 3x3 test, area is ~8100.
        if area > max_area and area > 1000:
            max_area = area
            best_rect = (x, y, w, h)

    return best_rect, img

def process_grid(img_gray, grid_rect):
    """
    Extract cells from the grid, compute rows/columns, and classify as open/blocked.
    """
    x, y, w, h = grid_rect
    grid_img = img_gray[y:y+h, x:x+w]

    # Binarize the grid image
    _, thresh = cv2.threshold(grid_img, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    cell_rects = []
    # Filter contours to find roughly square cells
    grid_area = w * h
    for cnt in contours:
        cx, cy, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        # A cell should be a fraction of the grid, e.g., 1/15th to 1/2nd in dimension
        if cw > 10 and ch > 10 and area < grid_area * 0.9 and 0.5 < cw/ch < 2.0:
            cell_rects.append((cx, cy, cw, ch))

    if not cell_rects:
        return None, None, None

    # Estimate average cell width and height
    avg_w = np.median([r[2] for r in cell_rects])
    avg_h = np.median([r[3] for r in cell_rects])

    cols = max(1, int(round(w / avg_w)))
    rows = max(1, int(round(h / avg_h)))

    # Construct a 2D array for the grid
    grid_data = []
    cell_w = w / cols
    cell_h = h / rows

    for r in range(rows):
        row_data = []
        for c in range(cols):
            # Extract cell region
            cy = int(r * cell_h)
            cx = int(c * cell_w)
            ch = int(cell_h)
            cw = int(cell_w)

            # shrink slightly to avoid border lines
            margin = 2
            cell_roi = grid_img[cy+margin:cy+ch-margin, cx+margin:cx+cw-margin]

            if cell_roi.size == 0:
                is_blocked = True
            else:
                # Average pixel value (close to 0 is black)
                avg_val = np.mean(cell_roi)
                is_blocked = avg_val < 128 # mostly dark

            row_data.append({
                "row": r,
                "col": c,
                "blocked": bool(is_blocked),
                "number": None # To be assigned later
            })
        grid_data.append(row_data)

    return rows, cols, grid_data

def assign_clues(grid_data, rows, cols):
    """
    Assign clue numbers from top-left to bottom-right.
    Infer valid Across/Down starts and validate they have at least 2 cells.
    """
    clue_num = 1
    across_clues = {}
    down_clues = {}

    for r in range(rows):
        for c in range(cols):
            if grid_data[r][c]["blocked"]:
                continue

            needs_across = False
            needs_down = False

            # Check Across
            if c == 0 or grid_data[r][c-1]["blocked"]:
                length = 0
                for i in range(c, cols):
                    if grid_data[r][i]["blocked"]:
                        break
                    length += 1
                if length >= 2:
                    needs_across = True
                    across_clues[str(clue_num)] = {
                        "placeholder": f"Across {clue_num}",
                        "length": length,
                        "cell": [r, c]
                    }

            # Check Down
            if r == 0 or grid_data[r-1][c]["blocked"]:
                length = 0
                for i in range(r, rows):
                    if grid_data[i][c]["blocked"]:
                        break
                    length += 1
                if length >= 2:
                    needs_down = True
                    down_clues[str(clue_num)] = {
                        "placeholder": f"Down {clue_num}",
                        "length": length,
                        "cell": [r, c]
                    }

            if needs_across or needs_down:
                grid_data[r][c]["number"] = clue_num
                clue_num += 1

    return across_clues, down_clues

from jinja2 import Environment, FileSystemLoader

def validate_grid(grid_data, rows, cols):
    """
    Apply standard crossword validation rules.
    Returns a list of issue strings.
    """
    issues = []

    # Standard dimensions
    standard_sizes = [15, 21]
    if rows not in standard_sizes or cols not in standard_sizes:
        issues.append(f"Grid size {rows}x{cols} is non-standard (expected 15x15 or 21x21).")

    if rows != cols:
        issues.append("Grid is not square.")

    # Rotational symmetry
    asymmetric_blocks = 0
    for r in range(rows):
        for c in range(cols):
            if grid_data[r][c]["blocked"] != grid_data[rows - 1 - r][cols - 1 - c]["blocked"]:
                asymmetric_blocks += 1

    if asymmetric_blocks > 0:
        issues.append(f"Grid lacks 180-degree rotational symmetry ({asymmetric_blocks} cells mismatch).")

    # Orphaned cells (open cell completely surrounded by boundaries/blocks)
    orphans = 0
    for r in range(rows):
        for c in range(cols):
            if not grid_data[r][c]["blocked"]:
                surrounded = True
                # Check neighbors (up, down, left, right)
                if r > 0 and not grid_data[r-1][c]["blocked"]: surrounded = False
                if r < rows - 1 and not grid_data[r+1][c]["blocked"]: surrounded = False
                if c > 0 and not grid_data[r][c-1]["blocked"]: surrounded = False
                if c < cols - 1 and not grid_data[r][c+1]["blocked"]: surrounded = False

                if surrounded:
                    orphans += 1

    if orphans > 0:
        issues.append(f"Found {orphans} orphaned open cell(s).")

    return issues

def render_template(template_path, context):
    """Render a template using Jinja2."""
    template_dir = Path(template_path).parent
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(Path(template_path).name)
    return template.render(context)

def digitize_crossword_image(image_path: str, output_dir: str, *, title: str = None, require_review: bool = True):
    """
    Digitize a clean/synthetic crossword image.
    Generates a crossword.json, index.html, and review.html.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img_name = Path(image_path).name
    # Copy image to output dir for review
    shutil.copy(image_path, out_dir / img_name)

    issues = []

    grid_res = find_grid(image_path)
    if not grid_res:
        issues.append("Failed to detect outer crossword grid bounding box.")
        require_review = True
        grid_data = []
        rows, cols = 0, 0
        across_clues, down_clues = {}, {}
    else:
        best_rect, img_gray = grid_res
        process_res = process_grid(img_gray, best_rect)
        if not process_res or process_res[0] is None:
            issues.append("Failed to segment grid cells.")
            require_review = True
            grid_data = []
            rows, cols = 0, 0
            across_clues, down_clues = {}, {}
        else:
            rows, cols, grid_data = process_res
            across_clues, down_clues = assign_clues(grid_data, rows, cols)

            # Validation
            validation_issues = validate_grid(grid_data, rows, cols)
            if validation_issues:
                issues.extend(validation_issues)
                require_review = True

            if not across_clues and not down_clues:
                issues.append("No clues found in the grid.")
                require_review = True

    cw_data = {
        "metadata": {
            "title": title or "Untitled Crossword",
            "source_image": img_name,
            "rows": rows,
            "columns": cols,
            "generated_at": datetime.now(timezone.utc).isoformat()
        },
        "grid": grid_data,
        "clues": {
            "across": across_clues,
            "down": down_clues
        },
        "issues": issues,
        "review_required": require_review
    }

    # Emit JSON
    json_path = out_dir / "crossword.json"
    with open(json_path, "w") as f:
        json.dump(cw_data, f, indent=2)

    # Templates dir
    template_dir = Path(__file__).parent / "templates"

    # Emit index.html
    index_context = {
        "title": cw_data["metadata"]["title"] or "Untitled Crossword",
        "crossword_json": json.dumps(cw_data)
    }
    index_html = render_template(template_dir / "index.html", index_context)
    with open(out_dir / "index.html", "w") as f:
        f.write(index_html)

    # Emit review.html
    review_context = {
        "title": cw_data["metadata"]["title"] or "Untitled Crossword",
        "review_required": cw_data["review_required"],
        "image_filename": img_name,
        "metadata": cw_data["metadata"],
        "grid": cw_data["grid"],
        "issues": cw_data["issues"],
        "json_str": json.dumps(cw_data, indent=2)
    }
    review_html = render_template(template_dir / "review.html", review_context)
    with open(out_dir / "review.html", "w") as f:
        f.write(review_html)
