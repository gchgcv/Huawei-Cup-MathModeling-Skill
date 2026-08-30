from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = REPO_ROOT / "shared" / "contracts"
VALIDATOR_PATH = CONTRACT_ROOT / "validate_project_facts.py"
ADAPTER_PATH = CONTRACT_ROOT / "adapters" / "legacy_ledger.py"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _facts() -> dict[str, Any]:
    return {
        "contract_version": "1",
        "fact_set_id": "case-1",
        "sources": [
            {"id": "src-problem", "artifact_id": "problem", "locator": "problem.pdf:p1"},
            {"id": "src-model", "artifact_id": "paper", "locator": "main.tex:section3"},
            {"id": "src-result", "artifact_id": "result", "locator": "result.json:$.value"},
            {"id": "src-claim", "artifact_id": "paper", "locator": "main.tex:section5"},
            {"id": "src-figure", "artifact_id": "figure", "locator": "figures/result.pdf"},
            {"id": "src-citation", "artifact_id": "citation", "locator": "refs.bib:key-a"},
        ],
        "problem": {
            "questions": [{"id": "Q1", "text": "求目标量", "source_ids": ["src-problem"]}]
        },
        "model": {
            "name": "线性规划",
            "source_ids": ["src-model"],
            "assumptions": [{"id": "A1", "text": "容量已知", "source_ids": ["src-model"]}],
            "equations": [
                {"id": "E1", "latex": "x+y=1", "meaning": "守恒关系", "source_ids": ["src-model"]}
            ],
            "parameters": [
                {
                    "id": "P1",
                    "symbol": "c",
                    "meaning": "单位成本",
                    "value": 2.5,
                    "unit": "元",
                    "source_ids": ["src-model"],
                    "evidence_status": "VERIFIED",
                }
            ],
        },
        "results": [
            {
                "id": "R1",
                "question_id": "Q1",
                "value": 12.5,
                "unit": "元",
                "source_ids": ["src-result"],
                "evidence_status": "VERIFIED",
            }
        ],
        "claims": [
            {
                "id": "C1",
                "text": "该方案在给定约束下成本最低。",
                "source_ids": ["src-claim"],
                "evidence_ids": ["R1"],
                "evidence_status": "VERIFIED",
            }
        ],
        "figures": [
            {
                "id": "F1",
                "path": "figures/result.pdf",
                "purpose": "展示方案成本",
                "source_ids": ["src-figure"],
                "evidence_status": "VERIFIED",
            }
        ],
        "citations": [
            {
                "id": "REF1",
                "source": "key-a",
                "source_ids": ["src-citation"],
                "evidence_status": "VERIFIED",
            }
        ],
        "limitations": [],
    }


def _legacy_ledger() -> dict[str, Any]:
    return {
        "project": {"title": "mapping-case"},
        "questions": [
            {
                "id": "Q1",
                "task": "求目标量",
                "model": "线性规划",
                "evidence": ["problem.pdf:p1"],
            }
        ],
        "parameters": [
            {
                "symbol": "c",
                "code_name": "cost",
                "meaning": "单位成本",
                "value": 2.5,
                "unit": "元",
                "source": "data.csv:column-cost",
                "status": "CONFIRMED",
            }
        ],
        "results": [
            {
                "id": "R1",
                "question_id": "Q1",
                "value": 12.5,
                "unit": "元",
                "source": "result.json:$.value",
                "status": "CONFIRMED",
            }
        ],
        "claims": [
            {
                "id": "C1",
                "text": "该方案满足约束。",
                "status": "CONFIRMED",
                "evidence": ["result.json:$.feasible"],
            }
        ],
    }


