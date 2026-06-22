# 11 — DOCVERT Backlog

Updated: 2026-06-13 UTC  
Status: Active Control Tower source  
Project: `docvert`

## 1. Backlog rules

- Accuracy and validation outrank polish.
- Do not run source PDF conversion from the Control Tower chat.
- Do not generate webpage code until the task explicitly moves into implementation/conversion mode.
- Do not proceed to large-scale conversion until first-pilot regression gates pass.
- Every implementation task must preserve traceability to source PDF page images.
- Every uncertain extraction must become an issue, not a silent assumption.
- Only uploaded and confirmed source PDFs are active ground truth.
- Reviewer-facing QA must precede clean student-facing release.

## 2. Priority vocabulary

- **P0** — required before meaningful implementation or conversion.
- **P1** — required for first extraction pilot / regression success.
- **P2** — needed for useful batch conversion and review.
- **P3** — polish, scalability, or later productization.

## 3. Current immediate queue

| Priority | ID | Task | Owner/Mode | Done when |
|---:|---|---|---|---|
| P0 | CT-001 | Preserve Control Tower sources. | Control Tower | `00_PROJECT_CHARTER.md`, `10_DECISION_LOG.md`, `11_BACKLOG.md`, `12_ARTIFACT_MAP.md`, `09_SOURCE_PDF_INVENTORY.md`, and `09_PILOT_PAGE_SELECTION.md` are current. |
| P0 | CT-002 | Register V4 spec-source set. | Control Tower | Artifact map and decision log list `03_ISSUE_TAXONOMY_V4.md`, `04_VALIDATION_RULES_V4.md`, `05_CORRECTION_MEMORY_SCHEMA_V4.json`, `06_CORRECTION_MEMORY_RULES_V4.md`, `07_REVIEW_HTML_SPEC_V4.md`, and `08_STUDENT_HTML_SPEC_V4.md`. |
| P0 | CT-003 | Keep first extraction pilot blocked until approval. | Control Tower | No OCR, extraction, layout detection, reviewer HTML, student HTML, or QA webpage generation starts from this chat. |
| P0 | CT-004 | Approve or revise the first extraction-pilot implementation brief. | Human + Control Tower | The implementation brief names pilot pages, V4 source specs, output artifacts, stop conditions, and hard gates. |
| P0 | CT-005 | Prepare source manifest requirements. | Control Tower / future implementation | Manifest requirements include hashes, page counts, source IDs, selected pages, and page-image traceability. |

## 4. Phase 0 — Governance backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P0 | GOV-001 | Maintain project charter. | Update scope, risks, open questions, immediate actions, and definitions of done. |
| P0 | GOV-002 | Maintain decision log. | Use accepted/deferred/rejected/superseded statuses. |
| P0 | GOV-003 | Maintain artifact map. | Distinguish Control Tower sources, V4 specs, source PDFs, generated artifacts, and expected outputs. |
| P0 | GOV-004 | Maintain backlog. | Keep immediate queue short and phase-gated. |
| P0 | GOV-005 | Maintain active source corpus inventory. | Keep active and missing PDFs synchronized across Control Tower docs. |
| P0 | GOV-006 | Maintain first-pilot approval status. | `09_PILOT_PAGE_SELECTION.md` remains pending until explicit approval/revision. |
| P0 | GOV-007 | Maintain V4 spec-source set. | Keep issue taxonomy, validation rules, correction-memory schema/rules, and renderer specs visible in all implementation prompts. |
| P1 | GOV-008 | Create `DOCVERT_SCOPE_AND_CONTAMINATION_GUARDRAILS.md`. | Useful before Codex/API workflow or larger handoff. |
| P1 | GOV-009 | Create durable source PDF intake checklist. | Should likely become `DOCVERT_SOURCE_PDF_INTAKE_CHECKLIST.md`. |

## 5. Phase 1 — Source PDF intake backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P0 | INT-001 | Maintain confirmed active source PDF list. | Active: `summerbridge trial.pdf`, `sumbridge2.pdf`, `sumbridge3.pdf`, `sumbridge4.pdf`, `sumbridge5.pdf`, `sumbridge6.pdf`. |
| P0 | INT-002 | Record missing expected PDFs. | Missing: `sumbridgetest.pdf`, `sumbridge7.pdf`, `sumbridge8.pdf`; none block the first pilot. |
| P0 | INT-003 | Validate file identity and page counts. | Prevent processing handoff/spec/generated files as source PDFs. |
| P0 | INT-004 | Build source manifest. | Include filename, page count, source status, selected pages, source ID, run ID, and hash. |
| P0 | INT-005 | Prepare first extraction-pilot implementation brief. | Must name selected pages, V4 sources, required outputs, hard gates, and stop conditions. |
| P1 | INT-006 | Define batch naming/versioning convention. | Needed before repeated pilot runs. |
| P2 | INT-007 | Upload `sumbridge7.pdf` and `sumbridge8.pdf` before broad batch expansion. | Not required for first pilot. |
| P3 | INT-008 | Upload `sumbridgetest.pdf` if its reference role becomes necessary. | Lower priority/reference. |

