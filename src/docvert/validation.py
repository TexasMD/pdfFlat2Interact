def validate_block_coherence(blocks: list[dict]) -> list[dict]:
    """
    Validate that layout blocks form a coherent sequence without impossible merges.
    Expected block dict format: {'id': str, 'role': str, 'x': int, 'y': int, 'w': int, 'h': int, 'text': str}

    Returns a list of issue dictionaries: {'id': str, 'message': str, 'blocks': list[str]}
    """
    issues = []
    issue_idx = 1

    # Check 1: Instruction / Factoid Merges (overlapping or nested bounding boxes)
    for i, block_a in enumerate(blocks):
        for j, block_b in enumerate(blocks):
            if i >= j: continue

            # Check for overlap
            xa1, ya1, xa2, ya2 = block_a['x'], block_a['y'], block_a['x'] + block_a['w'], block_a['y'] + block_a['h']
            xb1, yb1, xb2, yb2 = block_b['x'], block_b['y'], block_b['x'] + block_b['w'], block_b['y'] + block_b['h']

            overlap_x = max(0, min(xa2, xb2) - max(xa1, xb1))
            overlap_y = max(0, min(ya2, yb2) - max(ya1, yb1))
            overlap_area = overlap_x * overlap_y

            if overlap_area > 0:
                # If an instruction overlaps with a factoid, that's a contamination risk
                roles = {block_a.get('role'), block_b.get('role')}
                if "instruction" in roles and "factoid_sidebar" in roles:
                    issues.append({
                        "id": f"coherence-{issue_idx}",
                        "message": "Instruction block overlaps with factoid/sidebar block (possible merge contamination).",
                        "blocks": [block_a.get('id', f"idx-{i}"), block_b.get('id', f"idx-{j}")]
                    })
                    issue_idx += 1

    # Check 2: Impossible Reading Order
    # E.g., an instruction appearing *below* exercise items it supposedly applies to.
    # Assuming blocks are sorted roughly top-to-bottom.
    first_exercise_y = float('inf')
    for block in blocks:
        if block.get('role') == 'exercise_items':
            first_exercise_y = min(first_exercise_y, block['y'])

    for block in blocks:
        if block.get('role') == 'instruction':
            if block['y'] > first_exercise_y:
                issues.append({
                    "id": f"coherence-{issue_idx}",
                    "message": "Instruction block appears below exercise items (impossible reading order).",
                    "blocks": [block.get('id', "unknown")]
                })
                issue_idx += 1

    return issues
