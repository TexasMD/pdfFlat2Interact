# 08 — DOCVERT Student HTML Specification V4

Updated: 2026-06-13 UTC
Status: Durable Project-source renderer specification
Project: `docvert`
Mode: Specification only — no OCR, no extraction, no conversion, no reviewer HTML generation, no student HTML generation

## 1. Purpose

`08_STUDENT_HTML_SPEC_V4.md` defines the student-facing interactive worksheet output for `docvert`.

Student HTML is the final clean learning interface. It must be generated from validated structured content, not raw extracted PDF text, and not unresolved reviewer artifacts. It should preserve the educational task, required visuals, page logic, answer expectations, and source traceability while removing reviewer clutter.

Reviewer-facing QA must be designed and generated before student output is treated as releasable. A student page that looks nice while hiding extraction uncertainty is a failure.

## 2. Governing rules

1. Student HTML is generated from validated structured JSON.
2. Student HTML must not be released from unresolved critical issues or unreviewed major task-bearing issues.
3. Required visuals must be present, recreated, or the page must be withheld from clean student release.
4. The student page should render the learning task, not page decoration.
5. Reviewer-only warnings, OCR evidence, issue lists, debug overlays, and correction-memory suggestions must not clutter the student interface.
6. Source traceability must remain available in a subtle or hidden form for audit and debugging.
7. Every input control must correspond to a visible or semantically required answer field in the source worksheet.
8. Print/save/export behavior should be useful but must not outrank accuracy.

## 3. Required input JSON files

A student-render run requires validated or review-approved inputs:

| Input | Required | Purpose |
|---|---:|---|
| `run_manifest.json` | Yes | Run ID, source hashes, selected pages, tool versions, output inventory. |
| `source_manifest.json` | Yes | Confirmed source PDFs, source IDs, page counts, selected pages. |
| `json/all_pages.json` | Yes | Validated page metadata, release status, section/exercise records, traceability. |
| `json/exercises.json` | Yes | Structured exercise records used for rendering. |
| `json/issues.json` | Yes | Required to enforce release gates and hide/withhold blocked content. |
| `json/block_roles.json` | Yes | Include/exclude decisions for task, visual, factoid, footer, decoration, unknown blocks. |
| `json/visual_refs.json` | Required when visuals exist | Required/helpful visual references, asset paths, bboxes, labels, alt text. |
| `json/review_actions.json` | Required if any issue was manually resolved | Human review decisions, accepted fixes, downgrades, carried-forward warnings. |
| `json/correction_memory.json` | Recommended | Accepted corrections applied to the student-rendered content. |
| `final_qa_report.md` or equivalent gate record | Recommended for release | Confirms final validation against source images and issue records. |

Student rendering must fail closed. If release-gate JSON is absent or inconsistent, do not emit a clean student page for affected pages.

## 4. Required output files

Student rendering should produce:

| Output | Purpose |
|---|---|
| `index.html` | Main student-facing interactive worksheet. |
| `assets/student/` | Student CSS/JS and optional icons. |
| `assets/visual_refs/` | Cropped or recreated visual references used by the worksheet. |
| `assets/page_images/` | Optional traceability images; may be hidden from the normal student UI. |
| `student_manifest.json` | Optional output inventory and page release summary. |
| `student_responses_schema.json` | Optional schema for saved/exported student responses. |

All links must be relative and portable. The package should open locally in a browser without a server unless a later implementation explicitly chooses otherwise.

## 5. Required validation gates before student rendering

A page may enter clean student rendering only when all applicable gates pass:

1. Source identity is confirmed.
2. Page is in the approved run scope.
3. Rendered page-image traceability exists.
4. OCR-vs-embedded-text comparison is complete or explicitly reviewed.
5. Layout blocks and block roles are assigned.
6. Block coherence issues are resolved, reviewed, or non-blocking.
7. Structured exercises are complete.
8. Answer fields and input controls match visible answer expectations.
9. Required visuals are present and linked.
10. No open `critical` issue remains.
11. No unreviewed `major` task-bearing issue remains.
12. Any remaining `minor` or `advisory` issue is non-blocking and recorded.
13. Final student-render validation confirms no reviewer/debug clutter is visible.

