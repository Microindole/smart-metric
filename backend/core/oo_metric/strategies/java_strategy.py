from __future__ import annotations

from typing import Dict, List

from ..java_analyzer import analyze_java_source
from .base import SourceAnalyzer


class JavaSourceAnalyzer(SourceAnalyzer):
    language = "java"

    def analyze(self, filename: str, text: str) -> List[Dict]:
        results = analyze_java_source(filename, text)
        for item in results:
            item["language"] = self.language
        return results
