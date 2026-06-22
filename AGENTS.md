# AGENTS.md — docvert

## Project identity

docvert is a layout-aware, validation-first pipeline for converting workbook-style educational PDFs into accurate interactive student-facing HTML, with reviewer-facing QA generated first.

The rendered page image is the source of truth. OCR text, embedded PDF text, layout blocks, extracted questions, normalized symbols, and generated HTML are hypotheses until validated.

## Hard rules

- Do not implement naive PDF-text-to-HTML conversion.
- Do not treat handoff, spec, audit, or generated files as source PDFs.
- Do not treat generated HTML or prior run outputs as proof of correctness.
- Do not release clean student HTML from unresolved critical issues or unreviewed major task-bearing issues.
- Preserve traceability from every page, block, exercise, issue, visual reference, and rendered field back to source file, page, and rendered page image.
- Reviewer-facing QA comes before clean student release.
- Every uncertain extraction must become an issue, not a silent assumption.
- Required visuals such as number lines, maps, tables, graphs, charts, diagrams, grids, crossword regions, and word-search regions must be preserved, recreated, or block release.

## First pilot only

Do not expand beyond the approved first-pilot pages until the hard regression gates pass:

1. `sumbridge2.pdf` page 1 — factoid/sidebar separation.
2. `sumbridge2.pdf` page 2 — cents-symbol/money validation.
3. `summerbridge trial.pdf` page 5 — number-line visual-reference preservation.

## Implementation order

1. Source manifest and intake validation.
2. Page rendering.
3. Embedded PDF text extraction.
4. OCR.
5. OCR-vs-PDF-text comparison.
6. Layout block detection.
7. Block role classification.
8. Issue emission.
9. Reviewer QA.
10. Gated student HTML.
