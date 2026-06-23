# Agent Coordination

## Current Base

Branch repair work from `origin/main`.

## Active Task

PR #2 Option B repair: fix OCR confidence parsing, traceability metadata, layout-role hard-gate heuristics, and block-coherence issue evidence.

Owner: Codex

Current intent:

- Patch the merged PR #2 runtime modules in place instead of reverting them.
- Keep changes targeted to OCR/layout/validation helpers and their tests.
- Preserve source/page/rendered-image traceability in every emitted OCR word, layout block, and validation issue.
- Strengthen tests for decimal Tesseract confidences, factoid/sidebar classification, number-line visual references, and non-overlap merge-risk issue emission.
- Do not expand beyond the approved first-pilot hard gates or generate student HTML.

Current status:

- Jules recommended Option B on PR #2.
- Codex notified Jules that Codex will implement this repair to avoid competing patches.
- Repair is implemented locally on `codex/pr2-option-b-repair`.
- Targeted PR #2 tests pass: `8 passed`.
- Full test suite passes: `19 passed`.

## Files Reserved For Active Task

- `docs/AGENT_COORDINATION.md`
- `src/docvert/ocr.py`
- `src/docvert/layout.py`
- `src/docvert/validation.py`
- `tests/test_ocr.py`
- `tests/test_layout.py`
- `tests/test_validation.py`

Jules and other collaborators should not edit these files until this repair branch is reviewed unless explicitly asked.

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
