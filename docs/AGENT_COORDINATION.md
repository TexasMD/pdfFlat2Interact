# Agent Coordination

## Current Base

Use `origin/repair/jules-restore` until it is merged. After merge, branch from `origin/main`.

## Active Task

1. Core extraction modules (OCR, layout, validation) Option B repair (PR #6).
Owner: Codex

2. Update project status and documentation.
Owner: Jules

## Files Reserved For Active Task

**For Codex (PR #6):**
- `src/docvert/layout.py`
- `src/docvert/ocr.py`
- `src/docvert/validation.py`
- `tests/test_layout.py`
- `tests/test_ocr.py`

**For Jules:**
- `docs/10_DECISION_LOG.md`
- `docs/11_BACKLOG.md`
- `docs/AGENT_COORDINATION.md`

## Do Not Delete

- `AGENTS.md`
- `pyproject.toml`
- `docs/`
- `schemas/`
- existing `src/docvert/` files
- existing tests

If a file seems obsolete, mention it in PR notes instead of deleting it.

## Never Commit

- `__pycache__/`
- `.pyc`
- `.pytest_cache/`
- `.venv/`
- PDFs
- scanned images
- generated outputs
- `data/source/`

## Required Before PR

Run:

`.\.venv\Scripts\python.exe -m pytest`

Also check:

`git diff --name-status origin/main...HEAD`

Confirm there are no unexpected deletions or generated files.
