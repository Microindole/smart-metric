from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from core.project_metric import ProjectScanOptions, analyze_project_directory  # noqa: E402


class ProjectMetricTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

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

    def test_honors_custom_ignore_rules(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "coverage").mkdir()
            (root / "src" / "main.py").write_text("print('main')\n", encoding="utf-8")
            (root / "coverage" / "report.py").write_text("print('coverage')\n", encoding="utf-8")
            (root / "ignore_me.py").write_text("print('ignore')\n", encoding="utf-8")

            result = analyze_project_directory(
                str(root),
                ["inventory", "loc"],
                ProjectScanOptions(ignore_dirs=("coverage",), ignore_globs=("ignore_*.py",)),
            )

            files = {Path(item).name for item in result["inventory"]["code_files"]}
            self.assertEqual(files, {"main.py"})
            self.assertIn("coverage", result["scan_options"]["effective_ignore_dirs"])

    def test_reads_smartmetricignore_from_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "coverage").mkdir()
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('main')\n", encoding="utf-8")
            (root / "coverage" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / "skip.generated.py").write_text("print('skip')\n", encoding="utf-8")
            (root / ".smartmetricignore").write_text("coverage\n*.generated.py\n", encoding="utf-8")

            result = analyze_project_directory(str(root), ["inventory", "loc"])

            files = {Path(item).name for item in result["inventory"]["code_files"]}
            self.assertEqual(files, {"main.py"})
            self.assertTrue(result["scan_options"]["ignore_file_found"])
            self.assertIn("coverage", result["scan_options"]["ignore_file_dirs"])
            self.assertIn("*.generated.py", result["scan_options"]["effective_ignore_globs"])

    def test_smartmetricignore_supports_gitignore_like_negation_and_root_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "logs").mkdir()
            (root / "logs" / "keep.py").write_text("print('keep')\n", encoding="utf-8")
            (root / "logs" / "drop.py").write_text("print('drop')\n", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "logs").mkdir()
            (root / "nested" / "logs" / "nested.py").write_text("print('nested')\n", encoding="utf-8")
            (root / ".smartmetricignore").write_text("/logs/\n!/logs/keep.py\n", encoding="utf-8")

            result = analyze_project_directory(str(root), ["inventory", "loc"])

            files = {str(Path(item).relative_to(root)).replace("\\", "/") for item in result["inventory"]["code_files"]}
            self.assertIn("logs/keep.py", files)
            self.assertNotIn("logs/drop.py", files)
            self.assertIn("nested/logs/nested.py", files)
            self.assertTrue(result["scan_options"]["ignore_file_has_negation"])

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

    def test_cli_project_scan_supports_short_flags(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "coverage").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "coverage" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / "drop.generated.py").write_text("print('skip')\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "project-scan",
                    str(root),
                    "-m",
                    "inventory,loc",
                    "-d",
                    "coverage",
                    "-g",
                    "*.generated.py",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["code_file_count"], 1)

    def test_cli_project_scan_supports_command_alias(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "ps",
                    str(root),
                    "-m",
                    "inventory,loc",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["code_file_count"], 1)

    def test_cli_test_backend_supports_command_alias(self):
        completed = subprocess.run(
            [
                str(ROOT / ".venv" / "Scripts" / "python.exe"),
                str(ROOT / "backend" / "cli.py"),
                "tb",
                "--suite",
                "unit",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("OK", completed.stdout)

    def test_cli_root_help_lists_alias_on_next_line(self):
        completed = subprocess.run(
            [
                str(ROOT / ".venv" / "Scripts" / "python.exe"),
                str(ROOT / "backend" / "cli.py"),
                "--lang",
                "zh",
                "-h",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("  serve        启动 SmartMetric 后端服务", completed.stdout)
        self.assertIn("               srv, sv", completed.stdout)
        self.assertNotIn("serve / srv", completed.stdout)

    def test_cli_help_all_lists_command_catalog(self):
        completed = subprocess.run(
            [
                str(ROOT / ".venv" / "Scripts" / "python.exe"),
                str(ROOT / "backend" / "cli.py"),
                "help",
                "-a",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("全部命令", completed.stdout)
        self.assertIn("  test backend       运行后端自动化测试", completed.stdout)
        self.assertIn("别名: tb, t b, t backend", completed.stdout)

    def test_cli_help_topic_renders_specific_command_help(self):
        completed = subprocess.run(
            [
                str(ROOT / ".venv" / "Scripts" / "python.exe"),
                str(ROOT / "backend" / "cli.py"),
                "help",
                "serve",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("smartmetric serve - 启动 SmartMetric 后端服务", completed.stdout)
        self.assertIn("别名:", completed.stdout)

    def test_cli_project_scan_reads_ignore_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "coverage").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "coverage" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / ".smartmetricignore").write_text("coverage\n", encoding="utf-8")

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
            self.assertTrue(payload["scan_options"]["ignore_file_found"])
            self.assertEqual(payload["summary"]["code_file_count"], 1)

    def test_cli_project_scan_supports_ignore_args(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "dist").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "dist" / "bundle.py").write_text("print('skip')\n", encoding="utf-8")
            (root / "skip.generated.py").write_text("print('skip')\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "backend" / "cli.py"),
                    "project-scan",
                    str(root),
                    "--modules",
                    "inventory,loc",
                    "--ignore-dir",
                    "dist",
                    "--ignore-glob",
                    "*.generated.py",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["code_file_count"], 1)
            self.assertEqual(payload["scan_options"]["ignore_globs"], ["*.generated.py"])

    def test_project_scan_api_supports_ignore_rules(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "coverage").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "coverage" / "skip.py").write_text("print('skip')\n", encoding="utf-8")

            response = self.client.post(
                "/api/metrics/project/scan",
                json={
                    "path": str(root),
                    "modules": ["inventory", "loc"],
                    "ignore_dirs": ["coverage"],
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.get_json()["data"]
            self.assertEqual(payload["summary"]["code_file_count"], 1)
            self.assertIn("coverage", payload["scan_options"]["effective_ignore_dirs"])

    def test_project_scan_api_reads_ignore_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tmp").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tmp" / "skip.py").write_text("print('skip')\n", encoding="utf-8")
            (root / ".smartmetricignore").write_text("tmp\n", encoding="utf-8")

            response = self.client.post(
                "/api/metrics/project/scan",
                json={
                    "path": str(root),
                    "modules": ["inventory", "loc"],
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.get_json()["data"]
            self.assertTrue(payload["scan_options"]["ignore_file_found"])
            self.assertEqual(payload["summary"]["code_file_count"], 1)

    def test_pick_directory_api_returns_selected_path(self):
        with patch("routes.system_dialog.select_directory", return_value="D:\\works\\smart-metric"):
            response = self.client.post(
                "/api/system/pick-directory",
                json={"title": "选择项目目录"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]
        self.assertEqual(payload["path"], "D:\\works\\smart-metric")

    def test_pick_directory_api_handles_cancel(self):
        with patch("routes.system_dialog.select_directory", return_value=""):
            response = self.client.post(
                "/api/system/pick-directory",
                json={"title": "选择项目目录"},
            )

        self.assertEqual(response.status_code, 409)
        payload = response.get_json()
        self.assertFalse(payload["success"])


if __name__ == "__main__":
    unittest.main()
