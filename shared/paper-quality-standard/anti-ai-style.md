# Anti-AI Style Standard

本文件只描述可观察的文本风险，不据此判断作者或文本是否使用过 AI。

## AI-001 — 最终逻辑而非工作日志

- **Normative Statement:** 论文应呈现最终成立的题目—模型—证据—结论链，不按“先尝试、随后修改、最后采用”的研究时间顺序堆叠过程记录。
- **Scope:** 问题分析、模型建立、实验与结果章节。
- **Required Exceptions:** 方法筛选过程本身构成模型选择证据时，可以保留与最终选择直接相关的比较。
- **Relations:** `STRUCT-001`, `DEPTH-001`。

## AI-002 — 避免模板化过渡

- **Normative Statement:** 相邻句段不得高密度重复“针对……本文……”“首先……其次……最后……”“结果表明……”等同构框架，段落组织应随实际论证任务变化。
- **Scope:** 连续正文。
- **Required Exceptions:** 明确枚举互相独立的步骤或问题时可以采用有序结构。
- **Relations:** `PROSE-004`, `STRUCT-001`。

## AI-003 — 避免句法机械化

- **Normative Statement:** 连续多重“的”字定语、抽象名词堆叠、主干迟现和承担多重逻辑关系的超长复句不得持续妨碍阅读。
- **Scope:** 中文学术正文。
- **Required Exceptions:** 不能为了缩短句子破坏正式术语、公式条件或因果边界。
- **Relations:** `PROSE-003`, `TERM-001`。

## AI-004 — 避免段落形态过度均匀

- **Normative Statement:** 相邻段落不应机械复用相同开头、相同句数和相同论证模板；段落长度与结构应由内容职责决定。
- **Scope:** 连续多个段落。
- **Required Exceptions:** 平行呈现多个同类实验或子问题时允许结构对称，但每段仍应包含对应的具体证据。
- **Relations:** `AI-002`, `DEPTH-002`。

## AI-005 — 不以空泛概念替代事实

- **Normative Statement:** “框架、机制、体系、赋能、全面提升”等抽象表达只有在指向明确对象、关系或证据时才具有信息价值，不得替代可直接陈述的模型动作和结果。
- **Scope:** 摘要、贡献表述、模型说明和结论。
- **Required Exceptions:** 具有严格数学或领域定义的术语受 `TERM-001` 保护。
- **Relations:** `PROSE-002`, `TERM-001`。

## AI-006 — 风格风险不等于来源判断

- **Normative Statement:** 模板化语言、重复句法或元话语密度只能说明文本存在可观察的表达风险，不能单独证明文本由 AI 生成。
- **Scope:** 所有风格判断和相关报告。
- **Required Exceptions:** 无。
- **Relations:** `PROSE-001`。
