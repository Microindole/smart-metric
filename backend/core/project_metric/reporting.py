from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.cfg_metric import analyze_cfg_files
from core.estimate_metric import calculate_estimate
from core.function_point_metric.service import calculate_function_point_metrics

from .service import ProjectScanOptions, analyze_project_directory, detect_source_language


CFG_LANGUAGES = {"java", "c", "cpp", "python"}


def build_project_report_payload(
    root_path: str,
    modules: Iterable[str] | None = None,
    options: ProjectScanOptions | dict | None = None,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    function_point_payload: dict | None = None,
    estimate_payload: dict | None = None,
) -> tuple[dict, dict]:
    project_result = analyze_project_directory(root_path, modules, options)
    root = Path(project_result["root"])
    complexity_result = analyze_project_source_complexity(root, project_result["inventory"]["code_files"])
    function_point_result = calculate_function_point_metrics(function_point_payload) if function_point_payload else None
    estimate_result = calculate_estimate(estimate_payload) if estimate_payload else None

    summary = {
        "项目路径": str(root),
        "代码文件数": project_result["summary"].get("code_file_count", 0),
        "设计文件数": project_result["summary"].get("design_file_count", 0),
        "总代码行": project_result["summary"].get("code_lines", 0),
        "依赖边数": project_result["summary"].get("dependency_edge_count", 0),
        "类数量": project_result["summary"].get("class_count", 0),
        "上帝文件数": project_result["summary"].get("god_files", 0),
        "上帝类数": project_result["summary"].get("god_classes", 0),
        "源码复杂度文件数": complexity_result["summary"].get("file_count", 0),
        "最大圈复杂度": complexity_result["summary"].get("max_complexity", 0),
    }
    if function_point_result:
        summary["功能点 FP"] = function_point_result["fp"]
    if estimate_result:
        summary["估算工时"] = estimate_result["effort_hours"]
        summary["估算成本"] = estimate_result["cost"]

    payload = {
        "title": title or f"{root.name} 项目度量总报告",
        "subtitle": subtitle or "SmartMetric 项目级自动化度量导出",
        "summary": summary,
        "sections": build_report_sections(project_result, complexity_result, function_point_result, estimate_result),
    }
    return payload, {
        "project": project_result,
        "complexity": complexity_result,
        "function_point": function_point_result,
        "estimate": estimate_result,
    }


def analyze_project_source_complexity(root: Path, code_files: list[str]) -> dict:
    payload = []
    for path in code_files:
        filename = str(Path(path).relative_to(root)).replace("\\", "/")
        language = detect_source_language(path)
        if language not in CFG_LANGUAGES:
            continue
        payload.append({"filename": filename, "content": Path(path).read_bytes()})
    return analyze_cfg_files(payload)


def build_report_sections(
    project_result: dict,
    complexity_result: dict,
    function_point_result: dict | None,
    estimate_result: dict | None,
) -> list[dict]:
    sections = [
        build_overview_section(project_result),
        build_loc_section(project_result),
        build_complexity_section(complexity_result),
        build_dependency_section(project_result),
        build_oo_section(project_result),
        build_design_section(project_result),
        build_function_point_section(function_point_result),
        build_estimate_section(estimate_result),
    ]
    return [section for section in sections if section]


def build_overview_section(project_result: dict) -> dict:
    options = project_result.get("scan_options", {})
    modules = []
    if "loc" in project_result:
        modules.append("LoC")
    if "dependencies" in project_result:
        modules.append("依赖分析")
    if "oo" in project_result:
        modules.append("面向对象")
    if "design" in project_result:
        modules.append("设计图")
    return {
        "heading": "项目概览",
        "text": (
            f"扫描路径：{project_result['root']}\n"
            f"启用模块：{', '.join(modules) if modules else '无'}\n"
            f"默认忽略：{'是' if options.get('use_default_ignores') else '否'}\n"
            f"忽略文件：{options.get('ignore_file_name', '.smartmetricignore')} "
            f"({'已命中' if options.get('ignore_file_found') else '未命中'})"
        ),
    }


def build_loc_section(project_result: dict) -> dict:
    loc_result = project_result.get("loc")
    if not loc_result:
        return {}
    files = sorted(loc_result.get("files", []), key=lambda item: item.get("code_lines", 0), reverse=True)[:20]
    rows = [
        {
            "filename": item["filename"],
            "language": item.get("language", ""),
            "code_lines": item.get("code_lines", 0),
            "blank_lines": item.get("blank_lines", 0),
            "comment_lines": item.get("comment_lines", 0),
        }
        for item in files
    ]
    return {
        "heading": "代码规模 LoC",
        "text": (
            f"总代码行：{loc_result['summary'].get('code_lines', 0)}，"
            f"文件数：{loc_result['summary'].get('file_count', 0)}，"
            f"语言分布：{loc_result['summary'].get('language_breakdown', {})}"
        ),
        "rows": rows,
    }


