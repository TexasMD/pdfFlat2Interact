# 01 — DOCVERT Pipeline Specification V4

Created: 2026-06-12  
Status: Draft canonical technical source  
Project: `docvert`  
Supersedes: prior Summer Bridge-specific v3 pipeline framing  
Preserves: v3 validation-first architecture, block-aware extraction, issue reporting, and correction memory doctrine

---

## 1. Purpose

`01_PIPELINE_SPEC_V4.md` defines the canonical pipeline specification for `docvert`.

`docvert` is a layout-aware, validation-first document AI pipeline for converting workbook-style educational PDFs into accurate, usable, interactive HTML webpages.

The goal is **not** to make a screenshot-like worksheet overlay. The goal is to extract the educational task from a static page into clean structured interactive content while preserving any visual reference required for a student to answer correctly.

This v4 spec preserves the best of Pipeline V3 but updates it for the broader `docvert` Project:

- Summer Bridge examples are regression tests, not the project identity.
- Handoff/specification files are not source workbook PDFs.
- Conversion must not run until actual source PDFs are supplied and intake passes.
- Reviewer-facing QA is not optional polish; it is a required validation artifact.
- Student-facing output must be generated from validated structured content, not raw extracted text lines.
- Every converted page must retain traceability back to the source PDF page and rendered page image.

---

## 2. Pipeline overview

### 2.1 One-sentence pipeline identity

`docvert` converts workbook-style educational PDFs into student-facing interactive HTML packages using rendered-page verification, OCR/embedded-text comparison, layout/block detection, semantic validation, issue reporting, correction memory, and human review.

### 2.2 Core doctrine

The rendered page image is the source of truth.

Embedded PDF text, OCR output, and extracted structured content are hypotheses until checked against:

1. the rendered page image,
2. embedded PDF text,
3. OCR/visible text,
4. layout/block segmentation,
5. block-role classification,
6. contextual block coherence,
7. symbol normalization,
8. semantic plausibility,
9. exercise completeness,
10. visual-reference requirements,
11. human review when uncertainty remains.

Project rule:

> Do not silently generate confident garbage. Flag uncertainty.

### 2.3 V4 pipeline summary

```text
0. Confirm source-PDF intake readiness
1. Intake source PDF batch
2. Render each page as an image
3. Extract embedded PDF text
4. Run OCR on rendered page image
5. Compare embedded text against OCR/visible text
6. Detect layout blocks and visual regions
7. Classify block roles
8. Run block coherence validation
9. Normalize text and symbols conservatively
10. Extract questions, instructions, answer banks, and exercise structure
11. Detect visual dependencies
12. Run semantic sanity checks and exercise-specific validators
13. Generate structured intermediate JSON
14. Generate issue report
15. Generate reviewer-facing QA HTML
16. Perform human review and correction
17. Update correction memory
18. Generate student-facing interactive HTML
19. Run final QA against source page images and issue records
20. Package outputs with relative links intact
```

### 2.4 Stage ordering rule

Reviewer-facing QA output should be generated **before or alongside** student-facing output.

Student output may be previewed during development, but it is not release-ready until final QA confirms:

- required visuals are present,
- issue records are surfaced,
- high-severity uncertainties are reviewed or explicitly carried forward,
- the student page is built from validated structured data.

---

## 3. Inputs and outputs

## 3.1 Required inputs

### 3.1.1 Source workbook PDFs

The only valid source documents for conversion are actual workbook-style educational PDFs intentionally provided for conversion.

The pipeline must not treat these as source PDFs:

- handoff package Markdown files,
- JSON schemas,
- prior generated HTML files,
- prior generated ZIP files,
- audit files,
- screenshots unless explicitly provided as source images,
- derived artifacts from earlier conversion attempts.

Each source PDF must have an intake record containing:

| Field | Required | Notes |
|---|---:|---|
| `source_id` | yes | Stable run-local identifier. |
| `filename` | yes | Original filename. |
| `file_hash` | yes | For reproducibility. |
| `page_count` | yes | Must be verified before conversion. |
| `source_status` | yes | `source_pdf`, `reference_only`, `generated_artifact`, or `rejected`. |
| `intended_batch` | yes | Batch/run name. |
| `permission_or_use_notes` | recommended | Project-specific handling notes. |
| `intake_warnings` | recommended | Any uncertainty about identity or provenance. |

### 3.1.2 Durable project sources

Future implementation/conversion work should read these durable sources before running conversion:

- `DOCVERT_HANDOFF_BASELINE.md`
- `00_PROJECT_CHARTER.md`
- `10_DECISION_LOG.md`
- `11_BACKLOG.md`
- `12_ARTIFACT_MAP.md`
- `01_PIPELINE_SPEC_V4.md`
- issue schema
- block-role schema
- correction memory
- critical regression tests

### 3.1.3 Runtime configuration

A batch run should have a configuration file derived from the v3 template but updated for v4:

```json
{
  "pipeline_version": 4,
  "render_pages": true,
  "extract_pdf_text": true,
  "run_ocr": "production_all_pages_or_selective_during_prototype",
  "layout_block_detection": true,
  "block_role_classification": true,
  "block_coherence_check": true,
  "symbol_normalization": true,
  "semantic_validators": [
    "coin_problem",
    "arithmetic",
    "fraction",
    "matching",
    "word_bank",
    "visual_reference",
    "completeness",
    "external_reference"
  ],
  "human_review_required_for": [
    "high_severity_issues",
    "visual_reference_required_or_helpful",
    "contextual_coherence_failure",
    "ambiguous_fraction_layout",
    "pdf_text_layer_incomplete",
    "missing_visible_item"
  ]
}
```

## 3.2 Required outputs

Each conversion batch must produce this minimum artifact set:

