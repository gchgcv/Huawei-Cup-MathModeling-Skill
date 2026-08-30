from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark"
WRITING_EVALUATOR = BENCHMARK_ROOT / "writing" / "evaluate_writing.py"
REVIEW_EVALUATOR = BENCHMARK_ROOT / "review" / "evaluate_review.py"
INTEGRATION_EVALUATOR = BENCHMARK_ROOT / "integration" / "evaluate_integration.py"
AGGREGATOR = BENCHMARK_ROOT / "run_benchmark.py"
RULE_HEADER = re.compile(r"^## ([A-Z]+-[0-9]{3}) —", re.MULTILINE)


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _review_result(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contract_version": "2",
        "task_id": "phase6-test",
        "call_status": "SUCCESS",
        "status_meaning": "CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY",
        "read_only": True,
        "writes_performed": [],
        "findings": findings,
        "limitations": [],
    }


def _finding(
    finding_id: str = "finding-1",
    rule_id: str = "ADW-001",
    artifact_id: str = "paper",
    location: str = "paragraph 1",
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "rule_id": rule_id,
        "severity": "P2",
        "category": "style",
        "claim": "The opening is an unsupported disclaimer.",
        "location": location,
        "evidence": [
            {
                "artifact_id": artifact_id,
                "locator": location,
                "reason": "The disclaimer precedes the supported scope.",
            }
        ],
        "recommendation": "Let an authorized Writer state the supported scope directly.",
        "confidence": "high",
        "limitations": [],
    }


def _known_rule_ids() -> set[str]:
    standard = REPO_ROOT / "shared" / "paper-quality-standard"
    return {
        rule_id
        for path in standard.glob("*.md")
        for rule_id in RULE_HEADER.findall(path.read_text(encoding="utf-8"))
    }


def test_catalogs_are_explicitly_not_run_and_use_known_rule_ids() -> None:
    known = _known_rule_ids()
    for area in ("writing", "review", "integration"):
        catalog = yaml.safe_load(
            (BENCHMARK_ROOT / area / "cases.yaml").read_text(encoding="utf-8")
        )
        assert catalog["status"] == "CATALOG_VALIDATED_ONLY"
        assert catalog["execution_status"] == "NOT_RUN_AGENT_OUTPUTS_UNAVAILABLE"
        assert catalog["cases"]
        for case in catalog["cases"]:
            assert set(case.get("rules", [])) <= known
            assert set(case.get("accepted_rule_ids", [])) <= known


def test_writing_catalog_covers_six_legacy_ab_classes() -> None:
    catalog = yaml.safe_load(
        (BENCHMARK_ROOT / "writing" / "cases.yaml").read_text(encoding="utf-8")
    )
    classes = {case["class"] for case in catalog["cases"]}
    assert {
        "defensive",
        "ai_style",
        "shallow_depth",
        "clean",
        "terminology_resistance",
        "limitation_resistance",
    } <= classes


