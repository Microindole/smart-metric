from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from core.report_export import export_report  # noqa: E402


REPORT_PAYLOAD = {
    "title": "SmartMetric Test Report",
    "subtitle": "Report export verification",
    "summary": {"files": 1, "max_complexity": 2},
    "sections": [
        {"heading": "Summary", "text": "This is a generated report."},
        {"heading": "Rows", "rows": [{"filename": "demo.py", "complexity": 2}]},
    ],
}


class ReportExportUnitTests(unittest.TestCase):
    def test_exports_markdown(self):
        content = export_report(REPORT_PAYLOAD, "markdown").decode("utf-8")
        self.assertIn("# SmartMetric Test Report", content)
        self.assertIn("| filename | complexity |", content)

    def test_exports_html(self):
        content = export_report(REPORT_PAYLOAD, "html").decode("utf-8")
        self.assertIn("<html", content)
        self.assertIn("SmartMetric Test Report", content)

    def test_exports_pdf(self):
        content = export_report(REPORT_PAYLOAD, "pdf")
        self.assertTrue(content.startswith(b"%PDF"))


class ReportExportApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_report_export_markdown_api(self):
        response = self.client.post(
            "/api/export/report",
            json={"format": "markdown", "filename": "report.md", "report": REPORT_PAYLOAD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/markdown", response.content_type)

    def test_report_export_pdf_api(self):
        response = self.client.post(
            "/api/export/report",
            json={"format": "pdf", "filename": "report.pdf", "report": REPORT_PAYLOAD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.content_type)
        self.assertTrue(response.data.startswith(b"%PDF"))


class ReportExportCliTests(unittest.TestCase):
    def test_cli_report_generates_html_file(self):
        payload_path = ROOT / "tests" / "report_cli_input.json"
        output_path = ROOT / "tests" / "report_cli_output.html"
        payload_path.write_text(json.dumps(REPORT_PAYLOAD, ensure_ascii=False), encoding="utf-8")
        try:
            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "report",
                    str(payload_path),
                    "-F",
                    "html",
                    "-o",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertTrue(output_path.exists())
            self.assertIn(str(output_path), completed.stdout)
        finally:
            payload_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
