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
- `benchmark/runs/2026-08-30-independent-agent-ab/`
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
14 passed

ruff check benchmark
All checks passed

python -m compileall -q benchmark
PASS
```

专项测试覆盖 catalog/Rule ID、六类 A/B、缺输出 NOT_RUN、raw Agent bundle 读取、Writer 正常改写、数字篡改、局限删除、Review valid finding、clean empty findings、false positive、unsupported/duplicate finding、指标聚合、integration 零修改、handoff 完整性、evaluator 无写操作和输入对象不变。

## Regression

```text
pytest --import-mode=importlib \
  benchmark\tests \
  tests\test_shared_project_facts.py \
  tests\test_shared_paper_quality_standard.py \
  skills\huawei-cup-writing\tests \
  skills\huawei-cup-review\tests \
  legacy\huawei-cup-modeling-writing-v0.9.1\tests -q

129 passed, 12 subtests passed
```

默认 pytest import mode 会因 Review 保留的 Legacy 同名测试副本产生 module-name collection conflict；使用 `--import-mode=importlib` 后全量通过。分目录运行同样通过。

Verification summary：

```text
Build:     N/A (no package build configuration)
Types:     N/A (no configured project type checker)
Lint:      PASS
Compile:   PASS
Tests:     PASS (129 + 12 subtests)
Security:  PASS (no token/api-key/password/eval/exec pattern match in benchmark)
```

## Actual Independent Agent Run

运行目录：`benchmark/runs/2026-08-30-independent-agent-ab/`。Legacy Writing、Modular Writing、Modular Review、Writing→Review Integration 和独立裁决分别由隔离任务生成；生成任务禁止读取 benchmark 预期且禁止写仓库。

- Writing A/B：`EXECUTED`，自动 admission=`FAIL`。Legacy 3/6 cases pass、6 个 hard errors；Modular 2/6 cases pass、8 个 hard errors。
- Review：`EXECUTED`，13/13 synthetic cases pass；seeded fault recall=1.0、false positive=0、mutation=0。
- Integration：`EXECUTED`，5/5 envelope cases pass；Review immutability、Shared Rule ID consistency、finding handoff coverage 均为 1.0。
- Independent adjudication：确认 Writing Gate 应失败；确认 label/ref 锚点缩短为真实硬错误。新增 0.17/1.7 在当前保守 contract 下是硬错误，但一般论文写作中属于可复算派生量，不应直接视为事实错误。
- Independent adjudication 同时确认两项 exact-phrase 误计：`不外推到/至未观测地区` 与 `能耗指标上/其能耗指标不占优` 语义均被保留，不能称为必要局限或负面证据丢失。

机器可读摘要见 `benchmark/runs/2026-08-30-independent-agent-ab/evaluation-summary.json`，完整裁决见同目录 `adjudication.json`。

## Known Limitations

- Review PASS 仅覆盖 13 个短句 synthetic cases，不证明真实长论文、跨章节一致性、citation 真实性或 source truth 审查能力。
- Integration PASS 仅证明 envelope、hash、只读与 handoff；Review 未看到改写前原文，无法发现 source-relative 锚点或数值变化。
- `findings_allowed` 是弱断言，不要求实际检出 finding。
- exact phrase 与固定词面指标会误伤等义改写，下一轮需区分 deterministic fidelity 与 semantic adjudication。
- Legacy sample PDF 尚未进入真实 A/B。

## Risks

- 若把 catalog validation 或 evaluator unit pass 写成“新架构优于 Legacy”，会形成错误结论。
- 自动把 catalog 外 finding 计为 unsupported 只适用于受控 synthetic fixture；真实论文需要独立 adjudication。
- result directory 若缺生成方式、被测版本和来源记录，不能作为可复现 benchmark 证据。

## Gate Decision

FAIL。

总控已实际执行并返回 `status=EXECUTED`、`admission=FAIL`。Review synthetic 与 Integration envelope 均通过，但 Writing A/B 存在不可接受的 protected LaTeX reference anchor 变化；按当前 case contract 还存在新增派生数字。独立裁决排除了两项语义误判后，仍不足以改变 Gate 结论。

## Next Allowed Phase

仍为 Phase 6：修复 Writing fidelity（尤其完整保留 LaTeX label/ref），并把 exact-string fidelity 与 semantic preservation 分层评估后重新运行独立 A/B。

在总控返回 `EXECUTED` 且 `admission=PASS` 前，不允许进入 Phase 7 Legacy 收口。
