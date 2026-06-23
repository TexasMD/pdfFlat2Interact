param(
    [string]$SourceDir = "data/source",
    [string]$Output = "data/runs/first_pilot/source_manifest.json",
    [switch]$AllowMissing
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
$env:PYTHONPATH = Join-Path $repoRoot "src"

$argsList = @(
    "-m", "docvert.source_manifest",
    "--config", "schemas/first_pilot_source_manifest_config.json",
    "--project-root", $repoRoot,
    "--source-dir", $SourceDir,
    "--output", $Output
)

if ($AllowMissing) {
    $argsList += "--allow-missing"
}

& $python @argsList
exit $LASTEXITCODE
