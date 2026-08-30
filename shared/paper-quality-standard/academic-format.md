# Academic Format Standard

## FMT-001 — 提交格式服从当前权威要求

- **Normative Statement:** 最终提交格式应服从当届官方规范；来源不明、上一届或自制模板不能被表述为当前官方模板。
- **Scope:** 候选终稿和提交文档。
- **Required Exceptions:** 工作稿可以使用非官方模板，但必须保持其非提交身份可辨识。
- **Relations:** `FMT-002`, `REF-004`。

## FMT-002 — 唯一主编辑源可识别

- **Normative Statement:** 论文应具有唯一可识别的主编辑源及其真实依赖，不应存在多个未说明关系的平行主稿竞争同一最终输出。
- **Scope:** LaTeX、DOCX、Markdown 或其他可编辑论文源。
- **Required Exceptions:** 备份和明确标记的历史快照不属于当前主编辑源。
- **Relations:** `FMT-001`, `FMT-003`。

## FMT-003 — 最终输出与当前源一致

- **Normative Statement:** 用于交付或判断的 PDF/DOCX 必须由当前主编辑源和当前依赖生成；旧输出、旧截图和旧哈希不能证明修改后的文档状态。
- **Scope:** 候选终稿、交付稿和相关证据。
- **Required Exceptions:** 纯内容交付不产生正式排版文件时不适用。
- **Relations:** `FIG-006`, `FMT-004`。

## FMT-004 — 编译成功不等于版面合格

- **Normative Statement:** 正式 LaTeX 文档除成功编译外，还应以当前 PDF 为对象检查引用、溢出、浮动、分页、裁切、异常空白和图表可读性。
- **Scope:** LaTeX 候选终稿。
- **Required Exceptions:** 不涉及正式排版输出的纯内容任务不适用。
- **Relations:** `FIG-002`, `FIG-003`, `FMT-003`。

## FMT-005 — 模板内部约定保持一致

- **Normative Statement:** 正文列表、编号、图表、公式和参考文献格式应服从当前模板已有约定，不得为局部偏好引入与模板冲突的第二套样式体系。
- **Scope:** 使用既有模板的论文。
- **Required Exceptions:** 官方规范明确要求修正现有模板冲突时，以官方规范为准。
- **Relations:** `FMT-001`, `REF-004`。
