from __future__ import annotations

import json


def build_phase1_context(report_payload: dict, bundle: dict) -> str:
    project = bundle.get("project", {})
    complexity = bundle.get("complexity", {})

    lines = [
        f"项目标题: {report_payload.get('title', '')}",
        f"项目摘要: {report_payload.get('subtitle', '')}",
        "",
        "项目汇总:",
    ]
    for key, value in report_payload.get("summary", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "高风险事实:"])
    oo = project.get("oo", {})
    lines.append(f"- 上帝文件数: {oo.get('summary', {}).get('god_file_count', 0)}")
    lines.append(f"- 上帝类数: {oo.get('summary', {}).get('god_class_count', 0)}")
    lines.append(f"- 依赖边数: {project.get('summary', {}).get('dependency_edge_count', 0)}")
    lines.append(f"- 最大圈复杂度: {complexity.get('summary', {}).get('max_complexity', 0)}")
    lines.append(f"- 平均圈复杂度: {complexity.get('summary', {}).get('average_complexity', 0)}")

    loc = project.get("loc", {})
    if loc:
        lines.extend(["", "代码量 Top 10:"])
        for item in sorted(loc.get("files", []), key=lambda value: value.get("code_lines", 0), reverse=True)[:10]:
            lines.append(
                f"- {item['filename']} | language={item.get('language', '')} | "
                f"code_lines={item.get('code_lines', 0)} | methods={item.get('method_count', 0)}"
            )

    if complexity.get("files"):
        lines.extend(["", "复杂度 Top 10:"])
        for item in sorted(
            complexity.get("files", []),
            key=lambda value: value.get("cyclomatic_complexity", 0),
            reverse=True,
        )[:10]:
            lines.append(
                f"- {item['filename']} | complexity={item.get('cyclomatic_complexity', 0)} | "
                f"decision_points={item.get('decision_points', 0)} | method={item.get('analysis_method', '')}"
            )

    dependencies = project.get("dependencies", {}).get("edges", [])
    if dependencies:
        lines.extend(["", "依赖样例 Top 20:"])
        for item in dependencies[:20]:
            lines.append(f"- {item.get('from', '')} -> {item.get('to', '')}")

    design = project.get("design", {})
    if design:
        lines.extend(["", "设计图统计:"])
        lines.append(f"- 用例图: {design.get('summary', {}).get('usecase_diagram_count', 0)}")
        lines.append(f"- 类图: {design.get('summary', {}).get('class_diagram_count', 0)}")
        lines.append(f"- 控制流图: {design.get('summary', {}).get('cfg_graph_count', 0)}")

    return "\n".join(lines).strip() + "\n"


def build_phase2_context(phase1_result: dict, source_bundle: dict) -> str:
    lines = [
        "第一轮审查结果:",
        json.dumps(phase1_result, ensure_ascii=False, indent=2),
        "",
        "源码片段与本地度量:",
    ]
    for item in source_bundle.get("files", []):
        symbols = item.get("symbols", [])
        lines.extend(
            [
                f"文件: {item['filename']}",
                f"语言: {item.get('language', '')}",
                f"代码行: {item.get('code_lines', 0)}",
                f"圈复杂度: {item.get('cyclomatic_complexity', 0)}",
                f"符号: {', '.join(symbols) if symbols else '无'}",
                "源码:",
                item.get("source_excerpt", ""),
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"