## 6. Phase 2 — First extraction/validation prototype backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P1 | V4-001 | Select OCR strategy. | Must support visible-text verification; bounding boxes strongly preferred. |
| P1 | V4-002 | Select layout/block detection strategy. | Hybrid PDF text boxes + OCR boxes + visual segmentation likely needed. |
| P1 | V4-003 | Implement page renderer. | Rendered page image is canonical visual truth. |
| P1 | V4-004 | Implement embedded text extractor. | Treat output as hypothesis only. |
| P1 | V4-005 | Implement OCR extraction. | Required for visible-text verification and symbol/label checks. |
| P1 | V4-006 | Implement OCR-vs-PDF-text comparison. | Must flag gaps, symbol disagreements, item-count differences, and reading-order problems. |
| P1 | V4-007 | Implement layout block records. | Must include source/page, bbox, source methods, role, confidence, visual features, nearby blocks, issues. |
| P1 | V4-008 | Implement block role classifier. | Use durable roles such as instruction, exercise items, answer bank, visual reference, factoid, footer, unknown. |
| P1 | V4-009 | Implement block coherence validator. | Detect instruction/factoid merges and impossible reading order. |
| P1 | V4-010 | Map issue writer to `03_ISSUE_TAXONOMY_V4.md`. | Required fields, severity, `blocks_student_html`, status, evidence, and traceability must match V4. |
| P1 | V4-011 | Map validation stages to `04_VALIDATION_RULES_V4.md`. | Pilot run must follow V4 validation order and page release-category model. |
| P1 | V4-012 | Load or emit correction memory using V4 schema/rules. | Use `05_CORRECTION_MEMORY_SCHEMA_V4.json` and `06_CORRECTION_MEMORY_RULES_V4.md`; no broad silent corrections. |
| P1 | V4-013 | Generate reviewer QA according to `07_REVIEW_HTML_SPEC_V4.md`. | Reviewer output must expose source image, OCR/PDF evidence, block roles, issues, visual references, and correction suggestions. |
| P1 | V4-014 | Keep student output gated by `08_STUDENT_HTML_SPEC_V4.md`. | Clean student output is withheld unless V4 release gates pass. |

## 7. Phase 3 — Semantic validator backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P1 | VAL-001 | Coin/money semantic validator. | Detect cents-symbol corruption and implausible coin values. |
| P1 | VAL-002 | Arithmetic validator. | Check operands, operators, blanks, numbering sequence, and vertical layout. |
| P1 | VAL-003 | Fraction layout validator. | Protect stacked fractions and fraction-table references. |
| P1 | VAL-004 | Visual-reference validator. | Detect and preserve maps, number lines, graphs, charts, diagrams, tables, grids, and drawing areas. |
| P1 | VAL-005 | Completeness validator. | Check visible item count, answer-field count, instructions, choices, and response fields. |
| P1 | VAL-006 | Block-coherence semantic validator. | Detect merged unrelated text blocks and factoid/sidebar contamination. |

## 8. Phase 4 — Reviewer QA backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P1 | REV-001 | Create reviewer QA shell. | Must show run header, page navigator, page status, issue counts, and source traceability. |
| P1 | REV-002 | Show rendered source page image. | Full-page image is required evidence. |
| P1 | REV-003 | Show embedded text, OCR text, and comparison differences. | Required for pilot. |
| P1 | REV-004 | Show layout blocks, roles, confidence, and bboxes/overlays. | Required for block-aware validation. |
| P1 | REV-005 | Show issues with severity, status, blocking effect, evidence, and recommended action. | Required by V4 issue taxonomy. |
| P1 | REV-006 | Show visual references and correction-memory suggestions. | Required for visual and correction-memory gates. |
| P2 | REV-007 | Add review actions. | Accept/edit/reject/downgrade/carry-forward decisions can later update correction memory. |

## 9. Phase 5 — Student output backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P1 | STU-001 | Enforce student-release gates. | No open critical issue; no unreviewed major task-bearing issue; required visuals present. |
| P1 | STU-002 | Render from validated structured JSON only. | Never render clean student HTML from raw extracted lines. |
| P1 | STU-003 | Map exercise types to input controls. | Short answer, textarea, dropdown, matching, grid, drawing area, etc. |
| P1 | STU-004 | Preserve required visuals. | Use SVG recreation or crop as appropriate. |
| P2 | STU-005 | Add local save/export/print controls. | Useful after validation gates work. |

## 10. Later batch backlog

| Priority | ID | Task | Notes |
|---:|---|---|---|
| P2 | BATCH-001 | Expand after first-pilot acceptance. | Do not run a larger batch until first-pilot report is reviewed and accepted. |
| P2 | BATCH-002 | Add answer-page / answer-key exclusion tests. | Use `sumbridge6.pdf` after extraction logic is stable. |
| P2 | BATCH-003 | Add missing later PDFs if needed. | `sumbridge7.pdf` and `sumbridge8.pdf`. |

## 11. Definition of done for the first extraction pilot

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

## 12. Stop condition

No extraction, OCR, layout detection, reviewer HTML generation, student HTML generation, or source PDF conversion is authorized by this backlog update.
