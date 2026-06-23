import subprocess
from pathlib import Path

from docvert.pdf_text import (
    build_pdf_text_manifest,
    extraction_jobs,
    extract_page_pdf_text,
    parse_bbox_xhtml,
    stage3_risk_flags,
)


BBOX_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <body>
    <doc>
      <page width="612" height="792">
        <word xMin="10" yMin="20" xMax="40" yMax="30">Hello</word>
        <word xMin="45" yMin="20" xMax="80" yMax="30">world</word>
      </page>
    </doc>
  </body>
</html>
"""


def test_parse_bbox_xhtml_extracts_words_and_page_size(tmp_path):
    path = tmp_path / "bbox.xhtml"
    path.write_text(BBOX_XHTML, encoding="utf-8")

    parsed = parse_bbox_xhtml(path)

    assert parsed["page_width"] == 612
    assert parsed["page_height"] == 792
    assert parsed["coordinate_space"] == "pdf_points"
    assert parsed["text"] == "Hello world"
    assert parsed["word_count"] == 2
    assert parsed["words"][0]["bbox"] == {"x0": 10.0, "y0": 20.0, "x1": 40.0, "y1": 30.0}


def test_extraction_jobs_follow_render_records_only():
    source_manifest = {
        "ready_for_stage_1": True,
        "source_records": [
            {
                "source_id": "sample",
                "filename": "sample.pdf",
                "source_path": "data/source/sample.pdf",
                "source_status": "source_pdf",
                "selected_pages": [1, 2],
            }
        ],
    }
    render_manifest = {
        "render_ready": True,
        "render_records": [
            {
                "gate_id": "gate_one",
                "source_id": "sample",
                "page": 1,
                "render_status": "rendered",
                "image_path": "assets/page_images/sample_p001.png",
                "width_px": 100,
                "height_px": 200,
            }
        ],
    }

    jobs = extraction_jobs(source_manifest, render_manifest)

    assert len(jobs) == 1
    assert jobs[0]["gate_id"] == "gate_one"
    assert jobs[0]["rendered_page_image"] == "assets/page_images/sample_p001.png"


def test_extract_page_pdf_text_records_words_and_render_traceability(tmp_path):
    source_path = tmp_path / "sample.pdf"
    source_path.write_bytes(b"%PDF-1.4\n")

    def fake_runner(command, check, capture_output, text):
        Path(command[-1]).write_text(BBOX_XHTML, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    record = extract_page_pdf_text(
        {
            "gate_id": "gate",
            "source_id": "sample",
            "filename": "sample.pdf",
            "source_path": str(source_path),
            "page": 1,
            "rendered_page_image": "assets/page_images/sample_p001.png",
            "rendered_page_width_px": 100,
            "rendered_page_height_px": 200,
        },
        temp_dir=tmp_path / "tmp",
        pdftotext_path="pdftotext",
        runner=fake_runner,
    )

    assert record["extraction_status"] == "extracted"
    assert record["text"] == "Hello world"
    assert record["word_count"] == 2
    assert record["source_path"] == str(source_path)
    assert record["rendered_page_image"] == "assets/page_images/sample_p001.png"
    assert record["bbox_xhtml_path"].endswith("sample_p001_bbox.xhtml")
    assert record["extraction_command"][0] == "pdftotext"
    assert "-bbox-layout" in record["extraction_command"]
    assert record["stage3_risk_flags"] == []


def test_stage3_risk_flags_mark_known_hard_gate_hypotheses():
    money_flags = stage3_risk_flags("money_cents_symbol_sumbridge2_p2", "coins worth 110")
    factoid_flags = stage3_risk_flags("layout_factoid_separation_sumbridge2_p1", "instruction factoid")
    number_line_flags = stage3_risk_flags("number_line_visual_reference", "-10 -9 -8")

    assert money_flags[0]["issue_type"] == "possible_cents_symbol_misread"
    assert factoid_flags[0]["issue_type"] == "possible_layout_block_merge_error"
    assert number_line_flags[0]["issue_type"] == "visual_reference_required_or_helpful"


def test_build_pdf_text_manifest_marks_no_ocr_or_layout():
    manifest = build_pdf_text_manifest(
        source_manifest={"run_id": "run_1"},
        render_manifest={"pipeline_version": 4, "scope": "first_three_hard_gates"},
        page_records=[
            {
                "source_id": "sample",
                "page": 1,
                "extraction_status": "extracted",
                "word_count": 2,
                "stage3_risk_flags": [{"issue_type": "example"}],
            }
        ],
    )

    assert manifest["stage"] == "stage_3_embedded_pdf_text_extraction"
    assert manifest["pdf_text_only"] is True
    assert manifest["embedded_pdf_text_extraction_performed"] is True
    assert manifest["ocr_performed"] is False
    assert manifest["layout_detection_performed"] is False
    assert manifest["student_html_generated"] is False
    assert manifest["summary"]["word_count_total"] == 2
    assert manifest["summary"]["risk_flag_count"] == 1
