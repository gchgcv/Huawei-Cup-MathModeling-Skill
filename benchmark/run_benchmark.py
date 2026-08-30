#!/usr/bin/env python3
"""Run the read-only Phase 6 Writing, Review, and Integration benchmark."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

BENCHMARK_ROOT = Path(__file__).resolve().parent
NOT_RUN = "NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _review_admission(result: dict[str, Any]) -> bool:
    metrics = result.get("metrics")
    if not isinstance(metrics, dict):
        return False
    return (
        metrics.get("seeded_fault_recall") == 1.0
        and metrics.get("false_positive_count") == 0
        and metrics.get("false_negative_count") == 0
        and metrics.get("unsupported_finding_count") == 0
        and metrics.get("duplicate_finding_count") == 0
        and metrics.get("evidence_coverage") == 1.0
        and metrics.get("mutation_count") == 0
        and metrics.get("clean_case_empty_findings_rate") == 1.0
    )


def _integration_admission(result: dict[str, Any]) -> bool:
    metrics = result.get("metrics")
    if not isinstance(metrics, dict):
        return False
    return (
        metrics.get("cases") == metrics.get("cases_passed")
        and metrics.get("review_immutability_rate") == 1.0
        and metrics.get("review_mutation_count") == 0
        and metrics.get("shared_rule_id_consistency_rate") == 1.0
        and metrics.get("finding_handoff_coverage") == 1.0
    )


def run(
    legacy_writing: Path | None,
    modular_writing: Path | None,
    review_results: Path | None,
    integration_results: Path | None,
) -> dict[str, Any]:
    writing_module = _load(
        "phase6_writing_evaluator",
        BENCHMARK_ROOT / "writing" / "evaluate_writing.py",
    )
    review_module = _load(
        "phase6_review_evaluator",
        BENCHMARK_ROOT / "review" / "evaluate_review.py",
    )
    integration_module = _load(
        "phase6_integration_evaluator",
        BENCHMARK_ROOT / "integration" / "evaluate_integration.py",
    )
    writing = writing_module.evaluate_ab(
        BENCHMARK_ROOT / "writing" / "cases.yaml",
        legacy_writing,
        modular_writing,
    )
    review = review_module.evaluate_benchmark(
        BENCHMARK_ROOT / "review" / "cases.yaml",
        review_results,
    )
    integration = integration_module.evaluate_benchmark(
        BENCHMARK_ROOT / "integration" / "cases.yaml",
        integration_results,
    )
    results = {"writing_ab": writing, "review": review, "integration": integration}
    if any(item.get("status") != "EXECUTED" for item in results.values()):
        return {
            "status": NOT_RUN,
            "admission": None,
            "results": results,
            "limitations": ["all_real_output_sets_are_required", "no_quality_gain_is_inferred"],
        }
    passed = (
        writing.get("admission") == "PASS"
        and _review_admission(review)
        and _integration_admission(integration)
    )
    return {
        "status": "EXECUTED",
        "admission": "PASS" if passed else "FAIL",
        "results": results,
        "limitations": ["admission_applies_to_declared_cases_only_not_submission_quality"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-writing", type=Path)
    parser.add_argument("--modular-writing", type=Path)
    parser.add_argument("--review-results", type=Path)
    parser.add_argument("--integration-results", type=Path)
    args = parser.parse_args()
    result = run(
        args.legacy_writing,
        args.modular_writing,
        args.review_results,
        args.integration_results,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"EXECUTED", NOT_RUN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
