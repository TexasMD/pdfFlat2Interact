"""Command-line entry point for the docvert pipeline scaffold."""

from __future__ import annotations

import argparse

from docvert import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docvert",
        description="Layout-aware, validation-first PDF conversion pipeline scaffold.",
    )
    parser.add_argument("--version", action="store_true", help="Show the package version and exit.")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show the current implementation status.",
    )
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    print("docvert is in the first extraction/validation pilot phase.")
    print("Read docs/09_PILOT_PAGE_SELECTION.md before running conversion work.")
    print("Use scripts/run-ocr-cleanup.ps1 for OCR preprocessing today.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
