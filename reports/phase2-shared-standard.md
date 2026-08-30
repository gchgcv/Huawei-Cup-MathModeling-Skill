# Phase 2 Report

## Scope

Extract the single normative paper-quality source shared by the future modular Skills. This phase does not create either Skill, migrate runtime scripts, change Legacy policy, introduce a provider, or define a new workflow/submission state.

## Files Changed

Created:

```text
shared/paper-quality-standard/
├── README.md
├── abstract-standard.md
├── academic-format.md
├── academic-prose.md
├── anti-ai-style.md
├── anti-defensive-writing.md
├── argument-depth.md
├── claim-evidence.md
├── figure-table-standard.md
├── number-unit-precision.md
├── reference-standard.md
├── section-structure.md
└── terminology.md

tests/test_shared_paper_quality_standard.py
```

No file under `legacy/` was modified.

## Ownership Changes

The new Shared Standard is now the planned authoritative source for what a qualified paper must satisfy in these domains:

| Prefix | Rules | Domain |
|---|---:|---|
| `PROSE` | 5 | Chinese academic prose |
| `AI` | 6 | Observable mechanical-language risks |
| `ADW` | 6 | Defensive writing, scope and uncertainty |
| `DEPTH` | 5 | Model explanation and result-discussion depth |
| `CLAIM` | 6 | Claim–Evidence and extrapolation boundaries |
| `ABS` | 5 | Abstract quality |
| `STRUCT` | 5 | Section and paragraph structure |
| `FIG` | 7 | Figures and tables |
| `FMT` | 5 | Document and format integrity |
| `NUM` | 4 | Numbers, units and precision |
| `TERM` | 4 | Terminology and symbol semantics |
| `REF` | 5 | References and citations |

Total: `63` normative rules.

The standard does not own:

- prose generation or rewriting procedures;
- finding generation, severity, or report persistence;
- file mutation or cleanup;
- workflow, ledger mutation, or submission status;
- model selection, code execution, solver behavior, or experiments.

## Contracts

Every formal rule has exactly one:

```text
Rule ID
Normative Statement
Scope
Required Exceptions
Relations
```

Rule IDs use the prefixes registered in `README.md`. Rule relations must resolve to an existing Rule ID. The standard is package data and intentionally contains no `SKILL.md`, `manifest.yaml`, or `scripts/` directory.

The Contract tests prohibit role/runtime/submission fields such as `READY_TO_SUBMIT`, `writes_performed`, `submission_status`, severity policy, workflow state, and invokable runtime content from entering normative rule files.

## Source Extraction

The rules were extracted from the frozen Legacy authorities identified in Phase 1, primarily:

- `references/paper-prose-style.md`;
- `references/paper-writing.md`;
- `references/paper-depth-visual-density.md`;
- `references/result-visualization.md`;
- `references/reference-management.md`;
- `references/document-editing.md`;
- `references/latex-pdf-layout-audit.md`;
- `references/model-construction.md`;
- `static/core/consistency.md`;
- `static/core/quality-gates.md`.

Procedural and severity language was not copied into the Shared rules. Legacy remains unchanged as the comparison baseline.

## Tests

Command:

```text
D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m pytest -q \
  tests/test_shared_paper_quality_standard.py
```

Result: `PASS` — `7 passed in 0.03s`.

Validated:

- expected registry files exist;
- every Rule ID is unique;
- no normative statement is duplicated;
- Rule ID prefix matches its authoritative file;
- every rule has the complete normative shape;
- every related Rule ID exists;
- rule files contain no role/runtime/submission state;
- Shared Standard is not an invokable Skill or runtime.

## Regression

Command:

```text
D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m pytest -q \
  legacy/huawei-cup-modeling-writing-v0.9.1
```

Result: `PASS` — `49 passed, 12 subtests passed in 11.00s`.

`git diff --check`: `PASS`.

## Known Limitations

- Rule IDs are structurally validated but have not yet been exercised through the modular Writing and Review behaviors.
- Qualitative Benchmark adjudication remains future work; the current tests prove integrity, not paper-quality gains.
- Shared project facts, artifact schemas, and the versioned Reviewer finding schema belong to later approved phases.
- The first wave still does not strengthen modeling-code execution; this phase only creates the stable paper-standard layer.

## Risks

- Later Skill files could restate normative rules instead of referencing Rule IDs. Contract tests must be extended when those Skills are created.
- A rule may require refinement after real-paper Benchmark evaluation. Existing IDs should be preserved and semantics changed only with a documented compatibility decision.
- Format and artifact rules are currently normative paper requirements; mutation authority must remain outside Shared when corresponding tools are migrated.

## Gate Decision

`PASS`

- Each normative rule has one authoritative definition.
- All Rule IDs and relations are structurally valid.
- Shared contains no generation procedure, review severity, workflow, runtime, or submission state.
- Legacy regression is unchanged.

## Next Allowed Phase

Phase 3 only: create `skills/huawei-cup-writing` and reference Shared Rule IDs without copying normative statements. Phase 3 requires explicit user approval.
