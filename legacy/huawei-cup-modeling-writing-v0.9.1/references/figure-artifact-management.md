# 深层参考：正式图形产物唯一性与清理

本文件只负责正式图文件的**版本唯一性、文件集合、别名/遗留图识别和安全清理**。图像内容是否清晰由 `references/result-visualization.md` 负责；图进入 PDF 后的浮动与分页由 `references/latex-pdf-layout-audit.md` 负责。

## 1. 唯一正式版本原则

`outputs/figures` 应被视为论文正式图发布目录，不是实验图片仓库。每个进入论文的逻辑图只能有一个 canonical 正式文件。语义别名、早期方案图、旧编号图、临时导出图若不再使用，不得继续与 canonical 文件混放并被默认为有效版本。

正式图集合由 `figure-manifest.json` 决定，而不是仅靠文件名猜测。推荐从 `templates/figure-manifest.json` 建立项目级清单。

示例：

```json
{
  "figure_root": "outputs/figures",
  "canonical": [
    {"id": "fig:q1-shape", "file": "01_q1_shape_12.png", "source": "src/plot_q1.py"}
  ],
  "allowed_files": [],
  "trash_dir": "outputs/figures/.trash"
}
```

## 2. 白名单审计

对正式图目录执行集合核对：

```text
实际图文件
- canonical 文件
- 显式 allowed_files
= unexpected figure artifacts
```

必须同时检查：

- manifest 声明的 canonical 文件是否缺失；
- 是否存在未声明的旧图、语义别名或临时导出图；
- 非编号文件是否值得人工确认；
- 同一逻辑图是否存在多个近似名称版本；
- LaTeX/Markdown/脚本是否仍引用待清理文件。

文件名启发式只用于报警，**manifest 白名单才是正式事实源**。合法的非编号图可以显式进入 canonical/allowed 清单，不能只因未编号就自动删除。

可运行：

```bash
python scripts/audit_figure_outputs.py figure-manifest.json --project-root .
```

默认行为是 dry-run，不修改任何文件。

## 3. 安全清理

禁止直接 `rm` 正式图目录中的疑似旧文件。固定顺序：

```text
manifest 审计
→ dry-run 列出 unexpected files
→ 扫描引用
→ 人工/任务规则确认
→ 移入 .trash
→ 重新编译论文
→ 核对 PDF 与图引用
```

dry-run 会输出 `TRASH_PLAN_HASH`。只有在人工/任务规则确认 dry-run 结果后，携带同一计划哈希显式执行：

```bash
python scripts/audit_figure_outputs.py figure-manifest.json --project-root . --apply-trash --confirm-plan-hash <TRASH_PLAN_HASH>
```

才允许移动文件。脚本应拒绝移动仍被项目文本源引用的 unexpected 文件。`.trash` 是可恢复隔离区，不是正式图目录；脚本不得直接删除其中内容。

## 4. 何时必须执行

以下任务必须更新或核对 canonical manifest：

- 新增正式图；
- 重绘并替换正式图；
- 合并/拆分图导致图文件变化；
- 图文件改名；
- 删除语义别名或旧版本；
- 用户要求“整理 outputs/figures”“清理旧图”“只保留正式图”。

仅修改正文而完全未触及图文件时，不要求为了流程完整重新做图目录清理。

## 5. 完成条件

若本轮涉及正式图产物管理，完成时至少满足：

- canonical 文件全部存在；
- `outputs/figures` 中不存在未解释的 unexpected 图文件；
- 所有被移动到 `.trash` 的文件在移动前经过 dry-run；
- 仍被正文或脚本引用的文件没有被自动移动；
- LaTeX 当前主源重新编译后引用正常。

若 unexpected 文件仍存在，只能报告“待整理/待确认”，不能声称正式图目录已经唯一化。
