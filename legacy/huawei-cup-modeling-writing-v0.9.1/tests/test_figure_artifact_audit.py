from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_figure_outputs.py"


def manifest(tmp_path: Path) -> Path:
    data = {
        "figure_root": "outputs/figures",
        "canonical": [{"id": "fig:q1", "file": "01_q1.png", "source": "plot.py"}],
        "allowed_files": [],
        "trash_dir": "outputs/figures/.trash",
    }
    p = tmp_path / "figure-manifest.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def run(tmp_path: Path, apply: bool = False, confirm: str = ""):
    cmd = [sys.executable, str(SCRIPT), str(manifest(tmp_path)), "--project-root", str(tmp_path)]
    if apply:
        cmd.append("--apply-trash")
        if confirm:
            cmd += ["--confirm-plan-hash", confirm]
    return subprocess.run(cmd, text=True, capture_output=True)


def plan_hash(result: subprocess.CompletedProcess[str]) -> str:
    for line in result.stdout.splitlines():
        if line.startswith("TRASH_PLAN_HASH: "):
            return line.split(": ", 1)[1].strip()
    raise AssertionError(result.stdout)


def test_unexpected_figure_fails_dry_run(tmp_path):
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)
    (figures / "01_q1.png").write_bytes(b"x")
    (figures / "q1_old.png").write_bytes(b"x")
    r = run(tmp_path)
    assert r.returncode == 1
    assert "MODE: DRY_RUN" in r.stdout
    assert "UNEXPECTED: q1_old.png" in r.stdout
    assert (figures / "q1_old.png").exists()


def test_apply_moves_unreferenced_unexpected_to_trash(tmp_path):
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)
    (figures / "01_q1.png").write_bytes(b"x")
    (figures / "q1_old.png").write_bytes(b"x")
    dry = run(tmp_path)
    r = run(tmp_path, apply=True, confirm=plan_hash(dry))
    assert r.returncode == 0, r.stderr + r.stdout
    assert not (figures / "q1_old.png").exists()
    assert (figures / ".trash" / "q1_old.png").exists()
    assert (figures / "01_q1.png").exists()


def test_referenced_unexpected_is_not_moved(tmp_path):
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)
    (figures / "01_q1.png").write_bytes(b"x")
    (figures / "q1_old.png").write_bytes(b"x")
    (tmp_path / "main.tex").write_text(r"\includegraphics{outputs/figures/q1_old.png}", encoding="utf-8")
    dry = run(tmp_path)
    r = run(tmp_path, apply=True, confirm=plan_hash(dry))
    assert r.returncode == 1
    assert "referenced unexpected figure not moved" in r.stderr
    assert (figures / "q1_old.png").exists()


def test_apply_requires_prior_dry_run_hash(tmp_path):
    figures = tmp_path / "outputs" / "figures"
    figures.mkdir(parents=True)
    (figures / "01_q1.png").write_bytes(b"x")
    (figures / "q1_old.png").write_bytes(b"x")
    r = run(tmp_path, apply=True)
    assert r.returncode == 2
    assert "requires --confirm-plan-hash from a prior dry-run" in r.stderr
    assert (figures / "q1_old.png").exists()
