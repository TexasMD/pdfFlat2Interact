# 03 — DOCVERT Issue Taxonomy V4

Updated: 2026-06-13 UTC  
Status: Durable Project-source validator specification  
Project: `docvert`  
Mode: Specification only — no OCR, no extraction, no conversion, no student HTML, no reviewer HTML

## 1. Purpose

This document defines the issue taxonomy for the first `docvert` pilot.

`docvert` converts workbook-style educational PDFs into validated interactive student webpages. The validator must report every uncertainty that could corrupt the educational task, omit required content, detach required visuals, or allow student-facing HTML to appear complete when it is not.

This file defines issue types and release-blocking behavior. `04_VALIDATION_RULES_V4.md` defines when and how validators emit these issues.

## 2. Core doctrine

The rendered page image is the source of truth. Embedded PDF text, OCR text, layout blocks, extracted questions, normalized symbols, structured JSON, and generated HTML are hypotheses until checked against the rendered page image and reviewer-facing QA evidence.

The validator must not silently repair or ignore uncertainty. It must emit an issue, assign severity, preserve traceability to source page/block/exercise, and route unresolved risk to human review.

## 3. Severity model

| Severity | Meaning | Default release behavior |
|---|---|---|
| `critical` | Student task is missing, wrong, unanswerable, visually unsupported, or release gating failed. | Blocks clean student-facing HTML release. |
| `major` | Extracted content is likely wrong or incomplete, but review may repair or accept it. | Blocks release until fixed, reviewed, or explicitly downgraded with rationale. |
| `minor` | Local defect that does not prevent student answerability. | Does not block release if visible in QA and accepted. |
| `advisory` | Low-risk warning, audit note, or correction-memory candidate. | Does not block release. |

Escalate to `critical` when the issue changes the answer, removes required content, removes a required visual, hides a blocker from QA, or prevents traceability to the source page image.

## 4. Blocking policy

`blocks_student_html = true` means the page must not be released as a clean student-facing worksheet. A debug or review-only preview may exist only if clearly marked as blocked/incomplete.

Student-facing HTML release is blocked by any open `critical` issue and by any unreviewed `major` issue affecting task-bearing content.

## 5. Required issue record fields

Every issue in `json/issues.json` must include at least:

