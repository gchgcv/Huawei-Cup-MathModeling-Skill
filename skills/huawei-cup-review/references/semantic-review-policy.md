# Semantic Review Policy

Semantic review 负责解释“证据如何构成违反规则的问题”，不重写 Shared Standard。

## Style and AI-like patterns

- 对照 `PROSE-001` 至 `PROSE-006`、`AI-001` 至 `AI-006` 检查工作日志式叙事、机械连接、隐藏句子主干、空泛评价和过度均匀结构。
- 按 `PROSE-003` 检查中文句子是否照搬英语式信息压缩。若同一句同时承担现象、证据、解释、条件和范围，导致主干难以识别，应建议按逻辑拆句，而不是继续添加连接词或分号。
- 按 `PROSE-006` 检查“被……”是否属于不必要的翻译式被动。不得按“被”字数量自动形成 finding；应说明施事者是否明确、是否影响信息焦点，以及改写是否会改变责任归属、因果关系或模型含义。
- 风格检测结果只是候选证据；不得据此判断文本来源或作者身份。
- `TERM-001` 要求保护专业术语语义，不能把术语命中本身当作问题。

### Writing / Review language boundary

Review finding 可以使用“不能据此证明”“现有证据不足以支持”“需要指出的是”等诊断性表达，因为这些句式用于说明主张与证据之间的缺口。它们不应被原样复制到最终论文正文；Writing 应将同一问题改写为当前证据范围、成立条件或待验证层级。`lint_paper_style.py` 对这类文本只给 warning，不自动替换，也不要求删除必要的负面证据。

连续正文中以引号包住三个名词、用破折号连接并套“研究框架”“模型链”“完整闭环”等抽象名词时，可按 `AI-005` 或 `PROSE-003` 形成候选 finding。流程图节点、图题、表格阶段名和伪代码中的紧凑标签属于上下文例外；正式 finding 必须说明正文是否缺少实际输入、输出或问题接口，不能仅凭出现破折号形成问题。

## Defensive writing

- 使用 `ADW-001` 至 `ADW-006` 区分无信息免责、必要边界、真实限制和不确定性来源。
- 单个“可能”“限制”或 caveat 不自动构成 finding；必须说明它如何削弱主张、遮蔽结果或重复无信息内容。
- 检查段落是否反复以“未通过、未包含、未覆盖、未验证、未达到”等否定范围收尾。若事实边界必要但表达没有正面说明现有证据支持的对象、条件或验证层级，可按 `ADW-003` 形成 P2 finding；推荐改写证据范围，不得建议删除负面结果。
- `CLAIM-006` 所覆盖的核心负面证据不能因追求自信语气而被建议删除。

## Argument depth

- 使用 `DEPTH-001` 至 `DEPTH-005` 检查模型可复核性、结果讨论、实验职责与弱结果解释。
- “深度不足”必须指出缺少的具体论证环节及所在段落，不能只给泛化评价。
- 图后文字同时参考 `FIG-005`；只复述曲线方向而没有证据解释时，可形成有定位的候选 finding。

## Claim-Evidence

- 使用 `CLAIM-001` 至 `CLAIM-006` 检查范围外推、追溯缺失、相关与因果、模拟与观测、稳健性和负面证据。
- 证据既要定位主张，也应定位支持材料或明确说明已检查范围内缺少何种材料。
- 跨 artifact 数字冲突同时引用 `NUM-003`；符号语义冲突同时引用 `TERM-002`。

## Eight semantic extension checks

以下检查是对现有 Shared Rule 的操作化补充，不是新的 `rule_id` 体系。建议将下表中的名称作为 finding 的 `category`，正式 finding 的 `rule_id` 仍必须使用 Shared registry 中的编号；同一 finding 只选择一个最直接的主 Rule ID。

| 清单项 | 建议 category | 默认主 Rule ID | 审查重点 |
|---|---|---|---|
| 1. Model Tailoring Test | `generic_model_description` | `DEPTH-001` | 是否把题目特征映射到模型关系，而不是使用可替换到多数题目的通用模型介绍 |
| 2. True Cross-Question Linkage | `false_cross_question_linkage` | `STRUCT-001` | 是否能指出前一问的变量、参数、结果、约束或模型输出，以及后一问的实际使用方式 |
| 3. Parameter Provenance | `untraceable_parameter` | `DEPTH-001` | 关键参数是否同时具备数值、单位、来源或推导依据和模型作用 |
| 4. Equation Context | `uncontextualized_equation` | `DEPTH-001` | 核心公式前后是否交代建模对象、进入当前问题的原因、符号语义和输出含义 |
| 6. Evidence-based Model Evaluation | `unsupported_model_praise` | `PROSE-002` | “有效、合理、优越、稳健”等评价是否对应具体设计、评价目标和可定位证据 |
| 7. Bounded Limitation | `unbounded_limitation` / `fatal_issue_disguised_as_limitation` | `ADW-002` | 局限是否说明影响因素、作用环节、证据范围和对结论的影响；核心有效性问题不能被软化 |
| 8. Improvement–Limitation Alignment | `unaligned_improvement` | `DEPTH-005` | 后续改进是否回应已识别局限，并说明拟改变的环节和预期作用 |
| 9. Concrete Generalization | `vague_generalization` | `CLAIM-001` | 推广表述是否给出适用对象、关键条件、验证层级和不能外推的边界 |

