#!/usr/bin/env python3
"""Read-only evaluator for seeded Review faults and resistance cases."""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULT_VALIDATOR = (
    REPO_ROOT / "skills" / "huawei-cup-review" / "scripts" / "validate_review_result.py"
)
NOT_RUN = "NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE"


def _load_result_validator() -> Any:
    spec = importlib.util.spec_from_file_location("phase6_review_result_validator", RESULT_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Review validator: {RESULT_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_review_result


validate_review_result = _load_result_validator()


def load_catalog(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise TypeError("Review catalog must be an object with cases")
    policy = value.get("source_access_policy")
    if not isinstance(policy, Mapping):
        raise TypeError("source_access_policy missing")
    if policy.get("old_problem_training") is not False or policy.get("answer_artifact_access") is not False:
        raise ValueError("source access policy permits benchmark contamination")
    return value


def _load_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Review result must be an object: {path}")
    return value


def _load_results(results_dir: Path) -> dict[str, dict[str, Any]]:
    bundle_path = results_dir / "bundle.json"
    if bundle_path.is_file():
        bundle = _load_result(bundle_path)
        items = bundle.get("results")
        if not isinstance(items, list):
            raise ValueError("Review bundle results must be a list")
        return {
            str(item["case_id"]): dict(item["review_result"])
            for item in items
            if isinstance(item, Mapping)
            and isinstance(item.get("case_id"), str)
            and isinstance(item.get("review_result"), Mapping)
        }
    return {
        path.stem: _load_result(path)
        for path in results_dir.glob("*.json")
        if path.name != "bundle.json"
    }


def evaluate_case(case: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
    contract_errors = validate_review_result(result)
    if contract_errors:
        return {
            "case_id": case.get("id"),
            "status": "INVALID_OUTPUT",
            "contract_errors": contract_errors,
            "metrics": None,
        }
    findings = [item for item in result.get("findings", []) if isinstance(item, Mapping)]
    accepted = {str(item) for item in case.get("accepted_rule_ids", [])}
    expected_finding = case.get("expectation") == "finding"
    matched = [item for item in findings if str(item.get("rule_id")) in accepted]
    unsupported = [
        item
        for item in findings
        if str(item.get("rule_id")) not in accepted
        or any(
            evidence.get("artifact_id") != case.get("artifact_id")
            for evidence in item.get("evidence", [])
            if isinstance(evidence, Mapping)
        )
    ]
    semantic_keys = [
        (str(item.get("rule_id")), str(item.get("location"))) for item in findings
    ]
    duplicate_count = len(semantic_keys) - len(set(semantic_keys))
    evidence_backed = sum(bool(item.get("evidence")) for item in findings)
    false_negative = int(expected_finding and not matched)
    false_positive = int(not expected_finding and bool(findings))
    metrics = {
        "expected_finding": expected_finding,
        "seeded_fault_detected": bool(matched) if expected_finding else None,
        "false_negative": false_negative,
        "false_positive": false_positive,
        "unsupported_finding_count": len(unsupported),
        "duplicate_finding_count": duplicate_count,
        "finding_count": len(findings),
        "evidence_backed_count": evidence_backed,
        "mutation_count": len(result.get("writes_performed", [])),
        "clean_case_empty": not expected_finding and not findings,
    }
    passed = (
        not false_negative
        and not false_positive
        and not unsupported
        and not duplicate_count
        and evidence_backed == len(findings)
        and metrics["mutation_count"] == 0
    )
    return {
        "case_id": case.get("id"),
        "status": "PASS" if passed else "FAIL",
        "contract_errors": [],
        "metrics": metrics,
    }


def evaluate_benchmark(catalog_path: Path, results_dir: Path | None) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    cases = [item for item in catalog["cases"] if isinstance(item, Mapping)]
    if results_dir is None:
        return {"status": NOT_RUN, "cases_expected": len(cases), "metrics": None, "limitations": ["reviewer_results_not_supplied"]}
    loaded_results = _load_results(results_dir)
    missing = [str(case["id"]) for case in cases if str(case["id"]) not in loaded_results]
    if missing:
        return {"status": NOT_RUN, "cases_expected": len(cases), "metrics": None, "limitations": [f"missing_reviewer_results:{','.join(missing)}"]}
    results = [
        evaluate_case(case, loaded_results[str(case["id"])])
        for case in cases
    ]
    valid = [item for item in results if item["metrics"] is not None]
    fault_cases = [item for item in valid if item["metrics"]["expected_finding"]]
    clean_cases = [item for item in valid if not item["metrics"]["expected_finding"]]
    finding_count = sum(item["metrics"]["finding_count"] for item in valid)
    evidence_count = sum(item["metrics"]["evidence_backed_count"] for item in valid)
    metrics = {
        "cases": len(results),
        "cases_passed": sum(item["status"] == "PASS" for item in results),
        "seeded_fault_recall": sum(item["metrics"]["seeded_fault_detected"] for item in fault_cases) / len(fault_cases),
        "false_negative_count": sum(item["metrics"]["false_negative"] for item in valid),
        "false_positive_count": sum(item["metrics"]["false_positive"] for item in valid),
        "unsupported_finding_count": sum(item["metrics"]["unsupported_finding_count"] for item in valid),
        "duplicate_finding_count": sum(item["metrics"]["duplicate_finding_count"] for item in valid),
        "evidence_coverage": evidence_count / finding_count if finding_count else 1.0,
        "mutation_count": sum(item["metrics"]["mutation_count"] for item in valid),
        "clean_case_empty_findings_rate": sum(item["metrics"]["clean_case_empty"] for item in clean_cases) / len(clean_cases),
    }
    return {
        "status": "EXECUTED",
        "metrics": metrics,
        "cases": results,
        "limitations": ["fault support is adjudicated only against explicit synthetic case assertions"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path(__file__).with_name("cases.yaml"))
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()
    result = evaluate_benchmark(args.catalog, args.results)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"EXECUTED", NOT_RUN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
