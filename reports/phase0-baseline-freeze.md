# Phase 0 Baseline Freeze Report

## Scope

Freeze the local `0.9.1-writing` package as an immutable Legacy comparison point. No Writing, Review, Shared, External Layer, or runtime capability was migrated in this phase.

## Baseline

- Date: `2026-08-30`
- Source: `D:\Obsidian Project\Math project\skill\huawei-cup-modeling-stable-v0.9.1\huawei-cup-modeling-v090`
- Frozen copy: `legacy/huawei-cup-modeling-writing-v0.9.1`
- Manifest version: `0.9.1-writing`
- Baseline commit: `283757477b5f51a3e848e049e0c04f426ae3f725`
- Baseline files: `73`
- Remote operations: none

The source directory was not modified. Cache directories, bytecode, and test-run artifacts were deliberately excluded from the frozen Git baseline.

## Copy Integrity

Every copied file was compared with its source using SHA-256 before the baseline commit.

- Compared files: `73`
- Missing source files: `0`
- Hash mismatches: `0`

## Key SHA-256

| File | SHA-256 |
|---|---|
| `SKILL.md` | `a2bdd1bffc233c139f8f7dcc940fc84ad9f8cef92f629f05716cfcd99947ef46` |
| `manifest.yaml` | `31d4144aef085cb175059349d3436141f266bd7fc3aa733fd352c03047d92100` |
| `DESIGN.md` | `602cd2bdce83acd9f3b962494d6e2e0baa9dd6c73b5dc2a32f161d33075085c1` |
| `CHANGELOG.md` | `a454d3dafc8fbc813619f60eecfd21984ff0cf1d8fc1c007faa42b0feccd46bf` |
| `static/core/execution-contract.md` | `e95350639c48ad0868753ab1f6531b286d7af5e7a0592a517c9bfa576e14ee60` |
| `static/core/consistency.md` | `ae34648e0a8fcf9c90f86f2e1652ede867726ad57b70ba37a5e1c0d85ba407a0` |
| `static/core/quality-gates.md` | `e52a61addeb4fe635a294b3f583e847dfc6ad9a433c3bc3a733a005dfba4a263` |
| `references/paper-prose-style.md` | `e36defc7bb119b937f4f00ae515b0dc47effb3be7db6a0990e183c007f673783` |
| `scripts/lint_paper_style.py` | `f91176e05ea5e8f16914e455f9379bd42aa8084f9a771447f36aa8f3816de3fe` |
| `templates/modeling-ledger.json` | `394be82c1f57c584d48a2e271293eb036eaba7a3d6fa32488a7949607d66e394` |
| `assets/sample-papers/C24104220149.pdf` | `382bde4b71f57eae705347767120aa58b2d993ae090d71cdf246d0e13d6bf871` |

## Validation

### Package paths

```text
python legacy/huawei-cup-modeling-writing-v0.9.1/scripts/validate_package.py \
  legacy/huawei-cup-modeling-writing-v0.9.1
```

Result: `PASS` — all `57` referenced manifest paths exist.

### Regression tests

The system Python did not contain `pytest`, so no package was installed globally. The established project environment was used instead:

```text
D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m pytest -q \
  legacy/huawei-cup-modeling-writing-v0.9.1
```

Result: `PASS` — `49 passed, 12 subtests passed in 11.58s`.

## Known Limitations

- The original containing directory is named `huawei-cup-modeling-v090`, while its manifest version is `0.9.1-writing`; the frozen destination uses the manifest identity without renaming internal files.
- The current tests mainly cover policy routing, validators, style linting, artifact checks, and document QA. They do not establish strong modeling-code generation capability.
- No remote repository was configured or contacted from this local Git repository.

## Gate Decision

`PASS`

The Legacy baseline is reproducible, internally path-complete, test-clean in the project environment, and recoverable from the baseline commit. Phase 1 may proceed without modifying the frozen copy.

## Next Allowed Phase

Phase 1 only: asset inventory, ownership assignment, and duplication audit.
