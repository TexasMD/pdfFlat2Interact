# Agent Coordination

## Current Base

- `origin/main` is currently `a8d3df4` (`Merge pull request #6...`).
- Local `main` is fast-forwarded to `origin/main`.
- The PR #6 repair branch `codex/pr2-option-b-repair` has been merged.
- The staged first-pilot branch is `codex/first-pilot-validation` at `0ec71f6`.

## Project Status

Last verified: 2026-06-24.

- PR #6, `[codex] Repair PR2 OCR layout validation helpers`, has been merged into `main`.
- PR #6 merge commit: `a8d3df4`.
- PR #6 included repair commit `b534aa4` plus project-status handoff updates.
- Jules acknowledged the handoff on PR #2 and is not working a competing PR #2 repair.
- PR #2, PR #3, PR #4, PR #5, and PR #6 have been merged into `main`.
- `codex/first-pilot-validation` contains Stage 1 through Stage 4 first-pilot work:
  - Stage 1: source manifest intake.
  - Stage 2: hard-gate page rendering.
  - Stage 3: embedded PDF text extraction.
  - Stage 4: OCR over rendered hard-gate page images.
- Stage 5 OCR-vs-PDF text comparison has not started.
- Clean student HTML has not been generated and remains blocked until reviewer-facing QA and hard-gate validation pass.

## Active Task

Post-PR #6 project status update.

Owner: Codex

Current intent:

- Keep collaborators aligned after the PR #6 merge.
- Make `main` the base for new repair or coordination branches.
- Preserve the staged first-pilot branch until it is deliberately reconciled with updated `main`.
- Do not expand beyond the approved first-pilot hard gates or generate student HTML.

Current status:

- Jules recommended Option B on PR #2, then acknowledged Codex's repair handoff.
- PR #6 implemented the PR #2 Option B repair and has been merged.
- Targeted PR #2 tests pass: `8 passed`.
- Full test suite passes: `19 passed`.

## Next Review Or Decision Step

No PR #6 review remains pending. The next project decision should present these options:

- Proceed with reconciling `codex/first-pilot-validation` onto updated `main`, then start Stage 5.
- Audit the merged PR #6 changes once more before reconciling first-pilot work.
- Ask Jules or another collaborator to review the merged PR #6 repair before Stage 5.
- Pause implementation and revise the project plan/status first.

Any review/decision note must include explicit option selection plus a freeform suggestion/comment field.

## Recommended Next Implementation Step

1. Reconcile `codex/first-pilot-validation` with updated `origin/main` at `a8d3df4`.
2. Resume the staged pipeline at Stage 5: OCR-vs-PDF text comparison for the three first-pilot hard-gate pages.
3. Preserve manifest-backed source/page/rendered-image traceability in every comparison and issue artifact.

## Files Reserved For Active Task

- `docs/AGENT_COORDINATION.md`

No Jules-owned files are currently reserved.

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
