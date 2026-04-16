from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths
from ..services import print_json, read_binary_file


ensure_runtime_paths()
from core.class_diagram_metric import analyze_class_diagram_bytes  # noqa: E402


class OoDiagramCommand(BaseCommand):
    path = ("oo-diagram",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("file")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        file = read_binary_file(args.file)
        print_json(analyze_class_diagram_bytes(file["filename"], file["content"]))
        return 0
