import subprocess
from pathlib import Path

from docvert.ocr_text import (
    build_ocr_manifest,
    extract_page_ocr,
    ocr_jobs,
    parse_tesseract_tsv,
)


TSV_TEXT = "\n".join(
    [
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext",
        "1\t1\t0\t0\t0\t0\t0\t0\t100\t200\t-1\t",
        "5\t1\t1\t1\t1\t1\t10\t20\t30\t12\t95.5\tHello",
        "5\t1\t1\t1\t1\t2\t45\t20\t35\t12\t85.0\tworld",
        "5\t1\t1\t1\t1\t3\t90\t20\t10\t12\t-1\t",
    ]
)


def test_parse_tesseract_tsv_extracts_words_confidence_and_boxes():
    parsed = parse_tesseract_tsv(TSV_TEXT)

    assert parsed["coordinate_space"] == "image_pixels"
    assert parsed["text"] == "Hello world"
    assert parsed["word_count"] == 2
    assert parsed["mean_confidence"] == 90.25
    assert parsed["words"][0]["bbox"] == {"x0": 10, "y0": 20, "x1": 40, "y1": 32, "width": 30, "height": 12}
    assert parsed["words"][0]["confidence"] == 95.5


def test_ocr_jobs_follow_render_records_and_require_pdf_text(tmp_path):
    render_manifest = {
        "render_ready": True,
        "run_id": "run_1",
        "render_records": [
            {
                "gate_id": "gate_one",
                "source_id": "sample",
                "file": "sample.pdf",
                "page": 1,
                "render_status": "rendered",
                "image_path": "assets/page_images/sample_p001.png",
                "width_px": 100,
                "height_px": 200,
                "dpi": 200,
            }
        ],
    }
    pdf_text_manifest = {
        "extraction_ready": True,
        "run_id": "run_1",
        "page_records": [
            {
                "source_id": "sample",
                "file": "sample.pdf",
                "source_path": "data/source/sample.pdf",
                "page": 1,
                "extraction_status": "extracted",
                "stage3_risk_flags": [{"issue_type": "example"}],
            }
        ],
    }

    jobs = ocr_jobs(render_manifest, pdf_text_manifest, run_root=tmp_path)

    assert len(jobs) == 1
    assert jobs[0]["gate_id"] == "gate_one"
    assert jobs[0]["source_path"] == "data/source/sample.pdf"
    assert jobs[0]["rendered_page_image_path"] == str(tmp_path / "assets/page_images/sample_p001.png")
    assert jobs[0]["stage3_risk_flags"] == [{"issue_type": "example"}]


def test_extract_page_ocr_records_words_and_render_traceability(tmp_path):
    image_path = tmp_path / "sample_p001.png"
    image_path.write_bytes(b"not really a png for unit tests")

    def fake_runner(command, check, capture_output, text, encoding, errors):
        return subprocess.CompletedProcess(command, 0, TSV_TEXT, "")

    record = extract_page_ocr(
        {
            "gate_id": "gate",
            "source_id": "sample",
            "filename": "sample.pdf",
            "source_path": "data/source/sample.pdf",
            "page": 1,
            "rendered_page_image": "assets/page_images/sample_p001.png",
            "rendered_page_image_path": str(image_path),
            "rendered_page_width_px": 100,
            "rendered_page_height_px": 200,
            "dpi": 200,
            "stage3_risk_flags": [{"issue_type": "example"}],
        },
        tesseract_path="tesseract",
        language="eng",
        psm=3,
        runner=fake_runner,
    )

    assert record["ocr_status"] == "ocr_complete"
    assert record["text"] == "Hello world"
    assert record["word_count"] == 2
    assert record["mean_confidence"] == 90.25
    assert record["rendered_page_image"] == "assets/page_images/sample_p001.png"
    assert record["ocr_command"][0] == "tesseract"
    assert "tsv" in record["ocr_command"]
    assert record["stage3_risk_flags"] == [{"issue_type": "example"}]


def test_build_ocr_manifest_marks_no_comparison_or_layout():
    manifest = build_ocr_manifest(
        render_manifest={"pipeline_version": 4, "run_id": "run_1", "scope": "first_three_hard_gates"},
        pdf_text_manifest={"run_id": "run_1"},
        page_records=[
            {
                "source_id": "sample",
                "page": 1,
                "ocr_status": "ocr_complete",
                "word_count": 2,
                "mean_confidence": 90.0,
                "stage3_risk_flags": [{"issue_type": "example"}],
            }
        ],
    )

    assert manifest["stage"] == "stage_4_ocr_visible_text_extraction"
    assert manifest["ocr_only"] is True
    assert manifest["ocr_performed"] is True
    assert manifest["text_comparison_performed"] is False
    assert manifest["layout_detection_performed"] is False
    assert manifest["student_html_generated"] is False
    assert manifest["summary"]["word_count_total"] == 2
    assert manifest["summary"]["carried_stage3_risk_flag_count"] == 1
