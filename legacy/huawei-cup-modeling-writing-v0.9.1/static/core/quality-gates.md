# 质量门控与提交状态

本文件只负责终稿风险判定。输出顺序固定为：**硬阻断项 → 证据缺口 → 可改进项 → 内部诊断分数**。内部诊断分数不是官方评分、论文最终质量结论或奖项预测，不能覆盖硬错误。

## 1. 提交状态

- `DRAFT`：内容仍在形成；
- `NEEDS_VALIDATION`：主体已形成，但仍有关键事实、计算、检验、语言或格式未核实；
- `BLOCKED`：存在会导致结论错误、不可复现或违规的硬问题；
- `READY_TO_SUBMIT`：全部必需门控通过，无未解决 P0/P1，且完成终稿审核。

## 2. 八项硬门控

每项只能为 `PASS | FAIL | UNVERIFIED | NOT_APPLICABLE`。`PASS` 必须给出具体证据位置。

1. `question_coverage`：主要子问题均得到回答；
2. `result_traceability`：关键数字可追溯到数据、公式或实际程序输出；
3. `cross_artifact_consistency`：题意、单位、参数、公式、代码、表图和正文一致；
4. `model_validity`：假设、变量、目标和约束与题意匹配；
5. `validation_adequacy`：关键模型使用了适配的检验，结论不越界；
6. `format_and_citation`：模板与引用合规；参考文献按 `references/reference-management.md` 判定，LaTeX 终稿版面按 `references/latex-pdf-layout-audit.md` 判定；skill fallback 仅为工作稿，不能直接作为提交模板；
7. `no_fabrication`：不存在编造数据、结果、文献、运行过程或创新；
8. `prose_clarity`：正文表达直接、专业、可核验，无大面积模板化套话、无证据评价、成片防御性免责、工作日志式叙事、犹豫词堆叠或术语失真；同时不能因追求简洁而省略主模型的必要解释和核心结果讨论。论文语言按 `references/paper-prose-style.md` 审核。

有效证据应包含来源与位置，例如 `结果台账R3`、`run.log:42`、`论文4.2节表5`、`附件A字段speed`、`style-lint 报告 + 人工复核位置`。空泛的“已检查”“无问题”“见正文”不能作为证据。

## 3. P0 阻断项

出现任一项，状态必须为 `BLOCKED`：

- 编造或无法追溯的关键数据、结果、精度、最优解或参考文献；
- 代码未运行，却把预期输出写成实验结果；
- 漏答主要子问题且未明确标注；
- 关键公式、约束或单位错误，足以改变结论；
- 正文、代码、图表使用冲突参数或数据版本；
- 图表或结论与最终结果文件矛盾；
- 匿名、抄袭、来源标注等合规风险；
- 仍有未标记占位符，却声称论文已经完成；
- 为降低 AI 痕迹而错误改写专业术语，导致模型或结论含义改变。

## 4. P1 需验证项

以下问题未解决时通常不得高于 `NEEDS_VALIDATION`：

- 主模型缺少适配检验；
- 复杂模型没有简单基线或理论边界对照；
- 随机算法只运行一次却声称稳定；
- 时间序列随机划分或存在明显数据泄漏风险；
- 摘要、正文、结论的关键数字未完成交叉核对；
- 引用尚未核实真实性或正文对应关系；
- 关键结论使用“显著、稳健、优越、有效”等评价词，但没有相应证据；
- 语言修改造成专业术语、统计含义或因果边界可疑；
- 支撑下游结论的关键继承材料仍处于 `INHERITED_UNVERIFIED`、`NEEDS_REVIEW` 或缺少来源；
- 模板来源、当届有效性或用户模板提交适配性尚未核验；
- LaTeX 候选终稿未完成编译日志与最终 PDF 全页视觉审查；
- 核心代码生成图未实际打开/渲染检查，视觉质量仍未核验；
- 正式论文参考文献为空、真实性未核验，或旧题训练违反参考来源边界；
- 主模型正文过度压缩，缺少关键关系来源、约束意义、参数来源或求解说明；
- 核心图表只有趋势复述，没有足够的定量依据和问题解释。

