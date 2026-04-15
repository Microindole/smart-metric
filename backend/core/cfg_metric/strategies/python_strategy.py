from __future__ import annotations

import re
from typing import Dict, List

from .base import ControlFlowAnalyzer, Decision, ensure_summary_keys


class PythonAnalyzer(ControlFlowAnalyzer):
    """Strategy for Python.

    This rule-based implementation can later be replaced by a standard-library
    `ast` visitor without changing the rest of the system.
    """

    language = "python"
    analysis_method = "rule-python"

    PATTERNS = {
        "if": r"(?m)^\s*(?:if|elif)\b[^:\n]*:",
        "for": r"(?m)^\s*for\b[^:\n]*:",
        "while": r"(?m)^\s*while\b[^:\n]*:",
        "case": r"(?m)^\s*case\b[^:\n]*:",
        "catch": r"(?m)^\s*except\b[^:\n]*:",
        "ternary": r"\bif\b[^\n]+?\belse\b",
        "and": r"\band\b",
        "or": r"\bor\b",
    }

    def strip_comments(self, text: str) -> str:
        return re.sub(r"(?m)#.*$", "", text)

    def summary(self, text: str) -> Dict[str, int]:
        result = {key: len(re.findall(pattern, text)) for key, pattern in self.PATTERNS.items()}
        result["switch"] = 0
        result["default"] = 0
        result["do"] = 0
        return ensure_summary_keys(result)

    def decisions(self, text: str) -> List[Decision]:
        decisions: List[Decision] = []
        pattern = re.compile(r"(?m)^\s*(if|elif|for|while|except|case)\b([^:\n]*):")
        for match in pattern.finditer(text):
            raw_kind = match.group(1)
            kind = "if" if raw_kind == "elif" else "catch" if raw_kind == "except" else raw_kind
            condition = re.sub(r"\s+", " ", match.group(2).strip())
            decisions.append(Decision(kind, f"{raw_kind} {condition}".strip()[:80]))
        decisions.extend(
            Decision("ternary", f"Python 条件表达式 {index + 1}")
            for index in range(len(re.findall(self.PATTERNS["ternary"], text)))
        )
        decisions.extend(
            Decision("and", f"短路与 {index + 1}") for index in range(len(re.findall(self.PATTERNS["and"], text)))
        )
        decisions.extend(
            Decision("or", f"短路或 {index + 1}") for index in range(len(re.findall(self.PATTERNS["or"], text)))
        )
        return decisions
