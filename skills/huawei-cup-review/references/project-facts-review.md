# Project Facts Review

Review 只读消费 `../../shared/contracts/project-facts.schema.json`，不更新 Project Facts 或 Legacy ledger。

## Admission

- 先运行共享 validator；无效或 `NEEDS_MANUAL_MAPPING` 的输入只能产生 limitation，不能作为确定事实依据。
- `sources` 提供 artifact 与 locator；审核 evidence 应优先复用这些定位信息。
- `VERIFIED` 表示存在契约内证据引用，不表示 Reviewer 已独立证明事实正确。
- `UNVERIFIED` 和 `MISSING` 不能被当作反例或已证实缺陷；需要结合论文实际主张形成 finding。

## Comparison

- 论文 claim 与 `claims`、`results`、`model`、`figures` 不一致时，finding 同时定位论文和 Project Facts source。
- `evidence_ids` 悬空、source 不可解析或关键数字冲突属于契约/一致性问题，但 Review 仍保持只读。
- Project Facts 未覆盖的检查范围写入顶层 `limitations`，不猜 canonical value。
