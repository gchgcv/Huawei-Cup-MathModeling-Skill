from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_manifest_routes_reference_management_separately():
    text = read("manifest.yaml")
    assert "references/reference-management.md" in text
    assert "paper structure, abstract, conclusion, or final writing checklist" in text


def test_reference_management_is_canonical_and_scoped():
    text = read("references/reference-management.md")
    assert "唯一详细规则源" in text
    assert "正式论文的参考文献表不得为空" in text
    assert "官方参考答案" in text
    assert "对照材料" in text
    assert "纯读题、建模、编程或局部结果分析任务" in text
    assert "不得生成虚构的作者、题名、期刊或 DOI" in text


def test_paper_writing_delegates_reference_policy():
    text = read("references/paper-writing.md")
    assert "references/reference-management.md" in text
    assert "官方参考答案" not in text
    assert "培训机构" not in text


def test_result_visualization_separates_figure_and_pdf_layout_roles():
    text = read("references/result-visualization.md")
    assert "图文件本身" in text
    assert "references/latex-pdf-layout-audit.md" in text
    assert "实际生成文件" in text
    assert "FIGURE_VISUAL_UNVERIFIED" in text
    assert "主要说明文字默认使用中文" in text
    assert "missing glyph" in text


def test_stage_fragments_route_instead_of_copying_detailed_lists():
    figure_stage = read("static/fragments/stage/result-visualization.md")
    paper_stage = read("static/fragments/stage/paper-writing.md")
    assert "references/result-visualization.md" in figure_stage
    assert "references/reference-management.md" in paper_stage
    # detailed source lists should stay in the canonical reference file
    assert "培训机构现成解答" not in paper_stage
    assert "missing glyph" not in figure_stage


def test_quality_gate_knows_new_v082_issue_codes():
    quality = read("static/core/quality-gates.md")
    validator = read("scripts/validate_quality_report.py")
    for code in [
        "REFERENCE_MISSING",
        "REFERENCE_POLICY_VIOLATION",
        "REFERENCE_RELEVANCE_LOW",
        "FIGURE_VISUAL_UNVERIFIED",
        "FIGURE_VISUAL_DEFECT",
    ]:
        assert code in quality
        assert f'"{code}"' in validator


def test_v090_forbids_unrequested_parallel_tex_sources():
    skill = read("SKILL.md")
    contract = read("static/core/execution-contract.md")
    editing = read("references/document-editing.md")
    assert "未经用户明确要求" in skill
    assert "main_fixed.tex" in skill
    assert "未经用户明确要求创建新的 LaTeX 文件" in contract
    assert "用户要求“修改论文”" in editing


def test_v090_routes_micro_revision_and_scope_escalation():
    manifest = read("manifest.yaml")
    micro = read("static/fragments/mode/micro-revision.md")
    assert "micro-revision" in manifest
    assert "自动升级条件" in micro
    assert "分页" in micro and "浮动" in micro and "编号" in micro


def test_v090_has_canonical_figure_management_and_safe_trash():
    manifest = read("manifest.yaml")
    ref = read("references/figure-artifact-management.md")
    assert "references/figure-artifact-management.md" in manifest
    assert "canonical" in ref
    assert "dry-run" in ref
    assert ".trash" in ref
    assert "不得直接" in ref


def test_v090_quality_score_is_explicitly_internal_and_last():
    quality = read("static/core/quality-gates.md")
    validator = read("scripts/validate_quality_report.py")
    assert "硬阻断项 → 证据缺口 → 可改进项 → 内部诊断分数" in quality
    assert "INTERNAL_DIAGNOSTIC_SCORE" in validator
    assert "not an official competition score" in validator


def test_v090_carries_round_6_7_paper_review_rules():
    skill = read("SKILL.md")
    quality = read("static/core/quality-gates.md")
    writing = read("references/paper-writing.md")
    references = read("references/reference-management.md")
    layout = read("references/latex-pdf-layout-audit.md")
    submission = read("static/fragments/stage/submission-audit.md")
    validator = read("scripts/validate_quality_report.py")
    assert "模型假设结构" in skill
    assert "总—分结构" in quality and "总述—分条假设" in writing
    assert "顺序编码与格式统一" in references
    assert "最多两列" in layout
    assert "报告精度" in submission
    for code in [
        "MODEL_ASSUMPTION_STRUCTURE_THIN",
        "SYMBOL_GEOMETRY_UNEXPLAINED",
        "FIGURE_LAYOUT_UNREADABLE",
        "UNIT_PRESENTATION_ERROR",
        "REPORT_PRECISION_MISMATCH",
        "REFERENCE_ORDER_ERROR",
        "REFERENCE_FORMAT_INCONSISTENT",
        "AI_STYLE_OVERUSE",
    ]:
        assert code in quality
        assert f'"{code}"' in validator


def test_v091_writing_focus_and_anti_defensive_rules():
    skill = read("SKILL.md")
    prose = read("references/paper-prose-style.md")
    writing = read("references/paper-writing.md")
    quality = read("static/core/quality-gates.md")
    validator = read("scripts/validate_quality_report.py")
    assert "论文写作与审校优先" in skill
    assert "正面界定范围" in prose
    assert "Claim-forward" in prose
    assert "最终逻辑叙事" in prose
    assert "无必要免责" in prose and "真实方法局限" in prose
    assert "工作日志" in writing
    assert "不得隐藏" in prose
    for code in ["DEFENSIVE_PROSE_OVERUSE", "WORKLOG_NARRATIVE", "SYNTACTIC_AI_PATTERN"]:
        assert code in quality
        assert f'"{code}"' in validator

