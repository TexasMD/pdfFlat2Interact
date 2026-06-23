# Agent Coordination

## Current Base

Use `origin/repair/jules-restore` until it is merged. After merge, branch from `origin/main`.

## Active Task

Crossword Clue OCR, Advisory Validation Logic Update, and Correction JSON Merging.

Owner: Jules

## Files Reserved For Active Task

- `src/docvert/crossword.py`
- `src/docvert/merge_corrections.py`
- `tests/test_crossword.py`

Codex should not edit these files until Jules’s PR is reviewed unless explicitly asked.

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
