# 10 — DOCVERT Decision Log

Updated: 2026-06-13 UTC
Status: Active Control Tower source
Project: `docvert`

## 1. Decision status vocabulary

- **Accepted** — governing decision for current project work.
- **Deferred** — not decided yet; do not build assumptions around it.
- **Rejected** — explicitly not part of the project direction.
- **Superseded** — was used or considered earlier, but no longer governs.
- **Needs review** — plausible but requires user/engineering confirmation.

## 2. Accepted decisions

| ID | Decision | Rationale | Consequence |
|---|---|---|---|
| D-001 | `docvert` is a layout-aware, validation-first educational document conversion pipeline. | Linear extraction failed on workbook pages with sidebars, symbols, visuals, and spatial tasks. | All implementation must preserve layout and validation before student output. |
| D-002 | The rendered page image is the source of truth. | Embedded text and OCR are both fallible. | Extraction results remain hypotheses until checked against rendered page images. |
| D-003 | The project output is clean extracted interactive educational content, not an image overlay. | Image overlays are brittle and do not satisfy the extraction goal. | Student output must be built from structured exercise data, with visuals preserved when needed. |
| D-004 | Reviewer-facing QA output is required before or alongside student output. | Validation is the core value, not cosmetic conversion. | Future runs must include reviewer artifacts, issue reports, block roles, and processing reports. |
| D-005 | Block-aware extraction is required. | Sidebars, columns, tables, and factoids cannot be safely handled as linear text. | Each page needs block detection, roles, confidence, and coherence notes. |
| D-006 | Layout-aware contextual coherence validation is a core stage. | The canonical failure is merging instructions with unrelated factoids. | Nearby blocks must be tested for whether they logically belong together. |
| D-007 | Factoids and decorative sidebars must not be merged into main prompts. | This corrupts the task while appearing plausible. | Factoids default to `factoid_sidebar`; omit or show only as optional notes. |
| D-008 | Required visual references must be preserved, recreated, or flagged incomplete. | Number lines, maps, tables, graphs, diagrams, and grids can be necessary to answer. | Visual-reference validation is required before release. |
| D-009 | Symbol corrections must be conservative and logged. | Silent correction creates hidden errors. | Correct only with high confidence and rendered-image support; otherwise flag. |
| D-010 | Issue reporting is a first-class output. | Uncertainty must surface for human review. | Every suspicious item belongs in issue records, reviewer QA, and processing report. |
| D-011 | Correction memory stores reusable rules and human-confirmed corrections. | Repeat errors should not require repeat manual fixes. | Future pipelines load memory conservatively and update it after review. |
| D-012 | Handoff/specification files are not source workbook PDFs. | The handoff package preserved project state, not the source archive. | Treat source PDFs as absent unless uploaded or confirmed in the active environment. |
| D-013 | Summer Bridge examples are seed cases and regression tests, not system identity. | `docvert` is broader than one workbook series. | Do not hard-code project logic around Summer Bridge. |
| D-014 | Control Tower chats manage structure and decisions, not conversion runs. | Mixing governance and conversion causes artifact contamination. | No webpage code and no source-PDF conversion in this chat unless mode changes explicitly. |
| D-015 | Student output should be generated from validated structured JSON, not raw text lines. | Raw lines preserve extraction errors. | Structured extraction artifacts become the source for rendering. |
| D-016 | Package outputs must not depend on notebook/session memory. | Outputs need to be inspectable and portable. | Use relative links and explicit files. |
| D-017 | Only uploaded and confirmed source PDFs are active ground truth for conversion planning. | Artifact maps, audit JSON, handoff docs, snippets, and prior artifacts can reference absent PDFs. | A filename reference is not proof of source availability. |
| D-018 | `09_PILOT_PAGE_SELECTION.md` is the durable first-pilot page-selection source, pending approval. | Pilot scope must be explicit before implementation. | No OCR, extraction, layout detection, conversion, reviewer HTML, or student HTML is authorized until approval. |
| D-019 | `summerbridge trial.pdf` page 5 is included in the first pilot. | The active 19-page trial PDF preserves the number-line/spatial-layout regression. | The first pilot must include page 5 unless the pilot is revised. |
| D-020 | The six new V4 artifacts are durable Project sources for the first extraction pilot. | The issue taxonomy, validation rules, correction-memory design, reviewer HTML spec, and student HTML spec now guide implementation. | Future implementation must read and honor `03_ISSUE_TAXONOMY_V4.md`, `04_VALIDATION_RULES_V4.md`, `05_CORRECTION_MEMORY_SCHEMA_V4.json`, `06_CORRECTION_MEMORY_RULES_V4.md`, `07_REVIEW_HTML_SPEC_V4.md`, and `08_STUDENT_HTML_SPEC_V4.md`. |
| D-021 | Reviewer-facing QA is the first rendering target for the extraction pilot; clean student HTML remains gated. | The reviewer page exposes source image, OCR/PDF text, block roles, issues, visual references, and correction-memory suggestions. | Student-facing output must not be released from unresolved critical issues, unreviewed major task-bearing issues, missing required visuals, or absent reviewer evidence. |
| D-022 | The first extraction pilot definition of done is governed by the pilot page selection plus V4 issue, validation, correction-memory, reviewer, and student-output specs. | The pilot now has both selected pages and implementation-quality acceptance gates. | The next implementation prompt should treat these sources as required acceptance criteria. |
| D-023 | Phase 2 OCR, layout, and validation modules must be patched in place to preserve `AGENTS.md` traceability. | PR #2 introduced core modules lacking manifest traceability and had confidence parsing bugs. "Option B" was chosen to patch them in place. | All OCR and layout artifacts must strictly carry `source_file`, `page_num`, and dynamic `id` tags; Codex owns PR #6 for this repair. |

