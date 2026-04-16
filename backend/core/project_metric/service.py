from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

from core.cfg_metric import analyze_imported_graph
from core.loc_metric.service import analyze_files
from core.class_diagram_metric import analyze_class_diagram_bytes
from core.diagram_parser.service import parse_usecase_diagram
from core.oo_metric import analyze_oo_files
from core.usecase_metric import calculate_usecase_metrics, parse_oom_and_suggest_counts


SUPPORTED_CODE_EXTS = {
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".cc",
    ".cxx",
    ".hpp",
    ".hh",
    ".hxx",
    ".py",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".nuxt",
    ".output",
    "dist",
    "build",
    ".idea",
    ".vscode",
}


def analyze_project_directory(root_path: str, modules: Iterable[str] | None = None) -> dict:
    root = Path(root_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"项目目录不存在: {root}")

    requested = set(modules or {"inventory", "loc", "dependency", "oo", "design"})
    inventory = scan_inventory(root)
    result = {
        "root": str(root),
        "inventory": inventory,
        "summary": {
            "total_files": inventory["total_files"],
            "code_file_count": inventory["code_file_count"],
            "design_file_count": inventory["design_file_count"],
        },
    }

    code_files = inventory["code_files"]

    if "loc" in requested:
        loc_result = analyze_code_loc(root, code_files)
        result["loc"] = loc_result
        result["summary"]["total_lines"] = loc_result["summary"]["total_lines"]
        result["summary"]["code_lines"] = loc_result["summary"]["code_lines"]
        result["summary"]["language_breakdown"] = loc_result["summary"]["language_breakdown"]

    if "dependency" in requested:
        dependency_result = analyze_dependencies(root, code_files)
        result["dependencies"] = dependency_result
        result["summary"]["dependency_edge_count"] = dependency_result["summary"]["edge_count"]

    if "oo" in requested:
        oo_result = analyze_code_oo(root, code_files)
        result["oo"] = oo_result
        result["summary"]["class_count"] = oo_result["summary"]["class_count"]
        result["summary"]["god_files"] = oo_result["summary"]["god_file_count"]
        result["summary"]["god_classes"] = oo_result["summary"]["god_class_count"]

    if "design" in requested:
        design_result = analyze_design_artifacts(root, inventory["design_files"])
        result["design"] = design_result
        result["summary"]["usecase_diagram_count"] = design_result["summary"]["usecase_diagram_count"]
        result["summary"]["class_diagram_count"] = design_result["summary"]["class_diagram_count"]
        result["summary"]["cfg_graph_count"] = design_result["summary"]["cfg_graph_count"]

    return result


def scan_inventory(root: Path) -> dict:
    code_files: List[Path] = []
    design_files: List[Path] = []
    design_kinds = Counter()
    total_files = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        total_files += 1
        lower = path.suffix.lower()
        if lower in SUPPORTED_CODE_EXTS:
            code_files.append(path)
            continue
        if lower in {".oom", ".xml", ".json", ".mmd", ".mermaid", ".dot"}:
            kind = classify_design_file(path)
            if kind:
                design_files.append(path)
                design_kinds[kind] += 1

    return {
        "total_files": total_files,
        "code_file_count": len(code_files),
        "design_file_count": len(design_files),
        "code_files": [str(item) for item in code_files],
        "design_files": [{"path": str(path), "kind": classify_design_file(path)} for path in design_files],
        "design_breakdown": dict(design_kinds),
    }


def classify_design_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    suffix = path.suffix.lower()
    content = text.lower()
    if suffix in {".mmd", ".mermaid", ".dot"}:
        return "cfg_graph"
    if suffix == ".json":
        try:
            payload = json.loads(text)
        except Exception:
            return ""
        if isinstance(payload, dict) and "nodes" in payload and "edges" in payload:
            return "cfg_graph"
        return ""
    if "<usecase" in content or "<c:usecases" in content or "<c_usecases" in content:
        return "usecase_diagram"
    if "<class" in content or "<generalization" in content or "<association" in content:
        return "class_diagram"
    if "<decision" in content or "<activityflow" in content or "<c:flow" in content or "<c_flow" in content:
        return "cfg_graph"
    return ""


def analyze_code_loc(root: Path, code_files: List[str]) -> dict:
    payload = [{"filename": str(Path(path).relative_to(root)), "content": Path(path).read_bytes()} for path in code_files]
    loc_result = analyze_files(payload)
    language_breakdown = Counter()
    for item in loc_result["files"]:
        language_breakdown[item["language"]] += 1
    loc_result["summary"]["language_breakdown"] = dict(language_breakdown)
    return loc_result


def analyze_dependencies(root: Path, code_files: List[str]) -> dict:
    file_index = {path: str(Path(path).relative_to(root)).replace("\\", "/") for path in code_files}
    base_to_path = defaultdict(list)
    for path, rel in file_index.items():
        base_to_path[Path(path).stem].append(rel)

    edges = []
    by_file = {}
    for path, rel in file_index.items():
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
        language = detect_source_language(path)
        refs = sorted(extract_dependencies(text, language))
        resolved = []
        for ref in refs:
            for target in base_to_path.get(ref.split(".")[-1], []):
                if target != rel:
                    resolved.append(target)
        unique_resolved = sorted(set(resolved))
        by_file[rel] = {"language": language, "imports": refs, "internal_dependencies": unique_resolved}
        for target in unique_resolved:
            edges.append({"from": rel, "to": target})

    return {
        "files": by_file,
        "edges": edges,
        "summary": {"edge_count": len(edges), "file_count": len(by_file)},
    }


