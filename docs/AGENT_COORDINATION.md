# Agent Coordination

## Current Base

- `origin/main` is currently `272adc9` (`Merge pull request #2...`).
- The active repair branch is `codex/pr2-option-b-repair`; use PR #6 for the current pushed head.
- The staged first-pilot branch is `codex/first-pilot-validation` at `0ec71f6`.

## Project Status

Last verified: 2026-06-23.

- PR #6, `[codex] Repair PR2 OCR layout validation helpers`, is open as a draft against `main`.
- PR #6 is currently mergeable and contains repair commit `b534aa4` plus project-status handoff updates.
- PR #6 has no discussion comments yet.
- Jules acknowledged the handoff on PR #2 and is not working a competing PR #2 repair.
- PR #2, PR #3, PR #4, and PR #5 have been merged into `main`.
- Local `main` is stale relative to `origin/main`; refresh before branching from `main`.
- `codex/first-pilot-validation` contains Stage 1 through Stage 4 first-pilot work:
  - Stage 1: source manifest intake.
  - Stage 2: hard-gate page rendering.
  - Stage 3: embedded PDF text extraction.
  - Stage 4: OCR over rendered hard-gate page images.
- Stage 5 OCR-vs-PDF text comparison has not started.
- Clean student HTML has not been generated and remains blocked until reviewer-facing QA and hard-gate validation pass.

## Active Task

Project status update and PR #6 review handoff.

Owner: Codex

Current intent:

- Keep collaborators aligned on the current branch/PR split.
- Keep PR #6 as draft until it is reviewed.
- Do not expand beyond the approved first-pilot hard gates or generate student HTML.

Current status:

- Jules recommended Option B on PR #2.
- Codex notified Jules that Codex will implement this repair to avoid competing patches.
- Repair is implemented and pushed on `codex/pr2-option-b-repair`.
- Draft PR #6 is open for review: `https://github.com/TexasMD/pdfFlat2Interact/pull/6`.
- Targeted PR #2 tests pass: `8 passed`.
- Full test suite passes: `19 passed`.

## Next Review Step

PR #6 needs human review before merge. Reviewer-facing choices must include:

- Approve PR #6 and merge after final test confirmation.
- Request targeted changes on PR #6.
- Keep PR #6 draft and ask for another pass.
- Close PR #6 and choose a different repair strategy.

Review notes must include a freeform suggestion/comment field in the PR review or issue comment.

## Recommended Next Implementation Step

After PR #6 is reviewed and merged or explicitly deferred:

1. Reconcile `codex/first-pilot-validation` with updated `origin/main`.
2. Resume the staged pipeline at Stage 5: OCR-vs-PDF text comparison for the three first-pilot hard-gate pages.
3. Preserve manifest-backed source/page/rendered-image traceability in every comparison and issue artifact.

## Files Reserved For Active Task

- `docs/AGENT_COORDINATION.md`

No Jules-owned files are currently reserved. Avoid competing edits to the PR #6 repair files until PR #6 review is complete unless explicitly asked:

- `src/docvert/ocr.py`
- `src/docvert/layout.py`
- `src/docvert/validation.py`
- `tests/test_ocr.py`
- `tests/test_layout.py`
- `tests/test_validation.py`

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
