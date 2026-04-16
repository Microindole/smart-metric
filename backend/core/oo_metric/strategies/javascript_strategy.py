from __future__ import annotations

import re
from typing import Dict, List

from .base import SourceAnalyzer, SourceClassInfo
from .common import build_results

CONTROL_KEYWORDS = {"if", "for", "while", "switch", "catch"}


class JavaScriptSourceAnalyzer(SourceAnalyzer):
    language = "javascript"

    def analyze(self, filename: str, text: str) -> List[Dict]:
        cleaned = strip_comments(text)
        infos = extract_classes(cleaned)
        return build_results(filename, infos)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_classes(text: str) -> List[SourceClassInfo]:
    pattern = re.compile(r"\bclass\s+([A-Za-z_]\w*)(?:\s+extends\s+([A-Za-z_]\w*))?\s*\{")
    infos: List[SourceClassInfo] = []
    for match in pattern.finditer(text):
        start = match.end() - 1
        end = matching_brace(text, start)
        if end == -1:
            continue
        info = SourceClassInfo(name=match.group(1), parent=match.group(2) or "", body=text[start + 1 : end])
        info.language = "javascript"  # type: ignore[attr-defined]
        populate_members(info)
        infos.append(info)
    return infos


def populate_members(info: SourceClassInfo) -> None:
    method_pattern = re.compile(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{")
    for match in method_pattern.finditer(info.body):
        start = match.end() - 1
        end = matching_brace(info.body, start)
        if end == -1:
            continue
        name = match.group(1)
        if name in CONTROL_KEYWORDS:
            continue
        info.methods[name] = info.body[start + 1 : end]

    info.fields.update(re.findall(r"\bthis\.([A-Za-z_]\w*)\s*=", info.body))
    info.references.update(re.findall(r"\bnew\s+([A-Z][A-Za-z_]\w*)\s*\(", info.body))
    info.references.update(ref for ref in re.findall(r"\b([A-Z][A-Za-z_]\w*)\b", info.body) if ref != info.name)


def matching_brace(text: str, start: int) -> int:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1
