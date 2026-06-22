# pdfFlat2Interact

Windows OCR cleanup workflow for converting flat scanned PDFs into searchable, cleaner PDF files.

See [Windows Setup Guide](docs/setup-windows.md) for environment configuration instructions.

## Crossword Digitization

To extract a crossword grid from a synthetic or clean image:

```python
from docvert.crossword import digitize_crossword_image

digitize_crossword_image(
    image_path="path/to/crossword.png",
    output_dir="output/crossword_1",
    title="Daily Crossword"
)
```
This produces `crossword.json`, an interactive `index.html`, and a `review.html` to verify the extraction.

## Example

``powershell
.\scripts\run-ocr-cleanup.ps1
  -InputPdf "C:\path\to\input.pdf"
  -OutputPdf "C:\codex_work\projects\pdfFlat2Interact\output\cleaned.pdf"
  -EnableJbig2
