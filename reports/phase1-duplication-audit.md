# Phase 1 Duplication Audit

## Scope

This report identifies normative rules, procedures, review behavior, state semantics, and tool behavior that are currently repeated or mixed across the Legacy package and relevant External Layer assets. It does not modify the baseline.

## Classification Method

Each cluster is separated into four possible layers:

1. **Normative standard** — what a valid paper or artifact must satisfy;
2. **Writing procedure** — how authorized prose construction moves toward that standard;
3. **Review policy** — how evidence-backed violations are diagnosed and reported;
4. **Legacy state/runtime** — routing, mutation authority, workflow, and submission status.

Text repeated only in `CHANGELOG.md`, historical design notes, or tests is not automatically a defect. It becomes drift risk when multiple runtime-loaded files independently define the same rule.

## Duplication Clusters

### D01 — Academic prose, AI-style risk, and defensive writing

**Current locations**

- `references/paper-prose-style.md` — current detailed authority;
- `references/paper-writing.md`;
- `references/paper-depth-visual-density.md`;
- `static/core/quality-gates.md`;
- `static/fragments/mode/{paper,audit}.md`;
- `static/fragments/stage/paper-writing.md`;
- `SKILL.md`, `manifest.yaml`, and `agents/openai.yaml`;
- `scripts/lint_paper_style.py` and its tests.

**Problem**

Normative rules, rewrite procedures, severity language, completion behavior, and trigger text are interleaved. The Writer is instructed to audit itself through the same language used by the Reviewer, which can produce defensive prose and role leakage.

**Authoritative resolution**

- Shared: rule statements and exceptions for prose, AI-style risk, defensive writing, terminology protection, and claim scope;
- Writing: classification and transformation procedures such as Positive Scope and Claim-forward;
- Review: evidence locators, categories, severity, resistance behavior, and empty-findings policy;
- Legacy: submission state only.

**Migration action:** `SPLIT`

### D02 — Result-discussion and argument-depth rules

**Current locations**

- `references/paper-depth-visual-density.md`;
- `references/result-visualization.md`;
- `references/model-construction.md`;
- `references/paper-writing.md`;
- `static/core/quality-gates.md`;
- `static/fragments/stage/{paper-writing,result-visualization,submission-audit}.md`.

**Problem**

The same expectation—phenomenon, quantitative evidence, explanation, and task meaning—is expressed as writing guidance, quality criteria, and audit failure language. Model-building procedure is also mixed with paper explanation standards.

**Authoritative resolution**

- Shared: `DEPTH-*` and `CLAIM-*` normative requirements;
- Writing: paragraph and section construction procedures;
- Review: evidence-backed depth findings;
- Future Analysis/Modeling: actual model selection, derivation, validation, and sensitivity execution.

**Migration action:** `SPLIT`

### D03 — Claim–Evidence and fact preservation

**Current locations**

- `static/core/execution-contract.md`;
- `static/core/consistency.md`;
- `static/core/quality-gates.md`;
- `references/paper-prose-style.md`;
- `references/paper-writing.md`;
- modeling ledger templates and validators;
- External `reviewer-result.schema.json`, `cross_artifact_consistency.py`, and `quality_evidence_bridge.py`.

**Problem**

Fact priority, claim scope, evidence requirements, workflow status, and report projection are treated as one broad concern. This makes it easy for a new module to accidentally become a ledger writer or second state system.

**Authoritative resolution**

- Shared Contracts: project facts, artifact identity, evidence locators, immutable fact fields, and claim-to-evidence links;
- Writing: read-only fact consumption and mutation-protection checks;
- Review: read-only mismatch/unsupported-claim findings;
- Legacy: workflow and submission-state mutation.

**Migration action:** `SPLIT`

### D04 — Master source, document target, and controlled write authority

**Current locations**

- `references/document-editing.md` — current detailed authority;
- `static/core/execution-contract.md`;
- `SKILL.md` completion gates;
- `manifest.yaml` document-target axis;
- `static/fragments/document-target/*`;
- `static/fragments/mode/{micro-revision,revision}.md`;
- `references/latex-pdf-layout-audit.md`.

**Problem**

The prohibition against parallel LaTeX sources and the source-selection algorithm are repeated in several always-loaded or routed files. Some repetition is a deliberate safety guard, but ownership is not separated between write permission and read-only validation.

**Authoritative resolution**

- Shared Contract: authoritative artifact identity and immutable write boundary;
- Writing: source selection, explicit authorization, backup, edit, compile, and scope escalation;
- Review: verify source identity and current-output evidence without editing;
- `SKILL.md`: retain only a short hard boundary, referencing the Contract.

