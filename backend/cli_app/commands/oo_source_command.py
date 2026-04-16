from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..services import print_json, read_binary_file
from ..runtime import ensure_runtime_paths


ensure_runtime_paths()
from core.oo_metric import analyze_oo_files  # noqa: E402


class OoSourceCommand(BaseCommand):
    path = ("oo-source",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("files", nargs="+")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        files = [read_binary_file(path) for path in args.files]
        print_json(analyze_oo_files(files))
        return 0