## 5. P2 表达与格式项

不直接改变事实结论，但应在终稿前处理：

- 图表缺少单位、编号、来源或正文引用；
- 图片存在不影响结论但应修复的轻微拥挤、遮挡、比例或字体问题；
- 参考文献中存在少量相关性弱、未在正文实际使用的条目；
- 排版或编号错误；
- 引号、括号、冒号、破折号等在连续正文中明显滥用；
- 高频 AI 套话、机械过渡词或重复句式过多；
- 摘要、段首或结论反复出现“本文不声称/不能证明/不代表/仅作”等无信息增量的防御性免责；
- 同一句叠加多个“可能/或许/一定程度/潜在/初步”等犹豫词，而没有说明不确定性的具体来源；
- 正文按研究时间顺序罗列“先做 A、再做 B、最后做 C”，而没有重构成题目—模型—证据的最终逻辑；
- 多重“的”字定语、抽象名词链或过长复句导致主谓宾主干难以识别；
- 用空泛形容词替代可以直接给出的数值或事实；
- 把一句话或线性文字链放进矩形框并用箭头连接，作为没有信息增量的正式图。

## 5.1 第 6/7 轮暴露的论文规范审查规则

以下规则纳入终稿审核，不把“内容更完整”误认为“规范已经合格”。其中涉及数值、单位、引用和正文可信度的项目，在终稿阶段不得以未核验状态通过 `format_and_citation` 或 `prose_clarity`。排版和表达问题不改变数学事实时通常为 P2；一旦造成物理含义歧义、证据边界误判、引用不可追溯或结论可信度下降，应升级为 P1。

### 5.1.1 模型假设的总—分结构

- 模型假设不能只有 `(1)(2)(3)` 的机械条目；在条目之前先说明题面缺口、为什么需要这些假设以及它们分别处理哪类问题；
- 按问题或机制分条说明，每条假设应在后续模型中实际使用；
- 必要时在列表后说明适用范围、可能失效的场景和对结论的影响；
- 缺少总述但不影响模型复核时登记 `MODEL_ASSUMPTION_STRUCTURE_THIN`；若导致假设含义或适用边界无法核验，升级为 `MODEL_EXPLANATION_THIN` 的 P1。

### 5.1.2 符号表与空间几何说明

- 一般变量、参数和指标可以进入符号表；
- 空间位置、方向、角度、几何关系和机构变量不能只放在抽象符号表中；应使用示意图、图中标注和正文解释共同说明；
- 图中标注、符号表、公式和正文必须使用同一符号，不得出现同一符号多重含义；
- 空间变量缺少足以恢复几何意义的说明时登记 `SYMBOL_GEOMETRY_UNEXPLAINED`，必要时升级 `MODEL_VALIDITY` 或 `cross_artifact_consistency`。

### 5.1.3 图表版面与可读性

- 多子图默认最多两列；三维、机构、密集标注或坐标信息复杂的子图，宁可拆成两幅图，也不能为压缩篇幅缩小到无法读取；
- 坐标轴、图例、单位、刻度、标注和题注必须在最终论文尺寸下可读；不能只看独立原图或源码判断；
- 图表有信息冲突时优先保证可读性和解释顺序，不以占用页数少作为通过理由；
- 影响数据读取或结论判断时登记 `FIGURE_LAYOUT_UNREADABLE` 或 `FIGURE_VISUAL_DEFECT` 为 P1；仅轻微拥挤时为 P2。

### 5.1.4 单位、有效数字与计算精度

