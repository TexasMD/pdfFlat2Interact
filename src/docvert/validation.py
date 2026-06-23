INSTRUCTION_MARKERS = (
    "draw", "match", "write", "circle", "underline", "complete", "compare",
    "label", "use", "explain", "read", "find",
)

FACTOID_MARKERS = (
    "earthquake", "earthquakes", "did you know", "fun fact", "fact:",
    "temporarily flow backwards",
)


def _bounds(block: dict) -> tuple[int, int, int, int]:
    x = int(block.get("x", 0))
    y = int(block.get("y", 0))
    w = int(block.get("w", 0))
    h = int(block.get("h", 0))
    return x, y, x + w, y + h


def _block_id(block: dict, index: int) -> str:
    return block.get("id") or f"idx-{index}"


def _union_bbox(blocks: list[dict]) -> dict:
    boxes = [_bounds(block) for block in blocks]
    x1 = min(box[0] for box in boxes)
    y1 = min(box[1] for box in boxes)
    x2 = max(box[2] for box in boxes)
    y2 = max(box[3] for box in boxes)
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def _traceability(blocks: list[dict]) -> dict:
    trace = {}
    for key in ("run_id", "source_file", "page_num", "image_path", "rendered_image_path"):
        for block in blocks:
            if block.get(key) is not None:
                trace[key] = block.get(key)
                break
    trace["block_traceability"] = [
        {
            "id": block.get("id"),
            "source_file": block.get("source_file"),
            "page_num": block.get("page_num"),
            "image_path": block.get("image_path"),
            "rendered_image_path": block.get("rendered_image_path"),
            "run_id": block.get("run_id"),
        }
        for block in blocks
    ]
    return trace


def _make_issue(
    issue_idx: int,
    *,
    issue_type: str,
    message: str,
    blocks: list[dict],
    block_ids: list[str],
    severity: str = "high",
    confidence: str = "medium",
) -> dict:
    issue = {
        "id": f"coherence-{issue_idx}",
        "issue_type": issue_type,
        "severity": severity,
        "confidence": confidence,
        "status": "open",
        "blocks_student_html": severity in {"critical", "high"},
        "validator_stage": "block_coherence",
        "message": message,
        "blocks": block_ids,
        "related_block_ids": block_ids,
        "bbox": _union_bbox(blocks),
        "required_review_action": "Compare affected block(s) with the rendered page image before release.",
        "review_options": [
            "split_instruction_and_factoid",
            "mark_factoid_sidebar",
            "mark_false_positive",
            "block_page_pending_manual_review",
        ],
        "review_suggestion": "",
    }
    issue.update(_traceability(blocks))
    return issue


def _has_instruction_factoid_text_merge(block: dict) -> bool:
    text = block.get("text", "").lower()
    if not text:
        return False
    roles = set(block.get("role_hypotheses", [])) | set(block.get("merged_roles", []))
    explicit_role_mix = {"instruction", "factoid_sidebar"}.issubset(roles)
    has_instruction_marker = any(marker in text for marker in INSTRUCTION_MARKERS)
    has_factoid_marker = any(marker in text for marker in FACTOID_MARKERS)
    return explicit_role_mix or (has_instruction_marker and has_factoid_marker)


def validate_block_coherence(blocks: list[dict]) -> list[dict]:
    """
    Validate that layout blocks form a coherent sequence without impossible merges.
    Expected block dict format: {'id': str, 'role': str, 'x': int, 'y': int, 'w': int, 'h': int, 'text': str}

    Returns traceable issue dictionaries for reviewer QA.
    """
    issues = []
    issue_idx = 1

    # Check 1: Instruction / Factoid text stream contamination, even without bbox overlap.
    for i, block in enumerate(blocks):
        if _has_instruction_factoid_text_merge(block):
            issues.append(_make_issue(
                issue_idx,
                issue_type="possible_layout_block_merge_error",
                message="Block text contains both instruction and factoid/sidebar signals (possible reading-order merge contamination).",
                blocks=[block],
                block_ids=[_block_id(block, i)],
                confidence="high",
            ))
            issue_idx += 1

    # Check 2: Instruction / Factoid Merges (overlapping or nested bounding boxes)
    for i, block_a in enumerate(blocks):
        for j, block_b in enumerate(blocks):
            if i >= j: continue

            # Check for overlap
            xa1, ya1, xa2, ya2 = _bounds(block_a)
            xb1, yb1, xb2, yb2 = _bounds(block_b)

            overlap_x = max(0, min(xa2, xb2) - max(xa1, xb1))
            overlap_y = max(0, min(ya2, yb2) - max(ya1, yb1))
            overlap_area = overlap_x * overlap_y

            if overlap_area > 0:
                # If an instruction overlaps with a factoid, that's a contamination risk
                roles = {block_a.get('role'), block_b.get('role')}
                if "instruction" in roles and "factoid_sidebar" in roles:
                    issues.append(_make_issue(
                        issue_idx,
                        issue_type="possible_layout_block_merge_error",
                        message="Instruction block overlaps with factoid/sidebar block (possible merge contamination).",
                        blocks=[block_a, block_b],
                        block_ids=[_block_id(block_a, i), _block_id(block_b, j)],
                        confidence="high",
                    ))
                    issue_idx += 1

    # Check 3: Impossible Reading Order
    # E.g., an instruction appearing *below* exercise items it supposedly applies to.
    # Assuming blocks are sorted roughly top-to-bottom.
    first_exercise_y = float('inf')
    for block in blocks:
        if block.get('role') == 'exercise_items':
            first_exercise_y = min(first_exercise_y, int(block.get('y', 0)))

    for i, block in enumerate(blocks):
        if block.get('role') == 'instruction':
            if int(block.get('y', 0)) > first_exercise_y:
                issues.append(_make_issue(
                    issue_idx,
                    issue_type="contextual_coherence_failure",
                    message="Instruction block appears below exercise items (impossible reading order).",
                    blocks=[block],
                    block_ids=[_block_id(block, i)],
                    confidence="medium",
                ))
                issue_idx += 1

    return issues
