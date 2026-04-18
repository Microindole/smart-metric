from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths
from ..services import print_json


ensure_runtime_paths()
from core.project_metric import ProjectScanOptions, analyze_project_directory  # noqa: E402


class ProjectCommand(BaseCommand):
    path = ("project-scan",)
    aliases = (("ps",),)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("path")
        parser.add_argument("-m", "--modules", default="inventory,loc,dependency,oo,design")
        parser.add_argument("-d", "--ignore-dir", action="append", default=[])
        parser.add_argument("-g", "--ignore-glob", action="append", default=[])
        parser.add_argument("-f", "--ignore-file", default=".smartmetricignore")
        parser.add_argument("-G", "--no-ignore-file", action="store_true")
        parser.add_argument("-D", "--no-default-ignore", action="store_true")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        modules = [item.strip() for item in str(args.modules).split(",") if item.strip()]
        options = ProjectScanOptions(
            use_default_ignores=not bool(args.no_default_ignore),
            ignore_dirs=tuple(item.strip() for item in args.ignore_dir if str(item).strip()),
            ignore_globs=tuple(item.strip() for item in args.ignore_glob if str(item).strip()),
            use_ignore_file=not bool(args.no_ignore_file),
            ignore_file_name=str(args.ignore_file or ".smartmetricignore").strip() or ".smartmetricignore",
        )
        print_json(analyze_project_directory(args.path, modules, options))
        return 0
