# Next Tasks Suggestions

Based on a review of `11_BACKLOG.md`, `01_PIPELINE_SPEC_V4.md`, and the current state of the visual reference image (`IMG_7107.png`), the following immediate actions are recommended to advance the Phase 3 (Semantic Validators) and Phase 4 (Reviewer QA shell) efforts:

1. **Implement Phase 3 Semantic Validators**
   - **VAL-001 (Coin/money semantic validator):** Create logic to detect corrupted cents-symbols (e.g., misreading "11¢" as "110") and flag implausible coin values.
   - **VAL-002 (Arithmetic validator):** Validate math operands, operators, blanks, numbering sequence, and vertical layouts, ensuring alignment with reference images.
   - **VAL-003 (Fraction layout validator):** Protect stacked fractions and references to fraction tables.
   - **VAL-004 (Visual-reference validator):** Add specific tests for preserving graphs, charts, grids, and drawing areas, referencing crops from images like `IMG_7107.png`.

2. **Establish the Phase 4 Reviewer QA Shell**
   - **REV-001 (Create reviewer QA shell):** Create a basic UI displaying run header, page navigator, page status, issue counts, and source traceability.
   - **REV-002 (Show rendered source page image):** Ensure the full-page image is attached as required evidence.
   - **REV-003 (Show comparisons):** Present side-by-side views of embedded text, OCR text, and their differences.

3. **Incorporate Real-World Test Cases**
   - Synthesize test images programmatically based on `IMG_7107.png` (using Pillow) to ensure the validation logic accurately identifies specific math problems, layout structures, and block cohesion failures expected in actual documents.

**Next Steps:**
Please approve these recommendations or identify which validator/Reviewer task should be implemented first.
