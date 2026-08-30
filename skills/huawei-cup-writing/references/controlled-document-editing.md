# Controlled Document Editing

Normative rules: `FMT-001`–`FMT-005`, `FIG-002`, `FIG-003`, `REF-004`.

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

## Existing Manuscript

1. 定位唯一主编辑源及真实依赖；
2. 使用项目既有备份机制保护原源；
3. 只修改授权范围；
4. 不创建 `main_fixed.tex`、`final.tex` 或其他竞争主稿；
5. 编译或渲染当前主源；
6. 检查受影响页面和交叉引用；
7. 分页、浮动、编号、引用或图形影响外溢时扩大验证范围。

## New Working Draft

只有用户明确要求新建 LaTeX 且不存在可用模板时，才使用 `templates/latex/working-draft/main.tex`。该模板始终保持 `non_official_working_draft` 身份，不能冒充当届官方模板。

任何纯语言修改都必须保持受保护事实、公式、citation key、label/ref 和必要边界不变。
