param(
    [string]$SourceManifest = "data/runs/first_pilot/source_manifest.json",
    [string]$RenderManifest = "data/runs/first_pilot/json/page_renders.json",
    [string]$Output = "data/runs/first_pilot/json/pdf_text.json",
    [string]$TempDir = "data/runs/first_pilot/tmp/pdf_text_bbox"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
$env:PYTHONPATH = Join-Path $repoRoot "src"

$argsList = @(
    "-m", "docvert.pdf_text",
    "--source-manifest", $SourceManifest,
    "--render-manifest", $RenderManifest,
    "--output", $Output,
    "--temp-dir", $TempDir
)

& $python @argsList
exit $LASTEXITCODE
