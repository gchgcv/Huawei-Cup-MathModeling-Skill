# Paired A/B records

All records use the complete Legacy output as A. `AB-03` and `AB-04` retain the
first Writing candidate so the user-identified Review false negatives remain
traceable; their final versions apply the subsequent `ADW-003` repair.
`declared_derived_values` is empty for every record.

## AB-01 - abstract information density

- Location: `Demo.tex:30`
- Rule IDs: `PROSE-003`, `ABS-001`, `ABS-005`
- Original / Legacy A:

  > 针对问题一，利用混合效应模型、配对检验、ICC 和 Kendall 协调系数考察评委组间差异与组内评分一致性。两类葡萄酒均未出现稳定的统一组间偏移；红葡萄酒的质量代理较稳定，白葡萄酒的质量代理随评委组变化。针对问题二，在不将质量代理纳入聚类特征的条件下，采用 PCA--Ward 方法进行酒型内分级，并结合重采样稳定性和独立质量代理选择等级数，得到红葡萄酒二级、白葡萄酒三级的样本内分级结果。
- Writing output:

  > 针对问题一，利用混合效应模型、配对检验、ICC 和 Kendall 协调系数考察评委组间差异与组内评分一致性。两类葡萄酒均未出现稳定的统一组间偏移。红葡萄酒的质量代理较稳定，白葡萄酒的质量代理随评委组变化。针对问题二，在不将质量代理纳入聚类特征的条件下，采用 PCA--Ward 方法进行酒型内分级，并结合重采样稳定性和独立质量代理选择等级数，得到红葡萄酒二级、白葡萄酒三级的样本内分级结果。
- Review finding: none admitted; the split preserves the question-method-result mapping.
- Final version: same as Writing output.
- Fidelity validation: `PASS`; number/token delta empty.
- Human adjudication: `PENDING_USER_REVIEW`.

## AB-02 - weak predictive result

- Location: `Demo.tex:643`
- Rule IDs: `PROSE-003`, `DEPTH-005`, `CLAIM-006`
- Original / Legacy A:

  > 红葡萄酒的等权 LOOCV 标准化 RMSEY 为 $0.980$，等权 $Q^2_Y$ 为 $0.025$，整体样本外增益较小；白葡萄酒的对应值为 $0.899$ 和 $0.173$。置换检验的经验 $p$ 值分别为 $0.006$ 和 $0.002$，表示在固定成分数和相同 LOOCV 协议下，观测到的等权 $Q^2_Y$ 位于置换零分布的较端位置。如图~\ref{fig:q3_scores} 所示，红葡萄酒在一个潜变量上的展开已承担主要协方差信息，白葡萄酒则需要第二个潜变量补充样本差异。图中的相邻点表示理化和感官响应的联合模式接近，交叉验证指标对应整体预测表现。
- Writing output:

  > 红葡萄酒的等权 LOOCV 标准化 RMSEY 为 $0.980$，等权 $Q^2_Y$ 为 $0.025$，整体样本外增益较小。白葡萄酒的对应值为 $0.899$ 和 $0.173$。置换检验的经验 $p$ 值分别为 $0.006$ 和 $0.002$。在固定成分数和相同 LOOCV 协议下，观测到的等权 $Q^2_Y$ 位于置换零分布的较端位置。如图~\ref{fig:q3_scores} 所示，红葡萄酒在一个潜变量上的展开已承担主要协方差信息，白葡萄酒则需要第二个潜变量补充样本差异。图中的相邻点表示理化和感官响应的联合模式接近，交叉验证指标对应整体预测表现。
- Review finding: none admitted; the weak result and protocol boundary remain explicit.
- Final version: same as Writing output.
- Fidelity validation: `PASS`; six numeric values, eight inline formula tokens, and `\ref{fig:q3_scores}` are unchanged.
- Human adjudication: `PENDING_USER_REVIEW`.

## AB-03 - model-dependent aromatic increment

- Location: `Demo.tex:748`
- Rule IDs: `PROSE-003`, `DEPTH-005`, `CLAIM-006`
- Original / Legacy A:

  > 红葡萄酒中，D 块的 Elastic Net 相对均值基线把 RMSE 从 $7.507$ 降至 $6.232$，交叉验证决定系数为 $0.257$；按预设判定标准，芳香物质提供辅助性预测增量，其作用定位为信息补充。白葡萄酒的最佳 PLS 也选择 D 块，但芳香物质增量未满足稳定增量条件；采用第 2 评委组质量代理后，跨评委组的稳定增量判定仍未通过。
- Writing output:

  > 红葡萄酒中，D 块的 Elastic Net 相对均值基线把 RMSE 从 $7.507$ 降至 $6.232$，交叉验证决定系数为 $0.257$。按预设判定标准，芳香物质提供辅助性预测增量，其作用定位为信息补充。白葡萄酒的最佳 PLS 也选择 D 块，但芳香物质增量未满足稳定增量条件。采用第 2 评委组质量代理后，跨评委组的稳定增量判定仍未通过。
