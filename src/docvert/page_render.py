"""Rendered page-image generation for docvert Stage 2.

This module renders full source pages only. It does not run OCR, embedded text
extraction, layout detection, reviewer HTML generation, or student HTML.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from docvert.source_manifest import load_config


DEFAULT_CONFIG_PATH = Path("schemas/first_pilot_source_manifest_config.json")
DEFAULT_SOURCE_MANIFEST_PATH = Path("data/runs/first_pilot/source_manifest.json")
DEFAULT_RENDER_MANIFEST_PATH = Path("data/runs/first_pilot/json/page_renders.json")
DEFAULT_ASSET_DIR = Path("data/runs/first_pilot/assets/page_images")
DEFAULT_DPI = 200

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def require_ready_source_manifest(manifest: dict[str, Any]) -> None:
    if not manifest.get("ready_for_stage_1"):
        raise ValueError("Source manifest is not ready for Stage 1/2 rendering.")


def manifest_source_records(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["source_id"]: record for record in manifest.get("source_records", [])}


def hard_gate_jobs(config: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Build render jobs for hard-gate pages only."""
    require_ready_source_manifest(manifest)
    records_by_source = manifest_source_records(manifest)
    jobs: list[dict[str, Any]] = []

    for gate in config.get("hard_gates", []):
        source_id = gate["source_id"]
        page = int(gate["page"])
        source_record = records_by_source.get(source_id)
        if not source_record:
            raise ValueError(f"Hard gate references unknown source_id: {source_id}")
        if source_record.get("source_status") != "source_pdf":
            raise ValueError(f"Hard gate source is not a confirmed source_pdf: {source_id}")
        if page not in source_record.get("selected_pages", []):
            raise ValueError(f"Hard gate page {source_id} p{page} is not in selected_pages.")
        page_count = source_record.get("page_count")
        if page_count is None or page < 1 or page > int(page_count):
            raise ValueError(f"Hard gate page {source_id} p{page} is outside page count.")

        jobs.append(
            {
                "gate_id": gate["id"],
                "source_id": source_id,
                "filename": source_record["filename"],
                "source_path": source_record["source_path"],
                "page": page,
            }
        )

    return jobs


