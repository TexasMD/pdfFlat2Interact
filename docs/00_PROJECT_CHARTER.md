# 00 — DOCVERT Project Charter

Updated: 2026-06-13 UTC  
Status: Active Control Tower source  
Project: `docvert`

## 1. Charter

`docvert` is a layout-aware, validation-first document AI pipeline for converting workbook-style educational PDFs into accurate, usable, interactive student-facing webpages.

The project converts the educational task from a static workbook page into clean interactive content while preserving any visual reference required for the student to answer correctly.

This Control Tower chat manages project structure, decisions, risks, artifact inventory, open questions, backlog, and phase definitions. It does **not** run workbook conversion and does **not** generate student/reviewer webpage code.

## 2. Scope

### In scope

- Educational workbook PDF intake planning.
- Project-governance files and durable project memory.
- Pipeline architecture and validation rules.
- Artifact contracts and handoff maps.
- Decision logging.
- Backlog triage.
- Risk tracking.
- Open-question tracking.
- Definition of done for each phase.
- Regression-test planning.

### Out of scope for this Control Tower chat

- Running source PDF conversion.
- Generating `index.html`, `review.html`, or other webpage code.
- Performing OCR or layout extraction on workbook PDFs.
- Treating prior handoff materials as source workbook PDFs.
- Assuming prior generated artifacts are present unless confirmed in the active working directory.

### Project-level non-goals

- This is not a clinical, medical, PHI, legal, billing, patient-care, or healthcare workflow project.
- This is not a simple image-overlay worksheet generator.
- This is not a naive `PDF text -> HTML` converter.
- This is not a Summer Bridge-only system. Summer Bridge examples are seed regression cases, not the project identity.

## 3. Core doctrine

The rendered page image is the source of truth.

Embedded PDF text, OCR text, and extracted structure are hypotheses until checked against rendered page images, OCR/visible-text evidence, embedded text, layout/block segmentation, block-role classification, symbol normalization, semantic plausibility, exercise completeness, visual-reference requirements, and human review when uncertainty remains.

Project rule: **Do not silently generate confident garbage. Flag uncertainty.**

## 4. Product goal

The default final output for a conversion batch is a small local static website or standalone student-facing interactive HTML worksheet package, accompanied by reviewer-facing QA artifacts.

The student-facing output should be clean and usable. The reviewer-facing output should make missing content, symbol corruption, visual-reference omissions, block-merge errors, semantic nonsense, and unreviewed uncertainty obvious.

## 5. Current state summary

### Established durable sources

- `DOCVERT_HANDOFF_BASELINE.md`.
- `01_PIPELINE_SPEC_V4.md`.
- `00_PROJECT_CHARTER.md`.
- `10_DECISION_LOG.md`.
- `11_BACKLOG.md`.
- `12_ARTIFACT_MAP.md`.
- `09_SOURCE_PDF_INVENTORY.md`.
- `09_PILOT_PAGE_SELECTION.md`.
- `03_ISSUE_TAXONOMY_V4.md`.
- `04_VALIDATION_RULES_V4.md`.
- `05_CORRECTION_MEMORY_SCHEMA_V4.json`.
- `06_CORRECTION_MEMORY_RULES_V4.md`.
- `07_REVIEW_HTML_SPEC_V4.md`.
- `08_STUDENT_HTML_SPEC_V4.md`.

### Established project doctrine

- V4 pipeline architecture.
- Validator and QA rules.
- Known failure mode catalog.
- Exercise conversion rules.
- Required artifact/output contract.
- Correction-memory schema/rules.
- Issue taxonomy and blocking policy.
- Reviewer HTML specification.
- Student HTML release-gate specification.
- Critical regression tests.

### Current source-corpus status

Only uploaded and confirmed source PDFs are active ground truth. Artifact-map entries, audit JSON, handoff docs, parsed-text snippets, and prior generated artifacts are not proof that a source PDF is present.

Confirmed active source PDFs:

- `summerbridge trial.pdf` — 19 pages; selected for first-pilot page 5 number-line / spatial-layout / visual-reference regression.
- `sumbridge2.pdf` — 23 pages; selected for first-pilot pages 1, 2, and 6.
- `sumbridge3.pdf` — 23 pages; selected for first-pilot page 3.
- `sumbridge4.pdf` — 23 pages; selected for first-pilot page 2.
- `sumbridge5.pdf` — 23 pages; selected for first-pilot pages 8 and 2.
- `sumbridge6.pdf` — 23 pages; confirmed active but deferred from first pilot; later answer-page / answer-key exclusion candidate.

