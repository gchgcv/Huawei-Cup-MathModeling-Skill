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
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


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


def test_review_language_leakage_is_warning_not_error(tmp_path):
    r = run(tmp_path, "现有证据不足以支持该模型适用于所有城市。")
    assert r.returncode == 0
    assert "Review-language leakage candidate" in r.stdout
    assert "现有证据不足以支持" in r.stdout


def test_need_to_point_out_is_warning_only_in_strict_mode(tmp_path):
    r = run(tmp_path, "需要指出的是，当前结果适用于本数据集。")
    assert r.returncode == 0
    assert "Review-language leakage candidate" in r.stdout
    assert r.stderr == ""


def test_mechanical_label_chain_is_warning_not_error(tmp_path):
    text = "本文构建了“候选点评价—布局优化—扰动分析”的研究框架。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "mechanical label-chain prose" in r.stdout


def test_label_chain_in_latex_caption_is_allowed(tmp_path):
    text = r"\begin{figure}\caption{“候选点评价—布局优化—扰动分析”的研究框架}\end{figure}"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "mechanical label-chain prose" not in r.stdout


def test_paragraph_final_negative_scope_is_flagged(tmp_path):
    text = "跨评委组的稳定增量判定仍未通过。\n\n问题四的验证协议未包含独立外部测试。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert r.stdout.count("paragraph-final negative scope") == 2


def test_positive_evidence_scope_is_not_flagged_as_negative_ending(tmp_path):
    text = "结果表现出模型与评委组依赖性，证据范围定位为特定条件下的预测变化。当前结果反映模型在内部交叉验证下的表现，外部泛化能力还需在独立样本上进一步检验。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "paragraph-final negative scope" not in r.stdout


def test_generic_conclusion_lead_is_soft_warning(tmp_path):
    r = run(tmp_path, "由此可以看出，随着降雨强度增加，积水深度持续上升。")
    assert r.returncode == 0
    assert "context-dependent AI-like phrase" in r.stdout
    assert "由此可以看出" in r.stdout


def test_agent_meta_prose_is_soft_warning(tmp_path):
    r = run(tmp_path, "因此需要分别明确三个问题的关系，下面分别进行讨论。")
    assert r.returncode == 0
    assert "context-dependent AI-like phrase" in r.stdout
    assert "因此需要分别明确" in r.stdout


def test_repeated_negative_interface_is_soft_warning(tmp_path):
    text = "问题三不使用问题一结果，也不调用问题二结果，不为问题二提供参数。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "negative interface-audit stacking" in r.stdout


def test_pending_solve_status_is_soft_warning(tmp_path):
    r = run(tmp_path, "当前尚未完成实际求解，最终方案仍待计算。")
    assert r.returncode == 0
    assert "work-status meta-prose" in r.stdout


def test_bounded_result_shows_phrase_is_not_a_review_leak(tmp_path):
    text = "优化方案的能耗由 1264.8 kWh 降至 1187.3 kWh。该结果表明，在当前设施参数下，调度方案兼顾了能耗控制与积水削减。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "Review-language leakage candidate" not in r.stdout


def test_mid_paragraph_negative_result_with_positive_scope_is_not_flagged(tmp_path):
    text = "独立检验未达到显著性水平。该结果适用于当前样本的组间比较。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "paragraph-final negative scope" not in r.stdout


def test_hedge_stacking_is_flagged(tmp_path):
    r = run(tmp_path, "结果可能在一定程度上潜在表明该变量或许会影响目标值。")
    assert r.returncode == 0
    assert "hedge stacking" in r.stdout


def test_long_de_chain_is_flagged_but_technical_terms_are_preserved(tmp_path):
    text = "基于多源数据的复杂约束条件的动态耦合关系的综合评价模型的计算结果表明，方案在给定容量约束下满足全部需求点。"
    r = run(tmp_path, text)
    assert r.returncode == 0
    assert "dense attributive chain" in r.stdout


def test_translation_like_passive_voice_is_warning_not_error(tmp_path):
    r = run(tmp_path, "该方法被用来优化锚链质量。")
    assert r.returncode == 0
    assert "passive/translation-like voice" in r.stdout
    assert "被用来" in r.stdout


def test_necessary_passive_voice_is_not_banned(tmp_path):
    r = run(tmp_path, "测量结果被记录在表中，供后续核对。")
    assert r.returncode == 0
    assert "passive/translation-like voice" not in r.stdout


def test_worklog_sequence_is_flagged(tmp_path):
    r = run(tmp_path, "首先清洗数据，随后建立模型，然后求解参数，最后进行敏感性分析。")
    assert r.returncode == 0
    assert "work-log-like sequencing" in r.stdout
