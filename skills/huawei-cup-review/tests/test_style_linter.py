from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lint_paper_style.py"


def run(tmp_path: Path, text: str, strict: bool = True):
    p = tmp_path / "paper.md"
    p.write_text(text, encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), str(p)]
    if strict:
        cmd.append("--strict")
    return subprocess.run(cmd, text=True, capture_output=True)


def test_high_risk_phrase_fails_strict(tmp_path):
    r = run(tmp_path, "毋庸置疑，该方法具有不可磨灭的贡献。")
    assert r.returncode == 1
    assert "high-risk rhetorical phrase" in r.stderr


def test_technical_terms_are_not_banned(tmp_path):
    r = run(tmp_path, "采用混合整数线性规划（MILP）建立运输模型，并以总成本为目标函数。")
    assert r.returncode == 0


def test_quotes_are_warning_not_error(tmp_path):
    r = run(tmp_path, "本文将该方案称为“基准方案”，用于后续比较。")
    assert r.returncode == 0
    assert "Chinese quote pair" in r.stdout


def test_defensive_scope_is_warning_not_automatic_error(tmp_path):
    r = run(tmp_path, "本文并不声称该模型适用于所有场景，只用于当前样本分析。")
    assert r.returncode == 0
    assert "defensive/negative scope framing" in r.stdout


def test_hedge_stacking_is_flagged(tmp_path):
    r = run(tmp_path, "结果可能在一定程度上潜在表明该变量或许会影响目标值。")
    assert r.returncode == 0
    assert "hedge stacking" in r.stdout


def test_long_de_chain_is_flagged_but_technical_terms_are_preserved(tmp_path):
    text = "基于多源数据的复杂约束条件的动态耦合关系的综合评价模型的计算结果表明，方案在给定容量约束下满足全部需求点。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "dense attributive chain" in r.stdout


def test_worklog_sequence_is_flagged(tmp_path):
    r = run(tmp_path, "首先清洗数据，随后建立模型，然后求解参数，最后进行敏感性分析。")
    assert r.returncode == 0
    assert "work-log-like sequencing" in r.stdout
