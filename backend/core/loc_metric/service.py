from __future__ import annotations

import re
from typing import Iterable, Optional

from core.oo_metric.strategies import create_source_analyzer

from .language_rules import detect_language
from .java_structure import analyze_java_structure
from .scanner import scan_lines


def _decode_bytes(content: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("文件编码无法识别")


def _analyze_non_java_structure(filename: str, text: str, language: str) -> dict:
    analyzer = create_source_analyzer(language)
    classes = analyzer.analyze(filename, text)

    class_metrics = []
    method_metrics = []
    for item in classes:
        class_metrics.append(
            {
                "class_name": item["class_name"],
                "method_count": item["lk"]["nom"],
                "field_count": item["lk"]["noa"],
                "rfc": item["ck"]["rfc"],
                "lcom": item["ck"]["lcom"],
            }
        )

        for method_name in item.get("methods", []):
            method_metrics.append(
                {
                    "class_name": item["class_name"],
                    "method_name": method_name,
                    "called_methods": "",
                    "used_variables": "",
                }
            )

    condition_count = len(re.findall(r"\b(if|elif|switch|case)\b|\?", text))
    loop_count = len(re.findall(r"\b(for|while|do)\b", text))

    return {
        "class_count": len(class_metrics),
        "method_count": len(method_metrics),
        "condition_count": condition_count,
        "loop_count": loop_count,
        "class_metrics": class_metrics,
        "method_metrics": method_metrics,
    }


def analyze_single_file(filename: str, content: bytes, language: Optional[str] = None) -> dict:
    detected = detect_language(filename, language)
    text = _decode_bytes(content)
    stats = scan_lines(text, detected)
    ratio = 0.0 if stats["total_lines"] == 0 else stats["comment_lines"] / stats["total_lines"]

    class_count = 0
    method_count = 0
    class_scales = []
    method_scales = []
    structure_analysis = None

    if detected == "java":
        structure_analysis = analyze_java_structure(text)
    elif detected in {"python", "cpp", "c", "javascript"}:
        structure_analysis = _analyze_non_java_structure(filename, text, detected)

    if structure_analysis:
        class_count = structure_analysis["class_count"]
        method_count = structure_analysis["method_count"]

        class_scales = [
            {
                "class_name": item["class_name"],
                "method_count": item["method_count"],
                "field_count": item["field_count"],
                "rfc": item["rfc"],
                "lcom": item["lcom"],
            }
            for item in structure_analysis["class_metrics"]
        ]
        method_scales = structure_analysis["method_metrics"]

    return {
        "filename": filename,
        "language": detected,
        **stats,
        "comment_ratio": round(ratio, 4),
        "class_count": class_count,
        "method_count": method_count,
        "class_scales": class_scales,
        "method_scales": method_scales,
        "structure_analysis": structure_analysis,
    }


def analyze_files(files: Iterable[dict], language: Optional[str] = None) -> dict:
    results = []
    total = {
        "total_lines": 0,
        "blank_lines": 0,
        "comment_lines": 0,
        "code_lines": 0,
        "class_count": 0,
        "method_count": 0,
    }

    all_class_scales = []
    all_method_scales = []
    structure_summaries = []

    for item in files:
        res = analyze_single_file(item["filename"], item["content"], language)
        results.append(res)
        for key in total:
            total[key] += res[key]

        if res.get("class_scales"):
            for cls in res["class_scales"]:
                all_class_scales.append({"filename": res["filename"], **cls})

        if res.get("method_scales"):
            for m in res["method_scales"]:
                all_method_scales.append({"filename": res["filename"], **m})

        if res.get("structure_analysis"):
            structure_summaries.append(
                {
                    "filename": res["filename"],
                    "language": res["language"],
                    "class_count": res["structure_analysis"]["class_count"],
                    "method_count": res["structure_analysis"]["method_count"],
                    "condition_count": res["structure_analysis"]["condition_count"],
                    "loop_count": res["structure_analysis"]["loop_count"],
                }
            )

    total_ratio = 0.0 if total["total_lines"] == 0 else total["comment_lines"] / total["total_lines"]
    return {
        "files": results,
        "summary": {**total, "comment_ratio": round(total_ratio, 4)},
        "class_scales": all_class_scales,
        "method_scales": all_method_scales,
        "structure_summaries": structure_summaries,
        "java_structure_summaries": structure_summaries,
    }