def render_page(
    job: dict[str, Any],
    *,
    asset_dir: Path,
    asset_path_prefix: str,
    dpi: int,
    pdftoppm_path: str,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    source_path = Path(job["source_path"])
    page = int(job["page"])
    output_name = f"{job['source_id']}_p{page:03}.png"
    output_path = asset_dir / output_name
    output_prefix = output_path.with_suffix("")
    asset_dir.mkdir(parents=True, exist_ok=True)

    command = [
        pdftoppm_path,
        "-png",
        "-singlefile",
        "-f",
        str(page),
        "-l",
        str(page),
        "-r",
        str(dpi),
        str(source_path),
        str(output_prefix),
    ]
    result = runner(command, check=False, capture_output=True, text=True)

    warnings: list[str] = []
    if result.returncode != 0:
        return {
            "gate_id": job["gate_id"],
            "source_id": job["source_id"],
            "file": job["filename"],
            "page": page,
            "image_path": f"{asset_path_prefix}/{output_name}",
            "width_px": None,
            "height_px": None,
            "dpi": dpi,
            "render_tool": pdftoppm_path,
            "render_command": command,
            "render_status": "failed",
            "render_warnings": [f"pdftoppm_exit_{result.returncode}", result.stderr.strip()],
        }

    if not output_path.exists():
        return {
            "gate_id": job["gate_id"],
            "source_id": job["source_id"],
            "file": job["filename"],
            "page": page,
            "image_path": f"{asset_path_prefix}/{output_name}",
            "width_px": None,
            "height_px": None,
            "dpi": dpi,
            "render_tool": pdftoppm_path,
            "render_command": command,
            "render_status": "failed",
            "render_warnings": ["render_output_missing"],
        }

    try:
        with Image.open(output_path) as image:
            image.verify()
        with Image.open(output_path) as image:
            width_px, height_px = image.size
    except Exception as exc:
        return {
            "gate_id": job["gate_id"],
            "source_id": job["source_id"],
            "file": job["filename"],
            "page": page,
            "image_path": f"{asset_path_prefix}/{output_name}",
            "width_px": None,
            "height_px": None,
            "dpi": dpi,
            "render_tool": pdftoppm_path,
            "render_command": command,
            "render_status": "failed",
            "render_warnings": [f"image_open_failed: {exc.__class__.__name__}"],
        }

    return {
        "gate_id": job["gate_id"],
        "source_id": job["source_id"],
        "file": job["filename"],
        "page": page,
        "image_path": f"{asset_path_prefix}/{output_name}",
        "width_px": width_px,
        "height_px": height_px,
        "dpi": dpi,
        "render_tool": pdftoppm_path,
        "render_command": command,
        "render_status": "rendered",
        "render_warnings": warnings,
    }


def build_render_manifest(
    *,
    config: dict[str, Any],
    source_manifest: dict[str, Any],
    render_records: list[dict[str, Any]],
    dpi: int,
) -> dict[str, Any]:
    failures = [record for record in render_records if record["render_status"] != "rendered"]
    return {
        "manifest_version": 1,
        "pipeline_version": config["pipeline_version"],
        "run_id": source_manifest["run_id"],
        "generated_at_utc": utc_now_iso(),
        "stage": "stage_2_page_rendering",
        "scope": "first_three_hard_gates",
        "dpi": dpi,
        "rendering_only": True,
        "ocr_performed": False,
        "text_extraction_performed": False,
        "layout_detection_performed": False,
        "reviewer_html_generated": False,
        "student_html_generated": False,
        "render_ready": not failures,
        "render_records": render_records,
        "summary": {
            "requested_pages": len(render_records),
            "rendered_pages": sum(1 for record in render_records if record["render_status"] == "rendered"),
            "failed_pages": len(failures),
            "failed": [
                {"source_id": record["source_id"], "page": record["page"], "warnings": record["render_warnings"]}
                for record in failures
            ],
        },
    }


def render_hard_gates(
    *,
    config_path: Path,
    source_manifest_path: Path,
    render_manifest_path: Path,
    asset_dir: Path,
    dpi: int,
    pdftoppm_path: str | None = None,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    config = load_config(config_path)
    source_manifest = load_json(source_manifest_path)
    jobs = hard_gate_jobs(config, source_manifest)
    resolved_pdftoppm = pdftoppm_path or shutil.which("pdftoppm")
    if not resolved_pdftoppm:
        raise FileNotFoundError("pdftoppm was not found on PATH.")

    records = [
        render_page(
            job,
            asset_dir=asset_dir,
            asset_path_prefix="assets/page_images",
            dpi=dpi,
            pdftoppm_path=resolved_pdftoppm,
            runner=runner,
        )
        for job in jobs
    ]
    manifest = build_render_manifest(
        config=config,
        source_manifest=source_manifest,
        render_records=records,
        dpi=dpi,
    )
    write_json(render_manifest_path, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m docvert.page_render",
        description="Render first-pilot hard-gate source pages without OCR or extraction.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_RENDER_MANIFEST_PATH)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    parser.add_argument("--pdftoppm", default=None)
    args = parser.parse_args(argv)

    manifest = render_hard_gates(
        config_path=args.config,
        source_manifest_path=args.source_manifest,
        render_manifest_path=args.output,
        asset_dir=args.asset_dir,
        dpi=args.dpi,
        pdftoppm_path=args.pdftoppm,
    )
    summary = manifest["summary"]
    print(f"Wrote page render manifest: {args.output}")
    print(f"Rendered pages: {summary['rendered_pages']}/{summary['requested_pages']}")
    print("No OCR, text extraction, layout detection, reviewer HTML, or student HTML was performed.")
    return 0 if manifest["render_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
