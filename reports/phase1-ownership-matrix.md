# Phase 1 Ownership Matrix

## Scope

This phase assigns ownership for the `0.9.1-writing` Legacy package and the relevant read-only Reviewer assets in the existing External Layer. It does not migrate, delete, rename, or rewrite any capability.

## Binding Ownership Rules

- **Shared** defines normative paper standards, artifact schemas, and fact contracts. It has no workflow, runtime role, severity policy, submission state, or mutation permission.
- **Writing** constructs or revises paper content from frozen, traceable evidence. It may modify an authoritative manuscript only after explicit user authorization. It cannot change model facts, code results, canonical values, or submission state.
- **Review** reads artifacts and returns evidence-backed structured findings. It does not persist reports, patch artifacts, move files, update ledgers, or change submission state. Persistence, if later requested, belongs to an authorized coordinator outside Review.
- **Legacy Coordinator** remains the sole owner of `fresh/handoff`, workflow status, legacy ledger compatibility, quality-report state, and `READY_TO_SUBMIT` during the first modularization wave.
- **Benchmark** measures Writing and Review behavior. Benchmark success is not paper-quality or submission approval.

## Target Package Contract

The numeric labels are display order, not Skill identifiers.

```text
Huawei-Cup-MarhModeling-Skill-v1.0/
├── skills/
│   ├── huawei-cup-writing/
│   └── huawei-cup-review/
├── shared/
├── benchmark/
└── legacy/
```

`shared/` is a package resource, not a third Skill. The two Skills must be independently triggerable but installed and versioned with the same package. Missing Shared resources must fail closed. Relative paths and Rule IDs will be checked by contract tests before admission.

## Legacy Package Assets