**Migration action:** `SPLIT`

### D05 — Micro-revision workflow

**Current locations**

- `static/fragments/mode/micro-revision.md` — current procedural authority;
- `static/fragments/mode/revision.md`;
- `references/latex-pdf-layout-audit.md`;
- `static/core/execution-contract.md`;
- `SKILL.md`, `manifest.yaml`, validator logic, and regression tests.

**Problem**

The same admission and escalation rules appear in policy, routing, completion, layout audit, and tests. Review-specific validation is not clearly separated from Writer procedure.

**Authoritative resolution**

- Writing owns the editing procedure and scope escalation;
- Shared owns affected-artifact and evidence contracts;
- Review validates build/PDF evidence after the write;
- Legacy tests remain as regression until modular equivalents pass.

**Migration action:** `SPLIT`

### D06 — Canonical figure artifacts and cleanup

**Current locations**

- `references/figure-artifact-management.md` — current detailed authority;
- `references/result-visualization.md`;
- `static/core/execution-contract.md`;
- `SKILL.md` and `manifest.yaml`;
- `templates/figure-manifest.json`;
- `scripts/audit_figure_outputs.py` and tests.

**Problem**

The same tool contains both a read-only audit path and an explicitly mutating `--apply-trash` path. Moving it wholesale into Review would violate `writes_performed = []`.

**Authoritative resolution**

- Shared Contract: canonical figure schema and artifact identity;
- Review: pure inventory/reference findings only;
- Legacy or future Coding/Visual: explicitly authorized cleanup/mutation;
- split tests must prove Review cannot reach the mutation path.

**Migration action:** `SPLIT`

### D07 — LaTeX build and rendered-PDF evidence

**Current locations**

- `references/latex-pdf-layout-audit.md` — current detailed authority;
- `static/core/execution-contract.md`;
- `static/core/quality-gates.md`;
- `SKILL.md`, `agents/openai.yaml`, and `manifest.yaml`;
- `static/fragments/stage/{paper-writing,submission-audit}.md`;
- `scripts/audit_latex_build.py`, `validate_latex_review.py`, templates, and tests.

**Problem**

Compilation procedure, visual evidence requirements, submission gating, and Writer completion are repeated. A Writer currently transitions directly into final audit.

**Authoritative resolution**

- Shared: current-artifact identity, hash, page, and evidence coverage requirements;
- Writing: compile the authorized master source and hand artifacts off;
- Review: perform deterministic and visual-evidence validation;
- Legacy: decide whether legacy submission gates pass.

**Migration action:** `SPLIT`

### D08 — References and citation format

**Current locations**

- `references/reference-management.md` — current detailed authority;
- `references/paper-writing.md`;
- `static/core/quality-gates.md`;
- `static/fragments/stage/{paper-writing,submission-audit}.md`;
- `SKILL.md`, `manifest.yaml`, and agent prompt.

**Problem**

Authenticity, admissible sources, citation insertion procedure, format rules, and audit severity are partially repeated.

**Authoritative resolution**

- Shared: authenticity, traceability, source-policy, order, and formatting standards;
- Writing: evidence-first insertion and existing-key preservation;
- Review: citation/reference findings with locators;
- no module may fabricate bibliography metadata.

**Migration action:** `SPLIT`

### D09 — Submission state and quality-report semantics

**Current locations**

- `static/core/quality-gates.md` — current state authority;
- `static/fragments/stage/submission-audit.md`;
- `static/core/execution-contract.md`;
- `SKILL.md`, `manifest.yaml`, and paper/audit routes;
- `templates/quality-report.*`;
- `scripts/validate_quality_report.py` and tests;
- External Reviewer Contract status fields.

**Problem**

Legacy paper state and Reviewer call status both use words such as `PASS`, but they have different meanings. Copying quality-report logic into Review would create a second submission system.

**Authoritative resolution**

- Legacy alone owns `DRAFT`, `NEEDS_VALIDATION`, `BLOCKED`, and `READY_TO_SUBMIT`;
- Review owns finding severity and a call/contract status whose meaning remains `CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY`;
- Shared contains neither submission state nor reviewer severity.

**Migration action:** `KEEP_LEGACY` + versioned Review Contract

### D10 — Reviewer finding schema

**Current locations**

- External `schemas/reviewer-result.schema.json`;
- External `reviewer_contract.py`;
- External Reviewer reports and fault set;
- planned `shared/contracts/review-finding.schema.json` fields.

**Problem**

