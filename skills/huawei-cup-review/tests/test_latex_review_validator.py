from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_latex_review.py"
HAS_PAGE_COUNTER = importlib.util.find_spec("fitz") is not None or shutil.which("pdfinfo") is not None


def make_pdf(path: Path) -> None:
    # Minimal one-page PDF with correct xref offsets.
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\n",
    ]
    buf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(buf))
        buf.extend(obj)
    xref = len(buf)
    buf.extend(f"xref\n0 {len(objects)+1}\n".encode())
    buf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.extend(f"{off:010d} 00000 n \n".encode())
    buf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(buf)


@pytest.mark.skipif(not HAS_PAGE_COUNTER, reason="PyMuPDF and pdfinfo unavailable")
def test_full_review_passes_for_current_pdf(tmp_path):
    pdf = tmp_path / "paper.pdf"
    make_pdf(pdf)
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    review = {
        "pdf": "paper.pdf", "pdf_sha256": digest, "page_count": 1,
        "scope": "full", "affected_pages": [], "rendered_pages": [1],
        "reviewed_pages": [1], "status": "PASS", "notes": []
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(review), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), str(path), "--strict"], text=True, capture_output=True, check=False)
    assert r.returncode == 0, r.stderr + r.stdout
    assert "matches the current PDF" in r.stdout


@pytest.mark.skipif(not HAS_PAGE_COUNTER, reason="PyMuPDF and pdfinfo unavailable")
def test_hash_change_invalidates_review(tmp_path):
    pdf = tmp_path / "paper.pdf"
    make_pdf(pdf)
    review = {
        "pdf": "paper.pdf", "pdf_sha256": "0" * 64, "page_count": 1,
        "scope": "full", "affected_pages": [], "rendered_pages": [1],
        "reviewed_pages": [1], "status": "PASS", "notes": []
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(review), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), str(path), "--strict"], text=True, capture_output=True, check=False)
    assert r.returncode == 1
    assert "old visual review is invalid" in r.stderr
