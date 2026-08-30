# 执行契约

本文件只定义所有任务都必须遵守的行为边界。阶段细节由对应 fragment 决定，避免重复加载同一规则。

## 1. 决策优先级

固定优先级：

1. 不编造事实、数据、结果、文献或运行过程；
2. 不改变原题目标、约束和数据口径；
3. 优先继承已有且可用的成果，不做无必要的重复工作；
4. 题意、数据、公式、代码、图表和正文保持一致；
5. 结论不超过实际证据；
6. 先采用容易检查和验证的方案，再考虑复杂提升；
7. 只完成用户要求的范围。

## 2. 先判断入口，再判断模式

开始时确定：

```text
entry = fresh | handoff
checkpoint = fresh | after_problem_reading | after_data_preprocessing |
             after_model_construction | after_computation | after_results |
             after_draft | mixed
mode = analysis | build | paper | micro-revision | revision | audit
stage = 一个或多个必要阶段
artifacts = 当前实际可用的题目、数据、模型说明、代码、日志、结果、图表、论文和模板
document_target = preserve-existing | official-template | user-template |
                  latex-working-draft | docx-working-draft | content-only
```

若已有中间成果，必须优先进入 `handoff`，按 `static/fragments/entry/handoff.md` 做断点续接。只有用户明确要求从头重做，或已有成果无法满足最小桥接检查时，才回退到更早阶段。

局部分析、局部修改和局部审核不得自动扩展为完整论文。

## 3. 阶段完成状态与事实状态分离

事实或数字使用：

- `CONFIRMED`：来自原题、官方附件、可靠外部来源或用户明确提供/确认的源信息；该状态表示来源明确，不等于已独立证明其数学正确性；
- `DERIVED`：由 `CONFIRMED` 信息通过明确公式、可复现计算或实际运行程序得到的派生量与结果；
- `ASSUMED`：为建模所作假设，必须说明依据和影响；
- `MISSING`：信息缺失，禁止自行补值。

无法核验但需要继续检查的事项使用 `UNVERIFIED`，它不是事实状态，也不能替代证据。

工作流阶段使用另一套状态：

- `NOT_STARTED`
- `INHERITED_UNVERIFIED`
- `INHERITED_VERIFIED`
- `COMPLETED`
- `NEEDS_REVIEW`
- `BLOCKED`
- `NOT_APPLICABLE`

不要把“用户已经做过”自动等同于 `INHERITED_VERIFIED`，也不要把继承成果错误标成当前 agent 的 `COMPLETED`。

## 4. 证据前置，而不是阶段历史前置

下游阶段需要的是**可用证据**，不是“本 agent 已经执行过所有上游阶段”。

进入下一阶段只检查：

```text
当前任务需要哪些输入证据？
现有材料是否已经提供？
这些材料是否通过最小接口核验？
是否与更高优先级事实源冲突？
```

满足即可继续。若不满足，只补最短缺口；无法补齐时降级、标记阻断原因或停止。不得为了流程完整而从第一阶段重跑。

## 5. 继承成果的最小核验原则

- 已有题意拆解：检查覆盖、输入输出和硬约束，不重新写题意分析；
- 已有模型：检查是否回答题目、变量约束能否落到代码，不重新凑备选模型；
- 已有代码：反向提取输入、参数、核心逻辑和输出，再核对题目/模型；
- 已有结果：先核对来源和版本，不能从图片反向认定结果真实；
- 已有论文：保留正确内容，只修改目标范围及依赖项。

详细规则见 `static/fragments/entry/handoff.md`。

## 6. 证据规则

- 只报告实际完成的工作；
- 未运行的程序、未完成的实验和未核实的文献只能写成待执行或未验证；
- `PASS` 必须指向具体文件、结果编号、章节、表图、日志或数据字段；
- “已检查”“无问题”“见正文”“结果正常”等不构成证据；
- 复杂模型不能用文字完整、排版整齐或高内部评分证明正确。

## 7. 变更传播

事实、参数、公式、数据处理或模型一旦改变，先修改权威事实源，再沿依赖关系同步受影响对象。具体传播链见 `static/core/consistency.md`。


## 8. 论文文件的主编辑源与禁止擅自建稿

涉及论文文件时，必须先确定唯一主编辑源和模板来源，再修改内容。优先级和具体规则见 `references/document-editing.md`。

核心边界：

- 已有可编辑主稿时继续编辑原主稿，不创建平行主稿；
- **未经用户明确要求创建新的 LaTeX 文件，不得新建任何新的 `.tex` 主源或替代稿。**“为了安全”“为了避免改坏”“方便比较”都不是创建新 `.tex` 的授权；
- 禁止自行产生 `main_fixed.tex`、`main_new.tex`、`paper_revised.tex`、`final.tex`、`submission.tex` 等竞争性主源；
- 备份只能进入项目既有备份位置或明确的备份机制，备份副本不得继续作为新的工作主源；
- 若用户没有授权创建新 `.tex` 且当前不存在可编辑 LaTeX 主源，则保持 `content-only` 或仅给出补丁/修改建议，不自行落盘一个新 LaTeX 文件；
- 当届官方标准文档是提交格式最高优先级来源；
- skill 内置 LaTeX 仅为工作稿，不能称为官方模板；
- 没有正式文件需求时优先内容输出，不主动造 LaTeX/Word；
- PDF 默认用于输出和审核，有可编辑源时不直接修改 PDF 作为主稿。

## 9. 论文状态

完整论文不是默认输出。涉及论文提交判断时，状态只能由 `static/core/quality-gates.md` 决定；未经 `submission-audit` 不得使用 `READY_TO_SUBMIT`。


## 10. 强制完成门

Agent 的“完成”必须对应可验证动作，不对应主观感觉。

### 所有论文修改

- 当前修改必须落在已确定的唯一主源及其真实依赖中；
- 不得出现未经授权的新 `.tex` 平行稿；
- 用户要求范围之外的改动必须有明确依赖理由；
- 修改事实、参数、编号、图表或引用后，必须沿依赖链核对受影响对象。

### `micro-revision`

必须完成：定位 → 保护原源 → 局部修改 → 编译 → 日志检查 → 受影响页面视觉检查。若影响向外传播，升级为 `revision`。

### 正式图形变更

若新增、重绘、替换、改名或清理正式图，必须使用 canonical figure manifest 核对正式文件集合。清理先 dry-run；只能将确认无引用的遗留图移入 `.trash`，不得直接删除。

### LaTeX 全文、终稿或提交版

必须基于**当前 PDF**完成编译日志和全页视觉审核。旧截图、旧页码记录或旧 review 不得证明修改后的 PDF。建议使用 `scripts/validate_latex_review.py` 对 PDF 哈希、页数和审核覆盖范围做机器校验。

任何适用完成项没有证据时只能保留 `UNVERIFIED`，不得以“已检查”“编译通过”“无明显问题”替代。
