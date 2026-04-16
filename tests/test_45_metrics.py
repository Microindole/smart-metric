from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from core.cfg_metric import analyze_cfg_files  # noqa: E402
from core.cfg_metric.graph_import import analyze_imported_graph  # noqa: E402
from core.function_point_metric.service import calculate_function_point_metrics  # noqa: E402


class FunctionPoint45Tests(unittest.TestCase):
    def test_function_point_calculation(self):
        result = calculate_function_point_metrics(
            {
                "counts": {
                    "EI": {"simple": 1, "average": 1, "complex": 1},
                    "EO": {"simple": 1},
                },
                "gsc_factors": [{"level": 1} for _ in range(14)],
            }
        )

        self.assertEqual(result["ufp"], 17)
        self.assertEqual(result["gsc_total"], 14)
        self.assertEqual(result["vaf"], 0.79)
        self.assertEqual(result["fp"], 13.43)


class Cfg45Tests(unittest.TestCase):
    def test_cfg_supports_java_c_cpp_python(self):
        files = [
            {"filename": "Demo.java", "content": b"class Demo { int f(int x) { if (x > 0) return x; return 0; } }"},
            {"filename": "demo.c", "content": b"int f(int x) { if (x > 0 || x < -1) return x; return 0; }"},
            {"filename": "demo.cpp", "content": b"int f(int x) { while (x > 0) { x--; } return x; }"},
            {"filename": "demo.py", "content": b"def f(x):\n    return x if x > 0 else 0\n"},
        ]

        result = analyze_cfg_files(files)

        languages = {item["language"] for item in result["files"]}
        self.assertEqual(languages, {"java", "c", "cpp", "python"})
        self.assertEqual(result["summary"]["file_count"], 4)
        self.assertGreaterEqual(result["summary"]["max_complexity"], 2)

    def test_cfg_uses_ast_for_java_and_python(self):
        files = [
            {
                "filename": "Demo.java",
                "content": b"class Demo { int f(int x) { if (x > 0 && x < 10) return x; return x > 10 ? x : 0; } }",
            },
            {
                "filename": "demo.py",
                "content": b"def f(x):\n    if x > 0 and x < 10:\n        return x\n    return x if x > 10 else 0\n",
            },
        ]

        result = analyze_cfg_files(files)
        by_language = {item["language"]: item for item in result["files"]}

        self.assertEqual(by_language["java"]["analysis_method"], "ast-java-javalang")
        self.assertEqual(by_language["python"]["analysis_method"], "ast-python")
        self.assertEqual(by_language["java"]["summary"]["if"], 1)
        self.assertEqual(by_language["python"]["summary"]["if"], 1)
        self.assertGreaterEqual(by_language["java"]["cyclomatic_complexity"], 4)
        self.assertGreaterEqual(by_language["python"]["cyclomatic_complexity"], 4)

    def test_imports_json_graph(self):
        content = b'{"nodes":["start","if1","end"],"edges":[["start","if1"],["if1","end"]]}'
        result = analyze_imported_graph(content, "demo.json")

        self.assertEqual(result["format"], "json")
        self.assertEqual(result["node_count"], 3)
        self.assertEqual(result["edge_count"], 2)
        self.assertEqual(result["cyclomatic_complexity"], 1)

    def test_imports_mermaid_graph(self):
        content = b"flowchart TD\n  start --> if1\n  if1 --> end\n"
        result = analyze_imported_graph(content, "demo.mmd")

        self.assertEqual(result["format"], "mermaid")
        self.assertEqual(result["node_count"], 3)
        self.assertEqual(result["edge_count"], 2)
        self.assertEqual(result["cyclomatic_complexity"], 1)

    def test_imports_dot_graph(self):
        content = b"digraph G {\n  start -> if1;\n  if1 -> end;\n}\n"
        result = analyze_imported_graph(content, "demo.dot")

        self.assertEqual(result["format"], "dot")
        self.assertEqual(result["node_count"], 3)
        self.assertEqual(result["edge_count"], 2)
        self.assertEqual(result["cyclomatic_complexity"], 1)

    def test_imports_oom_graph(self):
        content = b"""
<Root>
  <c:Activities><o:Activity Id="A1" Name="DoWork" /></c:Activities>
  <c:Decisions><o:Decision Id="D1" Name="Judge" /></c:Decisions>
  <c:Start><o:Start Id="S1" Name="Start" /></c:Start>
  <c:End><o:End Id="E1" Name="End" /></c:End>
  <c:Flow>
    <o:ActivityFlow Id="F1"><c:Object1><o:Start Ref="S1" /></c:Object1><c:Object2><o:Decision Ref="D1" /></c:Object2></o:ActivityFlow>
    <o:ActivityFlow Id="F2"><c:Object1><o:Decision Ref="D1" /></c:Object1><c:Object2><o:Activity Ref="A1" /></c:Object2></o:ActivityFlow>
    <o:ActivityFlow Id="F3"><c:Object1><o:Activity Ref="A1" /></c:Object1><c:Object2><o:End Ref="E1" /></c:Object2></o:ActivityFlow>
  </c:Flow>
</Root>
"""
        result = analyze_imported_graph(content, "demo.oom")

        self.assertEqual(result["format"], "xml")
        self.assertEqual(result["node_count"], 4)
        self.assertEqual(result["edge_count"], 3)
        self.assertEqual(result["cyclomatic_complexity"], 1)


