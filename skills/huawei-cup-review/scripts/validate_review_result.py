#!/usr/bin/env python3
"""Validate the modular v2 Review result and its Shared Rule IDs."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_ROOT / "schemas" / "review-result.schema.json"
SHARED_ROOT = SKILL_ROOT.parents[1] / "shared" / "paper-quality-standard"
SHARED_CONTRACT_ROOT = SKILL_ROOT.parents[1] / "shared" / "contracts"
FINDING_SCHEMA_PATH = SHARED_CONTRACT_ROOT / "review-finding.schema.json"
RULE_HEADER = re.compile(r"^## ([A-Z]+-[0-9]{3}) —", re.MULTILINE)
STATUS_MEANING = "CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY"


def load_rule_ids(shared_root: Path = SHARED_ROOT) -> set[str]:
    """Load authoritative Rule IDs from the Shared registry directory."""
    if not (shared_root / "README.md").is_file():
        raise FileNotFoundError(f"Shared registry missing: {shared_root / 'README.md'}")
    rule_ids: set[str] = set()
    for path in sorted(shared_root.glob("*.md")):
        if path.name == "README.md":
            continue
        rule_ids.update(RULE_HEADER.findall(path.read_text(encoding="utf-8")))
    if not rule_ids:
        raise ValueError(f"No Shared Rule IDs found in {shared_root}")
    return rule_ids


def validate_review_result(result: Mapping[str, Any]) -> list[str]:
    """Return deterministic schema and Shared Rule-ID validation messages."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    finding_schema = json.loads(FINDING_SCHEMA_PATH.read_text(encoding="utf-8"))
    registry = Registry().with_resource(
        finding_schema["$id"], Resource.from_contents(finding_schema)
    )
    validator = Draft202012Validator(schema, registry=registry)
    schema_errors = sorted(
        validator.iter_errors(dict(result)), key=lambda item: list(item.absolute_path)
    )
    errors = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in schema_errors
    ]
    try:
        known_rule_ids = load_rule_ids()
    except (OSError, ValueError) as exc:
        return [*errors, str(exc)]
    findings = result.get("findings", [])
    if isinstance(findings, list):
        finding_ids: list[str] = []
        for index, finding in enumerate(findings):
            if not isinstance(finding, Mapping):
                continue
            finding_id = finding.get("finding_id")
            if isinstance(finding_id, str):
                finding_ids.append(finding_id)
            rule_id = finding.get("rule_id")
            if isinstance(rule_id, str) and rule_id not in known_rule_ids:
                errors.append(f"findings.{index}.rule_id: unknown Shared Rule ID: {rule_id}")
        duplicates = sorted({item for item in finding_ids if finding_ids.count(item) > 1})
        for finding_id in duplicates:
            errors.append(f"findings: duplicate finding_id: {finding_id}")
    return errors


def contract_failure(task_id: str, limitations: list[str]) -> dict[str, Any]:
    """Return a fail-closed, read-only result object without persistence."""
    return {
        "contract_version": "2",
        "task_id": task_id,
        "call_status": "CONTRACT_ERROR",
        "status_meaning": STATUS_MEANING,
        "read_only": True,
        "writes_performed": [],
        "findings": [],
        "limitations": limitations,
    }


def enforce_review_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return the result or a sanitized fail-closed result object."""
    errors = validate_review_result(result)
    if not errors:
        return dict(result)
    return contract_failure(str(result.get("task_id", "review-contract")), errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="Review result JSON to validate")
    args = parser.parse_args()
    try:
        value = json.loads(args.result.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not isinstance(value, dict):
        print("ERROR: result root must be an object", file=sys.stderr)
        return 2
    errors = validate_review_result(value)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"REVIEW_RESULT_VALIDATION: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
