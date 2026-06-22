# 07 — DOCVERT Reviewer HTML Specification V4

Updated: 2026-06-13 UTC  
Status: Durable Project-source renderer specification  
Project: `docvert`  
Mode: Specification only — no OCR, no extraction, no conversion, no reviewer HTML generation, no student HTML generation

## 1. Purpose

`07_REVIEW_HTML_SPEC_V4.md` defines the reviewer-facing QA webpage for `docvert`.

The reviewer page is the first rendering target. It exists to let a human quickly decide whether each converted workbook page is accurate, complete, visually supported, semantically coherent, traceable, and safe to use as the basis for student-facing HTML.

The reviewer page is not cosmetic output. It is a validation artifact. It must expose the evidence, uncertainty, issue records, block structure, visual references, and correction-memory suggestions that would otherwise be hidden behind a clean-looking student worksheet.

## 2. Governing rules

1. The rendered source page image is the visual truth.
2. Embedded PDF text and OCR text are hypotheses.
3. Layout/block records must be visible before student rendering is trusted.
4. Issues must be visible with severity, status, blocking effect, evidence, and recommended action.
5. A page must clearly show exactly one release status: `page_blocked`, `page_review_required`, `page_release_with_warnings`, or `page_release_ready`.
6. Reviewer HTML may show unresolved problems. Student HTML must not be released from unresolved critical or unreviewed major task-bearing issues.
7. Every page, block, exercise, issue, input field, visual reference, and correction-memory suggestion must trace back to source file, page, and rendered page image.
8. The reviewer page must be useful even if the extraction is bad. Bad extraction should look obviously bad, not quietly plausible.

## 3. Required input JSON files

A reviewer-render run requires these files or equivalent in the run directory:

| Input | Required | Purpose |
|---|---:|---|
| `run_manifest.json` | Yes | Run ID, pipeline version, source file hashes, tool versions, selected pages, output inventory. |
| `source_manifest.json` | Yes | Confirmed source PDFs, page counts, source IDs, selected pages, source status. |
| `json/all_pages.json` | Yes | Page-level structured extraction, metadata, page status, section records, exercise records. |
| `json/issues.json` | Yes | All issue records, including severity, blocking behavior, evidence, and status. |
| `json/block_roles.json` | Yes | Block records, roles, bounding boxes, confidence, include/exclude recommendations. |
| `json/pdf_text.json` | Yes for pilot | Embedded PDF text, text runs, bounding boxes, extraction warnings. |
| `json/ocr_text.json` | Yes for pilot | OCR text, OCR boxes, confidence, OCR warnings. |
| `json/text_comparison.json` | Yes for pilot | OCR-vs-PDF-text differences at page, block, item, symbol, and count level. |
| `json/layout_blocks.json` | Recommended | Pre-role block segmentation records and visual features. |
| `json/exercises.json` | Recommended | Normalized exercise objects used as the candidate student-render input. |
| `json/visual_refs.json` | Recommended | Visual reference records, crop/SVG paths, bbox, required/helpful status. |
| `json/correction_memory.json` | Yes | Loaded rules, candidate suggestions, accepted/rejected corrections when available. |
| `json/regression_results.json` | Recommended | Pass/fail status for known pilot regression tests. |

If a required file is missing, `review.html` may still render a diagnostic shell, but the affected run or page must be marked blocked or incomplete.

## 4. Required output files

Reviewer rendering should produce:

| Output | Purpose |
|---|---|
| `review.html` | Main reviewer-facing QA webpage. |
| `assets/page_images/` | Rendered full-page source images used by review panels. |
| `assets/visual_refs/` | Cropped or recreated visual-reference assets. |
| `assets/review/` | Optional reviewer-only CSS/JS/icons. |
| `json/review_actions.json` | Optional human review actions, issue decisions, edits, and correction-memory decisions. |
| `review_report.md` | Optional human-readable review summary, especially after review actions exist. |

The reviewer page must use stable relative paths so the run can be opened locally from the batch folder.

## 5. Validation gates before reviewer rendering

Reviewer HTML can be generated before all pages are clean, but it must not pretend the run is clean.

Minimum gates before rendering `review.html`:

1. Source manifest exists and identifies confirmed source PDFs.
2. Selected pages are known and within the approved pilot scope.
3. Rendered page images exist or missing images are represented as blocking issues.
4. Issue records exist, even if the issue list is empty.
5. Block-role records exist or their absence is represented as blocking/diagnostic issues.
6. Each page has a page-level status field.
7. Every page record has source ID, filename, page number, and page image path.

If later-stage JSON is missing, the reviewer page should show an explicit missing-artifact panel and mark affected pages `page_blocked` or `page_review_required`.

## 6. Page status model

Every page shown in `review.html` must expose one page status:

