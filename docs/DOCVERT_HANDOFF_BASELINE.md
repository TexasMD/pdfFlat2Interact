# DOCVERT_HANDOFF_BASELINE

## Purpose

This file is the durable baseline source for the `docvert` Project.

It distills the prior `summerbridge_handoff_package_final_audited` materials into a concise project-state reference. Treat the prior uploaded files as handoff/audit/specification materials only. They are **not** source workbook PDFs.

## Project identity

`docvert` is a layout-aware, validation-first document AI pipeline for converting workbook-style educational PDFs into accurate, usable, interactive HTML webpages.

The goal is not to create image overlays. The goal is to extract the educational task into clean student-facing interactive webpages while preserving any visual reference required to answer the questions.

## Non-goals and scope guardrails

- This is not a clinical, medical, PHI, legal, billing, or healthcare workflow project.
- Do not treat handoff files as source workbook PDFs.
- Do not run conversion until actual source PDFs are supplied.
- Do not assume prior generated artifacts, pseudocode files, or source PDFs are present unless they are explicitly uploaded into the current working environment.
- Do not hard-code the project as “Summer Bridge.” Summer Bridge examples are seed cases and regression tests, not the identity of the system.

## Core doctrine

The rendered page image is the source of truth.

Embedded PDF text, OCR text, and extracted structure are hypotheses until checked against:

- rendered page image
- embedded PDF text
- OCR output
- layout/block segmentation
- block-role classification
- symbol normalization
- semantic plausibility
- exercise completeness
- visual-reference requirements
- human review when uncertainty remains

Do not silently generate confident garbage. Flag uncertainty.

## Current state

Already established:

- v3 pipeline architecture
- validator and QA design
- known failure mode catalog
- exercise conversion rules
- artifact/output contract
- correction memory seed
- issue schema seed
- block role schema seed
- critical regression tests

Not established in the current Project:

- source workbook PDFs
- confirmed prior latest HTML/ZIP artifacts
- confirmed prior pseudocode/code files
- a proven current v3 implementation run
- OCR/layout engine choices
- reviewer edit/accept/reject UI behavior
- expected-output snapshots for regression tests

## V3 pipeline stages

1. Intake source PDF batch.
2. Render each PDF page as an image.
3. Extract embedded PDF text.
4. Run OCR on rendered page images.
5. Compare embedded text against OCR/visible text.
6. Detect layout blocks and visual regions.
7. Classify block roles.
8. Run layout-aware contextual coherence validation.
9. Extract structured exercises.
10. Normalize symbols.
11. Run semantic plausibility validators.
12. Validate visual-reference requirements.
13. Generate structured JSON.
14. Generate reviewer-facing QA output.
15. Generate student-facing interactive HTML.
16. Generate issue report.
17. Update correction memory.
18. Generate final processing report and package outputs.

## Block roles

Durable block roles:

- `main_instruction`
- `exercise_items`
- `answer_bank`
- `visual_reference`
- `factoid_sidebar`
- `decorative_text`
- `footer`
- `page_header`
- `caption_or_label`
- `external_reference`
- `unknown`

Each block record should preserve text, page, bounding box, source method, visual features, role, confidence, nearby blocks, and coherence notes.

## Layout-aware contextual coherence validation

Short name: block coherence check.

Purpose: decide whether nearby or sequential text blocks logically belong together.

Signals that blocks may be separate:

- different background or shading
- different font weight or size
- boxed or corner placement
- large horizontal/vertical gap
- sidebar/factoid label
- unrelated topic
- declarative trivia adjacent to imperative instruction

Canonical regression case:

- Main instruction: “Draw lines between these words and their abbreviations.”
- Separate factoid/sidebar: “Earthquakes can cause rivers to temporarily flow backwards.”

These must not be merged.

## Known failure modes to preserve

- cents symbol misread or omitted, e.g. `11¢` becoming `110`
- embedded PDF text missing visible problems
- factoid/sidebar text merged into instructions
- visual reference omitted when required
- number lines, maps, graphs, charts, tables, diagrams, and grids lost
- stacked fractions flattened
- vertical arithmetic flattened or corrupted
- matching exercises interleaved across columns
- word banks detached from fill-ins
- decorative/footer text entering student output
- external page references not flagged

## Durable issue types

- `possible_cents_symbol_misread`
- `visual_reference_required_or_helpful`
- `contextual_coherence_failure`
- `possible_layout_block_merge_error`
- `sidebar_factoid_detected`
- `pdf_text_layer_incomplete`
- `numbered_item_count_mismatch`
- `semantic_plausibility_failure`
- `ambiguous_fraction_layout`
- `external_page_reference`
- `missing_visible_item`