| Path | Purpose |
|---|---|
| `index.html` | Student-facing interactive worksheet. |
| `review.html` | Reviewer-facing QA interface. |
| `json/all_pages.json` | Complete structured extraction and page metadata. |
| `json/issues.json` | Machine-readable issue report. |
| `json/correction_memory.json` | Batch-applied and updated correction memory. |
| `json/block_roles.json` | Detected blocks, roles, confidence, and notes. |
| `processing_report.md` | Human-readable processing and QA summary. |
| `assets/page_images/` | Rendered source page images used as visual truth. |
| `assets/visual_refs/` | Cropped or recreated visual references used in student/review output. |
| `run_manifest.json` | Run metadata, source file hashes, tool versions, and output inventory. |

### 3.2.1 Optional but recommended outputs

| Path | Purpose |
|---|---|
| `json/ocr_text.json` | OCR text and OCR bounding boxes by page. |
| `json/pdf_text.json` | Embedded text extraction and text boxes by page. |
| `json/text_comparison.json` | OCR-vs-PDF-text comparison records. |
| `json/layout_blocks.json` | Pre-role block detection output. |
| `json/exercises.json` | Structured exercise records used to render student HTML. |
| `json/review_actions.json` | Human reviewer accept/edit/reject actions. |
| `json/regression_results.json` | Pass/fail results for known tests. |
| `final_qa_report.md` | Final release-readiness assessment. |

---

## 4. Processing stages

## Stage 0 — Source-PDF intake readiness

Purpose: prevent artifact contamination.

Before any conversion run:

1. Confirm source PDFs are actually present.
2. Reject handoff/spec/audit/generated files as source documents.
3. Verify page counts.
4. Compute file hashes.
5. Create `source_manifest.json`.
6. Record the intended batch name.
7. Mark unknown files as `needs_review`, not `source_pdf`.

Gate:

- If source PDFs are absent or ambiguous, stop. Do not convert.

## Stage 1 — Source PDF intake

For each accepted source PDF:

- assign `source_id`,
- store original filename,
- record page count,
- record hash,
- record batch membership,
- record any page exclusions or special handling notes.

Output:

- `source_manifest.json`
- source records inside `run_manifest.json`

## Stage 2 — Render each PDF page as an image

Each source page must be rendered to an image before extraction is trusted.

Rendered page images are used for:

- canonical visual review,
- OCR input,
- visual-reference cropping,
- layout detection,
- verification of missing text,
- final QA comparisons.

Minimum metadata per rendered page:

```json
{
  "source_id": "workbook_a",
  "file": "example.pdf",
  "page": 1,
  "image_path": "assets/page_images/workbook_a_p001.png",
  "width_px": 1700,
  "height_px": 2200,
  "dpi": 200,
  "render_tool": "...",
  "render_warnings": []
}
```

Rendering requirements:

- stable DPI across batch unless intentionally varied,
- page number in filename,
- no destructive cropping,
- preserve full page for traceability,
- log render errors.

## Stage 3 — Extract embedded PDF text

Embedded text extraction is fast and useful but untrusted.

It may provide:

- text runs,
- bounding boxes,
- font data,
- approximate reading order.

Known risks:

- missing visible text,
- broken reading order,
- symbol corruption,
- cents symbols misread or omitted,
- stacked fractions flattened,
- vertical arithmetic mangled,
- sidebars merged inline,
- visual labels detached from figures.

Output:

- `json/pdf_text.json`

## Stage 4 — Run OCR on rendered page image

OCR is required for visible-text verification.

In production mode, OCR should run on every page. During prototypes, OCR may run selectively on test pages, but any release candidate needs visible-text coverage.

OCR should ideally produce:

- text,
- word-level or line-level bounding boxes,
- confidence scores,
- page coordinates,
- language/model metadata.

OCR is especially important for:

- text absent from embedded PDF layer,
- symbol verification,
- diagram/map/number-line labels,
- small captions,
- handwritten-style fonts if present,
- checking whether a visual contains text required for the exercise.

Output:

- `json/ocr_text.json`

## Stage 5 — OCR and embedded text comparison

Purpose: detect disagreement between what the PDF text layer says and what the rendered page appears to show.

Comparison should check:

1. full-page text coverage,
2. per-block text coverage,
3. item counts,
4. numbered sequence continuity,
5. symbol differences,
6. suspicious numeric transformations,
7. labels in visuals,
8. missing or extra text,
9. major reading-order divergence.

Comparison output should include:

```json
{
  "file": "example.pdf",
  "page": 2,
  "comparison_type": "symbol_disagreement",
  "pdf_text": "110",
  "ocr_text": "11¢",
  "bbox": {"x0": 430, "y0": 612, "x1": 470, "y1": 640},
  "confidence": 0.86,
  "issue_type": "possible_cents_symbol_misread",
  "recommended_action": "confirm against rendered image; correct only if visually supported"
}
```

Disagreement handling:

| Condition | Action |
|---|---|
| OCR sees text missing from PDF layer | Flag `pdf_text_layer_incomplete` or `missing_visible_item`. |
| PDF text and OCR disagree on symbols | Flag symbol-specific issue. |
| PDF text has implausible numeric value in semantic context | Run semantic validator and flag if suspicious. |
| OCR confidence is low | Keep both hypotheses and require review. |
| Both PDF text and OCR agree but semantic validator fails | Flag `semantic_plausibility_failure`. |

## Stage 6 — Layout/block detection

Purpose: segment the page into meaningful visual and semantic regions before extracting exercises.

A block is not just a line of text. It is a page region that may contain:

- instruction text,
- exercise items,
- answer choices,
- word bank,
- factoid/sidebar,
- figure/map/chart/table/number line,
- caption or label,
- header/footer/decorative content.

### 6.1 Block detection inputs

Block detection may use:

- PDF text boxes,
- OCR bounding boxes,
- rendered image segmentation,
- whitespace gaps,
- columns,
- shaded regions,
- borders/boxes,
- font size/weight changes,
- page position,
- repeated footer/header patterns.

### 6.2 Minimum block record

