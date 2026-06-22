# pdfFlat2Interact

`pdfFlat2Interact` is a validation-first pipeline for turning flat or scanned PDFs into cleaner, searchable, and eventually interactive outputs.

The project currently has two layers:

- `scripts/run-ocr-cleanup.ps1`: Windows OCR cleanup helper using OCRmyPDF, Tesseract, Ghostscript, pngquant, unpaper, and optional JBIG2.
- `src/docvert`, `docs`, and `schemas`: the `docvert` workbook-conversion foundation for layout-aware PDF extraction, reviewer QA, validation gates, issue reporting, and gated student-facing HTML.

## Core Rule

The rendered page image is the source of truth. OCR text, embedded PDF text, extracted structure, generated HTML, and prior outputs are hypotheses until validated against the rendered page image.

## OCR Cleanup Example

```powershell
.\scripts\run-ocr-cleanup.ps1 `
  -InputPdf "C:\path\to\input.pdf" `
  -OutputPdf "C:\codex_work\projects\pdfFlat2Interact\output\cleaned.pdf" `
  -EnableJbig2
```

If `jbig2.exe` is not working on your machine, omit `-EnableJbig2`; the script will still use Ghostscript, Tesseract, pngquant, and unpaper.

## Repository Policy

Do not commit private, copyrighted, or large source PDFs. Keep source files and generated outputs local unless Git LFS is intentionally configured.

Ignored by default:

- `data/source/`
- `*.pdf`
- generated outputs and temporary files

## Current Implementation Phase

First extraction/validation pilot. Do not run broad batch conversion until the pilot regression gates in `docs/09_PILOT_PAGE_SELECTION.md` and `docs/04_VALIDATION_RULES_V4.md` pass.