### Evidence requirements for the extension checks

- **模型定制性**：至少同时定位题目特征和模型说明。仅凭“这段话听起来通用”不能形成正式 finding；应指出缺少哪一项特征—模型关系。
- **跨问承接**：先寻找实际传递的中间量或约束，再判断承接是否成立。章节连续、题号相邻或使用“基于上一问”不构成证据。
- **参数与公式**：关键参数缺来源，或核心公式缺前后语境时，应定位公式、参数表和相邻正文；若只是单位问题，优先使用 `NUM-001`，不要扩大为模型不可复核。
- **模型评价**：按照“采取的设计—针对的问题—观察到的证据—支持范围”核对。没有基线或指标时，不能仅凭结果较好形成“优于其他方法”的 finding。
- **局限判别**：先区分有界局限和核心有效性问题。后者若影响变量定义、关键约束、数据对应、结果复现或主要结论成立，不能只标为“仍有提升空间”；正式 Rule ID 根据实际违反的 `ADW`、`CLAIM` 或 `DEPTH` 规则选择。
- **改进与推广**：改进方向必须能回指具体局限；推广方向必须能回指对象、条件和验证层级。缺少这些信息时，finding 应说明缺口，不替论文补写效果或普适性。

## Second-batch coherence checks

以下 category 用于表达本轮“整篇论文串联”问题，仍不改变正式 finding 的 `rule_id` 契约。模型数量、图表数量或结果指标较多本身不是问题；只有在缺少论证职责、接口、解释或证据连续性时，才形成 finding。

| 建议 category | 默认主 Rule ID | 审查重点 |
|---|---|---|
| `undefined_model_responsibility` | `DEPTH-001` | 主要模型或模块没有说明解决的困难、输入输出、前后接口或存在必要性 |
| `redundant_model_component` | `DEPTH-001` | 模块输出未被后续使用，也没有承担对照、验证或解释职责；必须有完整链路证据 |
| `result_without_comparison` | `DEPTH-002` | 存在自然对照却没有说明基准或差异；没有自然对照时不得强行形成该 finding |
| `result_without_interpretation` | `DEPTH-002` | 只报告数字或“效果较好”，没有现象、机制或证据解释 |
| `result_not_closed_to_task` | `STRUCT-004` | 结果没有回到题目要求的最终输出、判断或决策含义 |
| `figure_without_argument_role` | `FIG-001` | 正式图没有可识别的主要论证职责、服务问题或支持 claim |
| `overloaded_figure` | `FIG-001` | 多种职责挤在同一复杂图中，读者无法判断主要信息；不能仅因子图多而报告 |
| `figure_without_reading_guidance` | `FIG-005` | 复杂图缺少必要的读图顺序、重点区域、子图关系或主要对照 |
| `cross_section_result_mismatch` | `CLAIM-002` | 正文、图表、摘要或结论对同一结果的模型、排序、指标或强度表述冲突 |
| `claim_evidence_discontinuity` | `CLAIM-002` | 核心 claim 在模型、结果、讨论和摘要/结论之间无法连续回溯到证据 |
| `abstract_body_mismatch` | `ABS-002` | 摘要核心内容与正文或有效结果源不一致；数字冲突还应考虑 `NUM-003` |
| `conclusion_evidence_mismatch` | `STRUCT-004` | 结论加入正文没有支撑的新评价、数字、证据或选择判断 |

### Second-batch evidence requirements

- **模型责任**：同时定位模块名称及其前后文或模型链接口。`redundant_model_component` 还必须证明该模块没有后续使用、对照、验证或解释职责，不能只凭算法名单较长判断冗余。
- **结果叙事**：定位结果段和对应题目要求。若存在自然基线，证据应指出缺少比较对象或差异；若题目没有自然基线，应检查绝对水平、阈值、约束或验证对象，不报告“缺少对照”。
- **题意闭环**：定位题目要求的最终输出与结果段或结论段，说明论文停留在哪个指标、权重、路径、聚类或排名，尚未完成什么判断；不能要求每个指标都转成现实建议。
- **图表职责**：同时定位图表和正文首次引入、读图或结论段。复杂图只有在主要信息不可识别或缺少必要读图提示时才形成 finding；辅助示意图不因没有数值结论而自动违规。
- **证据连续性**：跨章节 finding 至少定位冲突或断裂的两端，并说明当前有效结果源是否已检查。摘要、正文、图表或结论只有一端可见时，应记录 limitation，不凭缺失一端推断冲突。

## Abstract and coherence

- 摘要使用 `ABS-001` 至 `ABS-005`，章节关系使用 `STRUCT-001` 至 `STRUCT-005`。
- 摘要与正文冲突必须定位两处内容；不得只凭摘要措辞推断正文不存在证据。
- 结论越界可结合 `STRUCT-004` 与 `CLAIM-001`，但每个 finding 只选择最直接的主 Rule ID。
