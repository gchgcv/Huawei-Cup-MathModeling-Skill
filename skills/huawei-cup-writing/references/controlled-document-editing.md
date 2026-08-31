# Controlled Document Editing

Normative rules: `FMT-001`–`FMT-005`, `FIG-002`, `FIG-003`, `REF-004`.

本文件只规定 LaTeX 论文源、模板来源、PDF 审核对象和受控编辑边界。它不替代 Shared Standard，也不负责生成模型、图形或提交状态。

## Authorization Gate

默认只返回内容或 patch 建议。只有用户明确指定主稿并授权写回时，才允许修改论文文件。

修改前确认：

```text
master_source
source_format
template_source
requested_scope
final_output
```

若已有文件、项目结构或用户指令足以确定这些字段，直接记录并继续，不重复询问。若无法确定唯一主源，先报告证据缺口，不创建替代稿。

## Master Source and Submission Template

主编辑源与提交格式是两项不同判断，不能用同一个优先级同时决定：

### 主编辑源优先级

1. 用户明确指定的当前主稿；
2. 能够生成当前 PDF 的现有可编辑源；
3. 内容最完整且依赖关系明确的现有可编辑源；
4. 用户指定的新模板；
5. 当届官方模板；
6. Skill 工作稿模板；
7. 纯内容输出。

给出完整 `.tex/.cls/.sty/.bib` 项目时，优先继续在该项目中编辑，不迁移到另一套模板。

### 提交格式权威优先级

1. 当届官方论文规范、格式文档和模板；
2. 已逐项核对并确认符合当届要求的用户模板；
3. Skill 工作稿，仅用于内容和排版开发。

现有 LaTeX 可以继续作为主编辑源，但不能仅因编译成功就认定其符合当届提交格式。样例论文只用于结构与表达参考，不是排版模板。

推荐记录：

```text
template_source = official | user | skill_fallback | none
submission_template_verified = true | false | unknown
```

## Existing LaTeX Project

已有 LaTeX 项目时，优先识别并维护现有入口及依赖：

```text
main.tex / Demo.tex / paper.tex
.cls
.sty
.bib
figures/
```

编辑前检查：

- `\documentclass` 与主入口文件；
- 编译引擎和实际生成 PDF 的命令；
- 自定义宏、编号规则和交叉引用；
- 图表目录、参考文献方式及当前 PDF 的生成关系。

不得为了统一格式而重写整个 preamble、替换 `documentclass` 或删除不了解用途的 `.cls/.sty`。修改模板文件时必须有明确范围和授权，并验证受影响的全部输出。

### 正文列表与模板约定

正文列表服从当前 `.cls` 和用户指定模板。对 `gmcmthesis` 等竞赛类模板，若模板要求中文顺序段落，应使用 `（1）`、`（2）` 等文字段落，不得擅自新增 `enumerate`、`\item` 或 `\setlist` 来模拟列表。只检查正文源码中的列表使用，不改写类文件内部宏、参考文献环境或模板实现所需的 `\item`。

## New LaTeX Working Draft

只有用户明确要求新建 LaTeX 且不存在可用模板时，才使用：

```text
templates/latex/working-draft/main.tex
```

该模板的身份必须保持：

```text
template_source = skill_fallback
submission_template_verified = false
```

它是可编译工作稿，不具备官方提交权威性。正式提交前，必须迁入或校准到当届官方规范，并重新进行版式审查。

## Markdown and Content-only Output

当用户只要求章节内容、建模推导、编程说明、图表规划或论文大纲，且没有要求正式论文文件时，优先返回 Markdown 或纯文本，不主动创建 LaTeX 文件。

## PDF as Audit Object

PDF 默认是最终输出和版面审核对象，不是首选编辑源：

- 有可编辑源时，修改源文件后重新生成 PDF；
- 只有 PDF 时，可以审核内容、图表和版式，但不能把 PDF 当作可无损编辑源；
- 若必须从 PDF 重建可编辑稿，必须标记为 `RECONSTRUCTED`；
- `RECONSTRUCTED` 稿不得声称完全保留原模板结构，交付前应与原 PDF 和适用模板重新比较。

LaTeX 主稿形成候选终稿后，应交由 Review 的 `document-quality-review` 执行编译日志、当前 PDF 和图表版面检查。本文件不重复定义逐页视觉清单。

## Parallel Master Prohibition

未经用户明确授权，不得创建以下竞争性主稿或同类替代文件：

```text
main_fixed.tex
main_new.tex
final.tex
paper_revised.tex
submission.tex
```

备份、历史快照和临时渲染文件必须保持可识别身份，不能被重新当作当前主源。用户已有主稿时，不得另建一套独立模板；不得把上一届模板或 Skill 工作稿称为当届官方模板。

## Submission Template Verification

完整论文作为提交稿交付前，至少满足以下一项：

```text
A. template_source = official
   且 official_template_current = true

B. template_source = user
   且 submission_template_verified = true
   且已按当届官方要求完成逐项版式核对
```

若 `template_source = skill_fallback`，只能作为工作稿，不能直接作为提交稿。
