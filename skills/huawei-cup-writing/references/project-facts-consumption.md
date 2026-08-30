# Project Facts Consumption

Writing 只读消费 `../../shared/contracts/project-facts.schema.json`，不得创建、补写或回写 Project Facts。

## Use

- 先运行共享 validator；存在 schema、ID 或引用错误时停止事实性写作并报告缺口。
- 题意只来自 `problem.questions`，模型表述只来自 `model`，结果数字只来自 `results`。
- claim 必须使用其 `evidence_ids` 所指向的证据；`UNVERIFIED` 或 `MISSING` 内容不能被改写成确定事实。
- 图表和 citation 只能使用对应实体与 `sources` 中可追溯的位置。
- `limitations` 必须作为输入边界保留，不得通过顺畅措辞掩盖。

## Missing facts

缺失的模型名、公式、结果、单位、引用或 source locator 应进入 `unresolved_evidence_gaps`。Writing 可以写占位建议或提出补充需求，但不能猜值、补实验或替用户更新事实契约。
