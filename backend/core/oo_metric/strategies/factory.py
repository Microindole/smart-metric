from __future__ import annotations

from .base import SourceAnalyzer
from .c_strategy import CSourceAnalyzer
from .cpp_strategy import CppSourceAnalyzer
from .java_strategy import JavaSourceAnalyzer
from .javascript_strategy import JavaScriptSourceAnalyzer
from .python_strategy import PythonSourceAnalyzer


def detect_source_language(filename: str, override: str | None = None) -> str:
    if override:
        return normalize_language(override)

    lower = filename.lower()
    if lower.endswith(".java"):
        return "java"
    if lower.endswith((".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx")):
        return "cpp"
    if lower.endswith((".c", ".h")):
        return "c"
    if lower.endswith(".py"):
        return "python"
    if lower.endswith((".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx")):
        return "javascript"
    raise ValueError(f"暂不支持的源码类型: {filename}")


def create_source_analyzer(language: str) -> SourceAnalyzer:
    normalized = normalize_language(language)
    if normalized == "java":
        return JavaSourceAnalyzer()
    if normalized == "python":
        return PythonSourceAnalyzer()
    if normalized == "javascript":
        return JavaScriptSourceAnalyzer()
    if normalized == "cpp":
        return CppSourceAnalyzer()
    if normalized == "c":
        return CSourceAnalyzer()
    raise ValueError(f"暂不支持的源码语言: {language}")


def normalize_language(language: str) -> str:
    lower = language.lower()
    if lower in {"js", "javascript", "ts", "typescript"}:
        return "javascript"
    if lower in {"c++", "cpp", "cc", "cxx"}:
        return "cpp"
    if lower in {"py", "python"}:
        return "python"
    return lower
