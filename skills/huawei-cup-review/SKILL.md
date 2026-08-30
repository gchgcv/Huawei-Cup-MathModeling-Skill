---
name: huawei-cup-review
description: This skill should be used when the user asks to "审核数学建模论文", "检查论文 AI 味", "检查 Claim-Evidence", "审查 LaTeX/PDF", or needs an evidence-backed, read-only review of a Huawei Cup mathematical-modeling manuscript.
---

# Huawei Cup Review

## Goal

以只读方式检查数学建模论文，并返回可定位、可复核的 structured findings。审核调用成功不代表论文质量合格。

## Hard Boundary

- `read_only` 必须为 `true`，`writes_performed` 必须为 `[]`。
- 不修改论文、代码、模型、结果、ledger、figure manifest、workflow 或 submission state。
- 不自动调用 Writer，不生成补丁，不保存 review report。
- 不为了凑数制造 finding；未发现有证据支持的问题时返回 `findings: []`。
- Shared Paper Quality Standard 缺失或 Rule ID 无法解析时 fail closed。

## Default Workflow

1. 识别待审 artifact、审核范围和可用证据；缺失内容写入顶层 `limitations`。
2. 按需读取 `../../shared/paper-quality-standard/README.md` 及相关标准文件；若提供 Project Facts，按 `references/project-facts-review.md` 只读校验。
3. 先运行适用的只读 deterministic checks，再进行 semantic review。
4. 对候选问题定位 artifact、位置和理由；无 evidence 的候选不得进入正式 findings。
5. 按 `references/severity-and-evidence-policy.md` 分配 P0/P1/P2，不产生论文通过状态。
6. 按 `schemas/review-result.schema.json` 返回结果对象，不持久化到磁盘。

## Review Lenses

- 学术表达、AI-like pattern、防御性表达：`references/semantic-review-policy.md`
- 论证深度、Claim-Evidence、摘要与章节连贯性：`references/semantic-review-policy.md`
- LaTeX、PDF、DOCX 和图表引用：`references/deterministic-checks.md`
- 文档级检查与证据边界：`references/document-quality-review.md`

## Bundled Resources

- `schemas/review-request.schema.json`：只读审核输入契约。
- `schemas/review-result.schema.json`：v2 结果 envelope，finding 结构引用 Shared Contract。
- `../../shared/contracts/`：Project Facts、artifact 和 finding 的共享结构。
- `scripts/validate_review_result.py`：schema 与 Shared Rule ID 校验。
- `scripts/lint_paper_style.py`：保守的文本风格风险检测。
- `scripts/audit_latex_build.py`：LaTeX 主源与日志检查。
- `scripts/validate_latex_review.py`：当前 PDF 与视觉审核记录一致性检查。
- `scripts/verify_docx_math.py`：DOCX 公式结构检查。
- `scripts/audit_figure_references.py`：LaTeX 图形文件、caption、label 与引用检查。
