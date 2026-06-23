import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docvert.cli import main
from docvert import __version__


def test_main_version(capsys):
    """Test that main(["--version"]) prints the version and exits with 0."""
    result = main(["--version"])

    assert result == 0

    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_main_status(capsys):
    """Test that main(["--status"]) prints the status message and exits with 0."""
    result = main(["--status"])

    assert result == 0

    captured = capsys.readouterr()
    assert "docvert is in the first extraction/validation pilot phase." in captured.out
    assert "Read docs/09_PILOT_PAGE_SELECTION.md" in captured.out
    assert "Use scripts/run-ocr-cleanup.ps1" in captured.out


def test_main_no_args(capsys, monkeypatch):
    """Test that main(None) or main([]) prints the default status message and exits with 0."""
    # Test with None - we need to patch sys.argv because argparse uses sys.argv[1:] if argv is None
    monkeypatch.setattr(sys, "argv", ["docvert"])
    result_none = main()
    assert result_none == 0

    captured_none = capsys.readouterr()
    assert "docvert is in the first extraction/validation pilot phase." in captured_none.out

    # Test with empty list
    result_empty = main([])
    assert result_empty == 0

    captured_empty = capsys.readouterr()
    assert "docvert is in the first extraction/validation pilot phase." in captured_empty.out
