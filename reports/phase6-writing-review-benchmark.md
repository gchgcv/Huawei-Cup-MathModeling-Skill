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
- `benchmark/runs/2026-08-30-writing-repair3/`
- `reports/phase6-writing-review-benchmark.md`

## Ownership Changes

- Benchmark 只负责测量显式 case contract 与候选输出，不定义论文质量规范。
- Writing、Review 和 Legacy runtime 均未获得新的 benchmark 写入或状态权限。
- Shared Paper Quality Standard 继续提供唯一 Rule ID；evaluator 只读取。
- 真实 Writer/Reviewer 输出由被测系统产生，Benchmark 不代写候选内容。

## Contracts

### Writing

六类 Legacy A/B case：防御性、AI 工作日志、浅结果讨论、高质量 clean case、专业术语、必要局限与负面证据。

指标覆盖：deterministic fidelity、关键数字、公式、citation、label/ref、防御性减少、工作日志减少、AI 机械句法减少、controlled semantic assertions、论述深度、术语、必要局限、负面证据、未声明新增数字和 invented result count。关键事实变化进入 hard errors；语义断言单独计数并保留独立裁决。

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
17 passed

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

135 passed, 12 subtests passed
```

默认 pytest import mode 会因 Review 保留的 Legacy 同名测试副本产生 module-name collection conflict；使用 `--import-mode=importlib` 后全量通过。分目录运行同样通过。

Verification summary：

```text
Build:     N/A (no package build configuration)
Types:     N/A (no configured project type checker)
Lint:      PASS
Compile:   PASS
Tests:     PASS (135 + 12 subtests)
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

## Writing Repair3 Rerun

针对首轮失败，Writing 新增 fidelity lock、受保护 token 占位符策略、派生数字授权边界和 mandatory mutation validation gate。Benchmark 同时拆分 deterministic fidelity 与 controlled semantic assertions，不再把等义限定语改写直接当成事实层错误。

repair3 运行目录：`benchmark/runs/2026-08-30-writing-repair3/`。

- Writing A/B：`EXECUTED`，admission=`PASS`。
- Modular Writing：6/6 cases pass，hard errors=0，semantic failures=0，fact/number/formula/citation/label-ref/term/limitation/negative-evidence rates 均为 1.0，invented result count=0。
- Legacy：4/6 cases pass，hard errors=5，semantic failures=2，仍存在 reference anchor 和未声明派生数字问题。
- 独立裁决：确认完整 `\ref{fig:result}`、`\ref{fig:trend}` 已恢复，没有新增或删除数字；浅结果讨论同时保留结果意义和机制证据缺口。
- repair3 Integration：5/5 envelope cases pass，hash、只读性、Shared Rule ID 和 handoff 均通过。
- Review：沿用同一 Phase 6 Review 版本的 13/13 synthetic pass；未把该结果扩展为真实长论文能力声明。

总控最终返回 `status=EXECUTED`、`admission=PASS`。机器可读摘要和独立裁决位于 repair3 运行目录。

## Known Limitations

- Review PASS 仅覆盖 13 个短句 synthetic cases，不证明真实长论文、跨章节一致性、citation 真实性或 source truth 审查能力。
- Integration PASS 仅证明 envelope、hash、只读与 handoff；Review 未看到改写前原文，无法发现 source-relative 锚点或数值变化。
- `findings_allowed` 是弱断言，不要求实际检出 finding。
- exact phrase 与固定词面指标会误伤等义改写，下一轮需区分 deterministic fidelity 与 semantic adjudication。
- controlled semantic assertions 仍基于短语包含，可能受否定语境、词表外同义改写和术语误用影响；独立 adjudication 仍是必需层。
- mutation validator 的 multiset 一致不能证明数字与对象的绑定关系完全未交换，也没有覆盖所有 citation/ref command option 变化。
- Legacy sample PDF 尚未进入真实 A/B。

## Risks

- 若把 catalog validation 或 evaluator unit pass 写成“新架构优于 Legacy”，会形成错误结论。
- 自动把 catalog 外 finding 计为 unsupported 只适用于受控 synthetic fixture；真实论文需要独立 adjudication。
- result directory 若缺生成方式、被测版本和来源记录，不能作为可复现 benchmark 证据。

## Gate Decision

PASS（仅限已声明的 synthetic 与 integration envelope cases）。

首轮总控确实返回 FAIL；repair3 修复并重新生成真实 Writer 输出、重新进行独立 adjudication 与 Integration 后，总控返回 `status=EXECUTED`、`admission=PASS`。该 PASS 只说明当前六个 Writing cases、十三个 Review cases 与五个 Integration envelopes 达标，不代表真实论文或投稿质量通过。

## Next Allowed Phase

允许进入 Phase 7 的 `DEPRECATE` 步骤：把旧主 Skill 标记为 `Legacy Coordinator / Compatibility Baseline`，保留兼容入口，不删除文件。

计划要求“真实任务验证后才允许删除 Legacy 重复文件”。当前只有 synthetic/envelope evidence，因此 Phase 7 只能做兼容标记与职责收缩，不能执行 `REMOVE`。