- 表格优先将单位放在左侧的物理量列或表头，数值列只列数值，避免每个单元格重复单位；
- 必须区分算法内部精度、求解器容差、残差精度和论文报告精度；内部使用 `1e-8` 容差不等于物理结果需要展示八位或六位小数；
- 长度、角度、质量、百分比和评价指标的报告精度应匹配题目数据、测量/加工条件和实际决策需要；工程临界值应区分“计算值”和“选型/取整值”，必要时给出安全裕量；
- 不能把高精度中间量直接复制到摘要、结论、表格和图注；同一物理量在全文的有效数字和单位应统一；
- 单位缺失、位置造成歧义或精度夸大时登记 `UNIT_PRESENTATION_ERROR`；物理结果的报告精度与数据/工程精度不匹配时登记 `REPORT_PRECISION_MISMATCH`。若仅为不影响含义的格式问题可降为 P2，否则终稿不得保留为 P1。

### 5.1.5 引用顺序与参考文献格式

- 顺序编码制中，正文第一次出现的文献必须为 `[1]`，以后按首次引用顺序递增；
- 同一处多个引用按编号升序书写，如 `[5,6]`，不得出现 `[6,5]`；正文引用顺序、文献表顺序和 BibTeX/交叉引用必须一致；
- 全文统一采用目标竞赛/官方模板要求的格式；官方模板没有明确要求时，默认采用 GB/T 7714 顺序编码制，并按书籍 `[M]`、期刊 `[J]`、标准 `[S]` 等类型统一著录；
- 不能一条使用英文书目风格、另一条使用国标风格，也不能把 DOI、URL、作者或年份孤立到跨页而破坏条目完整性；
- 首次引用不是 `[1]` 或格式体系混用时分别登记 `REFERENCE_ORDER_ERROR`、`REFERENCE_FORMAT_INCONSISTENT`，在终稿中按 P1 处理；详细来源真实性和旧题答案边界仍执行 `references/reference-management.md`。

### 5.1.6 问题驱动写作与 AI 风格风险

- 不能仅凭论文判断作者是否使用 AI；审核对象是可观察的模板化语言、元话语密度、证据边界和问题解释质量；
- 少写“统一为……框架”“便于逐层检查”“完整覆盖”“预先声明的选择规则”“该结果仅反映……”等连续自我评价式话语；只有在确实需要限定证据边界时保留；
- 优先写题目驱动的因果链：题目约束/数据特征 → 模型选择 → 计算结果 → 对应解释；不要反复使用“做了什么—为什么—检验什么—证明什么”的均匀模板；
- 不能用“严谨、稳健、先进、有效”等评价词替代数值、公式、图表或检验依据；没有依据就删去评价，不补造证据；
- `lint_paper_style.py` 只能筛查高风险表达，不能证明“无 AI”或替代人工审核。高密度模板化元话语登记 `AI_STYLE_OVERUSE`；若因此掩盖证据缺口或扩大结论，按 `prose_clarity` 的 P1 处理。
- 去防御性审查必须先区分无必要免责、必要适用范围、真实方法局限、概念对比、证据强度限定和冗余澄清；不得以“更自信”为理由删除影响有效性、外推或决策使用的真实边界。
- 优先使用正面范围表述：直接写研究对象、参数区间、数据范围和适用场景，不反复写“没有覆盖什么”。高密度无必要免责登记 `DEFENSIVE_PROSE_OVERUSE`。
- 工作日志式论文结构登记 `WORKLOG_NARRATIVE`；多重定语、长难句、主干隐藏等高密度句法机械感登记 `SYNTACTIC_AI_PATTERN`。这些代码描述可观察写作风险，不用于断定作者使用了 AI。

## 6. 问题代码

优先使用固定代码：

