# pdfFlat2Interact

Windows OCR cleanup workflow for converting flat scanned PDFs into searchable, cleaner PDF files.

See [Windows Setup Guide](docs/setup-windows.md) for environment configuration instructions.

## Example

``powershell
.\scripts\run-ocr-cleanup.ps1 
  -InputPdf "C:\path\to\input.pdf" 
  -OutputPdf "C:\codex_work\projects\pdfFlat2Interact\output\cleaned.pdf" 
  -EnableJbig2
