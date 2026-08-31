#!/usr/bin/env python3
"""Read-only Writing benchmark evaluator and Legacy/Modular A/B aggregator."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MUTATION_VALIDATOR = (
    REPO_ROOT
    / "skills"
    / "huawei-cup-writing"
    / "scripts"
    / "validate_manuscript_mutation.py"
)
NOT_RUN = "NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE"


def _load_compare() -> Any:
    spec = importlib.util.spec_from_file_location(
        "writing_mutation_validator", MUTATION_VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load mutation validator: {MUTATION_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.compare


compare_protected = _load_compare()


def load_catalog(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise TypeError("Writing catalog must be an object with cases")
    return value


def _load_candidate(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Candidate must be a JSON object: {path}")
    return value


def _load_candidates(results_dir: Path) -> dict[str, dict[str, Any]]:
    bundle_path = results_dir / "bundle.json"
    if bundle_path.is_file():
        bundle = _load_candidate(bundle_path)
        system = bundle.get("system_under_test")
        outputs = bundle.get("outputs")
        if not isinstance(outputs, list):
            raise ValueError("Writing bundle outputs must be a list")
        return {
            str(item["case_id"]): {**item, "system_under_test": system}
            for item in outputs
            if isinstance(item, Mapping) and isinstance(item.get("case_id"), str)
        }
    return {
        path.stem: _load_candidate(path)
        for path in results_dir.glob("*.json")
        if path.name != "bundle.json"
    }


def _added_count(mutation: Mapping[str, Any], field: str) -> int:
    before = dict(mutation["before"][field])
    after = dict(mutation["after"][field])
    return sum(max(0, count - before.get(value, 0)) for value, count in after.items())


def _semantic_assertions(
    case: Mapping[str, Any], output: str
) -> tuple[list[dict[str, object]], list[str]]:
    results: list[dict[str, object]] = []
    failures: list[str] = []
    for raw in case.get("semantic_assertions", []):
        if not isinstance(raw, Mapping):
            continue
        assertion_id = str(raw.get("id", "unnamed"))
        phrases = [str(item) for item in raw.get("any_phrases", [])]
        passed = bool(phrases) and any(phrase in output for phrase in phrases)
        results.append(
            {
                "id": assertion_id,
                "kind": str(raw.get("kind", "general")),
                "status": "PASS" if passed else "FAIL",
                "matched_phrases": [phrase for phrase in phrases if phrase in output],
            }
        )
        if not passed:
            failures.append(assertion_id)
    return results, failures


def _semantic_kind_pass(assertions: list[dict[str, object]], kind: str) -> bool:
    relevant = [item for item in assertions if item.get("kind") == kind]
    return not relevant or all(item.get("status") == "PASS" for item in relevant)


def evaluate_case(
    case: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    if candidate.get("case_id") != case.get("id"):
        errors.append("case_id_mismatch")
    system_under_test = candidate.get("system_under_test")
    if not (
        system_under_test == "legacy-v0.9.1"
        or (
            isinstance(system_under_test, str)
            and system_under_test.startswith("modular-writing")
        )
    ):
        errors.append("unknown_system_under_test")
    output = candidate.get("output_text")
    if not isinstance(output, str) or not output.strip():
        return {
            "case_id": case.get("id"),
            "status": "INVALID_OUTPUT",
            "errors": [*errors, "output_text_missing"],
        }

    source = str(case.get("input_text", ""))
    mutation = compare_protected(source, output)
    changed = set(mutation["changes"])
    number_delta = mutation.get("number_delta", {})
    added_numbers = Counter(str(item) for item in number_delta.get("added", []))
    removed_numbers = Counter(str(item) for item in number_delta.get("removed", []))
    allowed_added_numbers = Counter(
        str(item) for item in case.get("allowed_added_numbers", [])
    )
    undeclared_added_numbers = sorted(
        (added_numbers - allowed_added_numbers).elements()
    )
    unauthorized_number_change = bool(removed_numbers or undeclared_added_numbers)
    effective_changes = changed - {"numbers"}
    if unauthorized_number_change:
        effective_changes.add("numbers")
    for field in sorted(effective_changes):
        errors.append(f"protected_{field}_changed")

    protected_phrases = [str(item) for item in case.get("protected_phrases", [])]
    missing_protected = [item for item in protected_phrases if item not in output]
    errors.extend(f"protected_phrase_missing:{item}" for item in missing_protected)

    undesirable = [str(item) for item in case.get("undesirable_patterns", [])]
    before_hits = sum(source.count(item) for item in undesirable)
    after_hits = sum(output.count(item) for item in undesirable)
    required = [str(item) for item in case.get("required_phrases", [])]
    missing_required = [item for item in required if item not in output]
    protected_kinds = {str(item) for item in case.get("protected_kinds", [])}
    semantic_results, semantic_failures = _semantic_assertions(case, output)

    metrics = {
        "deterministic_fidelity_pass": not effective_changes and not missing_protected,
        "protected_elements_unchanged": not effective_changes,
        "numbers_preserved": "numbers" not in effective_changes,
        "numeric_bindings_preserved": not (
            {"numeric_bindings", "project_facts"} & effective_changes
        ),
        "formulas_preserved": "formulas" not in effective_changes,
        "citations_preserved": "citations" not in effective_changes,
        "labels_and_references_preserved": not (
            {"labels", "references"} & effective_changes
        ),
        "undesirable_before": before_hits,
        "undesirable_after": after_hits,
        "undesirable_reduced": before_hits == 0 or after_hits < before_hits,
        "required_phrases_present": not missing_required,
        "semantic_assertions_pass": not semantic_failures,
        "technical_terms_preserved": "technical_terms" not in protected_kinds
        or not missing_protected,
        "necessary_limitation_preserved": "necessary_limitation" not in protected_kinds
        or _semantic_kind_pass(semantic_results, "necessary_limitation"),
        "negative_evidence_preserved": "negative_evidence" not in protected_kinds
        or _semantic_kind_pass(semantic_results, "negative_evidence"),
        "declared_derived_number_count": sum(
            (added_numbers & allowed_added_numbers).values()
        ),
        "undeclared_added_number_count": len(undeclared_added_numbers),
        "invented_number_count": len(undeclared_added_numbers),
        "invented_formula_count": _added_count(mutation, "formulas"),
    }
    return {
        "case_id": case.get("id"),
        "case_class": case.get("class"),
        "status": "PASS"
        if not errors and not missing_required and not semantic_failures
        else "FAIL",
        "deterministic_status": "PASS"
        if not errors and not missing_required
        else "FAIL",
        "semantic_status": "PASS" if not semantic_failures else "FAIL",
        "errors": errors,
        "missing_required": missing_required,
        "semantic_assertions": semantic_results,
        "semantic_failures": semantic_failures,
        "metrics": metrics,
    }


def evaluate_system(catalog_path: Path, results_dir: Path | None) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    evidence_mode = str(catalog.get("evidence_mode", "frozen-rewrite"))
    numeric_policy = str(catalog.get("numeric_policy", "declared_added_numbers_only"))
    cases = [item for item in catalog["cases"] if isinstance(item, Mapping)]
    if results_dir is None:
        return {
            "status": NOT_RUN,
            "cases_expected": len(cases),
            "evidence_mode": evidence_mode,
            "numeric_policy": numeric_policy,
            "metrics": None,
            "limitations": ["candidate_results_not_supplied"],
        }
    candidates = _load_candidates(results_dir)
    missing = [str(case["id"]) for case in cases if str(case["id"]) not in candidates]
    if missing:
        return {
            "status": NOT_RUN,
            "cases_expected": len(cases),
            "evidence_mode": evidence_mode,
            "numeric_policy": numeric_policy,
            "metrics": None,
            "limitations": [f"missing_candidate_results:{','.join(missing)}"],
        }

    results = [evaluate_case(case, candidates[str(case["id"])]) for case in cases]
    passed = [item for item in results if item["status"] == "PASS"]

    def rate(items: list[dict[str, Any]], key: str) -> float:
        if not items:
            return 1.0
        return sum(item.get("metrics", {}).get(key, False) for item in items) / len(
            items
        )

    defensive = [item for item in results if item.get("case_class") == "defensive"]
    ai_style = [item for item in results if item.get("case_class") == "ai_style"]
    depth = [item for item in results if item.get("case_class") == "shallow_depth"]
    technical = [
        item for item in results if item.get("case_class") == "terminology_resistance"
    ]
    limitations = [
        item
        for item in results
        if item.get("case_class") in {"clean", "limitation_resistance"}
    ]
    negative = [
        item for item in results if item.get("case_class") == "limitation_resistance"
    ]
    metrics = {
        "cases": len(results),
        "cases_passed": len(passed),
        "hard_error_count": sum(len(item["errors"]) for item in results),
        "semantic_failure_count": sum(
            len(item["semantic_failures"]) for item in results
        ),
        "fact_preservation_rate": rate(results, "protected_elements_unchanged"),
        "key_number_preservation_rate": rate(results, "numbers_preserved"),
        "numeric_binding_protection_rate": rate(results, "numeric_bindings_preserved"),
        "formula_preservation_rate": rate(results, "formulas_preserved"),
        "citation_protection_rate": rate(results, "citations_preserved"),
        "label_ref_protection_rate": rate(results, "labels_and_references_preserved"),
        "defensive_expression_reduction_rate": rate(defensive, "undesirable_reduced"),
        "worklog_narrative_reduction_rate": rate(ai_style, "undesirable_reduced"),
        "ai_mechanical_syntax_reduction_rate": rate(ai_style, "undesirable_reduced"),
        "argument_depth_requirement_rate": rate(depth, "semantic_assertions_pass"),
        "technical_term_preservation_rate": rate(
            technical, "technical_terms_preserved"
        ),
        "necessary_limitation_preservation_rate": rate(
            limitations, "necessary_limitation_preserved"
        ),
        "negative_evidence_preservation_rate": rate(
            negative, "negative_evidence_preserved"
        ),
        "invented_result_count": sum(
            item.get("metrics", {}).get("invented_number_count", 0)
            + item.get("metrics", {}).get("invented_formula_count", 0)
            for item in results
        ),
    }
    return {
        "status": "EXECUTED",
        "evidence_mode": evidence_mode,
        "numeric_policy": numeric_policy,
        "metrics": metrics,
        "cases": results,
        "limitations": [
            "deterministic fidelity and controlled semantic assertions are reported separately",
            "semantic phrase sets are fixture heuristics and still require independent adjudication",
        ],
    }


def evaluate_ab(
    catalog_path: Path, legacy_dir: Path | None, modular_dir: Path | None
) -> dict[str, Any]:
    legacy = evaluate_system(catalog_path, legacy_dir)
    modular = evaluate_system(catalog_path, modular_dir)
    if legacy["status"] != "EXECUTED" or modular["status"] != "EXECUTED":
        return {
            "status": NOT_RUN,
            "legacy": legacy,
            "modular": modular,
            "admission": None,
            "limitations": ["both_real_output_sets_are_required_for_ab"],
        }
    legacy_metrics = legacy["metrics"]
    modular_metrics = modular["metrics"]
    protected_rates = (
        "fact_preservation_rate",
        "numeric_binding_protection_rate",
        "technical_term_preservation_rate",
        "necessary_limitation_preservation_rate",
        "negative_evidence_preservation_rate",
    )
    improvement_rates = (
        "defensive_expression_reduction_rate",
        "worklog_narrative_reduction_rate",
        "ai_mechanical_syntax_reduction_rate",
        "argument_depth_requirement_rate",
    )
    regressions = [
        key
        for key in (*protected_rates, *improvement_rates)
        if modular_metrics[key] < legacy_metrics[key]
    ]
    if modular_metrics["hard_error_count"] or modular_metrics["invented_result_count"]:
        regressions.append("modular_hard_error_count")
    if modular_metrics["semantic_failure_count"]:
        regressions.append("modular_semantic_failure_count")
    return {
        "status": "EXECUTED",
        "legacy": legacy,
        "modular": modular,
        "admission": "PASS" if not regressions else "FAIL",
        "regressions": regressions,
        "limitations": ["admission_is_fixture_contract_only_not_paper_quality"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog", type=Path, default=Path(__file__).with_name("cases.yaml")
    )
    parser.add_argument("--legacy-results", type=Path)
    parser.add_argument("--modular-results", type=Path)
    args = parser.parse_args()
    result = evaluate_ab(args.catalog, args.legacy_results, args.modular_results)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"EXECUTED", NOT_RUN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
