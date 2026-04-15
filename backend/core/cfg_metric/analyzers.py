"""Compatibility exports for control-flow analyzer strategies."""

from .strategies.base import ControlFlowAnalyzer as BaseAnalyzer
from .strategies.base import Decision
from .strategies.c_style import CStyleAnalyzer
from .strategies.factory import create_analyzer
from .strategies.python_strategy import PythonAnalyzer

__all__ = ["BaseAnalyzer", "CStyleAnalyzer", "Decision", "PythonAnalyzer", "create_analyzer"]
