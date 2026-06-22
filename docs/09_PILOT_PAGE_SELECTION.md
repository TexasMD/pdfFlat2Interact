# 09_PILOT_PAGE_SELECTION.md

Updated: 2026-06-13 UTC  
Status: Durable pilot-selection source, pending human approval  
Project: `docvert`  
Mode: Pilot selection only — no OCR, no extraction, no conversion, no student HTML, no reviewer HTML

## 1. Purpose

This file defines the first `docvert` pilot page set. It is limited to page selection and justification only.

The first pilot should test the highest-risk workbook-conversion behaviors before any larger batch run: source-PDF discipline, OCR-vs-embedded-text comparison, layout/block detection, block coherence, visual-reference preservation, semantic sanity checks, and reviewer-facing QA readiness.

This file does **not** authorize extraction or HTML generation.

## 2. Active source PDFs used

Only PDFs confirmed present in the active `docvert` Project environment are eligible for this pilot.

| Active source PDF | Pilot use |
|---|---|
| `summerbridge trial.pdf` | Required prior number-line / spatial-layout regression source. |
| `sumbridge2.pdf` | Core first-pilot regression source for factoid/sidebar separation, cents-symbol validation, vertical arithmetic, and word-bank handling. |
| `sumbridge3.pdf` | Structured mixed-layout source for number-family and prefix/suffix grouping. |
| `sumbridge4.pdf` | Fraction-table visual-reference source. |
| `sumbridge5.pdf` | Crossword/grid visual-reference source and mostly text-based passage source. |

Confirmed active but not selected for the first pilot:

| Active source PDF | Reason not selected |
|---|---|
| `sumbridge6.pdf` | Better reserved for later answer-page / answer-key exclusion testing after first-pilot extraction logic is stable. |

## 3. Missing source PDFs excluded

These PDFs are not active source material for this pilot because they are not confirmed present in the active Project environment.

| Missing source PDF | Importance | Blocks first pilot? | Disposition |
|---|---|---:|---|
| `sumbridgetest.pdf` | Low-priority reference source. | No | Deferred. Do not chase before first pilot approval. |
| `sumbridge7.pdf` | Later batch candidate. | No | Deferred until broader batch testing. |
| `sumbridge8.pdf` | Later batch candidate. | No | Deferred until broader batch testing. |

## 4. Selected first pilot pages

The first pilot uses 8 pages. This is the maximum requested size, but it is justified because the prior failures span text extraction, symbol corruption, block grouping, and visual-reference omission.

