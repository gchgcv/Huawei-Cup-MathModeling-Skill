# Writing and Review Benchmark

本目录对 Writing、Review 与二者交接进行 API-free、read-only 评估。Benchmark 只测显式 case contract 和候选输出，不决定论文质量或 submission state。

## Status semantics

- `EXECUTED`：所需候选输出齐全，evaluator 已计算指标。
- `NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE`：catalog 已验证，但没有真实 Skill/Agent 输出。
- `INVALID_OUTPUT`：候选结果缺失字段或违反契约。

`NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE` 不能解释为 PASS、FAIL、无问题或模块优于 Legacy。

## Layout

- `writing/`：六类 Legacy A/B case、Writer 输出评估和硬错误检查。
- `review/`：seeded faults、resistance cases 和 evidence-backed finding 指标。
- `integration/`：Writing→Review 的 hash、只读性、Rule ID 与 handoff 检查。
- `tests/`：evaluator unit、fault 和 resistance tests。

## Candidate result ownership

Benchmark evaluator 不生成 Writer/Reviewer 内容。真实输出必须由被测系统独立产生，再以 JSON 放入调用方指定的 result directory。Evaluator 只读取 catalog/result，向 stdout 返回 JSON，不写 benchmark report。

每个 result directory 可以使用逐 case 的 `<case_id>.json`，也可以保存一个原始 `bundle.json`：

- Writing：`case_id`、`system_under_test`（`legacy-v0.9.1` 或以 `modular-writing` 开头的版本标识）、`output_text`；新版 Writing 可同时提供 `declared_derived_values` 与 `fidelity_validation`。
- Review：符合 `../skills/huawei-cup-review/schemas/review-result.schema.json` 的 v2 result，`task_id` 可使用 case ID。
- Integration：`case_id`、`writing_output_text`、`writing_rule_ids`、`review_input_sha256`、`review_output_sha256`、`review_result`、`next_writer_handoff.finding_ids` 和 `next_writer_handoff.understood_rule_ids`。

四组真实结果齐全后运行：

```powershell
python benchmark/run_benchmark.py `
  --legacy-writing <legacy-writing-result-dir> `
  --modular-writing <modular-writing-result-dir> `
  --review-results <review-result-dir> `
  --integration-results <integration-result-dir>
```

result directory 是外部运行输入，不应提交为已执行证据，除非同时记录生成方式、被测 Skill 版本和独立 adjudication。

## Legacy A/B admission

只有 Legacy 和 Modular 两组真实输出均齐全，才能计算 A/B。Modular admission 至少要求：

- 无关键数字、公式、citation、label/ref 硬错误；
- 无未声明新增数字，Modular 自身 semantic failure count 为零；
- 术语、必要局限和核心负面证据保持率不低于 Legacy；
- Review mutation count 为零；
- false positive 不高于明确阈值；
- 所有正式 findings 有 evidence。

Writing evaluator 分开报告 deterministic fidelity 与 controlled semantic assertions。后者的 `any_phrases` 只是受控 fixture heuristic，必须结合独立 adjudication，不能解释为通用语义理解能力。
