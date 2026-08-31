#!/usr/bin/env python3
"""Validate that a LaTeX PDF visual-review record belongs to the current PDF."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import fitz
except ImportError:  # pragma: no cover - exercised only without optional dependency
    fitz = None

ALLOWED_SCOPE = {"affected", "full"}
ALLOWED_STATUS = {"UNVERIFIED", "PASS"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_page_count(path: Path) -> int | None:
    if fitz is not None:
        try:
            with fitz.open(str(path)) as document:
                return document.page_count
        except (OSError, RuntimeError, ValueError):
            pass

    exe = shutil.which("pdfinfo")
    if not exe:
        return None
    proc = subprocess.run([exe, str(path)], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return None
    m = re.search(r"^Pages:\s+(\d+)\s*$", proc.stdout, re.MULTILINE)
    return int(m.group(1)) if m else None


def page_set(value: object, field: str, errors: list[str]) -> set[int]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return set()
    out: set[int] = set()
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool) or item < 1:
            errors.append(f"{field} contains invalid page: {item!r}")
        else:
            out.add(item)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("review", type=Path)
    ap.add_argument("--pdf", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    try:
        data = json.loads(args.review.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read review: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    pdf = args.pdf or Path(str(data.get("pdf", "")))
    if not pdf.is_absolute():
        pdf = (args.review.parent / pdf).resolve()
    if not pdf.is_file():
        print(f"ERROR: PDF not found: {pdf}", file=sys.stderr)
        return 2

    declared_hash = str(data.get("pdf_sha256", "")).strip().lower()
    actual_hash = sha256(pdf)
    if not declared_hash:
        errors.append("pdf_sha256 is missing")
    elif declared_hash != actual_hash:
        errors.append("pdf_sha256 does not match current PDF; old visual review is invalid")

    declared_pages = data.get("page_count")
    if not isinstance(declared_pages, int) or isinstance(declared_pages, bool) or declared_pages < 1:
        errors.append("page_count must be a positive integer")
        declared_pages = 0
    actual_pages = pdf_page_count(pdf)
    if actual_pages is None:
        msg = "cannot independently read PDF page count (PyMuPDF and pdfinfo unavailable or failed)"
        (errors if args.strict else warnings).append(msg)
    elif declared_pages and actual_pages != declared_pages:
        errors.append(f"page_count mismatch: review={declared_pages}, pdf={actual_pages}")

    scope = data.get("scope")
    if scope not in ALLOWED_SCOPE:
        errors.append(f"invalid scope: {scope!r}")
    status = data.get("status")
    if status not in ALLOWED_STATUS:
        errors.append(f"invalid status: {status!r}")

    rendered = page_set(data.get("rendered_pages", []), "rendered_pages", errors)
    reviewed = page_set(data.get("reviewed_pages", []), "reviewed_pages", errors)
    affected = page_set(data.get("affected_pages", []), "affected_pages", errors)

    if declared_pages:
        valid = set(range(1, declared_pages + 1))
        for field, pages in [("rendered_pages", rendered), ("reviewed_pages", reviewed), ("affected_pages", affected)]:
            extra = sorted(pages - valid)
            if extra:
                errors.append(f"{field} contains pages beyond page_count: {extra}")
        if scope == "full":
            missing_render = sorted(valid - rendered)
            missing_review = sorted(valid - reviewed)
            if missing_render:
                errors.append(f"full review missing rendered pages: {missing_render}")
            if missing_review:
                errors.append(f"full review missing reviewed pages: {missing_review}")
        elif scope == "affected":
            if not affected:
                errors.append("affected review requires non-empty affected_pages")
            if affected - rendered:
                errors.append(f"affected pages not rendered: {sorted(affected-rendered)}")
            if affected - reviewed:
                errors.append(f"affected pages not reviewed: {sorted(affected-reviewed)}")

    if status == "PASS" and errors:
        errors.append("status PASS is not allowed while review evidence is incomplete or stale")
    if status == "PASS" and scope == "affected":
        print("NOTE: affected-scope PASS validates only the declared local revision, not the full-paper layout.")

    for msg in warnings:
        print(f"WARNING: {msg}")
    for msg in errors:
        print(f"ERROR: {msg}", file=sys.stderr)
    print(f"PDF_SHA256: {actual_hash}")
    if actual_pages is not None:
        print(f"PDF_PAGES: {actual_pages}")
    print(f"SCOPE: {scope}")
    if errors:
        return 1
    print("OK: LaTeX visual-review evidence matches the current PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