def test_manifest_paths_and_required_metric_sets_are_complete() -> None:
    manifest = yaml.safe_load(
        (BENCHMARK_ROOT / "manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["benchmark"]["read_only"] is True
    assert manifest["benchmark"]["persists_report"] is False
    for group in ("catalogs", "evaluators"):
        for path in manifest[group].values():
            assert (BENCHMARK_ROOT / path).is_file()
    assert "invented_result_count" in manifest["required_metrics"]["writing"]
    assert "numeric_binding_protection_rate" in manifest["required_metrics"]["writing"]
    assert "seeded_fault_recall" in manifest["required_metrics"]["review"]
    assert "review_immutability_rate" in manifest["required_metrics"]["integration"]


def test_benchmarks_without_real_outputs_return_not_run() -> None:
    writing = _load_module("phase6_writing_not_run", WRITING_EVALUATOR)
    review = _load_module("phase6_review_not_run", REVIEW_EVALUATOR)
    integration = _load_module("phase6_integration_not_run", INTEGRATION_EVALUATOR)
    assert (
        writing.evaluate_ab(BENCHMARK_ROOT / "writing" / "cases.yaml", None, None)[
            "status"
        ]
        == writing.NOT_RUN
    )
    assert (
        review.evaluate_benchmark(BENCHMARK_ROOT / "review" / "cases.yaml", None)[
            "status"
        ]
        == review.NOT_RUN
    )
    assert (
        integration.evaluate_benchmark(
            BENCHMARK_ROOT / "integration" / "cases.yaml", None
        )["status"]
        == integration.NOT_RUN
    )
    aggregate = _load_module("phase6_aggregate_not_run", AGGREGATOR)
    overall = aggregate.run(None, None, None, None)
    assert overall["status"] == aggregate.NOT_RUN
    assert overall["admission"] is None


def test_evaluators_load_raw_agent_bundles(tmp_path: Path) -> None:
    writing = _load_module("phase6_writing_bundle", WRITING_EVALUATOR)
    review = _load_module("phase6_review_bundle", REVIEW_EVALUATOR)
    integration = _load_module("phase6_integration_bundle", INTEGRATION_EVALUATOR)

    writing_dir = tmp_path / "writing"
    review_dir = tmp_path / "review"
    integration_dir = tmp_path / "integration"
    writing_dir.mkdir()
    review_dir.mkdir()
    integration_dir.mkdir()

    (writing_dir / "bundle.json").write_text(
        json.dumps(
            {
                "system_under_test": "modular-writing",
                "outputs": [{"case_id": "case-1", "output_text": "text"}],
            }
        ),
        encoding="utf-8",
    )
    (review_dir / "bundle.json").write_text(
        json.dumps(
            {"results": [{"case_id": "case-1", "review_result": _review_result([])}]}
        ),
        encoding="utf-8",
    )
    (integration_dir / "bundle.json").write_text(
        json.dumps({"results": [{"case_id": "case-1", "value": 1}]}),
        encoding="utf-8",
    )

    assert (
        writing._load_candidates(writing_dir)["case-1"]["system_under_test"]
        == "modular-writing"
    )
    assert review._load_results(review_dir)["case-1"]["read_only"] is True
    assert integration._load_results(integration_dir)["case-1"]["value"] == 1


def test_writing_evaluator_accepts_evidence_preserving_scope_rewrite() -> None:
    module = _load_module("phase6_writing_good", WRITING_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "writing" / "cases.yaml")
    case = next(item for item in catalog["cases"] if item["id"] == "defensive_scope")
    candidate = {
        "case_id": "defensive_scope",
        "system_under_test": "modular-writing",
        "output_text": "样本覆盖 A 市 2024 年数据；在该范围内，模型满足 $x+y=1$，成本为 12.5 万元，依据\\cite{source-a}。",
    }
    result = module.evaluate_case(case, candidate)
    assert result["status"] == "PASS"
    assert result["metrics"]["undesirable_reduced"] is True
    assert result["metrics"]["protected_elements_unchanged"] is True


def test_writing_evaluator_rejects_number_and_limitation_mutation() -> None:
    module = _load_module("phase6_writing_bad", WRITING_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "writing" / "cases.yaml")
    number_case = next(
        item for item in catalog["cases"] if item["id"] == "defensive_scope"
    )
    number_candidate = {
        "case_id": "defensive_scope",
        "system_under_test": "modular-writing",
        "output_text": str(number_case["input_text"]).replace("12.5", "13.5"),
    }
    number_result = module.evaluate_case(number_case, number_candidate)
    assert number_result["status"] == "FAIL"
    assert "protected_numbers_changed" in number_result["errors"]
    assert number_result["metrics"]["invented_number_count"] == 1

    limitation_case = next(
        item for item in catalog["cases"] if item["id"] == "necessary_limitation"
    )
    limitation_candidate = {
        "case_id": "necessary_limitation",
        "system_under_test": "modular-writing",
        "output_text": "方案在给定成本约束下可行。",
    }
    limitation_result = module.evaluate_case(limitation_case, limitation_candidate)
    assert limitation_result["status"] == "FAIL"
    assert limitation_result["deterministic_status"] == "PASS"
    assert limitation_result["semantic_status"] == "FAIL"
    assert "seasonal_confounding_preserved" in limitation_result["semantic_failures"]


def test_writing_evaluator_separates_fidelity_from_semantic_paraphrase() -> None:
    module = _load_module("phase6_writing_semantic", WRITING_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "writing" / "cases.yaml")
    limitation_case = next(
        item for item in catalog["cases"] if item["id"] == "necessary_limitation"
    )
    candidate = {
        "case_id": "necessary_limitation",
        "system_under_test": "modular-writing",
        "output_text": "方案在给定成本约束下可行，但其能耗指标不占优；由于没有控制季节因素，现有结果仅用于描述观测关系，不能作因果解释。",
    }
    result = module.evaluate_case(limitation_case, candidate)
    assert result["deterministic_status"] == "PASS"
    assert result["semantic_status"] == "PASS"
    assert result["metrics"]["negative_evidence_preserved"] is True
    assert result["metrics"]["necessary_limitation_preserved"] is True


def test_writing_evaluator_allows_only_declared_derived_numbers() -> None:
    module = _load_module("phase6_writing_derived", WRITING_EVALUATOR)
    case = {
        "id": "derived",
        "class": "clean",
        "input_text": "误差由 4.8% 降至 3.1%。",
        "required_phrases": ["4.8%", "3.1%"],
        "protected_phrases": ["4.8%", "3.1%"],
        "protected_kinds": [],
        "allowed_added_numbers": ["1.7"],
    }
    candidate = {
        "case_id": "derived",
        "system_under_test": "modular-writing",
        "output_text": "误差由 4.8% 降至 3.1%，即下降 1.7 个百分点。",
    }
    result = module.evaluate_case(case, candidate)
    assert result["deterministic_status"] == "PASS"
    assert result["metrics"]["declared_derived_number_count"] == 1
    assert result["metrics"]["undeclared_added_number_count"] == 0


def test_writing_ab_rejects_modular_semantic_failure(tmp_path: Path) -> None:
    module = _load_module("phase6_writing_semantic_gate", WRITING_EVALUATOR)
    catalog = {
        "cases": [
            {
                "id": "meaning",
                "class": "shallow_depth",
                "input_text": "指标为 8.4。",
                "required_phrases": ["8.4"],
                "protected_phrases": ["8.4"],
                "allowed_added_numbers": [],
                "protected_kinds": [],
                "semantic_assertions": [
                    {
                        "id": "result_relevance",
                        "kind": "argument_depth",
                        "any_phrases": ["表明"],
                    }
                ],
            }
        ]
    }
    catalog_path = tmp_path / "cases.yaml"
    legacy_dir = tmp_path / "legacy"
    modular_dir = tmp_path / "modular"
    legacy_dir.mkdir()
    modular_dir.mkdir()
    catalog_path.write_text(yaml.safe_dump(catalog, allow_unicode=True), encoding="utf-8")
    (legacy_dir / "meaning.json").write_text(
        json.dumps(
            {
                "case_id": "meaning",
                "system_under_test": "legacy-v0.9.1",
                "output_text": "指标为 8.4。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (modular_dir / "meaning.json").write_text(
        json.dumps(
            {
                "case_id": "meaning",
                "system_under_test": "modular-writing-phase6-repair2",
                "output_text": "指标为 8.4。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = module.evaluate_ab(catalog_path, legacy_dir, modular_dir)
    assert result["admission"] == "FAIL"
    assert "modular_semantic_failure_count" in result["regressions"]


def test_review_evaluator_accepts_valid_fault_and_clean_empty_case() -> None:
    module = _load_module("phase6_review_good", REVIEW_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "review" / "cases.yaml")
    fault = next(
        item for item in catalog["cases"] if item["id"] == "fault_disclaimer_first"
    )
    clean = next(item for item in catalog["cases"] if item["id"] == "resistance_clean")
    fault_result = module.evaluate_case(fault, _review_result([_finding()]))
    clean_result = module.evaluate_case(clean, _review_result([]))
    assert fault_result["status"] == "PASS"
    assert fault_result["metrics"]["seeded_fault_detected"] is True
    assert clean_result["status"] == "PASS"
    assert clean_result["metrics"]["clean_case_empty"] is True


def test_review_evaluator_counts_false_positive_unsupported_and_duplicate() -> None:
    module = _load_module("phase6_review_bad", REVIEW_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "review" / "cases.yaml")
    clean = next(item for item in catalog["cases"] if item["id"] == "resistance_clean")
    false_positive = module.evaluate_case(
        clean, _review_result([_finding(rule_id="AI-001")])
    )
    assert false_positive["status"] == "FAIL"
    assert false_positive["metrics"]["false_positive"] == 1
    assert false_positive["metrics"]["unsupported_finding_count"] == 1

    fault = next(
        item for item in catalog["cases"] if item["id"] == "fault_disclaimer_first"
    )
    duplicate = module.evaluate_case(
        fault,
        _review_result(
            [
                _finding(finding_id="finding-1"),
                _finding(finding_id="finding-2"),
            ]
        ),
    )
    assert duplicate["status"] == "FAIL"
    assert duplicate["metrics"]["duplicate_finding_count"] == 1


def test_review_aggregate_metrics_cover_fault_and_resistance(tmp_path: Path) -> None:
    module = _load_module("phase6_review_aggregate", REVIEW_EVALUATOR)
    catalog = {
        "source_access_policy": {
            "old_problem_training": False,
            "answer_artifact_access": False,
        },
        "cases": [
            {
                "id": "fault",
                "expectation": "finding",
                "artifact_id": "paper",
                "accepted_rule_ids": ["ADW-001"],
            },
            {
                "id": "clean",
                "expectation": "empty_findings",
                "artifact_id": "paper",
                "accepted_rule_ids": [],
            },
        ],
    }
    catalog_path = tmp_path / "cases.yaml"
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    catalog_path.write_text(
        yaml.safe_dump(catalog, allow_unicode=True), encoding="utf-8"
    )
    (results_dir / "fault.json").write_text(
        json.dumps(_review_result([_finding()])), encoding="utf-8"
    )
    (results_dir / "clean.json").write_text(
        json.dumps(_review_result([])), encoding="utf-8"
    )
    result = module.evaluate_benchmark(catalog_path, results_dir)
    assert result["status"] == "EXECUTED"
    assert result["metrics"]["seeded_fault_recall"] == 1.0
    assert result["metrics"]["false_positive_count"] == 0
    assert result["metrics"]["evidence_coverage"] == 1.0
    assert result["metrics"]["clean_case_empty_findings_rate"] == 1.0


def test_integration_accepts_immutable_review_and_complete_handoff() -> None:
    module = _load_module("phase6_integration_good", INTEGRATION_EVALUATOR)
    case = {
        "id": "integration-case",
        "expected_review": "findings_allowed",
    }
    output = "在给定样本内，成本为 12.5。"
    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    envelope = {
        "case_id": "integration-case",
        "writing_output_text": output,
        "writing_rule_ids": ["ADW-003"],
        "review_input_sha256": digest,
        "review_output_sha256": digest,
        "review_result": _review_result([_finding()]),
        "next_writer_handoff": {
            "finding_ids": ["finding-1"],
            "understood_rule_ids": ["ADW-001"],
        },
    }
    result = module.evaluate_case(case, envelope)
    assert result["status"] == "PASS"
    assert result["metrics"]["review_output_unchanged"] is True
    assert result["metrics"]["finding_handoff_coverage"] == 1.0


def test_integration_rejects_mutation_and_incomplete_handoff() -> None:
    module = _load_module("phase6_integration_bad", INTEGRATION_EVALUATOR)
    case = {"id": "integration-case", "expected_review": "findings_allowed"}
    output = "结果为 12.5。"
    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    envelope = {
        "case_id": "integration-case",
        "writing_output_text": output,
        "writing_rule_ids": ["CLAIM-001"],
        "review_input_sha256": digest,
        "review_output_sha256": "0" * 64,
        "review_result": _review_result([_finding()]),
        "next_writer_handoff": {"finding_ids": [], "understood_rule_ids": []},
    }
    result = module.evaluate_case(case, envelope)
    assert result["status"] == "FAIL"
    assert "review_mutated_writer_output" in result["errors"]
    assert "finding_handoff_incomplete" in result["errors"]


def test_evaluators_are_read_only_and_do_not_depend_on_external_runtime() -> None:
    forbidden_writes = (
        "write_text(",
        "write_bytes(",
        "unlink(",
        "rename(",
        "shutil.move",
    )
    forbidden_runtime = (
        "external-layer",
        "modeling-integrations",
        "provider_environment",
    )
    for path in (
        WRITING_EVALUATOR,
        REVIEW_EVALUATOR,
        INTEGRATION_EVALUATOR,
        AGGREGATOR,
    ):
        text = path.read_text(encoding="utf-8")
        assert all(token not in text for token in forbidden_writes)
        assert all(token not in text for token in forbidden_runtime)


def test_evaluation_does_not_mutate_candidate_objects() -> None:
    module = _load_module("phase6_review_immutable", REVIEW_EVALUATOR)
    catalog = module.load_catalog(BENCHMARK_ROOT / "review" / "cases.yaml")
    case = next(
        item for item in catalog["cases"] if item["id"] == "fault_disclaimer_first"
    )
    result = _review_result([_finding()])
    before = copy.deepcopy(result)
    module.evaluate_case(case, result)
    assert result == before
