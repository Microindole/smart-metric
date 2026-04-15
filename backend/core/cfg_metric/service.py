from __future__ import annotations

from typing import Iterable, Optional

from core.loc_metric.service import _decode_bytes

from .analyzers import create_analyzer


LANGUAGE_ALIASES = {
    ".java": "java",
    ".c": "c",
    ".py": "python",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".h": "cpp",
}


def analyze_single_cfg(filename: str, content: bytes, language: Optional[str] = None) -> dict:
    detected = detect_cfg_language(filename, language)
    text = _decode_bytes(content)
    analysis = create_analyzer(detected).analyze(text)
    return {
        "filename": filename,
        **analysis,
    }


def analyze_cfg_files(files: Iterable[dict], language: Optional[str] = None) -> dict:
    results = [analyze_single_cfg(item["filename"], item["content"], language) for item in files]
    if not results:
        return {"files": [], "summary": {"file_count": 0, "max_complexity": 0, "average_complexity": 0}}

    total_complexity = sum(item["cyclomatic_complexity"] for item in results)
    return {
        "files": results,
        "summary": {
            "file_count": len(results),
            "max_complexity": max(item["cyclomatic_complexity"] for item in results),
            "average_complexity": round(total_complexity / len(results), 4),
            "total_decision_points": sum(item["decision_points"] for item in results),
        },
    }


def detect_cfg_language(filename: str, specified: str | None = None) -> str:
    if specified:
        return specified.lower().strip()
    lower = filename.lower()
    for ext, lang in LANGUAGE_ALIASES.items():
        if lower.endswith(ext):
            return lang
    raise ValueError(f"不支持的控制流图度量文件类型: {filename}")
