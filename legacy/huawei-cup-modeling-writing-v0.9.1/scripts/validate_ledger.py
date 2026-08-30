#!/usr/bin/env python3
"""Validate a modeling ledger for traceability, handoff state, and consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_STATUS = {"CONFIRMED", "DERIVED", "ASSUMED", "MISSING"}
ALLOWED_MODE = {"analysis", "build", "paper", "micro-revision", "revision", "audit"}
ALLOWED_ENTRY = {"fresh", "handoff"}
ALLOWED_CHECKPOINT = {
    "fresh",
    "after_problem_reading",
    "after_data_preprocessing",
    "after_model_construction",
    "after_computation",
    "after_results",
    "after_draft",
    "mixed",
}
ALLOWED_STAGE_STATUS = {
    "NOT_STARTED",
    "INHERITED_UNVERIFIED",
    "INHERITED_VERIFIED",
    "COMPLETED",
    "NEEDS_REVIEW",
    "BLOCKED",
    "NOT_APPLICABLE",
}
ALLOWED_STAGES = {
    "problem-reading",
    "data-preprocessing-visualization",
    "model-construction",
    "computation-experiment",
    "result-visualization",
    "sensitivity-analysis",
    "model-validation",
    "contribution-writing",
    "paper-writing",
    "submission-audit",
}
MODEL_DEPENDENT_STAGES = {
    "computation-experiment",
    "result-visualization",
    "sensitivity-analysis",
    "model-validation",
    "contribution-writing",
}

ALLOWED_DOCUMENT_TARGET = {
    "preserve-existing", "official-template", "user-template",
    "latex-working-draft", "docx-working-draft", "content-only",
}
ALLOWED_TEMPLATE_SOURCE = {"none", "official", "user", "skill_fallback"}
ALLOWED_SOURCE_FORMAT = {"", "latex", "docx", "markdown", "pdf", "other"}

VERIFIED_STAGE_STATES = {"INHERITED_VERIFIED", "COMPLETED"}


def duplicate_nonempty(values):
    seen, dup = set(), set()
    for value in values:
        if not value:
            continue
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--strict", action="store_true", help="Treat required handoff/traceability gaps as errors")
    args = parser.parse_args()
    path = Path(args.ledger)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = [], []
    for key in ("project", "document", "workflow", "questions", "data", "parameters", "results", "claims"):
        if key not in data:
            (errors if args.strict or key != "workflow" else warnings).append(f"missing top-level key: {key}")

    project = data.get("project", {}) if isinstance(data.get("project", {}), dict) else {}
    mode = project.get("mode")
    if mode not in ALLOWED_MODE:
        errors.append(f"invalid project.mode: {mode!r}")

    entry = project.get("entry")
    checkpoint = project.get("checkpoint")
    if entry not in ALLOWED_ENTRY:
        (errors if args.strict else warnings).append(f"invalid or missing project.entry: {entry!r}")
    if checkpoint not in ALLOWED_CHECKPOINT:
        (errors if args.strict else warnings).append(f"invalid or missing project.checkpoint: {checkpoint!r}")
    if entry == "fresh" and checkpoint not in (None, "fresh"):
        errors.append("project.entry is fresh but checkpoint is not fresh")
    if entry == "handoff" and checkpoint == "fresh":
        errors.append("project.entry is handoff but checkpoint is fresh")


    document = data.get("document", {}) if isinstance(data.get("document", {}), dict) else {}
    document_target = document.get("document_target")
    template_source = document.get("template_source")
    source_format = document.get("source_format", "")
    if document_target not in ALLOWED_DOCUMENT_TARGET:
        (errors if args.strict else warnings).append(f"invalid or missing document.document_target: {document_target!r}")
    if template_source not in ALLOWED_TEMPLATE_SOURCE:
        (errors if args.strict else warnings).append(f"invalid or missing document.template_source: {template_source!r}")
    if source_format not in ALLOWED_SOURCE_FORMAT:
        errors.append(f"invalid document.source_format: {source_format!r}")

    if document_target == "preserve-existing" and args.strict and mode in {"paper", "micro-revision", "revision", "audit"}:
        if not str(document.get("master_source", "")).strip():
            errors.append("preserve-existing requires document.master_source in paper/micro-revision/revision/audit strict mode")
    if document_target == "official-template" and template_source != "official":
        errors.append("official-template requires document.template_source=official")
    if document_target == "user-template" and template_source != "user":
        errors.append("user-template requires document.template_source=user")
    if document_target == "latex-working-draft":
        if args.strict and document.get("source_creation_authorized") is not True:
            errors.append("latex-working-draft requires document.source_creation_authorized=true; do not create a new .tex without explicit user authorization")
        if template_source != "skill_fallback":
            errors.append("latex-working-draft requires document.template_source=skill_fallback")
        expected = "templates/latex/working-draft/main.tex"
        if str(document.get("template_path", "")) not in {"", expected}:
            errors.append(f"latex-working-draft template_path must be {expected!r}")
        if args.strict and source_format not in {"", "latex"}:
            errors.append("latex-working-draft requires document.source_format=latex")
    if document_target == "content-only" and template_source not in {"none", ""}:
        warnings.append("content-only normally uses document.template_source=none")

    workflow = data.get("workflow", {}) if isinstance(data.get("workflow", {}), dict) else {}
    current_stage = workflow.get("current_stage")
    if current_stage and current_stage not in ALLOWED_STAGES:
        errors.append(f"invalid workflow.current_stage: {current_stage!r}")
    elif args.strict and not current_stage:
        errors.append("workflow.current_stage is required in strict mode")

    stage_items = workflow.get("stages", [])
    if stage_items is None:
        stage_items = []
    if not isinstance(stage_items, list):
        errors.append("workflow.stages must be a list")
        stage_items = []
    stage_names = [x.get("name", "") for x in stage_items if isinstance(x, dict)]
    for value in duplicate_nonempty(stage_names):
        errors.append(f"duplicate workflow stage: {value}")

    stage_status_map = {}
    for i, item in enumerate(stage_items):
        if not isinstance(item, dict):
            errors.append(f"workflow.stages[{i}] is not an object")
            continue
        name = item.get("name")
        status = item.get("status")
        evidence = item.get("evidence", [])
        notes = item.get("notes", "")
        if name not in ALLOWED_STAGES:
            errors.append(f"workflow.stages[{i}].name invalid: {name!r}")
        if status not in ALLOWED_STAGE_STATUS:
            errors.append(f"workflow.stages[{i}].status invalid: {status!r}")
        if name:
            stage_status_map[name] = status
        if status in {"INHERITED_UNVERIFIED", "INHERITED_VERIFIED", "COMPLETED"} and not evidence:
            (errors if args.strict else warnings).append(
                f"workflow.stages[{i}] status {status} requires concrete evidence/artifact location"
            )
        if status in {"NEEDS_REVIEW", "BLOCKED"} and not notes:
            (errors if args.strict else warnings).append(
                f"workflow.stages[{i}] status {status} requires notes explaining the gap"
            )
        if status and status.startswith("INHERITED_") and entry == "fresh":
            errors.append(f"workflow.stages[{i}] is inherited but project.entry is fresh")

    if args.strict and current_stage and stage_names and current_stage not in stage_names:
        warnings.append("workflow.current_stage is not explicitly listed in workflow.stages")

    questions = data.get("questions", [])
    qids = [q.get("id", "") for q in questions if isinstance(q, dict)]
    if not qids:
        errors.append("questions must contain at least one item")
    for value in duplicate_nonempty(qids):
        errors.append(f"duplicate question id: {value}")
    qid_set = set(qids)

    model_required = (
        (mode == "build" and current_stage in MODEL_DEPENDENT_STAGES)
        or stage_status_map.get("model-construction") in VERIFIED_STAGE_STATES
        or any(stage_status_map.get(stage) in VERIFIED_STAGE_STATES for stage in MODEL_DEPENDENT_STAGES)
    )

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append(f"questions[{i}] is not an object")
            continue
        required = ("id", "task", "outputs") if args.strict else ()
        for field in required:
            if not q.get(field):
                errors.append(f"questions[{i}].{field} is incomplete")
        if not args.strict and (not q.get("task") or not q.get("outputs")):
            warnings.append(f"questions[{i}] is incomplete")
        if model_required and not q.get("model"):
            (errors if args.strict else warnings).append(
                f"questions[{i}].model is required because the workflow has reached a model-dependent stage"
            )

    params = data.get("parameters", [])
    for field in ("symbol", "code_name"):
        for value in duplicate_nonempty([p.get(field, "") for p in params if isinstance(p, dict)]):
            errors.append(f"duplicate parameter {field}: {value}")
    for i, p in enumerate(params):
        if not isinstance(p, dict):
            errors.append(f"parameters[{i}] is not an object")
            continue
        status = p.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"parameters[{i}].status invalid: {status!r}")
        if status != "MISSING" and not p.get("source"):
            errors.append(f"parameters[{i}] has status {status} but no source")
        if status == "MISSING" and p.get("value") is not None:
            warnings.append(f"parameters[{i}] is MISSING but has a value")

    results = data.get("results", [])
    result_ids = [r.get("id", "") for r in results if isinstance(r, dict)]
    for value in duplicate_nonempty(result_ids):
        errors.append(f"duplicate result id: {value}")
    for i, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"results[{i}] is not an object")
            continue
        if not result.get("id"):
            errors.append(f"results[{i}] missing id")
        if result.get("question_id") not in qid_set:
            errors.append(f"results[{i}] references unknown question_id: {result.get('question_id')!r}")
        if not result.get("source"):
            errors.append(f"results[{i}] has no traceable source")

    claims = data.get("claims", [])
    claim_ids = [c.get("id", "") for c in claims if isinstance(c, dict)]
    for value in duplicate_nonempty(claim_ids):
        errors.append(f"duplicate claim id: {value}")
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{i}] is not an object")
            continue
        if not claim.get("id"):
            errors.append(f"claims[{i}] missing id")
        status = claim.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"claims[{i}].status invalid: {status!r}")
        evidence = claim.get("evidence", [])
        if status != "MISSING" and not evidence:
            errors.append(f"claims[{i}] has status {status} but no evidence")
        if status == "MISSING" and evidence:
            warnings.append(f"claims[{i}] is MISSING but has evidence")
        if args.strict and status != "MISSING" and not claim.get("text"):
            errors.append(f"claims[{i}].text is incomplete")

    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    if errors:
        return 1
    print("OK: ledger consistency and handoff checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
