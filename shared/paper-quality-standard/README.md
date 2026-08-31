# Shared Paper Quality Standard

Version: `1.0` (Suite `1.0.0-rc1`).

## Purpose

本目录是数学建模论文质量要求的唯一规范源，只回答“合格论文应满足什么条件”。它不规定生成步骤、检查步骤、严重度、文件修改权限、运行时行为或提交状态。

## Rule Format

每条规则包含：

- 稳定 Rule ID；
- Normative Statement；
- Scope；
- Required Exceptions；
- Relations。

Rule ID 一旦进入测试或 Benchmark，不得在没有兼容映射的情况下重命名。

## Registry

| Prefix | File | Scope |
|---|---|---|
| `PROSE` | `academic-prose.md` | 中文学术表达与句子可读性 |
| `AI` | `anti-ai-style.md` | 可观察的机械化语言风险 |
| `ADW` | `anti-defensive-writing.md` | 防御性表达、范围和不确定性 |
| `DEPTH` | `argument-depth.md` | 建模说明与结果讨论深度 |
| `CLAIM` | `claim-evidence.md` | 主张、证据和外推边界 |
| `ABS` | `abstract-standard.md` | 摘要内容与证据要求 |
| `STRUCT` | `section-structure.md` | 章节组织与问题驱动结构 |
| `FIG` | `figure-table-standard.md` | 图表信息、可读性与一致性 |
| `FMT` | `academic-format.md` | 文档格式与可编辑源边界 |
| `NUM` | `number-unit-precision.md` | 数字、单位和报告精度 |
| `TERM` | `terminology.md` | 术语、符号和名称保护 |
| `REF` | `reference-standard.md` | 引用真实性、相关性与格式 |

## Provenance

Rule ID 和基础规范从冻结的 `legacy/huawei-cup-modeling-writing-v0.9.1` 中已有要求提取。当前工作树可以根据用户提供的写作审核建议，对既有 Rule 的语义进行兼容性增补；这类增补不创建新的 Rule ID 命名空间，需在发布记录中保留其来源。历史文件继续作为回归基线，本目录不反向修改 Legacy。
