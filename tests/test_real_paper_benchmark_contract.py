from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = REPO_ROOT / "benchmark" / "real-paper" / "wine-evaluation"


def test_real_paper_case_preserves_required_ab_evidence_fields() -> None:
    text = (CASE_ROOT / "ab-records.md").read_text(encoding="utf-8")
    assert text.count("## AB-") >= 4
    for required in (
        "Original / Legacy A",
        "Writing output",
        "Review finding",
        "Final version",
        "Rule IDs",
        "Human adjudication",
        "Fidelity validation",
    ):
        assert text.count(required) >= 4


def test_real_paper_case_tracks_partial_human_adjudication() -> None:
    text = (CASE_ROOT / "ab-records.md").read_text(encoding="utf-8")
    assert text.count("PENDING_USER_REVIEW") == 2
    assert text.count("PASS_USER_APPROVED_2026-08-30") == 3
    assert "PASS_WITH_HUMAN_ADJUDICATION_PENDING" in (
        CASE_ROOT / "README.md"
    ).read_text(encoding="utf-8")


def test_real_paper_case_records_negative_ending_false_negative_repair() -> None:
    text = (CASE_ROOT / "ab-records.md").read_text(encoding="utf-8")
    assert text.count("P2 / ADW-003") == 3
    assert "稳定增量要求 PLS 与 Elastic Net 的结果同时改善" in text
    assert "更换质量代理后，增量方向应保持一致" in text
    assert "不同模型给出的增量方向仍不一致" in text
    assert "白葡萄酒的结果反映的是当前模型和评委组条件下的预测变化" in text
    assert "当前结果反映模型在内部交叉验证下的表现" in text
    assert "外部泛化能力还需在独立样本上进一步检验" in text


def test_real_paper_case_records_frozen_external_hashes() -> None:
    text = (CASE_ROOT / "README.md").read_text(encoding="utf-8")
    for digest in (
        "7DCC7FF936EE6B0BA8A510786EE3ACA3765231A8885133FAB022A4D28F381D4E",
        "670D087764EA1D595718E1453F48D6245C3D630D164826E6179EB4A9B07B57DF",
        "04CB88C07B5272C3FE1F85C2C35D7CC0EA4EC038E977FEF74E0EF6EE27431E39",
    ):
        assert digest in text
