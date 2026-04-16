from __future__ import annotations

import re
from typing import List

from .base import SourceAnalyzer, SourceClassInfo
from .common import build_results


class CSourceAnalyzer(SourceAnalyzer):
    language = "c"

    def analyze(self, filename: str, text: str):
        cleaned = strip_comments(text)
        infos = extract_structs(cleaned)
        attach_functions(cleaned, infos)
        return build_results(filename, infos)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_structs(text: str) -> List[SourceClassInfo]:
    pattern = re.compile(r"\b(?:typedef\s+)?struct\s+([A-Za-z_]\w*)?\s*\{")
    infos: List[SourceClassInfo] = []
    for match in pattern.finditer(text):
        start = match.end() - 1
        end = matching_brace(text, start)
        if end == -1:
            continue
        tail = text[end + 1 : end + 50]
        typedef_match = re.search(r"\s*([A-Za-z_]\w*)\s*;", tail)
        name = typedef_match.group(1) if typedef_match else (match.group(1) or f"struct_{len(infos)+1}")
        info = SourceClassInfo(name=name, body=text[start + 1 : end])
        info.language = "c"  # type: ignore[attr-defined]
        for field_type, field_name in re.findall(r"\b([A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*;", info.body):
            info.fields.add(field_name)
            if field_type[:1].isupper():
                info.references.add(field_type)
        infos.append(info)
    return infos


def attach_functions(text: str, infos: List[SourceClassInfo]) -> None:
    function_pattern = re.compile(r"\b[A-Za-z_]\w*\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*\{")
    info_map = {info.name: info for info in infos}
    for match in function_pattern.finditer(text):
        func_name = match.group(1)
        params = match.group(2)
        start = match.end() - 1
        end = matching_brace(text, start)
        if end == -1:
            continue
        owner = detect_owner(func_name, params, info_map)
        if not owner:
            continue
        body = text[start + 1 : end]
        info_map[owner].methods[func_name] = body
        info_map[owner].references.update(ref for ref in re.findall(r"\b([A-Z][A-Za-z_]\w*)\b", body) if ref != owner)


def detect_owner(func_name: str, params: str, info_map: dict[str, SourceClassInfo]) -> str:
    for name in info_map:
        if func_name.lower().startswith(name.lower() + "_"):
            return name
        if re.search(rf"\b(?:struct\s+)?{re.escape(name)}\s*\*", params):
            return name
    return ""


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
