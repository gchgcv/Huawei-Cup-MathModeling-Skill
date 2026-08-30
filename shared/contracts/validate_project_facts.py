#!/usr/bin/env python3
"""Read-only validation for the minimal Project Facts contract."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


CONTRACT_ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = CONTRACT_ROOT / "project-facts.schema.json"


def _items(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _duplicate_ids(items: list[Mapping[str, Any]]) -> set[str]:
    ids = [item.get("id") for item in items if isinstance(item.get("id"), str)]
    return {item for item in ids if ids.count(item) > 1}


def validate_project_facts(value: Mapping[str, Any]) -> list[str]:
    """Return schema, identity, and reference-integrity errors."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    schema_errors = sorted(
        validator.iter_errors(dict(value)), key=lambda item: list(item.absolute_path)
    )
    errors = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in schema_errors
    ]

    sources = _items(value.get("sources"))
    source_ids = {item["id"] for item in sources if isinstance(item.get("id"), str)}
    problem = value.get("problem") if isinstance(value.get("problem"), Mapping) else {}
    questions = _items(problem.get("questions"))
    model = value.get("model") if isinstance(value.get("model"), Mapping) else {}
    assumptions = _items(model.get("assumptions"))
    equations = _items(model.get("equations"))
    parameters = _items(model.get("parameters"))
    results = _items(value.get("results"))
    claims = _items(value.get("claims"))
    figures = _items(value.get("figures"))
    citations = _items(value.get("citations"))

    groups = {
        "sources": sources,
        "questions": questions,
        "assumptions": assumptions,
        "equations": equations,
        "parameters": parameters,
        "results": results,
        "claims": claims,
        "figures": figures,
        "citations": citations,
    }
    for group_name, group_items in groups.items():
        for item_id in sorted(_duplicate_ids(group_items)):
            errors.append(f"{group_name}: duplicate id: {item_id}")

    fact_items = [
        *questions,
        *assumptions,
        *equations,
        *parameters,
        *results,
        *claims,
        *figures,
        *citations,
    ]
    fact_ids = [item["id"] for item in fact_items if isinstance(item.get("id"), str)]
    for item_id in sorted({item for item in fact_ids if fact_ids.count(item) > 1}):
        errors.append(f"facts: id is not globally unique: {item_id}")

    def check_source_refs(owner: str, refs: object) -> None:
        if not isinstance(refs, list):
            return
        for source_id in refs:
            if isinstance(source_id, str) and source_id not in source_ids:
                errors.append(f"{owner}: unknown source_id: {source_id}")

    check_source_refs("model", model.get("source_ids"))
    for group_name, group_items in groups.items():
        if group_name == "sources":
            continue
        for item in group_items:
            check_source_refs(f"{group_name}.{item.get('id', '<unknown>')}", item.get("source_ids"))

    question_ids = {item["id"] for item in questions if isinstance(item.get("id"), str)}
    for result in results:
        question_id = result.get("question_id")
        if isinstance(question_id, str) and question_id not in question_ids:
            errors.append(f"results.{result.get('id', '<unknown>')}: unknown question_id: {question_id}")

    evidence_targets = source_ids | set(fact_ids)
    for claim in claims:
        evidence_ids = claim.get("evidence_ids")
        if isinstance(evidence_ids, list):
            for evidence_id in evidence_ids:
                if isinstance(evidence_id, str) and evidence_id not in evidence_targets:
                    errors.append(f"claims.{claim.get('id', '<unknown>')}: unknown evidence_id: {evidence_id}")
        if claim.get("evidence_status") == "VERIFIED" and not evidence_ids:
            errors.append(f"claims.{claim.get('id', '<unknown>')}: VERIFIED claim requires evidence_ids")

    for group_name in ("parameters", "results", "claims", "figures", "citations"):
        for item in groups[group_name]:
            if item.get("evidence_status") == "VERIFIED" and not item.get("source_ids"):
                errors.append(f"{group_name}.{item.get('id', '<unknown>')}: VERIFIED fact requires source_ids")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_facts", type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(args.project_facts.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not isinstance(value, dict):
        print("ERROR: Project Facts root must be an object", file=sys.stderr)
        return 2
    errors = validate_project_facts(value)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"PROJECT_FACTS_VALIDATION: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
