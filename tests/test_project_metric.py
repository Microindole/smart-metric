from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from core.project_metric import analyze_project_directory  # noqa: E402


class ProjectMetricTests(unittest.TestCase):
    def test_analyzes_project_directory_with_code_and_design_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pkg").mkdir()
            (root / "web").mkdir()
            (root / "ignored" / "node_modules").mkdir(parents=True)

            (root / "pkg" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "pkg" / "main.py").write_text("import helper\nfrom helper import VALUE\nprint(VALUE)\n", encoding="utf-8")
            (root / "web" / "app.js").write_text("const util = require('./util');\nconsole.log(util);\n", encoding="utf-8")
            (root / "web" / "util.js").write_text("module.exports = 1;\n", encoding="utf-8")
            (root / "ignored" / "node_modules" / "skip.js").write_text("console.log('skip');\n", encoding="utf-8")

            big_lines = ["class Huge:\n"]
            for index in range(305):
                big_lines.append(f"    line_{index} = {index}\n")
            (root / "god.py").write_text("".join(big_lines), encoding="utf-8")

            method_lines = ["class GodClass {\n"]
            for index in range(20):
                method_lines.append(f"  m{index}() {{ return {index}; }}\n")
            method_lines.append("}\n")
            (root / "GodClass.js").write_text("".join(method_lines), encoding="utf-8")

            shutil.copyfile(ROOT / "samples" / "cfg_demo.oom", root / "cfg_demo.oom")
            shutil.copyfile(ROOT / "samples" / "class_diagram_demo.xml", root / "class_diagram_demo.xml")
            shutil.copyfile(ROOT / "samples" / "sample_usecase.oom", root / "sample_usecase.oom")

            result = analyze_project_directory(str(root))

            self.assertEqual(result["summary"]["code_file_count"], 6)
            self.assertEqual(result["summary"]["design_file_count"], 3)
            self.assertGreaterEqual(result["summary"]["code_lines"], 300)
            self.assertIn("python", result["summary"]["language_breakdown"])
            self.assertGreaterEqual(result["summary"]["dependency_edge_count"], 1)
            self.assertEqual(result["summary"]["cfg_graph_count"], 1)
            self.assertEqual(result["summary"]["class_diagram_count"], 1)
            self.assertEqual(result["summary"]["usecase_diagram_count"], 1)

            god_files = {item["filename"] for item in result["oo"]["god_files"]}
            self.assertIn("god.py", god_files)

            god_classes = {(item["filename"], item["class_name"]) for item in result["oo"]["god_classes"]}
            self.assertIn(("GodClass.js", "GodClass"), god_classes)

            dependency_edges = {(item["from"], item["to"]) for item in result["dependencies"]["edges"]}
            self.assertIn(("pkg/main.py", "pkg/helper.py"), dependency_edges)

            usecase_metrics = result["design"]["usecase_diagrams"][0]
            self.assertIn("ucp", usecase_metrics)
            class_metrics = result["design"]["class_diagrams"][0]
            self.assertIn("summary", class_metrics)
            cfg_metrics = result["design"]["cfg_graphs"][0]
            self.assertIn("cyclomatic_complexity", cfg_metrics)

    def test_cli_project_scan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "project-scan",
                    str(root),
                    "--modules",
                    "inventory,loc",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["code_file_count"], 1)
            self.assertEqual(payload["summary"]["total_lines"], 1)


if __name__ == "__main__":
    unittest.main()