Missing expected PDFs:

- `sumbridgetest.pdf` — lower priority/reference; does not block first pilot.
- `sumbridge7.pdf` — later batch candidate; does not block first pilot.
- `sumbridge8.pdf` — later batch candidate; does not block first pilot.

### Selected first extraction-pilot pages

The first extraction pilot is defined by `09_PILOT_PAGE_SELECTION.md` and remains pending human approval.

1. `sumbridge2.pdf`, page 1 — factoid/sidebar separation and block coherence.
2. `sumbridge2.pdf`, page 2 — cents-symbol and money semantic validation.
3. `summerbridge trial.pdf`, page 5 — number-line / spatial-layout / visual-reference preservation.
4. `sumbridge2.pdf`, page 6 — vertical arithmetic plus word-bank/fill-in handling.
5. `sumbridge5.pdf`, page 8 — text-heavy passage and response-field baseline.
6. `sumbridge3.pdf`, page 3 — number-family grid and prefix/suffix grouping.
7. `sumbridge4.pdf`, page 2 — fraction-table visual dependency and fraction layout.
8. `sumbridge5.pdf`, page 2 — crossword/grid visual reference and factoid separation.

### Not yet established

- A proven current V4 implementation run.
- OCR engine choice.
- Layout/block-detection engine choice.
- Reviewer edit/accept/reject workflow.
- Regression snapshot format.
- Final batch naming/versioning convention.
- Long-term storage location for durable correction memory.
- First extraction-pilot implementation brief approval.

### Previously failed or unsafe approaches

- Linear PDF text extraction.
- Trusting embedded PDF text as complete.
- Trusting OCR as complete.
- Merging visually separate sidebars/factoids into instructions.
- Omitting visual references when the exercise depends on a number line, map, chart, table, diagram, grid, or spatial layout.
- Treating clean-looking output as proof of correctness.
- Correcting symbols without visual confirmation and logging.
- Generating student HTML before reviewer QA exposes extraction evidence.

## 6. Operating model

Control Tower maintains project-management sources. Future implementation/conversion chats must read these before running conversion work:

- `DOCVERT_HANDOFF_BASELINE.md`
- `01_PIPELINE_SPEC_V4.md`
- `00_PROJECT_CHARTER.md`
- `10_DECISION_LOG.md`
- `11_BACKLOG.md`
- `12_ARTIFACT_MAP.md`
- `09_SOURCE_PDF_INVENTORY.md`
- `09_PILOT_PAGE_SELECTION.md`
- `03_ISSUE_TAXONOMY_V4.md`
- `04_VALIDATION_RULES_V4.md`
- `05_CORRECTION_MEMORY_SCHEMA_V4.json`
- `06_CORRECTION_MEMORY_RULES_V4.md`
- `07_REVIEW_HTML_SPEC_V4.md`
- `08_STUDENT_HTML_SPEC_V4.md`

## 7. Immediate next actions

1. Preserve the Control Tower files and V4 specs as canonical Project sources.
2. Treat only uploaded and confirmed source PDFs as active ground truth.
3. Keep the source corpus gap visible: `sumbridgetest.pdf`, `sumbridge7.pdf`, and `sumbridge8.pdf` are missing and do not block the first pilot.
4. Review and explicitly approve or revise `09_PILOT_PAGE_SELECTION.md` before any extraction, OCR, layout detection, or HTML generation.
5. Prepare and approve a first extraction-pilot implementation brief naming the selected pages, V4 source specs, output artifacts, stop conditions, and hard gates.
6. Before any authorized run, create a source manifest with hashes, page counts, stable source IDs, selected page list, and page-image traceability.
7. When implementation is later authorized, run only the selected first-pilot pages and gate first on the three core regression pages: `sumbridge2.pdf` page 1, `sumbridge2.pdf` page 2, and `summerbridge trial.pdf` page 5.
8. Do not start conversion until pilot selection is approved and intake passes.

## 8. Open questions