| Status | Meaning | Reviewer behavior |
|---|---|---|
| `page_blocked` | Not safe for student rendering. | Show red/high-priority badge, blockers first, and explain what prevents release. |
| `page_review_required` | Human decision needed before student use. | Show major issues and required reviewer checks. |
| `page_release_with_warnings` | No blockers; minor/advisory issues remain. | Show warnings but allow candidate student preview after review. |
| `page_release_ready` | No open blockers or review-required issues. | Show cleared status and evidence summary. |

Status derivation:

- Any open `critical` issue forces `page_blocked`.
- Any unreviewed `major` task-bearing issue forces at least `page_review_required`.
- Missing page-image traceability forces `page_blocked`.
- Missing required visual reference forces `page_blocked`.
- Missing or unverified task-bearing text forces `page_blocked` or `page_review_required`, depending on severity.

## 7. Required reviewer interface structure

### 7.1 Run header

The top of `review.html` must show:

- project name and run ID;
- pipeline version;
- generated timestamp;
- selected source PDFs and pages;
- issue counts by severity and status;
- page counts by release status;
- links to JSON artifacts and processing reports;
- clear label if the run is a pilot, debug, blocked, or release candidate.

### 7.2 Page navigator

The page navigator must allow page-by-page review and show:

- source filename;
- source page number;
- page status badge;
- issue count by severity;
- required visual-reference badge;
- regression gate badge when applicable;
- search/filter by status, severity, issue type, source file, and page.

For the first pilot, the navigator must preserve the approved page order.

### 7.3 Per-page review layout

A durable default layout:

- Left column: rendered source page image with overlay controls.
- Right column: QA panels/tabs for text, blocks, exercises, visuals, issues, and suggestions.

The source image panel should remain visible or easily reachable while the reviewer inspects extracted evidence. On narrow screens, stack panels vertically and provide jump links.

### 7.4 Source image panel

The source image panel must show:

- full rendered page image;
- page metadata: source file, page number, DPI, image dimensions;
- overlay toggles for layout blocks, OCR boxes, PDF text boxes, visual references, answer fields, and issue bounding boxes;
- click or hover behavior linking image regions to block/exercise/issue records;
- zoom and pan controls;
- warning if the page image is missing, broken, cropped, or untraceable.

The image panel is the fastest way to catch hallucinated structure, missing visuals, and sidebar/task merges. Do not bury it.

## 8. Required QA panels

### 8.1 Embedded text panel

Show:

- extracted embedded PDF text by page and block;
- text boxes/bounding boxes when available;
- extraction warnings;
- reading-order confidence;
- linked issues caused by embedded-text gaps, corruption, or reading-order failures.

### 8.2 OCR text panel

Show:

- OCR text by page, line, word, or block;
- OCR confidence where available;
- OCR bounding boxes;
- low-confidence task-bearing text;
- linked issues caused by OCR gaps, garbling, or symbol errors.

### 8.3 OCR-vs-embedded-text differences panel

Show differences that matter for answerability:

- missing text in either source;
- symbol disagreements;
- number disagreements;
- item-count disagreements;
- reading-order divergence;
- suspicious transformations such as cents symbols becoming trailing-zero integers;
- labels missing from visual references.

Each difference should include source text, OCR text, confidence, bbox if available, linked block/exercise/issue IDs, and recommended action.

### 8.4 Layout blocks panel

Show detected blocks with:

- `block_id`;
- source page and bbox;
- text preview;
- source methods;
- visual features;
- assigned role;
- role confidence;
- include/exclude recommendation for student page;
- nearby blocks;
- coherence notes;
- linked issues.

The panel must make it obvious when footers, decorative text, factoids, or sidebars are excluded from student output.

### 8.5 Extracted questions and instructions panel

Show structured extraction by exercise:

- section title/context;
- instruction block IDs;
- item records and item count;
- answer bank or choices;
- input-control mapping;
- visual-reference dependencies;
- linked issues;
- candidate student rendering summary.

This panel should help the reviewer answer: “Does this exercise still mean what the source page means?”

### 8.6 Answer fields panel

Show every detected response location:

- short-answer blanks;
- text areas;
- writing lines;
- drawing regions;
- circles/checkboxes/selection marks;
- matching targets;
- table/grid cells;
- canvas or SVG-overlay tasks.

Each answer field must link to the source bbox and the candidate student input control.

### 8.7 Preserved visual references panel

Show each visual reference:

- `visual_id`;
- required/helpful/decorative status;
- source bbox;
- crop or SVG asset path;
- thumbnail preview;
- labels/tick marks/legend text when relevant;
- linked exercise IDs;
- asset existence/open check;
- required reviewer action if visual recreation or crop is uncertain.

