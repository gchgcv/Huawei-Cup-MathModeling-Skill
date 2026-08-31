# Deterministic Check Routing

所有 bundled scripts 都是只读检查器，只向 stdout/stderr 返回观察结果和退出码。它们不生成补丁，不保存审核报告。

| Need | Script | Interpretation |
|---|---|---|
| 中文正文风格风险 | `scripts/lint_paper_style.py` | 命中是人工复核候选，不自动成为 finding |
| LaTeX 主源、递归 include 与日志 | `scripts/audit_latex_build.py` | error/warning 需结合 `FMT-003`、`FMT-004` 定位 |
| PDF 视觉审核记录是否属于当前 PDF | `scripts/validate_latex_review.py` | 页数读取优先使用 `PyMuPDF`，`pdfinfo` 作为独立回退；stale hash 或页数范围错误可形成文档 finding |
| DOCX 公式结构 | `scripts/verify_docx_math.py` | 只检查结构证据，不改公式 |
| LaTeX 图形引用关系 | `scripts/audit_figure_references.py` | 解析递归 TeX 源及 `\\graphicspath`，检查文件、caption、label 与正文引用 |
| canonical 图产物集合 | `scripts/audit_canonical_figure_outputs.py` | 只读核对 manifest、缺失、unexpected 和引用关系；不移动或删除 |
| Review v2 结果 | `scripts/validate_review_result.py` | 同时校验 schema 和 Shared Rule ID |

脚本发现的问题仍需按 `references/severity-and-evidence-policy.md` 转换；原始 stdout 不能替代定位证据。未提供相应 artifact 时跳过，不猜测检查结果。

PDF 工具归位：最终版面视觉检查固定使用 `pdftoppm` 渲染后的页面；除视觉检查外的 PDF 程序化读取默认使用 `PyMuPDF`（`fitz`）。`pypdf` 和 `pdfplumber` 仅作为特定兼容性或表格结构诊断的回退工具，不作为默认路径。
