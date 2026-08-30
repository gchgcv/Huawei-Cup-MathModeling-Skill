#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_ledger.py"


def run_ledger(data: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            ["python3", str(SCRIPT), str(path), "--strict"],
            text=True,
            capture_output=True,
            check=False,
        )


def base(entry="fresh", checkpoint="fresh", current_stage="problem-reading") -> dict:
    return {
        "project": {
            "title": "test",
            "source_files": ["problem.pdf"],
            "entry": entry,
            "checkpoint": checkpoint,
            "mode": "analysis",
        },
        "document": {
            "master_source": "",
            "source_format": "",
            "document_target": "content-only",
            "template_source": "none",
            "template_path": "",
            "competition_year": None,
            "official_template_current": False,
            "submission_template_verified": False,
            "compile_engine": "",
            "entrypoint": "",
            "final_output": "",
        },
        "workflow": {
            "current_stage": current_stage,
            "stages": [],
        },
        "questions": [{
            "id": "Q1",
            "task": "计算目标量",
            "inputs": ["x"],
            "outputs": ["y"],
            "hard_constraints": [],
            "evaluation": [],
            "model": "",
            "evidence": ["problem.pdf:p1"],
        }],
        "data": [],
        "parameters": [],
        "results": [],
        "claims": [],
    }


class LedgerHandoffTests(unittest.TestCase):
    def test_fresh_problem_reading_does_not_require_model(self) -> None:
        data = base()
        data["workflow"]["stages"] = [{
            "name": "problem-reading", "status": "NOT_STARTED", "evidence": [], "notes": ""
        }]
        result = run_ledger(data)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)

    def test_handoff_after_model_can_enter_computation(self) -> None:
        data = base("handoff", "after_model_construction", "computation-experiment")
        data["project"]["mode"] = "build"
        data["questions"][0]["model"] = "线性规划"
        data["workflow"]["stages"] = [
            {"name": "problem-reading", "status": "INHERITED_VERIFIED", "evidence": ["problem-ledger.md"], "notes": ""},
            {"name": "model-construction", "status": "INHERITED_VERIFIED", "evidence": ["model.md:§3"], "notes": ""},
            {"name": "computation-experiment", "status": "NOT_STARTED", "evidence": [], "notes": ""},
        ]
        result = run_ledger(data)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)

    def test_inherited_verified_requires_evidence(self) -> None:
        data = base("handoff", "after_problem_reading", "model-construction")
        data["workflow"]["stages"] = [{
            "name": "problem-reading", "status": "INHERITED_VERIFIED", "evidence": [], "notes": ""
        }]
        result = run_ledger(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires concrete evidence", result.stderr)

    def test_fresh_entry_cannot_claim_inherited_stage(self) -> None:
        data = base("fresh", "fresh", "model-construction")
        data["workflow"]["stages"] = [{
            "name": "problem-reading", "status": "INHERITED_UNVERIFIED", "evidence": ["notes.md"], "notes": ""
        }]
        result = run_ledger(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project.entry is fresh", result.stderr)

    def test_code_first_handoff_requires_model_mapping_before_computation(self) -> None:
        data = base("handoff", "mixed", "computation-experiment")
        data["project"]["mode"] = "build"
        data["workflow"]["stages"] = [{
            "name": "computation-experiment", "status": "INHERITED_UNVERIFIED", "evidence": ["main.py"], "notes": ""
        }]
        result = run_ledger(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("model is required", result.stderr)


if __name__ == "__main__":
    unittest.main()


def test_micro_revision_is_allowed_mode() -> None:
    data = base()
    data["project"]["mode"] = "micro-revision"
    data["document"]["document_target"] = "preserve-existing"
    data["document"]["master_source"] = "main.tex"
    result = run_ledger(data)
    assert "invalid project.mode" not in result.stderr


def test_latex_working_draft_requires_creation_authorization() -> None:
    data = base()
    data["project"]["mode"] = "paper"
    data["document"].update({
        "document_target": "latex-working-draft",
        "template_source": "skill_fallback",
        "source_format": "latex",
        "template_path": "templates/latex/working-draft/main.tex",
        "source_creation_authorized": False,
    })
    result = run_ledger(data)
    assert result.returncode != 0
    assert "source_creation_authorized=true" in result.stderr
