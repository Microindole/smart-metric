from __future__ import annotations

import ast
from typing import Dict, List, Set

from .base import SourceAnalyzer, SourceClassInfo
from .common import build_results


class PythonSourceAnalyzer(SourceAnalyzer):
    language = "python"

    def analyze(self, filename: str, text: str) -> List[Dict]:
        tree = ast.parse(text)
        infos: List[SourceClassInfo] = []

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            info = SourceClassInfo(name=node.name, parent=extract_base(node), body=ast.get_source_segment(text, node) or "")
            info.language = self.language  # type: ignore[attr-defined]
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_text = ast.get_source_segment(text, child) or ""
                    info.methods[child.name] = method_text
                    info.references.update(collect_references(child))
                    info.fields.update(collect_self_fields(child))
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            info.fields.add(target.id)
            infos.append(info)

        return build_results(filename, infos)


def extract_base(node: ast.ClassDef) -> str:
    if not node.bases:
        return ""
    base = node.bases[0]
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""


def collect_self_fields(node: ast.AST) -> Set[str]:
    fields: Set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == "self":
            fields.add(child.attr)
    return fields


def collect_references(node: ast.AST) -> Set[str]:
    refs: Set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name) and func.id[:1].isupper():
                refs.add(func.id)
            elif isinstance(func, ast.Attribute) and func.attr[:1].isupper():
                refs.add(func.attr)
        elif isinstance(child, ast.Name) and child.id[:1].isupper():
            refs.add(child.id)
    return refs
