# Phase 6 Report

## Scope

本阶段建立 Writing、Review、Writing→Review integration 与 Legacy/Modular A/B 的 API-free、read-only benchmark。未调用或接入 External Provider，未伪造 Agent 输出，未修改 Skill runtime、Legacy、论文 artifact 或 submission state。

## Files Changed

- `benchmark/README.md`
- `benchmark/manifest.yaml`
- `benchmark/run_benchmark.py`
- `benchmark/writing/{cases.yaml,evaluate_writing.py}`
- `benchmark/review/{cases.yaml,evaluate_review.py}`
- `benchmark/integration/{cases.yaml,evaluate_integration.py}`
- `benchmark/tests/test_phase6_benchmark.py`
- `reports/phase6-writing-review-benchmark.md`

## Ownership Changes

- Benchmark 只负责测量显式 case contract 与候选输出，不定义论文质量规范。
- Writing、Review 和 Legacy runtime 均未获得新的 benchmark 写入或状态权限。
- Shared Paper Quality Standard 继续提供唯一 Rule ID；evaluator 只读取。
- 真实 Writer/Reviewer 输出由被测系统产生，Benchmark 不代写候选内容。

## Contracts

### Writing

六类 Legacy A/B case：防御性、AI 工作日志、浅结果讨论、高质量 clean case、专业术语、必要局限与负面证据。

指标覆盖：事实、关键数字、公式、citation、label/ref、防御性减少、工作日志减少、AI 机械句法减少、论述深度、术语、必要局限、负面证据和 invented result count。关键事实变化和 protected phrase 丢失进入 hard errors。

### Review

包含 9 个 seeded faults 与 4 个 resistance cases。指标覆盖 seeded fault recall、false positive/negative、unsupported finding、duplicate finding、evidence coverage、mutation count 和 clean-case empty-findings rate。

### Integration

检查 Writer 输出 hash、Review 前后 hash、`writes_performed=[]`、Shared Rule ID、finding ID/rule handoff 和 clean/resistance case 空 findings。

### Status

- `EXECUTED`：所需真实输出齐全并已评估。
- `NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE`：catalog/evaluator 可用，但没有真实被测输出。
- `INVALID_OUTPUT`：候选输出违反输入或结果契约。

`NOT_RUN` 不等于 PASS、FAIL、论文无问题或 Modular 优于 Legacy。

## Tests

```text
pytest benchmark\tests -q
13 passed

ruff check benchmark
All checks passed

python -m compileall -q benchmark
PASS
```

专项测试覆盖 catalog/Rule ID、六类 A/B、缺输出 NOT_RUN、Writer 正常改写、数字篡改、局限删除、Review valid finding、clean empty findings、false positive、unsupported/duplicate finding、指标聚合、integration 零修改、handoff 完整性、evaluator 无写操作和输入对象不变。

## Regression

```text
pytest --import-mode=importlib \
  benchmark\tests \
  tests\test_shared_project_facts.py \
  tests\test_shared_paper_quality_standard.py \
  skills\huawei-cup-writing\tests \
  skills\huawei-cup-review\tests \
  legacy\huawei-cup-modeling-writing-v0.9.1\tests -q

128 passed, 12 subtests passed
```

默认 pytest import mode 会因 Review 保留的 Legacy 同名测试副本产生 module-name collection conflict；使用 `--import-mode=importlib` 后全量通过。分目录运行同样通过。

Verification summary：

```text
Build:     N/A (no package build configuration)
Types:     N/A (no configured project type checker)
Lint:      PASS
Compile:   PASS
Tests:     PASS (128 + 12 subtests)
Security:  PASS (no token/api-key/password/eval/exec pattern match in benchmark)
```

## Known Limitations

- 总控 runner 当前返回 `NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE`，因为没有独立产生的 Legacy 与 Modular Writing、Review、Integration 真实输出目录。
- unit tests 执行的是 evaluator fault/resistance behavior，不是语言模型 Writing/Review 能力测试。
- catalog 使用显式 synthetic assertions，不能代替真实论文的人工 semantic adjudication。
- Legacy sample PDF 尚未用于真实 A/B；没有 Agent runner 时不得伪造对应输出。

## Risks

- 若把 catalog validation 或 evaluator unit pass 写成“新架构优于 Legacy”，会形成错误结论。
- 自动把 catalog 外 finding 计为 unsupported 只适用于受控 synthetic fixture；真实论文需要独立 adjudication。
- result directory 若缺生成方式、被测版本和来源记录，不能作为可复现 benchmark 证据。

## Gate Decision

BLOCKED。

Benchmark 基础设施、deterministic metrics、fault/resistance tests 和全量回归均通过；但 Phase 6 的能力验收要求真实 Legacy/Modular A/B 输出。当前总控状态为 `NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE`，因此不能证明事实错误、false positive、术语误伤或必要局限误删没有相对 Legacy 增加。

## Next Allowed Phase

仍为 Phase 6：为 catalog 中各 case 独立生成四组真实输出，并由独立 adjudication 核对后运行 `benchmark/run_benchmark.py`。

在总控返回 `EXECUTED` 且 `admission=PASS` 前，不允许进入 Phase 7 Legacy 收口。
