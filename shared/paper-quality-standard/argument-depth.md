# Argument Depth Standard

## DEPTH-001 — 模型说明可复核

- **Normative Statement:** 主模型说明应覆盖变量定义依据、关系建立依据、目标函数来源、关键约束的现实含义、参数来源、求解方法、输出与题目之间的对应关系，以及验证接口。
- **Scope:** 模型建立与求解章节。
- **Required Exceptions:** 简单直接的问题可以压缩篇幅，但不得省略决定模型含义和可复核性的关键环节。
- **Relations:** `STRUCT-002`, `CLAIM-002`, `TERM-002`。

## DEPTH-002 — 核心结果讨论完整

- **Normative Statement:** 核心结果讨论应包含主要现象、定量证据、模型或机理解释以及对题目子问题的意义，不能只复述图表趋势。
- **Scope:** 结果与讨论章节及核心图表后的正文。
- **Required Exceptions:** 次要辅助结果可以简短说明，但不得承载超出其讨论深度的核心结论。
- **Relations:** `FIG-005`, `CLAIM-002`, `PROSE-002`。

## DEPTH-003 — 实验具有论证职责

- **Normative Statement:** 对比、检验、敏感性和消融内容应服务于明确的主张，如有效性、机制、场景价值、替代解释或适用边界；未实际完成的实验不得写成结果。
- **Scope:** 实验、验证、敏感性和结果讨论。
- **Required Exceptions:** 计划中的实验只能明确标为待执行内容，不能支撑既有结论。
- **Relations:** `CLAIM-002`, `CLAIM-005`。

## DEPTH-004 — 深度来自证据而非篇幅

- **Normative Statement:** 论文深度应由必要推导、参数依据、约束解释、真实验证和结果分析构成，不由重复背景、无关公式、装饰性图表或空泛创新表述构成。
- **Scope:** 全文内容取舍。
- **Required Exceptions:** 官方模板要求的固定栏目可以保留，但不能替代实质论证。
- **Relations:** `FIG-001`, `AI-005`, `STRUCT-001`。

## DEPTH-005 — 弱结果按证据解释

- **Normative Statement:** 不占优或存在权衡的结果应根据目标、约束、精度、解释性、计算成本或适用范围如实解释，不得隐藏影响核心结论的证据，也不得把局部不足扩大为无依据的整体否定。
- **Scope:** 对比实验、结果讨论和结论。
- **Required Exceptions:** 与任何主张均无关的探索性结果可以不进入正式论文。
- **Relations:** `CLAIM-006`, `ADW-002`。