class Api45Tests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_function_point_api(self):
        response = self.client.post(
            "/api/metrics/function-point/calculate",
            json={
                "counts": {"EI": {"simple": 1}},
                "gsc_factors": [{"level": 0} for _ in range(14)],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["ufp"], 3)

    def test_cfg_api(self):
        response = self.client.post(
            "/api/metrics/cfg/calculate",
            data={
                "files": (io.BytesIO(b"def f(x):\n    if x > 0:\n        return x\n    return 0\n"), "demo.py"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["files"][0]["language"], "python")
        self.assertEqual(data["files"][0]["cyclomatic_complexity"], 2)

    def test_cfg_import_graph_api(self):
        response = self.client.post(
            "/api/metrics/cfg/import-graph",
            data={
                "file": (
                    io.BytesIO(b'{"nodes":["start","if1","end"],"edges":[["start","if1"],["if1","end"]]}'),
                    "demo.json",
                ),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["format"], "json")
        self.assertEqual(data["cyclomatic_complexity"], 1)

    def test_cfg_import_oom_api(self):
        response = self.client.post(
            "/api/metrics/cfg/import-graph",
            data={
                "file": (
                    io.BytesIO(
                        b"<Root><c:Activities><o:Activity Id='A1' Name='DoWork'/></c:Activities><c:Decisions><o:Decision Id='D1' Name='Judge'/></c:Decisions><c:Start><o:Start Id='S1' Name='Start'/></c:Start><c:End><o:End Id='E1' Name='End'/></c:End><c:Flow><o:ActivityFlow Id='F1'><c:Object1><o:Start Ref='S1'/></c:Object1><c:Object2><o:Decision Ref='D1'/></c:Object2></o:ActivityFlow><o:ActivityFlow Id='F2'><c:Object1><o:Decision Ref='D1'/></c:Object1><c:Object2><o:Activity Ref='A1'/></c:Object2></o:ActivityFlow><o:ActivityFlow Id='F3'><c:Object1><o:Activity Ref='A1'/></c:Object1><c:Object2><o:End Ref='E1'/></c:Object2></o:ActivityFlow></c:Flow></Root>"
                    ),
                    "demo.oom",
                ),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["format"], "xml")
        self.assertEqual(data["cyclomatic_complexity"], 1)


if __name__ == "__main__":
    unittest.main()
