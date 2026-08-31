# Paper Artifact Contract

## Purpose

Paper Artifact Contract 用于标识事实来自哪个 artifact、位于何处，以及在需要 freshness 判断时对应哪个内容版本。它不授予修改权限。

## Minimal artifact reference

```yaml
artifact_id: paper-main
kind: paper
path: paper/main.tex
authority: authoritative
sha256: optional-64-hex-content-hash
```

字段约束：

- `artifact_id`：项目内稳定且唯一的 ID；跨文件引用使用该 ID，不使用模糊文件名。
- `kind`：`problem`、`paper`、`pdf`、`code`、`result`、`figure`、`table`、`citation`、`context` 或 `project_facts`。
- `path`：项目内可解析位置；路径存在本身不证明内容最新。
- `authority`：`authoritative`、`derived` 或 `reference`。同一职责只能声明一个 authoritative artifact。
- `sha256`：当判断 PDF、图形或结果是否与当前源一致时必须提供；未知时留空并报告 limitation，不得猜 hash。

Project Facts 中的 `sources` 进一步记录：

```yaml
id: source-result-1
artifact_id: result-json
locator: $.metrics.objective
sha256: optional-64-hex-content-hash
```

## Invariants

- source 必须同时给出 `artifact_id` 和可定位的 `locator`。
- `sha256` 不匹配时，旧证据不得当作当前 artifact 的证据。
- derived artifact 不得覆盖其 authoritative source 的事实地位。
- Writing 和 Review 只能读取 artifact reference；本 Contract 不授权 patch、rename、delete、ledger update 或 report persistence。
- 缺失、冲突或多重 authoritative 声明必须显式暴露，不能按文件时间或名称自动猜选。