Each block should preserve:

```json
{
  "block_id": "sourceA_p001_b003",
  "source_id": "sourceA",
  "file": "example.pdf",
  "page": 1,
  "text": "Earthquakes can cause rivers to temporarily flow backwards.",
  "bbox": {"x0": 410, "y0": 42, "x1": 705, "y1": 115},
  "source_methods": ["pdf_text", "ocr", "vision_segmentation"],
  "visual_features": {
    "font_size_estimate": null,
    "font_weight_estimate": "bold-ish",
    "background": "shaded",
    "position": "upper_right",
    "border_or_box": false,
    "column": "right",
    "nearby_visual_elements": []
  },
  "role": "factoid_sidebar",
  "role_confidence": 0.91,
  "include_in_student_page": false,
  "include_in_review_page": true,
  "nearby_block_ids": ["sourceA_p001_b001", "sourceA_p001_b004"],
  "coherence_notes": "Semantically unrelated to abbreviation-matching instruction.",
  "issues": []
}
```

### 6.3 Block role vocabulary

Durable block roles:

| Role | Meaning | Student output default |
|---|---|---|
| `main_instruction` | Tells the student what to do. | Include. |
| `exercise_items` | Questions/problems/prompts the student answers. | Include. |
| `answer_bank` | Word bank or choices used by exercise items. | Include when attached to exercise. |
| `visual_reference` | Map, graph, chart, number line, diagram, table, picture, grid, or other visual needed to answer. | Include if required/helpful. |
| `factoid_sidebar` | Trivia or informational sidebar not part of the task. | Omit or optional note; never merge into prompt. |
| `decorative_text` | Nonessential decoration. | Omit. |
| `footer` | Copyright, URL, page number, publisher metadata. | Omit. |
| `page_header` | Page/day/section marker. | Include only if pedagogically useful. |
| `caption_or_label` | Label tied to a visual. | Include with visual if relevant. |
| `external_reference` | Instruction referring to another page/resource. | Flag. Include only if dependency is satisfied. |
| `unknown` | Role uncertain. | Review required before release. |

## Stage 7 — Block role classification

Purpose: classify each detected block before exercise extraction.

Role classification should consider:

- text content,
- imperative vs declarative sentence form,
- page position,
- block size,
- font and background,
- nearby visual elements,
- labels such as `FACTOID`,
- relation to adjacent blocks,
- repeated headers/footers across pages,
- expected workbook page patterns.

Classification must output:

- role,
- confidence,
- rationale or notes,
- include/exclude recommendation for student page,
- review requirement if confidence is low.

## Stage 8 — Block coherence validation

Formal name: **layout-aware contextual coherence validation**.  
Short name: **block coherence check**.

Purpose: decide whether nearby or sequential blocks logically belong together.

The core question:

> Do these text blocks logically belong together as one instruction, question, or exercise section?

### 8.1 Signals that blocks may be separate

- different background or shading,
- different font weight or size,
- large horizontal/vertical gap,
- boxed region,
- corner/sidebar placement,
- label such as `FACTOID`,
- unrelated topic,
- declarative trivia adjacent to imperative instruction,
- sudden switch from exercise command to informational fact,
- broken sentence only repairable by skipping an intervening block,
- multi-column layout that creates false reading order.

### 8.2 Required behavior

If a block sequence appears as:

```text
Draw lines between these words and their
Earthquakes can cause rivers to temporarily flow backwards.
abbreviations.
```

The validator must consider:

- the first and third fragments may belong to the same instruction,
- the middle factoid may be a separate sidebar,
- the raw reading order is likely wrong.

Correct structure:

```json
{
  "main_instruction": "Draw lines between these words and their abbreviations.",
  "factoid_sidebar": "Earthquakes can cause rivers to temporarily flow backwards.",
  "exercise_type": "matching"
}
```

If uncertainty remains, emit issues:

- `contextual_coherence_failure`,
- `possible_layout_block_merge_error`,
- `sidebar_factoid_detected`.

## Stage 9 — Conservative symbol normalization

Purpose: normalize typography and symbols without hiding extraction uncertainty.

Symbols to normalize and validate:

- cents sign: `¢`,
- multiplication sign: `×`,
- division sign: `÷`,
- minus sign/en dash/hyphen variants,
- comparison signs: `<`, `>`, `=`,
- apostrophes and quotation marks,
- stacked fractions,
- fraction bars,
- decimal points,
- commas in large numbers,
- degree symbols,
- map/chart labels,
- answer blank markers.

Rule:

- Correct only when confidence is high and rendered-page evidence supports the correction.
- Otherwise, preserve competing hypotheses and flag an issue.
- Every correction must be logged in the issue/correction trail.

Example:

| Extracted | Context | Suspected visible text | Action |
|---|---|---|---|
| `110` | coin/money problem | `11¢` | Flag or correct after visual confirmation. |
| `470` | coin/money problem | `47¢` | Flag or correct after visual confirmation. |
| `T + 4` | fraction layout | stacked fraction | Flag `ambiguous_fraction_layout`. |

## Stage 10 — Question and instruction extraction

Purpose: convert classified blocks into structured educational content.

Extraction should identify:

- page sections,
- main instructions,
- sub-instructions,
- passages,
- question groups,
- numbered items,
- answer blanks,
- choices,
- word banks,
- matching columns,
- tables,
- visual references,
- captions and labels,
- drawing/writing areas,
- external references.

### 10.1 Structured exercise object

Minimum exercise object:

```json
{
  "exercise_id": "sourceA_p001_ex01",
  "source_id": "sourceA",
  "file": "example.pdf",
  "page": 1,
  "section_title": "Abbreviations",
  "exercise_type": "matching",
  "instruction_block_ids": ["sourceA_p001_b001"],
  "item_block_ids": ["sourceA_p001_b005"],
  "visual_reference_ids": [],
  "answer_bank_block_ids": ["sourceA_p001_b006"],
  "items": [
    {
      "item_id": "sourceA_p001_ex01_i001",
      "prompt": "Doctor",
      "input_type": "dropdown",
      "choices": ["Dr.", "St.", "Ave."],
      "source_block_ids": ["sourceA_p001_b005"]
    }
  ],
  "validation_status": "needs_review",
  "issues": []
}
```

