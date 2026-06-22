# 06 — DOCVERT Correction Memory Rules V4

Updated: 2026-06-13 UTC
Status: Durable Project-source correction-memory specification
Project: `docvert`
Mode: Specification only — no OCR, no extraction, no conversion, no student HTML, no reviewer HTML

## 1. Purpose

Correction memory stores reusable knowledge about recurring extraction and validation failures so the same mistakes are not repaired manually again and again.

It may store patterns for OCR mistakes, embedded-text mistakes, symbol substitutions, number/currency/fraction errors, layout segmentation, headers/footers, question grouping, answer-line detection, visual-reference triggers, table/column reading, block coherence, semantic sanity checks, and human review decisions.

Correction memory is not a shortcut around validation. The rendered page image remains the source of truth.

## 2. Core rules

1. Prefer the narrowest safe scope: `block`, `question`, `region`, `page`, `pdf`, `document`, then `global`.
2. Preserve original extraction evidence before applying or suggesting any correction.
3. Do not silently change task-bearing text, numbers, symbols, operators, answer choices, labels, or visuals.
4. Every correction affecting student answerability must be logged and traceable to source PDF page evidence.
5. A reusable correction must not hide an issue that belongs in reviewer QA.
6. Human review decisions become durable correction memory only when they are reusable, safety-relevant, or useful as false-positive guards.

## 3. Correction record types

Use the schema in `05_CORRECTION_MEMORY_SCHEMA_V4.json`.

Supported correction types:

- `ocr_text_correction`
- `embedded_text_correction`
- `symbol_substitution`
- `number_correction`
- `currency_correction`
- `fraction_layout_correction`
- `math_operator_correction`
- `layout_segmentation_rule`
- `page_header_footer_artifact`
- `factoid_sidebar_rule`
- `question_grouping_rule`
- `answer_line_detection_rule`
- `visual_reference_trigger`
- `table_column_reading_correction`
- `block_coherence_rule`
- `semantic_sanity_rule`
- `human_review_decision`
- `source_specific_exception`
- `negative_rule`

Each record must include correction ID, source pattern, corrected value or corrected structure, correction type, scope, `applies_when`, confidence, source PDF/page traceability, reviewer note when available, record version/date fields, automatic-application policy, and human/visual confirmation requirements.

## 4. When to create a correction

Create a correction when one of these is true:

1. A human reviewer fixes an error likely to recur.
2. The same OCR, embedded-text, symbol, layout, grouping, or semantic failure appears across pages or runs.
3. A known regression case exposes a stable failure pattern.
4. A visual dependency is repeatedly missed.
5. A table, grid, column, number line, fraction layout, answer-line region, word bank, matching exercise, or block boundary is repeatedly misread.
6. A validator false positive is likely to recur and should become a `negative_rule`.
7. A reviewer decision should be reused, such as “this shaded corner block is a factoid sidebar, not part of the prompt.”

Do not create durable correction memory for one-off cleanup unless it affects answerability, traceability, release gating, or regression coverage.

## 5. When to reuse a correction

Reuse a correction only when all required conditions pass:

1. Record status is `active`.
2. The current page/block/question is inside the record scope.
3. `applies_when` conditions match current evidence.
4. No `do_not_apply_when` condition or negative example matches.
5. The rendered page image supports the correction or at least does not contradict a flag/suggestion.
6. Competing OCR/PDF/image hypotheses are preserved in evidence or issue records.
7. Required issue records are emitted or linked when uncertainty remains.
8. Confidence threshold is met.
9. Human confirmation is obtained when required.
10. Visual/rendered-image confirmation is obtained when required.

Global records should usually flag or suggest, not automatically rewrite content.

## 6. When not to reuse a correction

Do not reuse a correction when:

1. The same surface pattern appears in a different educational context.
2. A source-specific rule is outside its source/page/region/question/block scope.
3. The rendered image supports the original extraction.
4. OCR and embedded text disagree and neither is visually confirmed.
5. The correction would alter a number, symbol, operator, fraction, answer choice, label, or question meaning without strong evidence.
6. The correction would merge blocks that visual layout suggests are separate.
7. The correction would omit or downgrade a required visual reference.
8. The correction would suppress an unresolved issue.
9. A matching negative example exists.
10. The record is `rejected`, `deprecated`, or `superseded`.

Example: `110 -> 11¢` may be valid in a coin problem with visible cents-symbol evidence. It is not valid as a global string replacement.

