from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths
from ..services import print_json, read_binary_file


ensure_runtime_paths()
from core.cfg_metric import analyze_cfg_files  # noqa: E402


class CfgSourceCommand(BaseCommand):
    path = ("cfg-source",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("files", nargs="+")
        parser.add_argument("--language", default=None)
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        files = [read_binary_file(path) for path in args.files]
        print_json(analyze_cfg_files(files, args.language))
        return 0
