from __future__ import annotations

import re
from typing import Dict, Iterable, List, Set

from .base import SourceClassInfo


KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "class",
    "struct",
    "function",
    "def",
    "try",
}


def build_results(filename: str, infos: List[SourceClassInfo]) -> List[Dict]:
    parent_map = {item.name: (item.parent or None) for item in infos}
    child_count: Dict[str, int] = {}
    for item in infos:
        if item.parent:
            child_count[item.parent] = child_count.get(item.parent, 0) + 1

    results = []
    for item in infos:
        wmc = sum(method_complexity(body) for body in item.methods.values())
        dit = inheritance_depth(item.name, parent_map)
        noc = child_count.get(item.name, 0)
        cbo = len({ref for ref in item.references if ref and ref != item.name and ref not in KEYWORDS})
        rfc = len(item.methods) + len(extract_method_calls(item.body))
        lcom = lcom_value(item)
        results.append(
            {
                "filename": filename,
                "class_name": item.name,
                "parent": item.parent or "",
                "ck": {
                    "wmc": wmc,
                    "dit": dit,
                    "noc": noc,
                    "cbo": cbo,
                    "rfc": rfc,
                    "lcom": lcom,
                },
                "lk": {
                    "nom": len(item.methods),
                    "noa": len(item.fields),
                    "class_loc": count_code_lines(item.body),
                    "avg_method_complexity": round(wmc / len(item.methods), 4) if item.methods else 0,
                },
                "fields": sorted(item.fields),
                "methods": sorted(item.methods.keys()),
                "references": sorted(item.references),
                "language": item.language,
            }
        )
    return results


def method_complexity(body: str) -> int:
    decision_count = 0
    for pattern in (r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\?", r"&&", r"\|\|", r"\band\b", r"\bor\b"):
        decision_count += len(re.findall(pattern, body))
    return decision_count + 1


def inheritance_depth(class_name: str, parent_map: Dict[str, str | None]) -> int:
    depth = 0
    seen = set()
    current = parent_map.get(class_name)
    while current and current not in seen:
        depth += 1
        seen.add(current)
        current = parent_map.get(current)
    return depth


def extract_method_calls(body: str) -> Set[str]:
    calls = set()
    for call in re.findall(r"\b([A-Za-z_]\w*)\s*\(", body):
        if call not in KEYWORDS:
            calls.add(call)
    return calls


def lcom_value(item: SourceClassInfo) -> int:
    methods = list(item.methods.items())
    if len(methods) < 2 or not item.fields:
        return 0

    field_usage = []
    for _, body in methods:
        used = {field for field in item.fields if re.search(rf"\b{re.escape(field)}\b", body)}
        field_usage.append(used)

    disjoint = shared = 0
    for i in range(len(field_usage)):
        for j in range(i + 1, len(field_usage)):
            if field_usage[i].intersection(field_usage[j]):
                shared += 1
            else:
                disjoint += 1
    return max(disjoint - shared, 0)


def count_code_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())