### 10.2 Exercise-type handling

| Exercise type | Preferred interactive conversion |
|---|---|
| Arithmetic | Short answer boxes. |
| Vertical arithmetic | Recreated stacked layout or clear equivalent with answer input. |
| Fill-in-the-blank | Inline input or dropdown. |
| Word bank | Dropdowns populated from bank. |
| Multiple choice | Radio buttons. |
| Matching | Dropdown table first; drag/drop optional later. |
| Ordering | Number dropdowns. |
| Reading response | Passage plus text areas. |
| Writing prompt | Textarea. |
| Drawing prompt | Canvas or drawing-description area. |
| Geometry drawing | SVG/canvas with reference segments. |
| Number line | SVG/cropped number line plus inputs. |
| Map labeling | Map image/SVG plus labels/dropdowns. |
| Graph/chart completion | Visual plus inputs. |
| Crossword/word search | Preserve grid or provide structured equivalent. |
| Suffix wheel | Normalize into suffix headings unless wheel geometry matters. |
| Checklist/activity idea | Checklist. |
| External-page task | Flag unless referenced page/resource is included. |

### 10.3 Factoid handling

Factoids are usually not part of the student task.

Default behavior:

- classify as `factoid_sidebar`,
- include in review page,
- omit from student page or show as optional note only if configured,
- never merge into main instruction or prompt.

## Stage 11 — Visual dependency detection

Purpose: determine whether a student can answer from extracted text alone or needs a visual.

A prompt or exercise likely requires a visual if it contains or refers to:

- map,
- number line,
- graph,
- chart,
- table,
- diagram,
- figure,
- picture,
- grid,
- word search,
- crossword,
- fraction table,
- suffix wheel,
- geometry line/angle/shape,
- “shown below,”
- “use the picture,”
- “label,”
- “circle,”
- “underline,”
- “draw,”
- “complete this graph,”
- “regions,”
- “time zone.”

### 11.1 Visual handling choices

| Visual type | Preferred handling |
|---|---|
| Simple number line | Recreate as SVG if geometry is clear; otherwise crop. |
| Map | Crop/render source region unless a faithful SVG is available. |
| Graph/chart | Recreate only if all axes/labels/data are clear; otherwise crop. |
| Geometry figure | Recreate as SVG/canvas if possible; otherwise crop. |
| Word-search/crossword grid | Preserve grid image or recreate structured grid. |
| Table | Recreate as HTML table if structure is unambiguous; otherwise crop. |
| Picture-dependent prompt | Crop picture region. |
| Complex or uncertain visual | Crop source region and flag for review. |

### 11.2 Visual dependency issue rule

If an exercise needs a visual and the visual is missing or uncertain, flag:

- `visual_reference_required_or_helpful`.

Student output must either:

- include the visual reference, or
- clearly mark the page/exercise as incomplete or requiring review.

Answer boxes without the required visual are not acceptable.

## Stage 12 — Semantic sanity checks

Purpose: catch extraction errors that are not obvious from text comparison alone.

Semantic sanity checks ask:

> Does the extracted task make educational, mathematical, and contextual sense for the surrounding page?

### 12.1 Validator categories

Required validator categories:

1. visible-text verification,
2. layout block segmentation validation,
3. block role validation,
4. block coherence validation,
5. symbol normalization validation,
6. semantic plausibility validation,
7. visual-reference validation,
8. exercise completeness validation,
9. issue reporting validation,
10. correction-memory update validation.

### 12.2 Coin/money validator

For coin problems:

1. detect money/coin context,
2. parse coin count,
3. parse target value,
4. solve using standard denominations: penny, nickel, dime, quarter,
5. determine whether the result is plausible for grade-level coin problems,
6. check whether a trailing-zero value likely represents a missing cents symbol,
7. flag or correct only with visual confirmation.

Flag if:

- no standard solution exists,
- too many solutions exist when a unique/simple one seems expected,
- target value is implausible,
- numeric text suggests a missing cents symbol,
- OCR and embedded text disagree.

### 12.3 Arithmetic validator

Check:

- operands are present,
- operator is present,
- result blank/input is present,
- numbering sequence is complete,
- visible item count matches extracted item count,
- vertical layout is preserved or accurately converted.

Flag:

- missing operator,
- missing visible item,
- implausible expression,
- broken vertical arithmetic layout,
- numbered item mismatch.

### 12.4 Fraction validator

Check:

- numerator and denominator are identified,
- fraction bar exists or is reconstructed,
- common denominators/operations make sense,
- stacked layout has not been flattened incorrectly.

Flag:

- flattened fraction,
- ambiguous numerator/denominator,
- missing fraction bar,
- visual reconstruction required.

### 12.5 Matching/column validator

Check:

- left and right columns are detected separately,
- options are not interleaved by reading order,
- all match targets are present,
- dropdown choices are complete,
- factoids/sidebars are not included as match choices.

### 12.6 Word-bank validator

Check:

- word bank is detected,
- word bank is attached to correct exercise section,
- all fill-in blanks have available choices if dropdown mode is used,
- decorative text is not mistaken for word-bank content.

### 12.7 Completeness validator

Check:

- visible numbered items vs extracted numbered items,
- expected sequence continuity,
- count of blanks vs count of input controls,
- answer choices present when prompt says choose/circle,
- passage present when questions depend on passage,
- visuals present when prompt depends on visual,
- external references flagged when unresolved.

---

## 5. Intermediate artifacts

V4 requires transparent, inspectable intermediate artifacts.

