from __future__ import annotations

from typing import Iterable

from core.loc_metric.service import _decode_bytes

from .strategies import create_source_analyzer, detect_source_language


def analyze_oo_files(files: Iterable[dict], language: str | None = None) -> dict:
    classes = []
    for item in files:
        filename = item["filename"]
        text = _decode_bytes(item["content"])
        detected = detect_source_language(filename, language)
        analyzer = create_source_analyzer(detected)
        classes.extend(analyzer.analyze(filename, text))

    if not classes:
        return {"classes": [], "summary": {"class_count": 0}}

    summary = {
        "class_count": len(classes),
        "total_methods": sum(item["lk"]["nom"] for item in classes),
        "total_attributes": sum(item["lk"]["noa"] for item in classes),
        "average_wmc": round(sum(item["ck"]["wmc"] for item in classes) / len(classes), 4),
        "max_dit": max(item["ck"]["dit"] for item in classes),
        "max_cbo": max(item["ck"]["cbo"] for item in classes),
        "average_lcom": round(sum(item["ck"]["lcom"] for item in classes) / len(classes), 4),
    }
    return {"classes": classes, "summary": summary}
