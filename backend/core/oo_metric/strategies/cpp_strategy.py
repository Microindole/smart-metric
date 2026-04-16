from __future__ import annotations

import re
from typing import List

from .base import SourceAnalyzer, SourceClassInfo
from .common import build_results


class CppSourceAnalyzer(SourceAnalyzer):
    language = "cpp"

    def analyze(self, filename: str, text: str):
        cleaned = strip_comments(text)
        infos = extract_classes(cleaned)
        return build_results(filename, infos)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_classes(text: str) -> List[SourceClassInfo]:
    pattern = re.compile(r"\b(?:class|struct)\s+([A-Za-z_]\w*)(?:\s*:\s*(?:public|protected|private)?\s*([A-Za-z_]\w*))?\s*\{")
    infos: List[SourceClassInfo] = []
    for match in pattern.finditer(text):
        start = match.end() - 1
        end = matching_brace(text, start)
        if end == -1:
            continue
        info = SourceClassInfo(name=match.group(1), parent=match.group(2) or "", body=text[start + 1 : end])
        info.language = "cpp"  # type: ignore[attr-defined]
        populate_members(info)
        infos.append(info)
    return infos


def populate_members(info: SourceClassInfo) -> None:
    method_pattern = re.compile(
        r"(?:[A-Za-z_][\w:<>\*&\s]+)?\s+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:const\s*)?\{"
    )
    method_ranges = []
    for match in method_pattern.finditer(info.body):
        start = match.end() - 1
        end = matching_brace(info.body, start)
        if end == -1:
            continue
        name = match.group(1)
        info.methods[name] = info.body[start + 1 : end]
        method_ranges.append((match.start(), end + 1))

    field_area = remove_ranges(info.body, method_ranges)
    field_pattern = re.compile(r"\b([A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*;")
    for match in field_pattern.finditer(field_area):
        field_type = match.group(1)
        field_name = match.group(2)
        if field_name in {"public", "private", "protected"}:
            continue
        info.fields.add(field_name)
        if field_type[:1].isupper():
            info.references.add(field_type)

    info.references.update(re.findall(r"\bnew\s+([A-Z][A-Za-z_]\w*)\s*\(", info.body))


def remove_ranges(text: str, ranges: List[tuple[int, int]]) -> str:
    if not ranges:
        return text
    output = []
    cursor = 0
    for start, end in sorted(ranges):
        output.append(text[cursor:start])
        cursor = end
    output.append(text[cursor:])
    return "".join(output)


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
