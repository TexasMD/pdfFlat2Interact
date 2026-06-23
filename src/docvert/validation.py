def validate_grid(grid_data, rows, cols, start_issue_idx=1):
    """
    Apply standard crossword validation rules.
    Returns a list of issue dicts, the next available issue ID, and a boolean indicating if blocking issues exist.
    """
    issues = []
    issue_idx = start_issue_idx
    has_blocking_issues = False

    def add_issue(msg, is_blocking=True):
        nonlocal issue_idx, has_blocking_issues
        issues.append({"id": f"issue-{issue_idx}", "message": msg})
        issue_idx += 1
        if is_blocking:
            has_blocking_issues = True

    standard_sizes = [15, 21]
    if rows not in standard_sizes or cols not in standard_sizes:
        add_issue(f"Advisory: Grid size {rows}x{cols} is non-standard (expected 15x15 or 21x21).", is_blocking=False)

    if rows != cols:
        add_issue("Grid is not square.")

    asymmetric_blocks = 0
    for r in range(rows):
        for c in range(cols):
            if grid_data[r][c]["blocked"] != grid_data[rows - 1 - r][cols - 1 - c]["blocked"]:
                asymmetric_blocks += 1

    if asymmetric_blocks > 0:
        add_issue(f"Grid lacks 180-degree rotational symmetry ({asymmetric_blocks} cells mismatch).")

    orphans = 0
    for r in range(rows):
        for c in range(cols):
            if not grid_data[r][c]["blocked"]:
                surrounded = True
                if r > 0 and not grid_data[r-1][c]["blocked"]: surrounded = False
                if r < rows - 1 and not grid_data[r+1][c]["blocked"]: surrounded = False
                if c > 0 and not grid_data[r][c-1]["blocked"]: surrounded = False
                if c < cols - 1 and not grid_data[r][c+1]["blocked"]: surrounded = False

                if surrounded:
                    orphans += 1

    if orphans > 0:
        add_issue(f"Found {orphans} orphaned open cell(s).")

    return issues, issue_idx, has_blocking_issues