## 3. Source corpus decision

| Filename | Current status | Priority | Blocks first pilot? | Decision consequence |
|---|---|---|---:|---|
| `summerbridge trial.pdf` | Uploaded/confirmed active | First-pilot visual-reference regression source | Yes | Include page 5. |
| `sumbridge2.pdf` | Uploaded/confirmed active | Highest-priority pilot/regression source | Yes | Include pages 1, 2, and 6. |
| `sumbridge3.pdf` | Uploaded/confirmed active | First-pilot selected source | Yes | Include page 3. |
| `sumbridge4.pdf` | Uploaded/confirmed active | First-pilot selected source | Yes | Include page 2. |
| `sumbridge5.pdf` | Uploaded/confirmed active | First-pilot selected source plus later expansion candidate | Yes | Include pages 8 and 2. |
| `sumbridge6.pdf` | Uploaded/confirmed active | Later answer-key exclusion candidate | No | Defer from first pilot. |
| `sumbridgetest.pdf` | Missing expected PDF | Lower-priority/reference | No | Do not block first pilot. |
| `sumbridge7.pdf` | Missing expected PDF | Later batch candidate | No | Defer until broader batch testing. |
| `sumbridge8.pdf` | Missing expected PDF | Later batch candidate | No | Defer until broader batch testing. |

## 4. V4 specification artifact decision

| Artifact | Governing use |
|---|---|
| `03_ISSUE_TAXONOMY_V4.md` | Issue vocabulary, severity, blocking behavior, and required issue records. |
| `04_VALIDATION_RULES_V4.md` | Validation order, hard gates, page/question checks, and release categories. |
| `05_CORRECTION_MEMORY_SCHEMA_V4.json` | Correction-memory structure for reusable rules and reviewer decisions. |
| `06_CORRECTION_MEMORY_RULES_V4.md` | Correction creation/reuse rules and overbreadth controls. |
| `07_REVIEW_HTML_SPEC_V4.md` | Reviewer-facing QA page contract and evidence display requirements. |
| `08_STUDENT_HTML_SPEC_V4.md` | Student-facing HTML release gates and rendering requirements. |

Decision consequence: these are durable Project sources and acceptance criteria. They are not generated outputs and do not authorize conversion by themselves.

