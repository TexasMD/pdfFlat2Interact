"""OCR text extraction for docvert Stage 4.

This module runs OCR on already-rendered page images. The output is a
visible-text hypothesis for later comparison against embedded PDF text, not
proof of visible content. It does not run OCR-vs-PDF comparison, layout
detection, reviewer HTML, or student HTML.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_RENDER_MANIFEST_PATH = Path("data/runs/first_pilot/json/page_renders.json")
DEFAULT_PDF_TEXT_MANIFEST_PATH = Path("data/runs/first_pilot/json/pdf_text.json")
DEFAULT_OUTPUT_PATH = Path("data/runs/first_pilot/json/ocr_text.json")
DEFAULT_LANGUAGE = "eng"
DEFAULT_PSM = 3

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


def find_tesseract() -> str | None:
    found = shutil.which("tesseract")
    if found:
        return found

    windows_default = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if windows_default.exists():
        return str(windows_default)
    return None


def _int_value(value: str) -> int:
    return int(float(value))


def _float_value(value: str) -> float:
    return float(value)


def parse_tesseract_tsv(tsv_text: str) -> dict[str, Any]:
    """Parse Tesseract TSV stdout into word-level OCR evidence."""
    if not tsv_text.strip():
        return {
            "coordinate_space": "image_pixels",
            "text": "",
            "word_count": 0,
            "mean_confidence": None,
            "words": [],
        }

    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    required = {"level", "block_num", "par_num", "line_num", "word_num", "left", "top", "width", "height", "conf", "text"}
    missing = sorted(required - set(reader.fieldnames or []))
    if missing:
        raise ValueError(f"Tesseract TSV missing required column(s): {', '.join(missing)}")

    words: list[dict[str, Any]] = []
    confidences: list[float] = []
    for row in reader:
        if row.get("level") != "5":
            continue
        text = (row.get("text") or "").strip()
        if not text:
            continue

        left = _int_value(row["left"])
        top = _int_value(row["top"])
        width = _int_value(row["width"])
        height = _int_value(row["height"])
        confidence = _float_value(row["conf"])
        if confidence >= 0:
            confidences.append(confidence)

        words.append(
            {
                "text": text,
                "confidence": confidence,
                "bbox": {
                    "x0": left,
                    "y0": top,
                    "x1": left + width,
                    "y1": top + height,
                    "width": width,
                    "height": height,
                },
                "block_num": _int_value(row["block_num"]),
                "par_num": _int_value(row["par_num"]),
                "line_num": _int_value(row["line_num"]),
                "word_num": _int_value(row["word_num"]),
            }
        )

    mean_confidence = round(sum(confidences) / len(confidences), 2) if confidences else None
    return {
        "coordinate_space": "image_pixels",
        "text": " ".join(word["text"] for word in words),
        "word_count": len(words),
        "mean_confidence": mean_confidence,
        "words": words,
    }


def require_ready_inputs(render_manifest: dict[str, Any], pdf_text_manifest: dict[str, Any]) -> None:
    if not render_manifest.get("render_ready"):
        raise ValueError("Render manifest is not ready for OCR.")
    if not pdf_text_manifest.get("extraction_ready"):
        raise ValueError("PDF text manifest is not ready for OCR.")
    if render_manifest.get("run_id") != pdf_text_manifest.get("run_id"):
        raise ValueError("Render manifest and PDF text manifest run_id values differ.")


def pdf_text_records_by_page(pdf_text_manifest: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (record["source_id"], int(record["page"])): record
        for record in pdf_text_manifest.get("page_records", [])
    }


def ocr_jobs(
    render_manifest: dict[str, Any],
    pdf_text_manifest: dict[str, Any],
    *,
    run_root: Path,
) -> list[dict[str, Any]]:
    require_ready_inputs(render_manifest, pdf_text_manifest)
    pdf_records = pdf_text_records_by_page(pdf_text_manifest)
    jobs: list[dict[str, Any]] = []

    for render_record in render_manifest.get("render_records", []):
        if render_record.get("render_status") != "rendered":
            raise ValueError(f"Cannot run OCR for unrendered page: {render_record}")

        source_id = render_record["source_id"]
        page = int(render_record["page"])
        pdf_record = pdf_records.get((source_id, page))
        if not pdf_record:
            raise ValueError(f"Rendered page lacks Stage 3 PDF text record: {source_id} p{page}")
        if pdf_record.get("extraction_status") != "extracted":
            raise ValueError(f"Stage 3 PDF text record is not extracted: {source_id} p{page}")

        image_reference = Path(render_record["image_path"])
        image_path = image_reference if image_reference.is_absolute() else run_root / image_reference
        jobs.append(
            {
                "gate_id": render_record.get("gate_id"),
                "source_id": source_id,
                "filename": render_record["file"],
                "source_path": pdf_record.get("source_path"),
                "page": page,
                "rendered_page_image": render_record["image_path"],
                "rendered_page_image_path": str(image_path),
                "rendered_page_width_px": render_record["width_px"],
                "rendered_page_height_px": render_record["height_px"],
                "dpi": render_record.get("dpi"),
                "stage3_risk_flags": list(pdf_record.get("stage3_risk_flags", [])),
            }
        )

    return jobs


def extract_page_ocr(
    job: dict[str, Any],
    *,
    tesseract_path: str,
    language: str,
    psm: int,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    image_path = Path(job["rendered_page_image_path"])
    page = int(job["page"])
    dpi = int(job.get("dpi") or 200)
    command = [
        tesseract_path,
        str(image_path),
        "stdout",
        "-l",
        language,
        "--psm",
        str(psm),
        "--dpi",
        str(dpi),
        "tsv",
    ]
    warnings: list[str] = []

    base_record = {
        "gate_id": job.get("gate_id"),
        "source_id": job["source_id"],
        "file": job["filename"],
        "source_path": job.get("source_path"),
        "page": page,
        "rendered_page_image": job["rendered_page_image"],
        "rendered_page_image_path": str(image_path),
        "rendered_page_width_px": job["rendered_page_width_px"],
        "rendered_page_height_px": job["rendered_page_height_px"],
        "coordinate_space": "image_pixels",
        "ocr_engine": "tesseract",
        "ocr_engine_path": tesseract_path,
        "ocr_language": language,
        "ocr_psm": psm,
        "ocr_dpi": dpi,
        "ocr_command": command,
        "ocr_method": "tesseract_tsv",
        "stage3_risk_flags": list(job.get("stage3_risk_flags", [])),
    }

    if not image_path.exists():
        return {
            **base_record,
            "ocr_status": "failed",
            "text": "",
            "word_count": 0,
            "mean_confidence": None,
            "words": [],
            "ocr_warnings": ["rendered_page_image_missing"],
        }

    result = runner(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return {
            **base_record,
            "ocr_status": "failed",
            "text": "",
            "word_count": 0,
            "mean_confidence": None,
            "words": [],
            "ocr_warnings": [f"tesseract_exit_{result.returncode}", result.stderr.strip()],
        }

    if result.stderr.strip():
        warnings.append(result.stderr.strip())

    try:
        parsed = parse_tesseract_tsv(result.stdout)
    except ValueError as exc:
        return {
            **base_record,
            "ocr_status": "failed",
            "text": "",
            "word_count": 0,
            "mean_confidence": None,
            "words": [],
            "ocr_warnings": [str(exc)],
        }

    if parsed["word_count"] == 0:
        warnings.append("ocr_text_empty_or_unavailable")

    return {
        **base_record,
        "ocr_status": "ocr_complete",
        "text": parsed["text"],
        "word_count": parsed["word_count"],
        "mean_confidence": parsed["mean_confidence"],
        "words": parsed["words"],
        "ocr_warnings": warnings,
    }


def build_ocr_manifest(
    *,
    render_manifest: dict[str, Any],
    pdf_text_manifest: dict[str, Any],
    page_records: list[dict[str, Any]],
    pdf_text_manifest_path: Path | None = None,
) -> dict[str, Any]:
    failures = [record for record in page_records if record["ocr_status"] != "ocr_complete"]
    sparse = [record for record in page_records if record["word_count"] == 0]
    confidences = [
        record["mean_confidence"]
        for record in page_records
        if record.get("mean_confidence") is not None
    ]
    return {
        "manifest_version": 1,
        "pipeline_version": render_manifest["pipeline_version"],
        "run_id": render_manifest["run_id"],
        "generated_at_utc": utc_now_iso(),
        "stage": "stage_4_ocr_visible_text_extraction",
        "scope": render_manifest["scope"],
        "pdf_text_manifest_path": str(pdf_text_manifest_path) if pdf_text_manifest_path else None,
        "ocr_only": True,
        "ocr_performed": True,
        "embedded_pdf_text_extraction_performed": True,
        "text_comparison_performed": False,
        "layout_detection_performed": False,
        "reviewer_html_generated": False,
        "student_html_generated": False,
        "ocr_ready": not failures,
        "page_records": page_records,
        "summary": {
            "requested_pages": len(page_records),
            "ocr_pages": sum(1 for record in page_records if record["ocr_status"] == "ocr_complete"),
            "failed_pages": len(failures),
            "sparse_or_empty_pages": [
                {"source_id": record["source_id"], "page": record["page"]}
                for record in sparse
            ],
            "word_count_total": sum(record["word_count"] for record in page_records),
            "mean_confidence": round(sum(confidences) / len(confidences), 2) if confidences else None,
            "carried_stage3_risk_flag_count": sum(
                len(record.get("stage3_risk_flags", [])) for record in page_records
            ),
        },
    }


def run_ocr_for_rendered_pages(
    *,
    render_manifest_path: Path,
    pdf_text_manifest_path: Path,
    output_path: Path,
    tesseract_path: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    psm: int = DEFAULT_PSM,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    render_manifest = load_json(render_manifest_path)
    pdf_text_manifest = load_json(pdf_text_manifest_path)
    run_root = render_manifest_path.parent.parent
    jobs = ocr_jobs(render_manifest, pdf_text_manifest, run_root=run_root)
    resolved_tesseract = tesseract_path or find_tesseract()
    if not resolved_tesseract:
        raise FileNotFoundError("tesseract was not found on PATH or at the default Windows install path.")

    records = [
        extract_page_ocr(
            job,
            tesseract_path=resolved_tesseract,
            language=language,
            psm=psm,
            runner=runner,
        )
        for job in jobs
    ]
    manifest = build_ocr_manifest(
        render_manifest=render_manifest,
        pdf_text_manifest=pdf_text_manifest,
        page_records=records,
        pdf_text_manifest_path=pdf_text_manifest_path,
    )
    write_json(output_path, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m docvert.ocr_text",
        description="Run OCR on rendered hard-gate page images only.",
    )
    parser.add_argument("--render-manifest", type=Path, default=DEFAULT_RENDER_MANIFEST_PATH)
    parser.add_argument("--pdf-text-manifest", type=Path, default=DEFAULT_PDF_TEXT_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--tesseract", default=None)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--psm", type=int, default=DEFAULT_PSM)
    args = parser.parse_args(argv)

    manifest = run_ocr_for_rendered_pages(
        render_manifest_path=args.render_manifest,
        pdf_text_manifest_path=args.pdf_text_manifest,
        output_path=args.output,
        tesseract_path=args.tesseract,
        language=args.language,
        psm=args.psm,
    )
    summary = manifest["summary"]
    print(f"Wrote OCR text manifest: {args.output}")
    print(f"OCR pages: {summary['ocr_pages']}/{summary['requested_pages']}")
    print(f"Total OCR words: {summary['word_count_total']}")
    print("No OCR-vs-PDF comparison, layout detection, reviewer HTML, or student HTML was performed.")
    return 0 if manifest["ocr_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