| Asset | Current Path | Responsibility | New Owner | Shared? | Mutation Permission | Migration Action | Notes |
|---|---|---|---|---|---|---|---|
| Main Skill router | `SKILL.md` | Full workflow routing and completion gates | Legacy Coordinator | No | Legacy policy only | `KEEP_LEGACY` | Do not reuse as a new modular Skill. Later reduce to compatibility hooks only after admission. |
| Routing manifest | `manifest.yaml` | Entry, mode, stage, document-target and validation routing | Legacy Coordinator | No | None | `KEEP_LEGACY` | New Writing and Review manifests must be narrower and independent. |
| Agent interface | `agents/openai.yaml` | Display metadata and broad default prompt | Legacy Coordinator | No | None | `DEFER` | Replace only after modular Skills are stable; current prompt mixes all roles. |
| Design history | `DESIGN.md` | Architecture rationale and historical decisions | Legacy | No | None | `KEEP_LEGACY` | Evidence source for migration, not normative Shared content. |
| Changelog | `CHANGELOG.md` | Version history | Legacy | No | None | `KEEP_LEGACY` | Historical duplication is intentional and not loaded as policy. |
| Sample paper | `assets/sample-papers/C24104220149.pdf` | Local style/example artifact | Benchmark candidate | No | None | `DEFER` | Admit only after provenance, purpose, and expected assertions are documented. |
| Execution contract | `static/core/execution-contract.md` | Global behavior, routing, facts, source protection, completion | Legacy + Shared Contracts | Partial | Legacy only | `SPLIT` | Keep workflow/state in Legacy; extract evidence and artifact boundaries without role behavior. |
| Consistency contract | `static/core/consistency.md` | Fact priority, ledgers, propagation and cross-artifact consistency | Shared Contracts + Review | Yes | Shared/Review read-only | `SPLIT` | Shared defines facts; Review diagnoses mismatches; Legacy remains state owner. |
| Quality gates | `static/core/quality-gates.md` | Submission state, severity, standards and issue codes | Legacy + Shared Standard + Review Policy | Partial | Legacy state only | `SPLIT` | Normative paper rules to Shared; severity/finding logic to Review; submission state stays Legacy. |
| Problem reading reference | `references/problem-reading.md` | Problem decomposition | Future Analysis/Modeling | No | Future owner | `DEFER` | Not part of the first Writing/Review extraction. |
| Data preprocessing reference | `references/data-preprocessing-visualization.md` | Data cleaning and exploration | Future Coding/Visual | No | Future owner | `DEFER` | Review may later consume evidence but does not own execution guidance. |
| Model construction reference | `references/model-construction.md` | Model selection plus paper explanation depth | Future Analysis/Modeling + Shared + Writing + Review | Partial | Future Analysis only | `SPLIT` | Defer modeling procedure; extract paper explanation standard/procedure/check separately. |
| Model validation reference | `references/model-validation.md` | Validation choices and evidence boundaries | Future Analysis/Modeling + Shared + Review | Partial | Future Analysis only | `SPLIT` | Shared can define evidence sufficiency; Review diagnoses; no validation execution in Review. |
| Sensitivity reference | `references/sensitivity-analysis.md` | Sensitivity design and reporting | Future Analysis/Modeling + Shared + Review | Partial | Future Analysis only | `DEFER` | First wave may reference only existing verified sensitivity evidence. |
| Innovation reference | `references/model-innovation.md` | Contribution wording and evidence boundary | Shared + Writing + Review | Yes | Writing text only | `SPLIT` | Standard, construction procedure, and diagnostic behavior must remain separate. |
| Evaluation criteria | `references/evaluation-criteria.md` | Internal diagnostic orientation | Legacy + Review | No | None | `SPLIT` | Official/source claims remain evidence-gated; no competition score in Shared. |
| Prose style | `references/paper-prose-style.md` | Academic prose, anti-AI, anti-defensive and rewrite procedure | Shared + Writing + Review | Partial | Writing text only | `SPLIT` | Primary source for first Shared rules; procedures must not be copied into Shared. |
| Paper writing | `references/paper-writing.md` | Abstract/body/conclusion construction plus audit handoff | Writing | No | Authorized manuscript only | `MOVE_WRITING` | Remove submission-audit ownership from the new Writing Skill. |
| Paper depth | `references/paper-depth-visual-density.md` | Modeling explanation, result depth and figure-value standards | Shared + Writing + Review | Partial | Writing text only | `SPLIT` | Normative standard, construction guidance, and findings logic become separate. |
| Result visualization | `references/result-visualization.md` | Figure choice, visual QA, caption/discussion and consistency | Shared + Writing + Review + Future Coding/Visual | Partial | Writing caption only | `SPLIT` | Plot generation and repair stay future Coding/Visual; Review only diagnoses. |
| Reference management | `references/reference-management.md` | Citation authenticity, relevance, format and workflow | Shared + Writing + Review | Partial | Writing citation edits only | `SPLIT` | Shared defines requirements; Writing inserts authorized citations; Review checks evidence. |
| Document editing | `references/document-editing.md` | Master-source selection, write authorization and template boundary | Shared Contract + Writing + Review | Partial | Writing only when authorized | `SPLIT` | Review validates source identity but never edits it. |
| LaTeX/PDF audit | `references/latex-pdf-layout-audit.md` | Build-log and rendered-PDF review | Review | No | None | `MOVE_REVIEW` | Writing may invoke Review after writing; it does not absorb audit policy. |
| Figure artifact management | `references/figure-artifact-management.md` | Canonical set, audit and safe trash workflow | Shared Contract + Review + Legacy mutation tool | Partial | Legacy authorized mutation only | `SPLIT` | Canonical schema is Shared; dry-run audit is Review; trash action is excluded from Review. |
| Sample-paper style | `references/sample-paper-style.md` | Safe style-reference boundary | Writing | No | Text only | `MOVE_WRITING` | Keep explicit non-copying and non-template boundary. |
| Word formulas | `references/word-latex-formulas.md` | DOCX equation requirements and verification | Shared Standard + Review Utility | Yes | None | `SPLIT` | Writing creates content; Review owns deterministic verification. |
| Document-target fragments | `static/fragments/document-target/*` | Source/format routing | Writing | No | Authorized manuscript only | `MOVE_WRITING` | Review receives artifact references through its request contract, not these write routes. |
| Fresh entry | `static/fragments/entry/fresh.md` | Start-state workflow | Legacy Coordinator | No | Legacy state only | `KEEP_LEGACY` | Future `1_start` candidate, not first-wave work. |
| Handoff entry | `static/fragments/entry/handoff.md` | Inherited evidence and checkpoint routing | Legacy Coordinator + Shared Contract | Partial | Legacy state only | `SPLIT` | Shared may define evidence status semantics; routing remains Legacy. |
| Analysis mode | `static/fragments/mode/analysis.md` | Analysis routing | Future Analysis/Modeling | No | Future owner | `DEFER` | Not copied into Writing or Review. |
| Build mode | `static/fragments/mode/build.md` | Build/code routing | Future Coding/Visual | No | Future owner | `DEFER` | Not copied into Writing or Review. |
| Paper mode | `static/fragments/mode/paper.md` | Paper construction route | Writing | No | Authorized manuscript only | `MOVE_WRITING` | Remove automatic final-audit behavior from Writer contract. |
| Audit mode | `static/fragments/mode/audit.md` | Audit route | Review | No | None | `MOVE_REVIEW` | Convert to evidence-backed findings rather than submission decision. |
| Micro-revision mode | `static/fragments/mode/micro-revision.md` | Controlled local manuscript edit | Writing | No | Explicitly authorized manuscript | `MOVE_WRITING` | Shared owns immutable artifact boundaries; Review can validate resulting evidence separately. |
| Revision mode | `static/fragments/mode/revision.md` | Wider manuscript revision and scope escalation | Writing | No | Explicitly authorized manuscript | `MOVE_WRITING` | Preserve scope escalation; remove reviewer severity logic. |
| Problem/model/computation stages | `static/fragments/stage/{problem-reading,model-construction,computation-experiment,model-validation,sensitivity-analysis}.md` | Modeling workflow | Future Analysis/Modeling or Coding/Visual | No | Future owner | `DEFER` | First wave must not create placeholder Skills for these stages. |
| Contribution-writing stage | `static/fragments/stage/contribution-writing.md` | Evidence-bound contribution prose | Writing | No | Text only | `MOVE_WRITING` | Refer to Shared contribution/claim rules by Rule ID. |
| Paper-writing stage | `static/fragments/stage/paper-writing.md` | Paper construction plus final audit handoff | Writing | No | Authorized manuscript only | `MOVE_WRITING` | Split out submission-audit step and READY_TO_SUBMIT language. |
| Result-visualization stage | `static/fragments/stage/result-visualization.md` | Plot generation, inspection and discussion | Future Coding/Visual + Writing + Review | Partial | Future Coding/Writing only | `SPLIT` | No plotting or file repair in Review. |
| Submission-audit stage | `static/fragments/stage/submission-audit.md` | Final quality and submission decision | Legacy Coordinator + Review | No | Legacy state only | `SPLIT` | Review supplies findings; Legacy alone computes legacy submission state. |
| Style linter | `scripts/lint_paper_style.py` | Deterministic prose-risk detection | Review | No | None | `MOVE_REVIEW` | Findings require human/semantic confirmation; never auto-rewrite. |
| LaTeX build auditor | `scripts/audit_latex_build.py` | Read-only source/log audit | Review | No | None | `MOVE_REVIEW` | Preserve recursive source resolution and strict/non-strict behavior. |
| PDF review validator | `scripts/validate_latex_review.py` | PDF hash/page evidence validation | Review | No | None | `MOVE_REVIEW` | Read-only evidence validation. |
| Figure output auditor | `scripts/audit_figure_outputs.py` | Dry-run audit plus optional trash mutation | Review + Legacy utility | No | Legacy mutation only | `SPLIT` | Review gets a pure audit path; `--apply-trash` must not be present in Review runtime. |
| DOCX math verifier | `scripts/verify_docx_math.py` | Read-only equation inspection | Review | No | None | `MOVE_REVIEW` | Shared may define the standard, not the CLI behavior. |
| Ledger validator | `scripts/validate_ledger.py` | Legacy workflow/fact-state validation | Legacy + Shared compatibility | Partial | None | `KEEP_LEGACY` | Use later as mapping evidence; do not make Writing or Review ledger writers. |
| Quality-report validator | `scripts/validate_quality_report.py` | Legacy gates, issues and submission-state validation | Legacy + Review compatibility | Partial | None | `SPLIT` | Legacy keeps status validation; Review receives a separate findings validator. |
| Package validator | `scripts/validate_package.py` | Local path integrity | Shared development utility | Yes | None | `EXTRACT_SHARED` | Generalize for package-root Shared references and multiple Skills. |
| Figure manifest template | `templates/figure-manifest.json` | Canonical formal-figure contract | Shared Contracts | Yes | Owner outside Review | `EXTRACT_SHARED` | Review reads it; Writing does not mutate it. |
| LaTeX review template | `templates/latex-review.json` | PDF review evidence record | Review | No | Review returns result only | `MOVE_REVIEW` | Persistence remains an external authorized action. |
| Working-draft LaTeX | `templates/latex/working-draft/*` | Non-official manuscript fallback | Writing | No | Explicit creation authorization | `MOVE_WRITING` | Preserve non-official and non-submission status. |
| Modeling ledger templates | `templates/modeling-ledger.{json,yaml}` | Legacy facts/workflow state | Legacy + Shared adapter source | Partial | Legacy only | `KEEP_LEGACY` | Phase 5 may add a minimal read-only mapping; no replacement in first extraction. |
| Quality report templates | `templates/quality-report.{json,yaml}` | Legacy gate and submission state | Legacy | No | Legacy only | `KEEP_LEGACY` | New Review findings schema is versioned separately. |
| Figure audit tests | `tests/test_figure_artifact_audit.py` | Audit and trash safety | Review + Legacy regression | No | Test fixtures only | `SPLIT` | Review tests must prove zero mutation; apply-trash remains Legacy regression. |
| LaTeX build tests | `tests/test_latex_build_audit.py` | Build auditor behavior | Review | No | Test fixtures only | `MOVE_REVIEW` | Preserve clean/warning/error/subfile cases. |
| PDF review tests | `tests/test_latex_review_validator.py` | Current-PDF evidence behavior | Review | No | Test fixtures only | `MOVE_REVIEW` | Preserve stale-hash resistance. |
| Ledger handoff tests | `tests/test_ledger_handoff.py` | Legacy workflow and source authorization | Legacy + Writing regression | Partial | Test fixtures only | `SPLIT` | Writing retains document authorization cases; workflow cases remain Legacy. |
| Quality validator tests | `tests/test_quality_validator.py` | Legacy submission and evidence gates | Legacy + Review regression | Partial | Test fixtures only | `SPLIT` | Do not reinterpret legacy status as Review status. |
| Style linter tests | `tests/test_style_linter.py` | Prose-risk and resistance cases | Review | No | Test fixtures only | `MOVE_REVIEW` | Seed for deterministic Review unit tests. |
| Policy documentation tests | `tests/test_v082_policy_docs.py` | Cross-file policy regression | Legacy + Shared/Writing/Review contract tests | Partial | Test fixtures only | `SPLIT` | Replace string-copy assertions with Rule-ID/path/ownership assertions where appropriate. |

