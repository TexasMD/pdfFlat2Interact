param(
    [string]$SourceManifest = "data/runs/first_pilot/source_manifest.json",
    [string]$Output = "data/runs/first_pilot/json/page_renders.json",
    [string]$AssetDir = "data/runs/first_pilot/assets/page_images",
    [int]$Dpi = 200
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
$env:PYTHONPATH = Join-Path $repoRoot "src"

$argsList = @(
    "-m", "docvert.page_render",
    "--config", "schemas/first_pilot_source_manifest_config.json",
    "--source-manifest", $SourceManifest,
    "--output", $Output,
    "--asset-dir", $AssetDir,
    "--dpi", $Dpi
)

& $python @argsList
exit $LASTEXITCODE
