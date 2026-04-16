from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, Iterable, List


def analyze_class_diagram_bytes(filename: str, content: bytes) -> Dict:
    text = decode_bytes(content)
    root = ET.fromstring(text)

    classes: Dict[str, Dict] = {}
    relations: List[Dict] = []

    for node in root.iter():
        tag = local_name(node.tag)
        attrs = {k.lower(): v for k, v in node.attrib.items()}
        name = (attrs.get("name") or "").strip()
        node_id = (attrs.get("id") or name or f"node_{id(node)}").strip()
        signature = " ".join([tag, attrs.get("type", ""), attrs.get("xmi:type", ""), name]).lower()

        if "class" in signature:
            classes.setdefault(
                node_id,
                {
                    "id": node_id,
                    "name": name or node_id,
                    "attributes": set(),
                    "methods": set(),
                    "parent": "",
                    "links": set(),
                },
            )
        elif "attribute" in signature or "property" in signature:
            owner = attrs.get("owner") or attrs.get("class") or attrs.get("parent") or ""
            if owner and owner in classes:
                classes[owner]["attributes"].add(name or node_id)
        elif "operation" in signature or "method" in signature:
            owner = attrs.get("owner") or attrs.get("class") or attrs.get("parent") or ""
            if owner and owner in classes:
                classes[owner]["methods"].add(name or node_id)

        if any(keyword in signature for keyword in ("association", "dependency", "generalization", "inherit")):
            src = (attrs.get("source") or attrs.get("from") or attrs.get("client") or "").strip()
            dst = (attrs.get("target") or attrs.get("to") or attrs.get("supplier") or "").strip()
            rel_type = relation_type(signature)
            if src and dst:
                relations.append({"source": src, "target": dst, "type": rel_type})

    # Fallback: nested members under class nodes.
    for node in root.iter():
        tag = local_name(node.tag)
        attrs = {k.lower(): v for k, v in node.attrib.items()}
        name = (attrs.get("name") or "").strip()
        node_id = (attrs.get("id") or name or "").strip()
        if node_id not in classes:
            continue
        for child in node:
            child_tag = local_name(child.tag)
            child_name = (child.attrib.get("name") or child.attrib.get("id") or "").strip()
            if "attribute" in child_tag or "property" in child_tag:
                classes[node_id]["attributes"].add(child_name or f"attr_{id(child)}")
            elif "operation" in child_tag or "method" in child_tag:
                classes[node_id]["methods"].add(child_name or f"method_{id(child)}")

    children = defaultdict(int)
    for rel in relations:
        src = rel["source"]
        dst = rel["target"]
        if src not in classes or dst not in classes:
            continue
        classes[src]["links"].add(dst)
        classes[dst]["links"].add(src)
        if rel["type"] == "inheritance":
            classes[src]["parent"] = dst
            children[dst] += 1

    items = []
    for item in classes.values():
        dit = inheritance_depth(item["id"], classes)
        cbo_links = {ref for ref in item["links"] if ref != item["id"]}
        items.append(
            {
                "filename": filename,
                "class_name": item["name"],
                "parent": classes[item["parent"]]["name"] if item["parent"] in classes else item["parent"],
                "diagram_ck": {
                    "dit": dit,
                    "noc": children.get(item["id"], 0),
                    "cbo": len(cbo_links),
                },
                "diagram_lk": {
                    "nom": len(item["methods"]),
                    "noa": len(item["attributes"]),
                },
                "attributes": sorted(item["attributes"]),
                "methods": sorted(item["methods"]),
                "links": sorted(classes[ref]["name"] if ref in classes else ref for ref in cbo_links),
            }
        )

    summary = {
        "class_count": len(items),
        "total_methods": sum(item["diagram_lk"]["nom"] for item in items),
        "total_attributes": sum(item["diagram_lk"]["noa"] for item in items),
        "max_dit": max((item["diagram_ck"]["dit"] for item in items), default=0),
        "max_cbo": max((item["diagram_ck"]["cbo"] for item in items), default=0),
        "relation_count": len(relations),
    }
    return {"classes": items, "summary": summary, "relations": relations}


def relation_type(signature: str) -> str:
    if "generalization" in signature or "inherit" in signature:
        return "inheritance"
    if "dependency" in signature:
        return "dependency"
    return "association"


def inheritance_depth(class_id: str, classes: Dict[str, Dict]) -> int:
    depth = 0
    seen = set()
    current = classes[class_id]["parent"]
    while current and current not in seen and current in classes:
        depth += 1
        seen.add(current)
        current = classes[current]["parent"]
    return depth


def decode_bytes(content: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("文件编码无法识别")


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1].lower()
    return tag.lower()