A page that fails these gates may have a reviewer/debug preview, but it must not appear as a clean student worksheet.

## 6. How unresolved issues affect student rendering

| Issue state | Student-render behavior |
|---|---|
| Open `critical` | Do not render page into clean student worksheet. Mark page withheld/blocked in manifest. |
| Open unreviewed `major` affecting task-bearing content | Do not render clean page until fixed, reviewed, or explicitly downgraded. |
| Reviewed `major` intentionally carried forward | Render only if it does not affect answerability; record hidden trace note. |
| Open `minor` | May render if answerability is intact; hide from normal student UI. |
| Open `advisory` | May render; keep audit trace only. |
| Missing required visual | Do not render clean page unless task can be validly converted without it, with reviewer approval. |
| Unknown block role affecting task content | Do not render clean page until classified or reviewed. |

The student interface should not display scary internal warnings by default. It should also not silently include known-bad pages. The correct behavior is to withhold blocked pages from clean release or show a deliberately non-student debug placeholder only in development builds.

## 7. Student interface structure

### 7.1 Global shell

`index.html` should include:

- worksheet title or batch title;
- page navigation;
- progress indicator if feasible;
- print button;
- save/export controls if feasible;
- clear local responses control if local storage is implemented;
- optional hidden audit/source panel for traceability.

### 7.2 Page structure

Each rendered page should include:

- source-derived page title or section title when useful;
- instructions;
- exercise sections;
- questions/items;
- answer inputs;
- required visual references;
- writing or drawing areas when needed;
- subtle source traceability attributes.

Preferred structure:

```text
student page
  section card
    instruction
    visual reference, if needed
    item list/table/grid
    answer controls
  section card
    instruction
    items
```

Do not preserve workbook decoration unless it helps the student answer or understand the task.

## 8. Supported interaction types

The renderer should support these first:

| Source task | Student control |
|---|---|
| Short blank or answer line | Text input. |
| Multi-line writing prompt | Textarea with optional lined-paper styling. |
| Long writing page | Large textarea, optional print-friendly lines. |
| Drawing prompt | Canvas, SVG drawing layer, or large drawing placeholder with print fallback. |
| Matching exercise | Select controls, drag/drop later, or printable line-drawing fallback. |
| Multiple choice / circle the answer | Radio buttons or selectable chips. |
| Checkbox / mark all that apply | Checkboxes. |
| Fill-in passage | Inline text inputs. |
| Table/grid completion | Table with input cells. |
| Crossword / word-search grid | Preserved grid image/SVG plus answer inputs or print-friendly interaction. |
| Number line / graph / map / diagram task | Preserved or recreated visual plus mapped answer inputs. |
| Underline/circle/draw-on-text task | Click-to-mark/SVG overlay, or converted text-entry equivalent only after reviewer approval. |

If the source task requires a visual/spatial action that cannot be faithfully converted, preserve the visual and provide a print/drawing fallback rather than inventing a fake equivalent.

## 9. Visual-reference rendering

### 9.1 Required visual policy

A visual must be included when the question depends on it. This includes number lines, maps, graphs, charts, tables, diagrams, geometry figures, clocks, fraction bars/tables, word-search grids, crossword grids, picture prompts, and spatially meaningful writing/drawing areas.

### 9.2 Visual asset choices

| Visual type | Preferred handling |
|---|---|
| Simple number line, graph, geometry segment | Recreated SVG if accurate. |
| Complex map, illustration, crossword, dense table | Cropped source image unless robust recreation exists. |
| Fraction table/bar | Recreated SVG/table or cropped reference if exact spatial layout matters. |
| Drawing/writing box | HTML canvas/textarea plus print-friendly box/lines. |
| Decorative image | Omit unless reviewer marks helpful. |

Each visual reference must include:

- accessible label or alt text;
- source traceability data;
- caption/labels needed for the task;
- responsive scaling without destroying readability;
- print behavior that keeps it near the question it supports.

## 10. Source traceability in student output

Student pages should not look like QA screens, but they must retain audit hooks.

Use subtle or hidden traceability such as:

- `data-source-id`;
- `data-source-file`;
- `data-source-page`;
- `data-block-id`;
- `data-exercise-id`;
- `data-visual-id`;
- hidden `<details class="source-trace">` only visible in debug mode;
- manifest entries mapping student sections to source pages.

Do not expose issue IDs, OCR text, or correction-memory details to students unless a deliberate debug/review mode is enabled.

## 11. Save, print, and export behavior

First implementation should be simple and local:

- Use browser local storage for draft student responses when feasible.
- Provide a “Download responses” option as JSON or plain text when feasible.
- Provide print CSS so the page can be printed or saved as PDF.
- Preserve answer boxes, writing areas, drawing areas, tables, and visual references in print.
- Do not require login or server storage for the first pilot.
- Do not implement auto-grading unless a later spec defines answer keys and validation rules.

Suggested saved response record:

```json
{
  "run_id": "...",
  "student_session_id": "local-generated-id",
  "responses": [
    {
      "exercise_id": "...",
      "item_id": "...",
      "input_id": "...",
      "value": "...",
      "updated_utc": "..."
    }
  ]
}
```

## 12. Accessibility and usability requirements

Minimum requirements:

- semantic headings and landmarks;
- labels for every input;
- keyboard navigation for all controls;
- visible focus indicators;
- sufficient contrast;
- readable default font size;
- no answer control identified by color alone;
- alt text or accessible labels for required visuals;
- responsive layout without losing visuals;
- large tap targets for mobile;
- no critical content hidden behind hover-only interactions;
- print-friendly structure;
- canvas/drawing fallback text or printable box.

For younger students, keep the interface calm. The renderer should not turn a workbook into a cockpit designed by a committee of caffeinated raccoons.

## 13. Desktop and mobile layout expectations

Desktop:

- centered worksheet column with comfortable reading width;
- sticky or top page navigation;
- visual references beside or immediately above related questions when space allows;
- tables/grids readable without excessive zoom;
- print controls visible but not intrusive.

Mobile:

- single-column layout;
- page navigation collapses into a simple selector/list;
- large inputs and buttons;
- visual references scale to width, with horizontal scroll only for large grids/tables;
- drawing areas sized for touch but not allowed to crush surrounding content;
- long writing prompts remain usable.

## 14. First-pilot student rendering limits

Student HTML for the first pilot is limited to the approved eight pages only, and only after pilot approval and validation gates pass:

1. `sumbridge2.pdf`, page 1
2. `sumbridge2.pdf`, page 2
3. `summerbridge trial.pdf`, page 5
4. `sumbridge2.pdf`, page 6
5. `sumbridge5.pdf`, page 8
6. `sumbridge3.pdf`, page 3
7. `sumbridge4.pdf`, page 2
8. `sumbridge5.pdf`, page 2

First-pilot limits:

- no full-corpus batch rendering;
- no answer-key pages;
- no grading engine;
- no login/account system;
- no server dependency;
- no unresolved critical or unreviewed major task-bearing issues;
- no student-visible reviewer clutter;
- no silent fallback to plain text when a visual is required;
- no broad visual recreation beyond what can be validated against the source image.

## 15. Post-render validation

After `index.html` is generated, validate:

- every rendered page was release-eligible;
- every student section links to source traceability;
- every expected exercise appears once;
- every expected answer field appears once;
- no blocked issue is hidden in the student package;
- no footer/decorative/factoid block is incorrectly rendered as a student task;
- required visuals load and print;
- inputs are labeled and keyboard accessible;
- local save/export does not corrupt responses;
- relative links work offline;
- mobile and print layouts are usable.

## 16. Student page acceptance checklist

`index.html` is acceptable for the pilot only when:

- reviewer QA exists and has been checked first;
- all release gates pass for included pages;
- the page is generated from validated structured JSON;
- source-required visuals are present;
- instructions and questions preserve the source task meaning;
- inputs match the visible answer expectations;
- drawing/writing areas exist when required;
- reviewer/debug clutter is absent;
- traceability remains available for audit;
- save/print behavior works well enough for local use;
- known unresolved blockers are not visible as clean student worksheets.
