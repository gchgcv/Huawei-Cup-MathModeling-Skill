from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared" / "paper-quality-standard"
LEGACY_ROOT = REPO_ROOT / "legacy" / "huawei-cup-modeling-writing-v0.9.1"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_manuscript_mutation.py"
RULE_ID = re.compile(r"\b[A-Z]+-\d{3}\b")
RULE_HEADER = re.compile(r"^## ([A-Z]+-\d{3}) —", re.MULTILINE)


def _run_validator(
    tmp_path: Path, before: str, after: str
) -> subprocess.CompletedProcess[str]:
    before_path = tmp_path / "before.tex"
    after_path = tmp_path / "after.tex"
    before_path.write_text(before, encoding="utf-8")
    after_path.write_text(after, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(before_path), str(after_path)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_frontmatter_has_stable_identity_and_natural_triggers() -> None:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", maxsplit=2)[1]
    metadata = yaml.safe_load(frontmatter)
    assert metadata["name"] == "huawei-cup-writing"
    assert metadata["description"].startswith("This skill should be used when")
    assert "写数学建模论文" in metadata["description"]
    assert "重写摘要" in metadata["description"]


def test_manifest_paths_and_shared_registry_are_real() -> None:
    manifest = yaml.safe_load(
        (SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8")
    )
    paths = [manifest["shared_standard"]["registry"]]
    paths.extend(manifest["shared_standard"]["files"])
    paths.extend(
        value for key, value in manifest["shared_contracts"].items() if key != "access"
    )
    paths.extend(item["path"] for item in manifest["references"]["on_demand"])
    paths.extend(manifest["validation"].values())
    for value in paths:
        assert (SKILL_ROOT / value).resolve().exists(), value


def test_existing_text_revision_requires_fidelity_lock() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    reference = (
        SKILL_ROOT / "references" / "fidelity-and-derived-values.md"
    ).read_text(encoding="utf-8")
    prompt = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "fidelity-and-derived-values.md" in skill
    assert "完整 LaTeX token" in skill
    assert "默认禁止新增派生数字" in skill
    assert "\\ref{fig:result}" in reference
    assert "declared_derived_values" in reference
    assert "--before-text" in reference
    assert "validator 未 PASS 时不得返回" in skill
    assert "可复算不等于获准写入" in prompt


def test_writing_skill_has_no_legacy_runtime_dependency() -> None:
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".py", ".tex"}:
            continue
        if path.name == Path(__file__).name:
            continue
        assert "legacy/" not in path.read_text(encoding="utf-8")


def test_project_facts_access_is_read_only() -> None:
    manifest = yaml.safe_load(
        (SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["shared_contracts"]["access"] == "read_only"
    reference = (SKILL_ROOT / "references" / "project-facts-consumption.md").read_text(
        encoding="utf-8"
    )
    assert "只读" in reference
    assert "不得创建、补写或回写" in reference


def test_writing_skill_contains_no_review_state_or_finding_logic() -> None:
    forbidden = (
        "READY_TO_SUBMIT",
        "writes_performed",
        "reviewer severity",
        "finding schema",
        "submission_status",
    )
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".py"}:
            continue
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text
        assert not re.search(r"\bP[012]\b", text)


def test_writing_references_use_existing_rule_ids_without_copying_rules() -> None:
    shared_texts = [
        path.read_text(encoding="utf-8")
        for path in SHARED_ROOT.glob("*.md")
        if path.name != "README.md"
    ]
    known_ids = {
        rule_id for text in shared_texts for rule_id in RULE_HEADER.findall(text)
    }
    statements: set[str] = set()
    for text in shared_texts:
        for line in text.splitlines():
            prefix = "- **Normative Statement:**"
            if line.startswith(prefix):
                statements.add(line.removeprefix(prefix).strip())

    reference_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (SKILL_ROOT / "references").glob("*.md")
    )
    assert RULE_ID.findall(reference_text)
    assert set(RULE_ID.findall(reference_text)) <= known_ids
    assert all(statement not in reference_text for statement in statements)
    assert "Normative Statement" not in reference_text


def test_mutation_protector_accepts_prose_only_rewrite(tmp_path: Path) -> None:
    before = (
        "结果为 12.5%，见式 $y=ax+b$ 和图\\ref{fig:result}。"
        "\\label{sec:q1} 依据\\cite{key-a,key-b}。"
    )
    after = (
        "根据\\cite{key-a,key-b}，式 $y=ax+b$ 给出 12.5% 的结果；"
        "对应图见\\ref{fig:result}。\\label{sec:q1}"
    )
    result = _run_validator(tmp_path, before, after)
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"


@pytest.mark.parametrize(
    ("before", "after", "changed_field"),
    [
        ("结果为 12.5%。", "结果为 13.5%。", "numbers"),
        ("模型为 $y=ax+b$。", "模型为 $y=ax-b$。", "formulas"),
        ("依据\\cite{key-a}。", "依据\\cite{key-b}。", "citations"),
        (
            "\\label{sec:a} 见\\ref{sec:a}。",
            "\\label{sec:b} 见\\ref{sec:b}。",
            "labels",
        ),
    ],
)
def test_mutation_protector_rejects_protected_changes(
    tmp_path: Path,
    before: str,
    after: str,
    changed_field: str,
) -> None:
    result = _run_validator(tmp_path, before, after)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert changed_field in report["changes"]


def test_mutation_protector_reports_added_and_removed_numbers(tmp_path: Path) -> None:
    result = _run_validator(
        tmp_path,
        "误差由 4.8% 降至 3.1%。",
        "误差由 4.8% 降至 3.1%，下降 1.7 个百分点。",
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["number_delta"] == {"added": ["1.7"], "removed": []}


def test_mutation_protector_accepts_text_arguments_without_files() -> None:
    before = "结果为 8.4，见图\\ref{fig:result}。"
    after = "图\\ref{fig:result}给出结果 8.4。"
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--before-text",
            before,
            "--after-text",
            after,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"


def test_mutation_protector_is_read_only() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    forbidden_writes = ("write_text(", "unlink(", "rename(", "replace(", "shutil.move")
    assert all(token not in text for token in forbidden_writes)


def test_fallback_template_is_an_unchanged_legacy_copy() -> None:
    for relative in ("README.md", "main.tex"):
        current = SKILL_ROOT / "templates" / "latex" / "working-draft" / relative
        legacy = LEGACY_ROOT / "templates" / "latex" / "working-draft" / relative
        assert current.read_bytes() == legacy.read_bytes()


def test_writing_case_catalog_covers_required_behavior_classes() -> None:
    catalog = yaml.safe_load(
        (SKILL_ROOT / "tests" / "writing-cases.yaml").read_text(encoding="utf-8")
    )
    assert catalog["status"] == "SPECIFICATION_ONLY"
    cases = catalog["cases"]
    assert len({case["id"] for case in cases}) == len(cases)
    by_class = {
        class_name: [case for case in cases if case["class"] == class_name]
        for class_name in {case["class"] for case in cases}
    }
    assert len(by_class["normal"]) >= 5
    assert len(by_class["resistance"]) >= 4
    assert len(by_class["mutation"]) >= 5

    shared_ids = {
        rule_id
        for path in SHARED_ROOT.glob("*.md")
        for rule_id in RULE_HEADER.findall(path.read_text(encoding="utf-8"))
    }
    referenced_ids = {rule_id for case in cases for rule_id in case.get("rules", [])}
    assert referenced_ids <= shared_ids
