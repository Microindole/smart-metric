from __future__ import annotations

import re
from itertools import combinations

METHOD_KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "new", "throw", "else", "do"}


def _strip_comments(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"//.*", "", source)
    return source


def _find_block_end(text: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def _extract_classes(code: str) -> list[dict]:
    classes = []
    for m in re.finditer(r"\bclass\s+(\w+)\b[^\{]*\{", code):
        class_name = m.group(1)
        open_idx = code.find("{", m.start())
        end_idx = _find_block_end(code, open_idx)
        classes.append({"name": class_name, "body": code[open_idx + 1 : end_idx]})
    return classes


def _extract_methods(class_body: str) -> list[dict]:
    method_pat = re.compile(
        r"^\s*(?:(?:public|protected|private|static|final|native|synchronized|abstract)\s+)*(?:[\w<>\[\],?]+\s+)?(\w+)\s*\(([^)]*)\)\s*\{",
        flags=re.M,
    )

    methods = []
    for m in method_pat.finditer(class_body):
        name = m.group(1)
        if name in METHOD_KEYWORDS:
            continue

        start_brace = class_body.find("{", m.start())
        end_brace = _find_block_end(class_body, start_brace)
        body = class_body[start_brace + 1 : end_brace]

        params_text = (m.group(2) or "").strip()
        params = []
        if params_text:
            for p in params_text.split(","):
                p = p.strip()
                if not p:
                    continue
                token = p.split()[-1].replace("[]", "")
                if token:
                    params.append(token)

        methods.append({"name": name, "body": body, "params": params})

    return methods


def _extract_fields(class_body: str) -> set[str]:
    fields = set()
    depth = 0
    for raw in class_body.splitlines():
        line = raw.strip()
        if not line:
            continue

        if depth == 0 and line.endswith(";") and "(" not in line:
            m = re.match(
                r"(?:(?:public|protected|private)\s+)?(?:(?:static|final)\s+)*(?:[\w<>\[\],?]+)\s+(\w+)\s*(?:=.+)?;",
                line,
            )
            if m:
                fields.add(m.group(1))

        depth += line.count("{")
        depth -= line.count("}")

    return fields


def _extract_local_vars(method_body: str) -> set[str]:
    local_pat = re.compile(r"\b(?:int|long|double|float|boolean|char|byte|short|String|var|[A-Z]\w*)\s+(\w+)\b")
    return {m.group(1) for m in local_pat.finditer(method_body)}


def _extract_called_methods(method_body: str, self_name: str) -> list[str]:
    calls = []
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", method_body):
        name = m.group(1)
        if name in METHOD_KEYWORDS or name == self_name:
            continue
        calls.append(name)
    return sorted(set(calls))


def _used_variables(method_body: str, candidates: set[str]) -> list[str]:
    used = []
    for name in sorted(candidates):
        if re.search(rf"\b{re.escape(name)}\b", method_body):
            used.append(name)
    return used


def _lcom_by_fields(method_field_usage: list[set[str]]) -> int:
    if len(method_field_usage) <= 1:
        return 0

    p = 0
    q = 0
    for a, b in combinations(method_field_usage, 2):
        if a.intersection(b):
            q += 1
        else:
            p += 1
    return max(p - q, 0)


def analyze_java_structure(text: str) -> dict:
    code = _strip_comments(text)
    class_metrics = []
    method_metrics = []

    total_class_count = 0
    total_method_count = 0

    classes = _extract_classes(code)
    for cls in classes:
        total_class_count += 1
        class_name = cls["name"]
        class_body = cls["body"]

        fields = _extract_fields(class_body)
        methods = _extract_methods(class_body)
        total_method_count += len(methods)

        own_method_names = {m["name"] for m in methods}
        all_called = set()
        method_field_usage = []

        for m in methods:
            method_name = m["name"]
            body = m["body"]
            params = set(m["params"])
            locals_ = _extract_local_vars(body)

            called = _extract_called_methods(body, method_name)
            all_called.update(called)

            used = _used_variables(body, fields.union(params).union(locals_))
            used_fields = set(used).intersection(fields)
            method_field_usage.append(used_fields)

            method_metrics.append(
                {
                    "class_name": class_name,
                    "method_name": method_name,
                    "called_methods": ", ".join(called),
                    "used_variables": ", ".join(used),
                }
            )

        rfc = len(own_method_names.union(all_called))
        lcom = _lcom_by_fields(method_field_usage)

        class_metrics.append(
            {
                "class_name": class_name,
                "rfc": rfc,
                "lcom": lcom,
                "method_count": len(methods),
                "field_count": len(fields),
            }
        )

    condition_lines = len(re.findall(r"\b(if|switch|case|\?)\b", code))
    loop_lines = len(re.findall(r"\b(for|while|do)\b", code))

    return {
        "class_count": total_class_count,
        "method_count": total_method_count,
        "condition_count": condition_lines,
        "loop_count": loop_lines,
        "class_metrics": class_metrics,
        "method_metrics": method_metrics,
    }
