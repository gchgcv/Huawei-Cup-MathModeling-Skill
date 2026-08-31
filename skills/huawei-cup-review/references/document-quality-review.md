# Document Quality Review

## Source and output identity

- 使用 `FMT-002` 识别用户声明的唯一主源，使用 `FMT-003` 检查最终输出是否与当前源一致。
- 编译成功只证明构建链路完成；版面检查还需按 `FMT-004` 读取当前 PDF 的视觉证据。
- 未知主源或 stale PDF 必须记录 limitation，不得把旧审核记录当作当前证据。
- 只有 PDF 时，PDF 是审核对象而不是首选编辑源；若由 PDF 重建可编辑稿，必须将其标记为 `RECONSTRUCTED`，不能声称完整保留原模板结构。

## PDF tool routing

- 最终版面和图表的视觉证据固定通过 `pdftoppm` 将当前 PDF 渲染为 PNG 后取得；`PyMuPDF` 的页面渲染、文本框或坐标信息不能替代实际版面视觉检查。
- 需要程序化读取 PDF 时，默认使用 `PyMuPDF`（Python 中导入为 `fitz`）检查页数、页面尺寸、元数据、文本块、字符或词坐标、图片和绘图对象等。提取结果只用于定位和交叉核实，不单独证明版面可读性或论证语义正确。
- `pdfinfo` 可以作为页数、页面尺寸和元数据的独立交叉核对工具；它不是正文、表格或图形内容的主要解析器。现有 PDF review validator 可保留该独立校验。
- `pypdf` 与 `pdfplumber` 不作为默认依赖。只有在 `PyMuPDF` 无法读取特定对象，或确有表格结构诊断需要时，才使用它们，并记录所用工具和回退原因。

## LaTeX review chain

### 局部修改

```text
当前主源
→ 重新编译 PDF
→ 检查日志和引用状态
→ 渲染并检查受影响页面
→ 若分页、浮动或编号向外传播，扩大审核范围
```

### 全文、候选终稿或提交审核

```text
当前主源
→ 重新编译 PDF
→ 检查日志和引用状态
→ 渲染全部页面
→ 逐页检查图表、分页、空白、裁切和图文邻接
```

日志至少检查：

- `LaTeX Error`；
- `Overfull \\hbox` / `Overfull \\vbox`；
- `Float too large for page`；
- `Too many unprocessed floats`；
- `Float(s) lost`；
- 未定义引用、未定义文献和需要重新编译的交叉引用警告。

`audit_latex_build.py` 只能提供源码和日志层证据，不能代替 PDF 视觉检查。

视觉审核记录必须绑定当前 PDF：

- 记录 PDF 路径、SHA256、实际页数、审核范围和已渲染页码；
- `full` 审核只有在所有页面均已渲染和复核、且哈希与当前 PDF 一致时才可通过；
- `affected` 仅适用于局部修改，并覆盖所有受影响页面；
- 重新编译导致 PDF 哈希改变后，旧视觉审核记录自动失效。

## Figures and tables

- 使用 `FIG-001` 至 `FIG-008` 检查论证职责、可读性、引用关系、事实一致性、解释、正式版本、表格数值结构和图表语言。
- caption 与正文、图中数据不一致时，evidence 应分别定位冲突两端。
- 图形文件存在不等于已被正文正确引用；图未引用、重复 label 或缺 caption 是不同问题。
- 默认优先使用正常浮动行为，例如 `[htbp]`；只有正常浮动破坏阅读顺序且局部固定确有必要时才使用 `[H]`。`\FloatBarrier`、调整尺寸、拆分图表或局部 `\clearpage` 应服务于实际漂移问题，不能机械固定所有浮动体。
- 不得让小图或小表独占整页并留下大块空白，不得因为浮动体把章节标题或短段落挤成孤行；连续图表不应把正文解释整体推迟到数页之后。

### 图表论证职责

- 每张正式图应能定位到一个主要论证职责、服务的题目子问题或支持的 claim；不能仅因图形存在、分辨率合格或有 caption 就视为论证充分。
- 复杂图应按 `FIG-005` 检查正文是否给出必要的读图顺序、重点区域、子图关系或主要对照。若流程、分布、评价和最终结果混在一张图中而没有主次，才考虑 `overloaded_figure`；不能仅因子图数量多就形成 finding。
- 辅助示意图可以承担结构说明，不要求承载数值结论；判断依据应是图表实际职责和正文使用方式，而不是图表类型本身。

### PDF 图表视觉清单

在最终论文实际尺寸下逐项检查：

