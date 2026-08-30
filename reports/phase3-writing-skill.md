# Phase 3 Report

## Scope

Create an independently triggerable `huawei-cup-writing` Skill that constructs or revises Chinese mathematical-modeling papers from frozen evidence. This phase does not create the Review Skill, change Shared normative rules, modify Legacy, add a provider, or introduce a new workflow/submission state.

## Files Changed

```text
skills/huawei-cup-writing/
├── SKILL.md
├── manifest.yaml
├── agents/openai.yaml
├── references/
│   ├── abstract-writing.md
│   ├── anti-ai-rewriting.md
│   ├── anti-defensive-transformation.md
│   ├── argument-deepening.md
│   ├── conclusion-writing.md
│   ├── contribution-writing.md
│   ├── controlled-document-editing.md
│   ├── model-section-writing.md
│   ├── paragraph-construction.md
│   ├── prose-construction.md
│   └── result-discussion-writing.md
├── scripts/
│   └── validate_manuscript_mutation.py
├── templates/latex/working-draft/
│   ├── README.md
│   └── main.tex
└── tests/
    ├── test_writing_skill_contract.py
    └── writing-cases.yaml
```

No file under `legacy/` or `shared/` was modified.

## Ownership Changes

Writing now owns:

- paper content generation and revision procedures;
- abstract, model-section, result-discussion, contribution and conclusion construction;
- anti-defensive and anti-mechanical-language transformations;
- controlled manuscript editing after explicit user authorization;
- pre-delivery protection checks for numbers, formulas, citation keys, labels and references.

Writing does not own:

- model or algorithm selection;
- code, solver, data, experiment or canonical-result mutation;
- Shared normative definitions;
- finding severity or independent final audit;
- ledger, workflow or submission-state mutation.

## Contracts

### Trigger and identity

- Skill identifier: `huawei-cup-writing`;
- natural trigger phrases cover mathematical-modeling paper drafting, polishing, abstract rewriting, result-discussion deepening and anti-defensive/anti-mechanical-language revision;
- frontmatter, directory and manifest identities agree.

### Default permission

Default output is `content-only`. Project-file writes are permitted only for `micro-revision`, `revision`, or `full-paper` after explicit user authorization and authoritative-source resolution.

### Shared dependency

The Skill loads `../../shared/paper-quality-standard/README.md` and the relevant standard files. Writing references cite Shared Rule IDs but do not copy normative statements. Missing Shared paths fail package tests.

### Protected layers

```text
facts       → immutable by default
semantics   → may be narrowed or reorganized only with evidence
expression  → primary optimization target
```

### Mutation protector

`scripts/validate_manuscript_mutation.py` performs a read-only before/after comparison for UTF-8 `.txt`, `.md`, and `.tex` files. It compares multisets of:

- numeric literals;
- inline/display/equation formulas;
- citation keys;
- labels;
- references.

It exits `0` only when all protected elements are unchanged, `1` for detected mutation, and `2` for an unreadable or unsupported input.

## Tests

Command:

```text
D:\Obsidian Project\Math project\python\.venv\Scripts\python.exe -m pytest -q \
  skills/huawei-cup-writing/tests
```

Result: `PASS` — `13 passed in 0.54s`.

Validated:

- frontmatter identity and natural triggers;
- every manifest, Shared, reference, script and template path exists;
- no Legacy runtime dependency;
- no reviewer-state, finding, severity or submission-state logic;
- all referenced Rule IDs exist;
- no Shared normative statement is copied into Writing references;
- prose-only reorder keeps protected elements;
- number, formula, citation, label and reference mutations fail closed;
- mutation protector contains no project-file write path;
- fallback LaTeX files are byte-identical to the frozen Legacy source;
- the behavior catalog covers 5 normal, 4 resistance and 5 mutation cases.

The behavior catalog is explicitly `SPECIFICATION_ONLY_PENDING_PHASE6_EXECUTION`; it seeds later semantic Benchmark execution and is not presented as an LLM-quality result.

## Regression

Shared Contract tests:

```text
7 passed
```

Legacy regression:

```text
49 passed, 12 subtests passed
```

`git diff --check`: `PASS`.

Ruff on the new Python script and tests: `PASS`.

## Known Limitations

- Mutation protection currently supports UTF-8 text, Markdown and LaTeX; DOCX semantic comparison remains outside this script.
- Exact formula comparison is deliberately conservative and can reject harmless formula-format changes; such cases require explicit human review rather than silent acceptance.
- The current phase proves package integrity and protected-element behavior, not qualitative writing improvement on real papers.
- Project Facts and artifact schema integration remain later approved work.

## Risks

- A future prose procedure could restate a Shared rule. Contract tests must remain active as references evolve.
- Protected-element equality cannot detect every semantic change, especially altered causality or shifted scope with unchanged tokens; Shared Rule checks and later Review remain necessary.
- The bundled LaTeX template is a non-official working draft and must never be treated as a current competition template.

## Gate Decision

`PASS`

- Writing loads independently without Legacy.
- Core Writing behavior is separated from final audit behavior.
- Shared standards are referenced by Rule ID rather than duplicated.
- Protected elements fail closed under deterministic mutation tests.
- Legacy and Shared regressions remain clean.

## Next Allowed Phase

Phase 4 only: create the read-only `huawei-cup-review` Skill and its versioned evidence-backed finding contract after explicit user approval.