| Artifact | Required | Purpose |
|---|---:|---|
| `source_manifest.json` | yes | Source file identity, page counts, hashes, intake status. |
| `assets/page_images/*.png` | yes | Rendered page images used as visual truth. |
| `json/pdf_text.json` | yes | Embedded PDF text hypothesis. |
| `json/ocr_text.json` | yes in production | OCR visible-text hypothesis. |
| `json/text_comparison.json` | yes | OCR-vs-embedded comparison and discrepancies. |
| `json/layout_blocks.json` | yes | Detected block geometry before role classification. |
| `json/block_roles.json` | yes | Block roles, confidence, and coherence notes. |
| `json/exercises.json` | yes | Structured exercise objects for rendering. |
| `json/all_pages.json` | yes | Full joined page-level structure. |
| `json/issues.json` | yes | All suspicious or uncertain extraction items. |
| `json/correction_memory.json` | yes | Applied, updated, and confirmed correction rules. |
| `json/review_actions.json` | recommended | Human review decisions. |
| `processing_report.md` | yes | Run summary and open issues. |
| `final_qa_report.md` | recommended | Release-readiness decision. |
| `run_manifest.json` | yes | Run metadata and output inventory. |

Intermediate files must be plain JSON/Markdown/HTML where possible.

Do not rely on notebook memory, chat memory, hidden state, or untracked temporary files.

---

## 6. Issue taxonomy

## 6.1 Durable issue types

| Issue type | Default severity | Meaning |
|---|---|---|
| `possible_cents_symbol_misread` | high | Money/coin context suggests a trailing zero may be a missing cents symbol. |
| `visual_reference_required_or_helpful` | medium | Prompt depends on map, graph, diagram, number line, table, picture, or spatial layout. |
| `contextual_coherence_failure` | high | Adjacent or merged text blocks do not logically belong together. |
| `possible_layout_block_merge_error` | high | Text from separate visual regions may have been merged by reading-order extraction. |
| `sidebar_factoid_detected` | low | Factoid/sidebar block was identified and should not be treated as a prompt. |
| `pdf_text_layer_incomplete` | high | Embedded PDF text is sparse or missing relative to rendered page image. |
| `numbered_item_count_mismatch` | medium | PDF text and OCR/visible text disagree about number of worksheet items. |
| `semantic_plausibility_failure` | high | Extracted problem does not make educational or mathematical sense. |
| `ambiguous_fraction_layout` | high | Fraction layout is likely corrupted or ambiguous. |
| `external_page_reference` | medium | Question depends on another page/resource not included in current context. |
| `missing_visible_item` | high | Visible numbered problem or prompt is absent from extracted structure. |

## 6.2 V4 recommended additional issue types

These should be added as implementation matures:

| Issue type | Default severity | Meaning |
|---|---|---|
| `low_ocr_confidence` | medium | OCR confidence is too low to rely on extracted text. |
| `ocr_pdf_text_disagreement` | medium | OCR and embedded text differ meaningfully. |
| `uncertain_block_role` | medium | Block role confidence is below threshold. |
| `word_bank_detached` | medium | Word bank exists but cannot be confidently attached to an exercise. |
| `matching_columns_interleaved` | high | Left/right matching columns may have been flattened incorrectly. |
| `vertical_math_layout_uncertain` | high | Vertical arithmetic layout may have lost operands/operators. |
| `student_output_blocked_by_high_issue` | high | High-severity unresolved issue prevents release-ready student output. |
| `visual_crop_uncertain` | medium | Visual crop may omit needed labels/geometry. |
| `decorative_text_included` | medium | Footer/decorative text entered student content. |
| `review_required` | varies | Catchall marker when release requires human inspection. |

## 6.3 Issue record requirements

Every issue record must include:

```json
{
  "issue_id": "sourceA_p002_i004_issue001",
  "pipeline_version": 4,
  "file": "example.pdf",
  "source_id": "sourceA",
  "page": 2,
  "section": "Coins",
  "block_id": "sourceA_p002_b014",
  "exercise_id": "sourceA_p002_ex03",
  "item_id": "sourceA_p002_ex03_i004",
  "issue_type": "possible_cents_symbol_misread",
  "severity": "high",
  "confidence": "medium",
  "extracted_text": "Cammie has 3 coins worth 110.",
  "alternate_hypotheses": ["Cammie has 3 coins worth 11¢."],
  "visual_evidence": {
    "page_image": "assets/page_images/sourceA_p002.png",
    "bbox": {"x0": 300, "y0": 500, "x1": 640, "y1": 540}
  },
  "reason": "Coin context plus trailing-zero value suggests cents symbol corruption.",
  "recommended_action": "Review rendered image; correct to 11¢ only if visually confirmed.",
  "review_status": "unreviewed"
}
```

## 6.4 Issue propagation rule

Every issue must appear in:

1. `json/issues.json`,
2. `review.html`,
3. `processing_report.md`.

High-severity unresolved issues must also appear as warning badges or release blockers in student-facing output unless the page is intentionally excluded.

---

## 7. Correction memory behavior

## 7.1 Purpose

Correction memory stores reusable rules and human-confirmed corrections so repeated extraction failures are not fixed manually again and again.

Correction memory is not a license for blind autocorrection.

## 7.2 Correction memory categories

Correction memory should support:

- OCR-symbol rules,
- layout/coherence rules,
- exercise-type rules,
- visual-reference rules,
- human-confirmed corrections,
- source/document-specific exceptions,
- negative rules where a tempting correction should not be applied.

## 7.3 Seed patterns to preserve

Preserve these v3 seed patterns:

| Pattern | Behavior |
|---|---|
| Coin/money trailing zero | In money context, `110` may indicate `11¢`; flag or correct only after visual confirmation. |
| Visual dependency keywords | Map/number line/graph/chart/draw/label/etc. should trigger visual preservation or review. |
| Factoid/sidebar separation | Factoid text should not merge into exercise instructions. |
| Visual styling as block boundary | Different background/font/position can create likely block boundary. |
| Fraction layout protection | Stacked fractions should not be trusted as flattened text. |

