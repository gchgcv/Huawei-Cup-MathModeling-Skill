#!/usr/bin/env python3
"""Conservatively map a Legacy modeling ledger to minimal Project Facts."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

CONTRACT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = CONTRACT_ROOT / "validate_project_facts.py"


def _load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("project_facts_contract_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Project Facts validator: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_project_facts


validate_project_facts = _load_validator()


STATUS_MAP = {
    "CONFIRMED": "VERIFIED",
    "DERIVED": "VERIFIED",
    "ASSUMED": "UNVERIFIED",
    "MISSING": "MISSING",
}


class SourceRegistry:
    """Create stable source references while preserving Legacy locators."""

    def __init__(self) -> None:
        self._by_locator: dict[str, str] = {}
        self.items: list[dict[str, str]] = []

    def add(self, locator: str) -> str:
        normalized = locator.strip()
        if normalized in self._by_locator:
            return self._by_locator[normalized]
        source_id = f"legacy-source-{len(self.items) + 1:03d}"
        self._by_locator[normalized] = source_id
        self.items.append(
            {"id": source_id, "artifact_id": "legacy-modeling-ledger", "locator": normalized}
        )
        return source_id


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _source_ids(registry: SourceRegistry, value: object) -> list[str]:
    return [registry.add(item) for item in _strings(value)]


def map_legacy_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Return a mapping envelope; never mutate the input ledger."""
    registry = SourceRegistry()
    limitations: list[str] = []
    questions: list[dict[str, Any]] = []
    question_models: dict[str, list[str]] = {}

    raw_questions = ledger.get("questions")
    if not isinstance(raw_questions, list):
        raw_questions = []
        limitations.append("legacy questions is not a list")
    for index, raw in enumerate(raw_questions):
        if not isinstance(raw, Mapping):
            limitations.append(f"questions[{index}] is not an object")
            continue
        question_id = raw.get("id")
        text = raw.get("task")
        sources = _source_ids(registry, raw.get("evidence"))
        if not isinstance(question_id, str) or not question_id.strip():
            limitations.append(f"questions[{index}] has no stable id")
            continue
        if not isinstance(text, str) or not text.strip():
            limitations.append(f"questions[{index}] has no task text")
            continue
        if not sources:
            limitations.append(f"questions[{index}] has no traceable evidence")
            continue
        questions.append({"id": question_id, "text": text, "source_ids": sources})
        model_name = raw.get("model")
        if isinstance(model_name, str) and model_name.strip():
            question_models.setdefault(model_name.strip(), []).extend(sources)

    model_names = sorted(question_models)
    model_name: str | None = model_names[0] if len(model_names) == 1 else None
    model_sources = sorted(set(question_models.get(model_name, []))) if model_name else []
    if len(model_names) > 1:
        limitations.append(f"multiple Legacy model names cannot be merged safely: {model_names}")

    parameters: list[dict[str, Any]] = []
    raw_parameters = ledger.get("parameters")
    if not isinstance(raw_parameters, list):
        raw_parameters = []
        limitations.append("legacy parameters is not a list")
    for index, raw in enumerate(raw_parameters):
        if not isinstance(raw, Mapping):
            limitations.append(f"parameters[{index}] is not an object")
            continue
        status = raw.get("status")
        symbol = raw.get("symbol")
        code_name = raw.get("code_name")
        if status == "MISSING" and not symbol and not code_name and raw.get("value") is None:
            continue
        parameter_id = symbol or code_name
        if not isinstance(parameter_id, str) or not parameter_id.strip():
            limitations.append(f"parameters[{index}] has no stable symbol or code_name")
            continue
        if status not in STATUS_MAP:
            limitations.append(f"parameters[{index}] has unmappable status: {status!r}")
            continue
        sources = _source_ids(registry, raw.get("source"))
        if status != "MISSING" and not sources:
            limitations.append(f"parameters[{index}] has no traceable source")
            continue
        parameters.append(
            {
                "id": parameter_id,
                "symbol": str(symbol or code_name),
                "meaning": str(raw.get("meaning", "")),
                "value": raw.get("value"),
                "unit": str(raw.get("unit", "")),
                "source_ids": sources,
                "evidence_status": STATUS_MAP[status],
            }
        )

    results: list[dict[str, Any]] = []
    raw_results = ledger.get("results")
    if not isinstance(raw_results, list):
        raw_results = []
        limitations.append("legacy results is not a list")
    for index, raw in enumerate(raw_results):
        if not isinstance(raw, Mapping):
            limitations.append(f"results[{index}] is not an object")
            continue
        required = ("id", "question_id", "value", "source")
        missing = [field for field in required if field not in raw or raw.get(field) in (None, "")]
        if missing:
            limitations.append(f"results[{index}] cannot map fields: {missing}")
            continue
        status = raw.get("status")
        if status is None:
            evidence_status = "UNVERIFIED"
        elif status in STATUS_MAP:
            evidence_status = STATUS_MAP[status]
        else:
            limitations.append(f"results[{index}] has unmappable status: {status!r}")
            continue
        results.append(
            {
                "id": str(raw["id"]),
                "question_id": str(raw["question_id"]),
                "value": raw["value"],
                "unit": str(raw.get("unit", "")),
                "source_ids": _source_ids(registry, raw["source"]),
                "evidence_status": evidence_status,
            }
        )

    claims: list[dict[str, Any]] = []
    raw_claims = ledger.get("claims")
    if not isinstance(raw_claims, list):
        raw_claims = []
        limitations.append("legacy claims is not a list")
    for index, raw in enumerate(raw_claims):
        if not isinstance(raw, Mapping):
            limitations.append(f"claims[{index}] is not an object")
            continue
        claim_id = raw.get("id")
        text = raw.get("text")
        status = raw.get("status")
        if not isinstance(claim_id, str) or not claim_id.strip():
            limitations.append(f"claims[{index}] has no stable id")
            continue
        if not isinstance(text, str) or not text.strip():
            limitations.append(f"claims[{index}] has no text")
            continue
        if status not in STATUS_MAP:
            limitations.append(f"claims[{index}] has unmappable status: {status!r}")
            continue
        sources = _source_ids(registry, raw.get("evidence"))
        if status != "MISSING" and not sources:
            limitations.append(f"claims[{index}] has no traceable evidence")
            continue
        claims.append(
            {
                "id": claim_id,
                "text": text,
                "source_ids": sources,
                "evidence_ids": sources,
                "evidence_status": STATUS_MAP[status],
            }
        )

    project = ledger.get("project") if isinstance(ledger.get("project"), Mapping) else {}
    title = project.get("title")
    fact_set_id = f"legacy-ledger:{title.strip()}" if isinstance(title, str) and title.strip() else "legacy-ledger:untitled"
    project_facts = {
        "contract_version": "1",
        "fact_set_id": fact_set_id,
        "sources": registry.items,
        "problem": {"questions": questions},
        "model": {
            "name": model_name,
            "source_ids": model_sources,
            "assumptions": [],
            "equations": [],
            "parameters": parameters,
        },
        "results": results,
        "claims": claims,
        "figures": [],
        "citations": [],
        "limitations": list(limitations),
    }
    validation_errors = validate_project_facts(project_facts)
    all_limitations = [*limitations, *validation_errors]
    project_facts["limitations"] = all_limitations
    return {
        "mapping_status": "MAPPED" if not all_limitations else "NEEDS_MANUAL_MAPPING",
        "project_facts": project_facts,
        "limitations": all_limitations,
    }


def _load(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    value = yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
    if not isinstance(value, Mapping):
        raise ValueError("Legacy ledger root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        ledger = _load(args.ledger)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    result = map_legacy_ledger(ledger)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["mapping_status"] == "MAPPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
