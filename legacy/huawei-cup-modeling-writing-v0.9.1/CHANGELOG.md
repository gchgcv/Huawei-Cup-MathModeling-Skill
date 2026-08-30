# Changelog

## 0.9.1-writing

- 将主 Skill 定位调整为“数学建模论文写作与审校优先”，建模与工程能力主要作为事实核验和证据支撑，不以端到端重做为默认目标。
- 引入去防御性六分类：无必要免责、必要适用范围、真实方法局限、概念对比、证据强度限定、冗余澄清；先分类再删除、移动或重构。
- 新增 Positive Scope、Claim-forward 与 Limitation Placement：直接界定研究对象和适用范围，核心主张先行，必要局限集中到合适章节。
- 新增“真实不确定性写来源、不叠犹豫词”规则，要求主张宽度与证据强度一致。
- 新增“最终逻辑而非工作日志”叙事规则；实验按论证职责组织，不按研究时间顺序堆砌。
- 新增弱结果与权衡处理边界：不主动自我攻击，但不得隐藏会改变核心结论的负面证据。
- 去 AI 味扩展到句法层：多重“的”字定语、主干隐藏、抽象名词堆叠、超长复句和相邻段落同构句式。
- 保留专业术语保护：机制、稳健性、耦合、拓扑、动态等在具有明确数学/技术含义时不得机械禁用。
- 风格 linter 新增防御性范围、caveat-first、犹豫词堆叠、工作日志式叙事和长难句/定语链风险提示。
- 新增 `DEFENSIVE_PROSE_OVERUSE`、`WORKLOG_NARRATIVE`、`SYNTACTIC_AI_PATTERN` 风险代码及回归测试。

## 0.9.0-stable

- 强化 LaTeX 主源权威：未经用户明确授权禁止新建平行 `.tex` 主稿。
- 新增 `micro-revision` 模式及自动升级条件。
- 新增 canonical figure manifest、正式图白名单审计、dry-run 与 `.trash` 安全清理。
- 新增 PDF review 证据校验：绑定 SHA-256、页数、渲染页和复核页。
- LaTeX 源码审计递归跟踪 `\input` / `\include` / `\subfile`。
- 质量输出强调“硬阻断 → 证据缺口 → 改进项 → Internal Diagnostic Score”，弱化总分感。
- 将第 6/7 轮暴露的模型假设总—分结构、几何符号图文联动、两列以内子图可读性、单位与报告精度、顺序引用/统一格式和问题驱动写作纳入终稿审核。
- 新增 `REFERENCE_ORDER_ERROR`、`REFERENCE_FORMAT_INCONSISTENT`、`UNIT_PRESENTATION_ERROR`、`REPORT_PRECISION_MISMATCH`、`MODEL_ASSUMPTION_STRUCTURE_THIN`、`SYMBOL_GEOMETRY_UNEXPLAINED`、`FIGURE_LAYOUT_UNREADABLE` 风险代码并同步质量报告校验。
- 暂不加入 handoff 页数/图号/标题同步检查。

## 0.8.2-stable

- 新增正式代码出图的中文化与视觉检查闭环，要求 Agent/Codex 检查实际生成图文件，而非只看绘图源码或运行返回码。
- 明确图文件视觉质量与最终 PDF 版面审核的职责边界，避免 `result-visualization` 与 `latex-pdf-layout-audit` 重复。
- 新增 `references/reference-management.md` 作为参考文献唯一详细规则源：正式论文参考文献不得为空，不追求数量，必须真实、相关且正文实际使用。
- 历年旧题训练禁止把官方参考答案、优秀/获奖范文、培训机构现成解答或同题完整解题帖列为正式参考文献；用户要求复盘时仅可作为独立对照材料。
- 新增 `REFERENCE_MISSING`、`REFERENCE_POLICY_VIOLATION`、`REFERENCE_RELEVANCE_LOW`、`FIGURE_VISUAL_UNVERIFIED`、`FIGURE_VISUAL_DEFECT` 风险代码并同步质量报告校验。
- 阶段 fragment 与质量门控改为“路由/判定”，不复制参考文件中的详细执行规则。

## 0.8.1-stable

- 修复 v0.8.0 文档与 `validate_quality_report.py` 的风险代码漂移：机器校验现已接受 `PDF_LAYOUT_UNVERIFIED`、`MODEL_EXPLANATION_THIN`、`RESULT_DISCUSSION_THIN`、`PSEUDO_FIGURE`、`FLOAT_PLACEMENT_POOR`。
- 将机器端已有的 `TEMPLATE_SOURCE_UNVERIFIED` 补入质量门控文档，统一模板核验问题代码。
- 澄清四态信息：实际程序输出属于 `DERIVED`；`CONFIRMED` 表示源信息来源明确，不等价于数学正确性已被独立证明。
- 修正 `problem-reading` 产物措辞，避免“文字链路”诱导生成 v0.8 已禁止的装饰型伪流程图。
- 放宽模型构建/检验中的过度基线约束：复杂或数值型方案优先准备简单基线；无合理同类基线时允许理论边界、已知特例、量纲/极限检查或独立计算，不为形式完整强造基线。
- 新增 v0.8 风险代码回归测试，防止后续再次出现文档—脚本漂移。

## 0.8.0-stable

