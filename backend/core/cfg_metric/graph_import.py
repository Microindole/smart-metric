from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple


def analyze_imported_graph(content: bytes, filename: str) -> Dict:
    text = _decode_bytes(content)
    fmt = detect_graph_format(filename, text)
    if fmt == "json":
        nodes, edges = parse_json_graph(text)
    elif fmt == "mermaid":
        nodes, edges = parse_mermaid_graph(text)
    elif fmt == "dot":
        nodes, edges = parse_dot_graph(text)
    else:
        raise ValueError(f"暂不支持的控制流图格式: {filename}")

    nodes = sorted(nodes)
    normalized_edges = sorted(edges)
    node_count = len(nodes)
    edge_count = len(normalized_edges)
    components = connected_components(nodes, normalized_edges)
    complexity = edge_count - node_count + 2 * components if node_count else 0

    return {
        "filename": filename,
        "format": fmt,
        "node_count": node_count,
        "edge_count": edge_count,
        "connected_components": components,
        "cyclomatic_complexity": complexity,
        "nodes": [{"id": node} for node in nodes],
        "edges": [{"from": src, "to": dst} for src, dst in normalized_edges],
        "mermaid": build_mermaid(nodes, normalized_edges),
    }


def detect_graph_format(filename: str, text: str) -> str:
    lower = filename.lower()
    stripped = text.lstrip()
    if lower.endswith(".json") or stripped.startswith("{"):
        return "json"
    if lower.endswith((".mmd", ".mermaid")) or stripped.startswith("flowchart") or stripped.startswith("graph"):
        return "mermaid"
    if lower.endswith(".dot") or stripped.startswith("digraph") or stripped.startswith("graph"):
        return "dot"
    return ""


def parse_json_graph(text: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    payload = json.loads(text)
    raw_nodes = payload.get("nodes", [])
    raw_edges = payload.get("edges", [])

    nodes: Set[str] = set()
    for item in raw_nodes:
        if isinstance(item, str):
            nodes.add(item)
        elif isinstance(item, dict):
            node_id = item.get("id") or item.get("name") or item.get("label")
            if node_id:
                nodes.add(str(node_id))

    edges: Set[Tuple[str, str]] = set()
    for item in raw_edges:
        if isinstance(item, dict):
            src = item.get("from") or item.get("source") or item.get("src")
            dst = item.get("to") or item.get("target") or item.get("dst")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            src, dst = item[0], item[1]
        else:
            continue
        if src is None or dst is None:
            continue
        src_id = str(src)
        dst_id = str(dst)
        nodes.update([src_id, dst_id])
        edges.add((src_id, dst_id))

    return nodes, edges


def parse_mermaid_graph(text: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    nodes: Set[str] = set()
    edges: Set[Tuple[str, str]] = set()
    edge_pattern = re.compile(r"([A-Za-z0-9_]+)(?:\[[^\]]*\]|\([^\)]*\)|\{[^\}]*\})?\s*[-.=]+(?:\|[^|]*\|)?[->.]+\s*([A-Za-z0-9_]+)")

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("%%") or line.startswith(("flowchart", "graph")):
            continue
        match = edge_pattern.search(line)
        if not match:
            continue
        src, dst = match.group(1), match.group(2)
        nodes.update([src, dst])
        edges.add((src, dst))

    return nodes, edges


def parse_dot_graph(text: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    nodes: Set[str] = set()
    edges: Set[Tuple[str, str]] = set()
    edge_pattern = re.compile(r'"?([A-Za-z0-9_]+)"?\s*->\s*"?([A-Za-z0-9_]+)"?')
    node_pattern = re.compile(r'^\s*"?([A-Za-z0-9_]+)"?\s*(?:\[.*\])?;?\s*$')

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("digraph", "graph", "{", "}")):
            continue
        edge_match = edge_pattern.search(line)
        if edge_match:
            src, dst = edge_match.group(1), edge_match.group(2)
            nodes.update([src, dst])
            edges.add((src, dst))
            continue
        node_match = node_pattern.match(line)
        if node_match:
            nodes.add(node_match.group(1))

    return nodes, edges


def connected_components(nodes: Iterable[str], edges: Iterable[Tuple[str, str]]) -> int:
    node_set = set(nodes)
    if not node_set:
        return 0

    graph = defaultdict(set)
    for src, dst in edges:
        graph[src].add(dst)
        graph[dst].add(src)

    seen = set()
    count = 0
    for node in node_set:
        if node in seen:
            continue
        count += 1
        queue = deque([node])
        seen.add(node)
        while queue:
            current = queue.popleft()
            for nxt in graph[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return count


def build_mermaid(nodes: List[str], edges: List[Tuple[str, str]]) -> str:
    lines = ["flowchart TD"]
    for node in nodes:
        lines.append(f'  {node}["{node}"]')
    for src, dst in edges:
        lines.append(f"  {src} --> {dst}")
    return "\n".join(lines)


def _decode_bytes(content: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("文件编码无法识别")
