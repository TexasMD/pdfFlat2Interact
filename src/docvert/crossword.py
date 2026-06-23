import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from .grid import find_grid, process_grid, assign_clues
from .ocr import extract_clue_text_from_image
from .validation import validate_grid
from .html import render_template

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
    issue_idx = 1
    require_review_computed = False

    grid_res = find_grid(image_path)
    if not grid_res:
        issues.append({"id": f"issue-{issue_idx}", "message": "Failed to detect outer crossword grid bounding box."})
        issue_idx += 1
        require_review_computed = True
        grid_data = []
        rows, cols = 0, 0
        across_clues, down_clues = {}, {}
    else:
        best_rect, img_gray = grid_res
        process_res = process_grid(img_gray, best_rect)
        if not process_res or process_res[0] is None:
            issues.append({"id": f"issue-{issue_idx}", "message": "Failed to segment grid cells."})
            issue_idx += 1
            require_review_computed = True
            grid_data = []
            rows, cols = 0, 0
            across_clues, down_clues = {}, {}
        else:
            rows, cols, grid_data = process_res
            across_clues, down_clues = assign_clues(grid_data, rows, cols)

            # OCR Clue Extraction
            ocr_across, ocr_down = extract_clue_text_from_image(img_gray, best_rect)

            # Apply OCR text to assigned clues
            for num, clue in across_clues.items():
                if num in ocr_across:
                    clue["placeholder"] = ocr_across[num]
            for num, clue in down_clues.items():
                if num in ocr_down:
                    clue["placeholder"] = ocr_down[num]

            # Validation
            validation_issues, issue_idx, has_blocking = validate_grid(grid_data, rows, cols, issue_idx)
            if validation_issues:
                issues.extend(validation_issues)
                if has_blocking:
                    require_review_computed = True

            if not across_clues and not down_clues:
                issues.append({"id": f"issue-{issue_idx}", "message": "No clues found in the grid."})
                issue_idx += 1
                require_review_computed = True

    if require_review_computed:
        require_review = True

    # Build review targets
    review_targets = []

    # Add cells
    for r in range(rows):
        for c in range(cols):
            cell = grid_data[r][c]
            review_targets.append({
                "id": cell["id"],
                "type": "cell",
                "label": f"Cell R{r} C{c}",
                "current_value": "blocked" if cell["blocked"] else ("open" + (f" ({cell['number']})" if cell["number"] else "")),
                "source_coordinates": [r, c]
            })

    # Add clues
    for num, clue in across_clues.items():
        review_targets.append({
            "id": clue["id"],
            "type": "across_clue",
            "label": f"Across {num}",
            "current_value": clue["placeholder"],
            "source_coordinates": clue["cell"]
        })

    for num, clue in down_clues.items():
        review_targets.append({
            "id": clue["id"],
            "type": "down_clue",
            "label": f"Down {num}",
            "current_value": clue["placeholder"],
            "source_coordinates": clue["cell"]
        })

    # Add issues
    for issue in issues:
        review_targets.append({
            "id": issue["id"],
            "type": "issue",
            "label": f"Issue: {issue['id']}",
            "current_value": issue["message"]
        })

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
        "review_required": require_review,
        "review_targets": review_targets
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
        "clues": cw_data["clues"],
        "issues": cw_data["issues"],
        "review_targets": cw_data.get("review_targets", []),
        "json_str": json.dumps(cw_data, indent=2)
    }
    review_html = render_template(template_dir / "review.html", review_context)
    with open(out_dir / "review.html", "w") as f:
        f.write(review_html)
