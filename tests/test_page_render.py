import json
import subprocess
from pathlib import Path

from PIL import Image

from docvert.page_render import (
    build_render_manifest,
    hard_gate_jobs,
    render_page,
)


def test_hard_gate_jobs_are_limited_to_configured_gates():
    config = {
        "pipeline_version": 4,
        "hard_gates": [
            {"id": "gate_one", "source_id": "sample", "page": 1},
            {"id": "gate_two", "source_id": "sample", "page": 2},
        ],
    }
    manifest = {
        "ready_for_stage_1": True,
        "source_records": [
            {
                "source_id": "sample",
                "filename": "sample.pdf",
                "source_path": "data/source/sample.pdf",
                "source_status": "source_pdf",
                "selected_pages": [1, 2, 3],
                "page_count": 3,
            }
        ],
    }

    jobs = hard_gate_jobs(config, manifest)

    assert [job["gate_id"] for job in jobs] == ["gate_one", "gate_two"]
    assert [job["page"] for job in jobs] == [1, 2]


def test_hard_gate_jobs_reject_unready_manifest():
    config = {"hard_gates": [{"id": "gate", "source_id": "sample", "page": 1}]}
    manifest = {"ready_for_stage_1": False, "source_records": []}

    try:
        hard_gate_jobs(config, manifest)
    except ValueError as exc:
        assert "not ready" in str(exc)
    else:
        raise AssertionError("hard_gate_jobs should reject unready manifests")


def test_render_page_records_dimensions_and_command(tmp_path):
    source_path = tmp_path / "sample.pdf"
    source_path.write_bytes(b"%PDF-1.4\n")
    asset_dir = tmp_path / "assets"

    def fake_runner(command, check, capture_output, text):
        output_prefix = Path(command[-1])
        Image.new("RGB", (12, 34), "white").save(output_prefix.with_suffix(".png"))
        return subprocess.CompletedProcess(command, 0, "", "")

    record = render_page(
        {
            "gate_id": "gate",
            "source_id": "sample",
            "filename": "sample.pdf",
            "source_path": str(source_path),
            "page": 1,
        },
        asset_dir=asset_dir,
        asset_path_prefix="assets/page_images",
        dpi=200,
        pdftoppm_path="pdftoppm",
        runner=fake_runner,
    )

    assert record["render_status"] == "rendered"
    assert record["width_px"] == 12
    assert record["height_px"] == 34
    assert record["image_path"] == "assets/page_images/sample_p001.png"
    assert record["render_command"][0] == "pdftoppm"
    assert "-singlefile" in record["render_command"]


def test_build_render_manifest_marks_stage_scope():
    manifest = build_render_manifest(
        config={"pipeline_version": 4},
        source_manifest={"run_id": "run_1"},
        render_records=[
            {
                "source_id": "sample",
                "page": 1,
                "render_status": "rendered",
                "render_warnings": [],
            }
        ],
        dpi=200,
    )

    assert manifest["stage"] == "stage_2_page_rendering"
    assert manifest["scope"] == "first_three_hard_gates"
    assert manifest["ocr_performed"] is False
    assert manifest["student_html_generated"] is False
    assert manifest["render_ready"] is True
    assert manifest["summary"]["rendered_pages"] == 1
