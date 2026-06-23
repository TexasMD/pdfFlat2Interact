# Agent Coordination

## Current Base

Branch new work from `origin/main`.

## Active Task

Stage 2 hard-gate page rendering setup after first-pilot source intake verification.

Owner: Codex

Current intent:

- Add rendering-only tooling for the first three hard-gate pages.
- Write rendered page images and render metadata under ignored `data/runs/first_pilot/` paths.
- Do not run OCR, embedded-text extraction, layout detection, reviewer HTML generation, student HTML generation, or conversion in this task.

Current status:

- Source manifest is ready for Stage 1/2.
- The first three hard-gate pages render successfully at 200 DPI.
- Render artifacts are local/ignored:
  - `data/runs/first_pilot/assets/page_images/sumbridge2_p001.png`
  - `data/runs/first_pilot/assets/page_images/sumbridge2_p002.png`
  - `data/runs/first_pilot/assets/page_images/summerbridge_trial_p005.png`
  - `data/runs/first_pilot/json/page_renders.json`

Current files being edited:

- `src/docvert/page_render.py`
- `scripts/render-hard-gate-pages.ps1`
- `tests/test_page_render.py`
- `docs/AGENT_COORDINATION.md`

## Collaboration Updates

Keep Jules and other collaborators aware of edits and intentions before parallel-sensitive work starts. Update this file with:

- active task and owner,
- intended scope,
- files being edited or reserved,
- explicit non-goals and stop conditions.

If work changes scope, update this file before making the broader edit.

## Files Reserved For Active Task

No files are currently reserved for a Jules-owned task.

Jules's interactive review workflow and `repair/jules-restore` work have been merged into `main`. If a new Jules task starts, update this section with the owner, branch, and reserved files before parallel edits begin.

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