| Order | Source page | Pilot role | Why selected | Expected extraction hazards | Required validation checks | Prior regression status |
|---:|---|---|---|---|---|---|
| 1 | `sumbridge2.pdf`, page 1 | Block-coherence and factoid/sidebar separation. | Canonical case where linear extraction can merge the abbreviation instruction with the unrelated earthquake factoid. Also tests matching columns and sequence/order prompts. | Factoid merged into instruction; abbreviation columns interleaved; government sequence items detached; footer/decorative text included. | Block-role classification; block-coherence check; `sidebar_factoid_detected`; `possible_layout_block_merge_error`; matching-column completeness; prompt/item grouping. | **Preserves** prior factoid/sidebar regression. |
| 2 | `sumbridge2.pdf`, page 2 | Cents-symbol and money semantic validation. | Canonical case where visible cents values such as `11¢` and `47¢` can become `110` and `470`. Also includes answer lines and a second noun-form section. | Cents symbol dropped or converted to zero; two sections merged; coin art mistaken for content; item numbering errors. | OCR-vs-PDF-text comparison; cents-symbol normalization; coin-problem semantic validator; visible-symbol confirmation; item count check; issue logging. | **Preserves** prior cents-symbol regression. |
| 3 | `summerbridge trial.pdf`, page 5 | Number-line / spatial-layout / visual-reference preservation. | Required prior regression page now that `summerbridge trial.pdf` is confirmed active. The number line is necessary to answer the integer-location items. | Number line omitted; tick marks or letter positions lost; minus signs corrupted; comparison and absolute-value symbols flattened; reading passage grouped with math task. | Visual-reference validator; number-line crop/SVG verification; label/tick alignment; math-symbol check; answer-input count; section-boundary check. | **Preserves** prior number-line visual-reference regression. |
| 4 | `sumbridge2.pdf`, page 6 | Vertical arithmetic plus word-bank/fill-in handling. | Adds a true computation page with stacked addition and a separate possessive-noun word-bank exercise. | Vertical arithmetic flattened; plus signs/operands lost; thousands separators misread; word bank detached; math and grammar sections merged. | Arithmetic validator; vertical-layout check; operator/operand completeness; numbered-item sequence; word-bank attachment; blank/input count. | **Approximates/extends** vertical arithmetic and word-bank failure coverage. |
| 5 | `sumbridge5.pdf`, page 8 | Mostly text-based passage and response fields. | Provides a cleaner text-heavy baseline so the pilot is not only visual or math stress cases. | Paragraphs split/joined incorrectly; quotation marks or punctuation corrupted; response lines overcounted or missed; title/prompt merged; footer included. | Passage completeness; paragraph order; punctuation sanity; prompt/response grouping; five-response-field check; footer exclusion. | **New baseline** test; no prior regression replaced. |
| 6 | `sumbridge3.pdf`, page 3 | Structured number-family and prefix/suffix grouping. | Tests grouped math facts, table-like regions, prefix/suffix blanks, and sentence-writing prompts on one page. | Operators dropped; blue table/grid not recognized; prefixes/suffixes detached from base words; sentence lines mistaken for extra prompts. | Table/grid structure check; operator/symbol preservation; grouped-exercise completeness; blank/input count; section-boundary validation. | **Approximates** prior structured nonvisual Number Families target. |
| 7 | `sumbridge4.pdf`, page 2 | Fraction-table visual dependency. | Tests a visual table required for comparing fractions, plus fraction layout and report-writing separation. | Stacked fractions flattened; denominators ambiguous; comparison circles not converted to inputs; fraction table omitted; report-writing section merged with math task. | Fraction-layout validator; visual-reference validator; table label/row verification; comparison-input count; `ambiguous_fraction_layout` if uncertain; section separation. | **Approximates/extends** prior fraction/table visual coverage. |
| 8 | `sumbridge5.pdf`, page 2 | Crossword/grid visual-reference and reviewer-QA stress page. | Stress-tests grid preservation, across/down clue grouping, factoid separation, and reviewer-facing QA presentation. | Crossword grid omitted or distorted; clue numbers detached; across/down sections merged; factoid merged into clue text; illustrations interfere with segmentation. | Grid visual-reference check; clue numbering/count; across/down block separation; factoid/sidebar detection; visual crop completeness; issue surfacing in reviewer QA. | **Extends** visual-reference and factoid/sidebar regression coverage. |

## 5. Coverage summary

| Required first-pilot coverage | Selected page(s) |
|---|---|
| Mostly text-based page | `sumbridge5.pdf`, page 8 |
| Math computation page | `sumbridge2.pdf`, page 6 |
| Visually dependent page | `summerbridge trial.pdf`, page 5; `sumbridge4.pdf`, page 2; `sumbridge5.pdf`, page 2 |
| Answer lines, blanks, or fill-ins | `sumbridge2.pdf`, pages 1, 2, and 6; `sumbridge3.pdf`, page 3; `sumbridge4.pdf`, page 2; `sumbridge5.pdf`, page 8 |
| Table, word bank, diagram, chart, map, number line, or spatial layout | Number line: `summerbridge trial.pdf`, page 5; word bank: `sumbridge2.pdf`, page 6; table/grid: `sumbridge3.pdf`, page 3 and `sumbridge4.pdf`, page 2; crossword grid: `sumbridge5.pdf`, page 2 |
| Likely OCR or embedded-text errors | `sumbridge2.pdf`, page 2; `summerbridge trial.pdf`, page 5; `sumbridge4.pdf`, page 2 |
| Likely block-coherence or question-grouping problems | `sumbridge2.pdf`, page 1; `sumbridge3.pdf`, page 3; `sumbridge5.pdf`, page 2 |
| Reviewer-facing QA suitability | All selected pages, especially `sumbridge2.pdf`, pages 1 and 2; `summerbridge trial.pdf`, page 5; `sumbridge5.pdf`, page 2 |