## 7.4 Correction application rule

Each correction-memory rule should specify:

```json
{
  "id": "money_cents_trailing_zero",
  "category": "ocr_symbol_correction",
  "context": "money_coin_problem",
  "trigger": "trailing_zero_value_near_coin_terms",
  "suggested_correction": "replace trailing zero with cents sign",
  "allowed_action": "flag_or_correct_after_visual_confirmation",
  "requires_visual_confirmation": true,
  "confidence_boost": 0.35,
  "logs_issue_type": "possible_cents_symbol_misread"
}
```

A rule may:

- increase suspicion,
- suggest a correction,
- require review,
- block student release,
- automatically correct only when preconditions are met.

A rule must not:

- silently alter content without a log,
- override rendered-page evidence,
- erase competing hypotheses,
- treat a prior example as universally true.

## 7.5 Human-confirmed corrections

After human review, accepted corrections should be stored as:

- source-specific correction if unique to a page/document,
- pattern-based rule if likely reusable,
- negative example if the validator produced a false positive.

Each accepted correction should preserve:

- original extracted text,
- corrected text/structure,
- source page,
- block IDs,
- reviewer action,
- timestamp if available,
- confidence after review,
- whether it may be reused automatically.

---

## 8. Human review workflow

## 8.1 Review philosophy

Human review is part of the pipeline, not an emergency patch after bad output.

The review workflow exists to answer:

- Did extraction miss visible content?
- Did OCR or PDF text corrupt a symbol?
- Did layout merge unrelated blocks?
- Did the exercise remain educationally answerable?
- Did required visuals survive?
- Are unresolved issues clearly visible?

## 8.2 Review statuses

Each issue, block, exercise, and page may have review status:

| Status | Meaning |
|---|---|
| `unreviewed` | Not yet checked by human. |
| `accepted` | Extraction/correction accepted. |
| `edited` | Human changed extracted structure/text. |
| `rejected` | Extraction is wrong and should not be used. |
| `needs_more_context` | Page depends on missing source/visual/page. |
| `deferred` | Known issue intentionally carried forward. |
| `blocked` | Student-facing release should not proceed. |

## 8.3 Required review triggers

Human review is required for:

- high-severity issues,
- contextual coherence failures,
- possible layout block merge errors,
- missing visible items,
- PDF text layer incomplete issues,
- ambiguous fractions,
- visual references required or uncertain,
- external page references,
- low-confidence block roles,
- semantic plausibility failures.

## 8.4 Review output

Human review actions should be saved as `json/review_actions.json` or incorporated into `json/correction_memory.json` with a traceable record.

Minimum review action:

```json
{
  "review_action_id": "ra_000001",
  "target_type": "issue",
  "target_id": "sourceA_p001_issue003",
  "action": "edited",
  "before": "Draw lines between these words and their Earthquakes can cause rivers to temporarily flow backwards abbreviations.",
  "after": {
    "main_instruction": "Draw lines between these words and their abbreviations.",
    "factoid_sidebar": "Earthquakes can cause rivers to temporarily flow backwards."
  },
  "update_correction_memory": true,
  "notes": "Factoid is visually separated in upper-right shaded/sidebar region."
}
```

---

## 9. Reviewer-facing HTML requirements

`review.html` is the QA cockpit for the batch.

It must allow a reviewer to see what the pipeline thought happened and why it may be wrong.

## 9.1 Required content

Reviewer HTML must show, per page:

- rendered source page image,
- extracted embedded PDF text,
- OCR text,
- detected blocks,
- block bounding boxes or bbox list,
- block roles and confidence,
- block coherence notes,
- visual-reference status,
- structured exercise extraction,
- issues and severity,
- suggested corrections,
- links or references to JSON records,
- source filename and page number.

## 9.2 Required interactions for first useful version

Minimum viable reviewer HTML can be read-only, but it must support:

- page navigation,
- issue filtering by severity/type,
- source image display,
- block list with role labels,
- issue list tied to page/block/exercise/item,
- visible warning for high-severity unresolved issues.

## 9.3 Recommended interactions for later versions

Add:

- overlay block boxes on rendered page image,
- toggle OCR/PDF/block overlays,
- accept/edit/reject issue actions,
- inline text correction,
- structured exercise correction,
- export correction patch,
- update correction memory from accepted human review,
- compare current run to regression snapshot.

## 9.4 Reviewer HTML must not hide uncertainty

Reviewer output is wrong if it makes the page look clean while burying:

- low OCR confidence,
- symbol disagreement,
- block merge risk,
- missing visuals,
- incomplete embedded text,
- unresolved high-severity issues.

---

## 10. Student-facing HTML requirements

`index.html` is the student-facing interactive worksheet.

It must be clean, usable, and based on validated structured content.

## 10.1 Required content

Student HTML should include:

- clean exercise instructions,
- question/item text,
- appropriate answer controls,
- required visual references,
- section/page organization,
- review warning badges for flagged pages,
- local save if possible,
- print/save-as-PDF support,
- source traceability metadata hidden or available in developer/review mode.

## 10.2 Input controls by exercise type

| Exercise type | Student control |
|---|---|
| Short answer | Text input. |
| Arithmetic | Short answer input. |
| Fill-in-the-blank | Inline input or dropdown. |
| Word bank | Dropdowns populated from word bank. |
| Multiple choice | Radio buttons. |
| Matching | Dropdown table first. |
| Ordering | Number dropdowns. |
| Writing prompt | Textarea. |
| Drawing prompt | Canvas or drawing-description box. |
| Graph/chart/map/number line | Visual reference plus inputs. |
| Checklist/activity | Checkboxes. |

## 10.3 Student HTML exclusion rules

Do not include as student work:

