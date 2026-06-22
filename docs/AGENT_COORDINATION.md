# Agent Coordination

## Current Base

Branch new work from `origin/main`.

## Active Task

First-pilot validation setup.

Owner: Codex

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
