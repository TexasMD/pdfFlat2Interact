import json
from pathlib import Path

def merge_review_actions(crossword_json_path: str, review_actions_json_path: str, output_path: str):
    """
    Merge reviewer actions into the main crossword.json.
    Updates cell blocked states and clue placeholders based on 'accept' or 'needs_correction' decisions.
    """
    with open(crossword_json_path, 'r') as f:
        cw_data = json.load(f)

    with open(review_actions_json_path, 'r') as f:
        actions = json.load(f)

    # Build lookup dictionaries for quick access
    cells_by_id = {}
    for row in cw_data.get("grid", []):
        for cell in row:
            if "id" in cell:
                cells_by_id[cell["id"]] = cell

    across_by_id = {}
    for num, clue in cw_data.get("clues", {}).get("across", {}).items():
        if "id" in clue:
            across_by_id[clue["id"]] = clue

    down_by_id = {}
    for num, clue in cw_data.get("clues", {}).get("down", {}).items():
        if "id" in clue:
            down_by_id[clue["id"]] = clue

    # Apply actions
    for target_id, action in actions.items():
        decision = action.get("decision")
        corrected_val = action.get("corrected_value")

        if decision not in ("accept", "needs_correction"):
            continue

        # Try to apply correction
        if corrected_val:
            if target_id in cells_by_id:
                # Cells only care about blocked state right now, maybe numbers later
                if corrected_val.lower() == "blocked":
                    cells_by_id[target_id]["blocked"] = True
                elif corrected_val.lower() == "open":
                    cells_by_id[target_id]["blocked"] = False

            elif target_id in across_by_id:
                across_by_id[target_id]["placeholder"] = corrected_val

            elif target_id in down_by_id:
                down_by_id[target_id]["placeholder"] = corrected_val

            # If it's an issue, we don't 'correct' the issue text itself,
            # we just acknowledge it.

    # Re-evaluate require_review flag?
    # If all issues are 'accept' or 'not_applicable', maybe we can clear it.
    # For now, just save the merged data.

    with open(output_path, 'w') as f:
        json.dump(cw_data, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python merge_corrections.py <crossword.json> <review_actions.json> <output.json>")
        sys.exit(1)
    merge_review_actions(sys.argv[1], sys.argv[2], sys.argv[3])