## 5. Superseded decisions and assumptions

| ID | Superseded item | Replaced by | Reason |
|---|---|---|---|
| S-001 | Naive `PDF text -> HTML` conversion is sufficient. | Rendered-image + OCR + layout + validation pipeline. | Text extraction missed content, corrupted symbols, and merged unrelated blocks. |
| S-002 | Clean-looking generated pages are acceptable evidence of correctness. | Validation-first QA against source page images. | Visually tidy output can still be educationally wrong. |
| S-003 | Embedded PDF text can be trusted as complete. | OCR/visible-text comparison and issue reporting. | Embedded text can omit visible problems or corrupt symbols. |
| S-004 | Factoids can be read inline with prompts if extracted that way. | Block-role classification and coherence validation. | This can turn unrelated trivia into bogus instructions. |
| S-005 | Source PDFs are included because an audit JSON names them. | Source PDFs are active only if uploaded/confirmed. | Prior references are not active source truth. |
| S-006 | Student HTML can be the first renderer target. | Reviewer HTML is the first QA rendering target. | Student HTML must not hide unresolved extraction uncertainty. |

## 6. Rejected approaches

| ID | Rejected approach | Reason |
|---|---|---|
| R-001 | Image-only overlay worksheets as the primary output model. | Does not produce clean extracted educational content and is hard to validate semantically. |
| R-002 | Silent auto-correction of extracted text. | Creates hidden false confidence. |
| R-003 | Large-scale batch conversion before regression tests pass. | Known failure modes will scale into bad output. |
| R-004 | Treating review output as optional polish. | Review output is central to validation-first design. |
| R-005 | Using prior generated artifacts as current truth without verifying they exist. | Artifact presence varies by session/environment. |

## 7. Deferred decisions

| ID | Decision needed | Options under consideration | Blocking? |
|---|---|---|---:|
| DF-001 | OCR engine | Tesseract, PaddleOCR, cloud OCR, hybrid OCR, engine-specific adapters | Yes for implementation |
| DF-002 | Layout/block detector | PDF text boxes, OCR boxes, computer vision segmentation, hybrid rules | Yes for implementation |
| DF-003 | Reviewer UI interaction model | Read-only QA, accept/reject, inline edit, JSON patch export | Yes for correction memory workflow |
| DF-004 | Correction-memory storage | JSON per batch, project-level JSON, database, versioned patches | Medium |
| DF-005 | Visual handling default | SVG recreation, cropped source region, full-page crop, human-selected crop | Medium |
| DF-006 | Regression snapshot format | JSON expected structures, rendered screenshots, issue expectations, hybrid snapshots | Yes before stable tests |
| DF-007 | Batch naming/versioning | Date-based, source-based, semantic version, run ID | Medium |
| DF-008 | Exact confidence thresholds | Conservative fixed thresholds vs validator-specific scoring | Medium |

## 8. Critical regression decisions

| ID | Regression case | Required behavior | Decision status |
|---|---|---|---|
| T-001 | `sumbridge2.pdf`, page 1 | Separate abbreviation instruction from earthquake factoid/sidebar. | Accepted hard gate |
| T-002 | `sumbridge2.pdf`, page 2 | Detect/correct or flag cents-symbol misreads such as `11¢` becoming `110`. | Accepted hard gate |
| T-003 | `summerbridge trial.pdf`, page 5 | Preserve/recreate number-line visual reference; answer boxes alone are not enough. | Accepted hard gate |

## 9. Change-control rule

When a project decision changes: add a new decision ID, mark old decisions as superseded/rejected/revised when needed, state the reason, update backlog/artifact map if affected, and do not silently overwrite project doctrine.

## 10. Source basis

This decision log is based on the uploaded handoff baseline, V4 pipeline spec, V4 issue taxonomy, V4 validation rules, V4 correction-memory schema/rules, V4 reviewer/student HTML specs, source inventory, pilot page selection, schema/config/test-case files, and critical regression tests.
