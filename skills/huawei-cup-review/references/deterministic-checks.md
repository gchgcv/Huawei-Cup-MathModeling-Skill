# Deterministic Check Routing

所有 bundled scripts 都是只读检查器，只向 stdout/stderr 返回观察结果和退出码。它们不生成补丁，不保存审核报告。

| Need | Script | Interpretation |
|---|---|---|
| 中文正文风格风险 | `scripts/lint_paper_style.py` | 命中是人工复核候选，不自动成为 finding |
| LaTeX 主源、递归 include 与日志 | `scripts/audit_latex_build.py` | error/warning 需结合 `FMT-003`、`FMT-004` 定位 |
| PDF 视觉审核记录是否属于当前 PDF | `scripts/validate_latex_review.py` | stale hash 或页数范围错误可形成文档 finding |
| DOCX 公式结构 | `scripts/verify_docx_math.py` | 只检查结构证据，不改公式 |
| LaTeX 图形引用关系 | `scripts/audit_figure_references.py` | 检查文件、caption、label 与正文引用 |
| Review v2 结果 | `scripts/validate_review_result.py` | 同时校验 schema 和 Shared Rule ID |

脚本发现的问题仍需按 `references/severity-and-evidence-policy.md` 转换；原始 stdout 不能替代定位证据。未提供相应 artifact 时跳过，不猜测检查结果。
