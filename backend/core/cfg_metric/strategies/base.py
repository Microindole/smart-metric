from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Decision:
    kind: str
    label: str


class ControlFlowAnalyzer:
    """Strategy interface for language-specific control-flow analysis.

    Current strategies use lightweight syntax rules. The interface is designed
    so a language strategy can later be replaced by an AST-backed analyzer
    without changing Flask routes or frontend calls.
    """

    language = ""
    analysis_method = "rule"

    def analyze(self, text: str) -> Dict:
        cleaned = self.strip_comments(text)
        summary = self.summary(cleaned)
        decisions = self.decisions(cleaned)
        decision_points = self.decision_point_count(summary)
        nodes, edges = build_graph(decisions)
        formula_value = len(edges) - len(nodes) + 2 if nodes else 0
        return {
            "language": self.language,
            "analysis_method": self.analysis_method,
            "decision_points": decision_points,
            "cyclomatic_complexity": decision_points + 1,
            "formula_complexity": formula_value,
            "summary": summary,
            "nodes": nodes,
            "edges": edges,
            "mermaid": build_mermaid(nodes, edges),
        }

    def strip_comments(self, text: str) -> str:
        raise NotImplementedError

    def summary(self, text: str) -> Dict[str, int]:
        raise NotImplementedError

    def decisions(self, text: str) -> List[Decision]:
        raise NotImplementedError

    def decision_point_count(self, summary: Dict[str, int]) -> int:
        return (
            summary.get("if", 0)
            + summary.get("for", 0)
            + summary.get("while", 0)
            + summary.get("case", 0)
            + summary.get("default", 0)
            + summary.get("catch", 0)
            + summary.get("ternary", 0)
            + summary.get("and", 0)
            + summary.get("or", 0)
        )


def build_graph(decisions: List[Decision]) -> tuple[list[dict], list[dict]]:
    nodes = [{"id": "start", "label": "Start", "type": "start"}]
    edges = []
    previous = "start"
    for index, decision in enumerate(decisions, start=1):
        decision_id = f"d{index}"
        branch_id = f"b{index}"
        join_id = f"j{index}"
        nodes.append({"id": decision_id, "label": decision.label, "type": "decision"})
        nodes.append({"id": branch_id, "label": f"{decision.kind} 分支", "type": "branch"})
        nodes.append({"id": join_id, "label": "合流", "type": "join"})
        edges.append({"from": previous, "to": decision_id, "label": "next"})
        edges.append({"from": decision_id, "to": branch_id, "label": "true"})
        edges.append({"from": decision_id, "to": join_id, "label": "false"})
        if decision.kind in {"for", "while", "do"}:
            edges.append({"from": branch_id, "to": decision_id, "label": "loop"})
        else:
            edges.append({"from": branch_id, "to": join_id, "label": "join"})
        previous = join_id
    nodes.append({"id": "end", "label": "End", "type": "end"})
    edges.append({"from": previous, "to": "end", "label": "next"})
    return nodes, edges


def build_mermaid(nodes: list[dict], edges: list[dict]) -> str:
    lines = ["flowchart TD"]
    for node in nodes:
        label = str(node["label"]).replace('"', "'")
        if node["type"] == "decision":
            lines.append(f'  {node["id"]}{{"{label}"}}')
        else:
            lines.append(f'  {node["id"]}["{label}"]')
    for edge in edges:
        lines.append(f'  {edge["from"]} -->|{edge.get("label", "")}| {edge["to"]}')
    return "\n".join(lines)


def ensure_summary_keys(result: Dict[str, int]) -> Dict[str, int]:
    for key in ("if", "for", "while", "switch", "case", "default", "catch", "ternary", "and", "or", "do"):
        result.setdefault(key, 0)
    return result