## 7. Overbreadth controls

To prevent correction memory from turning into a tiny rule-goblin with a clipboard:

1. Start narrow; promote scope only after repeated evidence.
2. Require multiple signals for risky corrections: context words, layout, OCR/PDF disagreement, semantic-validator signal, and rendered-image support.
3. Treat broad/global rules as suspicion triggers unless the correction is deterministic and harmless.
4. Store false positives as `negative_rule` records.
5. Keep source-specific exceptions source-specific.
6. Never apply raw global string replacement to task-bearing content.
7. Log before/after evidence for every application.
8. Use confidence to route review, not to conceal uncertainty.
9. If uncertain, emit an issue and require review.

## 8. Interaction with issue reporting

Correction memory and issue reporting must reinforce each other.

A correction may:

- create an issue;
- attach to an existing issue;
- suggest a reviewer fix;
- apply a high-confidence fix with evidence;
- downgrade or close an issue only after evidence or review;
- create a `negative_rule` when a validator suggestion is rejected.

Every correction affecting task-bearing content must appear in at least one audit trail:

- `json/issues.json`
- reviewer-facing QA output
- `processing_report.md` or final QA report
- correction application log
- correction memory review log

If a correction is applied without adequate evidence, emit `correction_applied_without_evidence`. If a correction-related risk is not visible in the issue report or reviewer output, emit `issue_reporting_incomplete`.

## 9. Review after each pilot run

Before expanding beyond a pilot run, review correction memory.

Minimum review checklist:

1. List records loaded during the run.
2. List records applied automatically.
3. List records that only flagged or suggested.
4. List new candidate corrections from open issues and human edits.
5. Convert recurring false positives into `negative_rule` records.
6. Narrow any rule that matched too broadly.
7. Promote narrow rules only when repeated evidence supports broader scope.
8. Confirm every task-bearing correction has source-page evidence and issue visibility.
9. Update regression expectations when a correction resolves a known recurring failure.
10. Increment memory version and preserve change notes.

For the first pilot, specifically review:

- factoid/sidebar separation;
- cents-symbol and money-value correction;
- number-line visual preservation;
- vertical arithmetic layout;
- word-bank attachment;
- fraction-table and stacked-fraction handling;
- crossword/grid preservation;
- footer/decorative exclusion.

## 10. Versioning

Correction memory has two separate versions:

1. **Schema version** — structure of the memory file. This document defines V4.
2. **Memory version** — actual set of correction records used by a project or run.

Versioning rules:

1. Use append-only history for meaningful changes.
2. Do not silently overwrite correction meaning.
3. Increment a record version when scope, conditions, action, confidence, corrected value, or corrected structure changes.
4. Mark old records as `superseded` or `deprecated`; do not delete them from durable memory unless a cleanup migration explicitly does so.
5. Record `supersedes` and `superseded_by` when replacing a rule.
6. Keep rejected suggestions as negative examples when they explain likely future false positives.
7. Include memory version, schema version, run ID, source PDFs, and selected pages in run artifacts.

## 11. Default automatic-correction policy

| Correction kind | Default action |
|---|---|
| Currency, number, fraction, operator, answer choice | Flag or suggest; require rendered-image confirmation before changing. |
| OCR or embedded-text word correction | Suggest; auto-correct only if narrow and visibly supported. |
| Factoid/sidebar classification | Classify as review-only or optional note when layout and semantic signals are strong; log if near a prompt. |
| Header/footer/decorative artifact | Exclude from student output when repeated header/footer evidence is strong; keep traceability in QA. |
| Visual-reference trigger | Preserve/recreate/crop visual or block release if missing. |
| Table/column reading correction | Suggest or restructure only with layout evidence; require review for complex grids. |
| Answer-line detection | Create input controls when answer fields are visually clear; flag ambiguous response areas. |
| Semantic sanity correction | Flag or suggest; do not auto-rewrite the educational task. |

## 12. Required implementation behavior

A pipeline using correction memory must:

1. Load active correction memory before validation.
2. Check negative rules before broad positive rules.
3. Apply source/page/block scope filters before pattern matching.
4. Use correction records to flag, suggest, classify, or block before automatically changing content.
5. Preserve original OCR/PDF/layout evidence.
6. Emit or link issues for unresolved uncertainty.
7. Log every correction application, suggestion, skip, rejection, and automatic change.
8. Export candidate memory updates for human review.
9. Save updated durable memory only after post-run review.
