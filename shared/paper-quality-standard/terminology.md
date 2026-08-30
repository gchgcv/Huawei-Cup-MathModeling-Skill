# Terminology Standard

## TERM-001 — 专业术语语义优先

- **Normative Statement:** 数学、统计、运筹、机器学习、图论、仿真等领域术语，以及模型名、算法名、指标名、数据集名和正式名称，不得仅因风格优化或词表匹配而被删除或替换。
- **Scope:** 全文、图表和公式说明。
- **Required Exceptions:** 术语被误用、未定义或与实际方法不符时必须纠正。
- **Relations:** `PROSE-002`, `AI-005`, `CLAIM-005`。

## TERM-002 — 符号和变量语义唯一

- **Normative Statement:** 同一符号或代码变量在公式、符号表、正文、代码结果和图表中应保持同一含义、单位和角色；空间位置、方向、角度和几何关系应具有足以恢复其含义的说明。
- **Scope:** 公式、符号表、正文、代码映射和图表。
- **Required Exceptions:** 不同章节复用常见局部索引时必须具有清晰且互不冲突的局部作用域。
- **Relations:** `DEPTH-001`, `FIG-004`, `NUM-001`。

## TERM-003 — 缩写与专名可识别

- **Normative Statement:** 非普遍可识别的缩写应在首次出现时给出完整名称或定义；专名和数据字段应保持与权威来源一致。
- **Scope:** 正文、摘要、图表和附录。
- **Required Exceptions:** 题目或官方模板已明确规定且全文统一的缩写可以直接使用。
- **Relations:** `REF-001`, `PROSE-003`。

## TERM-004 — 技术名称不得冒充效果证据

- **Normative Statement:** 模型或算法名称中的“稳健、优化、智能、动态”等术语只说明技术身份，不能单独证明实际结果具有对应效果。
- **Scope:** 方法介绍、结果评价和贡献表述。
- **Required Exceptions:** 对名称本身的定义性说明不属于效果主张。
- **Relations:** `CLAIM-005`, `PROSE-002`。
