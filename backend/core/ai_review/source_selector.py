from __future__ import annotations

import re
import ast
from pathlib import Path


FILE_PATTERN = re.compile(r"(?P<path>[A-Za-z0-9_./\\-]+\.(?:py|java|js|ts|cpp|cc|cxx|c|h|hpp|xml|oom|json))")


def extract_focus_files(phase1_result: dict, raw_text: str = "") -> list[str]:
    collected: list[str] = []
    for item in phase1_result.get("focus_files", []):
        value = str(item or "").strip()
        if value:
            collected.append(normalize_path(value))
    for item in phase1_result.get("findings", []):
        value = str(item.get("filename", "")).strip()
        if value:
            collected.append(normalize_path(value))
    if raw_text:
        for match in FILE_PATTERN.finditer(raw_text):
            collected.append(normalize_path(match.group("path")))
    return list(dict.fromkeys(path for path in collected if path))


def build_source_bundle(root: Path, project_result: dict, complexity_result: dict, focus_files: list[str], max_chars: int = 6000) -> dict:
    loc_index = {normalize_path(item["filename"]): item for item in project_result.get("loc", {}).get("files", [])}
    complexity_index = {normalize_path(item["filename"]): item for item in complexity_result.get("files", [])}
    files = []
    for relative in focus_files[:8]:
        normalized = normalize_path(relative)
        target = root / Path(normalized)
        if not target.exists() or not target.is_file():
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        if len(text) > max_chars:
            excerpt = text[: max_chars // 2] + "\n...\n" + text[-max_chars // 2 :]
        else:
            excerpt = text
        loc = loc_index.get(normalized, {})
        complexity = complexity_index.get(normalized, {})
        files.append(
            {
                "filename": normalized,
                "language": loc.get("language", ""),
                "code_lines": loc.get("code_lines", 0),
                "cyclomatic_complexity": complexity.get("cyclomatic_complexity", 0),
                "symbols": extract_symbols(excerpt, loc.get("language", "")),
                "source_excerpt": excerpt,
            }
        )
    return {"files": files}


def normalize_path(value: str) -> str:
    return str(Path(value.replace("\\", "/"))).replace("\\", "/").lstrip("./")


def extract_symbols(source_text: str, language: str) -> list[str]:
    if language == "python":
        try:
            tree = ast.parse(source_text)
        except SyntaxError:
            return []
        names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
        return list(dict.fromkeys(names[:12]))

    pattern = re.compile(r"\b(class|def|function)\s+([A-Za-z_][A-Za-z0-9_]*)")
    names = [match.group(2) for match in pattern.finditer(source_text)]
    return list(dict.fromkeys(names[:12]))