The plan proposes `rule_id`, `location`, and per-finding `limitations`, while Contract v1 uses `finding_id`, structured `evidence`, `verification_status`, and top-level `limitations`. Overwriting the v1 schema would break frozen tests and erase useful compatibility semantics.

**Authoritative resolution**

- keep Contract v1 unchanged as a Legacy/External baseline;
- introduce a versioned modular schema or explicit adapter;
- formal modular findings require a Shared `rule_id` and locatable evidence;
- retain `findings=[]`;
- evidence-free observations cannot be promoted to formal findings.

**Migration action:** `SPLIT` through versioning/adapter

### D11 — Package identity and trigger surface

**Current locations**

- container directory `huawei-cup-modeling-v090`;
- manifest version `0.9.1-writing`;
- frontmatter name `huawei-cup-modeling`;
- display name “稳健审计版”;
- plan labels `5_writing` and `6_review`.

**Problem**

Directory, version, frontmatter, display name, and target identifiers express different identities. Numeric underscore names also conflict with the local kebab-case naming convention.

**Authoritative resolution**

- Skill identifiers: `huawei-cup-writing`, `huawei-cup-review`;
- numeric `5`/`6` labels are display/order metadata only;
- Shared is package data, not an invokable Skill;
- Legacy retains its original identity for reproducibility.

**Migration action:** new identifiers; no Legacy rename

### D12 — Review read-only semantics versus report persistence

**Current locations**

- External Reviewer Contract requires `read_only=true` and `writes_performed=[]`;
- the plan refers to `review-report` output;
- several existing CLIs can write files only when explicitly applied;
- phase reports are repository-development artifacts.

**Problem**

If Review writes a report file itself, `writes_performed=[]` is no longer literal. If mutation-capable utilities are included, the read-only boundary becomes dependent on caller discipline.

**Authoritative resolution**

- Review runtime returns a structured result object and never persists it;
- an explicitly authorized coordinator may later persist the returned object;
- Phase reports in `reports/` are development records produced by Codex, not Review runtime outputs;
- mutation-capable CLI branches must remain outside Review.

**Migration action:** enforce in manifest, schema, scripts, and tests

## Duplicate Authority Summary

| Area | Current Detailed Authority | New Normative Authority | New Behavioral Owners |
|---|---|---|---|
| Academic prose | `paper-prose-style.md` | Shared `PROSE/AI/ADW/TERM` rules | Writing transformations; Review findings |
| Argument depth | `paper-depth-visual-density.md` + related files | Shared `DEPTH/CLAIM` rules | Writing construction; Review diagnosis |
| Citations | `reference-management.md` | Shared `REF` rules | Writing insertion; Review verification |
| Figures | `figure-artifact-management.md` + `result-visualization.md` | Shared `FIG` and artifact contracts | Writing captions; Review audit; future Coding/Visual mutation |
| Document source | `document-editing.md` | Shared artifact/write-boundary contract | Writing authorized edits; Review validation |
| PDF evidence | `latex-pdf-layout-audit.md` | Shared evidence contract | Review inspection; Legacy submission state |
| Facts/claims | `consistency.md` + ledger | Shared project-facts contract | Writing/Review read-only; Legacy mutation |
| Submission state | `quality-gates.md` | None in Shared | Legacy only |
| Reviewer result | External Contract v1 | Versioned Review schema referencing Shared Rule IDs | Review only |

## Tests Required to Prevent Re-Duplication

Phase 2 and later must add contract tests that fail when:

1. the same Rule ID has more than one normative definition;
2. Writing or Review copies a Shared normative statement instead of referencing its Rule ID;
3. Shared contains workflow, severity, submission state, or executable behavior;
4. Review exposes a mutation flag or writes a project/report artifact;
5. Writing imports reviewer severity/finding logic;
6. Writing or Review depends on Legacy to load its core role rules;
7. a referenced Shared path is missing;
8. frontmatter name and Skill directory identity drift;
9. Reviewer Contract v1 compatibility is silently broken;
10. `READY_TO_SUBMIT` appears in a new Writing or Review state definition.

## Known Limitations

- This phase establishes ownership and authority, not final Rule IDs or exact file boundaries.
- The External Reviewer fault set is specification-only; no provider has been admitted or executed.
- Qualitative Writing benchmark thresholds and independent adjudication remain Phase 6 design work.
- The first wave deliberately does not strengthen modeling-code execution; it prevents Writing/Review extraction from making that later work harder.

## Gate Decision

`PASS`

The main duplicate-rule clusters have a single planned normative owner and separate behavioral owners. No cluster requires copying an authoritative rule into both Writing and Review.

## Next Allowed Phase

Phase 2: extract Shared Paper Quality Standard after explicit user approval.
