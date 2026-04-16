from __future__ import annotations

from .base import ControlFlowAnalyzer
from .c_style import CStyleAnalyzer
from .java_ast import JavaAstAnalyzer
from .python_ast import PythonAstAnalyzer


def create_analyzer(language: str) -> ControlFlowAnalyzer:
    if language == "python":
        return PythonAstAnalyzer()
    if language == "java":
        return JavaAstAnalyzer()
    if language in {"c", "cpp"}:
        return CStyleAnalyzer(language)
    raise ValueError(f"暂不支持语言: {language}")