def analyze_design_artifacts(root: Path, design_files: List[dict]) -> dict:
    result = {
        "usecase_diagrams": [],
        "class_diagrams": [],
        "cfg_graphs": [],
        "errors": [],
        "summary": {
            "usecase_diagram_count": 0,
            "class_diagram_count": 0,
            "cfg_graph_count": 0,
        },
    }

    for item in design_files:
        path = Path(item["path"])
        relative = str(path.relative_to(root)).replace("\\", "/")
        kind = item.get("kind", "")
        try:
            content = path.read_bytes()
            if kind == "usecase_diagram":
                parsed = parse_usecase_diagram(path.name, content)
                suggested = parse_oom_and_suggest_counts(parsed)
                metrics = calculate_usecase_metrics(suggested)
                result["usecase_diagrams"].append(
                    {
                        "filename": relative,
                        "metadata": suggested.get("metadata", {}),
                        "actors": len(suggested.get("actors", [])),
                        "use_cases": len(suggested.get("use_cases", [])),
                        "actor_counts": suggested["actor_counts"],
                        "use_case_counts": suggested["use_case_counts"],
                        "ucp": metrics["ucp"],
                    }
                )
                result["summary"]["usecase_diagram_count"] += 1
            elif kind == "class_diagram":
                analyzed = analyze_class_diagram_bytes(path.name, content)
                analyzed["filename"] = relative
                result["class_diagrams"].append(analyzed)
                result["summary"]["class_diagram_count"] += 1
            elif kind == "cfg_graph":
                analyzed = analyze_imported_graph(content, path.name)
                analyzed["filename"] = relative
                result["cfg_graphs"].append(analyzed)
                result["summary"]["cfg_graph_count"] += 1
        except Exception as exc:
            result["errors"].append({"filename": relative, "kind": kind, "message": str(exc)})

    return result


def analyze_code_oo(root: Path, code_files: List[str]) -> dict:
    oo_files = [path for path in code_files if detect_source_language(path) in {"java", "c", "cpp", "python", "javascript"}]
    payload = [{"filename": str(Path(path).relative_to(root)), "content": Path(path).read_bytes()} for path in oo_files]
    oo_result = analyze_oo_files(payload)

    loc_by_file = {}
    if payload:
        loc_payload = [{"filename": item["filename"], "content": item["content"]} for item in payload]
        loc_result = analyze_files(loc_payload)
        loc_by_file = {item["filename"]: item for item in loc_result["files"]}

    god_files = []
    for filename, info in loc_by_file.items():
        reasons = []
        if info["code_lines"] >= 300:
            reasons.append("代码行过多")
        if info.get("class_count", 0) >= 8:
            reasons.append("类数量过多")
        if info.get("method_count", 0) >= 30:
            reasons.append("方法数量过多")
        if reasons:
            god_files.append({"filename": filename, "reasons": reasons, "code_lines": info["code_lines"]})

    god_classes = []
    for item in oo_result.get("classes", []):
        reasons = []
        ck = item.get("ck", {})
        lk = item.get("lk", {})
        if ck.get("wmc", 0) >= 20:
            reasons.append("WMC 过高")
        if ck.get("cbo", 0) >= 8:
            reasons.append("CBO 过高")
        if lk.get("nom", 0) >= 15:
            reasons.append("NOM 过高")
        if reasons:
            god_classes.append(
                {
                    "filename": item["filename"],
                    "class_name": item["class_name"],
                    "language": item.get("language", ""),
                    "reasons": reasons,
                    "wmc": ck.get("wmc", 0),
                    "cbo": ck.get("cbo", 0),
                    "nom": lk.get("nom", 0),
                }
            )

    oo_result["god_files"] = god_files
    oo_result["god_classes"] = god_classes
    oo_result["summary"]["god_file_count"] = len(god_files)
    oo_result["summary"]["god_class_count"] = len(god_classes)
    return oo_result


def detect_source_language(path: str) -> str:
    lower = str(path).lower()
    if lower.endswith(".java"):
        return "java"
    if lower.endswith((".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx")):
        return "cpp"
    if lower.endswith((".c", ".h")):
        return "c"
    if lower.endswith(".py"):
        return "python"
    if lower.endswith((".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx")):
        return "javascript"
    return ""


def extract_dependencies(text: str, language: str) -> set[str]:
    if language == "java":
        return set(re.findall(r"^\s*import\s+([A-Za-z0-9_.*]+);", text, flags=re.M))
    if language == "python":
        refs = set(re.findall(r"^\s*import\s+([A-Za-z0-9_., ]+)", text, flags=re.M))
        refs.update(re.findall(r"^\s*from\s+([A-Za-z0-9_.]+)\s+import", text, flags=re.M))
        normalized = set()
        for item in refs:
            normalized.update(part.strip() for part in item.split(",") if part.strip())
        return normalized
    if language == "javascript":
        refs = set(re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", text))
        refs.update(re.findall(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", text))
        return refs
    if language in {"c", "cpp"}:
        return set(re.findall(r"^\s*#include\s+[\"<]([^\">]+)[\">]", text, flags=re.M))
    return set()