## External Layer Assets

These assets remain in their current project during Phase 1. Only ownership is assigned.

| Asset | Current Path | Responsibility | New Owner | Shared? | Mutation Permission | Migration Action | Notes |
|---|---|---|---|---|---|---|---|
| Reviewer request schema | `modeling-integrations/schemas/reviewer-request.schema.json` | Provider-neutral review input | Review Contracts | No | None | `MOVE_REVIEW` | Version and adapt; do not silently overwrite contract v1. |
| Reviewer result schema | `modeling-integrations/schemas/reviewer-result.schema.json` | Read-only structured findings | Review Contracts | No | None | `MOVE_REVIEW` | Extend through a versioned schema/mapping for `rule_id`; retain empty findings. |
| Reviewer contract adapter | `modeling-integrations/adapters/benchmark/reviewer_contract.py` | Contract validation and fail-closed normalization | Review | No | None | `MOVE_REVIEW` | Preserve `CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY`. |
| Cross-artifact consistency | `modeling-integrations/adapters/benchmark/cross_artifact_consistency.py` | Read-only declared-value comparison | Review + Shared Evidence | Yes | None | `SPLIT` | Shared declares canonical values; Review returns mismatch findings. |
| Quality evidence bridge | `modeling-integrations/adapters/benchmark/quality_evidence_bridge.py` | Read-only projection into legacy evidence semantics | Shared compatibility | Yes | None | `EXTRACT_SHARED` | Adapter only; no ledger/report writes. |
| Quality evidence writer | `modeling-integrations/adapters/benchmark/quality_evidence_writer.py` | Explicitly applied legacy ledger/report update | Legacy Coordinator utility | No | Explicit external authorization | `KEEP_LEGACY` | Prohibited from Review runtime because it can write with `--apply`. |
| Reviewer benchmark evaluator | `modeling-integrations/adapters/benchmark/reviewer_benchmark.py` | Contract and adjudication-based metrics | Benchmark/Review | No | Benchmark outputs only | `MOVE_REVIEW` | Keep separate from runtime Review Skill. |
| Reviewer fault set | `modeling-benchmark/reviewer-fault-set.yaml` | Seeded and resistance cases | Benchmark/Review | No | Fixtures only | `MOVE_REVIEW` | Current state is specification-only and can seed the new Benchmark. |
| Reviewer experiment | `modeling-benchmark/reviewer-experiment.yaml` | Provider experiment/admission status | Benchmark/Review | No | Fixtures only | `DEFER` | No provider is currently admitted; first-wave Review must not depend on one. |
| Solver feedback assets | `modeling-integrations/*solver*` | Solver contract/provider feedback | Future Analysis/Modeling + Coding/Visual | No | Future owner | `DEFER` | Explicitly outside first-wave scope. |
| Modeling Library | `modeling-library/**` | Metadata-only method candidates | Future Analysis/Modeling + Shared references | Partial | Read-only metadata | `DEFER` | Preserve frozen state; do not absorb into Writing/Review. |
| Runtime/capability discovery | `modeling-integrations/{runtime-registry.yaml,adapters/benchmark/capability_discovery.py}` | Runtime availability | Future Coordinator | No | None | `DEFER` | No new runtime capability in first wave. |

## Compatibility Decisions

1. `READY_TO_SUBMIT` remains a Legacy state. Review findings cannot create or change it.
2. Existing Reviewer Contract v1 remains valid. A new schema must be versioned or mapped; it cannot be overwritten in place.
3. A formal Review finding must carry locatable evidence and a Shared Rule ID. Evidence-free observations, if retained, belong in a separate candidate/limitation channel rather than formal findings.
4. Review runtime returns a result object only. `writes_performed = []` remains literal.
5. Any CLI that contains a mutation path must be split or wrapped before entering Review.
6. Writing and Review use stable kebab-case identifiers: `huawei-cup-writing` and `huawei-cup-review`.

## Gate Decision

`PASS`

Every first-wave asset has a defined owner or an explicit deferred owner. Shared, Writing, Review, Legacy, and Benchmark responsibilities can each be stated independently, and no unresolved mutation authority remains.

## Next Allowed Phase

Phase 2 may extract the Shared Paper Quality Standard only after user approval of this matrix and the accompanying duplication audit.
