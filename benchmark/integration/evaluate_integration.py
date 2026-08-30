#!/usr/bin/env python3
"""Evaluate API-free Writing-to-Review integration result envelopes."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_VALIDATOR = (
    REPO_ROOT / "skills" / "huawei-cup-review" / "scripts" / "validate_review_result.py"
)
SHARED_STANDARD = REPO_ROOT / "shared" / "paper-quality-standard"
RULE_HEADER = re.compile(r"^## ([A-Z]+-[0-9]{3}) —", re.MULTILINE)
NOT_RUN = "NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE"


def _load_review_validator() -> Any:
    spec = importlib.util.spec_from_file_location("integration_review_validator", REVIEW_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Review validator: {REVIEW_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_review_result


validate_review_result = _load_review_validator()


def _rule_ids() -> set[str]:
    ids: set[str] = set()
    for path in SHARED_STANDARD.glob("*.md"):
        ids.update(RULE_HEADER.findall(path.read_text(encoding="utf-8")))
    return ids


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_catalog(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise TypeError("Integration catalog must be an object with cases")
    return value


def _load_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Integration result must be an object: {path}")
    return value


def _load_results(results_dir: Path) -> dict[str, dict[str, Any]]:
    bundle_path = results_dir / "bundle.json"
    if bundle_path.is_file():
        bundle = _load_result(bundle_path)
        items = bundle.get("results")
        if not isinstance(items, list):
            raise ValueError("Integration bundle results must be a list")
        return {
            str(item["case_id"]): dict(item)
            for item in items
            if isinstance(item, Mapping) and isinstance(item.get("case_id"), str)
        }
    return {
        path.stem: _load_result(path)
        for path in results_dir.glob("*.json")
        if path.name != "bundle.json"
    }


def evaluate_case(case: Mapping[str, Any], envelope: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if envelope.get("case_id") != case.get("id"):
        errors.append("case_id_mismatch")
    output = envelope.get("writing_output_text")
    if not isinstance(output, str) or not output.strip():
        return {"case_id": case.get("id"), "status": "INVALID_OUTPUT", "errors": [*errors, "writing_output_text_missing"]}
    expected_hash = _sha256_text(output)
    input_hash = envelope.get("review_input_sha256")
    output_hash = envelope.get("review_output_sha256")
    if input_hash != expected_hash:
        errors.append("review_input_hash_mismatch")
    if output_hash != input_hash:
        errors.append("review_mutated_writer_output")

    review_result = envelope.get("review_result")
    if not isinstance(review_result, Mapping):
        return {"case_id": case.get("id"), "status": "INVALID_OUTPUT", "errors": [*errors, "review_result_missing"]}
    errors.extend(f"review_contract:{item}" for item in validate_review_result(review_result))
    if review_result.get("writes_performed"):
        errors.append("review_reports_writes")

    known_rules = _rule_ids()
    writing_rules = {str(item) for item in envelope.get("writing_rule_ids", [])}
    findings = [item for item in review_result.get("findings", []) if isinstance(item, Mapping)]
    review_rules = {str(item.get("rule_id")) for item in findings}
    if not writing_rules <= known_rules:
        errors.append("writing_unknown_shared_rule_id")
    if not review_rules <= known_rules:
        errors.append("review_unknown_shared_rule_id")

    handoff = envelope.get("next_writer_handoff")
    if not isinstance(handoff, Mapping):
        errors.append("next_writer_handoff_missing")
        handoff = {}
    finding_ids = {str(item.get("finding_id")) for item in findings}
    handed_ids = {str(item) for item in handoff.get("finding_ids", [])}
    understood_rules = {str(item) for item in handoff.get("understood_rule_ids", [])}
    if not finding_ids <= handed_ids:
        errors.append("finding_handoff_incomplete")
    if not review_rules <= understood_rules:
        errors.append("finding_rule_handoff_incomplete")

    if case.get("expected_review") == "empty_findings" and findings:
        errors.append("clean_or_resistance_case_has_findings")
    metrics = {
        "review_output_unchanged": input_hash == expected_hash and output_hash == input_hash,
        "review_write_count": len(review_result.get("writes_performed", [])),
        "shared_rule_ids_valid": writing_rules <= known_rules and review_rules <= known_rules,
        "finding_handoff_coverage": len(finding_ids & handed_ids) / len(finding_ids) if finding_ids else 1.0,
        "finding_rule_handoff_coverage": len(review_rules & understood_rules) / len(review_rules) if review_rules else 1.0,
    }
    return {
        "case_id": case.get("id"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "metrics": metrics,
    }


def evaluate_benchmark(catalog_path: Path, results_dir: Path | None) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    cases = [item for item in catalog["cases"] if isinstance(item, Mapping)]
    if results_dir is None:
        return {"status": NOT_RUN, "cases_expected": len(cases), "metrics": None, "limitations": ["integration_results_not_supplied"]}
    loaded_results = _load_results(results_dir)
    missing = [str(case["id"]) for case in cases if str(case["id"]) not in loaded_results]
    if missing:
        return {"status": NOT_RUN, "cases_expected": len(cases), "metrics": None, "limitations": [f"missing_integration_results:{','.join(missing)}"]}
    results = [
        evaluate_case(case, loaded_results[str(case["id"])])
        for case in cases
    ]
    valid = [item for item in results if item.get("metrics")]
    metrics = {
        "cases": len(results),
        "cases_passed": sum(item["status"] == "PASS" for item in results),
        "review_immutability_rate": sum(item["metrics"]["review_output_unchanged"] for item in valid) / len(valid),
        "review_mutation_count": sum(item["metrics"]["review_write_count"] for item in valid),
        "shared_rule_id_consistency_rate": sum(item["metrics"]["shared_rule_ids_valid"] for item in valid) / len(valid),
        "finding_handoff_coverage": sum(item["metrics"]["finding_handoff_coverage"] for item in valid) / len(valid),
    }
    return {"status": "EXECUTED", "metrics": metrics, "cases": results, "limitations": ["integration envelope metrics do not replace semantic paper adjudication"]}


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
