# Number, Unit, and Precision Standard

## NUM-001 — 单位明确且全文一致

- **Normative Statement:** 物理量、参数、坐标轴、表格和正文中的单位必须明确，并在换算后保持全文一致；单位位置不得造成数值含义歧义。
- **Scope:** 公式、符号表、表格、图形、正文、摘要和结论。
- **Required Exceptions:** 无量纲量应按其定义明确表示或说明。
- **Relations:** `FIG-002`, `FIG-007`, `TERM-002`。

## NUM-002 — 报告精度匹配证据精度

- **Normative Statement:** 结果的小数位、有效数字和取整方式应匹配输入数据、测量或加工条件及实际决策需要；求解器容差和内部计算精度不得直接等同于物理结果报告精度。
- **Scope:** 数值结果、摘要、表格、图注和结论。
- **Required Exceptions:** 为复现实验保留的内部日志可以记录更高计算精度，但不得与正式报告值混淆。
- **Relations:** `FIG-007`, `CLAIM-002`。

## NUM-003 — 关键数字跨材料一致

- **Normative Statement:** 同一关键数值在结果来源、正文、图表、摘要和结论中必须保持数值、单位、版本和含义一致；由关键数值形成的排序、差异或选型判断也不能在不同材料中无说明地改变。
- **Scope:** 所有承载关键结果的材料。
- **Required Exceptions:** 明确区分计算值、取整值和工程选型值时可以同时出现，但必须说明关系。
- **Relations:** `ABS-002`, `CLAIM-002`, `FIG-004`。

## NUM-004 — 工程临界值说明裕量与取整

- **Normative Statement:** 工程临界值、阈值和选型值应区分理论计算、数值近似和实际采用值，必要时说明安全裕量与取整依据。
- **Scope:** 工程型建模结果和决策建议。
- **Required Exceptions:** 题目已明确固定取整规则时直接遵守该规则。
- **Relations:** `NUM-002`, `CLAIM-002`。
