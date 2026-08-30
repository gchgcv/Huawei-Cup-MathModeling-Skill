from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_MANIFEST = REPO_ROOT / "suite" / "manifest.yaml"
SUITE_VALIDATOR = REPO_ROOT / "suite" / "validate_suite.py"
DIST_BUILDER = REPO_ROOT / "suite" / "build_distribution.py"


def _load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("suite_validator_test", SUITE_VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("suite_builder_test", DIST_BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _copy_suite(tmp_path: Path) -> Path:
    for directory in ("suite", "shared", "skills", "compat"):
        shutil.copytree(REPO_ROOT / directory, tmp_path / directory)
    return tmp_path / "suite" / "manifest.yaml"


def test_current_suite_deployment_contract_passes() -> None:
    validator = _load_validator()
    report = validator.validate_suite(SUITE_MANIFEST)
    assert report == {
        "status": "PASS",
        "suite_version": "1.0.0-rc1",
        "errors": [],
    }


def test_missing_shared_file_fails_closed(tmp_path: Path) -> None:
    validator = _load_validator()
    manifest = _copy_suite(tmp_path)
    (tmp_path / "shared" / "paper-quality-standard" / "README.md").unlink()
    report = validator.validate_suite(manifest)
    assert report["status"] == "BLOCKED"
    assert any("shared_missing" in error for error in report["errors"])


def test_component_version_drift_is_blocked(tmp_path: Path) -> None:
    validator = _load_validator()
    manifest = _copy_suite(tmp_path)
    writing_manifest = tmp_path / "skills" / "huawei-cup-writing" / "manifest.yaml"
    value = yaml.safe_load(writing_manifest.read_text(encoding="utf-8"))
    value["version"] = "1.0.0-rc2"
    writing_manifest.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    report = validator.validate_suite(manifest)
    assert report["status"] == "BLOCKED"
    assert "component:writing:version_mismatch" in report["errors"]


def test_shared_version_drift_is_blocked(tmp_path: Path) -> None:
    validator = _load_validator()
    manifest = _copy_suite(tmp_path)
    shared_manifest = tmp_path / "shared" / "manifest.yaml"
    value = yaml.safe_load(shared_manifest.read_text(encoding="utf-8"))
    value["paper_quality_standard"]["version"] = "1.1"
    shared_manifest.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    report = validator.validate_suite(manifest)
    assert report["status"] == "BLOCKED"
    assert "shared:paper_quality_standard_version_incompatible" in report["errors"]


def test_components_are_suite_installed_but_independently_disableable() -> None:
    manifest = yaml.safe_load(SUITE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["suite"]["install_model"] == "suite_required"
    assert manifest["deployment_contract"]["component_single_directory_install"] == "forbidden"
    assert manifest["deployment_contract"]["component_enable_disable"] == "independent"
    assert all(item["can_disable"] is True for item in manifest["components"].values())


def test_cli_reports_machine_readable_pass() -> None:
    result = subprocess.run(
        [sys.executable, str(SUITE_VALIDATOR)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"


def test_distribution_selection_excludes_repository_only_content() -> None:
    builder = _load_builder()
    manifest = yaml.safe_load(SUITE_MANIFEST.read_text(encoding="utf-8"))
    paths = [
        "skills/huawei-cup-writing/SKILL.md",
        "skills/huawei-cup-writing/tests/test_contract.py",
        "skills/huawei-cup-writing/__pycache__/module.pyc",
        "shared/manifest.yaml",
        "compat/huawei-cup-modeling/SKILL.md",
        "suite/manifest.yaml",
        "suite/INSTALL.md",
        "suite/build_distribution.py",
        "benchmark/run_benchmark.py",
        "legacy/huawei-cup-modeling-writing-v0.9.1/SKILL.md",
        "reports/release.md",
        ".git/config",
    ]
    selected = builder.select_distribution_paths(paths, manifest["distribution"])
    assert selected == [
        "compat/huawei-cup-modeling/SKILL.md",
        "shared/manifest.yaml",
        "skills/huawei-cup-writing/SKILL.md",
        "suite/INSTALL.md",
        "suite/manifest.yaml",
    ]