- LaTeX 正式稿新增“编译日志 + 最终 PDF 全页渲染 + 图表浮动/分页/裁切”强制审查链。
- 新增 `references/latex-pdf-layout-audit.md` 和 `scripts/audit_latex_build.py`。
- 禁止将纯文字箭头链、矩形文字框等无信息增量内容作为正式论文图；优先正文，确有结构时使用规范流程图/结构框图。
- 提高建模正文最低完整度，要求说明模型选择、关系来源、关键约束、参数来源、求解过程与验证接口。
- 提高核心图表讨论最低完整度，要求有定量依据、模型解释、题目对应和必要边界。
- 新增 `PDF_LAYOUT_UNVERIFIED`、`MODEL_EXPLANATION_THIN`、`RESULT_DISCUSSION_THIN`、`PSEUDO_FIGURE`、`FLOAT_PLACEMENT_POOR` 风险代码。
## 0.7.0-stable

- 明确论文文件的主编辑源与模板来源优先级，新增 `document_target` 路由。
- 已有 LaTeX/DOCX 主稿时默认原位继承，不再允许 agent 无理由另造模板或迁移格式。
- 新增 `references/document-editing.md`，区分官方模板、用户模板、skill fallback 与纯内容输出。
- 新增固定 `templates/latex/working-draft/main.tex`；只作为 XeLaTeX 工作稿，明确禁止冒充华为杯官方模板。
- 建模台账新增文档来源、模板来源、编译入口和提交模板核验状态。
- `READY_TO_SUBMIT` 将与模板来源联动：skill fallback 不能直接进入提交状态。

## 0.6.0-stable

- 新增 `fresh / handoff` 入口轴，支持 agent 从题意拆解、数据处理、建模思路、代码、结果、图表或论文任意阶段介入。
- 新增 `static/fragments/entry/handoff.md`，采用“继承优先、最小桥接、只补最短缺口”的断点续接规则。
- 将 manifest 的阶段前置条件从“必须执行过上游阶段”改为“必须具备可用上游证据”，允许继承材料经最小核验后直接满足下游输入。
- 新增工作流阶段状态：`NOT_STARTED / INHERITED_UNVERIFIED / INHERITED_VERIFIED / COMPLETED / NEEDS_REVIEW / BLOCKED / NOT_APPLICABLE`。
- 建模台账新增 `entry`、`checkpoint`、`workflow.current_stage` 和阶段证据记录，区分“已有成果”与“本次已完成”。
- 修正 `validate_ledger.py --strict` 的过度约束：只在真正进入模型依赖阶段时要求模型字段，不再对单纯读题或局部审核产生假错误。
- 代码优先介入时要求从代码反向提取最小模型映射，但不要求重写完整建模过程；无法运行时保持 `UNVERIFIED`。
- 新增 `HANDOFF_UNVERIFIED` 风险代码；终稿审核必须清除当前有效方案链上的未核验继承状态。
- `validate_quality_report.py` 新增可选 `--ledger` 联动校验；若继承阶段未核验或 submission-audit 未完成，机器层面禁止 `READY_TO_SUBMIT`。
- 新增断点续接回归测试，覆盖题意后介入、建模后介入、代码优先介入、继承证据缺失和错误 fresh/inherited 状态。

## 0.5.0-stable

- 将 `always_load` 从 7 个核心文件压缩为 3 个，合并重复的姿态、流程、输出和路由规则。
- 删除已被其他文件覆盖的 `stance.md`、`workflow.md`、`output-format.md`、`routing-examples.md` 和旧 `model-innovation` 兼容阶段。
- 新增 `paper-prose-style.md`，约束数学建模正文的引号、括号、冒号、破折号、套话、空泛评价和机械过渡。
- 明确“专业术语保护”优先于去 AI 味，禁止按词表机械替换模型名、统计术语、指标和正式名称。
- 质量门控由 7 项扩展为 8 项，新增 `prose_clarity`，并加入正文风格相关 P1/P2 问题代码。
- 新增 `lint_paper_style.py`，支持 TXT/Markdown/LaTeX/DOCX 的保守式风格风险筛查；脚本只报警，不自动改写。
- 新增风格 linter 回归测试，并将正文语言审核加入 paper/revision/audit 与 submission-audit。

## 0.4.0-stable

- 将竞赛评审导向转化为七项可执行硬门控，而非固定官方百分制。
- 新增 `DRAFT / NEEDS_VALIDATION / BLOCKED / READY_TO_SUBMIT` 四级提交状态。
- 新增 P0/P1/P2 问题体系、证据化 PASS 规则和诊断分封顶规则。
- 新增 `submission-audit` 阶段，规定“先阻断、再门控、后评分”的审核顺序。
- 新增质量报告 JSON/YAML 模板与 `validate_quality_report.py`。
- 新增关键结论 `claims` 台账，限制无证据结论进入摘要和结论。
- 新增质量校验回归测试；更新入口提示、论文模式、审计模式和写作规则。
- 内部评分明确为诊断工具，不宣称对应官方分数或获奖等级。

## 0.3.0-stable

- 将目标从“强制完整长论文”改为“优先正确、一致和可追溯”。
- 新增 analysis/build/paper/revision/audit 五种任务模式。
- 新增执行契约、四态信息标记、阶段门控和变更传播规则。
- 新增问题、数据、参数和结果四类统一台账。
- 为全部阶段加入输入、产物、通过条件和禁止行为。
- 补齐模型检验、贡献表述、Word 公式和篇幅控制参考文件。
- 修复 DOCX 公式重复计数，并扩展到页眉、页脚、脚注和尾注。
- 新增 manifest 路径完整性、台账一致性和 DOCX 公式校验脚本。
