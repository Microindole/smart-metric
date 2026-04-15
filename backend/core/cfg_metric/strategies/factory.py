from __future__ import annotations

from .base import ControlFlowAnalyzer
from .c_style import CStyleAnalyzer
from .python_strategy import PythonAnalyzer


def create_analyzer(language: str) -> ControlFlowAnalyzer:
    if language == "python":
        return PythonAnalyzer()
    if language in {"java", "c", "cpp"}:
        return CStyleAnalyzer(language)
    raise ValueError(f"暂不支持语言: {language}")