```json
{
  "issue_id": "sumbridge2_p001_contextual_coherence_failure_001",
  "issue_type": "contextual_coherence_failure",
  "severity": "major",
  "blocks_student_html": true,
  "status": "open",
  "confidence": "high",
  "source_id": "sumbridge2",
  "file": "sumbridge2.pdf",
  "page": 1,
  "page_image_path": "assets/page_images/sumbridge2_p001.png",
  "block_ids": ["sumbridge2_p001_b001"],
  "exercise_ids": [],
  "bbox": {"x0": 0, "y0": 0, "x1": 0, "y1": 0},
  "evidence": {
    "pdf_text": "...",
    "ocr_text": "...",
    "visible_text_summary": "..."
  },
  "description": "What went wrong or may be wrong.",
  "likely_cause": "Probable extraction/layout/OCR cause.",
  "recommended_human_action": "What reviewer should inspect or fix.",
  "suggested_fix": null,
  "validator_stage": "block_coherence",
  "created_utc": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Stable issue IDs should use:

```text
<source_id>_p<page3>_<issue_type>_<counter3>
```

## 6. Issue taxonomy

The table is intentionally compact. Implementations may add fields, but must preserve `issue_type`, severity semantics, human-review action, and blocking behavior.

| issue_type | Issue name | Description | Default severity | Detection method | Likely cause | Required human review action | Blocks student HTML? | Example |
|---|---|---|---|---|---|---|---|---|
| `source_identity_uncertain` | Source identity uncertain | File/page is not confirmed as active source workbook material. | critical | Source manifest, hash/page-count check, approved PDF list. | Handoff/spec/generated artifact mistaken for source. | Confirm source identity or reject file. | Yes | Audit references `sumbridge7.pdf`, but it is not active. |
| `source_page_not_in_approved_pilot` | Page not in approved pilot | Pipeline attempts to process a page outside the approved first-pilot set. | critical | Selected-page manifest vs pilot page list. | Batch scope creep or stale config. | Stop run or revise/approve pilot scope. | Yes | First pilot tries `sumbridge6.pdf` answer pages. |
| `page_render_failed` | Page render failed | Rendered page image is missing, unreadable, or incomplete. | critical | Render artifact existence/open/dimensions check. | PDF render failure, corrupt page, wrong index. | Re-render and verify page before extraction. | Yes | No page image exists for `sumbridge2.pdf` page 1. |
| `page_image_traceability_missing` | Page-image traceability missing | Block/exercise/issue cannot be traced to the rendered page image. | critical | Required path and metadata audit. | Generated from text-only intermediate artifacts. | Restore traceability and revalidate. | Yes | Exercise record lacks `page_image_path`. |
| `visual_asset_missing_or_broken` | Visual asset missing or broken | Rendered page image, crop, SVG, or visual-reference asset is missing, unreadable, or incorrectly linked. | critical | Asset existence/open/path check and QA link audit. | Failed crop/export, bad relative path, omitted visual generation. | Repair asset path or regenerate visual asset; revalidate linkage. | Yes if task-bearing or required visual | Number-line crop path exists in JSON but file does not open. |
| `ocr_error` | OCR error | OCR text is visibly wrong, garbled, or missing task text. | major | OCR vs rendered image and PDF text comparison. | Low image quality, font, layout, symbol recognition. | Check visible page image and correct or flag. | Yes if task-bearing | OCR reads `there` as `then`. |
| `ocr_low_confidence_task_text` | Low-confidence OCR in task text | OCR confidence is low for instructions, items, answers, labels, or symbols. | major | OCR confidence thresholds by block/word. | Small font, skew, graphics, handwriting-like marks. | Inspect image and confirm text. | Yes if unresolved | Low-confidence OCR on a fraction denominator. |
| `pdf_text_layer_incomplete` | Embedded PDF text incomplete | PDF text layer omits visible text or page content. | major | OCR/page-image coverage vs PDF text coverage. | Scanned text, image text, bad PDF encoding. | Use OCR/image as evidence; do not trust PDF text alone. | Yes if task-bearing | Visible problem appears in image but not PDF text. |
| `embedded_text_extraction_error` | Embedded text extraction error | PDF text exists but is garbled, out of order, or symbol-corrupted. | major | PDF text vs OCR/image alignment. | Bad text layer, encoding, reading-order extraction. | Review against image and prefer visually supported structure. | Yes if task-bearing | `SummerBridge` footer enters a prompt. |
| `ocr_pdf_text_disagreement` | OCR/PDF text disagreement | OCR and embedded text materially disagree. | major | Token, symbol, number, count, and bbox comparison. | OCR error, PDF extraction error, hidden text layer issue. | Compare both against rendered image. | Yes if unresolved and task-bearing | PDF says `110`; visible/OCR suggests `11¢`. |
| `missing_text` | Missing text | Visible task-bearing text is absent from extracted structure. | critical | Page-image/OCR/PDF coverage and item-count checks. | OCR/PDF omission, bad cropping, skipped block. | Add missing block/item or mark page blocked. | Yes | A visible numbered question is absent. |
| `duplicated_text` | Duplicated text | Text appears twice or as duplicate items/choices. | major | Duplicate token/block/exercise detection. | OCR and PDF text both ingested without deduplication. | Remove duplicate and verify count. | Yes if confusing | Same answer choice appears twice from OCR/PDF overlap. |
| `mangled_word` | Mangled word | Word is corrupted enough to change meaning or readability. | major | Dictionary/context check, OCR/PDF disagreement, semantic check. | OCR artifact, ligature, broken PDF encoding. | Correct from image or flag uncertain. | Usually yes if task-bearing | `principal` becomes `princlpal`. |
| `wrong_number` | Wrong number | Number, digit, comma, decimal, sign, or value is wrong. | critical | Numeric OCR/PDF comparison and semantic validators. | OCR digit confusion, dropped minus, PDF encoding. | Confirm visually and correct. | Yes | `47¢` becomes `470`. |
| `wrong_symbol` | Wrong symbol | Symbol is wrong, missing, or replaced. | critical | Symbol whitelist and image/PDF/OCR comparison. | OCR or PDF symbol corruption. | Confirm visible symbol and correct. | Yes | `<` becomes `=`. |
| `corrupted_math_operator` | Corrupted math operator | `+`, `-`, `×`, `÷`, `=`, `<`, `>`, absolute value, or fraction/operator layout is wrong. | critical | Math parser, visual alignment, symbol comparison. | Flattened math, OCR confusion, layout loss. | Recreate math from image or block. | Yes | `9×7` read as `9x?` or division. |
| `possible_cents_symbol_misread` | Possible cents-symbol misread | Money context suggests trailing zero or missing symbol may represent `¢`. | major | Coin/money validator, correction memory, OCR/PDF disagreement. | Cents sign dropped or read as zero. | Confirm against image; correct only with visual support. | Yes if unresolved | `Cammie has 3 coins worth 110` should be `11¢`. |
| `ambiguous_fraction_layout` | Ambiguous fraction layout | Fraction numerator/denominator or stacked layout may be flattened incorrectly. | major | Fraction parser, layout/bbox check, visual review. | PDF/OCR flattened stacked fractions. | Inspect image and recreate structure. | Yes if used to answer | `3/4` rendered as separate `3` and `4`. |
| `missing_answer_choices` | Missing answer choices | Choices, word bank, matching options, clue bank, or dropdown values are absent/incomplete. | critical | Choice-count and answer-bank attachment checks. | Detached block, column merge, crop omission. | Restore all choices and link to exercise. | Yes | Word Bank omitted from possessive-noun exercise. |
| `missing_answer_lines_or_blanks` | Missing answer lines or blanks | Visible blanks, answer lines, circles, boxes, or response areas are missing as inputs. | critical | Visual-field detection and input-count comparison. | Lines ignored as decoration; form conversion incomplete. | Add inputs matching visible answer fields. | Yes | A writing prompt has no textarea. |
| `wrong_input_type` | Wrong input type | Student control does not match task action. | major | Instruction verb and exercise-type validator. | Naive rendering template. | Change to appropriate input/control. | Yes if answerability affected | “Circle” rendered as text box only. |
| `broken_question_grouping` | Broken question grouping | Items, instructions, answer bank, visuals, or response fields are grouped incorrectly. | major | Exercise-structure validator and block adjacency. | Layout segmentation or reading-order error. | Reassign blocks and validate exercise structure. | Yes if unresolved | Money questions merged with noun exercise. |
| `instruction_question_separation_error` | Instruction separated from questions | Instruction is detached from the items it governs or attached to wrong items. | major | Instruction/item block linkage and proximity. | Bad block grouping, section boundary loss. | Attach instruction to correct exercise. | Yes if unresolved | “Write the singular or plural form” separated from noun list. |
| `contextual_coherence_failure` | Contextual coherence failure | Adjacent/merged text does not logically belong together. | major | Block coherence validator, semantic contrast. | Linear text extraction across visual regions. | Split/merge blocks according to page image. | Yes if prompt meaning changes | Abbreviation instruction merged with earthquake factoid. |
| `possible_layout_block_merge_error` | Possible layout block merge error | Separate visual regions may have been merged. | major | Bbox gaps, columns, shading, font/background signals. | Reading-order extraction ignored layout. | Inspect page image and split blocks if needed. | Yes if task-bearing | Sidebar included inside main instruction. |
| `columns_merged_incorrectly` | Columns merged incorrectly | Multi-column content is read across rows/columns in wrong order. | major | Column detection, row/column bbox sorting, item sequence check. | Naive line reading order. | Reconstruct columns and item sequence. | Yes if task-bearing | Abbreviation matching columns interleaved. |
| `table_reading_order_error` | Table read in wrong order | Table/grid rows, columns, headers, or cells are sequenced incorrectly. | major | Table structure detection and cell-order audit. | OCR/PDF reading order lost table geometry. | Recreate table from image; verify rows/columns. | Yes if used to answer | Fraction table rows detached from labels. |
| `grid_structure_missing_or_wrong` | Grid structure missing or wrong | Crossword, word-search, graph, chart, table, or coordinate grid is missing/distorted. | critical | Visual-region detection and grid asset validation. | Visual omitted; crop/SVG failed. | Preserve crop/SVG and verify labels/cells. | Yes | Crossword grid omitted from puzzle page. |
| `caption_or_label_separated_from_visual` | Caption/label separated from visual | Text that identifies a visual is detached or attached to wrong visual. | major | Visual-label proximity and reference matching. | Layout segmentation error. | Attach caption/label to correct visual. | Yes if needed | Number-line labels/tick marks detached. |
| `diagram_image_numberline_omitted` | Diagram/image/number line omitted | Required visual object is absent from structured/student output. | critical | Visual dependency and asset presence checks. | Visual region ignored as decoration. | Add crop/SVG or block page. | Yes | Number line omitted but integer questions remain. |
| `visual_reference_required_or_helpful` | Visual reference required/helpful | Prompt likely depends on a visual. | major | Keyword triggers plus layout/visual-region detection. | Visual dependency not classified. | Decide required/helpful; preserve or flag. | Yes if required | “Use the fraction table” without table asset. |
| `visual_reference_dependency_not_preserved` | Visual-reference dependency not preserved | Text references a visual, but the required visual is missing, broken, or insufficient. | critical | Cross-check dependency flags against visual assets. | Visual not cropped/recreated; asset broken. | Add/repair visual or block release. | Yes | “the number line” present in text but no number line shown. |
| `unresolved_deictic_visual_reference` | Unresolved visual/deictic reference | Phrases such as “the picture,” “chart,” “above,” “below,” “shown,” or “number line” lack preserved referent. | critical | Keyword/deictic-reference scan and visual-link audit. | Text extracted without associated visual. | Identify and attach referenced visual. | Yes | “shown below” but no diagram included. |
| `external_page_reference` | External page reference | Exercise depends on another page or resource not included in the validated context. | major | Reference-pattern scan: “page 75,” “see page,” etc. | Workbook cross-reference. | Include dependency or mark incomplete. | Yes if needed to answer | “Look at the letter on page 75…” without page 75. |
| `sidebar_factoid_detected` | Sidebar/factoid detected | Trivia/sidebar block identified; must not be treated as student prompt. | advisory | Role classifier: factoid labels, shaded/corner blocks, declarative trivia. | Workbook decorative/engagement sidebar. | Confirm omit/optional note; do not merge. | No unless merged | Earthquake factoid on abbreviation page. |
| `footer_or_decorative_text_in_student_output` | Footer/decorative text in student output | Footer, copyright, page number, decorative marks, or art text enters student task. | minor | Role classifier and repeated footer/header detection. | Poor block exclusion. | Remove from student output; keep traceability in review if needed. | Usually no; yes if prompt corrupted | `www.SummerBridgeActivities.com` appears in question. |
| `missing_visible_item` | Missing visible item | Visible numbered item, prompt, clue, sentence, or response line is absent. | critical | Item-count comparison against page image/OCR/PDF. | Skipped block, low-confidence OCR, table/column loss. | Add missing item or block page. | Yes | Clue 10 in crossword omitted. |
| `numbered_item_count_mismatch` | Numbered item count mismatch | Visible item count disagrees with extracted item count. | major | Number sequence and block/item reconciliation. | OCR/PDF duplicate, skipped item, page number confusion. | Verify item list and correct grouping. | Yes if unresolved | 12 visible math problems, 11 extracted. |
| `semantic_nonsense_from_extraction` | Semantic nonsense from extraction | Extracted prompt is grammatically or educationally nonsensical due to extraction. | major | Semantic sanity check and block-coherence analysis. | Merged unrelated blocks or dropped words. | Compare with image; repair structure/text. | Yes if task meaning unclear | “Draw lines between these words and their Earthquakes…” |
| `semantic_plausibility_failure` | Semantic plausibility failure | Problem is structurally valid text but implausible in context. | major | Exercise-specific validator. | Symbol/number/operator corruption. | Inspect source and correct/flag. | Yes if unresolved | Coin problem asks for 3 coins worth 110 cents in a worksheet showing 11¢. |
| `answer_key_or_solution_material_in_student_output` | Answer key in student output | Answer-page or filled solution content appears in student worksheet. | critical | Source/page classification, handwriting/answer-key detection, answer-section scan. | Answer pages processed as student pages. | Remove from student output; verify source page role. | Yes | `sumbridge6.pdf` answer section rendered as questions. |
| `correction_applied_without_evidence` | Correction applied without evidence | Text/symbol was changed without rendered-image support and audit trail. | major | Correction log vs evidence audit. | Over-aggressive normalization or correction memory. | Revert or document visual evidence. | Yes if task-bearing | Automatically changing all `110` to `11¢` without image check. |
| `issue_reporting_incomplete` | Issue reporting incomplete | Detected issues are absent from `issues.json`, reviewer QA, or processing report. | major | Issue-count reconciliation across artifacts. | Report generator skipped records. | Add records and rerun report stage. | Yes if hidden blocker | Visual issue appears in logs but not reviewer QA. |
| `reviewer_qa_missing_required_panel` | Reviewer QA missing required panel | Reviewer report lacks source image, extracted structure, OCR/PDF comparison, blocks, visuals, issues, or decisions. | major | Reviewer QA contract audit. | QA template incomplete. | Add missing panel before release. | Yes if review cannot verify | Review page shows only extracted text. |
| `final_qa_release_category_missing` | Final QA release category missing | Page/batch lacks release category and rationale. | major | Final QA report schema audit. | Report template incomplete. | Assign release status after issue review. | Yes until categorized | Page has issues but no `page_blocked`/`ready` status. |
| `student_html_generated_with_blockers` | Student HTML generated despite blockers | Clean student-facing output generated or marked ready while unresolved blockers remain. | critical | Release gate audit: HTML status vs open issues. | Stage-order failure; validation bypass. | Revoke release-ready status; fix/review issues. | Yes | Page with missing number line appears as complete worksheet. |

## 7. First-pilot regression issue expectations

The first pilot must at minimum prove that these issues can be detected and surfaced:

| Source page | Required issue behavior if failure or uncertainty occurs |
|---|---|
| `sumbridge2.pdf`, page 1 | Emit `contextual_coherence_failure`, `possible_layout_block_merge_error`, and/or `sidebar_factoid_detected` if the abbreviation instruction and earthquake factoid are at risk of merging. |
| `sumbridge2.pdf`, page 2 | Emit `possible_cents_symbol_misread`, `wrong_number`, `wrong_symbol`, `ocr_pdf_text_disagreement`, and/or `semantic_plausibility_failure` if cents values are uncertain. |
| `summerbridge trial.pdf`, page 5 | Emit `diagram_image_numberline_omitted`, `visual_reference_dependency_not_preserved`, `unresolved_deictic_visual_reference`, or `wrong_symbol` if the number line, tick labels, letter positions, minus signs, or comparison/absolute-value symbols are not preserved. |

## 8. Minimal issue status workflow

| Status | Meaning |
|---|---|
| `open` | Detected and unresolved. |
| `needs_human_review` | Requires reviewer decision before release. |
| `fixed` | Corrected and revalidated. |
| `accepted_with_rationale` | Reviewer accepts remaining risk; rationale required. |
| `false_positive` | Reviewer rejects issue; rationale required. |
| `deferred` | Known issue carried forward; page cannot be release-ready if blocker remains. |

## 9. Project-source maintenance rule

This taxonomy should remain concise and stable. Add a new issue type only when an observed failure cannot be represented by an existing type. Prefer enriching `evidence`, `validator_stage`, and `recommended_human_action` before expanding the vocabulary.
