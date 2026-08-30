---
name: huawei-cup-modeling
description: This compatibility skill should be used when the user invokes the old "huawei-cup-modeling" entry, asks to route an existing Huawei Cup paper task, or needs the legacy entry mapped to the modular Writing or read-only Review skill. It does not contain modeling, writing, review, ledger, or submission-state rules.
---

# Huawei Cup Modeling Compatibility Router

## Goal

Preserve the old `huawei-cup-modeling` entry while routing only the supported Wave 1
paper tasks to the modular Skills.

## Routing

1. Classify the request without opening or mutating project artifacts.
2. Route manuscript construction, revision, polishing, abstract, conclusion, result
   discussion, or caption work to `$huawei-cup-writing`.
3. Route read-only manuscript, Claim-Evidence, style, LaTeX/PDF, or consistency audit
   work to `$huawei-cup-review`.
4. If a request contains both jobs, complete Writing first, freeze the candidate
   artifact, and then run Review read-only.
5. If the request is analysis/modeling, coding/visualization, solver feedback, ledger
   mutation, or submission-state mutation, return `BLOCKED_UNSUPPORTED_ROUTE`. Those
   capabilities are outside the Wave 1 router and must not fall back to Legacy rules.

## Boundaries

- Do not read policy from `legacy/`.
- Do not copy Writing, Review, or Shared rules into this router.
- Do not write artifacts, persist findings, update a ledger, or emit
  `READY_TO_SUBMIT`.
- Missing target Skills or Shared dependencies must fail closed.
- The immutable Legacy baseline is historical and rollback-only; it is not a runtime
  fallback.

The machine-readable routing and dependency contract is in `manifest.yaml`.
