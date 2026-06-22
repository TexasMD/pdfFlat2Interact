# Windows Setup Guide

This guide explains how to set up the environment required to run the OCR cleanup workflow on Windows.

## Prerequisites

You need to install the following tools:

- Python 3.12
- Tesseract
- Ghostscript
- Chocolatey
- `pngquant`
- `unpaper`

### 1. Chocolatey, pngquant, and unpaper

First, install [Chocolatey](https://chocolatey.org/install), a package manager for Windows. Open an administrative PowerShell prompt and follow the instructions on their site.

Once Chocolatey is installed, you can easily install `pngquant` and `unpaper` from an administrative prompt:

```powershell
choco install pngquant -y
choco install unpaper -y
```

### 2. Tesseract and Ghostscript

- **Tesseract**: Download and install the Tesseract OCR engine for Windows. Make sure the installation directory is added to your system `PATH`.
- **Ghostscript**: Download and install Ghostscript. The cleanup script checks for it at `C:\Program Files\gs\gs10.07.1\bin` by default, but you can override this with the `-GhostscriptBin` parameter.

### 3. Python 3.12 and OCRmyPDF

Install Python 3.12 for Windows. Ensure the installer adds it to your system `PATH` or note the installation path. By default, the PowerShell script expects Python at `C:\Program Files\Python312\python.exe`, but you can customize this via `-PythonExe`.

Next, install the required Python packages:

```powershell
pip install ocrmypdf
```

#### ⚠️ PATH Pitfalls (Important)
If you also use MSYS2 (see below for JBIG2), **do not** put MSYS2's `python.exe` on your system `PATH` before your primary Windows Python 3.12. OCRmyPDF must be run using the standard Windows Python to function correctly. Ensure your Windows Python is discovered first when running python commands.

---

## Optional: JBIG2 with MSYS2

If you want to use the `-EnableJbig2` flag to produce highly compressed, lossy outputs, you'll need the `jbig2` encoder. A convenient way to get this on Windows is by building it with MSYS2.

1. **Install MSYS2**: Download from [msys2.org](https://www.msys2.org/) and install (usually to `C:\tools\msys64`).
2. **Open MSYS2 UCRT64** terminal and build `jbig2enc` from source.
3. The resulting `jbig2.exe` will be located in the UCRT64 bin directory, for instance: `C:\tools\msys64\ucrt64\bin`.

**Important**: When running the script, pass this directory using `-MsysUcrtBin "C:\tools\msys64\ucrt64\bin"`.
Do **not** add the entire MSYS2 root or the MSYS2 Python environment to your global Windows `PATH`, as it will conflict with your primary Python setup.

---

## Example Usage

Once your environment is configured, you can run the OCR cleanup script. Here is an example:

```powershell
.\scripts\run-ocr-cleanup.ps1 -InputPdf "C:\path\to\input.pdf" -OutputPdf "C:\path\to\output\cleaned.pdf" -EnableJbig2
```

If your tool paths differ from the defaults, supply them as arguments:

```powershell
.\scripts\run-ocr-cleanup.ps1 `
  -InputPdf "C:\path\to\input.pdf" `
  -OutputPdf "C:\path\to\output.pdf" `
  -PythonExe "C:\Python312\python.exe" `
  -GhostscriptBin "C:\Program Files\gs\gs10.08.0\bin" `
  -ChocolateyBin "C:\ProgramData\chocolatey\bin" `
  -MsysUcrtBin "C:\tools\msys64\ucrt64\bin" `
  -EnableJbig2
```
