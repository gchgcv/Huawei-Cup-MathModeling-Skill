# Huawei Cup Modeling Skills Suite v1.0.0-rc1 Release Evidence

## Status

`RC_READY_HUMAN_ADJUDICATION_PENDING`

The hardening implementation and automated RC gates are complete. Stable v1.0 is
not declared because the real-paper record still requires user adjudication.

## Required Evidence

- Commit: the commit targeted by local tag `v1.0.0-rc1`
- Tag: local annotated tag `v1.0.0-rc1`
- Suite validation: `PASS`, suite version `1.0.0-rc1`
- Full tests: `162 passed, 12 subtests passed`
- Python compile check: `PASS`
- Ruff check: `PASS`
- Synthetic benchmark: `EXECUTED`, automated admission `PASS`, independent adjudication `PASS`
- Real-paper A/B: `PASS_WITH_HUMAN_ADJUDICATION_PENDING`
- Real-paper evidence: `benchmark/real-paper/wine-evaluation/`
- Current PDF visual review: 36/36 pages freshly rendered and inspected
- Distribution ZIP: generated only from local tag `v1.0.0-rc1`
- SHA-256: authoritative sibling `.sha256` file generated with the ZIP

## Known Limitations

- RC status does not imply stable release.
- Synthetic benchmark remains a regression layer, not real-paper validation.
- The real-paper benchmark uses a complete paper plus targeted paired revisions;
  it does not claim that every sentence was regenerated.
- The paper project's earlier `latex-review.json` is stale for the current PDF;
  current visual evidence is recorded in the RC real-paper report, not written
  back to the external source project.
- Stable release requires the user to complete the two remaining human
  adjudication fields; AB-03, AB-04, and AB-05 passed on 2026-08-30.