- 刻度数量和数字格式合理，刻度没有重叠；
- 坐标轴标签、图例和注释没有遮挡关键曲线、柱体、散点或区域；
- 多条曲线、标记与图例能够一一对应；
- 子图、标签、标题和注释没有拥挤到难以阅读；
- 文字、数学符号和图元没有越界或被裁切；
- 纵横比例没有造成明显拉伸、压扁或变形；
- 字体、线宽和点大小与最终图幅匹配；
- 小数位数和科学计数法不会造成刻度拥挤；
- 信息过载时拆图，而不是继续缩小字体和图元；
- 多子图默认最多两列，标注密集或结构复杂的图优先拆分；
- 单位、刻度和中文字符在实际 PDF 尺寸下可读，不能只依据独立原图判断；
- 中文论文中的主要坐标轴、图例、方案或类别名称、注释和说明文字原则上使用中文；模型名、算法名、变量、单位、通用缩写及易产生歧义的专业术语可以保留标准形式；
- 中文字体、负号和数学符号正常显示。
- 页眉、页脚和页码正常；标题附近没有不自然分页，最后一页和附录没有意外空页。

图表存在视觉缺陷时，应定位到当前 PDF 页码和图表对象。影响数据读取、曲线辨认或结论判断的缺陷可形成 `FIGURE_VISUAL_DEFECT`；轻微审美问题只能作为较低优先级建议。

### Read-only canonical figure output audit

`audit_figure_references.py` 只检查 LaTeX 中的 `includegraphics`、caption、label 和正文引用；它不能证明正式图目录唯一。需要 manifest 时，Review 另调用只读的 `audit_canonical_figure_outputs.py`。

该审计读取由产出层提供的 manifest，结构以 `../../shared/contracts/figure-manifest.json` 为准，至少识别：

```json
{
  "figure_root": "outputs/figures",
  "canonical": [{"id": "fig:q1", "file": "01_q1.png", "source": "plot.py"}],
  "allowed_files": []
}
```

审计内容包括：

- canonical 文件是否全部存在；
- 实际图文件减去 canonical 和 `allowed_files` 后是否有 unexpected artifacts；
- 非编号文件、语义别名和近似名称版本是否需要人工确认；
- unexpected 文件是否仍被 LaTeX、Markdown、脚本或其他文本源引用。

Review 只返回观察结果和退出码，不创建或更新 manifest，不生成 trash plan，不移动或删除文件，不创建 `.trash`。图形生成、manifest 维护、dry-run 清理计划和可恢复隔离由未来的 Coding & Visual 能力负责。

## Evidence Continuity Review

对核心 claim 和最终选型进行跨材料抽查，按以下链条核对：

```text
Model / Project Facts
        ↓
Computed Result
        ↓
Table / Figure
        ↓
Result Discussion
        ↓
Abstract
        ↓
Conclusion
```

重点检查：

- 摘要中的核心数字、模型名称和指标是否能在正文或有效结果源中找到；
- 正文声称的最优方案、排序、权重或阈值是否与表格、图表和结论一致；
- 指标定义、单位、验证层级和结论强度是否在跨章节转述时发生变化；
- 结论是否引入正文未出现的新评价、数字、证据或模型；
- “稳健”“显著”“优于”等评价是否能回指相应的比较、检验或敏感性证据。

数字冲突优先使用 `NUM-003`；主张追溯或语义断裂使用 `CLAIM-002`；摘要与正文的冲突可使用 `ABS-002`；结论超出正文证据时使用 `STRUCT-004` 或 `CLAIM-001` 中最直接的一个。正式 finding 必须同时定位冲突两端和当前有效事实源；缺少其中一端时记录 limitation，不凭单一材料判定哪一处正确。Review 只读检查，不替用户统一数值、重排结论或修正图表。

## Numbers, terms and references

- 单位与精度检查引用 `NUM-001` 至 `NUM-004`，跨材料关键数字检查优先使用 `NUM-003`。
- 术语和符号检查引用 `TERM-001` 至 `TERM-004`。
- 引用真实性、正文关系与格式检查引用 `REF-001` 至 `REF-005`；未实际核对来源时只能记录 limitation，不能宣称引用虚假。

### Reference audit procedure

- 优先核对原始论文、教材、标准、政府或权威机构资料，以及数据集、软件和算法的官方说明；
- Agent 不得凭记忆补全作者、题名、年份、期刊、DOI 或 URL；无法核实时登记 `REFERENCE_UNVERIFIED` 或 `REFERENCE_MISSING`；
- 已有 `.bib` 时优先继承原格式和 cite key，除非发现重复、错误或用户明确要求，不批量重命名引用键；
- 顺序编码制按正文首次出现顺序编号，首次引用应为 `[1]`，同一处多篇文献按升序排列，如 `[5,6]`；
- 无官方格式要求时，默认检查 GB/T 7714 顺序编码制及 `[M]`、`[J]`、`[S]` 等类型标识；
- 首次引用顺序错误登记 `REFERENCE_ORDER_ERROR`，书目体系混用登记 `REFERENCE_FORMAT_INCONSISTENT`；
- 历年竞赛答案、获奖范文和培训机构解答只能作为对照材料，不能作为正式学术依据。

Review 只报告这些问题，不直接补文献、改 cite key、重排文献表或写回论文。
