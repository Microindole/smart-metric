from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths
from ..services import print_json


ensure_runtime_paths()
from core.project_metric import analyze_project_directory  # noqa: E402


class ProjectCommand(BaseCommand):
    path = ("project-scan",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("path")
        parser.add_argument("--modules", default="inventory,loc,dependency,oo,design")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        modules = [item.strip() for item in str(args.modules).split(",") if item.strip()]
        print_json(analyze_project_directory(args.path, modules))
        return 0
