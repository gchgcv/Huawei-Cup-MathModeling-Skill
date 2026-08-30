# 阶段：paper-writing

## 输入要求

问题台账，以及当前可用于写作的事实、模型、结果和图表。没有可靠结果时只能写方法与结构，不补造数值结论。

## 必读规则

- `references/document-editing.md`
- `references/paper-writing.md`
- `references/paper-prose-style.md`
- 完整论文或涉及引用时执行 `references/reference-management.md`
- 建模正文同时执行 `references/model-construction.md`
- LaTeX 候选终稿同时执行 `references/latex-pdf-layout-audit.md`

## 执行步骤

1. 先确定唯一主编辑源、模板来源和最终输出格式；已有主稿时直接继承，不另造模板。
2. 按子问题和逻辑依赖组织正文，只使用当前有效事实、模型和结果。
3. 建模部分写到足以复核模型选择、变量关系、关键公式/约束、参数来源和求解流程。
4. 核对假设、符号、单位、参数、图表与结论的一致性。
5. 对核心图表给出与其重要性相匹配的定量分析和模型解释。
6. 完整论文按 `reference-management.md` 整理和核验参考文献。
7. 按正文语言契约执行中文学术化、去防御性和句法去机械感审查：先分类限定语，再做 positive-scope、claim-forward 和最终逻辑重构；不删必要论证、不隐藏影响核心结论的负面证据、不改错专业术语。
8. 对关键结论登记 `claims` 及证据位置。
9. LaTeX 候选终稿按 `latex-pdf-layout-audit.md` 完成日志与最终 PDF 版面检查。
10. 完稿后进入 `submission-audit`。

## 阶段产物

论文正文、图表引用、参考文献、关键结论台账、必要的版面审核记录和待审核状态。

## 通过条件

逐问回答；关键数字可追溯；建模逻辑和核心结果讨论足以复核；正文不是工作日志式叙事；无成片防御性免责、犹豫词堆叠和机械长难句；图文一致；专业术语准确；参考文献满足 `reference-management.md`；无未标记占位符；满足指定模板要求；需要 LaTeX 终稿检查时已完成对应审核。

## 禁止行为

补写未做实验；机械追求页数；为追求简洁删掉建模依据和结果讨论；参考文献造假；把旧题现成答案包装成学术参考来源；为去 AI 味改错专业术语；审核前写 `READY_TO_SUBMIT`。