def build_complexity_section(complexity_result: dict) -> dict:
    files = sorted(
        complexity_result.get("files", []),
        key=lambda item: item.get("cyclomatic_complexity", 0),
        reverse=True,
    )[:20]
    rows = [
        {
            "filename": item["filename"],
            "language": item.get("language", ""),
            "analysis_method": item.get("analysis_method", ""),
            "decision_points": item.get("decision_points", 0),
            "cyclomatic_complexity": item.get("cyclomatic_complexity", 0),
        }
        for item in files
    ]
    return {
        "heading": "复杂度与控制流",
        "text": (
            f"源码复杂度文件数：{complexity_result['summary'].get('file_count', 0)}，"
            f"最大圈复杂度：{complexity_result['summary'].get('max_complexity', 0)}，"
            f"平均圈复杂度：{complexity_result['summary'].get('average_complexity', 0)}"
        ),
        "rows": rows,
    }


def build_dependency_section(project_result: dict) -> dict:
    dependency_result = project_result.get("dependencies")
    if not dependency_result:
        return {}
    rows = dependency_result.get("edges", [])[:30]
    return {
        "heading": "依赖关系",
        "text": f"内部依赖边数：{dependency_result['summary'].get('edge_count', 0)}",
        "rows": rows or [{"from": "-", "to": "-"}],
    }


def build_oo_section(project_result: dict) -> dict:
    oo_result = project_result.get("oo")
    if not oo_result:
        return {}
    rows = []
    for item in oo_result.get("god_files", [])[:10]:
        rows.append(
            {
                "type": "god_file",
                "filename": item["filename"],
                "name": "-",
                "reason": ", ".join(item.get("reasons", [])),
            }
        )
    for item in oo_result.get("god_classes", [])[:10]:
        rows.append(
            {
                "type": "god_class",
                "filename": item["filename"],
                "name": item.get("class_name", ""),
                "reason": ", ".join(item.get("reasons", [])),
            }
        )
    if not rows:
        rows = [{"type": "-", "filename": "-", "name": "-", "reason": "未发现明显上帝文件或上帝类"}]
    return {
        "heading": "面向对象与上帝文件排查",
        "text": (
            f"类总数：{oo_result['summary'].get('class_count', 0)}，"
            f"上帝文件：{oo_result['summary'].get('god_file_count', 0)}，"
            f"上帝类：{oo_result['summary'].get('god_class_count', 0)}"
        ),
        "rows": rows,
    }


def build_design_section(project_result: dict) -> dict:
    design_result = project_result.get("design")
    if not design_result:
        return {}
    rows = []
    for item in design_result.get("usecase_diagrams", [])[:10]:
        rows.append({"type": "usecase", "filename": item["filename"], "metric": "ucp", "value": item.get("ucp", 0)})
    for item in design_result.get("class_diagrams", [])[:10]:
        rows.append(
            {
                "type": "class_diagram",
                "filename": item["filename"],
                "metric": "class_count",
                "value": item.get("summary", {}).get("class_count", 0),
            }
        )
    for item in design_result.get("cfg_graphs", [])[:10]:
        rows.append(
            {
                "type": "cfg_graph",
                "filename": item["filename"],
                "metric": "cyclomatic_complexity",
                "value": item.get("cyclomatic_complexity", 0),
            }
        )
    if not rows:
        rows = [{"type": "-", "filename": "-", "metric": "-", "value": "未发现设计图"}]
    return {
        "heading": "设计图度量",
        "text": (
            f"用例图：{design_result['summary'].get('usecase_diagram_count', 0)}，"
            f"类图：{design_result['summary'].get('class_diagram_count', 0)}，"
            f"控制流图：{design_result['summary'].get('cfg_graph_count', 0)}"
        ),
        "rows": rows,
    }


def build_function_point_section(function_point_result: dict | None) -> dict:
    if not function_point_result:
        return {
            "heading": "功能点度量",
            "text": "未提供功能点输入 JSON；该指标不能从源码自动推导，请通过 -P/--fp-file 提供。",
        }
    rows = []
    for item in function_point_result.get("details", []):
        rows.append({"type": item["type"], "name": item["name"], "subtotal": item["subtotal"]})
    return {
        "heading": "功能点度量",
        "text": (
            f"UFP：{function_point_result.get('ufp', 0)}，"
            f"VAF：{function_point_result.get('vaf', 0)}，"
            f"FP：{function_point_result.get('fp', 0)}"
        ),
        "rows": rows,
    }


def build_estimate_section(estimate_result: dict | None) -> dict:
    if not estimate_result:
        return {
            "heading": "项目估算",
            "text": "未提供估算输入 JSON；该指标依赖人工输入，请通过 -E/--estimate-file 提供。",
        }
    rows = [{key: value for key, value in estimate_result.items()}]
    return {
        "heading": "项目估算",
        "text": "基于输入度量值的工作量、成本、工期与人员估算结果。",
        "rows": rows,
    }
