param(
    [Parameter(Mandatory = $true)]
    [string]$InputPdf,

    [Parameter(Mandatory = $true)]
    [string]$OutputPdf,

    [string]$PythonExe = "C:\Program Files\Python312\python.exe",
    [string]$GhostscriptBin = "C:\Program Files\gs\gs10.07.1\bin",
    [string]$ChocolateyBin = "C:\ProgramData\chocolatey\bin",
    [string]$MsysUcrtBin = "C:\tools\msys64\ucrt64\bin",
    [string]$WorkRoot = "C:\codex_work",
    [string]$Language = "eng",
    [string]$Pages = "",
    [switch]$EnableJbig2,
    [switch]$LossyJbig2
)

$ErrorActionPreference = "Stop"

function Add-PathIfExists {
    param([string]$PathToAdd)

    if ((Test-Path -LiteralPath $PathToAdd) -and ($env:Path -notlike "*$PathToAdd*")) {
        $env:Path = "$PathToAdd;$env:Path"
    }
}

function Require-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required command '$Name' was not found. $InstallHint"
    }
    return $cmd.Source
}

function Test-Jbig2 {
    $cmd = Get-Command "jbig2" -ErrorAction SilentlyContinue
    if (-not $cmd) {
        return $false
    }

    $result = & $cmd.Source --version 2>&1
    $text = ($result | Out-String)
    if ($text -match "Mingw-w64 runtime failure|pseudo relocation") {
        Write-Warning "jbig2 was found at '$($cmd.Source)', but it fails at runtime. It will not be used."
        return $false
    }

    return $true
}

if (-not (Test-Path -LiteralPath $InputPdf)) {
    throw "Input PDF not found: $InputPdf"
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

$tmpRoot = Join-Path $WorkRoot "tmp"
$cacheRoot = Join-Path $WorkRoot "cache"
$ocrTmp = Join-Path $tmpRoot "ocrmypdf"
$pipCache = Join-Path $cacheRoot "pip"

New-Item -ItemType Directory -Force -Path $ocrTmp | Out-Null
New-Item -ItemType Directory -Force -Path $pipCache | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPdf) | Out-Null

$env:TEMP = $ocrTmp
$env:TMP = $ocrTmp
$env:PIP_CACHE_DIR = $pipCache

Add-PathIfExists $GhostscriptBin
Add-PathIfExists $ChocolateyBin

if ($EnableJbig2) {
    Add-PathIfExists $MsysUcrtBin
}

$ghostscript = Require-Command "gswin64c" "Install Ghostscript or update -GhostscriptBin."
$tesseract = Require-Command "tesseract" "Install Tesseract OCR and make sure it is on PATH."
$pngquant = Require-Command "pngquant" "Install with: choco install pngquant -y"
$unpaper = Require-Command "unpaper" "Install with: choco install unpaper -y"

Write-Host "Using Ghostscript: $ghostscript"
Write-Host "Using Tesseract:   $tesseract"
Write-Host "Using pngquant:    $pngquant"
Write-Host "Using unpaper:     $unpaper"
Write-Host "Using Python:      $PythonExe"

if ($EnableJbig2) {
    if (Test-Jbig2) {
        Write-Host "Using jbig2:       $((Get-Command jbig2).Source)"
    }
    else {
        Write-Warning "Continuing without JBIG2. Rebuild/fix jbig2, then rerun with -EnableJbig2."
        $env:Path = (($env:Path -split ";") | Where-Object { $_ -ne $MsysUcrtBin }) -join ";"
    }
}
else {
    Write-Host "JBIG2 disabled. Pass -EnableJbig2 after jbig2.exe works from PowerShell."
}

$ocrArgs = @(
    "-m", "ocrmypdf",
    "--force-ocr",
    "--deskew",
    "--clean",
    "--clean-final",
    "--rotate-pages",
    "--optimize", "3",
    "--output-type", "pdf",
    "-l", $Language
)

if ($Pages.Trim()) {
    $ocrArgs += @("--pages", $Pages)
}

if ($LossyJbig2) {
    if (-not $EnableJbig2) {
        throw "-LossyJbig2 requires -EnableJbig2."
    }
    $ocrArgs += "--jbig2-lossy"
}

$ocrArgs += @($InputPdf, $OutputPdf)

Write-Host "Running OCRmyPDF..."
& $PythonExe @ocrArgs

if ($LASTEXITCODE -ne 0) {
    throw "OCRmyPDF failed with exit code $LASTEXITCODE."
}

$output = Get-Item -LiteralPath $OutputPdf
Write-Host "Wrote: $($output.FullName)"
Write-Host ("Size:  {0:N1} MB" -f ($output.Length / 1MB))
