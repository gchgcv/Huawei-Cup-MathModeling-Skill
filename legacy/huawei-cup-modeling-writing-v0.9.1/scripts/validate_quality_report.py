#!/usr/bin/env python3
"""Validate a quality report and enforce submission-state gates.

The script checks declared evidence and consistency. It cannot prove that the
mathematics or evidence itself is correct; those still require domain review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ALLOWED_GATE_STATUS = {"PASS", "FAIL", "UNVERIFIED", "NOT_APPLICABLE"}
ALLOWED_SUBMISSION_STATUS = {"DRAFT", "NEEDS_VALIDATION", "BLOCKED", "READY_TO_SUBMIT"}
ALLOWED_SEVERITY = {"P0", "P1", "P2"}
ALLOWED_ISSUE_CODES = {
    "Q_MISSING_MAJOR",
    "RESULT_UNTRACEABLE",
    "UNEXECUTED_RESULT_CLAIM",
    "CROSS_ARTIFACT_CONFLICT",
    "FORMULA_OR_UNIT_ERROR",
    "COMPLIANCE_RISK",
    "UNMARKED_PLACEHOLDER",
    "REPRODUCIBILITY_MISSING",
    "VALIDATION_MISSING",
    "BASELINE_MISSING",
    "DATA_LEAKAGE_RISK",
    "ABSTRACT_RESULT_MISSING",
    "FIGURE_REFERENCE_MISSING",
    "FIGURE_VISUAL_UNVERIFIED",
    "FIGURE_VISUAL_DEFECT",
    "REFERENCE_MISSING",
    "REFERENCE_UNVERIFIED",
    "REFERENCE_POLICY_VIOLATION",
    "REFERENCE_ORDER_ERROR",
    "REFERENCE_FORMAT_INCONSISTENT",
    "REFERENCE_RELEVANCE_LOW",
    "FORMAT_ERROR",
    "UNIT_PRESENTATION_ERROR",
    "REPORT_PRECISION_MISMATCH",
    "MODEL_ASSUMPTION_STRUCTURE_THIN",
    "SYMBOL_GEOMETRY_UNEXPLAINED",
    "FIGURE_LAYOUT_UNREADABLE",
    "AI_STYLE_OVERUSE",
    "DEFENSIVE_PROSE_OVERUSE",
    "WORKLOG_NARRATIVE",
    "SYNTACTIC_AI_PATTERN",
    "PUNCTUATION_OVERUSE",
    "EMPTY_EVALUATION",
    "TERM_DISTORTION",
    "HANDOFF_UNVERIFIED",
    "TEMPLATE_SOURCE_UNVERIFIED",
    "PDF_LAYOUT_UNVERIFIED",
    "MODEL_EXPLANATION_THIN",
    "RESULT_DISCUSSION_THIN",
    "PSEUDO_FIGURE",
    "FLOAT_PLACEMENT_POOR",
    "OTHER",
}
ISSUE_SCORE_CAPS = {
    "Q_MISSING_MAJOR": 59,
    "RESULT_UNTRACEABLE": 59,
    "UNEXECUTED_RESULT_CLAIM": 59,
    "CROSS_ARTIFACT_CONFLICT": 59,
    "REPRODUCIBILITY_MISSING": 69,
    "VALIDATION_MISSING": 74,
    "BASELINE_MISSING": 79,
    "ABSTRACT_RESULT_MISSING": 84,
}
REQUIRED_GATES = {
    "question_coverage",
    "result_traceability",
    "cross_artifact_consistency",
    "model_validity",
    "validation_adequacy",
    "format_and_citation",
    "no_fabrication",
    "prose_clarity",
}
SCORE_MAX = {
    "question_and_task": 15,
    "data_traceability": 15,
    "model_reasonableness": 20,
    "solution_correctness": 20,
    "validation_robustness": 10,
    "logic_explanation": 10,
    "format_expression": 5,
    "contribution": 5,
}


VAGUE_EVIDENCE = {
    "已检查", "已验证", "无问题", "正常", "通过", "见正文", "见附件",
    "checked", "verified", "ok", "pass", "see paper", "see attachment",
}


def has_evidence(value: object) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        text = str(item).strip()
        if text and text.lower() not in VAGUE_EVIDENCE:
            return True
    return False


def recommended_status(gates: dict, issues: list) -> str:
    unresolved = [item for item in issues if isinstance(item, dict) and not item.get("resolved", False)]
    if any(item.get("severity") == "P0" for item in unresolved):
        return "BLOCKED"
    statuses = [item.get("status") for item in gates.values() if isinstance(item, dict)]
    if "FAIL" in statuses:
        return "BLOCKED"
    if any(item.get("severity") == "P1" for item in unresolved):
        return "NEEDS_VALIDATION"
    if "UNVERIFIED" in statuses:
        return "NEEDS_VALIDATION"
    if all(status in {"PASS", "NOT_APPLICABLE"} for status in statuses):
        return "READY_TO_SUBMIT"
    return "DRAFT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--strict", action="store_true", help="Require evidence for all positive claims")
    parser.add_argument("--ledger", help="Optional modeling-ledger.json for handoff/workflow cross-checks")
    parser.add_argument("--latex-review", help="Current latex-review.json; required for strict READY_TO_SUBMIT when ledger source_format=latex")
    args = parser.parse_args()

    path = Path(args.report)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    ledger_data = None
    if args.ledger:
        ledger_path = Path(args.ledger)
        try:
            ledger_data = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read ledger: {exc}")

    declared = data.get("submission_status")
    if declared not in ALLOWED_SUBMISSION_STATUS:
        errors.append(f"invalid submission_status: {declared!r}")
    if declared == "READY_TO_SUBMIT" and args.strict and not args.ledger:
        errors.append("READY_TO_SUBMIT in strict mode requires --ledger for workflow and template-source checks")

    gates = data.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}
    missing_gates = sorted(REQUIRED_GATES - set(gates))
    extra_gates = sorted(set(gates) - REQUIRED_GATES)
    for name in missing_gates:
        errors.append(f"missing gate: {name}")
    for name in extra_gates:
        warnings.append(f"unknown gate: {name}")

    for name in sorted(REQUIRED_GATES & set(gates)):
        gate = gates[name]
        if not isinstance(gate, dict):
            errors.append(f"gate {name} must be an object")
            continue
        status = gate.get("status")
        if status not in ALLOWED_GATE_STATUS:
            errors.append(f"gate {name} has invalid status: {status!r}")
        if status in {"PASS", "NOT_APPLICABLE"} and not has_evidence(gate.get("evidence")):
            errors.append(f"gate {name} is {status} but has no evidence")
        if status == "FAIL" and not has_evidence(gate.get("evidence")):
            warnings.append(f"gate {name} is FAIL but has no recorded evidence")

    issues = data.get("issues", [])
    if not isinstance(issues, list):
        errors.append("issues must be a list")
        issues = []
    seen_issue_ids: set[str] = set()
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            errors.append(f"issues[{index}] must be an object")
            continue
        issue_id = str(issue.get("id", "")).strip()
        if not issue_id:
            errors.append(f"issues[{index}] missing id")
        elif issue_id in seen_issue_ids:
            errors.append(f"duplicate issue id: {issue_id}")
        seen_issue_ids.add(issue_id)
        code = str(issue.get("code", "OTHER")).strip() or "OTHER"
        if code not in ALLOWED_ISSUE_CODES:
            errors.append(f"issues[{index}] invalid code: {code!r}")
        severity = issue.get("severity")
        if severity not in ALLOWED_SEVERITY:
            errors.append(f"issues[{index}] invalid severity: {severity!r}")
        if not str(issue.get("problem", "")).strip():
            errors.append(f"issues[{index}] missing problem")
        if not issue.get("resolved", False):
            if not has_evidence(issue.get("evidence")):
                warnings.append(f"unresolved issue {issue_id or index} has no evidence")
            if not str(issue.get("action", "")).strip():
                warnings.append(f"unresolved issue {issue_id or index} has no repair action")

    scores = data.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores must be an object")
        scores = {}
    total = 0.0
    for name, expected_max in SCORE_MAX.items():
        entry = scores.get(name)
        if not isinstance(entry, dict):
            errors.append(f"missing or invalid score item: {name}")
            continue
        maximum = entry.get("max")
        score = entry.get("score")
        if maximum != expected_max:
            errors.append(f"score item {name} max must be {expected_max}, got {maximum!r}")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            errors.append(f"score item {name} score must be numeric")
            continue
        if score < 0 or score > expected_max:
            errors.append(f"score item {name} out of range: {score}")
        total += float(score)
        if score > 0 and not has_evidence(entry.get("evidence")):
            message = f"score item {name} is positive but has no evidence"
            (errors if args.strict or declared == "READY_TO_SUBMIT" else warnings).append(message)
        if score < expected_max and not str(entry.get("deduction", "")).strip():
            warnings.append(f"score item {name} is below full score but has no deduction note")

    unresolved_caps = []
    for item in issues:
        if not isinstance(item, dict) or item.get("resolved", False):
            continue
        code = str(item.get("code", "OTHER"))
        severity = item.get("severity")
        default_cap = 59 if severity == "P0" else 84 if severity == "P1" else 100
        unresolved_caps.append(ISSUE_SCORE_CAPS.get(code, default_cap))
    score_cap = min(unresolved_caps, default=100)
    if total > score_cap:
        errors.append(f"total score {total:.1f} exceeds unresolved-issue cap {score_cap}")

    if isinstance(ledger_data, dict):
        workflow = ledger_data.get("workflow", {})
        stages = workflow.get("stages", []) if isinstance(workflow, dict) else []
        stage_map = {}
        if isinstance(stages, list):
            for item in stages:
                if isinstance(item, dict) and item.get("name"):
                    stage_map[str(item.get("name"))] = str(item.get("status", ""))
        bad_handoff = [
            f"{name}:{status}"
            for name, status in stage_map.items()
            if status in {"INHERITED_UNVERIFIED", "NEEDS_REVIEW", "BLOCKED"}
        ]
        if declared == "READY_TO_SUBMIT":
            if bad_handoff:
                errors.append(
                    "READY_TO_SUBMIT is not allowed while workflow has unresolved inherited/review stages: "
                    + ", ".join(sorted(bad_handoff))
                )
            audit_status = stage_map.get("submission-audit")
            if audit_status != "COMPLETED":
                errors.append(
                    "READY_TO_SUBMIT with --ledger requires workflow stage submission-audit=COMPLETED"
                )
            document = ledger_data.get("document", {}) if isinstance(ledger_data.get("document", {}), dict) else {}
            template_source = str(document.get("template_source", "none"))
            document_target = str(document.get("document_target", "content-only"))
            if document_target == "content-only":
                errors.append("READY_TO_SUBMIT is not allowed with document_target=content-only")
            if template_source in {"none", "skill_fallback"}:
                errors.append(
                    "READY_TO_SUBMIT requires a verified official or user submission template; "
                    f"current template_source={template_source!r}"
                )
            elif template_source == "official" and document.get("official_template_current") is not True:
                errors.append(
                    "READY_TO_SUBMIT with template_source=official requires official_template_current=true"
                )
            elif template_source == "user" and document.get("submission_template_verified") is not True:
                errors.append(
                    "READY_TO_SUBMIT with template_source=user requires submission_template_verified=true"
                )

            source_format = str(document.get("source_format", "")).strip().lower()
            if source_format == "latex":
                if not args.latex_review:
                    errors.append(
                        "READY_TO_SUBMIT for LaTeX in strict mode requires --latex-review bound to the current PDF"
                    )
                else:
                    review_script = Path(__file__).with_name("validate_latex_review.py")
                    proc = subprocess.run(
                        [sys.executable, str(review_script), args.latex_review, "--strict"],
                        text=True, capture_output=True, check=False,
                    )
                    if proc.returncode != 0:
                        detail = (proc.stderr or proc.stdout).strip().replace("\n", "; ")
                        errors.append(f"LaTeX visual review is invalid: {detail}")
                    else:
                        try:
                            review_data = json.loads(Path(args.latex_review).read_text(encoding="utf-8"))
                        except (OSError, json.JSONDecodeError) as exc:
                            errors.append(f"cannot read latex review: {exc}")
                        else:
                            if review_data.get("scope") != "full" or review_data.get("status") != "PASS":
                                errors.append(
                                    "READY_TO_SUBMIT for LaTeX requires latex review scope=full and status=PASS"
                                )

    expected = recommended_status(gates, issues)
    if declared == "READY_TO_SUBMIT" and expected != "READY_TO_SUBMIT":
        errors.append(f"READY_TO_SUBMIT is not allowed; recommended status is {expected}")
    elif declared not in {expected, "DRAFT"}:
        errors.append(f"declared status {declared} conflicts with recommended status {expected}")
    elif declared == "DRAFT" and expected != "DRAFT":
        warnings.append(f"report is conservatively marked DRAFT; current evidence suggests {expected}")

    unresolved = [item for item in issues if isinstance(item, dict) and not item.get("resolved", False)]
    hard_blockers = []
    evidence_gaps = []
    improvements = []
    for name, gate in gates.items():
        if not isinstance(gate, dict):
            continue
        if gate.get("status") == "FAIL":
            hard_blockers.append(f"gate {name}=FAIL")
        elif gate.get("status") == "UNVERIFIED":
            evidence_gaps.append(f"gate {name}=UNVERIFIED")
    for item in unresolved:
        label = f"{item.get('id', '?')} {item.get('code', 'OTHER')}: {item.get('problem', '')}"
        if item.get("severity") == "P0":
            hard_blockers.append(label)
        elif item.get("severity") == "P1":
            evidence_gaps.append(label)
        elif item.get("severity") == "P2":
            improvements.append(label)

    print("HARD_BLOCKERS:")
    print("- none" if not hard_blockers else "\n".join(f"- {x}" for x in hard_blockers))
    print("EVIDENCE_GAPS:")
    print("- none" if not evidence_gaps else "\n".join(f"- {x}" for x in evidence_gaps))
    print("IMPROVEMENTS:")
    print("- none" if not improvements else "\n".join(f"- {x}" for x in improvements))
    print(f"INTERNAL_DIAGNOSTIC_SCORE: {total:.1f}/100")
    print("DIAGNOSTIC_NOTE: internal workflow diagnostic only; not an official competition score, final paper grade, or award prediction")
    print(f"SCORE_CAP: {score_cap}")
    print(f"RECOMMENDED_STATUS: {expected}")

    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    if errors:
        return 1
    print("OK: quality report checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