- footer/copyright/publisher metadata,
- decorative glyphs,
- page URLs,
- unrelated factoids as prompts,
- sidebars merged into instructions,
- extraction warnings hidden from reviewer,
- unresolved high-severity issue content as if correct.

## 10.4 Visual-reference rule

If a question depends on a visual, the student page must include the visual or clearly mark the exercise as incomplete/review-required.

A page that asks about a number line without showing the number line is a failed conversion.

## 10.5 Student output generation rule

Student HTML must be generated from:

- `json/exercises.json`, or
- equivalent validated structured content inside `json/all_pages.json`.

It must not be generated directly from raw PDF text lines or OCR text lines.

---

## 11. Final QA requirements

Final QA decides whether the batch is release-ready.

## 11.1 Required QA checks

Before release/package handoff:

1. Every source PDF has intake status `source_pdf`.
2. Every page has a rendered image.
3. Every page has embedded text extraction output, even if empty.
4. Production runs have OCR/visible-text output or a documented exception.
5. OCR-vs-PDF-text comparison completed.
6. Layout blocks exist for every page.
7. Block roles exist with confidence scores.
8. Block coherence validation completed.
9. Structured exercises exist for student-rendered pages.
10. Visual dependencies are satisfied or flagged.
11. Semantic validators completed.
12. All issues appear in `issues.json`, `review.html`, and `processing_report.md`.
13. High-severity unresolved issues are listed in final QA.
14. Student HTML includes warning badges for flagged pages.
15. Required visuals are included or page is blocked/incomplete.
16. Correction memory updates are saved.
17. Relative links work locally.
18. Package does not depend on notebook/session memory.

## 11.2 Release categories

| Category | Meaning |
|---|---|
| `release_ready` | No blocking issues; required visuals and QA checks pass. |
| `release_with_warnings` | Non-blocking issues remain and are clearly surfaced. |
| `review_required` | Human review required before student use. |
| `blocked` | Output is not safe/usable as student worksheet. |

## 11.3 Final QA report

`final_qa_report.md` should include:

- batch name,
- source PDFs processed,
- page count,
- tool/version metadata,
- issue counts by severity/type,
- pages requiring review,
- high-severity unresolved issues,
- visual-reference status summary,
- regression-test results,
- correction-memory updates,
- known limitations,
- release category.

---

## 12. Known failure modes

The pipeline must preserve and test against these known failures.

## 12.1 Cents symbol misread or omitted

Visible text such as `11¢` may become `110`.

Detection:

- money/coin context,
- trailing zero values,
- OCR comparison,
- semantic coin-solution validation,
- rendered image review.

Action:

- flag `possible_cents_symbol_misread`,
- correct only if visually confirmed,
- log correction.

## 12.2 Embedded PDF text missing visible problem

A visible item may not appear in the embedded text layer.

Detection:

- OCR comparison,
- item count comparison,
- numbering sequence checks,
- rendered page review.

Action:

- flag `pdf_text_layer_incomplete`, `numbered_item_count_mismatch`, or `missing_visible_item`.

## 12.3 Visual reference omitted

A generated student page may include answer boxes but omit the required visual.

Detection:

- visual dependency keywords,
- layout visual region detection,
- semantic check for answerability.

Action:

- include SVG/crop/rendered visual,
- or flag `visual_reference_required_or_helpful` and block release if necessary.

## 12.4 Factoid/sidebar merged with instruction

Sidebars may be read inline with instructions.

Detection:

- layout segmentation,
- sidebar/factoid markers,
- background/position differences,
- declarative trivia adjacent to imperative instruction,
- block coherence validation.

Action:

- separate blocks,
- classify factoid as `factoid_sidebar`,
- flag if uncertain.

## 12.5 Stacked fractions flattened

Stacked fractions may be turned into nonsensical text.

Action:

- preserve visual crop or reconstruct structurally,
- flag `ambiguous_fraction_layout` when uncertain.

## 12.6 Vertical arithmetic flattened incorrectly

Vertical arithmetic may lose operands or operators.

Action:

- reconstruct visually if possible,
- otherwise flag `vertical_math_layout_uncertain` or `semantic_plausibility_failure`.

## 12.7 Matching exercises flattened/interleaved

Left/right columns can be interleaved.

Action:

- use layout columns,
- preserve sides/options,
- render as dropdown matching table.

## 12.8 Word banks detached

Word banks may be lost or attached to the wrong section.

Action:

- detect answer-bank block,
- link to section/exercise,
- flag `word_bank_detached` if uncertain.

## 12.9 Decorative/footer text included

Footer/copyright/page metadata may enter student content.

Action:

- classify as `footer` or `decorative_text`,
- omit from student output,
- flag `decorative_text_included` if it leaks.

## 12.10 External page reference

A prompt may require another page.

Action:

- flag `external_page_reference`,
- include referenced page/resource if available,
- otherwise mark not self-contained.

---

## 13. Pilot execution plan

## 13.1 Pilot goal

The v4 pilot should prove the architecture works before large-scale conversion.

It should show that `docvert` can:

- intake actual source PDFs safely,
- render pages,
- compare embedded text and OCR,
- detect layout blocks,
- assign block roles,
- separate unrelated factoids/sidebars,
- identify visual dependencies,
- produce reviewer HTML,
- generate student HTML from structured content,
- write issue records and correction memory,
- pass or properly flag critical regression cases.

## 13.2 Pilot source requirements

Do not run the pilot until source PDFs are uploaded or mounted and intake passes.

Seed PDFs, if available, may include:

- `sumbridge2.pdf`,
- `sumbridge3.pdf`,
- `sumbridge4.pdf`,
- `summerbridge trial.pdf` for the 19-page number-line regression.

These are seed tests only. They do not define project scope.

## 13.3 Pilot phases

### Phase A — Intake and render smoke test

1. Confirm source PDFs are present.
2. Build `source_manifest.json`.
3. Render first page of each PDF.
4. Verify page image paths and dimensions.
5. Stop if rendering fails.

