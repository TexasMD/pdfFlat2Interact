param(
    [string]$RenderManifest = "data/runs/first_pilot/json/page_renders.json",
    [string]$PdfTextManifest = "data/runs/first_pilot/json/pdf_text.json",
    [string]$Output = "data/runs/first_pilot/json/ocr_text.json",
    [string]$Tesseract = "",
    [string]$Language = "eng",
    [int]$Psm = 3
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
$env:PYTHONPATH = Join-Path $repoRoot "src"

$argsList = @(
    "-m", "docvert.ocr_text",
    "--render-manifest", $RenderManifest,
    "--pdf-text-manifest", $PdfTextManifest,
    "--output", $Output,
    "--language", $Language,
    "--psm", $Psm
)

if ($Tesseract) {
    $argsList += @("--tesseract", $Tesseract)
}

& $python @argsList
exit $LASTEXITCODE