| ID | Question | Why it matters | Current disposition |
|---|---|---|---|
| OQ-001 | Which OCR engine should V4 use? | OCR must produce visible text and preferably bounding boxes. | Open |
| OQ-002 | Which layout/block engine should V4 use? | Block segmentation is the core failure-prevention mechanism. | Open |
| OQ-003 | Should factoids be omitted, shown as optional notes, or configurable? | Student output should not confuse decoration with tasks. | Default: omit or optional note; finalize later. |
| OQ-004 | How will human edits update correction memory? | Repeat errors should not require repeat manual fixes. | Open |
| OQ-005 | Where should source PDFs live long-term? | Source-data handling must be explicit and reproducible. | Partly resolved for current session; durable storage remains open. |
| OQ-006 | What is the minimum acceptable reviewer UI for the first extraction pilot? | QA must happen before polish. | Start with panels required by `07_REVIEW_HTML_SPEC_V4.md`. |
| OQ-007 | What snapshot format should regression tests use? | Future runs need objective comparison targets. | Open |
| OQ-008 | Should simple visuals be recreated as SVG or cropped by default? | Recreated visuals are cleaner; crops are safer when uncertain. | Default: SVG if simple, crop if complex/uncertain. |
| OQ-009 | Should clean student HTML be withheld entirely until reviewer approval or generated as a gated debug preview? | Prevents confusing preview with release-ready worksheet. | Default: withhold clean release; debug preview only if clearly marked. |

## 9. Risk list

| ID | Risk | Severity | Mitigation |
|---|---:|---:|---|
| R-001 | Handoff files are mistaken for source workbook PDFs. | High | Treat source PDFs as active only when uploaded/confirmed. |
| R-002 | Naive PDF text extraction re-enters as acceptable. | High | Enforce rendered-image + OCR + layout + validation pipeline. |
| R-003 | Output looks good but omits required visual references. | High | Visual-reference validator and reviewer QA required. |
| R-004 | Cents symbols, math signs, fractions, or operators are corrupted. | High | Symbol normalization plus semantic validators and issue logging. |
| R-005 | Factoids or sidebars are merged into prompts. | High | Block coherence validation; factoid regression test. |
| R-006 | Embedded PDF text misses visible problems. | High | OCR/visible-text verification and item-count checks. |
| R-007 | Reviewer UI becomes an afterthought. | High | Reviewer-facing QA is the first rendering target. |
| R-008 | Human corrections are not persisted. | Medium | Correction memory update phase required. |
| R-009 | Summer Bridge assumptions overfit the system. | Medium | Treat examples as seed tests, not global scope. |
| R-010 | Unlogged auto-correction creates hidden errors. | High | Correct only with high confidence and log every correction. |
| R-011 | Artifact references are mistaken for active source availability. | High | Maintain explicit active/missing source lists. |
| R-012 | Missing later-batch PDFs distract from first pilot. | Medium | Mark missing expected PDFs as non-blocking. |
| R-013 | Active source inventory drifts across docs. | Medium | Synchronize source status in all Control Tower docs. |
| R-014 | Pilot-selection documentation is mistaken for authorization to run extraction. | High | Preserve stop condition until approval and intake pass. |
| R-015 | `summerbridge trial.pdf`, page 5 is omitted despite being the active number-line regression source. | High | Keep it in first-pilot set unless explicitly revised. |
| R-016 | First pilot expands into a broad batch before core gates pass. | High | Limit first run to selected pages and stop after hard-gate failure. |
| R-017 | V4 specs are created but not wired into implementation acceptance tests. | High | Treat V4 specs as required inputs and acceptance criteria. |
| R-018 | Student HTML is generated from unresolved extraction output. | High | Reviewer QA first; clean student release gated by V4 student spec. |
| R-019 | Correction memory over-applies broad rules and silently changes task meaning. | High | Use V4 correction-memory rules: narrow scope, preserve evidence, require visual support, log corrections. |
| R-020 | Issue taxonomy drift causes nonstandard/incomplete issue records. | Medium | Map issue writer to `03_ISSUE_TAXONOMY_V4.md` before pilot run. |

## 10. Definition of done by phase

### Phase 0 — Control Tower setup

Done when:

- Control Tower sources exist and are synchronized.
- The docs explicitly prohibit conversion in Control Tower mode.
- Active source PDFs and missing expected PDFs are named.
- V4 spec-source set is registered in the artifact map and decision log.
- Immediate next actions and phase gates are clear.

### Phase 1 — Source PDF intake readiness

Done when:

- Required pilot source PDFs are uploaded/confirmed.
- Source manifest requirements are defined.
- Each source PDF has filename, page count, intended batch, selected pages, and status metadata.
- The intake process distinguishes source PDFs from handoff/spec/generated files.
- No conversion begins until intake passes.

### First extraction pilot — definition of done

The first extraction pilot is done only when:

- `09_PILOT_PAGE_SELECTION.md` has been explicitly approved or revised by the human reviewer.
- The run is limited to the approved pages: `sumbridge2.pdf` pages 1, 2, and 6; `summerbridge trial.pdf` page 5; `sumbridge5.pdf` pages 8 and 2; `sumbridge3.pdf` page 3; and `sumbridge4.pdf` page 2.
- A source manifest records each selected source PDF, page count, hash, stable source ID, selected pages, and page-image traceability.
- The implementation reads and follows `03_ISSUE_TAXONOMY_V4.md`, `04_VALIDATION_RULES_V4.md`, `05_CORRECTION_MEMORY_SCHEMA_V4.json`, `06_CORRECTION_MEMORY_RULES_V4.md`, `07_REVIEW_HTML_SPEC_V4.md`, and `08_STUDENT_HTML_SPEC_V4.md`.
- The first three regression gates pass or fail safely: factoid/sidebar separation, cents-symbol validation, and number-line visual-reference preservation.
- Each selected page has rendered-page traceability, embedded-text/OCR comparison, block roles, structured extraction, visual-reference status, issue records, and a page release category.
- Issue records conform to the V4 taxonomy and include severity, `blocks_student_html`, status, source/page traceability, evidence, and recommended human action.
- Correction-memory suggestions or applied corrections conform to the V4 schema/rules and do not silently rewrite task-bearing content without visual support.
- High-severity issues are either fixed, explicitly carried into reviewer QA, or stop the run.
- Reviewer-facing QA artifacts follow `07_REVIEW_HTML_SPEC_V4.md` and expose source images, extracted text, OCR text, comparison evidence, block roles, issues, visual references, and suggested corrections before any student-facing release.
- Student-facing output is not produced as a clean release unless it satisfies `08_STUDENT_HTML_SPEC_V4.md`; if produced later for preview, it must be clearly gated/withheld for blocked pages.
- No larger batch begins until the first-pilot report is reviewed and accepted.

### Reviewer QA output

Done when:

- Reviewer output shows rendered page image.
- Reviewer output shows embedded text and OCR text.
- Reviewer output shows blocks, bounding boxes, roles, confidence, issues, and suggested corrections.
- Every issue appears in `json/issues.json`, reviewer output, and report artifacts.
- Reviewer can tell why a page is risky without reading code.

### Student output generation

Done when:

- Student output is generated from validated structured JSON, not raw text lines.
- Required visuals are present or the page is withheld/flagged incomplete.
- Inputs match exercise type.
- Decorative/footer content is not treated as student work.
- No unresolved critical or unreviewed major task-bearing issue is hidden.

### Batch packaging and handoff

Done when:

- Required artifacts are generated with stable relative links.
- Batch package includes required JSON, reviewer QA, student output if cleared, reports, visual assets, and manifests.
- Known limitations and high-severity issues are documented.
- Correction memory updates are preserved.
- The package does not depend on notebook/session memory.

## 11. Source basis

This charter is based on:

- `DOCVERT_HANDOFF_BASELINE.md`
- `01_PIPELINE_SPEC_V4.md`
- `09_SOURCE_PDF_INVENTORY.md`
- `09_PILOT_PAGE_SELECTION.md`
- `03_ISSUE_TAXONOMY_V4.md`
- `04_VALIDATION_RULES_V4.md`
- `05_CORRECTION_MEMORY_SCHEMA_V4.json`
- `06_CORRECTION_MEMORY_RULES_V4.md`
- `07_REVIEW_HTML_SPEC_V4.md`
- `08_STUDENT_HTML_SPEC_V4.md`
- JSON schema/config/test-case files uploaded with the handoff materials
