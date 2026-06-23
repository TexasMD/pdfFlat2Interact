# Agent Coordination

## Current Base

Branch new work from `origin/main`.

## Active Task

Reviewer interaction contract capture before the next pipeline stage.

Owner: Codex

Current intent:

- Record the review UX requirement that every review-needed step must provide selectable options and a freeform suggestion field.
- Keep Jules and collaborators aware of this requirement before reviewer-facing UI work begins.
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

- `docs/AGENT_COORDINATION.md`
- `docs/07_REVIEW_HTML_SPEC_V4.md`
- `docs/04_VALIDATION_RULES_V4.md`
- `docs/11_BACKLOG.md`

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
