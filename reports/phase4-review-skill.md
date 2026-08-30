# Phase 4 Report

## Scope

本阶段仅从冻结的 Legacy 与现有 External Reviewer Contract 思想中提取独立的 `huawei-cup-review`。未修改 Legacy、Writing、Shared Standard、External Layer、workflow、ledger、submission state 或远程仓库。

## Files Changed

- `skills/huawei-cup-review/SKILL.md`
- `skills/huawei-cup-review/manifest.yaml`
- `skills/huawei-cup-review/agents/openai.yaml`
- `skills/huawei-cup-review/references/*.md`（4 个）
- `skills/huawei-cup-review/schemas/*.json`（2 个）
- `skills/huawei-cup-review/scripts/*.py`（6 个）
- `skills/huawei-cup-review/tests/*.py`（4 个）
- `skills/huawei-cup-review/tests/review-cases.yaml`
- `reports/phase4-review-skill.md`

## Ownership Changes

- Review 接管只读的论文诊断、finding admission、evidence policy 和 P0/P1/P2 severity。
- Legacy 的 style lint、LaTeX build audit、PDF review evidence validation 与 DOCX math verification 以只读副本进入 Review；Legacy 原文件保持不变。
- 原 Legacy figure auditor 的 mutation 路径未迁入；Review 新增纯只读的 LaTeX figure-reference auditor。
- Shared 继续作为论文规范的唯一 authoritative source；Review 只引用 Rule ID。
- Legacy Coordinator 继续独占 workflow、ledger 和 submission state。

## Contracts

- 新增 `review-request.schema.json` v2，强制 read-only policy、禁止 artifact write 与 automatic repair。
- 新增 `review-result.schema.json` v2：`read_only=true`、`writes_performed=[]`，允许 `findings=[]`。
- 每个正式 finding 必须包含唯一 ID、Shared Rule ID、severity、category、claim、location、至少一条可定位 evidence、recommendation、confidence 和 limitations。
- `call_status` 仅表示 Contract 调用结果；固定 `status_meaning=CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY`。
- `validate_review_result.py` 对 schema、Shared Rule ID 和 finding ID 唯一性执行 fail-closed 校验；无持久化操作。
- External Reviewer Contract v1 未覆盖或修改；本 Skill 不依赖未 admission 的 provider。

## Tests

```text
D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m pytest skills\huawei-cup-review\tests -q
29 passed

D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m ruff check skills\huawei-cup-review\scripts skills\huawei-cup-review\tests
All checks passed
```

Review tests覆盖：stable identity、真实路径、只读 request/result、空 findings、有 evidence finding、缺 evidence 拒绝、未知 Rule ID 拒绝、重复 finding ID 拒绝、禁止第二套质量状态、fail-closed normalization、Shared 文本不复制、无 Legacy/External runtime 依赖、无 mutation action、figure audit 零修改，以及六类 fault/resistance case catalog。

## Regression

```text
pytest tests\test_shared_paper_quality_standard.py -q
7 passed

pytest skills\huawei-cup-writing\tests -q
13 passed

pytest legacy\huawei-cup-modeling-writing-v0.9.1\tests -q
49 passed, 12 subtests passed
```

## Known Limitations

- `review-cases.yaml` 是 Phase 6 前的 specification-only catalog，尚未对真实论文或 Agent 输出执行 benchmark。
- 本阶段不连接 External Reviewer Provider。
- 跨 artifact canonical facts 与 figure manifest schema 等待 Phase 5 Shared Contracts；当前 figure checker 只审核 LaTeX 引用关系。
- deterministic checker 的 stdout 是候选观察，仍需 semantic review 转换为正式 evidence-backed finding。

## Risks

- 仅有 deterministic pass 不证明论文质量合格。
- 未提供当前 PDF、引用原文或事实 artifact 时，相应结论必须降级为 limitation。
- Legacy 与新模块在 Phase 7 compatibility closeout 前仍会并存；不得提前删除旧资产。

## Gate Decision

PASS。此处 PASS 仅表示 Phase 4 Contract、专项测试和相关回归通过，不表示任何论文达到比赛或投稿要求。

## Next Allowed Phase

Phase 5：Shared Project Facts / Artifact Contract 最小化。进入前等待用户批准。
