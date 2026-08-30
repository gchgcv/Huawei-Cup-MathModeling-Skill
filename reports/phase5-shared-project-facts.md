# Phase 5 Report

## Scope

本阶段只建立最小 Shared Project Facts / Artifact Contract、只读 validator、Legacy ledger 保守映射，以及 Writing/Review 的只读消费接口。未替换或修改 Legacy ledger，未创建新 workflow、submission state 或 Provider。

## Files Changed

- `shared/contracts/README.md`
- `shared/contracts/paper-artifact-contract.md`
- `shared/contracts/project-facts.schema.json`
- `shared/contracts/review-finding.schema.json`
- `shared/contracts/validate_project_facts.py`
- `shared/contracts/adapters/legacy_ledger.py`
- `skills/huawei-cup-writing/{SKILL.md,manifest.yaml}`
- `skills/huawei-cup-writing/references/project-facts-consumption.md`
- `skills/huawei-cup-writing/tests/test_writing_skill_contract.py`
- `skills/huawei-cup-review/{SKILL.md,manifest.yaml}`
- `skills/huawei-cup-review/references/project-facts-review.md`
- `skills/huawei-cup-review/schemas/{review-request.schema.json,review-result.schema.json}`
- `skills/huawei-cup-review/scripts/validate_review_result.py`
- `skills/huawei-cup-review/tests/test_review_skill_contract.py`
- `tests/test_shared_project_facts.py`
- `reports/phase5-shared-project-facts.md`

## Ownership Changes

- Shared Contracts 成为 Project Facts、artifact reference 和 review finding 结构的唯一规范源。
- Writing 与 Review 均声明 `shared_contracts.access=read_only`，不创建、补写或回写 Project Facts。
- Review 的 v2 result envelope 改为引用 Shared finding schema；severity 语义仍由 Review policy 独占。
- Legacy Coordinator 保留原 modeling ledger、workflow 和状态所有权；adapter 只读映射，不覆盖源文件。

## Contracts

### Project Facts v1

包含稳定且可追溯的：

- `sources`
- `problem.questions`
- `model.name/assumptions/equations/parameters`
- `results`
- `claims`
- `figures`
- `citations`
- `limitations`

所有事实通过稳定 ID 与 source locator 关联。`VERIFIED`、`UNVERIFIED`、`MISSING` 是 evidence status，不是 workflow 或 submission status。

### Artifact boundary

Paper Artifact Contract 定义 `artifact_id`、kind、path、authority 与可选 sha256。路径存在不代表 freshness；hash 不匹配或多 authoritative 声明必须暴露，不能自动猜选。

### Legacy mapping

adapter 将可确定的 questions、单一 model name、parameters、results 与 claims 映射到 Project Facts。多模型、缺 ID、缺 task、缺 source、未知 status 或 schema/reference 错误统一返回 `NEEDS_MANUAL_MAPPING`。

## Tests

```text
pytest tests\test_shared_project_facts.py -q
15 passed

pytest skills\huawei-cup-writing\tests -q
14 passed

pytest skills\huawei-cup-review\tests -q
30 passed

ruff check shared\contracts tests\test_shared_project_facts.py skills\huawei-cup-writing skills\huawei-cup-review
All checks passed
```

专项覆盖 schema 合法性、source/evidence 悬空引用、全局重复 ID、verified claim evidence、禁止 workflow/submission state、Shared 非 Skill、finding evidence、确定性无副作用映射、多模型歧义、缺 traceability、未知 result status 不猜测、Writing/Review 同源只读消费和 Legacy 模板保留。

只读 smoke test：对空白 Legacy JSON 模板运行 adapter，按预期返回 exit 1 与 `NEEDS_MANUAL_MAPPING`；运行前后模板 SHA-256 一致。

## Regression

```text
pytest tests\test_shared_paper_quality_standard.py -q
7 passed

pytest legacy\huawei-cup-modeling-writing-v0.9.1\tests -q
49 passed, 12 subtests passed
```

## Known Limitations

- Project Facts v1 是最小跨模块事实投影，不替代完整 Legacy ledger。
- Legacy 当前没有正式定义 assumptions、equations、figures 和 citations 的统一字段，adapter 不猜这些内容。
- Legacy results 的 status 缺失时只保守映射为 `UNVERIFIED`；缺少 id/question_id/value/source 时要求人工映射。
- 尚未通过 Phase 6 benchmark 检验真实 Writing→Review 交接质量。

## Risks

- source locator 存在不等于源内容真实或最新；需要 artifact hash 或一手材料核验。
- `VERIFIED` 仅表示契约内证据引用完整，不表示独立学术验证完成。
- 模块并存期间不得让 Project Facts 与 Legacy ledger 分别成为两套可写事实源。

## Gate Decision

PASS。Writing 不获得事实写权，Review 可依据同一事实契约审查 claim，source 可追溯，Legacy ledger 保持可用且未变化。

本 PASS 只表示 Phase 5 Contract 与回归通过，不表示论文质量、比赛结果或投稿状态通过。

## Next Allowed Phase

Phase 6：Writing / Review Benchmark。进入前等待用户批准。