def test_contract_schemas_are_valid_draft_2020_12() -> None:
    for name in ("project-facts.schema.json", "review-finding.schema.json"):
        schema = json.loads((CONTRACT_ROOT / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_valid_project_facts_passes_schema_and_reference_checks() -> None:
    module = _load_module("project_facts_validator", VALIDATOR_PATH)
    assert module.validate_project_facts(_facts()) == []


def test_unknown_source_and_evidence_references_fail_closed() -> None:
    module = _load_module("project_facts_validator_refs", VALIDATOR_PATH)
    facts = _facts()
    facts["results"][0]["source_ids"] = ["unknown-source"]
    facts["claims"][0]["evidence_ids"] = ["unknown-evidence"]
    errors = module.validate_project_facts(facts)
    assert any("unknown source_id" in item for item in errors)
    assert any("unknown evidence_id" in item for item in errors)


def test_ids_are_globally_unique() -> None:
    module = _load_module("project_facts_validator_ids", VALIDATOR_PATH)
    facts = _facts()
    facts["claims"][0]["id"] = "R1"
    assert any("not globally unique" in item for item in module.validate_project_facts(facts))


def test_verified_claim_requires_evidence_ids() -> None:
    module = _load_module("project_facts_validator_claim", VALIDATOR_PATH)
    facts = _facts()
    facts["claims"][0]["evidence_ids"] = []
    assert any("VERIFIED claim requires evidence_ids" in item for item in module.validate_project_facts(facts))


def test_contract_rejects_workflow_and_submission_state() -> None:
    module = _load_module("project_facts_validator_state", VALIDATOR_PATH)
    for field in ("workflow", "submission_status", "READY_TO_SUBMIT"):
        facts = _facts()
        facts[field] = {}
        assert module.validate_project_facts(facts)


def test_shared_directory_is_not_an_invokable_skill() -> None:
    assert not (CONTRACT_ROOT / "SKILL.md").exists()
    assert not (CONTRACT_ROOT / "manifest.yaml").exists()


def test_review_finding_schema_requires_evidence() -> None:
    schema = json.loads((CONTRACT_ROOT / "review-finding.schema.json").read_text(encoding="utf-8"))
    finding = {
        "finding_id": "F-1",
        "rule_id": "CLAIM-001",
        "severity": "P1",
        "category": "claim_evidence",
        "claim": "范围超过证据。",
        "location": "section 6",
        "evidence": [],
        "recommendation": "由授权角色核对范围。",
        "confidence": "high",
        "limitations": [],
    }
    assert list(Draft202012Validator(schema).iter_errors(finding))


def test_legacy_mapping_is_deterministic_valid_and_non_mutating() -> None:
    adapter = _load_module("legacy_ledger_adapter", ADAPTER_PATH)
    validator = _load_module("project_facts_validator_mapped", VALIDATOR_PATH)
    ledger = _legacy_ledger()
    before = copy.deepcopy(ledger)
    first = adapter.map_legacy_ledger(ledger)
    second = adapter.map_legacy_ledger(ledger)
    assert ledger == before
    assert first == second
    assert first["mapping_status"] == "MAPPED"
    assert validator.validate_project_facts(first["project_facts"]) == []
    assert first["project_facts"]["results"][0]["value"] == 12.5


def test_legacy_mapping_blocks_ambiguous_models() -> None:
    adapter = _load_module("legacy_ledger_adapter_models", ADAPTER_PATH)
    ledger = _legacy_ledger()
    ledger["questions"].append(
        {"id": "Q2", "task": "求另一目标", "model": "非线性规划", "evidence": ["problem.pdf:p2"]}
    )
    mapped = adapter.map_legacy_ledger(ledger)
    assert mapped["mapping_status"] == "NEEDS_MANUAL_MAPPING"
    assert mapped["project_facts"]["model"]["name"] is None
    assert any("multiple Legacy model names" in item for item in mapped["limitations"])


def test_legacy_mapping_blocks_missing_traceability() -> None:
    adapter = _load_module("legacy_ledger_adapter_trace", ADAPTER_PATH)
    ledger = _legacy_ledger()
    ledger["questions"][0]["evidence"] = []
    mapped = adapter.map_legacy_ledger(ledger)
    assert mapped["mapping_status"] == "NEEDS_MANUAL_MAPPING"
    assert any("no traceable evidence" in item for item in mapped["limitations"])


def test_legacy_mapping_does_not_guess_unknown_result_status() -> None:
    adapter = _load_module("legacy_ledger_adapter_result_status", ADAPTER_PATH)
    ledger = _legacy_ledger()
    ledger["results"][0]["status"] = "APPROVED"
    mapped = adapter.map_legacy_ledger(ledger)
    assert mapped["mapping_status"] == "NEEDS_MANUAL_MAPPING"
    assert mapped["project_facts"]["results"] == []
    assert any("unmappable status" in item for item in mapped["limitations"])


def test_validator_and_adapter_have_no_project_write_operations() -> None:
    forbidden = ("write_text(", "write_bytes(", "unlink(", "rename(", "replace(", "shutil.move")
    for path in (VALIDATOR_PATH, ADAPTER_PATH):
        text = path.read_text(encoding="utf-8")
        assert all(token not in text for token in forbidden)


def test_writing_and_review_reference_same_project_facts_contract_read_only() -> None:
    import yaml

    contract_path = "../../shared/contracts/project-facts.schema.json"
    for skill_name in ("huawei-cup-writing", "huawei-cup-review"):
        manifest_path = REPO_ROOT / "skills" / skill_name / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        assert manifest["shared_contracts"]["access"] == "read_only"
        assert manifest["shared_contracts"]["project_facts"] == contract_path


def test_legacy_templates_remain_present_and_unchanged_by_mapping() -> None:
    legacy = REPO_ROOT / "legacy" / "huawei-cup-modeling-writing-v0.9.1" / "templates"
    assert (legacy / "modeling-ledger.json").is_file()
    assert (legacy / "modeling-ledger.yaml").is_file()
