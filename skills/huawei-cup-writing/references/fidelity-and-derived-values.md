# Fidelity and Derived Values

Normative rules: `CLAIM-001`, `CLAIM-002`, `NUM-002`, `NUM-003`, `TERM-002`.

## Fidelity Lock

改写现有文本前，先建立不可重写 token 清单：

- 完整 LaTeX citation command，包括 command、可选参数和全部 citation keys；
- 完整 `\label{...}` 与 `\ref{...}`、`\eqref{...}`、`\autoref{...}`、`\cref{...}` token；
- 公式及其数学含义；
- 原文数字、百分数、单位和精度；
- 已声明必须逐字保留的专业术语、方案名和 artifact identifier。

这些 token 必须原样搬运，不能凭记忆重新输入，不能缩短 key，也不能把 `\ref{fig:result}` 改写成 `\ref{fig}`。只重写 token 之间的自然语言。

推荐先把受保护 token 映射为不可编辑占位符，例如：

```text
\ref{fig:result} → ⟦REF_001⟧
\cite{source-a} → ⟦CITE_001⟧
$x+y=1$ → ⟦FORMULA_001⟧
```

完成自然语言改写后，再按映射原样恢复 token。不得从缩写或记忆重建 token。

## Derived Values

默认模式不新增数字，即使该数字能由原文数值直接计算得到。

只有同时满足以下条件，才允许加入差值、比例、百分点或其他派生量：

1. 用户、Project Facts 或当前任务契约明确允许；
2. 原始数值及其含义已经可追溯；
3. 计算关系无歧义；
4. 输出明确说明它是由哪些数值计算得到的；
5. 派生量被列入本轮 `declared_derived_values`，并通过单独核算。

未满足时，保留原始数字并使用非数值表达。禁止把“可复算”自动解释为“已授权新增”。

## Evidence-Limited Deepening

结果讨论需要深化但缺少机制证据时：

- 可以说明观察到的变化及其决策含义；
- 可以明确“现有证据不足以判断机制”；
- 证据缺口说明不能替代结果意义；仍应在证据范围内回答该变化如何对应当前指标、约束或子问题；
- 不得为了出现“原因”“机制”或“意味着”等词而补造解释；
- 不得用新增派生数字制造分析深度。

## Final Check

完成改写后按以下顺序检查：

1. citation、label、reference 和公式 token 是否逐字符一致；
2. 原数字是否完整保留，新增数字是否全部得到显式授权；
3. 必要范围、真实局限和负面证据是否在语义上保留；
4. 深化内容是否来自已有证据，或被明确标为证据缺口。

## Mandatory Validation Gate

只要存在改写前文本，就必须在返回正文前运行 mutation protector。可以不创建临时文件，直接传入文本参数：

```powershell
python scripts/validate_manuscript_mutation.py `
  --before-text '图\ref{fig:result}显示结果为 8.4。' `
  --after-text '结果为 8.4，见图\ref{fig:result}。'
```

- `status=PASS`：才允许返回改写正文；
- `status=FAIL`：根据 `changes` 与 `number_delta` 修复后重新校验；
- 无法运行 validator：不得声称通过，返回 `fidelity_validation.status=NOT_RUN` 并保留原文，不输出未经验证的改写。

每项改写输出同时报告：

```json
{
  "declared_derived_values": [],
  "fidelity_validation": {
    "status": "PASS",
    "changes": {},
    "number_delta": {"added": [], "removed": []}
  }
}
```
