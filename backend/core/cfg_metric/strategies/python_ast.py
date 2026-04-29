from __future__ import annotations

import ast
from typing import Dict, List, Tuple

from .base import ControlFlowAnalyzer, Decision, build_mermaid, ensure_summary_keys
from .python_strategy import PythonAnalyzer

GraphExit = Tuple[str, str]


class PythonAstAnalyzer(ControlFlowAnalyzer):
    language = "python"
    analysis_method = "ast-python"

    def analyze(self, text: str) -> Dict:
        try:
            tree = ast.parse(text)
            summary = self.summary_from_tree(tree)
            decisions = self.decisions_from_tree(tree)
            decision_points = self.decision_point_count(summary)
            nodes, edges = PythonCfgGraphBuilder().build(tree, decision_points)
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
        except SyntaxError:
            result = PythonAnalyzer().analyze(text)
            result["analysis_method"] = "rule-python-fallback"
            return result

    def strip_comments(self, text: str) -> str:
        return text

    def summary(self, text: str) -> Dict[str, int]:
        return self.summary_from_tree(ast.parse(text))

    def summary_from_tree(self, tree: ast.AST) -> Dict[str, int]:
        result = {
            "if": 0,
            "for": 0,
            "while": 0,
            "switch": 0,
            "case": 0,
            "default": 0,
            "catch": 0,
            "ternary": 0,
            "and": 0,
            "or": 0,
            "do": 0,
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                result["if"] += 1
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                result["for"] += 1
            elif isinstance(node, ast.While):
                result["while"] += 1
            elif isinstance(node, ast.ExceptHandler):
                result["catch"] += 1
            elif isinstance(node, ast.IfExp):
                result["ternary"] += 1
            elif isinstance(node, ast.BoolOp):
                increment = max(len(node.values) - 1, 0)
                if isinstance(node.op, ast.And):
                    result["and"] += increment
                elif isinstance(node.op, ast.Or):
                    result["or"] += increment
            elif hasattr(ast, "Match") and isinstance(node, ast.Match):
                result["switch"] += 1
                result["case"] += len(getattr(node, "cases", []))
        return ensure_summary_keys(result)

    def decisions(self, text: str) -> List[Decision]:
        return self.decisions_from_tree(ast.parse(text))

    def decisions_from_tree(self, tree: ast.AST) -> List[Decision]:
        collected: List[tuple[int, int, int, Decision]] = []
        sequence = 0

        def add(node, kind: str, label: str) -> None:
            nonlocal sequence
            line = getattr(node, "lineno", 0)
            column = getattr(node, "col_offset", 0)
            collected.append((line, column, sequence, Decision(kind, label)))
            sequence += 1

        for node in ast.walk(tree):
            line = getattr(node, "lineno", 0)
            if isinstance(node, ast.If):
                add(node, "if", f"if line {line}")
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                add(node, "for", f"for line {line}")
            elif isinstance(node, ast.While):
                add(node, "while", f"while line {line}")
            elif isinstance(node, ast.ExceptHandler):
                add(node, "catch", f"except line {line}")
            elif isinstance(node, ast.IfExp):
                add(node, "ternary", f"条件表达式 line {line}")
            elif isinstance(node, ast.BoolOp):
                increment = max(len(node.values) - 1, 0)
                kind = "and" if isinstance(node.op, ast.And) else "or"
                for _ in range(increment):
                    add(node, kind, f"短路{kind.upper()} line {line}")
            elif hasattr(ast, "Match") and isinstance(node, ast.Match):
                add(node, "switch", f"match line {line}")
                for case in getattr(node, "cases", []):
                    case_line = getattr(case.pattern, "lineno", line)
                    add(case.pattern, "case", f"case line {case_line}")
        return [item[3] for item in sorted(collected)]


class PythonCfgGraphBuilder:
    def __init__(self):
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.index = 0
        self.loop_stack: list[dict] = []

    def build(self, tree: ast.AST, decision_points: int) -> tuple[list[dict], list[dict]]:
        self.nodes = [{"id": "start", "label": "Start", "type": "start"}]
        self.edges = []
        self.index = 0
        self.loop_stack = []

        if decision_points == 0:
            self.nodes.append({"id": "end", "label": "End", "type": "end"})
            self.add_edge("start", "end", "next")
            return self.nodes, self.edges

        exits: list[GraphExit] = []
        for body in self.control_bodies(tree):
            exits.extend(self.build_block(body, [("start", "next")]))

        self.nodes.append({"id": "end", "label": "End", "type": "end"})
        self.connect(exits, "end")
        return self.nodes, self.edges

    def control_bodies(self, tree: ast.AST) -> list[list[ast.stmt]]:
        bodies: list[list[ast.stmt]] = []
        if isinstance(tree, ast.Module):
            direct = [
                stmt
                for stmt in tree.body
                if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and self.statement_has_control(stmt)
            ]
            if direct:
                bodies.append(tree.body)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bodies.append(node.body)
        return bodies or [[]]

    def statement_has_control(self, statement: ast.AST) -> bool:
        control_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.Try,
            ast.Return,
            ast.Break,
            ast.Continue,
            ast.IfExp,
            ast.BoolOp,
            ast.Match,
        )
        return any(
            isinstance(node, control_nodes)
            for node in ast.walk(statement)
        )

    def build_block(self, statements: list[ast.stmt], incoming: list[GraphExit]) -> list[GraphExit]:
        exits = incoming
        for statement in statements:
            if not exits:
                break
            exits = self.build_statement(statement, exits)
        return exits

    def build_statement(self, statement: ast.stmt, incoming: list[GraphExit]) -> list[GraphExit]:
        if isinstance(statement, ast.If):
            return self.build_if(statement, incoming)
        if isinstance(statement, (ast.For, ast.AsyncFor)):
            return self.build_loop(statement, incoming, "for")
        if isinstance(statement, ast.While):
            return self.build_loop(statement, incoming, "while")
        if isinstance(statement, ast.Try):
            return self.build_try(statement, incoming)
        if isinstance(statement, ast.Return):
            return self.build_return(statement, incoming)
        if isinstance(statement, ast.Break):
            return self.build_break(statement, incoming)
        if isinstance(statement, ast.Continue):
            return self.build_continue(statement, incoming)
        if isinstance(statement, ast.Match):
            return self.build_match(statement, incoming)
        return incoming

    def build_if(self, statement: ast.If, incoming: list[GraphExit]) -> list[GraphExit]:
        line = getattr(statement, "lineno", 0)
        decision_id = self.add_node(f"if line {line}", "decision")
        self.connect(incoming, decision_id)

        true_exits, false_exits = self.add_condition_decisions(statement.test, [(decision_id, "true")], [(decision_id, "false")])
        body_exits = self.build_block(statement.body, true_exits)
        else_exits = self.build_block(statement.orelse, false_exits) if statement.orelse else false_exits
        return self.join_paths(line, body_exits + else_exits)

    def build_loop(self, statement: ast.stmt, incoming: list[GraphExit], kind: str) -> list[GraphExit]:
        line = getattr(statement, "lineno", 0)
        decision_id = self.add_node(f"{kind} line {line}", "decision")
        self.connect(incoming, decision_id)

        context = {"continue": decision_id, "breaks": []}
        self.loop_stack.append(context)
        body_exits = self.build_block(getattr(statement, "body", []), [(decision_id, "true")])
        self.connect(body_exits, decision_id, "loop")
        self.loop_stack.pop()

        return [(decision_id, "false")] + context["breaks"]

    def build_try(self, statement: ast.Try, incoming: list[GraphExit]) -> list[GraphExit]:
        if not statement.handlers:
            return self.build_block(statement.body, incoming)

        catch_id = self.add_node(f"except line {getattr(statement.handlers[0], 'lineno', getattr(statement, 'lineno', 0))}", "decision")
        self.connect(incoming, catch_id, "try")
        exits = self.build_block(statement.body, [(catch_id, "false")])
        for handler in statement.handlers:
            exits.extend(self.build_block(handler.body, [(catch_id, "true")]))
        return self.join_paths(getattr(statement, "lineno", 0), exits)

    def build_return(self, statement: ast.Return, incoming: list[GraphExit]) -> list[GraphExit]:
        exits = incoming
        if isinstance(statement.value, ast.IfExp):
            line = getattr(statement.value, "lineno", getattr(statement, "lineno", 0))
            ternary_id = self.add_node(f"条件表达式 line {line}", "decision")
            self.connect(exits, ternary_id)
            exits = [(ternary_id, "true"), (ternary_id, "false")]

        line = getattr(statement, "lineno", 0)
        return_id = self.add_node(f"return line {line}", "statement")
        self.connect(exits, return_id)
        self.add_edge(return_id, "end", "return")
        return []

    def build_break(self, statement: ast.Break, incoming: list[GraphExit]) -> list[GraphExit]:
        line = getattr(statement, "lineno", 0)
        break_id = self.add_node(f"break line {line}", "statement")
        self.connect(incoming, break_id)
        if self.loop_stack:
            self.loop_stack[-1]["breaks"].append((break_id, "break"))
            return []
        return [(break_id, "next")]

    def build_continue(self, statement: ast.Continue, incoming: list[GraphExit]) -> list[GraphExit]:
        line = getattr(statement, "lineno", 0)
        continue_id = self.add_node(f"continue line {line}", "statement")
        self.connect(incoming, continue_id)
        if self.loop_stack:
            self.add_edge(continue_id, self.loop_stack[-1]["continue"], "continue")
            return []
        return [(continue_id, "next")]

    def build_match(self, statement: ast.Match, incoming: list[GraphExit]) -> list[GraphExit]:
        line = getattr(statement, "lineno", 0)
        match_id = self.add_node(f"match line {line}", "decision")
        self.connect(incoming, match_id)
        exits: list[GraphExit] = []
        for case in statement.cases:
            case_line = getattr(case.pattern, "lineno", line)
            case_id = self.add_node(f"case line {case_line}", "decision")
            self.add_edge(match_id, case_id, "case")
            exits.extend(self.build_block(case.body, [(case_id, "true")]))
            exits.append((case_id, "false"))
        return self.join_paths(line, exits or [(match_id, "false")])

    def add_condition_decisions(
        self,
        expression: ast.AST,
        true_exits: list[GraphExit],
        false_exits: list[GraphExit],
    ) -> tuple[list[GraphExit], list[GraphExit]]:
        bool_nodes = sorted(
            (node for node in ast.walk(expression) if isinstance(node, ast.BoolOp)),
            key=lambda item: (getattr(item, "lineno", 0), getattr(item, "col_offset", 0)),
        )
        for bool_node in bool_nodes:
            kind = "AND" if isinstance(bool_node.op, ast.And) else "OR"
            line = getattr(bool_node, "lineno", 0)
            decision_id = self.add_node(f"短路{kind} line {line}", "decision")
            self.connect(true_exits, decision_id, "eval")
            true_exits = [(decision_id, "true")]
            false_exits.append((decision_id, "false"))
        return true_exits, false_exits

    def join_paths(self, line: int, exits: list[GraphExit]) -> list[GraphExit]:
        if not exits:
            return []
        join_id = self.add_node(f"合流 line {line}", "join")
        self.connect(exits, join_id)
        return [(join_id, "next")]

    def add_node(self, label: str, node_type: str) -> str:
        self.index += 1
        node_id = f"n{self.index}"
        self.nodes.append({"id": node_id, "label": label, "type": node_type})
        return node_id

    def add_edge(self, source: str, target: str, label: str) -> None:
        if source == "end":
            return
        self.edges.append({"from": source, "to": target, "label": label})

    def connect(self, exits: list[GraphExit], target: str, label: str | None = None) -> None:
        for source, edge_label in exits:
            self.add_edge(source, target, label or edge_label or "next")
