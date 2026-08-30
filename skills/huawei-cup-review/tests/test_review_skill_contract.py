from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared" / "paper-quality-standard"
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_review_result.py"
FIGURE_AUDITOR = SKILL_ROOT / "scripts" / "audit_figure_references.py"
RULE_HEADER = re.compile(r"^## ([A-Z]+-[0-9]{3}) —", re.MULTILINE)
RULE_ID = re.compile(r"\b[A-Z]+-[0-9]{3}\b")


def _load_validator_module() -> Any:
    spec = importlib.util.spec_from_file_location("review_result_validator", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result() -> dict[str, Any]:
    return {
        "contract_version": "2",
        "task_id": "phase4-test",
        "call_status": "SUCCESS",
        "status_meaning": "CALL_SUCCESS_ONLY_NOT_PAPER_QUALITY",
        "read_only": True,
        "writes_performed": [],
        "findings": [],
        "limitations": [],
    }


def _finding() -> dict[str, Any]:
    return {
        "finding_id": "finding-1",
        "rule_id": "CLAIM-001",
        "severity": "P1",
        "category": "claim_evidence_gap",
        "claim": "The conclusion exceeds the observed sample scope.",
        "location": "section 6, paragraph 2",
        "evidence": [
            {
                "artifact_id": "paper",
                "locator": "section 6, paragraph 2",
                "reason": "The conclusion is universal while the reported sample is local.",
            }
        ],
        "recommendation": "Verify and narrow the claim scope outside Review.",
        "confidence": "high",
        "limitations": [],
    }


def test_frontmatter_identity_and_natural_triggers() -> None:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---", maxsplit=2)[1])
    assert metadata["name"] == "huawei-cup-review"
    assert metadata["description"].startswith("This skill should be used when")
    assert "审核数学建模论文" in metadata["description"]
    assert "检查论文 AI 味" in metadata["description"]


def test_manifest_paths_are_real_and_boundary_is_exact() -> None:
    manifest = yaml.safe_load((SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    contract = manifest["contract"]
    assert contract["read_only"] is True
    assert contract["writes_performed"] == []
    assert contract["persists_report"] is False
    assert contract["automatic_repair"] is False
    assert contract["owns_submission_state"] is False
    paths = [manifest["skill"]["entrypoint"], manifest["shared_standard"]["registry"]]
    paths.extend(manifest["shared_standard"]["files"])
    paths.extend(
        value
        for key, value in manifest["shared_contracts"].items()
        if key != "access"
    )
    paths.extend(manifest["schemas"].values())
    paths.extend(item["path"] for item in manifest["references"]["on_demand"])
    paths.extend(manifest["checks"].values())
    assert all((SKILL_ROOT / path).resolve().exists() for path in paths)


def test_project_facts_access_is_read_only() -> None:
    manifest = yaml.safe_load((SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["shared_contracts"]["access"] == "read_only"
    reference = (SKILL_ROOT / "references" / "project-facts-review.md").read_text(
        encoding="utf-8"
    )
    assert "只读" in reference
    assert "不更新 Project Facts" in reference


def test_request_schema_forces_read_only_policy() -> None:
    schema = json.loads((SKILL_ROOT / "schemas" / "review-request.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    request = {
        "contract_version": "2",
        "task_id": "request-test",
        "artifacts": [{"artifact_id": "paper", "kind": "paper", "path": "main.tex"}],
        "review_lenses": ["claim_evidence"],
        "policy": {
            "read_only_required": True,
            "allow_artifact_writes": False,
            "allow_automatic_repair": False,
        },
    }
    assert not list(validator.iter_errors(request))
    request["policy"]["allow_artifact_writes"] = True
    assert list(validator.iter_errors(request))


def test_empty_findings_and_evidence_backed_finding_are_valid() -> None:
    module = _load_validator_module()
    assert module.validate_review_result(_result()) == []
    result = _result()
    result["findings"] = [_finding()]
    assert module.validate_review_result(result) == []


def test_formal_finding_without_evidence_is_rejected() -> None:
    module = _load_validator_module()
    result = _result()
    finding = _finding()
    finding["evidence"] = []
    result["findings"] = [finding]
    assert module.validate_review_result(result)


def test_unknown_rule_id_is_rejected() -> None:
    module = _load_validator_module()
    result = _result()
    finding = _finding()
    finding["rule_id"] = "CLAIM-999"
    result["findings"] = [finding]
    assert any("unknown Shared Rule ID" in item for item in module.validate_review_result(result))


def test_duplicate_finding_ids_are_rejected() -> None:
    module = _load_validator_module()
    result = _result()
    result["findings"] = [_finding(), _finding()]
    assert any("duplicate finding_id" in item for item in module.validate_review_result(result))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("submission_status", "READY_TO_SUBMIT"),
        ("paper_score", 90),
        ("automatic_repair", True),
    ],
)
def test_second_quality_state_and_repair_fields_are_rejected(field: str, value: object) -> None:
    module = _load_validator_module()
    result = _result()
    result[field] = value
    assert module.validate_review_result(result)


def test_invalid_result_is_sanitized_to_read_only_contract_error() -> None:
    module = _load_validator_module()
    result = _result()
    result["read_only"] = False
    result["writes_performed"] = ["main.tex"]
    sanitized = module.enforce_review_result(result)
    assert sanitized["call_status"] == "CONTRACT_ERROR"
    assert sanitized["read_only"] is True
    assert sanitized["writes_performed"] == []
    assert sanitized["findings"] == []
    assert module.validate_review_result(sanitized) == []


def test_references_use_shared_rule_ids_without_copying_normative_statements() -> None:
    shared_texts = [
        path.read_text(encoding="utf-8")
        for path in SHARED_ROOT.glob("*.md")
        if path.name != "README.md"
    ]
    known_ids = {rule_id for text in shared_texts for rule_id in RULE_HEADER.findall(text)}
    statements = {
        line.removeprefix("- **Normative Statement:**").strip()
        for text in shared_texts
        for line in text.splitlines()
        if line.startswith("- **Normative Statement:")
    }
    references = "\n".join(
        path.read_text(encoding="utf-8") for path in (SKILL_ROOT / "references").glob("*.md")
    )
    assert RULE_ID.findall(references)
    assert set(RULE_ID.findall(references)) <= known_ids
    assert all(statement not in references for statement in statements)
    assert "Normative Statement" not in references


def test_runtime_has_no_legacy_external_or_mutation_dependency() -> None:
    forbidden_paths = ("legacy/", "external-layer", "quality_evidence_writer")
    forbidden_actions = ("write_text(", "write_bytes(", "unlink(", "rename(", "shutil.move", "--apply", "apply-trash")
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".yaml", ".json", ".py"}:
            continue
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(token not in text for token in forbidden_paths), path
        if path.parent.name == "scripts":
            assert all(token not in text for token in forbidden_actions), path


def test_figure_auditor_is_read_only_and_detects_missing_reference(tmp_path: Path) -> None:
    (tmp_path / "plot.pdf").write_bytes(b"%PDF-placeholder")
    tex = tmp_path / "main.tex"
    tex.write_text(
        "\\begin{figure}\\includegraphics{plot.pdf}\\caption{Result}\\label{fig:result}\\end{figure}",
        encoding="utf-8",
    )
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    result = subprocess.run(
        [sys.executable, str(FIGURE_AUDITOR), str(tex), "--strict"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    after = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert result.returncode == 1
    assert "not referenced" in result.stdout
    assert before == after


def test_figure_auditor_treats_subfigures_as_children_of_outer_figure(tmp_path: Path) -> None:
    (tmp_path / "left.pdf").write_bytes(b"%PDF-placeholder")
    (tmp_path / "right.pdf").write_bytes(b"%PDF-placeholder")
    tex = tmp_path / "main.tex"
    tex.write_text(
        """\\begin{figure}
\\begin{subfigure}{0.48\\textwidth}
\\includegraphics{left.pdf}\\caption{Left}\\label{fig:left}
\\end{subfigure}
\\begin{subfigure}{0.48\\textwidth}
\\includegraphics{right.pdf}\\caption{Right}\\label{fig:right}
\\end{subfigure}
\\caption{Comparison}\\label{fig:comparison}
\\end{figure}
See Figure~\\ref{fig:comparison}.
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(FIGURE_AUDITOR), str(tex), "--strict"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "FIGURES_SCANNED: 1" in result.stdout
    assert "FIGURE_REFERENCE_AUDIT: 0 warning(s)" in result.stdout


def test_review_case_catalog_covers_phase4_fault_and_resistance_classes() -> None:
    catalog = yaml.safe_load((SKILL_ROOT / "tests" / "review-cases.yaml").read_text(encoding="utf-8"))
    assert catalog["status"] == "SPECIFICATION_ONLY_PENDING_PHASE6_EXECUTION"
    cases = catalog["cases"]
    assert len({case["id"] for case in cases}) == len(cases)
    classes = {case["class"] for case in cases}
    assert {"defensive", "ai_style", "depth", "claim_evidence", "document", "resistance"} <= classes
    assert sum(case["class"] == "resistance" for case in cases) >= 4
    known_ids = {
        rule_id
        for path in SHARED_ROOT.glob("*.md")
        for rule_id in RULE_HEADER.findall(path.read_text(encoding="utf-8"))
    }
    referenced_ids = {rule_id for case in cases for rule_id in case["rules"]}
    assert referenced_ids <= known_ids
