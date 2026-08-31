# Project Facts Consumption

Writing 只读消费 `../../shared/contracts/project-facts.schema.json`，不得创建、补写或回写 Project Facts。

## Use

- 先运行共享 validator；存在 schema、ID 或引用错误时停止事实性写作并报告缺口。
- 题意只来自 `problem.questions`，模型表述只来自 `model`，结果数字只来自 `results`。
- claim 必须使用其 `evidence_ids` 所指向的证据；`UNVERIFIED` 或 `MISSING` 内容不能被改写成确定事实。
- 图表和 citation 只能使用对应实体与 `sources` 中可追溯的位置。
- `limitations` 必须作为输入边界保留，不得通过顺畅措辞掩盖。

## Context, linkage, and provenance

- 模型段落涉及关键参数时，应从 `model.parameters` 读取其 `value`、`unit`、`source_ids` 和 `evidence_status`，并结合 `meaning` 判断其在目标函数、约束或结果解释中的作用；缺少来源或证据状态不是可凭经验补齐的空白。
- 只有在事实集能够指向前一问题的结果、后一问题的输入或明确的模型关系时，才能写出跨问题承接。题目编号相邻、章节连续或作者口头说明不构成事实证据。
- 模型链中的模块责任若未在事实集、代码映射或模型证据中明确，不得自行补写模块的选择理由、输入输出或替代效果；可以保留模块名称，同时登记责任说明的证据缺口。
- 结果进入摘要、结论或图表前，应沿结果来源、正文、图表、摘要和结论逐项核对模型名称、指标定义、单位、排序、关键数字和结论强度；冲突应进入 `unresolved_evidence_gaps`，不能由 Writing 选定一个口径覆盖其他材料。
- 事实集中的 `limitations`、`UNVERIFIED` 和 `MISSING` 状态必须影响写作强度：可以据此提出核验需求或有界推断，不能生成确定的评价、推广或改进效果。

## Computed-result boundary

本文件约束的是 Writing 对 Project Facts 的只读消费，不是对建模和结果分析的全局禁令。若任务处于 `evidence-backed-analysis` 或 `modeling-or-computation` 模式，Agent 可以依据可追溯数据、模型或程序输出计算新结果；但这些结果在完成独立核验并形成新的结果证据前，不得冒充 Project Facts 中已经存在的 `VERIFIED` 结果，也不得静默回写事实集。

## Missing facts

缺失的模型名、公式、结果、单位、引用或 source locator 应进入 `unresolved_evidence_gaps`。Writing 可以写占位建议或提出补充需求，但不能猜值、补实验或替用户更新事实契约。
