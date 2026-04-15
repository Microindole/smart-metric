from __future__ import annotations

import re
from typing import Dict, List

from .base import ControlFlowAnalyzer, Decision, ensure_summary_keys


class CStyleAnalyzer(ControlFlowAnalyzer):
    """Strategy for Java/C/C++ style languages.

    This is a rule-based implementation. It can be replaced by JavaParser,
    Eclipse ASTParser, or clang-based implementations while keeping the same
    strategy interface.
    """

    analysis_method = "rule-c-style"

    PATTERNS = {
        "if": r"\bif\s*\(",
        "for": r"\bfor\s*\(",
        "while": r"\bwhile\s*\(",
        "switch": r"\bswitch\s*\(",
        "case": r"\bcase\b",
        "default": r"\bdefault\s*:",
        "catch": r"\bcatch\s*\(",
        "ternary": r"\?",
        "and": r"&&",
        "or": r"\|\|",
    }

    def __init__(self, language: str):
        self.language = language

    def strip_comments(self, text: str) -> str:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        return re.sub(r"//.*", "", text)

    def summary(self, text: str) -> Dict[str, int]:
        result = {key: len(re.findall(pattern, text)) for key, pattern in self.PATTERNS.items()}
        result["do"] = len(re.findall(r"\bdo\b", text))
        return ensure_summary_keys(result)

    def decisions(self, text: str) -> List[Decision]:
        decisions: List[Decision] = []
        pattern = re.compile(
            r"\b(if|for|while|switch|catch)\s*\(([^)]*)\)|\b(case)\s+([^:]+):|\b(default)\s*:",
            flags=re.S,
        )
        for match in pattern.finditer(text):
            kind = match.group(1) or match.group(3) or match.group(5) or "decision"
            condition = re.sub(r"\s+", " ", (match.group(2) or match.group(4) or "").strip())
            label = f"{kind} ({condition})" if condition else kind
            decisions.append(Decision(kind, label[:80]))
        decisions.extend(Decision("ternary", f"三元表达式 {index + 1}") for index in range(text.count("?")))
        decisions.extend(Decision("and", f"短路与 {index + 1}") for index in range(text.count("&&")))
        decisions.extend(Decision("or", f"短路或 {index + 1}") for index in range(text.count("||")))
        return decisions
