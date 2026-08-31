---
name: huawei-cup-writing
description: This skill should be used when the user asks to “写数学建模论文”, “润色华为杯论文”, “重写摘要”, “深化结果分析”, “去除 AI 味或防御性表达”, or revise an existing Chinese mathematical-modeling manuscript. It constructs or revises paper text from frozen, traceable problem, model, result, figure, and citation evidence; it does not redesign models, change computed facts, or make an independent final-acceptance decision.
---

# Huawei Cup Writing

## Goal

把已冻结、可核验的题意、模型、公式、结果、图表和引用证据转化为自然、准确、论证充分的中文数学建模论文。表达优化不得改变事实层和数学含义。

## Boundaries

可以：

- 生成或改写摘要、问题分析、模型说明、结果讨论、贡献和结论；
- 重构工作日志式叙事、无信息防御性表达和机械化句法；
- 在证据范围内补足解释、段落逻辑、caption 和图后分析；
- 在 `evidence-backed-analysis` 或 `modeling-or-computation` 模式下，基于用户提供且可核验的原始数据、结果表或计算记录生成派生结果，并保留其计算依据；
- 在用户明确指定主稿并授权写回后进行受控修改。

不可以：

- 重选模型、算法或求解器；
- 修改原始数据、程序结果、canonical value 或 figure manifest；
- 改变公式数学含义、关键数字、引用事实或真实方法边界；
- 发明未完成的实验、检验、敏感性、显著性或创新；
- 隐藏会改变核心结论的负面证据；
- 创建或修改 workflow、ledger、submission state；
- 把文本写完解释为论文已经独立验收通过。

## Default Workflow

1. 确认用户要求的章节、载体和交付方式；默认 `content-only`。交付模式只决定是否写回和显示哪些元数据，不决定数字是否可以计算。
2. 读取 `../../shared/paper-quality-standard/README.md`，再按任务加载相关 Rule 文件。
3. 若提供 Project Facts，先按 `references/project-facts-consumption.md` 只读校验并提取受保护事实；否则从用户材料建立本轮受保护事实集：数字、公式、模型含义、结果、citation key、label/ref、单位和适用边界。
4. 判定本轮 `evidence_mode`：冻结事实或纯改写使用 `frozen-rewrite`；已有数据、结果表并要求分析或计算时使用 `evidence-backed-analysis`；明确要求建模、求解或从输入生成结果时使用 `modeling-or-computation`。无法判断时按更保守的模式处理并报告证据缺口。
5. 处理数字时加载 `references/fidelity-and-derived-values.md`：先锁定完整 LaTeX token、显式数字绑定和原始数字，再只改写 token 之间的自然语言。`frozen-rewrite` 默认不得新增派生数字；另外两种模式可以在数据、公式、单位和计算记录均可追溯时报告派生结果。提供 Project Facts 时必须传给 mutation protector 做 canonical value 校验。
6. 选择满足请求的最小写作模式：`content-only`、`section-draft`、`micro-revision`、`revision` 或 `full-paper`。
7. 加载最少的 Writing reference，按 Shared Rule ID 建设文本；不得复制 Shared 规范正文形成第二定义。
8. 最终正文必须完成一次语体隔离：加载 `references/prose-blacklist.md`，将审核报告中的禁止性判断转为正向适用范围，将机械标签链改为真实的因果、递进或输入输出关系；不得以全局禁词替换，也不得删除必要的负面证据。
9. 改写后分两层检查：deterministic fidelity 检查 token、数字、公式和 citation；semantic preservation 检查主张范围、必要局限、负面证据和术语含义。只要存在改写前文本，必须运行 `scripts/validate_manuscript_mutation.py`；validator 未 PASS 时不得返回改写正文，必须修复并重跑。无法运行时保留原文并报告 `NOT_RUN`。
10. 只有用户明确授权写回时，才按 `references/controlled-document-editing.md` 修改唯一主稿；否则返回正文、patch 建议或 dry-run 结果。
11. 按用户要求返回正文、草稿或 patch。`fidelity_validation`、`declared_derived_values` 和未解决证据缺口属于验收元数据：在 `content-only` 与 `section-draft` 模式下默认内部保留，用户要求核验，或进入修订、授权写回模式时再展示。需要独立验收时，将当前产物交给单独的审核能力。

## Protected Layers

```text
事实层：数据 / 公式 / 模型 / 数字 / 图表 / 引用 / 已完成实验
→ 默认不可变

计算层：基于可追溯输入产生的派生指标或求解结果
→ 仅在相应 `evidence_mode` 获得授权，并登记计算依据

语义层：主张 / 因果 / 范围 / 证据关系
→ 只有证据支持时才能收缩或重组

表达层：句式 / 套话 / 防御性 / 冗余 / 机械感
→ 主要优化对象
```

若表达修改会扩大主张、掩盖真实局限、删除重要负面结果或改变专业含义，停止该修改并保留原科学边界。

## Resources

- `manifest.yaml`：任务路由、Shared Rule 文件和权限清单；
- `references/`：只定义“如何写”，不重新定义“什么是合格论文”；
- `references/prose-blacklist.md`：正文改写语料库、作用域例外和 Review→Writing 语体隔离；
- `references/reference-management.md`：参考文献核验、BibTeX/cite key 和顺序编码操作；
- `references/fidelity-and-derived-values.md`：改写现有文本时的 token 锁定、派生数字授权和证据不足处理；
- `../../shared/contracts/`：Project Facts、artifact 和跨模块结构的只读契约；
- `scripts/validate_manuscript_mutation.py`：只读比较改写前后的受保护元素；
- `templates/latex/working-draft/`：仅在用户明确要求新建 LaTeX 且没有现有模板时使用的非官方工作稿。

## Completion

在 `content-only` 与 `section-draft` 模式下，默认只返回用户要求的论文正文或草稿；进入修订、授权写回或用户明确要求审计时，再附带以下验收信息：

- 实际生成或修改了什么；
- 哪些事实和证据被保留；
- 是否写入了主稿，以及授权来源；
- mutation protector 是否通过或为何不适用；
- 每项改写的 `fidelity_validation` 状态与 `declared_derived_values`；
- 哪些信息仍缺证据，因而没有写成事实。
