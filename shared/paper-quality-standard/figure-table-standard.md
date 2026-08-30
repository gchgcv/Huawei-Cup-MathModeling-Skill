# Figure and Table Standard

## FIG-001 — 图表必须提供信息增量

- **Normative Statement:** 正式图表应展示正文难以同等清晰表达的趋势、结构、分布、空间关系、网络、流程分支或多变量比较；纯文字装框、线性词语箭头链和装饰性总览不构成有效图形。
- **Scope:** 正式论文图表。
- **Required Exceptions:** 官方模板要求的固定示意元素可以保留。
- **Relations:** `DEPTH-004`。

## FIG-002 — 最终版面尺寸下可读

- **Normative Statement:** 坐标轴、图例、刻度、单位、标注、题注和子图必须在最终论文版面尺寸下可读，不得仅凭独立原图或绘图代码判断通过。
- **Scope:** 进入最终文档的图表。
- **Required Exceptions:** 交互式或附录高分辨率材料不能替代正文图表的最低可读性。
- **Relations:** `FMT-004`, `NUM-001`。

## FIG-003 — 图表与引用位置关系清晰

- **Normative Statement:** 图题、表题应与对象紧邻，正文首次引用与图表位置应保持合理阅读顺序，图表不得漂移到与讨论脱节的章节。
- **Scope:** 最终排版文档。
- **Required Exceptions:** 跨页表格和模板规定的图表清单可以采用专门排版结构。
- **Relations:** `STRUCT-003`, `FMT-004`。

## FIG-004 — 图表内容与事实源一致

- **Normative Statement:** 图表数据、排序、单位、有效数字、图例含义、方案名称和正文解释必须与当前有效结果和事实来源一致。
- **Scope:** 所有正式图表及其正文引用。
- **Required Exceptions:** 明确标注的示意图可以不使用结果数据，但不得伪装成计算或观测结果。
- **Relations:** `CLAIM-004`, `NUM-003`, `TERM-002`。

## FIG-005 — 核心图表必须得到解释

- **Normative Statement:** 核心图表后的讨论应给出关键数值、模型或机理解释以及与题目子问题的关系，不能停留在“由图可知”或趋势复述。
- **Scope:** 核心结果图表。
- **Required Exceptions:** 自解释的辅助表格可以通过附近正文统一说明。
- **Relations:** `DEPTH-002`, `CLAIM-002`。

## FIG-006 — 图形正式版本唯一

- **Normative Statement:** 每个进入论文的逻辑图应有唯一可追溯的正式版本；旧图、语义别名和临时导出不得与正式版本形成未解释竞争关系。
- **Scope:** 正式图形集合和论文引用。
- **Required Exceptions:** 明确区分用途、版本和引用位置的对比图不属于竞争版本。
- **Relations:** `FIG-004`, `FMT-003`。

## FIG-007 — 表格单位与数值结构清晰

- **Normative Statement:** 表格应在物理量列或表头明确单位，数值列避免重复冗长单位；列名、精度和对齐方式应支持准确比较。
- **Scope:** 数值表格。
- **Required Exceptions:** 单元格单位确实不同且无法由表头表达时可以逐项注明。
- **Relations:** `NUM-001`, `NUM-002`。