## 6. Regression-test disposition

| Prior or planned regression/test | Disposition in this pilot | Page |
|---|---|---|
| Factoid/sidebar separation: abbreviation instruction must not merge with earthquake factoid. | Preserved. | `sumbridge2.pdf`, page 1 |
| Cents-symbol validation: `11¢`, `47¢`, etc. must not become trailing-zero integers. | Preserved. | `sumbridge2.pdf`, page 2 |
| Number-line visual-reference preservation. | Preserved because `summerbridge trial.pdf` is active. | `summerbridge trial.pdf`, page 5 |
| Structured Number Families conversion. | Approximated using an active structured page. | `sumbridge3.pdf`, page 3 |
| Fraction/table visual-reference handling. | Approximated and expanded. | `sumbridge4.pdf`, page 2 |
| Crossword/grid visual-reference handling. | Added as an expanded stress test. | `sumbridge5.pdf`, page 2 |
| Clock/envelope spatial task. | Deferred; not needed in the first 8 pages. | Future candidate: `sumbridge5.pdf`, page 7 |
| 19-page trial high-priority visual pages beyond number line: geometry/map/time-zone pages. | Deferred until after first-pilot gates pass. | Future candidates: `summerbridge trial.pdf`, pages 13, 16, and 18 |
| Answer-page / answer-key exclusion. | Deferred; important later but not part of first student-page pilot. | Future candidate: `sumbridge6.pdf`, page 10 or 11 |

## 7. Recommendation for the first extraction/conversion run

After this pilot selection is approved, the first authorized implementation run should process only these 8 pages, in this order:

1. `sumbridge2.pdf`, page 1
2. `sumbridge2.pdf`, page 2
3. `summerbridge trial.pdf`, page 5
4. `sumbridge2.pdf`, page 6
5. `sumbridge5.pdf`, page 8
6. `sumbridge3.pdf`, page 3
7. `sumbridge4.pdf`, page 2
8. `sumbridge5.pdf`, page 2

Before processing any selected page, the run must create a source manifest with hashes, page counts, stable source IDs, and page-image traceability.

Recommended gate: process the first three regression pages first. If factoid separation, cents-symbol validation, or number-line preservation fails, stop and fix the pipeline before continuing to the remaining five pages.

## 8. Definition of done for the first pilot

The first pilot is done only when:

- This pilot page selection has been explicitly approved or revised by the human reviewer.
- The authorized run processes only the selected 8 pages listed above.
- A source manifest records file hashes, page counts, stable source IDs, selected pages, and rendered-page traceability.
- The first three regression gates pass or fail safely before continuing: `sumbridge2.pdf` page 1 factoid/sidebar separation, `sumbridge2.pdf` page 2 cents-symbol validation, and `summerbridge trial.pdf` page 5 number-line visual-reference preservation.
- Every selected page has rendered source image traceability, OCR-vs-embedded-text comparison, block-role records, visual-reference status, structured exercise records, and issue records.
- High-severity issues are fixed, explicitly flagged for reviewer decision, or used to stop the run.
- Reviewer-facing QA clearly exposes source images, extracted text, OCR text, block roles, confidence, issues, and suggested corrections.
- Student-facing output, if later authorized, is generated from validated structured JSON and not raw text lines.
- No broader batch begins until the first-pilot report is reviewed and accepted.

## 9. Stop condition

Stop here until the pilot selection is approved.

No OCR, embedded-text extraction, layout detection, conversion, student-facing HTML, reviewer-facing HTML, or QA webpage generation should occur until this pilot page set is explicitly approved.
