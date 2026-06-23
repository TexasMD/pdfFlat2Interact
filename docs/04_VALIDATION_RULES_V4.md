# 04 — DOCVERT Validation Rules V4

Updated: 2026-06-13 UTC
Status: Durable Project-source validator specification
Project: `docvert`
Mode: Specification only — no OCR, no extraction, no conversion, no student HTML, no reviewer HTML

## 1. Purpose

This document defines validation rules for the first `docvert` pilot.

The validator must decide whether workbook content extracted from a PDF page is accurate, complete, visually supported, semantically coherent, traceable, reviewable, and safe to release as student-facing interactive HTML.

`03_ISSUE_TAXONOMY_V4.md` defines the issue vocabulary. This document defines required checks, gates, records, and stop conditions.

## 2. Validator doctrine

1. The rendered page image is the source of truth.
2. Embedded PDF text and OCR text are both untrusted hypotheses.
3. OCR and PDF text must be compared against each other and against the rendered image.
4. Layout/block detection must precede question extraction.
5. Block role classification and block coherence checks must precede student rendering.
6. Required visuals must be preserved, recreated, or flagged as blocking.
7. Semantic sanity checks must run before release.
8. Student output must be generated from validated structured JSON, not raw extracted lines.
9. Every uncertainty affecting answerability must become an issue.
10. Reviewer-facing QA is required before release.

## 3. First-pilot scope and hard gates

The first pilot uses these selected pages only:

| Order | Source page | Validation role |
|---:|---|---|
| 1 | `sumbridge2.pdf`, page 1 | Factoid/sidebar separation, block coherence, matching columns. |
| 2 | `sumbridge2.pdf`, page 2 | Cents-symbol validation, money semantic plausibility, answer lines. |
| 3 | `summerbridge trial.pdf`, page 5 | Number-line/spatial-layout visual preservation. |
| 4 | `sumbridge2.pdf`, page 6 | Vertical arithmetic, operators, word-bank attachment. |
| 5 | `sumbridge5.pdf`, page 8 | Text-heavy passage and response-field baseline. |
| 6 | `sumbridge3.pdf`, page 3 | Number-family grid and prefix/suffix grouping. |
| 7 | `sumbridge4.pdf`, page 2 | Fraction-table visual dependency and fraction layout. |
| 8 | `sumbridge5.pdf`, page 2 | Crossword/grid visual reference, clue grouping, factoid separation. |

The first three are hard regression gates. If any fails and the pipeline does not emit clear blocking issues plus reviewer evidence, stop implementation work and fix the validator before expanding.

## 4. Required validation stages

A pilot run must validate in this order:

1. Source manifest and pilot-scope validation.
2. Page rendering and page-image traceability validation.
3. Embedded PDF text extraction audit.
4. OCR visible-text audit.
5. OCR-vs-PDF-text comparison.
6. Layout/block detection audit.
7. Block role classification audit.
8. Block coherence validation.
9. Symbol, number, operator, and fraction-layout validation.
10. Question/instruction/exercise extraction validation.
11. Visual-reference dependency validation.
12. Exercise completeness validation.
13. Exercise-specific semantic sanity checks.
14. Issue-record completeness validation.
15. Reviewer-facing QA report validation.
16. Student-output release-gate validation.
17. Final QA report validation.

A later stage must not hide failure from an earlier stage. Later artifacts may exist only as review/debug output if earlier blockers remain.

## 5. Required page-level validation checks

Each selected page needs a page-level validation record.

### 5.1 Source and page identity

Validate that:

- source file is confirmed active source material;
- page is in the approved pilot list;
- manifest includes `source_id`, filename, hash, page count, selected pages, source status, and run ID;
- source type is `source_pdf`, not handoff/spec/audit/generated artifact.

Emit: `source_identity_uncertain`, `source_page_not_in_approved_pilot`.
Block release if any identity check fails.

### 5.2 Rendered page image

Validate that:

- rendered full-page image exists and opens locally;
- dimensions, DPI, render tool, and page index are recorded;
- no destructive crop was used as the canonical page image;
- all page/block/exercise/issue records reference the image path.

Emit: `page_render_failed`, `page_image_traceability_missing`, `visual_asset_missing_or_broken`.
Block release if the image is missing, broken, or untraceable.

### 5.3 Text coverage

Validate that:

- embedded PDF text is extracted or explicitly marked sparse/incomplete;
- OCR text exists for every selected pilot page;
- OCR/PDF text coverage is compared at page, block, and item level;
- visible task-bearing text missing from either source becomes an issue;
- duplicate OCR/PDF ingestion is detected and deduplicated.

