from __future__ import annotations

import json
from pathlib import Path

from .runtime import ensure_runtime_paths


ensure_runtime_paths()

from core.cfg_metric import analyze_cfg_files, analyze_imported_graph  # noqa: E402
from core.class_diagram_metric import analyze_class_diagram_bytes  # noqa: E402
from core.estimate_metric import calculate_estimate  # noqa: E402
from core.function_point_metric.service import calculate_function_point_metrics  # noqa: E402
from core.oo_metric import analyze_oo_files  # noqa: E402


def read_binary_file(path: str) -> dict:
    target = Path(path)
    return {"filename": target.name, "content": target.read_bytes()}


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_path_metric(path: str, metric: str, language: str | None) -> dict:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"文件不存在: {target}")

    resolved_metric = detect_metric(metric, target)
    if resolved_metric == "cfg-source":
        return analyze_cfg_files([read_binary_file(str(target))], language)
    if resolved_metric == "cfg-graph":
        file = read_binary_file(str(target))
        return analyze_imported_graph(file["content"], file["filename"])
    if resolved_metric == "oo-source":
        return analyze_oo_files([read_binary_file(str(target))])
    if resolved_metric == "oo-diagram":
        file = read_binary_file(str(target))
        return analyze_class_diagram_bytes(file["filename"], file["content"])
    if resolved_metric == "fp":
        payload = json.loads(target.read_text(encoding="utf-8"))
        return calculate_function_point_metrics(payload)
    if resolved_metric == "estimate":
        payload = json.loads(target.read_text(encoding="utf-8"))
        return calculate_estimate(payload)
    raise ValueError(f"无法识别度量类型: {target.name}")


def detect_metric(metric: str, target: Path) -> str:
    if metric != "auto":
        return metric

    lower = target.name.lower()
    if lower.endswith(".java"):
        return "oo-source"
    if lower.endswith((".py", ".c", ".cpp", ".cc", ".cxx")):
        return "cfg-source"
    if lower.endswith((".xml", ".oom")):
        return "oo-diagram"
    if lower.endswith((".mmd", ".mermaid", ".dot")):
        return "cfg-graph"
    if lower.endswith(".json"):
        payload = json.loads(target.read_text(encoding="utf-8"))
        if "counts" in payload and "gsc" in payload:
            return "fp"
        if "nodes" in payload and "edges" in payload:
            return "cfg-graph"
        if "metric_type" in payload and "metric_value" in payload:
            return "estimate"
    raise ValueError("自动识别失败，请显式传入 --metric")
