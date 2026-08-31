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

Token fidelity 比较完整的 `command + optional args + required args`。例如
`\eqref{eq:a}` 与 `\ref{eq:a}`、`\citep[见]{foo}` 与 `\cite{foo}` 均不等价；
仅 citation key 或 reference target 相同不能通过。

推荐先把受保护 token 映射为不可编辑占位符，例如：

```text
\ref{fig:result} → ⟦REF_001⟧
\cite{source-a} → ⟦CITE_001⟧
$x+y=1$ → ⟦FORMULA_001⟧
```

完成自然语言改写后，再按映射原样恢复 token。不得从缩写或记忆重建 token。

## Evidence Modes and Derived Values

交付模式（如 `content-only`、`section-draft`）只决定输出载体和写回权限，不能决定数字是否可以计算。数字权限由任务的 `evidence_mode` 决定：

| `evidence_mode` | 适用任务 | 派生数字规则 |
|---|---|---|
| `frozen-rewrite` | 纯润色、冻结事实改写、已有结果的语言重组 | 默认不得新增差值、增幅、均值或其他派生量，即使能够由原文数字复算 |
| `evidence-backed-analysis` | 基于原始数据、结果表或已核验输出进行结果分析 | 可以计算任务需要的派生量，但必须保留数据来源、计算关系、单位和适用范围 |
| `modeling-or-computation` | 明确要求建模、求解或从输入数据生成结果 | 求解产生的新结果属于计算输出，必须有可追溯输入、模型或代码依据，并在进入论文正文前完成核验 |

在 `evidence-backed-analysis` 或 `modeling-or-computation` 模式下，加入差值、比例、百分点或其他派生量，至少需要满足：

1. 任务明确要求分析、计算、建模或求解，或当前模型目标本身要求该计算；
2. 原始数值、数据表、模型参数或程序输出及其含义可追溯；
3. 计算关系、单位和分母（如适用）无歧义；
4. 结果经过独立核算，且没有把估算、推测或未运行的结果写成已完成事实；
5. 需要跨模块复用时，将结果登记为可核验的结果证据；仅供当前段落使用时，至少在内部记录 `declared_derived_values` 及其来源。

在 `frozen-rewrite` 模式下，保留原始数字并使用非数值表达。不要把“可复算”自动解释为“已授权新增”；同样，也不要把该模式的限制推广到实际建模和结果分析任务。

### Examples

- 纯改写：材料写明误差由 `4.8%` 降至 `3.1%`，但未要求计算变化量。应保留这两个数字，不自行写入 `1.7`。
- 结果分析：用户要求比较下降幅度，且 `4.8%` 与 `3.1%` 的口径一致。可以计算并报告 `1.7` 个百分点，同时登记计算关系。
- 建模求解：用户提供数据、模型和求解任务。求解得到的目标值可以作为新结果，但必须保留求解输入和验证记录，不能凭空填入未运行的数值。

## Numeric Binding

数字 multiset 一致不能证明事实一致。Validator 会对显式局部绑定建立
`anchor → value` 映射，例如 `A=1`、`RMSE为0.1347`，并阻止同一 anchor 的数值
被交换。绑定出现顺序可以变化，`A=1，B=2` 改成 `B=2，A=1` 可以通过。

第一版绑定器只处理显式赋值或命名指标，不承担完整 NLP。若自然语言改写使显式
anchor 消失，validator 会继续依赖数字、完整 token 和 Project Facts；不得据此把
`PASS` 扩大解释为全文语义等价。

## Project Facts Priority

提供已通过 Shared validator 的 Project Facts 时，把文件传给
`--project-facts`。Validator 会读取 parameter 的 `id/symbol/meaning` 和 result
`id` 对应的 canonical value；输出中的显式绑定若与 canonical value 冲突，必须
FAIL。Project Facts 只读，validator 不创建、补写或回写该文件。

## Evidence-Limited Deepening

结果讨论需要深化但缺少机制证据时：

- 可以说明观察到的变化及其决策含义；
- 可以明确“现有证据不足以判断机制”；
- 证据缺口说明不能替代结果意义；仍应在证据范围内回答该变化如何对应当前指标、约束或子问题；
- 不得为了出现“原因”“机制”或“意味着”等词而补造解释；
- 在 `frozen-rewrite` 模式下，不得用新增派生数字制造分析深度；在其他模式下，派生数字仍须满足本文件的来源、计算和核验条件。

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
  --after-text '结果为 8.4，见图\ref{fig:result}。' `
  --project-facts project-facts.json
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
    "number_delta": {"added": [], "removed": []},
    "numeric_binding": {"conflicts": []},
    "project_facts_validation": {"status": "PASS", "conflicts": []}
  }
}
```
