from __future__ import annotations

from typing import Dict, List

from .base import ControlFlowAnalyzer, Decision, ensure_summary_keys
from .c_style import CStyleAnalyzer


class JavaAstAnalyzer(ControlFlowAnalyzer):
    language = "java"
    analysis_method = "ast-java-javalang"

    def analyze(self, text: str) -> Dict:
        try:
            import javalang  # noqa: F401

            return super().analyze(text)
        except Exception:
            result = CStyleAnalyzer("java").analyze(text)
            result["analysis_method"] = "rule-c-style-fallback"
            return result

    def strip_comments(self, text: str) -> str:
        return text

    def summary(self, text: str) -> Dict[str, int]:
        tree = parse_java(text)
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
        for _, node in tree:
            name = node.__class__.__name__
            if name == "IfStatement":
                result["if"] += 1
            elif name == "ForStatement":
                result["for"] += 1
            elif name == "WhileStatement":
                result["while"] += 1
            elif name == "DoStatement":
                result["do"] += 1
                result["while"] += 1
            elif name == "SwitchStatement":
                result["switch"] += 1
            elif name == "SwitchStatementCase":
                result["case"] += 1
                if not getattr(node, "case", None):
                    result["default"] += 1
            elif name == "CatchClause":
                result["catch"] += 1
            elif name == "TernaryExpression":
                result["ternary"] += 1
            elif name == "BinaryOperation":
                operator = getattr(node, "operator", "")
                if operator == "&&":
                    result["and"] += 1
                elif operator == "||":
                    result["or"] += 1
        return ensure_summary_keys(result)

    def decisions(self, text: str) -> List[Decision]:
        tree = parse_java(text)
        decisions: List[Decision] = []
        for _, node in tree:
            name = node.__class__.__name__
            position = getattr(node, "position", None)
            line = getattr(position, "line", 0) if position else 0
            if name == "IfStatement":
                decisions.append(Decision("if", f"if line {line}"))
            elif name == "ForStatement":
                decisions.append(Decision("for", f"for line {line}"))
            elif name == "WhileStatement":
                decisions.append(Decision("while", f"while line {line}"))
            elif name == "DoStatement":
                decisions.append(Decision("while", f"do-while line {line}"))
            elif name == "SwitchStatement":
                decisions.append(Decision("switch", f"switch line {line}"))
            elif name == "SwitchStatementCase":
                kind = "default" if not getattr(node, "case", None) else "case"
                decisions.append(Decision(kind, f"{kind} line {line}"))
            elif name == "CatchClause":
                decisions.append(Decision("catch", f"catch line {line}"))
            elif name == "TernaryExpression":
                decisions.append(Decision("ternary", f"三元表达式 line {line}"))
            elif name == "BinaryOperation":
                operator = getattr(node, "operator", "")
                if operator == "&&":
                    decisions.append(Decision("and", f"短路与 line {line}"))
                elif operator == "||":
                    decisions.append(Decision("or", f"短路或 line {line}"))
        return decisions


def parse_java(text: str):
    import javalang

    return javalang.parse.parse(text)
