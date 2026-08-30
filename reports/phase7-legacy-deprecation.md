# Phase 7 Compatibility Split Report

## Decision

The original Phase 7 draft mixed an immutable historical baseline with an active
coordinator. Hardening corrected that design before commit:

- `legacy/huawei-cup-modeling-writing-v0.9.1/` is byte-identical to the
  `baseline-v0.9.1-writing` tag;
- `compat/huawei-cup-modeling/` is the independently versioned active router;
- no runtime responsibility or hook was added to the historical baseline.

## Routing

- The old entry name is preserved by the compat router.
- Paper construction routes to `huawei-cup-writing`.
- Audit routes to read-only `huawei-cup-review`.
- Analysis/Modeling, Coding/Visual, ledger mutation, and submission-state mutation
  return `BLOCKED_UNSUPPORTED_ROUTE` during Wave 1.
- Missing modular targets or Shared resources fail closed; Legacy is not a runtime
  fallback.

## Files Changed

- `compat/huawei-cup-modeling/SKILL.md`: narrow route-only workflow and boundaries.
- `compat/huawei-cup-modeling/manifest.yaml`: independent router contract and version.
- `compat/huawei-cup-modeling/agents/openai.yaml`: old-entry routing prompt.
- `tests/test_legacy_deprecation.py`: immutable-tag and router independence coverage.

## External Layer

This repository does not expose a separate External Layer directory that can be safely
dismantled in this wave. The Phase 1 ownership matrix already assigns the relevant
Reviewer Contract, consistency, evidence bridge, and benchmark responsibilities.
Phase 7 therefore records the boundary without mechanically moving unrelated Solver,
Modeling Library, or analysis/coding discovery assets.

## Removal Gate

The historical baseline is rollback-only and is not a removal candidate in this RC.
The compat router can evolve independently and its deletion would not change baseline
bytes.

## Verification

Verification results are refreshed after all Hardening changes; earlier Phase 7 staged
results are not release evidence.