Done when:

- every source has verified page count,
- first page renders correctly,
- no handoff/spec/generated file is misclassified as a source PDF.

### Phase B — Critical regression page extraction

Start with the factoid separation regression:

- target: `sumbridge2.pdf`, page 1,
- expected main instruction: `Draw lines between these words and their abbreviations.`,
- expected factoid/sidebar: `Earthquakes can cause rivers to temporarily flow backwards.`,
- expected exercise type: matching/dropdown abbreviations.

Done when:

- blocks are separated,
- roles are assigned,
- coherence validator passes or flags appropriate issues,
- reviewer HTML makes the structure obvious.

### Phase C — Symbol/semantic regression

Run the coin/cents test:

- target: `sumbridge2.pdf`, page 2,
- expected behavior: detect/correct or flag values such as `11¢` misread as `110`,
- required validators: OCR comparison, symbol normalization, coin semantic plausibility.

Done when:

- suspected cents errors are detected,
- corrections are logged only if visually confirmed,
- unresolved uncertainty appears in `issues.json`, `review.html`, and `processing_report.md`.

### Phase D — Visual-reference regression

Run the number-line test:

- target: 19-page trial PDF page 5, if source is available,
- expected behavior: preserve or recreate the number line,
- failure condition: answer boxes without number line.

Done when:

- visual dependency is detected,
- number line appears in student/review output or page is blocked,
- issue record is emitted if uncertain.

### Phase E — Minimal batch output

Process a small batch only after regression pages pass or properly flag issues.

Minimum batch outputs:

- `index.html`,
- `review.html`,
- `json/all_pages.json`,
- `json/issues.json`,
- `json/correction_memory.json`,
- `json/block_roles.json`,
- `processing_report.md`,
- rendered page images,
- run manifest.

Done when:

- package opens locally,
- links work,
- issue records are visible,
- required visuals are present or flagged,
- high-severity unresolved issues are summarized.

### Phase F — Snapshot and regression fixture creation

Create expected-output snapshots for:

1. factoid/sidebar separation,
2. cents-symbol detection,
3. number-line visual preservation.

Recommended snapshot format:

- expected block roles,
- expected exercise structure,
- expected issue types if uncertain,
- expected visual-reference status,
- rendered output screenshot optional,
- reviewer notes optional.

Done when:

- future runs can objectively pass/fail these cases.

## 13.4 Pilot stop conditions

Stop or block release if:

- source PDF identity is uncertain,
- page rendering fails,
- embedded text and OCR both miss visible content,
- high-severity layout/coherence issues remain unresolved,
- required visual references are absent,
- student output is generated from raw text instead of structured content,
- issue reporting is incomplete,
- correction memory changes are unlogged.

---

## 14. V4 implementation notes

## 14.1 Start simple

The first v4 implementation should prefer transparent files over clever automation.

Recommended first implementation path:

1. page renderer,
2. embedded text extractor,
3. OCR extractor with boxes,
4. block detector,
5. role classifier,
6. block coherence validator,
7. issue writer,
8. reviewer HTML,
9. structured exercise extractor,
10. student HTML renderer,
11. final QA packager.

## 14.2 Accuracy before polish

Do not spend effort polishing student HTML before:

- source page rendering works,
- OCR/PDF comparison works,
- block roles are visible,
- known issue types are emitted,
- reviewer HTML makes failures obvious.

## 14.3 Traceability requirement

Every student-facing exercise must trace back to:

- source PDF filename,
- page number,
- rendered page image,
- source block IDs,
- relevant issue IDs,
- visual reference IDs if any.

## 14.4 Confidence policy

Confidence scores should be used to route work, not to conceal doubt.

Low confidence must produce:

- an issue,
- a reviewer-visible marker,
- a release warning or block if material to answerability.

---

## 15. V4 definition of done

Pipeline V4 is ready for broader batch conversion when:

1. Source intake prevents handoff/spec/generated files from being treated as source PDFs.
2. Page rendering, embedded text extraction, and OCR/visible-text verification work.
3. OCR-vs-embedded comparison produces useful discrepancy records.
4. Layout blocks have bounding boxes and roles.
5. Block coherence validation catches or flags instruction/sidebar merge risks.
6. Structured exercises are generated from block roles, not raw lines.
7. Visual dependency detection prevents missing maps/number lines/graphs/diagrams.
8. Semantic validators catch coin/cents, arithmetic, fraction, matching, and completeness failures.
9. Issues are emitted for every uncertainty.
10. Reviewer HTML exposes source image, OCR/PDF text, blocks, roles, issues, and suggested corrections.
11. Human review actions can update correction memory.
12. Student HTML is clean, usable, and generated from validated structured JSON.
13. Final QA compares output against rendered page images and issues.
14. Required artifacts are packaged with stable relative links.
15. Critical regression tests pass or fail loudly with correct issue records.

---

## 16. Source basis

This v4 specification is based on the uploaded docvert handoff and control-tower materials, especially:

- `DOCVERT_HANDOFF_BASELINE.md`
- `00_PROJECT_CHARTER.md`
- `02_PIPELINE_V3_SPEC.md`
- `03_KNOWN_FAILURE_MODES.md`
- `04_VALIDATORS_AND_QA.md`
- `05_PAGE_CONVERSION_RULES.md`
- `06_ARTIFACTS_AND_OUTPUTS.md`
- `07_NEXT_ENGINEERING_TASKS.md`
- `08_FINAL_HANDOFF_QA_AUDIT.md`
- `09_SOURCE_PDF_REUPLOAD_CHECKLIST.md`
- `10_DECISION_LOG.md`
- `11_BACKLOG.md`
- `12_ARTIFACT_MAP.md`
- `pipeline_config_template.json`
- `block_role_schema_v1.json`
- `issue_schema_v3.json`
- `correction_memory_v3.json`
- `critical_test_cases_v1.json`