Emit: `pdf_text_layer_incomplete`, `embedded_text_extraction_error`, `ocr_error`, `ocr_low_confidence_task_text`, `ocr_pdf_text_disagreement`, `missing_text`, `duplicated_text`.
Block release if task-bearing text is missing or unverified.

### 5.4 Layout and block structure

Validate that:

- page has block records with bounding boxes;
- each block records source methods: PDF text, OCR, rendered-image segmentation as available;
- every block has role, confidence, student include/exclude recommendation, and nearby-block context;
- task-bearing blocks are assigned to an exercise, passage, visual reference, instruction, answer bank, or review-only category;
- footer/decorative/factoid blocks are not merged into task prompts.

Emit: `possible_layout_block_merge_error`, `columns_merged_incorrectly`, `table_reading_order_error`, `footer_or_decorative_text_in_student_output`, `sidebar_factoid_detected`.
Block release if task-bearing layout grouping is unresolved.

### 5.5 Page release category

Each page must end with exactly one release category:

| Category | Meaning |
|---|---|
| `page_release_ready` | No open blockers; required structure and visuals validated. |
| `page_release_with_warnings` | Only non-blocking issues remain and are visible in QA. |
| `page_review_required` | Human review required before student use. |
| `page_blocked` | Page is not safe as a student worksheet. |

Any open `critical` issue forces `page_blocked`. Any unreviewed `major` task-bearing issue forces at least `page_review_required`.

## 6. Required question-level validation checks

Each exercise/question group needs a structured record and validation status.

### 6.1 Exercise structure

Validate that each exercise has:

- stable `exercise_id`;
- source ID, file, page, page image path;
- section title/context if visible;
- attached instruction block IDs;
- attached item block IDs;
- attached answer-bank/choice block IDs when present;
- attached visual-reference IDs when needed;
- input controls mapped to visible answer fields;
- linked issue IDs.

Emit: `broken_question_grouping`, `instruction_question_separation_error`, `missing_visible_item`, `numbered_item_count_mismatch`, `wrong_input_type`.

### 6.2 Instruction validation

Check that instructions:

- are complete and not merged with unrelated text;
- attach to the correct item group;
- are not separated from items they govern;
- preserve action verbs such as write, circle, underline, draw, label, match, complete, compare, use, and explain;
- trigger the correct interaction type;
- flag external references.

Emit: `instruction_question_separation_error`, `contextual_coherence_failure`, `semantic_nonsense_from_extraction`, `external_page_reference`, `wrong_input_type`.

### 6.3 Item, numbering, and choices

Check that:

- visible item count equals extracted item count;
- numbered sequences are continuous unless the source intentionally skips;
- item numbers are not confused with page numbers, clue numbers, labels, or answer-key numbers;
- choices/word banks/matching options are complete and attached;
- OCR/PDF duplicates do not create duplicate items.

Emit: `missing_visible_item`, `numbered_item_count_mismatch`, `missing_answer_choices`, `duplicated_text`, `columns_merged_incorrectly`.

### 6.4 Answer fields and input controls

Check that:

- every visible answer line, blank, circle, checkbox, box, grid cell, or drawing/writing area is represented by an appropriate input or visual task region;
- response areas are not counted as separate questions;
- drawing prompts have a canvas, drawing area, upload/sketch placeholder, or reviewer-approved equivalent;
- writing prompts have suitable text areas;
- matching and multiple-choice prompts have appropriate controls.

Emit: `missing_answer_lines_or_blanks`, `wrong_input_type`, `broken_question_grouping`.

## 7. Required visual-reference validation checks

A visual reference is required when the student cannot answer correctly from text alone.

### 7.1 Visual triggers

Flag a likely visual dependency when text includes:

- `picture`, `chart`, `graph`, `map`, `table`, `diagram`, `number line`, `clock`, `grid`, `crossword`, `puzzle`, `fraction table`, `shown`, `above`, `below`, `following`, `draw`, `circle`, `underline`, `label`, `use the`, `look at`.

Also flag when layout/image analysis detects task-bearing visuals near questions.

### 7.2 Required visual types

The validator must preserve or flag:

- number lines and tick labels;
- maps and region labels;
- graphs, charts, and tables;
- fraction tables and bars;
- geometry figures and line segments;
- clocks;
- crossword and word-search grids;
- picture prompts;
- drawing/writing boxes when the layout itself defines the response area.

### 7.3 Visual asset checks

For every required visual, validate:

- `visual_id`, source page, bbox, and asset path exist;
- asset is either a source-page crop or faithful SVG/recreation;
- crop/SVG includes all labels, tick marks, rows, columns, axes, clue numbers, captions, and relevant spatial relationships;
- visual is linked to the relevant exercise;
- reviewer QA shows source image and preserved visual side by side.

Emit: `visual_reference_required_or_helpful`, `diagram_image_numberline_omitted`, `visual_reference_dependency_not_preserved`, `unresolved_deictic_visual_reference`, `caption_or_label_separated_from_visual`, `grid_structure_missing_or_wrong`.

Block release if a required visual is missing or insufficient.

## 8. OCR/PDF-text comparison rules

Comparison must occur after rendering, embedded text extraction, and OCR.

### 8.1 Normalize only for comparison

For matching purposes only, create normalized copies that standardize whitespace, common quote variants, dash variants, case where appropriate, and obvious line breaks. Keep raw OCR and raw PDF text in the record.

Do not silently normalize source content for student output unless visually supported and logged.

### 8.2 Compare at four levels

| Level | Required checks |
|---|---|
| Page | Overall text coverage, missing/extra text, obvious reading-order gaps. |
| Block | OCR/PDF overlap, bbox alignment, role-bearing text coverage. |
| Item | Numbered item presence, choices/blanks/answer lines. |
| Symbol/number | Digits, currency, operators, comparison signs, fractions, decimals, commas, minus signs. |

### 8.3 Disagreement handling

| Condition | Required action |
|---|---|
| OCR sees visible text missing from PDF text | Emit `pdf_text_layer_incomplete` or `missing_text`; prefer image/OCR for review. |
| PDF text contains text not visible on image | Emit `embedded_text_extraction_error`; exclude unless visually confirmed. |
| OCR and PDF disagree on symbol/number/operator | Emit `ocr_pdf_text_disagreement` plus specific issue. |
| OCR confidence is low on task text | Emit `ocr_low_confidence_task_text`; require review. |
| Both agree but semantic validator fails | Emit `semantic_plausibility_failure`; inspect rendered image. |
| Both are incomplete | Block page until human review or better extraction. |

## 9. Block-coherence validation rules

Block coherence asks: do nearby text/visual blocks logically belong together as one instruction, question, section, answer bank, or visual reference?

### 9.1 Separation signals

Treat blocks as probably separate when they differ by:

- background/shading;
- font size/weight;
- large horizontal/vertical gap;
- boxed/sidebar/corner placement;
- column membership;
- factoid labels or decorative framing;
- imperative instruction vs unrelated declarative trivia;
- topic/domain shift;
- sentence coherence improving when an intervening block is skipped.

### 9.2 Merge signals

Treat blocks as possibly connected when:

- a sentence is split across line breaks or columns but remains coherent;
- a word bank visually belongs to following blanks;
- a caption labels an adjacent figure;
- answer lines or blanks align with numbered prompts;
- table cells share row/column geometry.

### 9.3 Required behavior

If raw extraction yields a sequence like:

```text
Draw lines between these words and their
Earthquakes can cause rivers to temporarily flow backwards.
abbreviations.
```

The validator must consider that the first and third fragments form the instruction, while the middle factoid is a separate sidebar. Emit `contextual_coherence_failure`, `possible_layout_block_merge_error`, and/or `sidebar_factoid_detected` if uncertain.

## 10. Semantic sanity-check rules

Semantic validators do not need to solve every problem. They must catch likely extraction nonsense and high-risk corruption.

| Validator | Required checks | Issues to emit |
|---|---|---|
| Coin/money | Values use cents symbols when visually present; coin counts/values are plausible; trailing-zero money values are suspicious. | `possible_cents_symbol_misread`, `wrong_number`, `wrong_symbol`, `semantic_plausibility_failure` |
| Arithmetic | Operators, operands, thousands separators, vertical alignment, blanks, and item counts are preserved. | `corrupted_math_operator`, `wrong_number`, `missing_answer_lines_or_blanks`, `numbered_item_count_mismatch` |
| Fractions | Numerators/denominators, bars, comparison signs, and fraction-table references are preserved. | `ambiguous_fraction_layout`, `wrong_symbol`, `visual_reference_dependency_not_preserved` |
| Tables/grids | Headers, row/column order, cells, labels, clue numbers, and blank cells are preserved. | `table_reading_order_error`, `grid_structure_missing_or_wrong`, `missing_visible_item` |
| Matching/word bank | All choices exist and attach to the correct prompts; columns are not interleaved. | `missing_answer_choices`, `columns_merged_incorrectly`, `broken_question_grouping` |
| Passage/writing | Passage order, paragraph grouping, prompt linkage, and response fields are preserved. | `missing_text`, `mangled_word`, `missing_answer_lines_or_blanks` |
| Visual references | Text references visual and visual is present, linked, complete, and reviewable. | `visual_reference_required_or_helpful`, `unresolved_deictic_visual_reference`, `diagram_image_numberline_omitted` |
| External references | “See/look at page…” dependencies are detected. | `external_page_reference` |