Every issue should appear in `json/issues.json`, `review.html`, and `processing_report.md`.

## Correction memory principles

Correction memory stores reusable, conservative rules and human-confirmed corrections.

Preserve these seed patterns:

- In coin/money contexts, trailing-zero values like `110` may indicate a missing cents symbol such as `11¢`.
- Visual-dependency keywords should trigger visual preservation or review.
- Factoid/sidebar text should not be merged into instructions.
- Visual styling differences should create likely block boundaries.
- Stacked fractions should be protected from plain text flattening.

Do not silently correct unless confidence is high and the rendered page image supports the correction. Log all corrections.

## Visual-reference preservation rules

If a prompt depends on a visual, include that visual or flag the page as incomplete.

Required/helpful visuals include:

- maps
- number lines
- graphs
- charts
- tables
- diagrams
- geometry figures
- word-search grids
- crossword grids
- suffix wheels when pedagogically relevant
- fraction bars/tables
- pictures used by the question

Preferred handling:

- recreate simple visuals as SVG
- crop/render complex visuals from the source page
- flag uncertainty for review

## Exercise conversion rules

Convert the learning task, not page decoration.

Typical conversions:

- arithmetic: short answer boxes
- vertical arithmetic: recreated stacked layout or clear equivalent
- fill-in-the-blank: inline input or dropdown
- word bank: dropdowns populated from bank
- multiple choice: radio buttons
- matching: dropdown table or drag/drop
- ordering: number dropdowns
- reading response: passage plus text areas
- writing prompt: textarea
- drawing prompt: canvas or drawing-description area
- number line: SVG/cropped visual plus answer inputs
- map labeling: map image/SVG plus labels/dropdowns
- graph/chart completion: visual plus inputs
- crossword/word search: preserve grid or provide structured equivalent

Factoids are usually omitted from student output or shown as optional notes. They must never be merged into prompts.

## Required batch artifacts

Each conversion batch should produce:

- `index.html` — student-facing interactive worksheet
- `review.html` — reviewer-facing QA interface
- `json/all_pages.json` — full structured extraction
- `json/issues.json` — machine-readable issue report
- `json/correction_memory.json` — reusable correction rules and confirmed corrections
- `json/block_roles.json` — block-level layout/semantic roles
- `processing_report.md` — human-readable processing and QA summary

Package outputs with relative links intact. Do not rely on notebook/session memory.

## Reviewer-facing QA requirements

The review interface should show:

- rendered page image
- extracted embedded text
- OCR text
- detected blocks and bounding boxes
- block roles and confidence
- visual-reference status
- issues and severity
- suggested corrections
- links to underlying JSON records

Student-facing output should be generated from validated structured content, not raw text lines.

## Critical regression tests

Initial durable tests:

1. `sumbridge2.pdf`, page 1 — separate abbreviation instruction from earthquake factoid/sidebar.
2. `sumbridge2.pdf`, page 2 — detect/correct or flag cents-symbol misreads in coin problems.
3. 19-page trial PDF, page 5 — preserve/recreate the number line visual reference.

These examples are regression tests, not project scope limits.

## Contamination warnings

Do not carry forward:

- naive `PDF text -> HTML` extraction as an acceptable pipeline
- image-overlay worksheets as the desired output model
- confidence based only on clean visual appearance
- unlogged auto-corrections
- source-PDF assumptions from audit files
- references to missing artifacts as if they are present
- Summer Bridge-specific naming as global project identity

Specific warning: one audit JSON reported source PDFs as present, while the manifest/checklist stated that original workbook PDFs were not bundled. In the current Project, treat source PDFs as absent unless uploaded.

## Recommended next durable sources

This baseline can stand alone, but the full Project should eventually maintain these focused durable sources:

- `DOCVERT_PIPELINE_V3_SPEC.md`
- `DOCVERT_VALIDATION_AND_QA_RULES.md`
- `DOCVERT_KNOWN_FAILURE_MODES_AND_TESTS.md`
- `DOCVERT_EXERCISE_CONVERSION_RULES.md`
- `DOCVERT_ARTIFACT_CONTRACT.md`
- `DOCVERT_CORRECTION_MEMORY.json`
- `DOCVERT_ISSUE_SCHEMA.json`
- `DOCVERT_BLOCK_ROLE_SCHEMA.json`
- `DOCVERT_SOURCE_PDF_INTAKE_CHECKLIST.md`
- `DOCVERT_SCOPE_AND_CONTAMINATION_GUARDRAILS.md`

## Immediate next project step

Before running any conversion, create or preserve canonical docvert project sources from this baseline. After that, source workbook PDFs can be uploaded and the v3 pipeline can be tested against the critical regression cases.
