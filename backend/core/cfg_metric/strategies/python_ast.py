from __future__ import annotations

import ast
from typing import Dict, List

from .base import ControlFlowAnalyzer, Decision, ensure_summary_keys
from .python_strategy import PythonAnalyzer


class PythonAstAnalyzer(ControlFlowAnalyzer):
    language = "python"
    analysis_method = "ast-python"

    def analyze(self, text: str) -> Dict:
        try:
            return super().analyze(text)
        except SyntaxError:
            result = PythonAnalyzer().analyze(text)
            result["analysis_method"] = "rule-python-fallback"
            return result

    def strip_comments(self, text: str) -> str:
        return text

    def summary(self, text: str) -> Dict[str, int]:
        tree = ast.parse(text)
        result = {
            "if": 0,
            "for": 0,
            "while": 0,
            "switch": 0,
            "case": 0,
            "default": 0,
            "catch": 0,
            "ternary": 0,
            "and": 0,
            "or": 0,
            "do": 0,
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                result["if"] += 1
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                result["for"] += 1
            elif isinstance(node, ast.While):
                result["while"] += 1
            elif isinstance(node, ast.ExceptHandler):
                result["catch"] += 1
            elif isinstance(node, ast.IfExp):
                result["ternary"] += 1
            elif isinstance(node, ast.BoolOp):
                increment = max(len(node.values) - 1, 0)
                if isinstance(node.op, ast.And):
                    result["and"] += increment
                elif isinstance(node.op, ast.Or):
                    result["or"] += increment
            elif hasattr(ast, "Match") and isinstance(node, ast.Match):
                result["switch"] += 1
                result["case"] += len(getattr(node, "cases", []))
        return ensure_summary_keys(result)

    def decisions(self, text: str) -> List[Decision]:
        tree = ast.parse(text)
        decisions: List[Decision] = []
        for node in ast.walk(tree):
            line = getattr(node, "lineno", 0)
            if isinstance(node, ast.If):
                decisions.append(Decision("if", f"if line {line}"))
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                decisions.append(Decision("for", f"for line {line}"))
            elif isinstance(node, ast.While):
                decisions.append(Decision("while", f"while line {line}"))
            elif isinstance(node, ast.ExceptHandler):
                decisions.append(Decision("catch", f"except line {line}"))
            elif isinstance(node, ast.IfExp):
                decisions.append(Decision("ternary", f"条件表达式 line {line}"))
            elif isinstance(node, ast.BoolOp):
                increment = max(len(node.values) - 1, 0)
                kind = "and" if isinstance(node.op, ast.And) else "or"
                decisions.extend(Decision(kind, f"短路{kind.upper()} line {line}") for _ in range(increment))
            elif hasattr(ast, "Match") and isinstance(node, ast.Match):
                decisions.append(Decision("switch", f"match line {line}"))
                for case in getattr(node, "cases", []):
                    case_line = getattr(case.pattern, "lineno", line)
                    decisions.append(Decision("case", f"case line {case_line}"))
        return decisions
