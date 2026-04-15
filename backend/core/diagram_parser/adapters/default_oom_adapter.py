from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict, List

from ..base import DiagramAdapter


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1].lower()
    return tag.lower()


class DefaultOomAdapter(DiagramAdapter):
    name = "default_oom"

    def can_handle(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".oom")

    def parse(self, content: bytes) -> Dict:
        root = ET.fromstring(content)
        actors: Dict[str, Dict] = {}
        use_cases: Dict[str, Dict] = {}
        links: List[Dict] = []

        for node in root.iter():
            tag = _local_name(node.tag)
            name = (node.attrib.get("name") or "").strip()
            node_id = (node.attrib.get("id") or name or f"node_{id(node)}").strip()

            if "actor" in tag:
                actors[node_id] = {"id": node_id, "name": name or node_id, "links": 0}
            elif "usecase" in tag or "use_case" in tag or ("use" in tag and "case" in tag):
                use_cases[node_id] = {
                    "id": node_id,
                    "name": name or node_id,
                    "links": 0,
                    "transactions": int(node.attrib.get("transactions", "0") or 0),
                }

            if "association" in tag or "include" in tag or "extend" in tag:
                src = (node.attrib.get("source") or node.attrib.get("from") or "").strip()
                dst = (node.attrib.get("target") or node.attrib.get("to") or "").strip()
                if src and dst:
                    links.append({"source": src, "target": dst, "type": tag})

        for rel in links:
            src = rel["source"]
            dst = rel["target"]
            if src in actors:
                actors[src]["links"] += 1
            if dst in actors:
                actors[dst]["links"] += 1
            if src in use_cases:
                use_cases[src]["links"] += 1
            if dst in use_cases:
                use_cases[dst]["links"] += 1

        return {
            "actors": list(actors.values()),
            "use_cases": list(use_cases.values()),
            "relations": links,
            "metadata": {
                "adapter": self.name,
                "actor_count": len(actors),
                "use_case_count": len(use_cases),
                "relation_count": len(links),
            },
        }
