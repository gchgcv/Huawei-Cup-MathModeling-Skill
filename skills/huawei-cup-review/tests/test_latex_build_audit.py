from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_latex_build.py"


def run(tmp_path: Path, tex: str, log: str, strict: bool = True):
    tex_path = tmp_path / "main.tex"
    log_path = tmp_path / "main.log"
    tex_path.write_text(tex, encoding="utf-8")
    log_path.write_text(log, encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), str(tex_path), "--log", str(log_path)]
    if strict:
        cmd.append("--strict")
    return subprocess.run(cmd, text=True, capture_output=True)


def test_clean_build_passes(tmp_path):
    r = run(tmp_path, r"\documentclass{article}\begin{document}x\end{document}", "Output written on main.pdf (1 page).")
    assert r.returncode == 0


def test_float_error_fails(tmp_path):
    r = run(tmp_path, r"\begin{figure}[htbp]x\end{figure}", "LaTeX Warning: Float too large for page by 12.0pt")
    assert r.returncode == 1
    assert "float too large" in r.stderr


def test_overfull_is_warning_and_strict_failure(tmp_path):
    r = run(tmp_path, "x", r"Overfull \hbox (10.0pt too wide)")
    assert r.returncode == 1
    assert "overfull hbox" in r.stdout


def test_excessive_H_float_usage_warns(tmp_path):
    tex = "\n".join([r"\begin{figure}[H]x\end{figure}" for _ in range(4)])
    r = run(tmp_path, tex, "Output written on main.pdf")
    assert r.returncode == 1
    assert "[H] float placement" in r.stdout


def test_scans_input_subfiles(tmp_path):
    main = tmp_path / "main.tex"
    sec = tmp_path / "section.tex"
    log = tmp_path / "main.log"
    main.write_text(r"\documentclass{article}\begin{document}\input{section}\end{document}", encoding="utf-8")
    sec.write_text("\n".join([r"\begin{figure}[H]x\end{figure}" for _ in range(4)]), encoding="utf-8")
    log.write_text("Output written on main.pdf", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(main), "--log", str(log), "--strict"],
        text=True, capture_output=True,
    )
    assert r.returncode == 1
    assert "SOURCE_FILES_SCANNED: 2" in r.stdout
    assert "[H] float placement" in r.stdout
