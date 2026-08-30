#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_quality_report.py"
TEMPLATE = ROOT / "templates" / "quality-report.json"


class QualityValidatorTests(unittest.TestCase):
    def run_report(self, data: dict, ledger: dict | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            cmd = ["python3", str(SCRIPT), str(path), "--strict"]
            if ledger is not None:
                ledger_path = Path(tmp) / "ledger.json"
                ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
                cmd += ["--ledger", str(ledger_path)]
            return subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                check=False,
            )

    def base(self) -> dict:
        return json.loads(TEMPLATE.read_text(encoding="utf-8"))


    def submission_ledger(self, template_source: str = "official", verified: bool = True) -> dict:
        document = {
            "document_target": "official-template" if template_source == "official" else "user-template",
            "template_source": template_source,
            "official_template_current": bool(verified) if template_source == "official" else False,
            "submission_template_verified": bool(verified) if template_source == "user" else False,
        }
        return {
            "document": document,
            "workflow": {
                "stages": [
                    {"name": "submission-audit", "status": "COMPLETED"},
                ]
            },
        }

    def test_ready_requires_evidence(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for gate in data["gates"].values():
            gate["status"] = "PASS"
        result = self.run_report(data, self.submission_ledger())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no evidence", result.stderr)

    def test_p0_forces_blocked(self) -> None:
        data = self.base()
        data["submission_status"] = "NEEDS_VALIDATION"
        data["issues"] = [{
            "id": "I001", "code": "RESULT_UNTRACEABLE", "severity": "P0", "location": "结果",
            "problem": "关键结果无法追溯", "evidence": ["结果表2"],
            "action": "重新运行并登记输出", "resolved": False,
        }]
        result = self.run_report(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("recommended status BLOCKED", result.stderr)

    def test_vague_pass_evidence_is_rejected(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for gate in data["gates"].values():
            gate["status"] = "PASS"
            gate["evidence"] = ["已检查"]
        result = self.run_report(data, self.submission_ledger())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no evidence", result.stderr)

    def test_unresolved_issue_enforces_score_cap(self) -> None:
        data = self.base()
        data["submission_status"] = "BLOCKED"
        data["issues"] = [{
            "id": "I002", "code": "RESULT_UNTRACEABLE", "severity": "P0",
            "location": "摘要", "problem": "关键数字没有来源",
            "evidence": ["摘要第2句"], "action": "绑定结果台账", "resolved": False,
        }]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        result = self.run_report(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds unresolved-issue cap 59", result.stderr)


    def test_ready_with_ledger_rejects_unverified_handoff(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for name, gate in data["gates"].items():
            gate["status"] = "PASS"
            gate["evidence"] = [f"evidence:{name}"]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        ledger = self.submission_ledger()
        ledger["workflow"]["stages"].insert(0, {"name": "model-construction", "status": "INHERITED_UNVERIFIED"})
        result = self.run_report(data, ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unresolved inherited/review stages", result.stderr)

    def test_ready_with_ledger_requires_completed_submission_audit(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for name, gate in data["gates"].items():
            gate["status"] = "PASS"
            gate["evidence"] = [f"evidence:{name}"]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        ledger = self.submission_ledger()
        ledger["workflow"]["stages"] = [{"name": "submission-audit", "status": "INHERITED_VERIFIED"}]
        result = self.run_report(data, ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("submission-audit=COMPLETED", result.stderr)

    def test_valid_ready_report(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for name, gate in data["gates"].items():
            gate["status"] = "PASS"
            gate["evidence"] = [f"evidence:{name}"]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        result = self.run_report(data, self.submission_ledger())
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("RECOMMENDED_STATUS: READY_TO_SUBMIT", result.stdout)


    def test_ready_rejects_skill_fallback_template(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for name, gate in data["gates"].items():
            gate["status"] = "PASS"
            gate["evidence"] = [f"evidence:{name}"]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        ledger = self.submission_ledger()
        ledger["document"] = {
            "document_target": "latex-working-draft",
            "template_source": "skill_fallback",
            "official_template_current": False,
            "submission_template_verified": False,
        }
        result = self.run_report(data, ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verified official or user submission template", result.stderr)

    def test_ready_rejects_unverified_user_template(self) -> None:
        data = self.base()
        data["submission_status"] = "READY_TO_SUBMIT"
        for name, gate in data["gates"].items():
            gate["status"] = "PASS"
            gate["evidence"] = [f"evidence:{name}"]
        for name, item in data["scores"].items():
            item["score"] = item["max"]
            item["evidence"] = [f"evidence:{name}"]
        ledger = self.submission_ledger("user", verified=False)
        result = self.run_report(data, ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("submission_template_verified=true", result.stderr)

    def test_v080_issue_codes_are_accepted(self) -> None:
        for code, severity in [
            ("PDF_LAYOUT_UNVERIFIED", "P1"),
            ("MODEL_EXPLANATION_THIN", "P1"),
            ("RESULT_DISCUSSION_THIN", "P1"),
            ("PSEUDO_FIGURE", "P2"),
            ("FLOAT_PLACEMENT_POOR", "P2"),
            ("TEMPLATE_SOURCE_UNVERIFIED", "P1"),
        ]:
            with self.subTest(code=code):
                data = self.base()
                data["submission_status"] = "NEEDS_VALIDATION" if severity == "P1" else "DRAFT"
                data["issues"] = [{
                    "id": "I-V080", "code": code, "severity": severity,
                    "location": "audit", "problem": "regression",
                    "evidence": ["audit:1"], "action": "review", "resolved": False,
                }]
                result = self.run_report(data)
                self.assertNotIn("invalid code", result.stderr, msg=result.stderr + result.stdout)



    def test_v082_issue_codes_are_accepted(self) -> None:
        for code, severity in [
            ("REFERENCE_MISSING", "P1"),
            ("REFERENCE_POLICY_VIOLATION", "P1"),
            ("REFERENCE_RELEVANCE_LOW", "P2"),
            ("FIGURE_VISUAL_UNVERIFIED", "P1"),
            ("FIGURE_VISUAL_DEFECT", "P1"),
            ("FIGURE_VISUAL_DEFECT", "P2"),
        ]:
            with self.subTest(code=code, severity=severity):
                data = self.base()
                data["submission_status"] = "NEEDS_VALIDATION" if severity == "P1" else "DRAFT"
                data["issues"] = [{
                    "id": f"I-{code}-{severity}",
                    "code": code,
                    "severity": severity,
                    "location": "audit",
                    "problem": "v0.8.2 regression",
                    "evidence": ["audit:1"],
                    "action": "review",
                    "resolved": False,
                }]
                result = self.run_report(data)
                self.assertNotIn("invalid code", result.stderr, msg=result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()


def test_ready_latex_requires_current_full_visual_review(tmp_path) -> None:
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    data["submission_status"] = "READY_TO_SUBMIT"
    for name, gate in data["gates"].items():
        gate["status"] = "PASS"
        gate["evidence"] = [f"evidence:{name}"]
    for name, item in data["scores"].items():
        item["score"] = item["max"]
        item["evidence"] = [f"evidence:{name}"]
    ledger = {
        "document": {
            "document_target": "official-template",
            "template_source": "official",
            "official_template_current": True,
            "submission_template_verified": False,
            "source_format": "latex",
        },
        "workflow": {"stages": [{"name": "submission-audit", "status": "COMPLETED"}]},
    }
    report_path = tmp_path / "report.json"
    ledger_path = tmp_path / "ledger.json"
    report_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        ["python3", str(SCRIPT), str(report_path), "--strict", "--ledger", str(ledger_path)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert "requires --latex-review" in result.stderr