- Review finding: `P2 / ADW-003`. The candidate preserves the facts but ends two consecutive judgments with “未满足／未通过”, defining the result mainly by failure. Retain the negative evidence and state the positive evidence boundary.
- Final version:

  > 红葡萄酒中，D 块的 Elastic Net 相对均值基线把 RMSE 从 $7.507$ 降至 $6.232$，交叉验证决定系数为 $0.257$。按预设判定标准，芳香物质为红葡萄酒提供辅助性预测信息。白葡萄酒的最佳 PLS 也选择 D 块，但 PLS 与 Elastic Net 对芳香物质增量的判断方向不同。采用第 2 评委组质量代理后，不同模型给出的增量方向仍不一致。白葡萄酒的结果反映的是当前模型和评委组条件下的预测变化。
- Fidelity validation: `PASS`; four numeric values and three formula tokens are unchanged.
- Human adjudication: `PASS_USER_APPROVED_2026-08-30`.

## AB-04 - limitations and external validity

- Location: `Demo.tex:881`
- Rule IDs: `PROSE-003`, `ADW-002`, `CLAIM-001`
- Original / Legacy A:

  > 当前数据规模较小，问题三的 $X$ 特征数为 53，而酒型内样本数为 27 或 28；置换检验的经验 $p$ 值反映当前样本和验证协议下的结果，外部泛化能力需由独立样本检验。问题一中的白葡萄酒组间排序一致性较弱，问题二中的聚类分离度也不高，白葡萄酒质量代理需要新增样本或独立评委数据复核。问题四的验证协议包含嵌套交叉验证，未包含独立外部测试。
- Writing output:

  > 当前数据规模较小，问题三的 $X$ 特征数为 53，而酒型内样本数为 27 或 28。置换检验的经验 $p$ 值反映当前样本和验证协议下的结果，外部泛化能力需由独立样本检验。问题一中的白葡萄酒组间排序一致性较弱，问题二中的聚类分离度也不高，白葡萄酒质量代理需要新增样本或独立评委数据复核。问题四的验证协议包含嵌套交叉验证，未包含独立外部测试。
- Review finding: `P2 / ADW-003`. “未包含独立外部测试” is a necessary boundary expressed as a paragraph-final exclusion. State the current validation level affirmatively while retaining external-validity limits.
- Final version:

  > 当前数据规模较小，问题三的 $X$ 特征数为 53，而酒型内样本数为 27 或 28。置换检验的经验 $p$ 值反映当前样本和验证协议下的结果，外部泛化能力需由独立样本检验。问题一中的白葡萄酒组间排序一致性较弱，问题二中的聚类分离度也不高，白葡萄酒质量代理需要新增样本或独立评委数据复核。当前结果反映模型在内部交叉验证下的表现，外部泛化能力还需在独立样本上进一步检验。
- Fidelity validation: `PASS`; three numeric values and `$X$` / `$p$` are unchanged.
- Human adjudication: `PASS_USER_APPROVED_2026-08-30`.

## AB-05 - stable-increment decision rule

- Location: `Demo.tex:726`
- Rule IDs: `ADW-003`, `CLAIM-006`, `DEPTH-005`
- Original / Legacy A:

  > 正的 $\Delta\mathrm{RMSE}$ 表示加入信息块后误差下降；任一模型未改善，或质量代理改变后方向反转时，结果记为未形成稳定增量。
- Writing output: same as Legacy A; the initial pass retained the rule but missed its negative-only ending.
- Review finding: `P2 / ADW-003`. The sentence defines the category only through failure conditions. Preserve the decision rule and state affirmatively which evidence receives the stable-increment label.
- Final version:

  > 正的 $\Delta\mathrm{RMSE}$ 表示加入信息块后误差下降。稳定增量要求 PLS 与 Elastic Net 的结果同时改善。此外，更换质量代理后，增量方向应保持一致。
- Fidelity validation: `PASS`; `$\Delta\mathrm{RMSE}$` is unchanged and no number is added or removed.
- Human adjudication: `PASS_USER_APPROVED_2026-08-30`.

## Full-paper dimension adjudication

| Dimension | A observation | B observation | RC adjudication |
|---|---|---|---|
| Chinese academic prose | Mature but several dense sentence boundaries | Four boundaries split without paraphrasing facts | pass |
| AI-template style | No formal work-log or empty-transition finding | No new template phrase introduced | pass |
| Defensive writing | Real limitations are explicit but three paragraphs use negative-only endings | `ADW-003` repair positively states the decision rule, model dependence, and validation level | pending user review |
| Work-log narrative | Not observed in sampled core sections | Not introduced | pass |
| Argument depth | Methods, values, validation, and limitations coexist | No depth removed | pass |
| Result analysis | Includes weak and model-dependent results | Negative evidence retained | pass |
| Abstract density | Four questions covered | Q1 contrast made easier to scan | pass |
| Figure explanation | Figures receive nearby interpretation | No figure interpretation altered | pass |
| Claim-Evidence | Existing claims point to values, protocols, and figures | Relations unchanged | pass |
| Numeric fidelity | Baseline evidence frozen | Zero numeric delta in all records | pass |
| Formula fidelity | Baseline evidence frozen | Zero formula-token delta | pass |
| Citation fidelity | Baseline evidence frozen | Zero citation-token delta | pass |
| Review false positives | 38 deterministic candidates before auditor repair | 2 non-admitted candidates after repair | pass |
| Review false negatives | User confirmed misses in AB-03 and AB-04; the same pattern also affected AB-05 | All three are recorded and repaired under `ADW-003` | repaired; pending user recheck |
| Cross-section consistency | Existing abstract/body/conclusion values were inspected | No cross-section fact changed | pass |
