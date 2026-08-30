# Real-paper A/B: wine evaluation paper

## Scope

This case validates the RC against one complete, real Chinese mathematical-modeling
paper without modifying the source project. The paper contains four modeling
questions, equations, citations, cross-references, tables, figures, an appendix,
and an existing human-oriented remediation record.

- Source project: `D:/Obsidian Project/Math project/4_培训/8_葡萄酒的评价/LaTeX论文`
- Legacy input: `Demo.tex.bak_20260824_122231`
- Legacy 0.9.1-writing output: `Demo.tex`
- Current PDF: `Demo.pdf`
- Source input SHA-256: `7DCC7FF936EE6B0BA8A510786EE3ACA3765231A8885133FAB022A4D28F381D4E`
- Legacy output SHA-256: `670D087764EA1D595718E1453F48D6245C3D630D164826E6179EB4A9B07B57DF`
- Current PDF SHA-256: `04CB88C07B5272C3FE1F85C2C35D7CC0EA4EC038E977FEF74E0EF6EE27431E39`
- Current PDF page count: 36

The external files are evidence only. No source, PDF, audit record, or figure was
written by this benchmark.

## Design

`A` is the complete manuscript produced under the immutable Legacy workflow.
`B` is a paired, content-only modular pass over A: New Writing proposes five
minimal replacements, New Review checks them read-only, and Writing would retain
or revise them only if a supported finding exists. The full manuscript was
reviewed; the modular pass deliberately does not rewrite paragraphs that already
meet the Shared rules.

This is therefore a full-document review plus a targeted paired revision, not a
claim that every sentence was regenerated. Exact replacement records are in
`ab-records.md`.

## Deterministic evidence

- Mutation Protector: all five proposed replacements returned `PASS`.
- Number delta: zero additions and zero removals in all five records.
- Formula, citation, label, and reference token delta: zero in all five records.
- Review contract tests after the real-paper repair: 17 passed.
- Figure audit before repair: 38 candidate warnings, dominated by nested
  `subfigure` false positives.
- Figure audit after repair: 2 candidate warnings. Both are adjacent paired
  figures described collectively as “两幅图”; they were not admitted as formal
  findings because `FIG-003` does not require one explicit `\\ref` token per
  child or sibling figure.
- Current PDF: all 36 pages were freshly rendered at 110 dpi and inspected as six
  contact sheets. No clipping, overlap, broken glyph, unreadable table, or missing
  page was observed.
- Existing `audit/latex-review.json` is stale: it records a different SHA-256 and
  38 pages. It cannot support the current PDF and is recorded as a `FMT-003`
  limitation rather than silently reused.

## Gate result

Automated and agent-executed RC gate: `PASS_WITH_HUMAN_ADJUDICATION_PENDING`.

The modular pass preserved all checked facts and improved five sentence
boundaries without removing limitations or negative results. User adjudication
then identified two Review false negatives: paragraph-final “未通过／未包含”
formulations in AB-03 and AB-04. A full-paper rescan found the same negative-only
definition in AB-05. All three are now recorded and repaired by stating the
decision rule, model dependence, or validation level affirmatively. No formula, citation,
reference token, or number changed. Review false-positive and false-negative
behavior found by the real paper is regression-tested.

Stable v1.0 is not declared by this case alone. AB-03, AB-04, and AB-05 passed
user adjudication. AB-01 and AB-02 remain `PENDING_USER_REVIEW`; until the user
completes them, the suite remains `1.0.0-rc1`.
