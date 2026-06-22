# 09 — DOCVERT Source PDF Inventory

Updated: 2026-06-13 UTC  
Status: Active source-corpus intake record  
Project: `docvert`

## 1. Purpose

This file records which original workbook-style source PDFs are actively present in the current `docvert` Project environment, which previously referenced or expected PDFs are still missing, and whether those missing files block the first pilot.

This inventory is an intake/control document only. It does **not** authorize conversion, OCR, layout extraction, or HTML generation.

## 2. Governing interpretation

The artifact map and audit JSON may list source PDFs that were expected, referenced, or previously present in another handoff context. That does **not** prove those PDFs are present in the active Project environment.

Only PDFs actually uploaded and confirmed in this Project should be treated as active source material.

Current active-source rule:

> A PDF is active source material only if it is present in the current Project working environment and intentionally treated as an original workbook/source PDF.

## 3. Confirmed active source PDFs

| Filename | Active status | Page count | Approximate document type | Likely role in pilot / project |
|---|---:|---:|---|---|
| `summerbridge trial.pdf` | Confirmed present | 19 | Summer Bridge workbook trial/sample pages | Selected first-pilot visual-reference regression source; use page 5 for number-line / spatial-layout test. |
| `sumbridge2.pdf` | Confirmed present | 23 | Summer Bridge workbook source PDF | Primary first-pilot regression source: page 1 factoid/sidebar separation; page 2 cents-symbol/money validation. |
| `sumbridge3.pdf` | Confirmed present | 23 | Summer Bridge workbook source PDF | Selected first-pilot source; use page 3 for number families and prefix/suffix grouping. |
| `sumbridge4.pdf` | Confirmed present | 23 | Summer Bridge workbook source PDF | Selected first-pilot source; use page 2 for fraction-table visual dependency. |
| `sumbridge5.pdf` | Confirmed present | 23 | Summer Bridge workbook source PDF | Selected first-pilot source for page 8 text baseline and page 2 crossword/grid stress; also useful for later expansion. |
| `sumbridge6.pdf` | Confirmed present | 23 | Summer Bridge workbook / answer-section source PDF | Later pilot expansion; useful for detecting answer pages and excluding answer-key material from student output. |

## 4. Missing expected source PDFs

| Filename | Current status | Importance | Blocks first pilot? | Recommended next action |
|---|---|---|---:|---|
| `sumbridgetest.pdf` | Missing from active Project environment | Low priority / reference. Previously referenced, but source purpose is not yet important for the first pilot. | No | Do not chase before the first pilot. Request/upload later only if a specific regression or comparison need appears. |
| `sumbridge7.pdf` | Missing from active Project environment | Later batch candidate. Potentially useful for broader corpus coverage after first-pilot gates pass. | No | Defer. Upload before larger batch conversion or coverage testing, not before the first pilot. |
| `sumbridge8.pdf` | Missing from active Project environment | Later batch candidate. Potentially useful for broader corpus coverage after first-pilot gates pass. | No | Defer. Upload before larger batch conversion or coverage testing, not before the first pilot. |

## 5. First-pilot blocking assessment

The first pilot is **not blocked** by the missing expected PDFs.

Reason:

- `sumbridge2.pdf` is present for the two highest-priority regression tests:
  - page 1: factoid/sidebar separation and block coherence,
  - page 2: cents-symbol and money semantic validation.
- `summerbridge trial.pdf` is present for the 19-page trial visual-reference regression:
  - page 5: number-line preservation/recreation.
- `sumbridge3.pdf`, `sumbridge4.pdf`, and `sumbridge5.pdf` are present and selected for additional first-pilot coverage after the three core gates.
- `sumbridge6.pdf` is present but deferred from the first pilot for later answer-page / answer-key exclusion testing.
- `sumbridgetest.pdf`, `sumbridge7.pdf`, and `sumbridge8.pdf` are lower-priority or later-batch files and should not delay the first pilot.

## 6. Recommended first pilot subset

Use a small regression-first subset before any larger batch conversion:

| Order | File | Page | Why this page belongs in the first pilot |
|---:|---|---:|---|
| 1 | `sumbridge2.pdf` | 1 | Canonical block-coherence test: keep the abbreviation instruction separate from the earthquake factoid/sidebar. |
| 2 | `sumbridge2.pdf` | 2 | Canonical cents-symbol test: detect `11¢`, `47¢`, etc. rather than accepting trailing-zero OCR/PDF-text errors. |
| 3 | `summerbridge trial.pdf` | 5 | Canonical visual-reference test: preserve or recreate the number line needed to answer the questions. |
| 4 | `sumbridge2.pdf` | 6 | Vertical arithmetic plus word-bank/fill-in handling. |
| 5 | `sumbridge5.pdf` | 8 | Mostly text-based passage and response-field baseline. |
| 6 | `sumbridge3.pdf` | 3 | Mixed structured layout: number families plus prefixes/suffixes. |
| 7 | `sumbridge4.pdf` | 2 | Fraction-table visual dependency and fraction-layout validation. |
| 8 | `sumbridge5.pdf` | 2 | Crossword/grid and factoid layout stress page. |

## 7. Recommended next action

Next action: obtain explicit human approval or revision of `09_PILOT_PAGE_SELECTION.md`, then proceed only to a **source-intake smoke check**, not conversion.

That smoke check should:

1. record file hashes for the confirmed active source PDFs,
2. preserve page counts,
3. assign stable `source_id` values,
4. create or update a future `source_manifest.json`,
5. avoid OCR, extraction, layout detection, conversion, reviewer HTML, student HTML, and QA webpage generation until explicitly authorized after pilot approval.

Do **not** run conversion yet.  
Do **not** generate student-facing HTML yet.  
Do **not** generate reviewer-facing HTML yet.
