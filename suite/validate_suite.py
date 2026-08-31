#!/usr/bin/env python3
"""Validate Huawei Cup Modeling Suite deployment and version compatibility."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"YAML root must be an object: {path}")
    return value


def _inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_file(
    root: Path,
    relative_path: object,
    errors: list[str],
    label: str,
) -> Path | None:
    if not isinstance(relative_path, str) or not relative_path:
        errors.append(f"{label}:path_missing")
        return None
    resolved = (root / relative_path).resolve()
    if not _inside(root.resolve(), resolved):
        errors.append(f"{label}:path_escapes_suite:{relative_path}")
        return None
    if not resolved.is_file():
        errors.append(f"{label}:file_missing:{relative_path}")
    return resolved


def _component_identity(manifest: Mapping[str, Any]) -> tuple[object, object]:
    nested = manifest.get("skill")
    if isinstance(nested, Mapping):
        return nested.get("id"), nested.get("version")
    return manifest.get("name"), manifest.get("version")


def _shared_paths(component: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    standard = component.get("shared_standard")
    if isinstance(standard, Mapping):
        registry = standard.get("registry")
        if isinstance(registry, str):
            values.append(registry)
        files = standard.get("files")
        if isinstance(files, list):
            values.extend(item for item in files if isinstance(item, str))
    contracts = component.get("shared_contracts")
    if isinstance(contracts, Mapping):
        values.extend(
            item
            for key, item in contracts.items()
            if key != "access" and isinstance(item, str)
        )
    return values


def _validate_component(
    suite_root: Path,
    shared_root: Path,
    suite_version: object,
    component_name: str,
    declaration: Mapping[str, Any],
    errors: list[str],
) -> None:
    component_path_value = declaration.get("path")
    if not isinstance(component_path_value, str):
        errors.append(f"component:{component_name}:path_missing")
        return
    component_root = (suite_root / component_path_value).resolve()
    if not _inside(suite_root, component_root):
        errors.append(f"component:{component_name}:path_escapes_suite")
        return
    if not (component_root / "SKILL.md").is_file():
        errors.append(f"component:{component_name}:skill_missing")

    manifest_path = _resolve_file(
        suite_root,
        declaration.get("manifest"),
        errors,
        f"component:{component_name}:manifest",
    )
    if manifest_path is None or not manifest_path.is_file():
        return
    component = _load_yaml(manifest_path)
    actual_id, actual_version = _component_identity(component)
    if actual_id != declaration.get("id"):
        errors.append(f"component:{component_name}:id_mismatch")
    if actual_version != declaration.get("version"):
        errors.append(f"component:{component_name}:version_mismatch")

    compatibility = component.get("suite_compatibility")
    if not isinstance(compatibility, Mapping):
        compatibility = component.get("dependencies")
    if not isinstance(compatibility, Mapping):
        errors.append(f"component:{component_name}:suite_compatibility_missing")
    else:
        if compatibility.get("suite_version") != suite_version:
            errors.append(f"component:{component_name}:suite_version_incompatible")
        if compatibility.get("shared_bundle_version") != declaration.get(
            "shared_bundle_version", "1.0.0-rc1"
        ):
            errors.append(f"component:{component_name}:shared_bundle_incompatible")
        for key in (
            "paper_quality_standard_version",
            "project_facts_contract_version",
            "review_finding_contract_version",
            "paper_artifact_contract_version",
            "figure_manifest_contract_version",
        ):
            if key in compatibility and compatibility.get(key) != declaration.get(key):
                errors.append(f"component:{component_name}:{key}_incompatible")

    for relative_path in _shared_paths(component):
        resolved = (component_root / relative_path).resolve()
        if not _inside(shared_root, resolved):
            errors.append(
                f"component:{component_name}:non_authoritative_shared_path:{relative_path}"
            )
        elif not resolved.is_file():
            errors.append(f"component:{component_name}:shared_missing:{relative_path}")


def validate_suite(manifest_path: Path) -> dict[str, object]:
    """Return a read-only deployment validation report."""
    errors: list[str] = []
    manifest_path = manifest_path.resolve()
    suite_root = manifest_path.parent.parent.resolve()
    suite_manifest = _load_yaml(manifest_path)
    suite = suite_manifest.get("suite")
    components = suite_manifest.get("components")
    shared_declaration = suite_manifest.get("shared")
    if not isinstance(suite, Mapping):
        return {"status": "BLOCKED", "errors": ["suite_declaration_missing"]}
    if not isinstance(components, Mapping):
        return {"status": "BLOCKED", "errors": ["components_declaration_missing"]}
    if not isinstance(shared_declaration, Mapping):
        return {"status": "BLOCKED", "errors": ["shared_declaration_missing"]}

    suite_version = suite.get("version")
    shared_manifest_path = _resolve_file(
        suite_root,
        shared_declaration.get("manifest"),
        errors,
        "shared:manifest",
    )
    shared_root = (suite_root / "shared").resolve()
    if shared_manifest_path is not None and shared_manifest_path.is_file():
        shared_manifest = _load_yaml(shared_manifest_path)
        shared = shared_manifest.get("shared")
        standard = shared_manifest.get("paper_quality_standard")
        contracts = shared_manifest.get("contracts")
        if not isinstance(shared, Mapping) or shared.get(
            "bundle_version"
        ) != shared_declaration.get("bundle_version"):
            errors.append("shared:bundle_version_incompatible")
        if not isinstance(standard, Mapping) or standard.get(
            "version"
        ) != shared_declaration.get("paper_quality_standard_version"):
            errors.append("shared:paper_quality_standard_version_incompatible")
        elif isinstance(standard.get("registry"), str):
            _resolve_file(
                shared_root,
                standard["registry"],
                errors,
                "shared:paper_quality_standard_registry",
            )
        for name in (
            "project_facts",
            "review_finding",
            "paper_artifact",
            "figure_manifest",
        ):
            expected_key = f"{name}_contract_version"
            contract = contracts.get(name) if isinstance(contracts, Mapping) else None
            if not isinstance(contract, Mapping) or contract.get(
                "version"
            ) != shared_declaration.get(expected_key):
                errors.append(f"shared:{name}_version_incompatible")
            elif isinstance(contract.get("path"), str):
                _resolve_file(
                    shared_root,
                    contract["path"],
                    errors,
                    f"shared:{name}",
                )

    for component_name, declaration in components.items():
        if not isinstance(declaration, Mapping):
            errors.append(f"component:{component_name}:declaration_invalid")
            continue
        extended = dict(declaration)
        for key in (
            "bundle_version",
            "paper_quality_standard_version",
            "project_facts_contract_version",
            "review_finding_contract_version",
            "paper_artifact_contract_version",
            "figure_manifest_contract_version",
        ):
            extended[key] = shared_declaration.get(key)
        extended["shared_bundle_version"] = shared_declaration.get("bundle_version")
        _validate_component(
            suite_root,
            shared_root,
            suite_version,
            str(component_name),
            extended,
            errors,
        )

    deployment = suite_manifest.get("deployment_contract")
    if not isinstance(deployment, Mapping):
        errors.append("deployment_contract_missing")
    else:
        for key in ("missing_shared", "incompatible_shared"):
            if deployment.get(key) != "BLOCKED":
                errors.append(f"deployment:{key}_must_block")
        if deployment.get("copied_rule_fallback") is not False:
            errors.append("deployment:copied_rule_fallback_must_be_false")

    return {
        "status": "PASS" if not errors else "BLOCKED",
        "suite_version": suite_version,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        type=Path,
        nargs="?",
        default=Path(__file__).with_name("manifest.yaml"),
    )
    args = parser.parse_args()
    try:
        report = validate_suite(args.manifest)
    except (OSError, TypeError, UnicodeError, yaml.YAMLError) as error:
        report = {"status": "BLOCKED", "errors": [f"validator_error:{error}"]}
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
