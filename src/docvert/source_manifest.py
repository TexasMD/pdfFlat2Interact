"""Source PDF intake manifest generation for docvert.

This module performs Stage 0/1 intake checks only. It does not render pages,
extract text, run OCR, detect layout, or generate student/reviewer HTML.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("schemas/first_pilot_source_manifest_config.json")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"first_pilot_validation_{stamp}"


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    required = {"manifest_version", "pipeline_version", "intended_batch", "source_dir", "sources"}
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Manifest config missing required field(s): {', '.join(missing)}")

    source_ids = [source.get("source_id") for source in config["sources"]]
    duplicate_ids = sorted({source_id for source_id in source_ids if source_ids.count(source_id) > 1})
    if duplicate_ids:
        raise ValueError(f"Duplicate source_id value(s): {', '.join(duplicate_ids)}")

    return config


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_pdf_pages(path: Path) -> tuple[int | None, str | None, list[str]]:
    """Return page count, method, warnings."""
    warnings: list[str] = []

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return len(reader.pages), "pypdf", warnings
    except Exception as exc:  # pragma: no cover - depends on local optional package
        warnings.append(f"pypdf_page_count_failed: {exc.__class__.__name__}")

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        try:
            result = subprocess.run(
                [pdfinfo, str(path)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
                if match:
                    return int(match.group(1)), "pdfinfo", warnings
            warnings.append(f"pdfinfo_page_count_failed: exit_{result.returncode}")
        except OSError as exc:
            warnings.append(f"pdfinfo_page_count_failed: {exc.__class__.__name__}")

    try:
        data = path.read_bytes()
    except OSError as exc:
        warnings.append(f"pdf_regex_page_count_failed: {exc.__class__.__name__}")
        return None, None, warnings

    count = len(re.findall(rb"/Type\s*/Page\b", data))
    if count:
        warnings.append("page_count_used_pdf_regex_fallback")
        return count, "pdf_regex_fallback", warnings

    warnings.append("page_count_unavailable")
    return None, None, warnings


def page_traceability(source_id: str, filename: str, selected_pages: list[int]) -> list[dict[str, Any]]:
    return [
        {
            "source_id": source_id,
            "filename": filename,
            "page": page,
            "page_image_path": f"assets/page_images/{source_id}_p{page:03}.png",
            "traceability_status": "pending_render"
        }
        for page in selected_pages
    ]


def build_source_record(source: dict[str, Any], source_dir: Path, intended_batch: str) -> dict[str, Any]:
    source_id = source["source_id"]
    filename = source["filename"]
    selected_pages = list(source.get("selected_pages", []))
    source_path = source_dir / filename
    warnings = list(source.get("intake_warnings", []))

    record: dict[str, Any] = {
        "source_id": source_id,
        "filename": filename,
        "source_path": str(source_path),
        "file_hash_sha256": None,
        "page_count": None,
        "page_count_method": None,
        "source_status": "missing",
        "intake_status": "missing_source_file",
        "intended_batch": intended_batch,
        "selected_pages": selected_pages,
        "permission_or_use_notes": source.get("permission_or_use_notes", ""),
        "pilot_roles": list(source.get("pilot_roles", [])),
        "page_traceability": page_traceability(source_id, filename, selected_pages),
        "intake_warnings": warnings,
    }

    if not source_path.exists():
        record["intake_warnings"].append("expected_source_pdf_not_found")
        return record

    if source_path.suffix.lower() != ".pdf":
        record["source_status"] = "rejected"
        record["intake_status"] = "rejected_not_pdf"
        record["intake_warnings"].append("source_path_is_not_pdf")
        return record

    record["file_hash_sha256"] = sha256_file(source_path)
    page_count, method, page_warnings = count_pdf_pages(source_path)
    record["page_count"] = page_count
    record["page_count_method"] = method
    record["intake_warnings"].extend(page_warnings)

    if page_count is None:
        record["source_status"] = "needs_review"
        record["intake_status"] = "page_count_unavailable"
        return record

    invalid_pages = [page for page in selected_pages if page < 1 or page > page_count]
    if invalid_pages:
        record["source_status"] = "needs_review"
        record["intake_status"] = "selected_page_out_of_range"
        record["intake_warnings"].append(
            "selected_pages_out_of_range: " + ", ".join(str(page) for page in invalid_pages)
        )
        return record

    record["source_status"] = "source_pdf"
    record["intake_status"] = "ready_for_stage_1"
    return record


def build_manifest(
    config: dict[str, Any],
    project_root: Path,
    *,
    source_dir_override: Path | None = None,
    run_id: str | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    source_dir = source_dir_override or project_root / config["source_dir"]
    if not source_dir.is_absolute():
        source_dir = project_root / source_dir
    source_dir = source_dir.resolve()

    intended_batch = config["intended_batch"]
    records = [build_source_record(source, source_dir, intended_batch) for source in config["sources"]]
    missing = [record["filename"] for record in records if record["intake_status"] == "missing_source_file"]
    not_ready = [record["filename"] for record in records if record["source_status"] != "source_pdf"]
    ready_for_stage_1 = not not_ready

    manifest = {
        "manifest_version": config["manifest_version"],
        "pipeline_version": config["pipeline_version"],
        "run_id": run_id or default_run_id(),
        "generated_at_utc": generated_at_utc or utc_now_iso(),
        "intended_batch": intended_batch,
        "source_dir": str(source_dir),
        "conversion_authorized": False,
        "ready_for_stage_1": ready_for_stage_1,
        "stop_reason": None if ready_for_stage_1 else "source_intake_not_ready",
        "source_records": records,
        "hard_gates": config.get("hard_gates", []),
        "summary": {
            "expected_source_count": len(records),
            "ready_source_count": sum(1 for record in records if record["source_status"] == "source_pdf"),
            "missing_source_count": len(missing),
            "missing_sources": missing,
            "not_ready_sources": not_ready,
            "selected_page_count": sum(len(record["selected_pages"]) for record in records),
        },
    }
    return manifest


def write_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def _resolve_output_path(config: dict[str, Any], project_root: Path, output_override: Path | None) -> Path:
    output_path = output_override or Path(config.get("output_path", "data/runs/source_manifest.json"))
    if not output_path.is_absolute():
        output_path = project_root / output_path
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m docvert.source_manifest",
        description="Build the first-pilot source_manifest.json without conversion.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--source-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Write the manifest and return success even if expected PDFs are missing.",
    )
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_config(config_path)
    manifest = build_manifest(
        config,
        project_root,
        source_dir_override=args.source_dir,
        run_id=args.run_id,
    )
    output_path = _resolve_output_path(config, project_root, args.output)
    write_manifest(manifest, output_path)

    summary = manifest["summary"]
    print(f"Wrote source manifest: {output_path}")
    print(f"Ready sources: {summary['ready_source_count']}/{summary['expected_source_count']}")
    print(f"Selected pages: {summary['selected_page_count']}")
    print("No rendering, OCR, extraction, reviewer HTML, or student HTML was performed.")
    if not manifest["ready_for_stage_1"]:
        missing = ", ".join(summary["missing_sources"]) or "none"
        print(f"Source intake is not ready. Missing sources: {missing}")
        return 0 if args.allow_missing else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