## 11. Stop conditions before clean student HTML release

Stop release and mark the affected page `page_blocked` if any condition applies:

1. Source file/page identity is uncertain.
2. Page is outside approved pilot scope.
3. Rendered page image is missing or untraceable.
4. Task-bearing visible text is missing.
5. OCR/PDF disagreement affects symbols, numbers, operators, choices, or instructions and remains unresolved.
6. Required visual reference is missing, broken, cropped incorrectly, or not linked to the exercise.
7. Question grouping is broken enough to change meaning.
8. Required answer fields, blanks, choices, or input controls are missing.
9. Semantic validator finds unresolved nonsense or implausibility in a task-bearing item.
10. Any open `critical` issue remains.
11. Any unreviewed `major` task-bearing issue remains.
12. `issues.json`, reviewer QA, or final QA omits a known blocking issue.
13. Student-facing HTML was generated from raw extracted lines instead of validated structured data.
14. Final QA lacks page release category and rationale.

## 12. Required contents of `issues.json`

`json/issues.json` must contain:

```json
{
  "schema_version": 4,
  "run_id": "pilot_v4_YYYYMMDD_HHMMSS",
  "created_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "source_manifest_path": "json/source_manifest.json",
  "issue_count": 0,
  "open_blocking_issue_count": 0,
  "issues": []
}
```

Each issue record must include the fields defined in `03_ISSUE_TAXONOMY_V4.md`, including:

- stable `issue_id`;
- `issue_type`, `severity`, `blocks_student_html`, `status`, `confidence`;
- source ID, file, page, page image path;
- related block/exercise/visual IDs;
- bbox when available;
- raw PDF/OCR/visible evidence when relevant;
- validator stage;
- likely cause;
- required human-review action;
- suggested fix when safe;
- reviewer decision fields when reviewed.

Issue records must be referenced by page records, block records, exercise records, reviewer QA, and final QA.

## 13. Required reviewer-facing QA report contents

The reviewer-facing QA report must let a human compare output against source evidence without guessing.

For each page, include:

1. Source filename, page number, page image, page hash/manifest link.
2. Rendered page image viewer.
3. Extracted page structure summary.
4. OCR text panel with confidence warnings.
5. Embedded PDF text panel.
6. OCR-vs-PDF comparison panel.
7. Layout/block map with bboxes, roles, confidence, include/exclude recommendation.
8. Exercise records with instructions, items, answer fields, choices, visuals, and issue links.
9. Preserved visual references shown beside source-page regions.
10. All issues for the page, grouped by severity and blocking status.
11. Suggested fixes and correction-memory matches.
12. Reviewer actions: accept, edit, reject, mark false positive, downgrade/upgrade severity, require rerun.
13. For every review-needed action, selectable reviewer options plus a freeform suggestion or notes field.
14. Page release category and rationale.

For the batch, include:

- source manifest summary;
- selected pilot pages;
- hard-gate pass/fail status;
- issue counts by severity/type/page;
- unresolved blocking issue list;
- correction-memory updates proposed/applied;
- final recommendation: release-ready, release with warnings, review required, or blocked.

## 14. First-pilot pass criteria

The pilot passes only if:

1. All eight selected pages have rendered page images and traceability.
2. OCR/PDF comparison records exist for all selected pages.
3. Block roles and block coherence results exist for all task-bearing blocks.
4. Every required visual is preserved or the page is blocked with a clear issue.
5. Every question has complete instructions, items, answer fields, and choices when applicable.
6. Known regression failures are detected or prevented:
   - `sumbridge2.pdf` page 1 factoid is not merged into instruction.
   - `sumbridge2.pdf` page 2 cents values are not silently accepted as trailing-zero numbers.
   - `summerbridge trial.pdf` page 5 number line is preserved or the page is blocked.
7. `issues.json`, reviewer QA, and final QA agree on open issues and release status.
8. No clean student-facing release is produced while blockers remain.

## 15. Maintenance rule

Keep this document concise and implementation-guiding. Add validation rules only when they change required behavior, issue emission, reviewer evidence, or release gating. Put implementation details, code snippets, and engine-specific thresholds in separate engineering documents unless they are true release rules.
