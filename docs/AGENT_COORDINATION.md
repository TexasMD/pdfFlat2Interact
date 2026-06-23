# Agent Coordination

## Current Base

Branch new work from `origin/main`.

## Active Task

Stage 3 embedded PDF text extraction for the first three hard-gate pages.

Owner: Codex

Current intent:

- Add embedded PDF text extraction tooling for the same three hard-gate pages already rendered in Stage 2.
- Use extracted PDF text as a hypothesis only, preserving links to source file, page, and rendered page image.
- Write `data/runs/first_pilot/json/pdf_text.json` as a local/ignored run artifact.
- Do not run OCR, OCR-vs-PDF comparison, layout detection, reviewer HTML generation, student HTML generation, or conversion in this task.

Current status:

- Source manifest is ready for Stage 1/2.
- The first three hard-gate pages render successfully at 200 DPI.
- Embedded PDF text extraction now succeeds for the three rendered hard-gate pages.
- The local/ignored Stage 3 artifact is `data/runs/first_pilot/json/pdf_text.json`.
- Current Stage 3 summary: 3 requested pages, 3 extracted pages, 0 failed pages, 593 embedded-text words.
- Stage 3 carries 3 hard-gate risk flags forward for later issue emission:
  - `possible_layout_block_merge_error` for `sumbridge2.pdf` page 1.
  - `possible_cents_symbol_misread` for `sumbridge2.pdf` page 2.
  - `visual_reference_required_or_helpful` for `summerbridge trial.pdf` page 5.
- Render artifacts are local/ignored:
  - `data/runs/first_pilot/assets/page_images/sumbridge2_p001.png`
  - `data/runs/first_pilot/assets/page_images/sumbridge2_p002.png`
  - `data/runs/first_pilot/assets/page_images/summerbridge_trial_p005.png`
  - `data/runs/first_pilot/json/page_renders.json`
- Stage 4 OCR has not started.

Current files being edited:

- `docs/AGENT_COORDINATION.md`
- `src/docvert/pdf_text.py`
- `scripts/extract-hard-gate-pdf-text.ps1`
- `tests/test_pdf_text.py`

## Collaboration Updates

Keep Jules and other collaborators aware of edits and intentions before parallel-sensitive work starts. Update this file with:

- active task and owner,
- intended scope,
- files being edited or reserved,
- explicit non-goals and stop conditions.

If work changes scope, update this file before making the broader edit.

## Review Interaction Requirement

Any step, panel, issue, correction, page status, or gate that requires human review must provide:

- explicit options the reviewer can choose from;
- a freeform suggestion or notes field;
- saved traceability from the choice and suggestion back to source file, page, rendered page image, and affected issue/block/exercise where applicable.

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
