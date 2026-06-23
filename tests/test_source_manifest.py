import hashlib
import json
from pathlib import Path

from docvert.source_manifest import build_manifest, count_pdf_pages, load_config, main


MINIMAL_TWO_PAGE_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""


def write_config(path: Path, source_dir: str) -> None:
    path.write_text(
        json.dumps(
            {
                "manifest_version": 1,
                "pipeline_version": 4,
                "intended_batch": "unit_test_batch",
                "source_dir": source_dir,
                "sources": [
                    {
                        "source_id": "sample",
                        "filename": "sample.pdf",
                        "selected_pages": [1, 2],
                        "permission_or_use_notes": "unit test"
                    }
                ],
                "hard_gates": [{"id": "sample_gate", "source_id": "sample", "page": 1}],
            }
        ),
        encoding="utf-8",
    )


def test_count_pdf_pages_uses_available_method(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(MINIMAL_TWO_PAGE_PDF)

    page_count, method, warnings = count_pdf_pages(pdf_path)

    assert page_count == 2
    assert method in {"pypdf", "pdfinfo", "pdf_regex_fallback"}
    assert isinstance(warnings, list)


def test_build_manifest_marks_missing_sources(tmp_path):
    config_path = tmp_path / "config.json"
    source_dir = tmp_path / "source"
    write_config(config_path, str(source_dir))

    config = load_config(config_path)
    manifest = build_manifest(config, tmp_path, run_id="test_run", generated_at_utc="2026-06-22T00:00:00+00:00")

    record = manifest["source_records"][0]
    assert manifest["ready_for_stage_1"] is False
    assert manifest["stop_reason"] == "source_intake_not_ready"
    assert record["source_status"] == "missing"
    assert record["intake_status"] == "missing_source_file"
    assert record["page_traceability"][0]["traceability_status"] == "pending_render"


def test_build_manifest_records_hash_page_count_and_selected_pages(tmp_path):
    config_path = tmp_path / "config.json"
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdf_path = source_dir / "sample.pdf"
    pdf_path.write_bytes(MINIMAL_TWO_PAGE_PDF)
    write_config(config_path, str(source_dir))

    config = load_config(config_path)
    manifest = build_manifest(config, tmp_path, run_id="test_run", generated_at_utc="2026-06-22T00:00:00+00:00")

    record = manifest["source_records"][0]
    assert manifest["ready_for_stage_1"] is True
    assert record["source_status"] == "source_pdf"
    assert record["intake_status"] == "ready_for_stage_1"
    assert record["page_count"] == 2
    assert record["selected_pages"] == [1, 2]
    assert record["file_hash_sha256"] == hashlib.sha256(MINIMAL_TWO_PAGE_PDF).hexdigest()
    assert record["page_traceability"][1]["page_image_path"] == "assets/page_images/sample_p002.png"


def test_cli_writes_manifest_with_allow_missing(tmp_path):
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "source_manifest.json"
    write_config(config_path, str(tmp_path / "missing_source"))

    exit_code = main([
        "--config",
        str(config_path),
        "--project-root",
        str(tmp_path),
        "--output",
        str(output_path),
        "--run-id",
        "cli_test_run",
        "--allow-missing",
    ])

    assert exit_code == 0
    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest["run_id"] == "cli_test_run"
    assert manifest["ready_for_stage_1"] is False