- P0 常用：`Q_MISSING_MAJOR`、`RESULT_UNTRACEABLE`、`UNEXECUTED_RESULT_CLAIM`、`CROSS_ARTIFACT_CONFLICT`、`FORMULA_OR_UNIT_ERROR`、`COMPLIANCE_RISK`、`UNMARKED_PLACEHOLDER`、`TERM_DISTORTION`；
- P1 常用：`REPRODUCIBILITY_MISSING`、`VALIDATION_MISSING`、`BASELINE_MISSING`、`DATA_LEAKAGE_RISK`、`ABSTRACT_RESULT_MISSING`、`REFERENCE_MISSING`、`REFERENCE_UNVERIFIED`、`REFERENCE_POLICY_VIOLATION`、`REFERENCE_ORDER_ERROR`、`REFERENCE_FORMAT_INCONSISTENT`、`UNIT_PRESENTATION_ERROR`、`REPORT_PRECISION_MISMATCH`、`FIGURE_VISUAL_UNVERIFIED`、`FIGURE_VISUAL_DEFECT`、`EMPTY_EVALUATION`、`TERM_DISTORTION`、`HANDOFF_UNVERIFIED`、`TEMPLATE_SOURCE_UNVERIFIED`、`PDF_LAYOUT_UNVERIFIED`、`MODEL_EXPLANATION_THIN`、`RESULT_DISCUSSION_THIN`；
- P2 常用：`FORMAT_ERROR`、`MODEL_ASSUMPTION_STRUCTURE_THIN`、`SYMBOL_GEOMETRY_UNEXPLAINED`、`FIGURE_LAYOUT_UNREADABLE`、`FIGURE_REFERENCE_MISSING`、`FIGURE_VISUAL_DEFECT`、`REFERENCE_RELEVANCE_LOW`、`AI_STYLE_OVERUSE`、`DEFENSIVE_PROSE_OVERUSE`、`WORKLOG_NARRATIVE`、`SYNTACTIC_AI_PATTERN`、`PUNCTUATION_OVERUSE`、`EMPTY_EVALUATION`、`PSEUDO_FIGURE`、`FLOAT_PLACEMENT_POOR`；
- 无法归类时使用 `OTHER`。

同一代码可因影响范围不同落在不同严重度，严重度由它是否改变事实、结论或可提交性决定。

## 7. 内部诊断分数（仅内部定位）

内部百分制只用于定位薄弱环节。对用户展示时必须放在硬阻断、证据缺口和改进项之后，并明确标注 `Internal Diagnostic Score`；它不代表官方固定分值、论文最终质量结论，也不预测奖项：

- 题意理解与任务完成：15
- 数据处理与可追溯性：15
- 模型合理性：20
- 求解与结果正确性：20
- 检验与稳健性：10
- 论文逻辑与解释：10
- 格式与表达：5
- 贡献或创新：5

无证据的项目不得给满分；未执行内容按未完成计；创新没有证据时可为 0，不得虚构。

### 未解决问题的诊断分封顶

- `Q_MISSING_MAJOR`、`RESULT_UNTRACEABLE`、`UNEXECUTED_RESULT_CLAIM`、`CROSS_ARTIFACT_CONFLICT`：59；
- `REPRODUCIBILITY_MISSING`：69；
- `VALIDATION_MISSING`：74；
- `BASELINE_MISSING`：79；
- `ABSTRACT_RESULT_MISSING`：84。

多个问题并存时取最低封顶。评分与门控冲突时，以门控为准。

## 8. 状态判定与输出顺序

```text
硬阻断项（P0 / gate FAIL）
→ 证据缺口（gate UNVERIFIED / P1）
→ 可改进项（P2）
→ Internal Diagnostic Score
→ 推荐状态
```

- 有未解决 P0 或必需门控 `FAIL`：`BLOCKED`；
- 无 P0/FAIL，但有必需门控 `UNVERIFIED` 或未解决 P1：`NEEDS_VALIDATION`；
- 全部必需门控通过、无未解决 P0/P1、无占位符并完成终稿审核：才可 `READY_TO_SUBMIT`；
- 其余工作中版本：`DRAFT`。
