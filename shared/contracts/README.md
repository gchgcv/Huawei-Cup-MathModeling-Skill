# Shared Contracts

Contract versions in Suite `1.0.0-rc1`: Project Facts `1`, Review Finding `1`,
Paper Artifact `1`, and Figure Manifest `1`. Review's call-result envelope remains
component-owned v2.

本目录定义 Writing、Review 与后续建模/编码能力之间共享的数据形状，不是可调用 Skill，也不拥有 workflow、severity policy 或 submission state。

## Contract inventory

- `paper-artifact-contract.md`：artifact 身份、权威性和可追溯性边界。
- `figure-manifest.json`：canonical 正式图产物集合的结构定义；产出层维护，Writing 与 Review 只读使用。
- `project-facts.schema.json`：最小 Project Facts v1 schema。
- `review-finding.schema.json`：Review finding 的共享结构；P0/P1/P2 的解释仍由 Review policy 定义。
- `validate_project_facts.py`：只读 schema、ID 和引用完整性校验器。
- `adapters/legacy_ledger.py`：Legacy modeling ledger 的保守只读映射器。

## Ownership

| Consumer/producer | Access in the first wave |
|---|---|
| Future Analysis/Modeling | later owner of `problem` and `model` writes |
| Future Coding/Visual | later owner of verified `results` and `figures` writes |
| Huawei Cup Writing | read only |
| Huawei Cup Review | read only |
| Legacy Coordinator | retains the original ledger and workflow state |

Project Facts 不是新 ledger，不记录阶段、路由或投稿状态。映射失败时必须返回 `NEEDS_MANUAL_MAPPING`，不能补猜缺失事实。