Required visuals include number lines, maps, graphs, charts, tables, fraction tables, geometry figures, clocks, crossword grids, word-search grids, diagrams, picture prompts, and drawing/writing areas when layout defines the task.

### 8.8 Issues panel

Show all issue records for the page, sorted by blocking effect and severity.

Each issue card must show:

- issue ID;
- type;
- severity;
- status;
- `blocks_student_html`;
- validator stage;
- confidence;
- source file/page;
- bbox and linked page-image overlay;
- evidence from PDF text, OCR text, and visible-text summary;
- description;
- likely cause;
- recommended human action;
- suggested fix if any;
- affected block/exercise/visual/input IDs.

Issue controls should initially be read-only if no reviewer-edit workflow exists. When editing is implemented, allowed actions are: accept, reject, edit, downgrade, escalate, mark fixed, mark intentionally carried forward, and create correction-memory candidate.

### 8.9 Correction-memory suggestions panel

Show correction-memory suggestions separately from confirmed content.

Each suggestion must show:

- rule ID;
- matched context;
- proposed correction or structural action;
- confidence;
- supporting evidence;
- affected text/block/exercise;
- whether the suggestion was auto-applied, pending review, rejected, or accepted;
- link to the issue record created or modified by the suggestion.

Rules must be conservative. Suggestions do not silently make the page release-ready.

### 8.10 Raw JSON/debug panel

Provide collapsible raw JSON snippets for page, blocks, exercises, issues, visual refs, and comparison records. This is ugly but useful. Hide it by default; never remove it from reviewer builds.

## 9. How unresolved issues affect reviewer rendering

Reviewer rendering must always surface unresolved issues. It may render incomplete pages for review, but the page must be marked accordingly.

| Issue state | Reviewer HTML behavior |
|---|---|
| Open `critical` | Page marked `page_blocked`; blocker shown at top; student release prohibited. |
| Open unreviewed `major` affecting task content | Page marked `page_review_required`; candidate rendering shown only as suspect. |
| Open `minor` | Page may show warning; does not block if answerability is intact. |
| Open `advisory` | Show in suggestions/audit area; does not block. |
| Missing required JSON | Diagnostic page shown; affected pages blocked or review-required. |
| Missing required visual asset | Page blocked if visual is task-bearing. |

## 10. Accessibility and usability requirements

Reviewer HTML must be usable by a tired human trying to find subtle errors before the machinery invents nonsense with a straight face.

Minimum requirements:

- semantic HTML landmarks;
- keyboard navigable tabs, filters, issue cards, and overlays;
- visible focus indicators;
- readable font size;
- sufficient contrast;
- issue severity conveyed by text labels, not color alone;
- alt text for rendered page images and visual-reference thumbnails;
- large clickable targets;
- no hidden critical warnings;
- support browser zoom;
- local-file friendly relative paths;
- print summary for issue lists and page status.

## 11. Desktop and mobile layout expectations

Desktop/tablet default:

- page navigator on the left or top;
- source image beside QA panels;
- sticky status bar for current page;
- overlay controls near the source image.

Mobile/narrow layout:

- stacked sections;
- jump links to image, issues, blocks, exercises, and visuals;
- horizontal scrolling allowed only for data tables and large visual references;
- status and blocker summary visible before detailed panels.

Mobile support is required for review, but dense QA work is expected to be better on desktop. Do not mutilate the evidence to fit a phone screen.

## 12. First-pilot reviewer rendering limits

For the first pilot, `review.html` is limited to the approved eight pages:

1. `sumbridge2.pdf`, page 1
2. `sumbridge2.pdf`, page 2
3. `summerbridge trial.pdf`, page 5
4. `sumbridge2.pdf`, page 6
5. `sumbridge5.pdf`, page 8
6. `sumbridge3.pdf`, page 3
7. `sumbridge4.pdf`, page 2
8. `sumbridge5.pdf`, page 2

The first three pages are hard gates:

- factoid/sidebar separation;
- cents-symbol validation;
- number-line visual-reference preservation.

If any hard gate fails and the pipeline does not emit clear blocking issues with reviewer evidence, stop expansion and fix the validator/renderer. Do not continue toward student release.

## 13. Reviewer page acceptance checklist

`review.html` is acceptable for the pilot only when:

- every selected page appears in the approved order;
- every page shows the rendered source image or a blocking image error;
- embedded text, OCR text, and comparison records are visible;
- layout blocks, roles, confidence, and bboxes are visible;
- extracted questions/instructions and answer fields are visible;
- visual references are shown with crop/SVG status;
- issue flags are visible with severity and blocking effect;
- correction-memory suggestions are visible and not confused with facts;
- each page status is clear;
- source traceability is intact;
- unresolved blockers cannot be mistaken for cleared pages.

