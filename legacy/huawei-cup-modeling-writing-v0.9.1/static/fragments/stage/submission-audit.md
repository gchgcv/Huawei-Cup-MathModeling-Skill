# 阶段：submission-audit

## 输入要求

完整或接近完整的论文，以及当前可用的问题台账、数据、代码、结果文件、图表和参考文献。缺少材料必须登记为 `UNVERIFIED`。

## 执行步骤

0. 核对唯一主编辑源、模板来源和最终 PDF。若仍使用 `skill_fallback`、上一届未核验模板或来源不明模板，禁止 READY_TO_SUBMIT。
1. 先检查工作流状态。凡支撑最终结论的继承阶段仍为 `INHERITED_UNVERIFIED`、`NEEDS_REVIEW` 或 `BLOCKED`，不得直接进入提交判定。
2. 若主稿为 LaTeX，按 `references/latex-pdf-layout-audit.md` 完成候选终稿的日志与最终 PDF 版面审核。
3. 按 `references/result-visualization.md` 核对正式图文件的视觉检查证据；核心代码图若从未被实际打开/渲染检查，登记 `FIGURE_VISUAL_UNVERIFIED`。
4. 按 `references/reference-management.md` 审核参考文献；正式论文无有效参考文献时登记 `REFERENCE_MISSING`，旧题训练违反来源边界时登记 `REFERENCE_POLICY_VIOLATION`。
5. 检查模型假设是否符合“总述—分条—适用范围”结构，空间几何符号是否有示意图和正文解释；缺失时登记 `MODEL_ASSUMPTION_STRUCTURE_THIN` 或 `SYMBOL_GEOMETRY_UNEXPLAINED`。
6. 检查单位、有效数字和报告精度是否匹配题目数据与工程情境；区分求解器容差/残差精度和物理结果报告精度，必要时登记 `UNIT_PRESENTATION_ERROR` 或 `REPORT_PRECISION_MISMATCH`。
7. 检查多子图默认不超过两列、复杂图是否拆分、最终 PDF 实际尺寸是否可读；检查表格单位是否位于物理量列或表头。
8. 检查伪图、主模型论证完整度和核心图表讨论，分别按现有问题代码登记。
9. 按 `static/core/quality-gates.md` 依次检查 P0 和八项硬门控。
10. 每个 `PASS` 记录具体证据；没有证据不得判定通过。
11. 按 P0/P1/P2 登记问题和修复动作。
12. 审核正文时执行 `references/paper-prose-style.md`；减少高密度元话语和模板化自我评价，但不能据此断定作者是否使用 AI；可运行 `scripts/lint_paper_style.py` 辅助筛查，必须人工判断技术场景和专业术语。
13. 硬门控检查完成后再做内部 100 分诊断。
14. 生成质量报告，并优先连同建模台账执行 `python scripts/validate_quality_report.py quality-report.json --ledger modeling-ledger.json --strict`，让提交状态同时受工作流继承状态约束。

## 阶段产物

提交状态、八项门控及证据、P0/P1/P2 清单、诊断评分、PDF 版面审核记录和修复动作。

## 通过条件

全部必需门控为 `PASS` 或确实 `NOT_APPLICABLE`，无未解决 P0/P1，无未标记占位符，建模解释和结果讨论达到可复核程度，正文语言和专业术语完成复核；LaTeX 最终 PDF 已完成日志检查和全页视觉审查，才可输出 `READY_TO_SUBMIT`。

## 禁止行为

先给总分再补证据；用高分掩盖 P0；看不到代码或数据时判定结果正确；把排版整齐当作模型正确；只看到 LaTeX 编译成功就跳过最终 PDF 审查；把“未发现问题”写成“已证明正确”；按词表机械替换专业术语。
