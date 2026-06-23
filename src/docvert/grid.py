import cv2
import numpy as np
import math

def deskew_image(img):
    """Detect skew and rotate image to straighten it."""
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return img

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        if -45 <= angle <= 45:
            angles.append(angle)
        elif angle > 45:
            angles.append(angle - 90)
        elif angle < -45:
            angles.append(angle + 90)

    if not angles:
        return img

    median_angle = np.median(angles)

    if abs(median_angle) < 0.5:
        return img

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

    img = deskew_image(img)

    blurred = cv2.medianBlur(img, 3)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    kernel = np.ones((5,5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    max_area = 0
    best_rect = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
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

    _, thresh = cv2.threshold(grid_img, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    cell_rects = []
    grid_area = w * h
    for cnt in contours:
        cx, cy, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        if cw > 10 and ch > 10 and area < grid_area * 0.9 and 0.5 < cw/ch < 2.0:
            cell_rects.append((cx, cy, cw, ch))

    if not cell_rects:
        return None, None, None

    avg_w = np.median([r[2] for r in cell_rects])
    avg_h = np.median([r[3] for r in cell_rects])

    cols = max(1, int(round(w / avg_w)))
    rows = max(1, int(round(h / avg_h)))

    grid_data = []
    cell_w = w / cols
    cell_h = h / rows

    for r in range(rows):
        row_data = []
        for c in range(cols):
            cy = int(r * cell_h)
            cx = int(c * cell_w)
            ch = int(cell_h)
            cw = int(cell_w)

            margin = 2
            cell_roi = grid_img[cy+margin:cy+ch-margin, cx+margin:cx+cw-margin]

            if cell_roi.size == 0:
                is_blocked = True
            else:
                avg_val = np.mean(cell_roi)
                is_blocked = avg_val < 128

            row_data.append({
                "id": f"cell-r{r}-c{c}",
                "row": r,
                "col": c,
                "blocked": bool(is_blocked),
                "number": None
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

            if c == 0 or grid_data[r][c-1]["blocked"]:
                length = 0
                for i in range(c, cols):
                    if grid_data[r][i]["blocked"]:
                        break
                    length += 1
                if length >= 2:
                    needs_across = True
                    across_clues[str(clue_num)] = {
                        "id": f"clue-across-{clue_num}",
                        "placeholder": f"Across {clue_num}",
                        "length": length,
                        "cell": [r, c]
                    }

            if r == 0 or grid_data[r-1][c]["blocked"]:
                length = 0
                for i in range(r, rows):
                    if grid_data[i][c]["blocked"]:
                        break
                    length += 1
                if length >= 2:
                    needs_down = True
                    down_clues[str(clue_num)] = {
                        "id": f"clue-down-{clue_num}",
                        "placeholder": f"Down {clue_num}",
                        "length": length,
                        "cell": [r, c]
                    }

            if needs_across or needs_down:
                grid_data[r][c]["number"] = clue_num
                clue_num += 1

    return across_clues, down_clues
