from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..services import print_json, run_path_metric


class TestPathCommand(BaseCommand):
    path = ("test", "path")

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[-1], add_help=False)
        parser.add_argument("path")
        parser.add_argument(
            "--metric",
            choices=("auto", "cfg-source", "cfg-graph", "oo-source", "oo-diagram", "fp", "estimate"),
            default="auto",
        )
        parser.add_argument("--language", default=None)
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        print_json(run_path_metric(args.path, args.metric, args.language))
        return 0
