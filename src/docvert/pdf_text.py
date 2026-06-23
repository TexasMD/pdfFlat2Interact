"""Embedded PDF text extraction for docvert Stage 3.

This module extracts PDF text-layer evidence for already-rendered pages. The
output is a hypothesis for later OCR comparison, not proof of visible content.
It does not run OCR, layout detection, reviewer HTML, or student HTML.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from xml.etree import ElementTree


DEFAULT_SOURCE_MANIFEST_PATH = Path("data/runs/first_pilot/source_manifest.json")
DEFAULT_RENDER_MANIFEST_PATH = Path("data/runs/first_pilot/json/page_renders.json")
DEFAULT_OUTPUT_PATH = Path("data/runs/first_pilot/json/pdf_text.json")

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


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_bbox_xhtml(path: Path) -> dict[str, Any]:
    """Parse Poppler pdftotext -bbox-layout XHTML into page and word records."""
    root = ElementTree.parse(path).getroot()
    page_element = None
    words: list[dict[str, Any]] = []

    for element in root.iter():
        name = local_name(element.tag)
        if name == "page" and page_element is None:
            page_element = element
        elif name == "word":
            text = "".join(element.itertext())
            if not text:
                continue
            words.append(
                {
                    "text": text,
                    "bbox": {
                        "x0": float(element.attrib["xMin"]),
                        "y0": float(element.attrib["yMin"]),
                        "x1": float(element.attrib["xMax"]),
                        "y1": float(element.attrib["yMax"]),
                    },
                }
            )

    page_width = float(page_element.attrib["width"]) if page_element is not None and "width" in page_element.attrib else None
    page_height = float(page_element.attrib["height"]) if page_element is not None and "height" in page_element.attrib else None

    return {
        "page_width": page_width,
        "page_height": page_height,
        "coordinate_space": "pdf_points",
        "text": " ".join(word["text"] for word in words),
        "word_count": len(words),
        "words": words,
    }


def stage3_risk_flags(gate_id: str | None, text: str) -> list[dict[str, Any]]:
    """Carry known first-pilot extraction risks forward until issue emission."""
    gate = gate_id or ""
    flags: list[dict[str, Any]] = []

    if "layout_factoid" in gate:
        flags.append(
            {
                "issue_type": "possible_layout_block_merge_error",
                "severity": "high",
                "reason": "Hard gate requires factoid/sidebar separation; PDF text reading order may merge unrelated blocks.",
                "requires_later_issue_emission": True,
            }
        )

    if "money_cents_symbol" in gate and "\u00a2" not in text and re.search(r"\b\d{2,3}0\b", text):
        flags.append(
            {
                "issue_type": "possible_cents_symbol_misread",
                "severity": "high",
                "reason": "Money hard gate text has trailing-zero values and no cents sign in the embedded PDF text.",
                "requires_later_issue_emission": True,
            }
        )

    if "number_line" in gate:
        flags.append(
            {
                "issue_type": "visual_reference_required_or_helpful",
                "severity": "medium",
                "reason": "Hard gate depends on preserving or recreating a number-line visual reference.",
                "requires_later_issue_emission": True,
            }
        )

    return flags


def require_ready_inputs(source_manifest: dict[str, Any], render_manifest: dict[str, Any]) -> None:
    if not source_manifest.get("ready_for_stage_1"):
        raise ValueError("Source manifest is not ready for embedded text extraction.")
    if not render_manifest.get("render_ready"):
        raise ValueError("Render manifest is not ready for embedded text extraction.")


def source_records_by_id(source_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["source_id"]: record for record in source_manifest.get("source_records", [])}


def extraction_jobs(source_manifest: dict[str, Any], render_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    require_ready_inputs(source_manifest, render_manifest)
    source_records = source_records_by_id(source_manifest)
    jobs: list[dict[str, Any]] = []

    for render_record in render_manifest.get("render_records", []):
        if render_record.get("render_status") != "rendered":
            raise ValueError(f"Cannot extract text for unrendered page: {render_record}")

        source_id = render_record["source_id"]
        source_record = source_records.get(source_id)
        if not source_record:
            raise ValueError(f"Render record references unknown source_id: {source_id}")

        page = int(render_record["page"])
        if page not in source_record.get("selected_pages", []):
            raise ValueError(f"Rendered page {source_id} p{page} is not in selected_pages.")

        jobs.append(
            {
                "gate_id": render_record.get("gate_id"),
                "source_id": source_id,
                "filename": source_record["filename"],
                "source_path": source_record["source_path"],
                "page": page,
                "rendered_page_image": render_record["image_path"],
                "rendered_page_width_px": render_record["width_px"],
                "rendered_page_height_px": render_record["height_px"],
            }
        )

    return jobs


def extract_page_pdf_text(
    job: dict[str, Any],
    *,
    temp_dir: Path,
    pdftotext_path: str,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    page = int(job["page"])
    output_path = temp_dir / f"{job['source_id']}_p{page:03}_bbox.xhtml"
    command = [
        pdftotext_path,
        "-bbox-layout",
        "-enc",
        "UTF-8",
        "-f",
        str(page),
        "-l",
        str(page),
        job["source_path"],
        str(output_path),
    ]
    result = runner(command, check=False, capture_output=True, text=True)
    warnings: list[str] = []

    base_record = {
        "gate_id": job.get("gate_id"),
        "source_id": job["source_id"],
        "file": job["filename"],
        "source_path": job["source_path"],
        "page": page,
        "rendered_page_image": job["rendered_page_image"],
        "rendered_page_width_px": job["rendered_page_width_px"],
        "rendered_page_height_px": job["rendered_page_height_px"],
        "bbox_xhtml_path": str(output_path),
        "extraction_tool": pdftotext_path,
        "extraction_command": command,
        "extraction_method": "poppler_pdftotext_bbox_layout",
    }

    if result.returncode != 0:
        return {
            **base_record,
            "extraction_status": "failed",
            "text": "",
            "word_count": 0,
            "page_width": None,
            "page_height": None,
            "coordinate_space": "pdf_points",
            "words": [],
            "extraction_warnings": [f"pdftotext_exit_{result.returncode}", result.stderr.strip()],
            "stage3_risk_flags": stage3_risk_flags(job.get("gate_id"), ""),
        }

    if result.stderr.strip():
        warnings.append(result.stderr.strip())
    if not output_path.exists():
        return {
            **base_record,
            "extraction_status": "failed",
            "text": "",
            "word_count": 0,
            "page_width": None,
            "page_height": None,
            "coordinate_space": "pdf_points",
            "words": [],
            "extraction_warnings": ["pdftotext_output_missing"],
            "stage3_risk_flags": stage3_risk_flags(job.get("gate_id"), ""),
        }

    parsed = parse_bbox_xhtml(output_path)
    if parsed["word_count"] == 0:
        warnings.append("embedded_pdf_text_empty_or_unavailable")
    risk_flags = stage3_risk_flags(job.get("gate_id"), parsed["text"])

    return {
        **base_record,
        "extraction_status": "extracted",
        "page_width": parsed["page_width"],
        "page_height": parsed["page_height"],
        "coordinate_space": parsed["coordinate_space"],
        "text": parsed["text"],
        "word_count": parsed["word_count"],
        "words": parsed["words"],
        "extraction_warnings": warnings,
        "stage3_risk_flags": risk_flags,
    }


def build_pdf_text_manifest(
    *,
    source_manifest: dict[str, Any],
    render_manifest: dict[str, Any],
    page_records: list[dict[str, Any]],
) -> dict[str, Any]:
    failures = [record for record in page_records if record["extraction_status"] != "extracted"]
    sparse = [record for record in page_records if record["word_count"] == 0]
    risk_flag_count = sum(len(record.get("stage3_risk_flags", [])) for record in page_records)
    return {
        "manifest_version": 1,
        "pipeline_version": render_manifest["pipeline_version"],
        "run_id": source_manifest["run_id"],
        "generated_at_utc": utc_now_iso(),
        "stage": "stage_3_embedded_pdf_text_extraction",
        "scope": render_manifest["scope"],
        "pdf_text_only": True,
        "embedded_pdf_text_extraction_performed": True,
        "ocr_performed": False,
        "text_comparison_performed": False,
        "layout_detection_performed": False,
        "reviewer_html_generated": False,
        "student_html_generated": False,
        "extraction_ready": not failures,
        "page_records": page_records,
        "summary": {
            "requested_pages": len(page_records),
            "extracted_pages": sum(1 for record in page_records if record["extraction_status"] == "extracted"),
            "failed_pages": len(failures),
            "sparse_or_empty_pages": [
                {"source_id": record["source_id"], "page": record["page"]}
                for record in sparse
            ],
            "word_count_total": sum(record["word_count"] for record in page_records),
            "risk_flag_count": risk_flag_count,
        },
    }


def extract_pdf_text_for_rendered_pages(
    *,
    source_manifest_path: Path,
    render_manifest_path: Path,
    output_path: Path,
    temp_dir: Path,
    pdftotext_path: str | None = None,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    source_manifest = load_json(source_manifest_path)
    render_manifest = load_json(render_manifest_path)
    jobs = extraction_jobs(source_manifest, render_manifest)
    resolved_pdftotext = pdftotext_path or shutil.which("pdftotext")
    if not resolved_pdftotext:
        raise FileNotFoundError("pdftotext was not found on PATH.")

    records = [
        extract_page_pdf_text(
            job,
            temp_dir=temp_dir,
            pdftotext_path=resolved_pdftotext,
            runner=runner,
        )
        for job in jobs
    ]
    manifest = build_pdf_text_manifest(
        source_manifest=source_manifest,
        render_manifest=render_manifest,
        page_records=records,
    )
    write_json(output_path, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m docvert.pdf_text",
        description="Extract embedded PDF text for rendered hard-gate pages only.",
    )
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST_PATH)
    parser.add_argument("--render-manifest", type=Path, default=DEFAULT_RENDER_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--temp-dir", type=Path, default=Path("data/runs/first_pilot/tmp/pdf_text_bbox"))
    parser.add_argument("--pdftotext", default=None)
    args = parser.parse_args(argv)

    manifest = extract_pdf_text_for_rendered_pages(
        source_manifest_path=args.source_manifest,
        render_manifest_path=args.render_manifest,
        output_path=args.output,
        temp_dir=args.temp_dir,
        pdftotext_path=args.pdftotext,
    )
    summary = manifest["summary"]
    print(f"Wrote PDF text manifest: {args.output}")
    print(f"Extracted pages: {summary['extracted_pages']}/{summary['requested_pages']}")
    print(f"Total PDF text words: {summary['word_count_total']}")
    print("No OCR, text comparison, layout detection, reviewer HTML, or student HTML was performed.")
    return 0 if manifest["extraction_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
