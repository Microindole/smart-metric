from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple


def analyze_imported_graph(content: bytes, filename: str) -> Dict:
    text = _decode_bytes(content)
    fmt = detect_graph_format(filename, text)
    if fmt == "json":
        nodes, edges, node_meta, edge_labels = parse_json_graph(text)
    elif fmt == "mermaid":
        nodes, edges = parse_mermaid_graph(text)
        node_meta = {}
        edge_labels = {}
    elif fmt == "dot":
        nodes, edges = parse_dot_graph(text)
        node_meta = {}
        edge_labels = {}
    elif fmt == "xml":
        nodes, edges = parse_xml_graph(text)
        node_meta = {}
        edge_labels = {}
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
        "nodes": [build_node_payload(node, node_meta.get(node, {})) for node in nodes],
        "edges": [build_edge_payload(src, dst, edge_labels.get((src, dst), "")) for src, dst in normalized_edges],
        "mermaid": build_mermaid(nodes, normalized_edges, edge_labels),
    }


def detect_graph_format(filename: str, text: str) -> str:
    lower = filename.lower()
    stripped = text.lstrip()
    if lower.endswith(".json") or stripped.startswith("{"):
        return "json"
    if lower.endswith((".oom", ".xml")) or stripped.startswith("<"):
        return "xml"
    if lower.endswith((".mmd", ".mermaid")) or stripped.startswith("flowchart") or stripped.startswith("graph"):
        return "mermaid"
    if lower.endswith(".dot") or stripped.startswith("digraph") or stripped.startswith("graph"):
        return "dot"
    return ""


def parse_json_graph(text: str) -> Tuple[Set[str], Set[Tuple[str, str]], Dict[str, Dict[str, str]], Dict[Tuple[str, str], str]]:
    payload = json.loads(text)
    raw_nodes = payload.get("nodes", [])
    raw_edges = payload.get("edges", [])

    nodes: Set[str] = set()
    node_meta: Dict[str, Dict[str, str]] = {}
    for item in raw_nodes:
        if isinstance(item, str):
            nodes.add(item)
        elif isinstance(item, dict):
            node_id = item.get("id") or item.get("name") or item.get("label")
            if node_id:
                node_id = str(node_id)
                nodes.add(node_id)
                node_meta[node_id] = {
                    key: str(value)
                    for key, value in {
                        "label": item.get("label") or item.get("name"),
                        "type": item.get("type"),
                    }.items()
                    if value
                }

    edges: Set[Tuple[str, str]] = set()
    edge_labels: Dict[Tuple[str, str], str] = {}
    for item in raw_edges:
        label = ""
        if isinstance(item, dict):
            src = item.get("from") or item.get("source") or item.get("src")
            dst = item.get("to") or item.get("target") or item.get("dst")
            label = str(item.get("label") or item.get("condition") or "")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            src, dst = item[0], item[1]
        else:
            continue
        if src is None or dst is None:
            continue
        src_id = str(src)
        dst_id = str(dst)
        nodes.update([src_id, dst_id])
        edge = (src_id, dst_id)
        edges.add(edge)
        if label:
            edge_labels[edge] = label

    return nodes, edges, node_meta, edge_labels


def build_node_payload(node_id: str, metadata: Dict[str, str]) -> Dict[str, str]:
    payload = {"id": node_id}
    if metadata.get("label"):
        payload["label"] = metadata["label"]
    if metadata.get("type"):
        payload["type"] = metadata["type"]
    return payload


def build_edge_payload(src: str, dst: str, label: str = "") -> Dict[str, str]:
    payload = {"from": src, "to": dst}
    if label:
        payload["label"] = label
    return payload


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


def parse_xml_graph(text: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    root = ET.fromstring(sanitize_xml_prefixes(text))
    nodes: Dict[str, str] = {}
    edges: Set[Tuple[str, str]] = set()

    for node in root.iter():
        tag = _local_name(node.tag)
        kind = normalized_tag_name(tag)
        attrs = {str(k).lower(): str(v) for k, v in node.attrib.items()}
        node_id = (attrs.get("id") or "").strip()
        name = (attrs.get("name") or attrs.get("code") or node_id).strip()
        signature = " ".join([kind, attrs.get("xmi:type", ""), attrs.get("type", ""), name]).lower()

        if is_cfg_node(kind, signature) and "ref" not in attrs and (node_id or name):
            if not node_id:
                node_id = name or f"node_{id(node)}"
            nodes[node_id] = name or node_id

        if is_cfg_edge(kind, signature):
            src = (attrs.get("source") or attrs.get("from") or attrs.get("client") or "").strip()
            dst = (attrs.get("target") or attrs.get("to") or attrs.get("supplier") or "").strip()
            if src and dst:
                nodes.setdefault(src, src)
                nodes.setdefault(dst, dst)
                edges.add((src, dst))
                continue

            src, dst = parse_embedded_flow(node)
            if src and dst:
                nodes.setdefault(src, src)
                nodes.setdefault(dst, dst)
                edges.add((src, dst))

    return set(nodes.keys()), edges


def is_cfg_node(kind: str, signature: str) -> bool:
    return kind in {"activity", "decision", "start", "end", "initial", "final", "merge", "fork", "join"}


def is_cfg_edge(kind: str, signature: str) -> bool:
    return kind in {"activityflow", "controlflow", "transition", "edge"}


def parse_embedded_flow(node: ET.Element) -> Tuple[str, str]:
    refs: List[str] = []
    for child in node.iter():
        tag = _local_name(child.tag)
        if tag in {"object1", "object2"}:
            continue
        attrs = {str(k).lower(): str(v) for k, v in child.attrib.items()}
        ref = (attrs.get("ref") or attrs.get("idref") or "").strip()
        if ref:
            refs.append(ref)
    if len(refs) >= 2:
        return refs[0], refs[1]
    return "", ""


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


def build_mermaid(nodes: List[str], edges: List[Tuple[str, str]], edge_labels: Dict[Tuple[str, str], str] | None = None) -> str:
    edge_labels = edge_labels or {}
    lines = ["flowchart TD"]
    for node in nodes:
        lines.append(f'  {node}["{node}"]')
    for src, dst in edges:
        label = edge_labels.get((src, dst), "")
        if label:
            lines.append(f"  {src} -->|{label}| {dst}")
        else:
            lines.append(f"  {src} --> {dst}")
    return "\n".join(lines)


def _decode_bytes(content: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("文件编码无法识别")


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1].lower()
    if ":" in tag:
        return tag.split(":", 1)[1].lower()
    return tag.lower()


def normalized_tag_name(tag: str) -> str:
    return tag.split("_")[-1].lower()


def sanitize_xml_prefixes(text: str) -> str:
    text = re.sub(r"<(/?)([A-Za-z_]\w*):", r"<\1\2_", text)
    text = re.sub(r"\s([A-Za-z_]\w*):([A-Za-z_]\w*)=", r" \1_\2=", text)
    return text
