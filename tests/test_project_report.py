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

from core.project_metric import ProjectScanOptions, build_project_report_payload  # noqa: E402


class ProjectReportTests(unittest.TestCase):
    def test_build_project_report_payload_with_optional_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "pkg" / "main.py").write_text(
                "from helper import VALUE\n\nclass Service:\n    def run(self):\n        if VALUE:\n            return True\n",
                encoding="utf-8",
            )
            (root / "pkg" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "sample_usecase.oom").write_text("<model><usecase name='Login'/></model>", encoding="utf-8")

            fp_payload = {
                "counts": {"EI": {"simple": 1}, "EO": {"simple": 1}, "EQ": {}, "ILF": {}, "EIF": {}},
                "gsc_factors": [{"level": 1}] * 14,
            }
            estimate_payload = {"metric_type": "fp", "metric_value": 20, "productivity": 8, "team_size": 2}

            payload, bundle = build_project_report_payload(
                str(root),
                ["inventory", "loc", "dependency", "oo", "design"],
                ProjectScanOptions(),
                function_point_payload=fp_payload,
                estimate_payload=estimate_payload,
            )

            self.assertIn("总代码行", payload["summary"])
            self.assertIn("功能点 FP", payload["summary"])
            self.assertIn("估算工时", payload["summary"])
            headings = {section["heading"] for section in payload["sections"]}
            self.assertIn("代码规模 LoC", headings)
            self.assertIn("复杂度与控制流", headings)
            self.assertIn("功能点度量", headings)
            self.assertIn("项目估算", headings)
            self.assertIn("complexity", bundle)
            self.assertGreaterEqual(bundle["complexity"]["summary"]["file_count"], 1)

    def test_cli_project_report_generates_pdf(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "main.py").write_text("class Service:\n    def run(self):\n        return 1\n", encoding="utf-8")
            fp_path = root / "fp.json"
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
            estimate_path = root / "estimate.json"
            estimate_path.write_text(
                json.dumps({"metric_type": "fp", "metric_value": 20, "productivity": 8, "team_size": 2}, ensure_ascii=False),
                encoding="utf-8",
            )
            output_path = root / "report.pdf"

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "project-report",
                    str(root),
                    "-F",
                    "pdf",
                    "-o",
                    str(output_path),
                    "-P",
                    str(fp_path),
                    "-E",
                    str(estimate_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertTrue(output_path.exists())
            self.assertIn(str(output_path), completed.stdout)
            self.assertTrue(output_path.read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
