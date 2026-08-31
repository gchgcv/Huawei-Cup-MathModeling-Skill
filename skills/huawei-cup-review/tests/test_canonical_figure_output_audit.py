from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_canonical_figure_outputs.py"


def write_manifest(tmp_path: Path, allowed_files: list[str] | None = None) -> Path:
    data = {
        "figure_root": "outputs/figures",
        "canonical": [
            {"id": "fig:q1", "file": "01_q1.png", "source": "plot.py"}
        ],
        "allowed_files": allowed_files or [],
        "trash_dir": "outputs/figures/.trash",
    }
    path = tmp_path / "figure-manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def run(tmp_path: Path, strict: bool = False) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        str(write_manifest(tmp_path)),
        "--project-root",
        str(tmp_path),
    ]
    if strict:
        command.append("--strict")
    return subprocess.run(command, check=False, text=True, capture_output=True)


def prepare_canonical(tmp_path: Path) -> Path:
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)
    (figures / "01_q1.png").write_bytes(b"png")
    return figures


def test_clean_manifest_passes_and_ignores_trash(tmp_path: Path) -> None:
    figures = prepare_canonical(tmp_path)
    trash = figures / ".trash"
    trash.mkdir()
    (trash / "q1_old.png").write_bytes(b"png")

    result = run(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "MODE: READ_ONLY" in result.stdout
    assert "MUTATIONS: none" in result.stdout
    assert "OK: canonical figure output set is clean" in result.stdout


def test_unexpected_output_is_reported_without_mutation(tmp_path: Path) -> None:
    figures = prepare_canonical(tmp_path)
    unexpected = figures / "q1_old.png"
    unexpected.write_bytes(b"png")

    result = run(tmp_path)

    assert result.returncode == 1
    assert "UNEXPECTED: q1_old.png" in result.stdout
    assert "does not move or remove files" in result.stdout
    assert unexpected.exists()
    assert not (figures / ".trash" / "q1_old.png").exists()


def test_referenced_unexpected_output_is_located(tmp_path: Path) -> None:
    figures = prepare_canonical(tmp_path)
    (figures / "q1_old.png").write_bytes(b"png")
    (tmp_path / "main.tex").write_text(
        r"\includegraphics{outputs/figures/q1_old.png}", encoding="utf-8"
    )

    result = run(tmp_path)

    assert result.returncode == 1
    assert "REFERENCED_UNEXPECTED: q1_old.png" in result.stdout
    assert "main.tex" in result.stdout


def test_missing_canonical_output_fails(tmp_path: Path) -> None:
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)

    result = run(tmp_path)

    assert result.returncode == 1
    assert "missing canonical figure: 01_q1.png" in result.stderr


def test_non_numbered_unexpected_output_is_reported(tmp_path: Path) -> None:
    figures = prepare_canonical(tmp_path)
    (figures / "preview.png").write_bytes(b"png")

    normal = run(tmp_path)
    strict = run(tmp_path, strict=True)

    assert normal.returncode == 1
    assert strict.returncode == 1
    assert "non-numbered unexpected figure filename: preview.png" in normal.stdout


def test_auditor_source_has_no_mutation_operation() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    forbidden = ("write_text(", "write_bytes(", "unlink(", "rename(", "shutil.move")
    assert all(token not in text for token in forbidden)
