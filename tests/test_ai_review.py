from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from core.ai_review import build_ai_review_report_payload, run_ai_review  # noqa: E402
from core.ai_review.source_selector import extract_focus_files  # noqa: E402
from core.project_metric import ProjectScanOptions  # noqa: E402


class FakeReviewer:
    def review_phase1(self, context_text: str) -> dict:
        return {
            "summary": {"risk_level": "medium", "project_overview": "项目存在复杂度和职责集中过高的问题。"},
            "focus_files": ["pkg/main.py"],
            "findings": [
                {
                    "id": "F1",
                    "severity": "high",
                    "category": "complexity",
                    "filename": "pkg/main.py",
                    "reason": "核心逻辑集中在单文件中。",
                    "need_source": True,
                }
            ],
        }

    def review_phase2(self, review_context: str) -> dict:
        return {
            "summary": {"overall_priority": "high", "refactor_order": ["pkg/main.py"]},
            "recommendations": [
                {
                    "finding_id": "F1",
                    "filename": "pkg/main.py",
                    "priority": "high",
                    "problem": "核心文件职责过多",
                    "evidence": ["LoC 偏高", "主逻辑集中在单文件"],
                    "target_symbols": ["Service", "run"],
                    "suggestion": "拆分文件内的扫描和报告生成逻辑",
                    "refactor_steps": ["先拆分核心流程", "再补测试"],
                    "expected_benefit": "降低复杂度并提升可测试性",
                    "refactor_scope": "medium",
                }
            ],
        }


class AIReviewTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_extract_focus_files_supports_structured_and_regex_fallback(self):
        result = extract_focus_files(
            {
                "focus_files": ["backend/core/project_metric/service.py"],
                "findings": [{"filename": "backend/core/report_export.py"}],
            },
            raw_text="建议查看 backend/app.py 和 backend/core/project_metric/service.py",
        )
        self.assertIn("backend/core/project_metric/service.py", result)
        self.assertIn("backend/core/report_export.py", result)
        self.assertIn("backend/app.py", result)

    def test_run_ai_review_with_fake_reviewer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "pkg" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "pkg" / "main.py").write_text(
                "from helper import VALUE\n\nclass Service:\n    def run(self):\n        if VALUE:\n            return True\n",
                encoding="utf-8",
            )
            result = run_ai_review(
                str(root),
                ["inventory", "loc", "dependency", "oo", "design"],
                ProjectScanOptions(),
                reviewer=FakeReviewer(),
            )

            self.assertEqual(result["phase1"]["summary"]["risk_level"], "medium")
            self.assertEqual(result["focus_files"], ["pkg/main.py"])
            self.assertEqual(result["source_bundle"]["files"][0]["filename"], "pkg/main.py")
            self.assertGreater(result["source_bundle"]["files"][0]["code_lines"], 0)

            report_payload = build_ai_review_report_payload(result)
            headings = {section["heading"] for section in report_payload["sections"]}
            self.assertIn("AI 第一轮审查", headings)
            self.assertIn("AI 改进建议", headings)
            recommendations = next(section for section in report_payload["sections"] if section["heading"] == "AI 改进建议")["rows"]
            self.assertIn("target_symbols", recommendations[0])
            self.assertIn("evidence", recommendations[0])

    def test_ai_review_api_returns_review_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "pkg" / "main.py").write_text("class Service:\n    def run(self):\n        return 1\n", encoding="utf-8")
            phase1_path = root / "phase1.json"
            phase2_path = root / "phase2.json"
            fp_path = root / "fp.json"
            estimate_path = root / "estimate.json"
            phase1_path.write_text(
                json.dumps(FakeReviewer().review_phase1(""), ensure_ascii=False),
                encoding="utf-8",
            )
            phase2_path.write_text(
                json.dumps(FakeReviewer().review_phase2(""), ensure_ascii=False),
                encoding="utf-8",
            )
            fp_path.write_text(
                json.dumps(
                    {
                        "counts": {"EI": {"simple": 1}, "EO": {}, "EQ": {}, "ILF": {}, "EIF": {}},
                        "gsc_factors": [{"level": 1}] * 14,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            estimate_path.write_text(
                json.dumps({"metric_type": "fp", "metric_value": 20, "productivity": 8, "team_size": 2}, ensure_ascii=False),
                encoding="utf-8",
            )

            response = self.client.post(
                "/api/metrics/ai-review/run",
                json={
                    "path": str(root),
                    "modules": ["inventory", "loc", "dependency", "oo", "design"],
                    "phase1_file": str(phase1_path),
                    "phase2_file": str(phase2_path),
                    "fp_file": str(fp_path),
                    "estimate_file": str(estimate_path),
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.get_json()["data"]
            self.assertIn("review", payload)
            self.assertIn("report", payload)
            self.assertEqual(payload["report"]["summary"]["AI 风险等级"], "medium")
            self.assertIn("功能点 FP", payload["report"]["summary"])

    def test_ai_review_api_supports_inline_phase_payloads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "pkg" / "main.py").write_text("class Service:\n    def run(self):\n        return 1\n", encoding="utf-8")

            response = self.client.post(
                "/api/metrics/ai-review/run",
                json={
                    "path": str(root),
                    "modules": ["inventory", "loc", "dependency", "oo", "design"],
                    "phase1_payload": FakeReviewer().review_phase1(""),
                    "phase2_payload": FakeReviewer().review_phase2(""),
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.get_json()["data"]
            self.assertEqual(payload["review"]["phase1"]["summary"]["risk_level"], "medium")

    def test_ai_review_config_api(self):
        response = self.client.get("/api/metrics/ai-review/config")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertIn("local_config_path", payload)
        self.assertIn("example_config_path", payload)

    def test_cli_ai_review_supports_fixture_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "pkg" / "main.py").write_text("class Service:\n    def run(self):\n        return 1\n", encoding="utf-8")
            phase1_path = root / "phase1.json"
            phase2_path = root / "phase2.json"
            output_path = root / "review.json"
            phase1_path.write_text(json.dumps(FakeReviewer().review_phase1(""), ensure_ascii=False), encoding="utf-8")
            phase2_path.write_text(json.dumps(FakeReviewer().review_phase2(""), ensure_ascii=False), encoding="utf-8")

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "ai-review",
                    str(root),
                    "-F",
                    "json",
                    "-o",
                    str(output_path),
                    "--phase1-file",
                    str(phase1_path),
                    "--phase2-file",
                    str(phase2_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertTrue(output_path.exists())
            self.assertIn(str(output_path), completed.stdout)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["phase1"]["summary"]["risk_level"], "medium")


if __name__ == "__main__":
    unittest.main()
