from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set


JAVA_KEYWORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "if",
    "implements",
    "import",
    "int",
    "interface",
    "long",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
}


@dataclass
class JavaClassInfo:
    name: str
    parent: str | None = None
    body: str = ""
    fields: Set[str] = field(default_factory=set)
    methods: Dict[str, str] = field(default_factory=dict)
    references: Set[str] = field(default_factory=set)


def analyze_java_source(filename: str, text: str) -> List[Dict]:
    cleaned = strip_comments(text)
    classes = extract_classes(cleaned)
    parent_map = {item.name: item.parent for item in classes}
    child_count: Dict[str, int] = {}
    for item in classes:
        if item.parent:
            child_count[item.parent] = child_count.get(item.parent, 0) + 1

    results = []
    for item in classes:
        populate_members(item)
        wmc = sum(method_complexity(body) for body in item.methods.values())
        dit = inheritance_depth(item.name, parent_map)
        noc = child_count.get(item.name, 0)
        cbo = len({ref for ref in item.references if ref != item.name and ref not in JAVA_KEYWORDS})
        rfc = len(item.methods) + len(extract_method_calls(item.body))
        lcom = lcom_value(item)
        lk = {
            "nom": len(item.methods),
            "noa": len(item.fields),
            "class_loc": count_code_lines(item.body),
            "avg_method_complexity": round(wmc / len(item.methods), 4) if item.methods else 0,
        }

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
                "lk": lk,
                "fields": sorted(item.fields),
                "methods": sorted(item.methods.keys()),
                "references": sorted(item.references),
            }
        )
    return results


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_classes(text: str) -> List[JavaClassInfo]:
    pattern = re.compile(r"\bclass\s+([A-Za-z_]\w*)(?:\s+extends\s+([A-Za-z_]\w*))?[^{]*\{")
    classes: List[JavaClassInfo] = []
    for match in pattern.finditer(text):
        start = match.end() - 1
        end = matching_brace(text, start)
        if end == -1:
            continue
        classes.append(JavaClassInfo(name=match.group(1), parent=match.group(2), body=text[start + 1 : end]))
    return classes


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


def populate_members(item: JavaClassInfo) -> None:
    method_pattern = re.compile(
        r"(?:public|private|protected|static|final|synchronized|abstract|\s)+\s*"
        r"([A-Za-z_][\w<>\[\]]*)\s+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{"
    )
    method_ranges = []
    for match in method_pattern.finditer(item.body):
        start = match.end() - 1
        end = matching_brace(item.body, start)
        if end == -1:
            continue
        name = match.group(2)
        item.methods[name] = item.body[start + 1 : end]
        method_ranges.append((match.start(), end + 1))
        item.references.add(clean_type(match.group(1)))

    field_area = remove_ranges(item.body, method_ranges)
    field_pattern = re.compile(
        r"(?:public|private|protected|static|final|transient|volatile|\s)+\s*"
        r"([A-Za-z_][\w<>\[\]]*)\s+([A-Za-z_]\w*)\s*(?:=[^;]*)?;"
    )
    for match in field_pattern.finditer(field_area):
        item.references.add(clean_type(match.group(1)))
        item.fields.add(match.group(2))

    for ref in re.findall(r"\bnew\s+([A-Z][A-Za-z_]\w*)\s*\(", item.body):
        item.references.add(ref)
    for ref in re.findall(r"\b([A-Z][A-Za-z_]\w*)\b", item.body):
        if ref != item.name:
            item.references.add(ref)


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


def clean_type(type_name: str) -> str:
    return re.sub(r"[<\[].*", "", type_name).strip()


def method_complexity(body: str) -> int:
    decision_count = 0
    for pattern in (r"\bif\s*\(", r"\bfor\s*\(", r"\bwhile\s*\(", r"\bcase\b", r"\bcatch\s*\(", r"\?", r"&&", r"\|\|"):
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
        if call not in {"if", "for", "while", "switch", "catch", "return", "new"}:
            calls.add(call)
    return calls


def lcom_value(item: JavaClassInfo) -> int:
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
