# Severity and Evidence Policy

Severity 是 Review 的诊断优先级，不是 Shared Standard，也不是投稿状态。

## Severity

- `P0`：已定位的事实、数学或交付硬阻断，例如关键数字冲突、当前产物与声明版本不一致、不可编译错误。
- `P1`：需要验证或会显著削弱核心论证的问题，例如关键主张缺证据、结论越界、模型说明不可复核。
- `P2`：不改变核心事实但值得修正的表达、结构或格式问题。

Severity 依赖问题影响和证据，不由 Rule ID 固定映射。同一规则在不同上下文可有不同 severity。

## Formal finding admission

正式 finding 必须同时具备：

- 唯一 `finding_id`；
- Shared registry 中存在的 `rule_id`；
- P0/P1/P2 `severity`；
- 清楚陈述的问题 `claim`；
- 汇总定位 `location`；
- 至少一条包含 `artifact_id`、`locator` 和 `reason` 的 evidence；
- 不执行修改的 `recommendation`；
- `confidence` 与必要的 `limitations`。

证据不足的观察只能进入顶层 `limitations` 或留在工作过程，不得包装成 finding。无问题时返回空列表。

## Result semantics

`call_status` 只表示契约处理是否成功。`SUCCESS` 不等于论文通过、可投稿、已接收或不存在未审范围。Review 不创建任何二级质量状态。
