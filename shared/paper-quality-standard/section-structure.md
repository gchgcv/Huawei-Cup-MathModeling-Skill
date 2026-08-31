# Section Structure Standard

## STRUCT-001 — 结构由题目和论证驱动

- **Normative Statement:** 章节应按子问题、逻辑依赖和证据链组织，不按代码文件、算法清单、研究时间线或固定话术模板组织；跨子问题的承接必须能指出实际传递的变量、参数、结果、约束或模型输出，仅按题号先后排列不构成真实依赖。
- **Scope:** 全文章节和段落结构。
- **Required Exceptions:** 附录中的代码、补充实验和数据清单可以按文件或技术类别组织。
- **Relations:** `AI-001`, `AI-002`, `DEPTH-004`。

## STRUCT-002 — 假设采用总述—分条—范围结构

- **Normative Statement:** 模型假设应先说明题面缺口和假设用途，再列出真正进入模型的假设，必要时说明适用范围、失效条件及其对结论的影响。
- **Scope:** 模型假设章节。
- **Required Exceptions:** 只有一个简单且直接的假设时可以合并表述，但仍须说明其用途。
- **Relations:** `DEPTH-001`, `CLAIM-001`。

## STRUCT-003 — 模型、求解、结果和解释就近对应

- **Normative Statement:** 模型定义、求解方法、关键结果和相应解释应保持可识别的阅读邻接，避免结果与其模型或讨论跨越无关章节。
- **Scope:** 模型和结果章节。
- **Required Exceptions:** 全文共享的数据或统一预处理可以集中说明，并通过明确引用建立关系。
- **Relations:** `DEPTH-001`, `DEPTH-002`, `FIG-003`。

## STRUCT-004 — 结论逐问回答且不引入新内容

- **Normative Statement:** 结论应逐问压缩已经证实的答案和关键量化结果，明确回到题目要求的输出及其现实、工程、物理或决策含义，不突然加入正文未出现的新模型、新数字、新证据或成组免责声明。
- **Scope:** 结论章节。
- **Required Exceptions:** 可以简要给出不冒充既有结果的后续研究方向。
- **Relations:** `ABS-003`, `CLAIM-001`, `ADW-005`。

## STRUCT-005 — 段落承担明确任务

- **Normative Statement:** 每个段落应围绕一个可识别的主要任务、关系或结论展开，不能混合无关主张、重复澄清、道歉式限定和空泛总结。
- **Scope:** 连续正文。
- **Required Exceptions:** 为比较两个紧密相关方案而构成的统一论证可以在同一段落完成。
- **Relations:** `PROSE-001`, `ADW-006`, `AI-004`。
